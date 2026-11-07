# Model card
## Intended use
Historical portfolio demonstration of customer inactivity and future spending models. Adaptable to loyalty retention research, but this source is not a documented loyalty program. Not an operational deployment.
## Targets
90-day inactivity is an observable proxy, not permanent churn. Value is 90-day gross positive product spending, not full lifetime value or profit. Returns and administrative lines are excluded, so estimated value is not net cashflow.
## Features and evaluation
9 numeric historical features. SQL runs locally in DuckDB. Train snapshots: June/September/December 2010 and March 2011. Validation: June 2011. Untouched test: September 2011. Each 90-day outcome window completes before the next split. Same customers may appear across time, reflecting repeated scoring of known customers; this is not a new-customer generalisation test.
Choose churn model by validation PR-AUC and spending model by validation MAE. Do not select using test results. Hyperparameters are fixed, with no broad tuning. Calibration is measured, not assumed or claimed to be corrected.
Cox model uses March 2011 only to avoid treating repeated landmarks as independent survival observations. Fixed 90-day censoring supports complete binary evaluation at that horizon. Concordance and 90-day Brier are reported against a Kaplan–Meier baseline. Proportional-hazards assumptions are not guaranteed; diagnostics must be reviewed before deployment.
Bootstrap intervals resample customers within the single test snapshot; they do not capture uncertainty across economic periods.
## Limitations
Old single-retailer dataset, wholesale customers, incomplete identity coverage, source missingness, imperfect duplicate policy and right truncation of observed history. Frequent snapshots are correlated; transactional scale does not imply millions of independent customers. No campaign effect, uplift or causal benefit is established.
## Operations
Local batch scoring, input/output checks, feature drift CSV, versioned run IDs and MLflow experiment records. Latest scores use the held-out evaluated models without retraining; labels are unavailable for that final snapshot. Scheduling, cloud execution, alert delivery, authentication, rollback service and production feedback collection remain deployment work.
Only load trusted pickle files. Model compatibility depends on the recorded Python/package versions.

## Observed diagnostics from this run
The proportional-hazards test flagged recency (p=0.0018) and spend_180 (p=0.0077), with observed tenure borderline (p=0.0468), before adjustment for multiple comparisons. Treat Cox as exploratory; do not interpret hazard ratios as stable causal effects.
The churn calibration curve overpredicts inactivity in the September test. Latest observed-tenure PSI is large and partly reflects the mechanically increasing observation history. These are reasons to review temporal stability before deployment.
The selected spending model underpredicts test aggregate revenue by 48.8% and has worse RMSE than the historical baseline; its marginal MAE improvement is not a deployment justification.
