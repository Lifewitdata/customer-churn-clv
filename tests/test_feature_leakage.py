import pandas as pd
from loyalty_ml.features import build_features

def test_future_changes_do_not_change_features(tx,root):
    a=build_features(tx,'2011-03-01',root).sort_values('customer_id').reset_index(drop=True)
    changed=tx.copy();changed.loc[changed.invoice_date>='2011-03-01','revenue']=999999
    b=build_features(changed,'2011-03-01',root).sort_values('customer_id').reset_index(drop=True)
    pd.testing.assert_frame_equal(a,b)

def test_cutoff_is_excluded(tx,root):
    x=build_features(tx,'2011-03-01',root).set_index('customer_id')
    assert x.loc['1','spend_180']==10

def test_customers_without_recent_history_excluded(tx,root):
    assert build_features(tx,'2012-01-01',root).empty
