# Data dictionary
Grain: one customer at one prediction date. Eligible customers purchased within the preceding 180 days.
Features use strictly earlier transactions. Dates have the source's unspecified timezone.

| Field | Meaning |
|---|---|
| customer_id | Source customer identifier; never a model input |
| snapshot_date | Exclusive feature cutoff, inclusive outcome-window start |
| recency_days | Calendar days since last positive purchase |
| frequency_180 / frequency_90 | Distinct purchase invoices in preceding 180/90 days |
| spend_180 / spend_90 / spend_30 | Positive product revenue in GBP in preceding window |
| average_order_value | spend_180 divided by frequency_180 |
| products_180 | Distinct product codes in preceding 180 days |
| observed_tenure_days | Days since first purchase observed in this dataset; not true customer tenure |
| inactive_90 | 1 if no qualifying purchase in following 90 days |
| future_spend_90 | Gross positive product revenue during following 90 days (GBP) |
| duration / event | Time until next purchase capped at 90 days / event indicator |
| inactivity_probability | Model probability of inactive_90=1 |
| predicted_spend_90 | Predicted 90-day gross product purchases (GBP) |
| priority_proxy | Inactivity probability multiplied by historical spend_90; heuristic, not causal benefit |
| risk_band | Descriptive fixed probability bands: low <0.3, medium 0.3–0.6, high >0.6 |
| psi | Population stability index relative to training distribution; descriptive drift signal |
