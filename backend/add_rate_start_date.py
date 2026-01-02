"""
Migration script to add rate_start_date column to plans table.
"""
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("DATABASE_URL not set")
    exit(1)

# Handle Railway's postgres:// vs postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Check if column exists
    result = conn.execute(text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'plans' AND column_name = 'rate_start_date'
    """))

    if result.fetchone():
        print("Column 'rate_start_date' already exists")
    else:
        print("Adding 'rate_start_date' column to plans table...")
        conn.execute(text("ALTER TABLE plans ADD COLUMN rate_start_date TIMESTAMP"))
        conn.commit()
        print("Column added successfully!")
