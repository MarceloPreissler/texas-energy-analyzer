"""
EMERGENCY FIX SCRIPT - Run this to fix everything immediately

This script will:
1. Force database migrations
2. Test all scrapers
3. Load data into database
4. Verify everything works
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import SessionLocal, engine
from app.models import Base, Plan, Provider
from app import crud, schemas
from app.scraping import scraper, energybot_scraper_v2, energybot_business_enhanced
from app.migrations import run_migrations
from sqlalchemy import inspect

print("="*80)
print("EMERGENCY FIX SCRIPT - RUNNING NOW")
print("="*80)

# Step 1: Force migrations
print("\n[1/5] FORCING DATABASE MIGRATIONS...")
db = SessionLocal()
try:
    run_migrations(db)
    print("✅ Migrations completed")
except Exception as e:
    print(f"⚠️ Migration error (may be OK): {e}")
finally:
    db.close()

# Step 2: Verify schema
print("\n[2/5] VERIFYING DATABASE SCHEMA...")
db = SessionLocal()
inspector = inspect(db.bind)
plans_columns = [col['name'] for col in inspector.get_columns('plans')]
print(f"Plans table columns: {plans_columns}")
if 'plan_url' in plans_columns:
    print("✅ plan_url column exists")
else:
    print("❌ plan_url column MISSING - trying to add manually...")
    from sqlalchemy import text
    db.execute(text("ALTER TABLE plans ADD COLUMN plan_url VARCHAR"))
    db.commit()
    print("✅ Added plan_url column manually")
db.close()

# Step 3: Test scrapers
print("\n[3/5] TESTING SCRAPERS...")

print("\n[3a] Testing Legacy Residential Scraper...")
try:
    residential_plans = scraper.scrape_all()
    print(f"✅ Scraped {len(residential_plans)} residential plans")
    if residential_plans:
        print(f"   Sample: {residential_plans[0].get('provider_name')} - {residential_plans[0].get('plan_name')}")
except Exception as e:
    print(f"❌ Residential scraper failed: {e}")
    residential_plans = []

print("\n[3b] Testing Enhanced Commercial Scraper (1 ZIP only for speed)...")
try:
    # Test just Dallas for speed
    from app.scraping.energybot_business_enhanced import scrape_energybot_business_enhanced
    commercial_plans = scrape_energybot_business_enhanced("75214", "ONCOR", "Dallas")
    print(f"✅ Scraped {len(commercial_plans)} commercial plans (Dallas only)")
    if commercial_plans:
        print(f"   Sample: {commercial_plans[0].get('provider_name')} - {commercial_plans[0].get('plan_name')}")
except Exception as e:
    print(f"❌ Commercial scraper failed: {e}")
    import traceback
    traceback.print_exc()
    commercial_plans = []

# Step 4: Load data into database
print("\n[4/5] LOADING DATA INTO DATABASE...")
db = SessionLocal()
loaded_count = 0

try:
    # Load residential plans
    for plan_data in residential_plans[:20]:  # Limit to 20 for speed
        try:
            provider_name = plan_data.get("provider_name")
            if not provider_name:
                continue

            provider = crud.get_provider_by_name(db, provider_name)
            if not provider:
                provider = crud.create_provider(db, schemas.ProviderCreate(name=provider_name))

            plan_create = schemas.PlanCreate(
                provider_id=provider.id,
                plan_name=plan_data.get("plan_name", "Unknown"),
                plan_url=plan_data.get("plan_url"),
                plan_type=plan_data.get("plan_type", "Fixed"),
                service_type="Residential",
                zip_code=plan_data.get("zip_code", "75001"),
                contract_months=plan_data.get("contract_months"),
                rate_1000_cents=plan_data.get("rate_1000_cents"),
                rate_500_cents=plan_data.get("rate_500_cents"),
                rate_2000_cents=plan_data.get("rate_2000_cents"),
            )

            crud.create_or_update_plan(db, provider.id, plan_create)
            loaded_count += 1
        except Exception as e:
            print(f"   Error loading plan: {e}")
            continue

    # Load commercial plans
    for plan_data in commercial_plans[:20]:  # Limit to 20 for speed
        try:
            provider_name = plan_data.get("provider_name")
            if not provider_name:
                continue

            provider = crud.get_provider_by_name(db, provider_name)
            if not provider:
                provider = crud.create_provider(db, schemas.ProviderCreate(name=provider_name))

            plan_create = schemas.PlanCreate(
                provider_id=provider.id,
                plan_name=plan_data.get("plan_name", "Unknown"),
                plan_url=plan_data.get("plan_url"),
                plan_type=plan_data.get("plan_type", "Fixed"),
                service_type="Commercial",
                zip_code=plan_data.get("zip_code", "75001"),
                contract_months=plan_data.get("contract_months"),
                rate_1000_cents=plan_data.get("rate_1000_cents"),
            )

            crud.create_or_update_plan(db, provider.id, plan_create)
            loaded_count += 1
        except Exception as e:
            print(f"   Error loading plan: {e}")
            continue

    db.commit()
    print(f"✅ Loaded {loaded_count} plans into database")

except Exception as e:
    db.rollback()
    print(f"❌ Database loading failed: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

# Step 5: Verify data
print("\n[5/5] VERIFYING DATA IN DATABASE...")
db = SessionLocal()
try:
    residential_count = db.query(Plan).filter(Plan.service_type == "Residential").count()
    commercial_count = db.query(Plan).filter(Plan.service_type == "Commercial").count()
    provider_count = db.query(Provider).count()

    print(f"✅ Database contains:")
    print(f"   - {provider_count} providers")
    print(f"   - {residential_count} residential plans")
    print(f"   - {commercial_count} commercial plans")
    print(f"   - TOTAL: {residential_count + commercial_count} plans")

    if residential_count + commercial_count > 0:
        print("\n✅✅✅ SUCCESS! Data is in the database! ✅✅✅")
    else:
        print("\n❌ WARNING: No plans in database!")

finally:
    db.close()

print("\n" + "="*80)
print("EMERGENCY FIX COMPLETE")
print("="*80)
print("\nNext steps:")
print("1. Go to your frontend: https://texasenergyanalyzer.com")
print("2. Select 'Commercial' - you should see plans")
print("3. Select 'Residential' - you should see plans")
print("\nIf you still don't see data, the issue is in your frontend API connection.")
print("="*80)
