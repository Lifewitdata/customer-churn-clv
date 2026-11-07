SELECT COUNT(*) AS invalid_rows FROM clean_transactions
WHERE customer_id IS NULL OR invoice_date IS NULL OR quantity <= 0 OR unit_price <= 0 OR revenue <= 0;
