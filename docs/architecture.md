# Architecture Notes

## Why Medallion Architecture?

The Medallion Architecture (Bronze → Silver → Gold) is the industry standard
pattern used by companies like Databricks, Microsoft, and Netflix for
organizing data lakes. Each layer has a specific purpose:

### Bronze Layer
- **Purpose:** Raw data storage — exactly as received from source
- **Why:** Preserves original data for audit, replay, and debugging
- **Rule:** Never transform here. Only ingest.

### Silver Layer
- **Purpose:** Cleaned, trusted, enriched data
- **Why:** Single source of truth for analysts. Data quality enforced here.
- **What we do:** Type casting, null removal, derived columns

### Gold Layer
- **Purpose:** Business-ready aggregations for reporting
- **Why:** Pre-aggregated tables are fast for dashboards and BI tools
- **What we do:** Group by dimensions, calculate KPIs

## Delta Lake Benefits
- **ACID Transactions:** Prevents data corruption during writes
- **Time Travel:** Can query previous versions of data
- **Schema Enforcement:** Rejects bad data automatically
- **Scalable:** Works from laptop-scale to petabyte-scale

## Data Flow
```
CSV File → bronze_sales → silver_sales → gold_* tables → Charts
```

## Table Summary

| Table | Layer | Rows (approx) | Key Columns Added |
|-------|-------|---------------|-------------------|
| bronze_sales | Bronze | ~10,000 | None (raw) |
| silver_sales | Silver | ~9,990 | Profit Margin %, Order Status, Shipping Days |
| gold_region_performance | Gold | 4 | Total Profit, Avg Margin %, Total Orders |
| gold_category_loss | Gold | ~15 | Total Loss, Loss Orders |
| gold_segment_analysis | Gold | 3 | Avg Order Value, Avg Margin % |
| gold_top_states | Gold | ~49 | Total Profit by State |
