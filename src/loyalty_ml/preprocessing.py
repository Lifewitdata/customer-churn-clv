import pandas as pd

def clean(raw):
    x = raw.copy()
    audit = {'raw_rows':len(x)}
    x['invoice_date'] = pd.to_datetime(x.invoice_date, errors='coerce')
    # Conservative exact duplicate policy; source has no unique line ID.
    for name, mask in [
        ('exact_duplicates',x.duplicated()),
    ]:
        audit[name] = int(mask.sum()); x = x.loc[~mask].copy()
    mask = x.customer_id.isna() | x.invoice_date.isna()
    audit['missing_customer_or_date'] = int(mask.sum()); x = x.loc[~mask].copy()
    mask = x.invoice.astype(str).str.upper().str.startswith('C') | (x.quantity <= 0) | (x.unit_price <= 0)
    audit['cancellations_nonpositive'] = int(mask.sum()); x = x.loc[~mask].copy()
    # Codes with no digit are administrative lines (postage, manual adjustments, fees).
    mask = ~x.stock_code.astype(str).str.match(r'^\d')
    audit['administrative_lines'] = int(mask.sum()); x = x.loc[~mask].copy()
    # Last observed calendar day may be incomplete: discard it for consistent censoring.
    observation_end = raw.invoice_date.max().normalize()
    mask = x.invoice_date >= observation_end
    audit['partial_final_day'] = int(mask.sum()); x = x.loc[~mask].copy()
    x['customer_id'] = x.customer_id.astype('int64').astype(str)
    x['invoice'] = x.invoice.astype(str)
    x['stock_code'] = x.stock_code.astype(str)
    x['description'] = x.description.astype('string')
    x['country'] = x.country.astype('string')
    x['revenue'] = x.quantity * x.unit_price
    audit.update(clean_rows=len(x), customers=x.customer_id.nunique(), invoices=x.invoice.nunique(),
                 observation_end_exclusive=str(observation_end.date()), gross_revenue=float(x.revenue.sum()))
    assert sum(audit[k] for k in ['exact_duplicates','missing_customer_or_date','cancellations_nonpositive','administrative_lines','partial_final_day']) + len(x) == len(raw)
    return x, audit
