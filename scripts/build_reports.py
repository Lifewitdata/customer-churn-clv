from pathlib import Path
import json,importlib.metadata as md
import pandas as pd,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(__file__).resolve().parents[1]
m=json.loads((p/'outputs/metrics/evaluation.json').read_text());a=json.loads((p/'reports/data_audit.json').read_text())
s=pd.read_csv(p/'outputs/tableau/customer_scores.csv');h=pd.read_csv(p/'outputs/tableau/holdout_predictions.csv');c=pd.read_csv(p/'outputs/tableau/calibration.csv');d=pd.read_csv(p/'outputs/tableau/feature_drift.csv')
plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','axes.titlesize':13,'figure.facecolor':'#f5f7fa','axes.facecolor':'#ffffff'})
colors=['#17818d','#e3ac43','#c85b64']
def setup(title,subtitle):
 fig,ax=plt.subplots(2,2,figsize=(16,9));fig.suptitle(title,x=.07,ha='left',fontsize=23,fontweight='bold',color='#17324d')
 fig.text(.07,.925,subtitle,fontsize=12,color='#52677b');fig.subplots_adjust(top=.83,bottom=.12,hspace=.48,wspace=.3)
 fig.text(.07,.025,'Source: UCI Online Retail II | Historical portfolio analysis | GBP gross product purchases',fontsize=10,color='#52677b')
 return fig,ax.ravel()
