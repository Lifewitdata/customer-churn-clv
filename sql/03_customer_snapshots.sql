-- One record per customer active in the preceding 180 days.
SELECT DISTINCT customer_id FROM clean_transactions
WHERE invoice_date >= CAST($cutoff AS TIMESTAMP) - INTERVAL 180 DAY
  AND invoice_date < CAST($cutoff AS TIMESTAMP);
