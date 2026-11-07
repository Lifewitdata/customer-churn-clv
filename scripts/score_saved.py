from pathlib import Path
import argparse,pickle
import pandas as pd
from loyalty_ml.features import build_features
from loyalty_ml.score import score
parser=argparse.ArgumentParser();parser.add_argument('--date',required=True);args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
with (root/'artifacts/models.pkl').open('rb') as f: bundle=pickle.load(f)
tx=pd.read_parquet(root/'data/processed/transactions.parquet')
if pd.Timestamp(args.date)>tx.invoice_date.max().normalize()+pd.Timedelta(days=1):
    raise ValueError('Scoring date exceeds available transaction history')
f=build_features(tx,args.date,root)
x=score(f,bundle['churn'],bundle['value'],args.date)
path=root/'outputs/predictions'/('scores_'+args.date+'.csv');x.to_csv(path,index=False)
print(path)
