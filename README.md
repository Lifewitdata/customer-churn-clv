# Customer Churn & Value Analytics

**Predicting 90-day customer inactivity, future spending and time to next purchase using Python, SQL, BigQuery and Tableau.**

### [View the interactive Tableau dashboards](https://public.tableau.com/app/profile/isfaque.ansari5273/viz/Customer_Churn_Value_Analytic/02CustomerValueandAccuracy)

The link opens **Customer Value and Accuracy**. The workbook also contains **Customer Retention Risk** and **Model Reliability**.

> **Project scope:** “Churn” means no qualifying purchase during the next 90 days. “Value” means gross positive product spending over that horizon, not full customer lifetime value, net revenue or profit. This is a historical retail modelling project; the source does not identify loyalty-program members.

## Business problem

Retention teams need to understand which customers may stop buying, which customers have substantial purchase history, and how reliable the predictions are before using them in a campaign or financial forecast.

This project addresses three questions:

1. **Inactivity risk:** which customers are likely to make no purchase in the following 90 days?
2. **Customer value:** how much might each customer spend over the same period?
3. **Purchase timing:** how does time to the next purchase vary across customers?

The outputs support historical customer review and model evaluation. They do not establish that contacting a customer will prevent churn or generate incremental revenue. That would require a separate experiment or defensible causal analysis.

## Results at a glance

The latest BigQuery-backed run evaluates **2,768 customers** at the **1 September 2011** snapshot. Outcomes cover the following 90 days.

| Measure | Holdout result | Interpretation |
| --- | ---: | --- |
| Inactivity ROC-AUC | 0.7350 | Measures ranking across classification thresholds |
| Inactivity average precision | 0.5969 | Summarises precision–recall performance |
| Top-decile lift | 1.73× | Inactivity is more concentrated in the highest-risk 10% than in the full population |
| Inactivity Brier score | 0.2156 | Measures probability error; lower is better |
| Observed inactivity | 39.31% | 1,088 customers made no qualifying purchase |
| Average predicted inactivity | 51.66% | Average risk exceeds the observed rate |
| Spending MAE | £632.17 | Mean absolute error per customer |
| Historical-spending baseline MAE | £631.80 | The selected model does not beat this baseline on test MAE |
| Aggregate spending bias | −48.79% | Total predicted spending is substantially below actual spending |
| Survival concordance | 0.6716 | Measures ordering of time-to-purchase predictions |

**What the results mean:** the inactivity model provides useful risk ranking, but its probabilities need further calibration assessment. The spending model underpredicts aggregate purchases and performs slightly worse than the historical baseline on test MAE. These results do not justify using it for operational financial forecasting.

Actual holdout purchases total **£2,401,424.89**, compared with predicted purchases of **£1,229,750.94**. No retention uplift, cost savings or realised commercial impact is claimed.

### Which evaluation files to use

The latest results come from:

`outputs/bigquery_runs/20261106T185235316273Z/`

| File | Purpose |
| --- | --- |
| `evaluation.json` | Model selection results, holdout metrics and baseline comparisons |
| `holdout_predictions.csv` | September customer features, observed outcomes and predictions |
| `calibration.csv` | Predicted versus observed inactivity by probability group |
| `bigquery_provenance.json` | Source tables, query jobs and processing metadata |
| `package_versions.json` | Package versions recorded for this training run |

Earlier notebooks, reports and `outputs/tableau/` exports retain results from the original local run. Their numbers may differ. **Use the BigQuery run above for the headline metrics in this README.** December customer scores are a separate scoring snapshot and must not be mixed with the September holdout evaluation.

## Dataset and preparation

Source: **UCI Online Retail II**, historical transactions from a UK online retailer between December 2009 and December 2011. The dataset includes wholesale activity and missing customer identifiers.

| Data preparation measure | Recorded value |
| --- | ---: |
| Original transaction rows | 1,067,371 |
| Cleaned transaction rows | 775,972 |
| Identified customers after cleaning | 5,851 |
| Distinct invoices after cleaning | 36,553 |
| Gross positive product revenue | £16,884,397.31 |

The cleaning pipeline removes exact duplicate rows, records without a usable customer/date, cancelled or nonpositive purchases, administrative product lines and the incomplete final day. The resulting revenue measure excludes returns and is therefore not net revenue.

The source manifest records the downloaded workbook hash. Data quality checks and cleaning counts are documented in `reports/data_audit.json` and `reports/source_manifest.json`.

## Technical stack

