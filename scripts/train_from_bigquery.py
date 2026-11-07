"""Read existing BigQuery snapshots and train locally. Does not modify cloud tables.
Place in the project's scripts directory. Run from the project root:
python scripts/train_from_bigquery.py --project customer-churn-clv
"""
import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import pickle
import re

import numpy as np
import pandas as pd
from loyalty_ml.features import FEATURES
from loyalty_ml import train_churn, train_value, train_survival
from loyalty_ml.evaluate import churn_metrics, value_metrics, calibration_table, bootstrap_ap
from loyalty_ml.validation import validate_features

EXPECTED = {'train': 12277, 'validation': 2658, 'test': 2768}
DATES = {'train': ['2010-06-01', '2010-09-01', '2010-12-01', '2011-03-01'],
         'validation': ['2011-06-01'], 'test': ['2011-09-01']}

def normalize(frame):
    x = frame.copy()
    required = ['customer_id', 'snapshot_date', *FEATURES, 'inactive_90', 'future_spend_90', 'duration', 'event']
    missing = set(required) - set(x.columns)
    if missing:
        raise ValueError(f'Missing BigQuery columns: {sorted(missing)}')
    if x[required].isna().any().any():
        raise ValueError('Null values in required columns')
    x['customer_id'] = x.customer_id.astype(str)
    x['snapshot_date'] = pd.to_datetime(x.snapshot_date)
    for col in FEATURES + ['future_spend_90', 'duration']:
        x[col] = pd.to_numeric(x[col], errors='raise').astype(float)
    for col in ['inactive_90', 'event']:
        if not x[col].isin([0, 1]).all():
            raise ValueError(f'{col} must be binary')
        x[col] = x[col].astype(int)
    if not np.isfinite(x[FEATURES + ['future_spend_90','duration']].to_numpy()).all():
        raise ValueError('Nonfinite data')
    if (x.future_spend_90 < 0).any() or not x.duration.between(1/86400, 90).all():
        raise ValueError('Invalid outcome amount or survival duration')
    if not (x.event + x.inactive_90 == 1).all():
        raise ValueError('Inconsistent inactivity/event indicators')
    if not ((x.future_spend_90 > 0).astype(int) == x.event).all():
        raise ValueError('Purchase values and event labels disagree')
    for _, group in x.groupby('snapshot_date'):
        validate_features(group)
    return x.sort_values(['snapshot_date', 'customer_id']).reset_index(drop=True)

def check_splits(train, validation, test):
    for name, frame in [('train',train),('validation',validation),('test',test)]:
        dates = sorted(frame.snapshot_date.dt.strftime('%Y-%m-%d').unique())
        if len(frame) != EXPECTED[name] or dates != DATES[name]:
            raise ValueError(f'{name}: expected {EXPECTED[name]} rows on {DATES[name]}, got {len(frame)} rows on {dates}')
    if train.snapshot_date.max() + pd.Timedelta(days=90) > validation.snapshot_date.min():
        raise ValueError('Training outcomes overlap validation cutoff')
    if validation.snapshot_date.max() + pd.Timedelta(days=90) > test.snapshot_date.min():
        raise ValueError('Validation outcomes overlap test cutoff')

