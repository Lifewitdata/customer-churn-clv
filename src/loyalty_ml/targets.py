import pandas as pd

def add_targets(features, tx, cutoff, observation_end, horizon=90):
    cutoff = pd.Timestamp(cutoff); end = cutoff + pd.Timedelta(days=horizon)
    if end > pd.Timestamp(observation_end):
        raise ValueError('Future outcome window is not fully observed')
    future = tx.loc[(tx.invoice_date >= cutoff)&(tx.invoice_date < end)]
    labels = future.groupby('customer_id').agg(future_spend_90=('revenue','sum'), next_purchase=('invoice_date','min'))
    x = features.merge(labels,how='left',on='customer_id')
    x['event'] = x.next_purchase.notna().astype(int)
    x['inactive_90'] = 1-x.event
    x['future_spend_90'] = x.future_spend_90.fillna(0)
    x['duration'] = ((x.next_purchase-cutoff).dt.total_seconds()/86400).fillna(horizon).clip(lower=1/86400)
    x['snapshot_date'] = cutoff
    return x.drop(columns='next_purchase')
