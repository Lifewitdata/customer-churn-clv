import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score,roc_auc_score,brier_score_loss,mean_absolute_error,mean_squared_error
from sklearn.calibration import calibration_curve

def churn_metrics(y,p):
    y=np.asarray(y);p=np.asarray(p);k=max(1,int(np.ceil(.1*len(y))))
    return dict(pr_auc=float(average_precision_score(y,p)),roc_auc=float(roc_auc_score(y,p)),
      brier=float(brier_score_loss(y,p)),prevalence=float(y.mean()),
      lift_top_10pct=float(y[np.argsort(-p,kind='stable')[:k]].mean()/y.mean()))

def value_metrics(y,p):
    return dict(mae=float(mean_absolute_error(y,p)),rmse=float(mean_squared_error(y,p)**.5),
                aggregate_bias_pct=float((np.sum(p)/np.sum(y)-1)*100))

def bootstrap_ap(y,p,seed=42):
    rng=np.random.default_rng(seed);y=np.asarray(y);p=np.asarray(p);scores=[]
    for _ in range(200):
        idx=rng.integers(0,len(y),len(y))
        if len(np.unique(y[idx]))==2:scores.append(average_precision_score(y[idx],p[idx]))
    return np.quantile(scores,[.025,.975]).tolist()

def calibration_table(y,p):
    observed,predicted=calibration_curve(y,p,n_bins=10,strategy='quantile')
    return pd.DataFrame({'predicted_probability':predicted,'observed_inactivity_rate':observed})
