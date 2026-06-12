# Databricks notebook source
# NOTEBOOK: 01_bronze_ingestion
# PURPOSE:  Read raw Superstore CSV and save as Bronze Delta table
# LAYER:    Bronze — raw data, no transformations

# ============================================================
# STEP 1: Read the raw CSV file from Databricks FileStore
# ============================================================

# spark is automatically available in Databricks — no import needed
# We read the CSV with:
#   header=true  → first row is column names
#   inferSchema  → auto-detect data types (int, string, etc.)

df_raw = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load("/FileStore/tables/superstore.csv")

# ============================================================
# STEP 2: Inspect the raw data before saving
# ============================================================

# Print the schema — shows all column names and their detected types
print("=== SCHEMA ===")
df_raw.printSchema()

# Show first 5 rows to visually verify the data loaded correctly
print("=== FIRST 5 ROWS ===")
df_raw.show(5, truncate=False)

# Count total rows — gives us a baseline number
total_rows = df_raw.count()
print(f"=== TOTAL ROWS LOADED: {total_rows} ===")

# ============================================================
# STEP 3: Save as Bronze Delta table
# ============================================================

# Delta format is a versioned, ACID-compliant storage format
# mode("overwrite") means: replace the table if it already exists
# saveAsTable saves it to the Databricks metastore as "bronze_sales"

df_raw.write.format("delta") \
    .mode("overwrite") \
    .saveAsTable("bronze_sales")

# Confirm completion
print("✅ Bronze layer complete — Delta table 'bronze_sales' created successfully.")
print(f"   Total rows saved: {total_rows}")
