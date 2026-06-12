# Databricks notebook source
# NOTEBOOK: 04_visualizations
# PURPOSE:  Convert Gold tables to Pandas and create business charts
# NOTE:     Run this AFTER 03_gold_insights.py

# ============================================================
# STEP 1: Import libraries
# ============================================================

import matplotlib.pyplot as plt   # main charting library
import matplotlib.ticker as mtick # for % formatting on axes
import pandas as pd               # Pandas for chart-friendly data format

# Use a clean, professional chart style
plt.style.use('seaborn-v0_8-whitegrid')

# ============================================================
# CHART 1: Regional Profit Comparison (Bar Chart)
# ============================================================

# Load Gold table and convert to Pandas
region_pd = spark.table("gold_region_performance").toPandas()

fig, ax = plt.subplots(figsize=(8, 5))

# Color bars: green for positive profit, red for negative
colors = ['#2ecc71' if v > 0 else '#e74c3c' for v in region_pd["Total Profit"]]

bars = ax.bar(region_pd["Region"], region_pd["Total Profit"], color=colors, edgecolor='white', linewidth=0.8)

# Add value labels on top of each bar
for bar, val in zip(bars, region_pd["Total Profit"]):
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 500,
            f'${val:,.0f}',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

ax.set_title('Total Profit by Region', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Region', fontsize=11)
ax.set_ylabel('Total Profit (USD)', fontsize=11)
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'${x:,.0f}'))
plt.tight_layout()
plt.savefig('/tmp/chart1_region_profit.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ Chart 1 saved")

# ============================================================
# CHART 2: Top 10 Loss-Making Sub-Categories (Horizontal Bar)
# ============================================================

loss_pd = spark.table("gold_category_loss").toPandas().head(10)

fig, ax = plt.subplots(figsize=(10, 6))

bars = ax.barh(loss_pd["Sub-Category"], loss_pd["Total Loss"],
               color='#e74c3c', edgecolor='white', linewidth=0.8)

# Add value labels inside each bar
for bar, val in zip(bars, loss_pd["Total Loss"]):
    ax.text(val - abs(val)*0.05, bar.get_y() + bar.get_height()/2,
            f'${val:,.0f}',
            ha='right', va='center', fontsize=9, color='white', fontweight='bold')

ax.set_title('Top 10 Loss-Making Sub-Categories', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Total Loss (USD)', fontsize=11)
ax.set_ylabel('Sub-Category', fontsize=11)
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'${x:,.0f}'))
plt.tight_layout()
plt.savefig('/tmp/chart2_category_loss.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ Chart 2 saved")

# ============================================================
# CHART 3: Customer Segment Comparison (Grouped Bar)
# ============================================================

seg_pd = spark.table("gold_segment_analysis").toPandas()

x = range(len(seg_pd["Segment"]))
width = 0.35

fig, ax1 = plt.subplots(figsize=(9, 5))
ax2 = ax1.twinx()   # second Y axis for Avg Margin %

bars1 = ax1.bar([i - width/2 for i in x], seg_pd["Total Profit"],
                width, label='Total Profit', color='#3498db', alpha=0.85)
bars2 = ax2.bar([i + width/2 for i in x], seg_pd["Avg Margin %"],
                width, label='Avg Margin %', color='#f39c12', alpha=0.85)

ax1.set_xlabel('Customer Segment', fontsize=11)
ax1.set_ylabel('Total Profit (USD)', fontsize=11, color='#3498db')
ax2.set_ylabel('Avg Profit Margin %', fontsize=11, color='#f39c12')
ax1.set_xticks(list(x))
ax1.set_xticklabels(seg_pd["Segment"])
ax1.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f'${v:,.0f}'))
ax2.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f'{v:.1f}%'))

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

plt.title('Customer Segment: Total Profit vs Avg Margin %', fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('/tmp/chart3_segment_analysis.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ Chart 3 saved")

# ============================================================
# CHART 4: Top 10 vs Bottom 10 States (Color-Coded Bar)
# ============================================================

states_pd = spark.table("gold_top_states").toPandas()

top10    = states_pd.head(10)
bottom10 = states_pd.tail(10).sort_values("Total Profit")
combined = pd.concat([top10, bottom10]).drop_duplicates()
combined = combined.sort_values("Total Profit", ascending=True)

colors = ['#e74c3c' if v < 0 else '#2ecc71' for v in combined["Total Profit"]]

fig, ax = plt.subplots(figsize=(10, 8))
bars = ax.barh(combined["State"], combined["Total Profit"],
               color=colors, edgecolor='white', linewidth=0.5)

ax.axvline(x=0, color='black', linewidth=0.8, linestyle='--', alpha=0.5)
ax.set_title('Top 10 vs Bottom 10 States by Total Profit', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Total Profit (USD)', fontsize=11)
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'${x:,.0f}'))
plt.tight_layout()
plt.savefig('/tmp/chart4_top_bottom_states.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ Chart 4 saved")

print("\n✅ All 4 charts generated and saved to /tmp/")
print("   Take screenshots of each chart to add to your GitHub README.")
