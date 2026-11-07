from pathlib import Path
import argparse,json,logging,pickle,platform
import pandas as pd
import numpy as np
import yaml
import mlflow
from sklearn.metrics import brier_score_loss
from lifelines.utils import concordance_index
from .ingestion import load
from .preprocessing import clean
from .features import FEATURES,build_features
from .targets import add_targets
from .validation import validate_features
from . import train_churn,train_value,train_survival
from .evaluate import churn_metrics,value_metrics,bootstrap_ap,calibration_table
from .monitor import drift
from .score import score

def run(root):
    root=Path(root).resolve();cfg=yaml.safe_load((root/'configs/model_config.yaml').read_text())
    if cfg['horizon_days'] != 90 or cfg['lookback_days'] != 180:
        raise ValueError('Current SQL and targets require 90-day outcomes and 180-day history')
    for folder in ['data/processed','data/sample','artifacts','outputs/metrics','outputs/predictions','outputs/tableau','reports']:
        (root/folder).mkdir(parents=True,exist_ok=True)
    logging.info('Loading source and auditing transactions')
    cache=root/'data/processed/transactions.parquet'
    if cache.exists():
        tx=pd.read_parquet(cache);audit=json.loads((root/'reports/data_audit.json').read_text())
    else:
        tx,audit=clean(load(root));tx.to_parquet(cache,index=False)
        (root/'reports/data_audit.json').write_text(json.dumps(audit,indent=2))
    tx.head(500).to_csv(root/'data/sample/transactions_sample.csv',index=False)
    dates=cfg['train_dates']+[cfg['validation_date'],cfg['test_date']]
    panels=[]
    for date in dates:
        logging.info('Building snapshot %s',date)
        f=build_features(tx,date,root);validate_features(f)
        panels.append(add_targets(f,tx,date,audit['observation_end_exclusive']))
    train=pd.concat(panels[:-2],ignore_index=True);val,test=panels[-2:]
    assert train.snapshot_date.max()+pd.Timedelta(days=90)<=val.snapshot_date.min()
    assert val.snapshot_date.max()+pd.Timedelta(days=90)<=test.snapshot_date.min()
    dataset=pd.concat(panels,ignore_index=True);dataset.to_parquet(root/'data/processed/customer_snapshots.parquet',index=False)
    mlflow.set_tracking_uri('sqlite:///' + str(root/'artifacts/mlflow.db'));mlflow.set_experiment('customer-inactivity-spending')
    with mlflow.start_run() as run:
        mlflow.log_params({'seed':cfg['seed'],'horizon_days':90,'lookback_days':180,'train_rows':len(train),'validation_rows':len(val),'test_rows':len(test)})
        logging.info('Training churn, spending and survival models')
        churn,cn,cv=train_churn.train(train,val,cfg['seed']);value,vn,vv=train_value.train(train,val,cfg['seed'])
        # One landmark per customer for survival fitting avoids pretending repeated rows are independent.
        cox,km=train_survival.train(panels[-3])
        p=churn.predict_proba(test[FEATURES])[:,1];v=value.predict(test[FEATURES])
        survival=cox.predict_survival_function(np.log1p(test[FEATURES]),times=[90]).iloc[0].to_numpy()
        metrics={'churn_model':cn,'value_model':vn,'validation_pr_auc':cv,'validation_value_mae':vv,
          'test_churn':churn_metrics(test.inactive_90,p),'test_value':value_metrics(test.future_spend_90,v),
          'test_value_historical_baseline':value_metrics(test.future_spend_90,test.spend_90),
          'test_ap_bootstrap_95pct':bootstrap_ap(test.inactive_90,p),
          'survival':{'concordance':float(concordance_index(test.duration,-cox.predict_partial_hazard(np.log1p(test[FEATURES])),test.event)),
                      'brier_at_90':float(brier_score_loss(test.inactive_90,survival)),
                      'km_brier_at_90':float(brier_score_loss(test.inactive_90,np.repeat(float(km.predict(90)),len(test))))},
          'split_rows':{'train':len(train),'validation':len(val),'test':len(test)},'run_id':run.info.run_id}
        mlflow.log_metrics({**{'churn_'+k:v for k,v in metrics['test_churn'].items()},**{'value_'+k:v for k,v in metrics['test_value'].items()}})
        bundle={'churn':churn,'value':value,'cox':cox,'km':km,'features':FEATURES,'config':cfg,'metrics':metrics,'python':platform.python_version()}
        with (root/'artifacts/models.pkl').open('wb') as f:pickle.dump(bundle,f)
        (root/'outputs/metrics/evaluation.json').write_text(json.dumps(metrics,indent=2))
        mlflow.log_artifact(str(root/'outputs/metrics/evaluation.json'))
    test_scores=score(test[FEATURES+['customer_id']],churn,value,cfg['test_date'])
    test_scores=test_scores.merge(test[['customer_id','inactive_90','future_spend_90']],on='customer_id')
    test_scores.to_csv(root/'outputs/tableau/holdout_predictions.csv',index=False)
    calibration_table(test.inactive_90,p).to_csv(root/'outputs/tableau/calibration.csv',index=False)
    latest=audit['observation_end_exclusive'];latest_features=build_features(tx,latest,root)
    latest_scores=score(latest_features,churn,value,latest)
    latest_scores.to_csv(root/'outputs/predictions/customer_scores.csv',index=False)
    latest_scores.to_csv(root/'outputs/tableau/customer_scores.csv',index=False)
    drift(train,latest_features).to_csv(root/'outputs/tableau/feature_drift.csv',index=False)
    by_month=tx.assign(month=tx.invoice_date.dt.to_period('M').astype(str)).groupby('month').agg(gross_revenue=('revenue','sum'),customers=('customer_id','nunique'),orders=('invoice','nunique'))
    by_month.to_csv(root/'outputs/tableau/monthly_trends.csv')
    pd.DataFrame([{'task':'churn','model':k,'validation_score':v,'metric':'PR-AUC'} for k,v in cv.items()]+[{'task':'spending','model':k,'validation_score':v,'metric':'MAE_GBP'} for k,v in vv.items()]).to_csv(root/'outputs/tableau/model_comparison.csv',index=False)
    print(json.dumps(metrics,indent=2))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',default='.');args=parser.parse_args()
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s')
    try:run(args.root)
    except Exception:logging.exception('Pipeline failed');raise
if __name__=='__main__':main()
