import numpy as np
import pandas as pd
from .features import FEATURES

def drift(reference,current):
    rows=[]
    for col in FEATURES:
        edges=np.unique(np.quantile(reference[col],np.linspace(0,1,11)))
        edges[0]=-np.inf;edges[-1]=np.inf
        if len(edges)<2: continue
        a=np.histogram(reference[col],edges)[0]/len(reference)
        b=np.histogram(current[col],edges)[0]/len(current)
        a=np.maximum(a,1e-6);b=np.maximum(b,1e-6)
        rows.append(dict(feature=col,psi=float(np.sum((b-a)*np.log(b/a))),reference_mean=reference[col].mean(),current_mean=current[col].mean()))
    return pd.DataFrame(rows)
