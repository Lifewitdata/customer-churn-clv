DECLARE cutoff TIMESTAMP DEFAULT TIMESTAMP('2011-09-01');
WITH history AS (
 SELECT * FROM `YOUR_PROJECT.customer_analytics.clean_transactions`
 WHERE invoice_date < cutoff
), recent AS (
 SELECT * FROM history
 WHERE invoice_date >= cutoff - INTERVAL 180 DAY
), lifetime AS (
 SELECT customer_id, DATE_DIFF(DATE(cutoff),DATE(MIN(invoice_date)),DAY) AS observed_tenure_days
 FROM history GROUP BY customer_id
)
SELECT r.customer_id,
 DATE_DIFF(DATE(cutoff),DATE(MAX(invoice_date)),DAY) AS recency_days,
 COUNT(DISTINCT invoice) AS frequency_180,
 SUM(revenue) AS spend_180,
 SUM(revenue)/COUNT(DISTINCT invoice) AS average_order_value,
 COUNT(DISTINCT stock_code) AS products_180,
 SUM(CASE WHEN invoice_date >= cutoff-INTERVAL 30 DAY THEN revenue ELSE 0 END) AS spend_30,
 SUM(CASE WHEN invoice_date >= cutoff-INTERVAL 90 DAY THEN revenue ELSE 0 END) AS spend_90,
 COUNT(DISTINCT CASE WHEN invoice_date >= cutoff-INTERVAL 90 DAY THEN invoice END) AS frequency_90,
 MAX(l.observed_tenure_days) AS observed_tenure_days
FROM recent r JOIN lifetime l USING(customer_id) GROUP BY r.customer_id;
