"""
Delete fake/sample commercial plans from the database.

This script removes all commercial plans that contain "verify with" or "Typical rate"
in their special_features field, which indicates they're sample data, not real plans.

Only keeps REAL commercial plans scraped from live sources (EnergyBot).
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.models import Plan

def delete_fake_commercial_plans():
    """Delete all fake/sample commercial plans."""
    db = SessionLocal()

    try:
        # Find all commercial plans with "verify" or "Typical rate" (= fake)
        fake_plans = db.query(Plan).filter(
            Plan.service_type == "Commercial",
            Plan.special_features.like("%verify%")
        ).all()

        print(f"Found {len(fake_plans)} FAKE commercial plans to delete:")
        for plan in fake_plans[:10]:  # Show first 10
            print(f"  - {plan.provider.name}: {plan.plan_name} ({plan.special_features[:50]}...)")

        if len(fake_plans) > 10:
            print(f"  ... and {len(fake_plans) - 10} more")

        if fake_plans:
            confirm = input(f"\nDelete {len(fake_plans)} fake commercial plans? (yes/no): ")
            if confirm.lower() == 'yes':
                for plan in fake_plans:
                    db.delete(plan)
                db.commit()
                print(f"\n[OK] Deleted {len(fake_plans)} fake commercial plans")
            else:
                print("Cancelled")
        else:
            print("\n[OK] No fake commercial plans found")

        # Show remaining commercial plans
        real_plans = db.query(Plan).filter(Plan.service_type == "Commercial").all()
        print(f"\nRemaining REAL commercial plans: {len(real_plans)}")
        for plan in real_plans:
            print(f"  - {plan.provider.name}: {plan.plan_name}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Fake Commercial Plans Deleter")
    print("=" * 60)
    print()
    delete_fake_commercial_plans()
