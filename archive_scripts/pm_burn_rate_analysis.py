"""
Project Manager Burn Rate Analysis and Visualization
Analyzes time allocation, utilization, and burn rates from timesheet data
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np

# Read the Excel file
file_path = r"C:\Users\chris.marinelli\Downloads\List_20251123_215037.xlsx"
print(f"Reading Excel file: {file_path}")
df = pd.read_excel(file_path)

print(f"Total records loaded: {len(df)}")
print(f"Columns: {df.columns.tolist()}")

# Convert Account Date to datetime
df['Account Date'] = pd.to_datetime(df['Account Date'])

# Filter for last week (Nov 16-23, 2025)
start_date = datetime(2025, 11, 16)
end_date = datetime(2025, 11, 23)
df_week = df[(df['Account Date'] >= start_date) & (df['Account Date'] <= end_date)].copy()

print(f"\nRecords in last week (Nov 16-23): {len(df_week)}")

# Identify Project Managers
pm_titles = ['Project Manager', 'Program Manager', 'Lead', 'Manager']
df_week['Is_PM'] = df_week['Position Description'].fillna('').apply(
    lambda x: any(title.lower() in str(x).lower() for title in pm_titles)
)

pm_data = df_week[df_week['Is_PM']].copy()
print(f"Project Manager records: {len(pm_data)}")

# Get unique PMs
unique_pms = pm_data['Employee Description'].unique()
print(f"Unique Project Managers: {unique_pms.tolist()}")

# Calculate burn rate by project
project_burn = pm_data.groupby(['Project', 'Project Description']).agg({
    'Internal Quantity': 'sum',
    'Internal Amount': 'sum',
    'Sales Amount': 'sum'
}).reset_index()

project_burn.columns = ['Project', 'Project Description', 'Total Hours', 'Total Cost', 'Total Revenue']
project_burn['Daily Hours'] = project_burn['Total Hours'] / 7
project_burn['Daily Cost'] = project_burn['Total Cost'] / 7
project_burn['Daily Revenue'] = project_burn['Total Revenue'] / 7

# Sort by daily revenue and get top 15
project_burn_sorted = project_burn.sort_values('Daily Revenue', ascending=False).head(15)

# Billing type breakdown
billing_breakdown = pm_data.groupby('Report Code Description').agg({
    'Internal Quantity': 'sum',
    'Internal Amount': 'sum',
    'Sales Amount': 'sum'
}).reset_index()

billing_breakdown.columns = ['Billing Type', 'Hours', 'Cost', 'Revenue']

# Activity breakdown
activity_breakdown = pm_data.groupby('Activity Description').agg({
    'Internal Quantity': 'sum',
    'Internal Amount': 'sum',
    'Sales Amount': 'sum'
}).reset_index()

activity_breakdown.columns = ['Activity', 'Hours', 'Cost', 'Revenue']
activity_breakdown = activity_breakdown.sort_values('Hours', ascending=False)

# Daily utilization
daily_data = pm_data.groupby('Account Date').agg({
    'Internal Quantity': 'sum',
    'Sales Amount': 'sum'
}).reset_index()

daily_data.columns = ['Date', 'Total Hours', 'Revenue']
daily_data['Billable Hours'] = pm_data[pm_data['Sales Amount'] > 0].groupby('Account Date')['Internal Quantity'].sum().reindex(daily_data['Date'], fill_value=0).values
daily_data['Utilization %'] = (daily_data['Billable Hours'] / daily_data['Total Hours'] * 100).fillna(0)

# Create visualizations
fig = plt.figure(figsize=(20, 12))

# 1. Burn Rate by Project (Top 15)
ax1 = plt.subplot(2, 2, 1)
y_pos = np.arange(len(project_burn_sorted))
bars = ax1.barh(y_pos, project_burn_sorted['Daily Revenue'], color='#2E86AB')

# Add hours labels
for i, (rev, hrs) in enumerate(zip(project_burn_sorted['Daily Revenue'], project_burn_sorted['Daily Hours'])):
    ax1.text(rev + 50, i, f'{hrs:.1f}h/day', va='center', fontsize=9)

ax1.set_yticks(y_pos)
ax1.set_yticklabels([f"{row['Project']}\n{row['Project Description'][:30]}" for _, row in project_burn_sorted.iterrows()], fontsize=8)
ax1.set_xlabel('Daily Revenue ($)', fontsize=10)
ax1.set_title('Top 15 Projects by Daily Burn Rate (Last Week)', fontsize=12, fontweight='bold')
ax1.grid(axis='x', alpha=0.3)

# 2. Billing Type Breakdown
ax2 = plt.subplot(2, 2, 2)
colors = ['#A23B72', '#F18F01', '#C73E1D', '#6A994E']
wedges, texts, autotexts = ax2.pie(
    billing_breakdown['Hours'],
    labels=billing_breakdown['Billing Type'],
    autopct=lambda pct: f'{pct:.1f}%\n({pct/100 * billing_breakdown["Hours"].sum():.0f}h)',
    colors=colors,
    startangle=90
)
ax2.set_title('Time Allocation by Billing Type', fontsize=12, fontweight='bold')
for text in texts:
    text.set_fontsize(9)
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(8)

# 3. Activity Category Distribution (Top 10)
ax3 = plt.subplot(2, 2, 3)
top_activities = activity_breakdown.head(10)
bars = ax3.bar(range(len(top_activities)), top_activities['Hours'], color='#118AB2')
ax3.set_xticks(range(len(top_activities)))
ax3.set_xticklabels([act[:25] for act in top_activities['Activity']], rotation=45, ha='right', fontsize=8)
ax3.set_ylabel('Hours', fontsize=10)
ax3.set_title('Top 10 Activities by Time Spent (Last Week)', fontsize=12, fontweight='bold')
ax3.grid(axis='y', alpha=0.3)

# Add value labels on bars
for i, (hrs, rev) in enumerate(zip(top_activities['Hours'], top_activities['Revenue'])):
    ax3.text(i, hrs + 1, f'{hrs:.0f}h\n${rev:,.0f}', ha='center', va='bottom', fontsize=8)

# 4. Daily Utilization Trend
ax4 = plt.subplot(2, 2, 4)
ax4.plot(daily_data['Date'], daily_data['Total Hours'], marker='o', label='Total Hours', linewidth=2, markersize=8, color='#073B4C')
ax4.plot(daily_data['Date'], daily_data['Billable Hours'], marker='s', label='Billable Hours', linewidth=2, markersize=8, color='#06D6A0')

# Add utilization percentage on secondary y-axis
ax4_2 = ax4.twinx()
ax4_2.plot(daily_data['Date'], daily_data['Utilization %'], marker='^', label='Utilization %', linewidth=2, markersize=8, color='#EF476F', linestyle='--')
ax4_2.set_ylabel('Utilization %', fontsize=10, color='#EF476F')
ax4_2.tick_params(axis='y', labelcolor='#EF476F')
ax4_2.set_ylim(0, 100)

ax4.set_xlabel('Date', fontsize=10)
ax4.set_ylabel('Hours', fontsize=10)
ax4.set_title('Daily Utilization Trend (Last Week)', fontsize=12, fontweight='bold')
ax4.xaxis.set_major_formatter(mdates.DateFormatter('%a\n%b %d'))
ax4.grid(True, alpha=0.3)
ax4.legend(loc='upper left', fontsize=9)
ax4_2.legend(loc='upper right', fontsize=9)

plt.tight_layout()
output_file = r"C:\Code\Promethian  Light\pm_burn_rate_dashboard.png"
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\nDashboard saved to: {output_file}")

# Save detailed data to CSV
project_burn_sorted.to_csv(r"C:\Code\Promethian  Light\pm_project_burn_rates.csv", index=False)
billing_breakdown.to_csv(r"C:\Code\Promethian  Light\pm_billing_breakdown.csv", index=False)
activity_breakdown.to_csv(r"C:\Code\Promethian  Light\pm_activity_breakdown.csv", index=False)
daily_data.to_csv(r"C:\Code\Promethian  Light\pm_daily_utilization.csv", index=False)

print("\nCSV files saved:")
print("  - pm_project_burn_rates.csv")
print("  - pm_billing_breakdown.csv")
print("  - pm_activity_breakdown.csv")
print("  - pm_daily_utilization.csv")

# Print summary statistics
print("\n" + "="*80)
print("SUMMARY STATISTICS - LAST WEEK (Nov 16-23, 2025)")
print("="*80)
print(f"\nTotal PM Hours: {pm_data['Internal Quantity'].sum():.2f}")
print(f"Total Billable Hours: {pm_data[pm_data['Sales Amount'] > 0]['Internal Quantity'].sum():.2f}")
print(f"Overall Utilization: {(pm_data[pm_data['Sales Amount'] > 0]['Internal Quantity'].sum() / pm_data['Internal Quantity'].sum() * 100):.1f}%")
print(f"\nTotal Cost: ${pm_data['Internal Amount'].sum():,.2f}")
print(f"Total Revenue: ${pm_data['Sales Amount'].sum():,.2f}")
print(f"Net Margin: ${(pm_data['Sales Amount'].sum() - pm_data['Internal Amount'].sum()):,.2f}")
print(f"\nNumber of Projects: {pm_data['Project'].nunique()}")
print(f"Number of Activities: {pm_data['Activity Description'].nunique()}")
print(f"Average Hours per Day: {pm_data['Internal Quantity'].sum() / 7:.2f}")

print("\nTop 5 Projects by Revenue:")
for i, row in project_burn_sorted.head(5).iterrows():
    print(f"  {row['Project']}: ${row['Total Revenue']:,.2f} ({row['Total Hours']:.1f}h)")

print("\n" + "="*80)
print("Analysis complete!")
print("="*80)
