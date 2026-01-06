"""Check database sizes for backup estimation"""
from pathlib import Path

mydata_path = Path.home() / '.mydata'
print(f'Checking: {mydata_path}')
print(f'Exists: {mydata_path.exists()}')

if mydata_path.exists():
    print('\nFiles in .mydata:')
    for f in mydata_path.iterdir():
        if f.is_file():
            size_mb = f.stat().st_size / (1024*1024)
            print(f'  {f.name}: {size_mb:.2f} MB')

    qdrant = mydata_path / 'qdrant'
    print(f'\nQdrant dir exists: {qdrant.exists()}')
    if qdrant.exists():
        qdrant_files = [f for f in qdrant.rglob('*') if f.is_file()]
        qdrant_size = sum(f.stat().st_size for f in qdrant_files)
        print(f'Qdrant total: {qdrant_size / (1024*1024):.2f} MB ({len(qdrant_files)} files)')

# Also check local mydata.db
local_db = Path('mydata/mydata.db')
if local_db.exists():
    print(f'\nLocal mydata.db: {local_db.stat().st_size / (1024*1024):.2f} MB')
