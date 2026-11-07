# Customer Churn & Lifetime Value Prediction System

**[View the interactive Tableau dashboards](https://public.tableau.com/app/profile/isfaque.ansari5273/viz/Customer_Churn_Value_Analytic/02CustomerValueandAccuracy)**
A real-data machine-learning portfolio project for customer retention: 90-day inactivity classification, 90-day gross spending regression, and time-to-next-purchase survival analysis.

**Value scope:** the implemented value target is 90-day purchases, not full lifetime value or profit. Source customers are not labelled loyalty members.

## Latest BigQuery-backed run and Tableau workbook

The latest uploaded run is `outputs/bigquery_runs/20261106T185235316273Z/`. It uses `customer-churn-clv.customer_analytics` in BigQuery and trains models locally. Its September 2011 holdout contains 2,768 customers.

| Metric | Latest holdout result |
| --- | ---: |
| Inactivity ROC-AUC | 0.7350 |
| Inactivity average precision | 0.5969 |
| Brier score | 0.2156 |
| Spending MAE | £632.17 |
| Historical-spending baseline MAE | £631.80 |
| Aggregate spending bias | -48.79% |

The spending model does not beat the baseline MAE and substantially underpredicts aggregate purchases. These are historical evaluation results, not measured campaign impact. The other reports, notebooks and `outputs/tableau` files preserve an earlier local run; use the latest run's `evaluation.json` and `holdout_predictions.csv` for these results. December scores and September holdout predictions represent different reporting dates.

To repeat BigQuery training after configuring Application Default Credentials and the documented source tables:

```bash
python scripts/train_from_bigquery.py --project customer-churn-clv
```

The uploaded Tableau workbook includes its Hyper extract. Open the `.twbx` in Tableau; it is an exported snapshot, not an automatically refreshed BigQuery connection. Cloud deployment, scheduling and alerting remain future work.

## Quick start (Python 3.11+)
```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e .
python -m loyalty_ml.pipeline --root .
pytest -q
```
First run downloads the original 43.5 MB UCI workbook and reads both sheets; Excel ingestion can take a few minutes. Later runs reuse the cleaned Parquet cache. Delete data/processed/transactions.parquet when changing cleaning rules. Run from the extracted project root. Internet access is required for initial download and package installation.

## Structure
- `src/loyalty_ml/`: ingestion, cleaning, feature/target creation, training, validation, scoring and drift.
- `sql/`: executed local SQL; `sql/bigquery/` contains cloud adaptations and setup instructions.
- `notebooks/`: six executable analyses with real data and model outputs.
- `tests/`: boundary, leakage, data-quality, scoring and metric checks.
- `outputs/`: measured evaluation, held-out predictions, latest batch scores and Tableau CSVs.
- `reports/`: source hash, data audit, dictionary, model card, measured results and executive summary.
- `dashboards/`: packaged Tableau workbook, build specification and earlier static previews.

## Models
Compare logistic regression with LightGBM for inactivity. Compare historical-spending baseline, Tweedie GLM and LightGBM Tweedie for future spending. Fit Cox survival and Kaplan–Meier baseline. Model selection uses validation data only. Splits and important limitations are detailed in reports/model_card.md.

## Reproduce notebooks
After the pipeline:
```bash
python scripts/execute_notebooks.py
```
## Batch scoring saved models
```bash
python scripts/score_saved.py --date 2011-12-09
```
This scores the included historical data. For future production data, adapt ingestion and validate schema/observation completeness first.

## Tracking and deployment
MLflow records live in artifacts/mlflow.db. `python -m pip install mlflow` then `mlflow ui --backend-store-uri sqlite:///artifacts/mlflow.db` opens the local UI; skinny is sufficient for pipeline logging. Models are local trusted pickle artifacts. Docker recipe and GitHub Actions tests are supplied; their remote execution is not claimed. The BigQuery-backed training run has been executed locally; cloud scheduling and Cloud Run deployment are not yet implemented. No Streamlit dependency.

## Source
Chen, D. (2012). Online Retail II. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D — CC BY 4.0.
https://archive.ics.uci.edu/dataset/502/online+retail+ii
Raw workbook is downloaded rather than committed. Included derived outputs retain this attribution. See data/README.md and reports/source_manifest.json.

## Results and status
See reports/evaluation_report.md for this run's exact metrics and reports/executive_summary.md for interpretation. No campaign improvement, deployed business impact or cloud-scale performance is claimed.

The native Tableau workbook is available at [dashboards/Customer_Churn_Value_Analytics.twbx](dashboards/Customer_Churn_Value_Analytics.twbx). It contains Customer Retention Risk, Customer Value & Accuracy, and Model Reliability dashboards. Earlier Python-generated previews remain in dashboards/screenshots; they are not screenshots of this workbook.

## Execution environment
This delivered run was tested with Python 3.12. The package declares Python 3.11+ support, but Python 3.11 was not separately executed here. `requirements-tested.txt` records exact direct dependency versions. Notebook code cells were executed in-process because kernel sockets were unavailable; their outputs are saved in the notebooks.

The ZIP includes cleaned Parquet data and the evaluated models for convenient inspection. Those paths are intentionally ignored by Git. Raw source data can be downloaded again by removing the processed transaction cache. Rerun the pipeline to create MLflow records with paths valid on your machine.
