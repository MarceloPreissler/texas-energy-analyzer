"""
Database migration: Add plan_url column to plans table.

This migration adds a plan_url column to store direct links to plans
on provider websites, making it easy for users to click through and sign up.
"""
import os
from sqlalchemy import create_engine, text

# Use environment variable or default to local SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./plans.db")

def add_plan_url_column():
    """Add plan_url column to plans table"""
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        try:
            # Check if column exists
            result = conn.execute(text("SELECT sql FROM sqlite_master WHERE type='table' AND name='plans'"))
            table_sql = result.fetchone()

            if table_sql and 'plan_url' not in str(table_sql[0]):
                # Add the column
                conn.execute(text("ALTER TABLE plans ADD COLUMN plan_url VARCHAR"))
                conn.commit()
                print("✓ Added plan_url column to plans table")
            else:
                print("✓ plan_url column already exists")

        except Exception as e:
            print(f"Error: {e}")
            print("Note: This migration is for SQLite. For PostgreSQL on Railway, the column will be added automatically.")

if __name__ == "__main__":
    add_plan_url_column()
