-- DuckDB: the Python runner registers cleaned pandas data as transactions.
CREATE OR REPLACE TABLE clean_transactions AS SELECT * FROM transactions;
