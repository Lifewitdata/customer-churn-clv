-- [cutoff, cutoff+90d): labels never enter the feature query.
SELECT customer_id, SUM(revenue) AS future_spend_90,
 MIN(invoice_date) AS next_purchase
FROM clean_transactions
WHERE invoice_date >= CAST($cutoff AS TIMESTAMP)
 AND invoice_date < CAST($cutoff AS TIMESTAMP) + INTERVAL 90 DAY
GROUP BY customer_id;
