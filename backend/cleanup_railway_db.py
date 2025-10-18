"""
Cleanup script to delete fake commercial plans from Railway database.

This script connects to the Railway PostgreSQL database and removes
all fake commercial plans (those with "verify" or "Typical" in special_features).

Run this script once to clean up the production database.
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

# Get Railway database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set!")
    print("Please set DATABASE_URL to your Railway PostgreSQL connection string")
    exit(1)

# Create engine
engine = create_engine(DATABASE_URL)

print("=" * 60)
print("Railway Database Cleanup - Remove Fake Commercial Plans")
print("=" * 60)
print()

with Session(engine) as db:
    # Count fake commercial plans
    count_query = text("""
        SELECT COUNT(*) FROM plans
        WHERE service_type = 'Commercial'
        AND (special_features LIKE '%verify%' OR special_features LIKE '%Typical%')
    """)

    fake_count = db.execute(count_query).scalar()
    print(f"Found {fake_count} fake commercial plans to delete")

    if fake_count > 0:
        # Delete fake commercial plans
        delete_query = text("""
            DELETE FROM plans
            WHERE service_type = 'Commercial'
            AND (special_features LIKE '%verify%' OR special_features LIKE '%Typical%')
        """)

        result = db.execute(delete_query)
        db.commit()

        print(f"[OK] Deleted {result.rowcount} fake commercial plans")
    else:
        print("[OK] No fake commercial plans found")

    # Count remaining commercial plans
    remaining_query = text("SELECT COUNT(*) FROM plans WHERE service_type = 'Commercial'")
    remaining = db.execute(remaining_query).scalar()

    print(f"[OK] {remaining} commercial plans remaining (should be 0-5 real EnergyBot plans)")
    print()
    print("SUCCESS: Database cleanup complete!")