def fit_and_save(train, validation, test, out, provenance):
    from lifelines.utils import concordance_index
    from sklearn.metrics import brier_score_loss
    import mlflow
    check_splits(train, validation, test)
    out.mkdir(parents=True, exist_ok=False)
    print('Verified rows:', {k:len(v) for k,v in [('train',train),('validation',validation),('test',test)]}, flush=True)
    mlflow.set_tracking_uri('sqlite:///' + str((out/'mlflow.db').resolve()))
    mlflow.set_experiment('bigquery-customer-models')
    with mlflow.start_run() as run:
        print('Training churn models...', flush=True)
        churn, churn_name, churn_validation = train_churn.train(train, validation, 42)
        print('Training spending models...', flush=True)
        value, value_name, value_validation = train_value.train(train, validation, 42)
        print('Training survival model...', flush=True)
        cox, km = train_survival.train(train[train.snapshot_date == pd.Timestamp('2011-03-01')])
        probability = churn.predict_proba(test[FEATURES])[:,1]
        spending = value.predict(test[FEATURES])
        survival = cox.predict_survival_function(np.log1p(test[FEATURES]), times=[90]).iloc[0].to_numpy()
        metrics = {
            'churn_model':churn_name, 'value_model':value_name,
            'validation_pr_auc':churn_validation, 'validation_value_mae':value_validation,
            'test_churn':churn_metrics(test.inactive_90, probability),
            'test_value':value_metrics(test.future_spend_90, spending),
            'test_value_historical_baseline':value_metrics(test.future_spend_90, test.spend_90),
            'test_ap_bootstrap_95pct':bootstrap_ap(test.inactive_90, probability),
            'survival':{
                'concordance':float(concordance_index(test.duration, -cox.predict_partial_hazard(np.log1p(test[FEATURES])), test.event)),
                'brier_at_90':float(brier_score_loss(test.inactive_90, survival)),
                'km_brier_at_90':float(brier_score_loss(test.inactive_90, np.repeat(float(km.predict(90)),len(test))))
            },
            'split_rows':EXPECTED, 'mlflow_run_id':run.info.run_id
        }
        result = test.copy()
        result['inactivity_probability'] = probability
        result['predicted_spend_90'] = spending
        result.to_csv(out/'holdout_predictions.csv', index=False)
        calibration_table(test.inactive_90, probability).to_csv(out/'calibration.csv',index=False)
        (out/'evaluation.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
        (out/'bigquery_provenance.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
        versions = {p:importlib.metadata.version(p) for p in ['pandas','numpy','scikit-learn','lightgbm','lifelines','google-cloud-bigquery','mlflow-skinny']}
        (out/'package_versions.json').write_text(json.dumps(versions,indent=2),encoding='utf-8')
        with (out/'models.pkl').open('wb') as f:
            pickle.dump({'churn':churn,'value':value,'cox':cox,'km':km,'features':FEATURES,'metrics':metrics},f)
        mlflow.log_params({'project':provenance['project'], 'seed':42,'churn_model':churn_name,'value_model':value_name})
        mlflow.log_metrics({f'churn_{k}':v for k,v in metrics['test_churn'].items()})
        mlflow.log_metrics({f'value_{k}':v for k,v in metrics['test_value'].items()})
        mlflow.log_artifact(str(out/'evaluation.json'))
    print(json.dumps(metrics,indent=2),flush=True)
    print(f'\nSUCCESS. Results saved in: {out.resolve()}',flush=True)
    print('Training ran on this computer using BigQuery data. Cloud tables were not modified.')
    print('Value is gross 90-day spending, not full lifetime value. Review error and bias before use.')

def main():
    from google.cloud import bigquery
    parser=argparse.ArgumentParser()
    parser.add_argument('--project',default='customer-churn-clv')
    parser.add_argument('--dataset',default='customer_analytics')
    parser.add_argument('--root',default='.')
    args=parser.parse_args()
    if not re.fullmatch(r'[a-z][a-z0-9-]{4,61}[a-z0-9]',args.project) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',args.dataset):
        raise ValueError('Invalid project or dataset identifier')
    root=Path(args.root).resolve()
    if not (root/'pyproject.toml').exists():
        raise ValueError('Run this command from the project folder containing pyproject.toml')
    client=bigquery.Client(project=args.project)
    provenance={'project':args.project,'dataset':args.dataset,'location':'US','jobs':[],
                'note':'Models run locally; source tables queried in BigQuery. Test used only after validation selection.'}
    def read(table):
        sql=f'SELECT * FROM `{args.project}.{args.dataset}.{table}` ORDER BY snapshot_date, customer_id'
        print(f'Reading {table}...',flush=True)
        job=client.query(sql,location='US',job_config=bigquery.QueryJobConfig(maximum_bytes_billed=1_000_000_000))
        rows=job.result()
        # REST download avoids requiring the BigQuery Storage API.
        frame=rows.to_dataframe(create_bqstorage_client=False)
        provenance['jobs'].append({'table':table,'job_id':job.job_id,'bytes_processed':job.total_bytes_processed,'rows':len(frame),'sql':sql})
        return frame
    tv=read('customer_train_validation')
    if 'split' not in tv or tv.split.isna().any() or not set(tv.split.unique()) <= {'train','validation'}:
        raise ValueError('Training table requires valid train/validation split labels')
    tv=normalize(tv)
    test=normalize(read('customer_model_dataset_20110901'))
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    provenance['started_utc']=stamp
    fit_and_save(tv[tv.split=='train'].copy(),tv[tv.split=='validation'].copy(),test,
                 root/'outputs/bigquery_runs'/stamp,provenance)

if __name__=='__main__':
    main()
