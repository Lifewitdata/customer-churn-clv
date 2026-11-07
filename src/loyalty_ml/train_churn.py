import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from lightgbm import LGBMClassifier
from .features import FEATURES

def train(train, validation, seed=42):
    candidates = {
      'logistic_regression':make_pipeline(FunctionTransformer(np.log1p),StandardScaler(),LogisticRegression(max_iter=2000,random_state=seed)),
      'lightgbm':LGBMClassifier(n_estimators=150,num_leaves=15,max_depth=5,min_child_samples=60,learning_rate=.04,reg_lambda=5,random_state=seed,n_jobs=2,verbosity=-1)
    }
    metrics = {}
    for name, model in candidates.items():
        model.fit(train[FEATURES],train.inactive_90)
        metrics[name] = float(average_precision_score(validation.inactive_90,model.predict_proba(validation[FEATURES])[:,1]))
    winner = max(metrics,key=metrics.get)
    return candidates[winner],winner,metrics
