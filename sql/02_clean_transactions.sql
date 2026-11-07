-- Audit the result of preprocessing.py (gross positive product purchases only).
SELECT COUNT(*) AS rows, COUNT(DISTINCT customer_id) AS customers,
       COUNT(DISTINCT invoice) AS invoices, SUM(revenue) AS gross_revenue
FROM clean_transactions;
