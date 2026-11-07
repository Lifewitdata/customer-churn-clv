import pandas as pd
from .features import FEATURES
from .validation import validate_features,validate_scores

def score(features,churn,value,snapshot_date):
    validate_features(features)
    x=features.copy()
    x['snapshot_date']=str(pd.Timestamp(snapshot_date).date())
    x['inactivity_probability']=churn.predict_proba(x[FEATURES])[:,1]
    x['predicted_spend_90']=value.predict(x[FEATURES]).clip(min=0)
    # Historical spend proxy: do not claim this is preventable loss or causal offer value.
    x['priority_proxy']=x.inactivity_probability*x.spend_90
    x['risk_band']=pd.cut(x.inactivity_probability,[-.001,.3,.6,1.001],labels=['Low','Medium','High'])
    validate_scores(x)
    return x.sort_values('priority_proxy',ascending=False)