fig,ax=setup('Customer retention overview',f'Latest scoring date: 9 December 2011 | {len(s):,} eligible customers | Inactivity = no purchase in next 90 days')
s.risk_band.value_counts().reindex(['Low','Medium','High']).plot.bar(ax=ax[0],color=colors,rot=0);ax[0].set_title('Customers by predicted risk');ax[0].set_ylabel('Customers')
ax[1].hist(s.inactivity_probability,bins=25,color=colors[0]);ax[1].set_title('Predicted inactivity probability');ax[1].set_xlabel('Probability')
q=s.groupby('risk_band').spend_90.sum().reindex(['Low','Medium','High'])/1000;q.plot.bar(ax=ax[2],color=colors,rot=0);ax[2].set_title('Historical spending by risk band');ax[2].set_ylabel('Previous 90 days, GBP thousands')
ax[3].scatter(s.recency_days,s.inactivity_probability,s=7,alpha=.3,color=colors[0]);ax[3].set_title('Recency and predicted inactivity');ax[3].set_xlabel('Days since last purchase');ax[3].set_ylabel('Probability')
fig.savefig(p/'dashboards/screenshots/01_retention_overview.png',dpi=120);plt.close(fig)
fig,ax=setup('Customer value overview','September 2011 holdout | 90-day gross spending prediction, not full lifetime value or profit')
ax[0].bar(['Actual','Predicted'],[h.future_spend_90.sum()/1e6,h.predicted_spend_90.sum()/1e6],color=colors[:2]);ax[0].set_title('Total holdout spending');ax[0].set_ylabel('GBP millions')
ax[1].scatter(h.future_spend_90,h.predicted_spend_90,s=8,alpha=.3,color=colors[0]);ax[1].set_xscale('symlog');ax[1].set_yscale('symlog');ax[1].set_xlabel('Actual GBP (symlog)');ax[1].set_ylabel('Predicted GBP (symlog)');ax[1].set_title('Customer-level prediction error')
h.groupby('risk_band')[['future_spend_90','predicted_spend_90']].sum().div(1000).plot.bar(ax=ax[2],color=colors[:2],rot=0);ax[2].set_title('Spending by risk band');ax[2].set_ylabel('GBP thousands');ax[2].legend(['Actual','Predicted'])
ax[3].axis('off');ax[3].text(0,.9,f"Selected model: {m['value_model']}\n\nTest MAE: £{m['test_value']['mae']:,.2f}\nHistorical baseline MAE: £{m['test_value_historical_baseline']['mae']:,.2f}\nAggregate bias: {m['test_value']['aggregate_bias_pct']:+.1f}%\n\nNo campaign uplift or recovered revenue is measured.",va='top',fontsize=14,color='#17324d')
fig.savefig(p/'dashboards/screenshots/02_value_overview.png',dpi=120);plt.close(fig)
fig,ax=setup('Model performance and monitoring','Holdout evaluation and latest input drift | Drift is descriptive; thresholds need operational validation')
ax[0].plot(c.predicted_probability,c.observed_inactivity_rate,'o-',color=colors[0]);ax[0].plot([0,1],[0,1],'--',color='#8c9aa7');ax[0].set_title('Calibration on test customers');ax[0].set_xlabel('Predicted probability');ax[0].set_ylabel('Observed inactivity rate')
d.sort_values('psi').plot.barh(x='feature',y='psi',ax=ax[1],legend=False,color=colors[0]);ax[1].set_title('Latest feature drift');ax[1].set_ylabel('');ax[1].tick_params(axis='y',labelsize=8)
pd.Series(m['validation_pr_auc']).plot.bar(ax=ax[2],color=colors[:2],rot=0);ax[2].set_title('Validation model selection');ax[2].set_ylabel('PR-AUC')
ax[3].axis('off');ax[3].text(0,.9,f"Selected churn model: {m['churn_model']}\n\nTest PR-AUC: {m['test_churn']['pr_auc']:.3f}\nTest ROC-AUC: {m['test_churn']['roc_auc']:.3f}\nTop 10% lift: {m['test_churn']['lift_top_10pct']:.2f}×\nBrier score: {m['test_churn']['brier']:.3f}\nSurvival concordance: {m['survival']['concordance']:.3f}",va='top',fontsize=14,color='#17324d')
fig.savefig(p/'dashboards/screenshots/03_model_monitoring.png',dpi=120);plt.close(fig)
(p/'reports/evaluation_report.md').write_text('# Measured evaluation\n\nThis report is generated from the completed local pipeline, not hypothetical results.\n\n```json\n'+json.dumps(m,indent=2)+'\n```\n\n## Data audit\n```json\n'+json.dumps(a,indent=2)+'\n```\n\nValidation selects models. Test results are reported once without choosing a new winner. Spending MAE and aggregate bias measure different properties; a low MAE does not guarantee accurate portfolio totals. Latest predictions have no observed future labels.\n')
improvement=(1-m['test_value']['mae']/m['test_value_historical_baseline']['mae'])*100
(p/'reports/executive_summary.md').write_text(f'''# Executive summary
The project processed {a['raw_rows']:,} real transaction line items and retained {a['clean_rows']:,} qualifying purchase lines across {a['customers']:,} customers.

The validation-selected inactivity model was {m['churn_model']}. Its held-out PR-AUC was {m['test_churn']['pr_auc']:.3f}, versus an inactivity prevalence of {m['test_churn']['prevalence']:.3f}. The highest-scoring 10% had {m['test_churn']['lift_top_10pct']:.2f} times the overall inactivity rate. This measures prioritisation of inactivity risk, not preventable churn.

The spending model was {m['value_model']}, with held-out MAE £{m['test_value']['mae']:.2f}; the historical spending baseline had MAE £{m['test_value_historical_baseline']['mae']:.2f}. The relative MAE reduction was {improvement:.1f}%. Aggregate spending bias was {m['test_value']['aggregate_bias_pct']:+.1f}%, which must be considered before financial planning.

Use these outputs to identify customers for investigation and design a retention experiment. Do not claim campaign benefit without treatment/control evidence. Before deployment, update the dataset, examine calibration and survival assumptions, validate gross-versus-net value, and collect delayed labels to measure performance over time.

Delivered: executed local pipeline, notebooks, tests, model artifacts, SQL, metrics, static dashboard previews and Tableau-ready CSVs. BigQuery execution, Docker execution and a native Tableau workbook have not been validated here.
''')
packages=['pandas','numpy','scikit-learn','lightgbm','lifelines','duckdb','mlflow-skinny','openpyxl','pyarrow','PyYAML','matplotlib','seaborn','nbformat','nbclient','ipykernel','pytest','SQLAlchemy','alembic']
(p/'requirements-tested.txt').write_text('# Exact direct dependency versions used in this Python 3.12 execution.\n'+'\n'.join(f'{x}=={md.version(x)}' for x in packages)+'\n')
print('Reports and 3 dashboard previews generated')
