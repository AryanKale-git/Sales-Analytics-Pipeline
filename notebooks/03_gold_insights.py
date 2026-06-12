# Databricks notebook source
# NOTEBOOK: 03_gold_insights
# PURPOSE:  Create 4 business-ready aggregation tables from Silver layer
# LAYER:    Gold — business insights, ready for reporting/dashboards

# ============================================================
# STEP 1: Import aggregation functions
# ============================================================

# sum()   → total of a column
# avg()   → average of a column
# count() → count rows
# desc()  → sort descending
# col()   → reference a column
from pyspark.sql.functions import sum, avg, count, desc, col, round

# ============================================================
# STEP 2: Load Silver table
# ============================================================

df = spark.table("silver_sales")
print(f"Silver rows loaded: {df.count()}")

# ============================================================
# GOLD TABLE 1: Regional Performance
# Business Question: Which region is most profitable?
# ============================================================

gold_region = df.groupBy("Region") \
    .agg(
        round(sum("Profit"),           2).alias("Total Profit"),
        round(sum("Sales"),            2).alias("Total Sales"),
        round(avg("Profit Margin %"),  2).alias("Avg Margin %"),
        count("Order ID")               .alias("Total Orders"),
        round(avg("Discount"),         3).alias("Avg Discount")
    ) \
    .orderBy(desc("Total Profit"))

# Save to Gold Delta table
gold_region.write.format("delta") \
    .mode("overwrite") \
    .saveAsTable("gold_region_performance")

print("\n=== GOLD TABLE 1: Regional Performance ===")
gold_region.show(truncate=False)

# ============================================================
# GOLD TABLE 2: Category Loss Analysis
# Business Question: Which sub-categories lose the most money?
# ============================================================

gold_loss = df.filter(col("Order Status") == "Loss") \
    .groupBy("Category", "Sub-Category") \
    .agg(
        round(sum("Profit"),  2).alias("Total Loss"),
        count("Order ID")      .alias("Loss Orders"),
        round(avg("Discount"), 3).alias("Avg Discount on Loss Orders")
    ) \
    .orderBy("Total Loss")   # ascending = worst losses first

gold_loss.write.format("delta") \
    .mode("overwrite") \
    .saveAsTable("gold_category_loss")

print("\n=== GOLD TABLE 2: Category Loss Analysis ===")
gold_loss.show(15, truncate=False)

# ============================================================
# GOLD TABLE 3: Customer Segment Analysis
# Business Question: Which customer segment is most valuable?
# ============================================================

gold_segment = df.groupBy("Segment") \
    .agg(
        round(sum("Profit"),           2).alias("Total Profit"),
        round(sum("Sales"),            2).alias("Total Sales"),
        round(avg("Sales"),            2).alias("Avg Order Value"),
        round(avg("Profit Margin %"),  2).alias("Avg Margin %"),
        round(avg("Discount"),         3).alias("Avg Discount"),
        count("Order ID")               .alias("Total Orders")
    ) \
    .orderBy(desc("Total Profit"))

gold_segment.write.format("delta") \
    .mode("overwrite") \
    .saveAsTable("gold_segment_analysis")

print("\n=== GOLD TABLE 3: Customer Segment Analysis ===")
gold_segment.show(truncate=False)

# ============================================================
# GOLD TABLE 4: State-Level Performance
# Business Question: Which states are top 10 and bottom 10?
# ============================================================

gold_states = df.groupBy("State") \
    .agg(
        round(sum("Profit"),  2).alias("Total Profit"),
        round(sum("Sales"),   2).alias("Total Sales"),
        count("Order ID")      .alias("Total Orders")
    ) \
    .orderBy(desc("Total Profit"))

gold_states.write.format("delta") \
    .mode("overwrite") \
    .saveAsTable("gold_top_states")

print("\n=== GOLD TABLE 4: Top 10 States ===")
gold_states.show(10, truncate=False)

print("\n=== GOLD TABLE 4: Bottom 10 States ===")
gold_states.orderBy("Total Profit").show(10, truncate=False)

# ============================================================
# FINAL SUMMARY
# ============================================================
print("\n✅ Gold layer complete — 4 business insight tables created:")
print("   → gold_region_performance")
print("   → gold_category_loss")
print("   → gold_segment_analysis")
print("   → gold_top_states")
