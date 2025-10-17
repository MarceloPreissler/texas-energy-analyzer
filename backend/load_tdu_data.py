"""
Load TDU data into the database.

This script populates the database with information about all Texas
Transmission and Distribution Utilities (TDUs).

Run this script after creating the database tables:
    python load_tdu_data.py
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import from app
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app import schemas, crud
from app.tdu_data import get_all_tdus

def load_tdus():
    """Load all TDU data into the database."""
    db = SessionLocal()

    try:
        tdus = get_all_tdus()
        print(f"Loading {len(tdus)} TDUs into database...")

        for tdu_data in tdus:
            tdu_create = schemas.TDUCreate(**tdu_data)
            tdu = crud.create_or_update_tdu(db, tdu_create)
            print(f"  [OK] {tdu.full_name} ({tdu.name})")
            print(f"    - Customers: {tdu.customers:,}")
            print(f"    - Monthly Charge: ${tdu.monthly_charge}")
            print(f"    - Delivery: {tdu.delivery_charge_per_kwh} cents/kWh")
            print(f"    - Major Cities: {tdu.major_cities[:80]}...")
            print()

        print(f"SUCCESS: Loaded {len(tdus)} TDUs!")

    except Exception as e:
        print(f"ERROR: Error loading TDUs: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Texas TDU Data Loader")
    print("=" * 60)
    print()
    load_tdus()
