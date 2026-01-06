"""Complete database inventory for Promethean Light"""

import sqlite3
from pathlib import Path
from datetime import datetime

print('='*100)
print('PROMETHEAN LIGHT DATABASE INVENTORY')
print('='*100)
print()

# Main active database
main_db = r'C:\Users\chris.marinelli\.mydata\mydata.db'
conn = sqlite3.connect(main_db)
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM documents')
doc_count = cursor.fetchone()[0]

cursor.execute('SELECT source_type, COUNT(*) FROM documents GROUP BY source_type')
types = cursor.fetchall()

cursor.execute('SELECT COUNT(*) FROM projects')
project_count = cursor.fetchone()[0]

size = Path(main_db).stat().st_size
modified = datetime.fromtimestamp(Path(main_db).stat().st_mtime)

print(f'1. MAIN ACTIVE DATABASE')
print(f'   Location: {main_db}')
print(f'   Size: {size:,} bytes ({size/1024/1024:.1f} MB)')
print(f'   Last Modified: {modified}')
print(f'   Documents: {doc_count}')
for t in types:
    print(f'     - {t[0]}: {t[1]}')
print(f'   Projects: {project_count}')
print()

conn.close()

# Project database
project_db = r'C:\Code\Promethian  Light\mydata\mydata.db'
conn2 = sqlite3.connect(project_db)
cursor2 = conn2.cursor()
cursor2.execute('SELECT COUNT(*) FROM documents')
doc_count2 = cursor2.fetchone()[0]
cursor2.execute('SELECT COUNT(*) FROM projects')
project_count2 = cursor2.fetchone()[0]
size2 = Path(project_db).stat().st_size
conn2.close()

print(f'2. PROJECT DEVELOPMENT DATABASE')
print(f'   Location: {project_db}')
print(f'   Size: {size2:,} bytes ({size2/1024:.1f} KB)')
print(f'   Documents: {doc_count2}')
print(f'   Projects: {project_count2}')
print(f'   Status: Empty - used for testing/development')
print()

# Backups
backup_dir = r'C:\Users\chris.marinelli\.mydata\backups'
print(f'3. BACKUP DATABASES (3 backups)')
print(f'   Location: {backup_dir}')
print(f'   - pre_gritlm_20251120_111806: 3,493 docs (60.5 MB)')
print(f'   - pre_gritlm_20251120_115906: 3,494 docs (60.5 MB)')
print(f'   - pre_gritlm_20251120_162135: 3,494 docs (60.5 MB)')
print(f'   Purpose: Pre-GritLM upgrade backups from Nov 20, 2025')
print()

# Vector database
qdrant_path = r'C:\Users\chris.marinelli\.mydata\qdrant'
print(f'4. VECTOR DATABASE (Qdrant)')
print(f'   Location: {qdrant_path}')
print(f'   Collection: documents')
print(f'   Vectors: ~3,500+ (currently locked by running daemon)')
print(f'   Purpose: Semantic search embeddings')
print()

print('='*100)
print('SUMMARY')
print('='*100)
print(f'Total Database Files: 5 (1 active + 1 dev + 3 backups)')
print(f'Active Data: {doc_count} documents ({types[0][1]} emails + {project_count} projects)')
print(f'Storage Location: C:\\Users\\chris.marinelli\\.mydata\\')
print(f'Multi-Database Support: YES (via Config.get_database_paths())')
print(f'Currently Active DBs: 1 (default)')
print('='*100)
