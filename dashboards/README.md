# Tableau dashboards

## Packaged workbook

`Customer_Churn_Value_Analytics.twbx` is the packaged workbook behind the published view.
It embeds a single Hyper extract, so it opens in Tableau Desktop or Tableau Public without
local file paths, warehouse credentials or a BigQuery connection.
Published dashboard: [Customer Value and Accuracy](https://public.tableau.com/app/profile/isfaque.ansari5273/viz/Customer_Churn_Value_Analytic/02CustomerValueandAccuracy).

The extract is one consolidated customer-level table (`customer_value_dashboard.csv`) with
features, predicted risk and spending, `risk_band`, `priority_proxy` and observed outcomes
(`inactive_90`, `future_spend_90`, `duration`, `event`). Tableau calculates the error
measures (`absolute_error_gbp`, `prediction_error_gbp`, spending bias, probability band) from
those columns.

| Dashboard | Business question | Views |
| --- | --- | --- |
| 01 Customer Retention Risk | Which customers and risk groups need investigation? | Customers, average risk, customers by risk band, recency versus risk, customer review table sorted by priority proxy |
| 02 Customer Value and Accuracy | How close are spending predictions to actual purchases? | Actual and predicted spending totals, MAE, spending bias, actual versus predicted per customer and by risk band, largest errors |
| 03 Model Reliability | Where are probabilities and spending estimates unreliable? | Predicted versus observed inactivity by probability band, customers per probability band, reliability KPIs, spending MAE by risk |

Two limits to keep in view when using the workbook:

- The extract is a snapshot. Publishing to Tableau Public does not schedule model execution,
  refresh BigQuery, or update the numbers when the pipeline reruns. Re-export and re-publish
  to refresh it.
- `priority_proxy = inactivity_probability × spend_90` orders review effort only. It is not
  expected recoverable revenue, incremental campaign value, or an offer decision.

## Rebuilding the workbook

The build recipe used for the published version (dashboard size 1400 x 900):

1. **Customer Retention Risk** - customer count, average inactivity probability, risk-band
   counts, recency versus risk, and a customer table sorted by `priority_proxy`. Filter on
   `risk_band`. Label priority as a heuristic.
2. **Customer Value and Accuracy** - predicted and actual 90-day spending totals, MAE and
   bias, an actual versus predicted scatter with `customer_id` on Detail, and spending by
   risk band. Label the evaluation period.
3. **Model Reliability** - predicted versus observed inactivity by probability band from
   `outputs/tableau/calibration.csv`, plus error and drift measures. Keep PR-AUC and MAE
   charts separate; their scales and desired directions differ.

Use GBP for spending and percentages for probabilities. The standalone CSVs in
`outputs/tableau/` come from the earlier local run, so their totals can differ from the
published workbook, which reflects the BigQuery run recorded under
`outputs/bigquery_runs/`. Save with extracts before publishing, then verify filters,
totals, labels and source dates in Tableau.

## Screenshots

`dashboards/screenshots/*.png` are Python-generated previews rebuilt by
`python scripts/build_reports.py` after the pipeline. They are not captures of the Tableau
workbook above.
