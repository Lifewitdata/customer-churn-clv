# Measured evaluation

This report is generated from the completed local pipeline, not hypothetical results.

```json
{
  "churn_model": "logistic_regression",
  "value_model": "lightgbm_tweedie",
  "validation_pr_auc": {
    "logistic_regression": 0.7043713794908235,
    "lightgbm": 0.7021870731258967
  },
  "validation_value_mae": {
    "historical_spending": 457.5173062452972,
    "tweedie_glm": 436.646691283545,
    "lightgbm_tweedie": 404.70577700470875
  },
  "test_churn": {
    "pr_auc": 0.5969053864202215,
    "roc_auc": 0.7350123643207284,
    "brier": 0.21560095752146816,
    "prevalence": 0.3930635838150289,
    "lift_top_10pct": 1.7266935655128477
  },
  "test_value": {
    "mae": 631.4177320300732,
    "rmse": 3121.1696468762148,
    "aggregate_bias_pct": -48.82398491196944
  },
  "test_value_historical_baseline": {
    "mae": 631.7958778901734,
    "rmse": 2655.299811546528,
    "aggregate_bias_pct": -23.50146999600724
  },
  "test_ap_bootstrap_95pct": [
    0.5639105481787894,
    0.62923275808673
  ],
  "survival": {
    "concordance": 0.6716218515655664,
    "brier_at_90": 0.2219160018878942,
    "km_brier_at_90": 0.2721742959663217
  },
  "split_rows": {
    "train": 12277,
    "validation": 2658,
    "test": 2768
  },
  "run_id": "ea62ad6ac46d479d857d6c24e044ae58"
}
```

## Data audit
```json
{
  "raw_rows": 1067371,
  "exact_duplicates": 34335,
  "missing_customer_or_date": 235151,
  "cancellations_nonpositive": 18460,
  "administrative_lines": 2848,
  "partial_final_day": 605,
  "clean_rows": 775972,
  "customers": 5851,
  "invoices": 36553,
  "observation_end_exclusive": "2011-12-09",
  "gross_revenue": 16884397.310000002
}
```

Validation selects models. Test results are reported once without choosing a new winner. Spending MAE and aggregate bias measure different properties; a low MAE does not guarantee accurate portfolio totals. Latest predictions have no observed future labels.
