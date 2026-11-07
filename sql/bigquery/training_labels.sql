DECLARE cutoff TIMESTAMP DEFAULT TIMESTAMP('2011-09-01');
-- [cutoff, cutoff+90d): labels never enter the feature query.
SELECT customer_id, SUM(revenue) AS future_spend_90,
 MIN(invoice_date) AS next_purchase
FROM `YOUR_PROJECT.customer_analytics.clean_transactions`
WHERE invoice_date >= cutoff
 AND invoice_date < cutoff + INTERVAL 90 DAY
GROUP BY customer_id;
