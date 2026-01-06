"""
Extract ALL team member data from Excel and save as JSON for dashboard
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
    print("No records found in date range. Using all data...")
    df_week = df.copy()

# Target team members
target_members = [
    'Amani Syafiqah binti Mohd Razif',
    'Anthony Morton',
    'Chris Marinelli',
    'Dominic Joey Moncada',
    'Eduardo Jr Laygo',
    'Hayden Brunjes',
    'Khadija Tul Kobra',
    'Komal Gaikwad',
    'Md Momtazur Rahman',
    'Mohammed Arif Kandanari Nathar',
    'Muhammad Syafiq Ishamuddin',
    'Naveenkumar Rajagopal',
    'Parthena Savvidis',
    'Shahrul Azri Mohammad Faudzi',
    'Zabir Uddin Hussainy Syed'
]

# Filter for target team members
team_data = df_week[df_week['Employee Description'].isin(target_members)].copy()
print(f"Team member records: {len(team_data)}")

# Get actual members who have data
actual_members = sorted(team_data['Employee Description'].unique().tolist())
print(f"Actual members with data: {len(actual_members)}")
print(actual_members)

# Overall summary
total_hours = team_data['Internal Quantity'].sum()
billable_mask = team_data['Sales Amount'].fillna(0) > 0
billable_hours = team_data[billable_mask]['Internal Quantity'].sum()
utilization = (billable_hours / total_hours * 100) if total_hours > 0 else 0

# Employee-level analysis
employees = []
for emp_name in actual_members:
    emp_data = team_data[team_data['Employee Description'] == emp_name].copy()

    emp_total_hours = emp_data['Internal Quantity'].sum()
    emp_billable_hours = emp_data[emp_data['Sales Amount'].fillna(0) > 0]['Internal Quantity'].sum()
    emp_utilization = (emp_billable_hours / emp_total_hours * 100) if emp_total_hours > 0 else 0

    # Get position
    position = emp_data['Position Description'].iloc[0] if len(emp_data) > 0 else 'Unknown'

    # Projects for this employee
    emp_projects = emp_data.groupby(['Project', 'Project Description']).agg({
        'Internal Quantity': 'sum',
        'Sales Amount': 'sum'
    }).reset_index()
    emp_projects = emp_projects.sort_values('Internal Quantity', ascending=False).head(10)

    # Activities for this employee
    emp_activities = emp_data.groupby('Activity Description').agg({
        'Internal Quantity': 'sum'
    }).reset_index()
    emp_activities = emp_activities.sort_values('Internal Quantity', ascending=False).head(5)

    # Billing breakdown
    emp_billing = emp_data.groupby('Report Code Description').agg({
        'Internal Quantity': 'sum'
    }).reset_index()

    employees.append({
        'name': emp_name,
        'position': position,
        'totalHours': round(emp_total_hours, 2),
        'billableHours': round(emp_billable_hours, 2),
        'utilization': round(emp_utilization, 1),
        'revenue': round(emp_data['Sales Amount'].fillna(0).sum(), 2),
        'numProjects': int(emp_data['Project'].nunique()),
        'projects': [
            {
                'project': row['Project'],
                'description': row['Project Description'][:50] if pd.notna(row['Project Description']) else '',
                'hours': round(row['Internal Quantity'], 2),
                'revenue': round(row['Sales Amount'], 2)
            }
            for _, row in emp_projects.iterrows()
        ],
        'activities': [
            {
                'activity': row['Activity Description'][:40] if pd.notna(row['Activity Description']) else 'Unknown',
                'hours': round(row['Internal Quantity'], 2)
            }
            for _, row in emp_activities.iterrows()
        ],
        'billing': [
            {
                'type': row['Report Code Description'],
                'hours': round(row['Internal Quantity'], 2),
                'percentage': round(row['Internal Quantity'] / emp_total_hours * 100, 1) if emp_total_hours > 0 else 0
            }
            for _, row in emp_billing.iterrows()
        ]
    })

# Sort employees by total hours
employees.sort(key=lambda x: x['totalHours'], reverse=True)

# Project burn rates (overall)
project_burn = team_data.groupby(['Project', 'Project Description']).agg({
    'Internal Quantity': 'sum',
    'Internal Amount': 'sum',
    'Sales Amount': 'sum'
}).reset_index()

project_burn['Daily Hours'] = project_burn['Internal Quantity'] / 7
project_burn['Daily Revenue'] = project_burn['Sales Amount'].fillna(0) / 7
project_burn_sorted = project_burn.sort_values('Daily Revenue', ascending=False).head(15)

# Billing breakdown (overall)
billing_breakdown = team_data.groupby('Report Code Description').agg({
    'Internal Quantity': 'sum'
}).reset_index()

# Activity breakdown (overall)
activity_breakdown = team_data.groupby('Activity Description').agg({
    'Internal Quantity': 'sum',
    'Sales Amount': 'sum'
}).reset_index()
activity_breakdown = activity_breakdown.sort_values('Internal Quantity', ascending=False).head(10)

# Daily utilization (overall)
if team_data['Account Date'].notna().any():
    team_data['DateStr'] = team_data['Account Date'].dt.strftime('%Y-%m-%d')
    daily_data = team_data.groupby('DateStr').agg({
        'Internal Quantity': 'sum'
    }).reset_index()
    daily_data.columns = ['Date', 'Total Hours']

    billable_by_day = team_data[billable_mask].groupby('DateStr')['Internal Quantity'].sum()
    daily_data['Billable Hours'] = daily_data['Date'].map(billable_by_day).fillna(0)
    daily_data['Utilization'] = (daily_data['Billable Hours'] / daily_data['Total Hours'] * 100).round(1)
    daily_data = daily_data.sort_values('Date')
    daily_records = daily_data.to_dict('records')
else:
    daily_records = []

# Build JSON output
output = {
    'summary': {
        'totalHours': round(total_hours, 2),
        'billableHours': round(billable_hours, 2),
        'utilization': round(utilization, 1),
        'totalCost': round(team_data['Internal Amount'].sum(), 2),
        'totalRevenue': round(team_data['Sales Amount'].fillna(0).sum(), 2),
        'numProjects': int(team_data['Project'].nunique()),
        'numEmployees': len(actual_members),
        'avgDailyHours': round(total_hours / 7, 2) if total_hours > 0 else 0,
        'dateRange': f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
    },
    'employees': employees,
    'projects': [
        {
            'project': row['Project'],
            'description': row['Project Description'][:50] if pd.notna(row['Project Description']) else '',
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
            'percentage': round(row['Internal Quantity'] / total_hours * 100, 1) if total_hours > 0 else 0
        }
        for _, row in billing_breakdown.iterrows()
    ],
    'activities': [
        {
            'activity': row['Activity Description'][:40] if pd.notna(row['Activity Description']) else 'Unknown',
            'hours': round(row['Internal Quantity'], 2),
            'revenue': round(row['Sales Amount'], 2)
        }
        for _, row in activity_breakdown.iterrows()
    ],
    'daily': daily_records
}

# Save to JSON
output_file = r"C:\Code\Promethian  Light\team_dashboard_data.json"
with open(output_file, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nData saved to: {output_file}")
print(f"\nSummary:")
print(f"  Total Hours: {total_hours:.0f}h")
print(f"  Billable Hours: {billable_hours:.0f}h ({utilization:.1f}% utilization)")
print(f"  Total Revenue: ${team_data['Sales Amount'].fillna(0).sum():,.2f}")
print(f"  Team Members: {len(actual_members)}")
print(f"\nTop 3 contributors:")
for i, emp in enumerate(employees[:3], 1):
    print(f"  {i}. {emp['name']}: {emp['totalHours']}h ({emp['utilization']:.1f}% util)")
