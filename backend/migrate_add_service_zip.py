"""
Database migration to add service_type and zip_code columns to plans table.

Run this script to update existing database schema.
"""
import sqlite3
import sys
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "plans.db"

def migrate():
    """Add service_type and zip_code columns to plans table."""

    if not DB_PATH.exists():
        print(f"[ERROR] Database not found at {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(plans)")
        columns = [col[1] for col in cursor.fetchall()]

        # Add service_type if it doesn't exist
        if 'service_type' not in columns:
            print("[OK] Adding service_type column...")
            cursor.execute("""
                ALTER TABLE plans
                ADD COLUMN service_type TEXT DEFAULT 'Residential'
            """)
            print("[OK] service_type column added")
        else:
            print("[SKIP] service_type column already exists")

        # Add zip_code if it doesn't exist
        if 'zip_code' not in columns:
            print("[OK] Adding zip_code column...")
            cursor.execute("""
                ALTER TABLE plans
                ADD COLUMN zip_code TEXT
            """)
            print("[OK] zip_code column added")
        else:
            print("[SKIP] zip_code column already exists")

        conn.commit()
        print("\n[SUCCESS] Migration completed successfully!")

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Migration failed: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
