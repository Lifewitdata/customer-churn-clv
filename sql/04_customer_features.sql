WITH history AS (
 SELECT * FROM clean_transactions
 WHERE invoice_date < CAST($cutoff AS TIMESTAMP)
), recent AS (
 SELECT * FROM history
 WHERE invoice_date >= CAST($cutoff AS TIMESTAMP) - INTERVAL 180 DAY
), lifetime AS (
 SELECT customer_id, date_diff('day',MIN(invoice_date),CAST($cutoff AS TIMESTAMP)) AS observed_tenure_days
 FROM history GROUP BY customer_id
)
SELECT r.customer_id,
 date_diff('day',MAX(invoice_date),CAST($cutoff AS TIMESTAMP)) AS recency_days,
 COUNT(DISTINCT invoice) AS frequency_180,
 SUM(revenue) AS spend_180,
 SUM(revenue)/COUNT(DISTINCT invoice) AS average_order_value,
 COUNT(DISTINCT stock_code) AS products_180,
 SUM(CASE WHEN invoice_date >= CAST($cutoff AS TIMESTAMP)-INTERVAL 30 DAY THEN revenue ELSE 0 END) AS spend_30,
 SUM(CASE WHEN invoice_date >= CAST($cutoff AS TIMESTAMP)-INTERVAL 90 DAY THEN revenue ELSE 0 END) AS spend_90,
 COUNT(DISTINCT CASE WHEN invoice_date >= CAST($cutoff AS TIMESTAMP)-INTERVAL 90 DAY THEN invoice END) AS frequency_90,
 MAX(l.observed_tenure_days) AS observed_tenure_days
FROM recent r JOIN lifetime l USING(customer_id) GROUP BY r.customer_id;
