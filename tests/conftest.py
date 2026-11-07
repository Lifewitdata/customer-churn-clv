import pandas as pd
import pytest
from pathlib import Path
@pytest.fixture
def root(): return Path(__file__).resolve().parents[1]
@pytest.fixture
def tx():
    return pd.DataFrame({'customer_id':['1','1','1','2'],'invoice':['100','101','102','103'],
     'invoice_date':pd.to_datetime(['2011-01-01','2011-03-01','2011-05-30','2011-02-01']),
     'stock_code':['100']*4,'revenue':[10.,20.,30.,40.],'quantity':[1]*4,'unit_price':[10.,20.,30.,40.]})
