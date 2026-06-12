# Databricks notebook source
# NOTEBOOK: 02_silver_transformation
# PURPOSE:  Clean, fix types, and engineer new features from Bronze layer
# LAYER:    Silver — cleaned, trusted, enriched data

# ============================================================
# STEP 1: Import required functions from PySpark
# ============================================================

# col()     → refers to a column by name
# to_date() → converts a string to a proper DateType
# round()   → rounds a decimal to N places
# when()    → like IF/ELSE logic for columns
# datediff()→ calculates difference in days between two dates
from pyspark.sql.functions import col, to_date, round, when, datediff

# ============================================================
# STEP 2: Load data from the Bronze Delta table
# ============================================================

# Read the raw bronze table we created in notebook 01
df_bronze = spark.table("bronze_sales")

print(f"Bronze rows loaded: {df_bronze.count()}")

# ============================================================
# STEP 3: Fix data types
# ============================================================

# The CSV reader may have read dates as strings — convert them to DateType
# The format "MM/dd/yyyy" matches values like "01/03/2017"
# Sales, Profit, Discount need to be DoubleType for math operations

df_silver = df_bronze \
    .withColumn("Order Date",  to_date(col("Order Date"),  "MM/dd/yyyy")) \
    .withColumn("Ship Date",   to_date(col("Ship Date"),   "MM/dd/yyyy")) \
    .withColumn("Sales",       col("Sales").cast("double")) \
    .withColumn("Profit",      col("Profit").cast("double")) \
    .withColumn("Discount",    col("Discount").cast("double")) \
    .withColumn("Quantity",    col("Quantity").cast("integer"))

# ============================================================
# STEP 4: Remove null / bad rows
# ============================================================

# Drop rows where critical business columns are missing
# We cannot calculate insights without Order ID, Sales, or Profit
rows_before = df_silver.count()

df_silver = df_silver.dropna(subset=["Order ID", "Sales", "Profit"])

rows_after = df_silver.count()
print(f"Rows removed due to nulls: {rows_before - rows_after}")

# ============================================================
# STEP 5: Add derived business columns
# ============================================================

# --- Profit Margin % ---
# Formula: (Profit / Sales) * 100
# round(..., 2) keeps it to 2 decimal places
# We also guard against division by zero using when()
df_silver = df_silver.withColumn(
    "Profit Margin %",
    when(col("Sales") == 0, 0.0)
    .otherwise(round((col("Profit") / col("Sales")) * 100, 2))
)

# --- Order Status ---
# Simple flag: was this order profitable or a loss?
# Useful for filtering and counting loss orders quickly
df_silver = df_silver.withColumn(
    "Order Status",
    when(col("Profit") < 0, "Loss").otherwise("Profitable")
)

# --- Shipping Days ---
# How many days between when order was placed vs when it shipped?
# datediff(end_date, start_date) returns an integer
df_silver = df_silver.withColumn(
    "Shipping Days",
    datediff(col("Ship Date"), col("Order Date"))
)

# ============================================================
# STEP 6: Print a summary to verify the transformation
# ============================================================

total_orders    = df_silver.count()
loss_orders     = df_silver.filter(col("Order Status") == "Loss").count()
profitable      = total_orders - loss_orders
avg_margin      = df_silver.selectExpr("round(avg(`Profit Margin %`), 2) as avg_margin").collect()[0]["avg_margin"]
avg_ship_days   = df_silver.selectExpr("round(avg(`Shipping Days`), 1) as avg_ship").collect()[0]["avg_ship"]

print("=== SILVER LAYER SUMMARY ===")
print(f"  Total Orders     : {total_orders}")
print(f"  Profitable Orders: {profitable}")
print(f"  Loss Orders      : {loss_orders}")
print(f"  Avg Profit Margin: {avg_margin}%")
print(f"  Avg Shipping Days: {avg_ship_days} days")

# Show a few rows to confirm new columns look correct
print("\n=== SAMPLE ROWS WITH NEW COLUMNS ===")
df_silver.select(
    "Order ID", "Order Date", "Ship Date",
    "Sales", "Profit", "Profit Margin %",
    "Order Status", "Shipping Days"
).show(5, truncate=False)

# ============================================================
# STEP 7: Save as Silver Delta table
# ============================================================

df_silver.write.format("delta") \
    .mode("overwrite") \
    .saveAsTable("silver_sales")

print("✅ Silver layer complete — Delta table 'silver_sales' created successfully.")
