from pathlib import Path
import duckdb
import pandas as pd
FEATURES = ['recency_days','frequency_180','spend_180','average_order_value','products_180','spend_30','spend_90','frequency_90','observed_tenure_days']
def build_features(tx, cutoff, root):
    with duckdb.connect() as con:
        con.register('transactions',tx)
        con.execute((Path(root)/'sql/01_create_tables.sql').read_text())
        return con.execute((Path(root)/'sql/04_customer_features.sql').read_text(), {'cutoff':str(cutoff)}).df()
