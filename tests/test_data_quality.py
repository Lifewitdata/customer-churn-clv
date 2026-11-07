import pandas as pd
import pytest
from loyalty_ml.preprocessing import clean
from loyalty_ml.validation import validate_features
from loyalty_ml.features import build_features

def test_clean_audit_and_cancellations(tx):
    tx=tx.assign(description='Product',country='UK')
    bad=tx.iloc[[0]].copy();bad['invoice']='C1';bad['quantity']=-1
    raw=pd.concat([tx,tx.iloc[[0]],bad],ignore_index=True)
    cleaned,audit=clean(raw)
    assert audit['exact_duplicates']==1
    assert audit['cancellations_nonpositive']==1
    assert audit['partial_final_day']==1
    assert len(cleaned)==3

def test_duplicate_customer_rejected(tx,root):
    f=build_features(tx,'2011-03-01',root)
    with pytest.raises(ValueError,match='Duplicate'):
        validate_features(pd.concat([f,f]))

def test_nan_rejected(tx,root):
    f=build_features(tx,'2011-03-01',root);f.loc[0,'spend_90']=float('nan')
    with pytest.raises(ValueError,match='Nonfinite'):validate_features(f)
