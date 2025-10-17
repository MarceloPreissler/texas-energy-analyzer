"""
Database migration: Add tdus table.

This migration adds the tdus table to store information about Texas
Transmission and Distribution Utilities.
"""
import os
from sqlalchemy import create_engine, text

# Use environment variable or default to local SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./plans.db")

def add_tdu_table():
    """Add tdus table to the database"""
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        try:
            # Check if table exists
            result = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='tdus'"
            ))
            table_exists = result.fetchone()

            if not table_exists:
                print("Creating tdus table...")

                # Create the tdus table
                conn.execute(text("""
                    CREATE TABLE tdus (
                        id INTEGER PRIMARY KEY,
                        name VARCHAR NOT NULL UNIQUE,
                        full_name VARCHAR,
                        website VARCHAR,
                        service_area TEXT,
                        major_cities TEXT,
                        customers INTEGER,
                        monthly_charge FLOAT,
                        delivery_charge_per_kwh FLOAT,
                        last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        rate_effective_date VARCHAR
                    )
                """))
                conn.commit()
                print("[OK] Created tdus table successfully")
            else:
                print("[OK] tdus table already exists")

        except Exception as e:
            print(f"Error: {e}")
            print("Note: This migration is for SQLite. For PostgreSQL on Railway, the table will be added automatically.")

if __name__ == "__main__":
    add_tdu_table()
