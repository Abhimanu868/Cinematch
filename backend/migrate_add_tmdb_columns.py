import os
import sys

# Add backend directory to Python path if running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, inspect, text
from app.config import settings

def run_migration():
    print(f"Connecting to database: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    
    inspector = inspect(engine)
    
    # Check if movies table exists
    if not inspector.has_table("movies"):
        print("Movies table does not exist yet. Skipping migration.")
        return

    columns = [col['name'] for col in inspector.get_columns("movies")]
    
    with engine.begin() as conn:
        # Add tmdb_id if it doesn't exist
        if "tmdb_id" not in columns:
            print("Adding tmdb_id column...")
            conn.execute(text("ALTER TABLE movies ADD COLUMN tmdb_id INTEGER"))
            print("tmdb_id added successfully.")
        else:
            print("tmdb_id column already exists.")

        # Add tagline if it doesn't exist
        if "tagline" not in columns:
            print("Adding tagline column...")
            conn.execute(text("ALTER TABLE movies ADD COLUMN tagline VARCHAR(500)"))
            print("tagline added successfully.")
        else:
            print("tagline column already exists.")
            
    print("Migration complete!")

if __name__ == "__main__":
    run_migration()
