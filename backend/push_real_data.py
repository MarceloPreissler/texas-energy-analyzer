"""
Push real scraped data to Railway production database
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Provider, Plan
from app.scraping.scraper import scrape_all

# Railway production database URL
RAILWAY_DB_URL = "postgresql://postgres:rmbKXqbhbEpnOTUbBWZyQWXglPKawaxp@junction.proxy.rlwy.net:45652/railway"

def push_real_data():
    """Scrape real data and push to Railway"""
    print("Scraping REAL data from PowerChoiceTexas...")
    plans = scrape_all()

    if not plans:
        print("ERROR: No plans scraped!")
        return

    print(f"SUCCESS: Scraped {len(plans)} REAL plans")

    # Connect to Railway database
    print("Connecting to Railway database...")
    engine = create_engine(RAILWAY_DB_URL)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        added = 0
        updated = 0

        for plan_data in plans:
            # Get or create provider
            provider = db.query(Provider).filter(Provider.name == plan_data['provider_name']).first()
            if not provider:
                provider = Provider(name=plan_data['provider_name'])
                db.add(provider)
                db.flush()

            # Check if plan exists
            existing = db.query(Plan).filter(
                Plan.provider_id == provider.id,
                Plan.plan_name == plan_data['plan_name']
            ).first()

            if existing:
                # Update existing plan
                existing.plan_type = plan_data.get('plan_type', 'Fixed')
                existing.service_type = plan_data.get('service_type', 'Residential')
                existing.rate_1000_cents = plan_data.get('rate_1000_cents')
                existing.special_features = plan_data.get('special_features', '')
                updated += 1
            else:
                # Create new plan
                new_plan = Plan(
                    provider_id=provider.id,
                    plan_name=plan_data['plan_name'],
                    plan_type=plan_data.get('plan_type', 'Fixed'),
                    service_type=plan_data.get('service_type', 'Residential'),
                    zip_code=plan_data.get('zip_code', '75001'),
                    contract_months=plan_data.get('contract_months', 12),
                    rate_1000_cents=plan_data.get('rate_1000_cents'),
                    special_features=plan_data.get('special_features', '')
                )
                db.add(new_plan)
                added += 1

        db.commit()
        print(f"SUCCESS! Pushed to Railway:")
        print(f"   - Added: {added} new plans")
        print(f"   - Updated: {updated} existing plans")
        print(f"   - Total: {added + updated} REAL plans in database")

    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    push_real_data()
