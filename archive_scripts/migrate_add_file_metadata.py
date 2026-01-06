"""Database migration: Add file metadata columns to documents table"""

import sqlite3
import sys
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


def migrate_database(db_path: Path):
    """Add file metadata columns to documents table if they don't exist"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get current columns
    cursor.execute("PRAGMA table_info(documents)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    print(f"Existing columns: {existing_columns}")

    # Add missing columns
    columns_to_add = {
        "file_modified_at": "DATETIME",
        "file_created_at": "DATETIME",
        "file_size_bytes": "INTEGER",
        "file_owner": "VARCHAR"
    }

    for col_name, col_type in columns_to_add.items():
        if col_name not in existing_columns:
            print(f"Adding column: {col_name} ({col_type})")
            try:
                cursor.execute(f"ALTER TABLE documents ADD COLUMN {col_name} {col_type}")
                conn.commit()
                print(f"✓ Added {col_name}")
            except sqlite3.Error as e:
                print(f"✗ Error adding {col_name}: {e}")
        else:
            print(f"⊙ Column {col_name} already exists")

    # Create indexes for datetime columns
    indexes = [
        ("idx_file_modified_at", "file_modified_at"),
        ("idx_file_created_at", "file_created_at"),
    ]

    for idx_name, col_name in indexes:
        if col_name in columns_to_add and col_name not in existing_columns:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON documents({col_name})")
                conn.commit()
                print(f"✓ Created index {idx_name}")
            except sqlite3.Error as e:
                print(f"✗ Error creating index {idx_name}: {e}")

    conn.close()
    print("\n✓ Migration complete!")


if __name__ == "__main__":
    # Migrate main database
    db_path = Path.home() / ".mydata" / "mydata.db"

    if not db_path.exists():
        print(f"Database not found at: {db_path}")
        exit(1)

    print(f"Migrating database: {db_path}\n")
    migrate_database(db_path)
