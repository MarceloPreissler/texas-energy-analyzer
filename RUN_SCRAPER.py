"""
RUN SCRAPER - Scrapes real data and loads it into the database
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import SessionLocal
from app.models import Plan, Provider
from app import crud, schemas

print("="*80)
print("SCRAPING REAL DATA NOW")
print("="*80)

# Step 1: Scrape Enhanced Commercial Data (Dallas only for speed)
print("\n[1/3] SCRAPING COMMERCIAL PLANS (Dallas/ONCOR)...")
try:
    from app.scraping.energybot_business_enhanced import scrape_energybot_business_enhanced
    print("Launching headless browser and navigating EnergyBot...")
    commercial_plans = scrape_energybot_business_enhanced("75214", "ONCOR", "Dallas")
    print(f"✅ Scraped {len(commercial_plans)} commercial plans")
    if commercial_plans:
        print(f"\n   Sample plans:")
        for i, plan in enumerate(commercial_plans[:3]):
            print(f"   {i+1}. {plan.get('provider_name')} - {plan.get('plan_name')[:50]}")
except Exception as e:
    print(f"❌ Commercial scraper failed: {e}")
    import traceback
    traceback.print_exc()
    commercial_plans = []

# Step 2: Load commercial data into database
print("\n[2/3] LOADING COMMERCIAL DATA INTO DATABASE...")
db = SessionLocal()
loaded = 0

try:
    for plan_data in commercial_plans:
        try:
            provider_name = plan_data.get("provider_name")
            if not provider_name:
                continue

            # Get or create provider
            provider = crud.get_provider_by_name(db, provider_name)
            if not provider:
                provider = crud.create_provider(db, schemas.ProviderCreate(name=provider_name))

            # Create plan
            plan_create = schemas.PlanCreate(
                provider_id=provider.id,
                plan_name=plan_data.get("plan_name", "Unknown"),
                plan_url=plan_data.get("plan_url"),
                plan_type=plan_data.get("plan_type", "Fixed"),
                service_type="Commercial",
                zip_code=plan_data.get("zip_code", "75214"),
                contract_months=plan_data.get("contract_months"),
                rate_1000_cents=plan_data.get("rate_1000_cents"),
            )

            crud.create_or_update_plan(db, provider.id, plan_create)
            loaded += 1

        except Exception as e:
            print(f"   ⚠️ Error loading plan {plan_data.get('plan_name', 'Unknown')}: {e}")
            continue

    db.commit()
    print(f"✅ Loaded {loaded} commercial plans into database")

except Exception as e:
    db.rollback()
    print(f"❌ Database loading failed: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

# Step 3: Verify data
print("\n[3/3] VERIFYING DATA IN DATABASE...")
db = SessionLocal()
try:
    commercial_count = db.query(Plan).filter(Plan.service_type == "Commercial").count()
    provider_count = db.query(Provider).count()

    print(f"\n✅ DATABASE CONTAINS:")
    print(f"   • {provider_count} providers")
    print(f"   • {commercial_count} commercial plans")

    if commercial_count > 0:
        print(f"\n✅✅✅ SUCCESS! {commercial_count} REAL COMMERCIAL PLANS LOADED! ✅✅✅")

        # Show a few examples
        print("\n📋 Example plans in database:")
        sample_plans = db.query(Plan).filter(Plan.service_type == "Commercial").limit(5).all()
        for i, plan in enumerate(sample_plans, 1):
            provider = db.query(Provider).filter(Provider.id == plan.provider_id).first()
            rate = plan.rate_1000_cents / 100 if plan.rate_1000_cents else "N/A"
            print(f"   {i}. {provider.name} - {plan.plan_name[:50]}")
            print(f"      Rate: {rate}¢/kWh | Contract: {plan.contract_months} months")
    else:
        print("\n❌ WARNING: No plans in database!")

finally:
    db.close()

print("\n" + "="*80)
print("SCRAPING COMPLETE!")
print("="*80)
print("\nNext steps:")
print("1. Start your backend server: cd backend && uvicorn app.main:app --reload")
print("2. Go to: http://localhost:8000/plans?service_type=Commercial")
print("3. You should see your scraped plans in JSON format")
print("\nOr check Railway: https://web-production-665ac.up.railway.app/plans?service_type=Commercial")
print("="*80)