| Area | Tools and purpose |
| --- | --- |
| Data processing | Python, pandas, NumPy, Parquet |
| SQL and warehouse | DuckDB for the local pipeline; Google BigQuery for warehouse-backed training data |
| Machine learning | scikit-learn and LightGBM for classification and spending regression |
| Survival modelling | lifelines: Cox proportional hazards and Kaplan–Meier baseline |
| Experiment tracking | MLflow for parameters, metrics and local run records |
| Visualisation | Tableau Public and a packaged Tableau workbook |
| Exploration | Six Jupyter notebooks; matplotlib and seaborn |
| Validation | pytest for data quality, leakage, target windows and scoring checks |
| Reproducibility | Git, dependency records, Docker recipe and a GitHub Actions test workflow |

Docker and CI configuration are included in the repository. Their presence alone does not establish successful cloud deployment or a passing remote CI run.

## Workflow and architecture

There are two supported execution paths:

- **Local reproduction:** download the UCI workbook, clean transactions, create features with DuckDB SQL, train and evaluate models, then generate reports and dashboard exports.
- **BigQuery-backed training:** read prepared snapshots from BigQuery, validate their schema and dates, train and evaluate models in local Python, then export results for reporting.

In the completed workflow, results were uploaded/exported for Tableau reporting. The Python training script itself reads BigQuery data and saves results locally; it does not automatically write predictions back to the warehouse.

**BigQuery project:** `customer-churn-clv`  
**Dataset:** `customer_analytics`  
**Data location:** `US`

The Tableau workbook uses an exported snapshot. Publishing it to Tableau Public does not schedule model execution or automatically refresh its BigQuery data.

## Feature engineering

Features use only transactions observed before each snapshot date. Customers must have qualifying purchase history in the preceding 180 days.

| Feature | Definition |
| --- | --- |
| `recency_days` | Days since the most recent qualifying purchase |
| `frequency_180` | Distinct invoices during the previous 180 days |
| `spend_180` | Gross positive product spending during the previous 180 days |
| `average_order_value` | 180-day spending divided by distinct invoice count |
| `products_180` | Distinct products purchased during the previous 180 days |
| `spend_30` | Spending during the previous 30 days |
| `spend_90` | Spending during the previous 90 days |
| `frequency_90` | Distinct invoices during the previous 90 days |
| `observed_tenure_days` | Days since the customer's first purchase visible in the dataset |

Observed tenure is bounded by the available data history; it is not a verified membership start date.

## Models and evaluation design

| Task | Candidates / baseline | Selection or evaluation |
| --- | --- | --- |
| 90-day inactivity | Logistic regression; LightGBM classifier | Select by validation average precision |
| 90-day spending | Historical spending; Tweedie GLM; LightGBM Tweedie | Select by validation MAE |
| Time to next purchase | Cox proportional hazards; Kaplan–Meier baseline | Concordance and 90-day Brier score |

The latest run selected **logistic regression** for inactivity and **LightGBM Tweedie** for spending. Selection used validation performance, not the final holdout.

| Split | Snapshot dates | Rows |
| --- | --- | ---: |
| Training | June, September and December 2010; March 2011 | 12,277 |
| Validation | June 2011 | 2,658 |
| Test | September 2011 | 2,768 |

Outcome windows complete before the next evaluation split. Some customers appear at multiple dates, reflecting repeated scoring of known customers; this is not a test of generalisation to entirely new customers.

The Cox model uses the March 2011 snapshot to avoid treating repeated snapshots as independent survival observations. Its assumptions require further diagnostics before operational use. Bootstrap uncertainty estimates within the test snapshot do not measure uncertainty across future economic periods.

## Tableau dashboards

| Dashboard | Business question | Main views |
| --- | --- | --- |
| **Customer Retention Risk** | Which customers and risk groups need investigation? | Customer count, risk bands, recency versus risk and customer review table |
| **Customer Value and Accuracy** | How close are spending predictions to actual purchases? | Actual/predicted totals, MAE, bias, comparisons by risk and largest errors |
| **Model Reliability** | Where are probabilities and spending estimates unreliable? | Predicted versus observed inactivity, probability-group counts and spending errors |

The review priority proxy is:

`inactivity_probability × spend_90`

It combines predicted risk with historical spending. It is **not** expected recoverable revenue, incremental campaign value or an optimal offer decision.

The packaged workbook is committed at `dashboards/Customer_Churn_Value_Analytics.twbx`. It contains its own Hyper extract, so it opens in Tableau Desktop without warehouse credentials or local data paths. `dashboards/README.md` documents its contents, limits and rebuild recipe. The images under `dashboards/screenshots/` are Python-generated previews, not screenshots of this workbook. Use the Tableau Public link at the top to view the published dashboard.

## Project structure

