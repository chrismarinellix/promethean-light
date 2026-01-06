"""
Extract PM data from Excel and save as JSON for dashboard
"""

import pandas as pd
import json
from datetime import datetime, date

# Read the Excel file
file_path = r"C:\Users\chris.marinelli\Downloads\List_20251123_215037.xlsx"
print(f"Reading Excel file: {file_path}")
df = pd.read_excel(file_path)

print(f"Total records loaded: {len(df)}")

# Handle Account Date - could be dates, datetimes, or formulas
def parse_account_date(val):
    if pd.isna(val):
        return None
    if isinstance(val, (datetime, date)):
        return pd.to_datetime(val)
    if isinstance(val, str):
        return pd.to_datetime(val, errors='coerce')
    # For Excel serial dates
    try:
        return pd.to_datetime(val, unit='D', origin='1899-12-30')
    except:
        return None

df['Account Date'] = df['Account Date'].apply(parse_account_date)

# Filter for last week (Nov 16-23, 2025)
start_date = pd.to_datetime('2025-11-16')
end_date = pd.to_datetime('2025-11-23')
df_week = df[(df['Account Date'] >= start_date) & (df['Account Date'] <= end_date)].copy()

print(f"Records in last week: {len(df_week)}")

if len(df_week) == 0:
    print("No records found in date range. Checking all dates...")
    print("Sample dates:", df['Account Date'].dropna().head(10).tolist())
    print("Min date:", df['Account Date'].min())
    print("Max date:", df['Account Date'].max())
    # Use all data if no weekly data found
    df_week = df.copy()
    print(f"Using all {len(df_week)} records instead")

# Identify Project Managers
pm_titles = ['Project Manager', 'Program Manager', 'Lead', 'Manager']
df_week['Is_PM'] = df_week['Position Description'].fillna('').apply(
    lambda x: any(title.lower() in str(x).lower() for title in pm_titles)
)

pm_data = df_week[df_week['Is_PM']].copy()
print(f"PM records: {len(pm_data)}")

if len(pm_data) == 0:
    print("No PM records found. Using all records...")
    pm_data = df_week.copy()

# Calculate metrics
total_hours = pm_data['Internal Quantity'].sum()
billable_mask = pm_data['Sales Amount'].fillna(0) > 0
billable_hours = pm_data[billable_mask]['Internal Quantity'].sum()
utilization = (billable_hours / total_hours * 100) if total_hours > 0 else 0

# Project burn rates
project_burn = pm_data.groupby(['Project', 'Project Description']).agg({
    'Internal Quantity': 'sum',
    'Internal Amount': 'sum',
    'Sales Amount': 'sum'
}).reset_index()

project_burn['Daily Hours'] = project_burn['Internal Quantity'] / 7
project_burn['Daily Revenue'] = project_burn['Sales Amount'].fillna(0) / 7
project_burn_sorted = project_burn.sort_values('Daily Revenue', ascending=False).head(15)

# Billing breakdown
billing_breakdown = pm_data.groupby('Report Code Description').agg({
    'Internal Quantity': 'sum'
}).reset_index()

# Activity breakdown
activity_breakdown = pm_data.groupby('Activity Description').agg({
    'Internal Quantity': 'sum',
    'Sales Amount': 'sum'
}).reset_index()
activity_breakdown = activity_breakdown.sort_values('Internal Quantity', ascending=False).head(10)

# Daily utilization
pm_data['DateStr'] = pm_data['Account Date'].dt.strftime('%Y-%m-%d')
daily_data = pm_data.groupby('DateStr').agg({
    'Internal Quantity': 'sum'
}).reset_index()
daily_data.columns = ['Date', 'Total Hours']

billable_by_day = pm_data[billable_mask].groupby('DateStr')['Internal Quantity'].sum()
daily_data['Billable Hours'] = daily_data['Date'].map(billable_by_day).fillna(0)
daily_data['Utilization'] = (daily_data['Billable Hours'] / daily_data['Total Hours'] * 100).round(1)
daily_data = daily_data.sort_values('Date')

# Build JSON output
output = {
    'summary': {
        'totalHours': round(total_hours, 2),
        'billableHours': round(billable_hours, 2),
        'utilization': round(utilization, 1),
        'totalCost': round(pm_data['Internal Amount'].sum(), 2),
        'totalRevenue': round(pm_data['Sales Amount'].fillna(0).sum(), 2),
        'numProjects': int(pm_data['Project'].nunique()),
        'avgDailyHours': round(total_hours / 7, 2),
        'dateRange': f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
    },
    'projects': [
        {
            'project': row['Project'],
            'description': row['Project Description'][:50],
            'totalHours': round(row['Internal Quantity'], 2),
            'dailyHours': round(row['Daily Hours'], 2),
            'totalRevenue': round(row['Sales Amount'], 2),
            'dailyRevenue': round(row['Daily Revenue'], 2)
        }
        for _, row in project_burn_sorted.iterrows()
    ],
    'billing': [
        {
            'type': row['Report Code Description'],
            'hours': round(row['Internal Quantity'], 2),
            'percentage': round(row['Internal Quantity'] / total_hours * 100, 1)
        }
        for _, row in billing_breakdown.iterrows()
    ],
    'activities': [
        {
            'activity': row['Activity Description'][:40],
            'hours': round(row['Internal Quantity'], 2),
            'revenue': round(row['Sales Amount'], 2)
        }
        for _, row in activity_breakdown.iterrows()
    ],
    'daily': daily_data.to_dict('records')
}

# Save to JSON
output_file = r"C:\Code\Promethian  Light\pm_dashboard_data.json"
with open(output_file, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nData saved to: {output_file}")
print(f"Summary: {total_hours:.0f}h total, {billable_hours:.0f}h billable ({utilization:.1f}% utilization)")
print(f"Top project: {project_burn_sorted.iloc[0]['Project']} - ${project_burn_sorted.iloc[0]['Daily Revenue']:.2f}/day")
