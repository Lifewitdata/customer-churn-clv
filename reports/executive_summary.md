# Executive summary
The project processed 1,067,371 real transaction line items and retained 775,972 qualifying purchase lines across 5,851 customers.

The validation-selected inactivity model was logistic_regression. Its held-out PR-AUC was 0.597, versus an inactivity prevalence of 0.393. The highest-scoring 10% had 1.73 times the overall inactivity rate. This measures prioritisation of inactivity risk, not preventable churn.

The spending model was lightgbm_tweedie, with held-out MAE £631.42; the historical spending baseline had MAE £631.80. The relative MAE reduction was 0.1%. Aggregate spending bias was -48.8%, which must be considered before financial planning.

Use these outputs to identify customers for investigation and design a retention experiment. Do not claim campaign benefit without treatment/control evidence. Before deployment, update the dataset, examine calibration and survival assumptions, validate gross-versus-net value, and collect delayed labels to measure performance over time.

Delivered: executed local pipeline, notebooks, tests, model artifacts, SQL, metrics, static dashboard previews and Tableau-ready CSVs. BigQuery execution, Docker execution and a native Tableau workbook have not been validated here.