| Path | Contents |
| --- | --- |
| `src/loyalty_ml/` | Ingestion, preprocessing, features, targets, training, evaluation, scoring and drift utilities |
| `sql/` | Local SQL definitions and BigQuery adaptations |
| `scripts/train_from_bigquery.py` | BigQuery-backed training and evaluation |
| `scripts/score_saved.py` | Historical batch scoring using saved local models |
| `scripts/execute_notebooks.py` | Notebook execution helper |
| `notebooks/` | Six analyses covering quality, behaviour, classification, value, survival and evaluation |
| `tests/` | Quality, leakage, scoring and target-window tests |
| `data/sample/` | Small attributed transaction sample; raw and processed data is generated locally |
| `outputs/` | Evaluation records, predictions and Tableau exports |
| `reports/` | Data dictionary, audits, model card and earlier analysis reports |
| `dashboards/` | Packaged Tableau workbook, build recipe and Python-generated previews |
| `configs/` | Modelling configuration |
| `.github/workflows/tests.yml` | Automated test workflow definition |

## Run the project locally

Clone the repository and work from its root folder, which contains `pyproject.toml`.

```powershell
git clone https://github.com/Lifewitdata/customer-churn-clv.git
cd customer-churn-clv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m pytest -q
python -m loyalty_ml.pipeline --root .
```

On macOS/Linux, activate the environment with `source .venv/bin/activate` instead. The package declares Python 3.11+ support; the publication-stage tests passed on Python 3.12. Use the version records associated with the run when reproducing its exact outputs.

The first pipeline execution downloads the UCI workbook and processes both sheets. Later runs reuse cached cleaned transactions. If cleaning rules change, rebuild the processed cache before comparing results. Models, processed data and local tracking databases are generated locally and are not committed.

### Train using the existing BigQuery snapshots

Configure Google Cloud Application Default Credentials for an account with access to the source tables. The training script expects:

- `customer_train_validation`, including the `split` column and the training/validation dates above.
- `customer_model_dataset_20110901`, including September features and observed outcomes.

Both tables must contain the required features and labels, including `customer_id`, `snapshot_date`, `inactive_90`, `future_spend_90`, `duration` and `event`.

```powershell
python scripts/train_from_bigquery.py --project customer-churn-clv --dataset customer_analytics
```

The script checks exact split counts, snapshot dates, required columns, finite values and consistent outcomes before fitting. Each run creates a timestamped folder under `outputs/bigquery_runs/` containing predictions, evaluation, provenance, version records and local model/tracking artifacts.

The SQL files in `sql/bigquery/` are feature/label adaptations, not a one-command warehouse bootstrap. Adjust placeholders, materialise the required snapshot tables and validate them before running training.

### Reproduce notebooks and score saved local models

After the local pipeline has generated its artifacts:

```powershell
python scripts/execute_notebooks.py
python scripts/score_saved.py --date 2011-12-09
```

`score_saved.py` uses `artifacts/models.pkl` and the cleaned transaction Parquet file from the local pipeline. It does not automatically select the newest model from `outputs/bigquery_runs/`. Saved pickle artifacts should only be loaded from trusted sources with compatible package versions.

## Validation and current status

**12 automated tests passed** during publication preparation. They cover cleaning behaviour, invalid inputs, duplicate customers, prevention of future-data leakage, snapshot boundaries, target windows, scoring and metric behaviour. This does not substitute for a full pipeline rerun or native Tableau visual testing.

| Capability | Status |
| --- | --- |
| Historical data preparation and local modelling | Implemented and previously executed |
| BigQuery-backed training | Executed locally using warehouse snapshots |
| Model comparison and holdout evaluation | Completed; limitations reported above |
| Tableau dashboard | Published on Tableau Public |
| Local saved-model batch scoring | Implemented |
| Feature drift export | Implemented for historical comparison |
| MLflow tracking | Local run records |
| Cloud Run execution and Cloud Scheduler | Not deployed |
| Automatic warehouse writes and dashboard refresh | Not implemented end to end |
| Production alerts, rollback and feedback collection | Future work |
| Campaign experimentation or causal uplift | Outside the implemented scope |

## Limitations and next steps

The data is historical and comes from one retailer. Missing identities, wholesale behaviour and incomplete observed customer histories affect interpretation. The customer population is not evidence of performance on loyalty programs with millions of members.

Next steps are to assess probability calibration, investigate spending underprediction and large errors, compare alternative models on additional time-based validation periods, and define acceptance criteria before deployment. Operational work would then add cloud execution, scheduling, monitored data checks and failure alerts. A separate controlled campaign experiment would be needed to measure incremental retention benefit.

## Data attribution

Chen, D. (2012). **Online Retail II**. UCI Machine Learning Repository.  
Dataset: https://archive.ics.uci.edu/dataset/502/online+retail+ii  
DOI: https://doi.org/10.24432/C5CG6D  
Dataset licence: **Creative Commons Attribution 4.0 International (CC BY 4.0)**.

Derived analysis retains this attribution. The raw source workbook is downloaded by the ingestion script rather than committed to this repository; a small de-duplicated sample is included under `data/sample/`. The dataset licence is not a separate software licence for this repository.
