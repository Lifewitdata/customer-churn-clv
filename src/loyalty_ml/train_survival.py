import numpy as np
from lifelines import CoxPHFitter, KaplanMeierFitter
from .features import FEATURES

def survival_features(x):
    return np.log1p(x[FEATURES]).assign(duration=x.duration.values,event=x.event.values)

def train(frame):
    cox=CoxPHFitter(penalizer=.1)
    cox.fit(survival_features(frame),duration_col='duration',event_col='event',robust=True)
    km=KaplanMeierFitter().fit(frame.duration,frame.event)
    return cox,km
