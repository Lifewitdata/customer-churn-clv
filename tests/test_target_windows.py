import pandas as pd
import pytest
from loyalty_ml.features import build_features
from loyalty_ml.targets import add_targets

def test_inclusive_start_exclusive_end(tx,root):
    f=build_features(tx,'2011-03-01',root)
    x=add_targets(f,tx,'2011-03-01','2011-06-01').set_index('customer_id')
    assert x.loc['1','future_spend_90']==20
    assert x.loc['1','inactive_90']==0
    assert x.loc['2','inactive_90']==1
    assert x.loc['2','duration']==90

def test_incomplete_outcomes_rejected(tx,root):
    with pytest.raises(ValueError,match='fully observed'):
        add_targets(build_features(tx,'2011-03-01',root),tx,'2011-03-01','2011-05-01')

def test_only_eligible_customers_labelled(tx,root):
    f=build_features(tx,'2011-03-01',root)
    future=tx.iloc[[1]].copy();future['customer_id']='new'
    x=add_targets(f,pd.concat([tx,future]),'2011-03-01','2011-06-01')
    assert 'new' not in x.customer_id.tolist()
