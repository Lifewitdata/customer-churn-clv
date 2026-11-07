import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from loyalty_ml.features import FEATURES
from loyalty_ml.score import score
from loyalty_ml.train_value import HistoricalSpending
from loyalty_ml.monitor import drift
from loyalty_ml.evaluate import churn_metrics

def test_scoring_with_real_estimator():
    rng=np.random.default_rng(42)
    x=pd.DataFrame(rng.uniform(1,10,(40,len(FEATURES))),columns=FEATURES)
    x['customer_id']=[str(i) for i in range(40)]
    y=(x.recency_days>5).astype(int)
    model=LogisticRegression().fit(x[FEATURES],y)
    result=score(x,model,HistoricalSpending(),'2011-09-01')
    assert len(result)==40
    assert result.inactivity_probability.between(0,1).all()
    assert result.priority_proxy.is_monotonic_decreasing

def test_identical_distributions_zero_drift():
    x=pd.DataFrame({c:np.arange(100) for c in FEATURES})
    assert np.allclose(drift(x,x).psi,0)

def test_known_perfect_ranking():
    result=churn_metrics([1,0,1,0],[.9,.1,.8,.2])
    assert result['pr_auc']==1
    assert result['lift_top_10pct']==2
