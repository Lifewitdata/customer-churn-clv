# Source and processing
Source: https://archive.ics.uci.edu/dataset/502/online+retail+ii
Chen, D. (2012). Online Retail II. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D
License: CC BY 4.0. Source data: UK giftware retailer, 2009–2011; includes wholesale activity.
The pipeline downloads the original workbook; source_manifest.json records its SHA-256.
Raw data is excluded from Git and the deliverable ZIP to avoid unnecessary duplication. A small processed sample is included, with the same attribution.
Transformations: exact duplicate removal; exclude missing customer/date, cancelled/nonpositive purchases, administrative nonnumeric product codes and incomplete last day.
This creates positive product purchase revenue, not net revenue/profit. Unknown-customer transactions cannot support customer-level modeling.
No loyalty status, points, tiers or marketing treatments are invented. Customer IDs are source pseudonymous IDs.
