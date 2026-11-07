# BigQuery deployment
These GoogleSQL scripts mirror the local feature definitions. They have not been executed against a cloud account.
1. Export cleaned transactions with `python -c "import pandas as pd; pd.read_parquet('data/processed/transactions.parquet').to_csv('data/processed/transactions.csv',index=False)"`.
2. Replace `YOUR_PROJECT.customer_analytics` in the scripts with your project and dataset.
3. Load the CSV as `clean_transactions`, with customer_id and invoice as STRING, invoice_date as TIMESTAMP, revenue as FLOAT64, stock_code as STRING.
4. Run the feature and label scripts separately. Join on customer_id for a single snapshot and validate counts and totals against the local outputs.
Do not claim BigQuery execution until this step has been run in your own account. The local pipeline executes SQL in DuckDB.
