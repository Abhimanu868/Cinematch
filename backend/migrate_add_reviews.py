"""Run once to add review columns to the ratings table."""
import sqlite3
import os

db_path = os.getenv("DATABASE_URL", "sqlite:///./cinematch.db").replace("sqlite:///./", "")
if not os.path.exists(db_path):
    db_path = "cinematch.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

existing_cols = [row[1] for row in cursor.execute("PRAGMA table_info(ratings)")]
print(f"Existing columns: {existing_cols}")

columns_to_add = [
    ("review_text",  "TEXT"),
    ("review_title", "VARCHAR(150)"),
    ("edited_at",    "DATETIME"),
]

for col_name, col_type in columns_to_add:
    if col_name not in existing_cols:
        cursor.execute(f"ALTER TABLE ratings ADD COLUMN {col_name} {col_type}")
        print(f"  ✓ Added: {col_name}")
    else:
        print(f"  → Already exists: {col_name}")

conn.commit()
conn.close()
print("Migration complete.")
