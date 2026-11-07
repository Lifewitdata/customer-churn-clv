import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler
from sklearn.linear_model import TweedieRegressor
from sklearn.metrics import mean_absolute_error
from lightgbm import LGBMRegressor
from .features import FEATURES

class HistoricalSpending:
    def predict(self,x): return x['spend_90'].to_numpy()

def train(train, validation, seed=42):
    candidates = {
      'historical_spending':HistoricalSpending(),
      'tweedie_glm':make_pipeline(FunctionTransformer(np.log1p),StandardScaler(),TweedieRegressor(power=1.5,alpha=1,max_iter=1000)),
      'lightgbm_tweedie':LGBMRegressor(objective='tweedie',n_estimators=150,num_leaves=15,max_depth=5,min_child_samples=60,learning_rate=.04,reg_lambda=5,random_state=seed,n_jobs=2,verbosity=-1)
    }
    metrics = {}
    for name,model in candidates.items():
        if name != 'historical_spending': model.fit(train[FEATURES],train.future_spend_90)
        metrics[name] = float(mean_absolute_error(validation.future_spend_90,model.predict(validation[FEATURES])))
    winner = min(metrics,key=metrics.get)
    return candidates[winner],winner,metrics
