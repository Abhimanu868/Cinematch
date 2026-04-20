"""Run this once to add tmdb columns to existing database."""
import sqlite3, os

db_path = os.getenv("DATABASE_URL", "cinematch.db").replace("sqlite:///", "").replace("./data/", "")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

columns_to_add = [
    ("poster_url",   "TEXT"),
    ("backdrop_url", "TEXT"),
    ("tmdb_id",      "INTEGER"),
]

existing = [row[1] for row in cursor.execute("PRAGMA table_info(movies)")]

for col_name, col_type in columns_to_add:
    if col_name not in existing:
        cursor.execute(f"ALTER TABLE movies ADD COLUMN {col_name} {col_type}")
        print(f"Added column: {col_name}")
    else:
        print(f"Column already exists: {col_name}")

conn.commit()
conn.close()
print("Migration complete.")
