"""
Quick script to populate database with live PowerToChoose.org data.
Run this to get plans with zip codes and fresh data!
"""
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.scraping import powertochoose_scraper
from app import crud, schemas

def populate_residential():
    print("=" * 60)
    print("POPULATING DATABASE WITH RESIDENTIAL PLANS")
    print("=" * 60)

    db: Session = SessionLocal()
    try:
        # Scrape residential plans from PowerToChoose
        print("\n[1/3] Scraping residential plans from PowerToChoose.org...")
        plans = powertochoose_scraper.scrape_powertochoose_all_texas(service_type="Residential")
        print(f"✓ Found {len(plans)} residential plans")

        # Insert into database
        print("\n[2/3] Inserting plans into database...")
        created_or_updated = 0
        for plan in plans:
            provider_name = plan.pop("provider_name")
            provider = crud.get_provider_by_name(db, provider_name)
            if not provider:
                provider = crud.create_provider(
                    db, schemas.ProviderCreate(name=provider_name)
                )
            plan_create = schemas.PlanCreate(provider_id=provider.id, **plan)
            crud.create_or_update_plan(db, provider.id, plan_create)
            created_or_updated += 1
            if created_or_updated % 10 == 0:
                print(f"  Processed {created_or_updated}/{len(plans)} plans...")

        print(f"✓ Successfully processed {created_or_updated} plans")

        # Verify
        print("\n[3/3] Verifying database...")
        cursor = db.connection().connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM plans WHERE service_type='Residential'")
        total_residential = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM plans WHERE zip_code IS NOT NULL")
        total_with_zip = cursor.fetchone()[0]

        print(f"✓ Total residential plans: {total_residential}")
        print(f"✓ Plans with zip codes: {total_with_zip}")

        print("\n" + "=" * 60)
        print("SUCCESS! Database populated with fresh residential data.")
        print("Now refresh your browser to see the plans!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)
    finally:
        db.close()

def populate_commercial():
    print("=" * 60)
    print("POPULATING DATABASE WITH COMMERCIAL PLANS")
    print("=" * 60)

    db: Session = SessionLocal()
    try:
        # Scrape commercial plans from PowerToChoose
        print("\n[1/3] Scraping commercial plans from PowerToChoose.org...")
        plans = powertochoose_scraper.scrape_powertochoose_all_texas(service_type="Commercial")
        print(f"✓ Found {len(plans)} commercial plans")

        # Insert into database
        print("\n[2/3] Inserting plans into database...")
        created_or_updated = 0
        for plan in plans:
            provider_name = plan.pop("provider_name")
            provider = crud.get_provider_by_name(db, provider_name)
            if not provider:
                provider = crud.create_provider(
                    db, schemas.ProviderCreate(name=provider_name)
                )
            plan_create = schemas.PlanCreate(provider_id=provider.id, **plan)
            crud.create_or_update_plan(db, provider.id, plan_create)
            created_or_updated += 1
            if created_or_updated % 10 == 0:
                print(f"  Processed {created_or_updated}/{len(plans)} plans...")

        print(f"✓ Successfully processed {created_or_updated} plans")

        print("\n" + "=" * 60)
        print("SUCCESS! Database populated with commercial data.")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "commercial":
        populate_commercial()
    else:
        populate_residential()
        print("\nTip: To also add commercial plans, run: python quick_populate.py commercial")
