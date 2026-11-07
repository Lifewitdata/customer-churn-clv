import numpy as np
from .features import FEATURES

def validate_features(frame):
    if frame.empty: raise ValueError('No eligible customers')
    if frame.customer_id.duplicated().any(): raise ValueError('Duplicate customer snapshot')
    if not np.isfinite(frame[FEATURES].to_numpy(dtype=float)).all(): raise ValueError('Nonfinite features')
    if (frame[FEATURES] < 0).any().any(): raise ValueError('Negative purchase features')

def validate_scores(frame):
    if not frame.inactivity_probability.between(0,1).all(): raise ValueError('Invalid probability')
    if not np.isfinite(frame.predicted_spend_90).all() or (frame.predicted_spend_90 < 0).any():
        raise ValueError('Invalid spending prediction')
