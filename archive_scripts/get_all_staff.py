import sqlite3

conn = sqlite3.connect('mydata/mydata.db')
cursor = conn.cursor()

# Get all regions
cursor.execute('SELECT DISTINCT region FROM staff_v2 ORDER BY region')
regions = cursor.fetchall()
print('Regions:', [r[0] for r in regions])

# Get all staff
cursor.execute('SELECT id, name, position, region FROM staff_v2 ORDER BY region, name')
staff = cursor.fetchall()

print('\n\nAll Staff by Region:')
print('=' * 80)
current_region = None
for s in staff:
    region = s[3] if s[3] else 'Unknown'
    if region != current_region:
        print(f'\n{region}:')
        print('-' * 80)
        current_region = region
    print(f'  {s[1]} - {s[2]} (ID: {s[0]})')

print(f'\n\nTotal Staff: {len(staff)}')
conn.close()
