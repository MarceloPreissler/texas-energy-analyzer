"""
Populate database with real commercial plans from EnergyBot.
"""
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.database import SessionLocal
from app import crud, schemas
from app.scraping.energybot_scraper_v2 import scrape_energybot_commercial_v2

print("="*60)
print("POPULATING DATABASE WITH COMMERCIAL PLANS")
print("="*60)

# Scrape commercial plans
print("\n[1/3] Scraping EnergyBot for commercial plans...")
plans = scrape_energybot_commercial_v2()

if not plans:
    print("ERROR: No plans scraped!")
    exit(1)

print(f"SUCCESS: Scraped {len(plans)} commercial plans")

# Connect to database
db = SessionLocal()

print("\n[2/3] Adding plans to database...")
added = 0
updated = 0

for plan in plans:
    # Get or create provider
    provider_name = plan.pop('provider_name')
    provider = crud.get_provider_by_name(db, provider_name)

    if not provider:
        print(f"  + Creating new provider: {provider_name}")
        provider = crud.create_provider(db, schemas.ProviderCreate(name=provider_name))

    # Create/update plan
    plan_create = schemas.PlanCreate(provider_id=provider.id, **plan)

    # Check if plan already exists
    existing = db.query(crud.models.Plan).filter(
        crud.models.Plan.provider_id == provider.id,
        crud.models.Plan.plan_name == plan_create.plan_name
    ).first()

    if existing:
        updated += 1
        print(f"  ~ Updating: {plan_create.plan_name}")
    else:
        added += 1
        print(f"  + Adding: {plan_create.plan_name}")

    crud.create_or_update_plan(db, provider.id, plan_create)

db.close()

print(f"\n[3/3] Complete!")
print(f"  Added: {added} new plans")
print(f"  Updated: {updated} existing plans")
print(f"  Total: {added + updated} commercial plans")

print("\n" + "="*60)
print("DATABASE UPDATED SUCCESSFULLY!")
print("="*60)
print("\nRefresh your browser to see commercial plans!")
