"""
Load EnergyBot commercial plans to local database.
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base
from app.scraping.energybot_scraper_v2 import scrape_energybot_commercial_v2
from app.crud import get_provider_by_name, create_provider, create_or_update_plan
from app.schemas import ProviderCreate, PlanCreate

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

print("=" * 80)
print("LOADING ENERGYBOT COMMERCIAL PLANS TO DATABASE")
print("=" * 80)

# Scrape plans from EnergyBot
print("\n[1/3] Scraping plans from EnergyBot...")
plans = scrape_energybot_commercial_v2(zip_code="75001", max_plans=50)
print(f"Scraped {len(plans)} commercial plans")

# Load to database
print(f"\n[2/3] Loading {len(plans)} plans to local database...")
db = SessionLocal()
try:
    added = 0
    updated = 0

    for plan_dict in plans:
        # Get or create provider
        provider = get_provider_by_name(db, name=plan_dict['provider_name'])
        if not provider:
            provider_create = ProviderCreate(
                name=plan_dict['provider_name'],
                website=None  # EnergyBot doesn't provide provider websites
            )
            provider = create_provider(db, provider_create)
            print(f"  Created provider: {provider.name}")

        # Create PlanCreate schema object
        plan_create = PlanCreate(
            provider_id=provider.id,
            plan_name=plan_dict['plan_name'],
            plan_type=plan_dict['plan_type'],
            service_type=plan_dict['service_type'],
            zip_code=plan_dict.get('zip_code'),
            contract_months=plan_dict.get('contract_months'),
            rate_500_cents=plan_dict.get('rate_500_cents'),
            rate_1000_cents=plan_dict.get('rate_1000_cents'),
            rate_2000_cents=plan_dict.get('rate_2000_cents'),
            monthly_bill_1000=plan_dict.get('monthly_bill_1000'),
            monthly_bill_2000=plan_dict.get('monthly_bill_2000'),
            early_termination_fee=plan_dict.get('early_termination_fee'),
            base_monthly_fee=plan_dict.get('base_monthly_fee'),
            renewable_percent=plan_dict.get('renewable_percent'),
            special_features=plan_dict.get('special_features'),
        )

        # Create or update plan
        plan = create_or_update_plan(
            db,
            provider_id=provider.id,
            plan_data=plan_create
        )

        if plan:
            added += 1
            print(f"  OK: {plan_dict['provider_name']} - {plan_dict['plan_name']}")

    print(f"\n[3/3] Database updated successfully!")
    print(f"  Total plans processed: {added}")

except Exception as e:
    db.rollback()
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

# Verify what's in the database
print("\n" + "=" * 80)
print("VERIFICATION - Current Database Contents")
print("=" * 80)

db = SessionLocal()
try:
    from app.crud import get_plans

    # Get all plans
    all_plans = get_plans(db)
    residential_plans = get_plans(db, service_type="Residential")
    commercial_plans = get_plans(db, service_type="Commercial")

    print(f"Total plans: {len(all_plans)}")
    print(f"  Residential: {len(residential_plans)}")
    print(f"  Commercial: {len(commercial_plans)}")

    if commercial_plans:
        print(f"\nCommercial Plans ({len(commercial_plans)}):")
        for i, plan in enumerate(commercial_plans, 1):
            print(f"  {i}. {plan.provider.name} - {plan.plan_name}")
            print(f"     Rate: {plan.rate_1000_cents}cents/kWh, Term: {plan.contract_months} months")

finally:
    db.close()

print("\n" + "=" * 80)
print("SUCCESS - Ready to deploy to Railway!")
print("=" * 80)
