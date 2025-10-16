"""
Load initial data into Railway database.
This script populates the database with commercial and residential plans
without needing to run scrapers (which require Playwright).
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app import crud, schemas

# Sample commercial plans data (similar to fallback data)
COMMERCIAL_PLANS = [
    {
        "provider_name": "TXU Energy",
        "provider_website": "https://www.txu.com",
        "plan_name": "Business Choice 24",
        "plan_type": "Fixed",
        "service_type": "Commercial",
        "zip_code": "75001",
        "contract_months": 24,
        "rate_1000_cents": 11.5,
        "rate_2000_cents": 11.2,
        "monthly_bill_1000": 115.0,
        "monthly_bill_2000": 224.0,
        "early_termination_fee": 195.0,
        "base_monthly_fee": 0.0,
        "renewable_percent": 0.0,
        "special_features": "24-month fixed rate"
    },
    {
        "provider_name": "TXU Energy",
        "provider_website": "https://www.txu.com",
        "plan_name": "Business Advantage 24",
        "plan_type": "Fixed",
        "service_type": "Commercial",
        "zip_code": "75001",
        "contract_months": 24,
        "rate_1000_cents": 12.0,
        "rate_2000_cents": 11.7,
        "monthly_bill_1000": 120.0,
        "monthly_bill_2000": 234.0,
        "early_termination_fee": 195.0,
        "base_monthly_fee": 0.0,
        "renewable_percent": 10.0,
        "special_features": "10% renewable energy"
    },
    {
        "provider_name": "TXU Energy",
        "provider_website": "https://www.txu.com",
        "plan_name": "Business Select 24",
        "plan_type": "Fixed",
        "service_type": "Commercial",
        "zip_code": "75001",
        "contract_months": 24,
        "rate_1000_cents": 11.8,
        "rate_2000_cents": 11.5,
        "monthly_bill_1000": 118.0,
        "monthly_bill_2000": 230.0,
        "early_termination_fee": 195.0,
        "base_monthly_fee": 0.0,
        "renewable_percent": 0.0,
        "special_features": "Competitive fixed rate"
    },
    {
        "provider_name": "Direct Energy",
        "provider_website": "https://www.directenergy.com",
        "plan_name": "Business Power Plus 24",
        "plan_type": "Fixed",
        "service_type": "Commercial",
        "zip_code": "75001",
        "contract_months": 24,
        "rate_1000_cents": 12.3,
        "rate_2000_cents": 11.9,
        "monthly_bill_1000": 123.0,
        "monthly_bill_2000": 238.0,
        "early_termination_fee": 200.0,
        "base_monthly_fee": 0.0,
        "renewable_percent": 0.0,
        "special_features": "24-month fixed rate"
    },
    {
        "provider_name": "Direct Energy",
        "provider_website": "https://www.directenergy.com",
        "plan_name": "Business Green 12",
        "plan_type": "Fixed",
        "service_type": "Commercial",
        "zip_code": "75001",
        "contract_months": 12,
        "rate_1000_cents": 13.5,
        "rate_2000_cents": 13.0,
        "monthly_bill_1000": 135.0,
        "monthly_bill_2000": 260.0,
        "early_termination_fee": 150.0,
        "base_monthly_fee": 0.0,
        "renewable_percent": 100.0,
        "special_features": "100% renewable energy"
    },
    {
        "provider_name": "Gexa Energy",
        "provider_website": "https://www.gexaenergy.com",
        "plan_name": "Gexa Business 24",
        "plan_type": "Fixed",
        "service_type": "Commercial",
        "zip_code": "75001",
        "contract_months": 24,
        "rate_1000_cents": 11.9,
        "rate_2000_cents": 11.6,
        "monthly_bill_1000": 119.0,
        "monthly_bill_2000": 232.0,
        "early_termination_fee": 195.0,
        "base_monthly_fee": 0.0,
        "renewable_percent": 0.0,
        "special_features": "Reliable fixed rate"
    },
    {
        "provider_name": "Reliant Energy",
        "provider_website": "https://www.reliant.com",
        "plan_name": "Reliant Business 24",
        "plan_type": "Fixed",
        "service_type": "Commercial",
        "zip_code": "75001",
        "contract_months": 24,
        "rate_1000_cents": 12.1,
        "rate_2000_cents": 11.8,
        "monthly_bill_1000": 121.0,
        "monthly_bill_2000": 236.0,
        "early_termination_fee": 200.0,
        "base_monthly_fee": 0.0,
        "renewable_percent": 0.0,
        "special_features": "Trusted provider"
    },
    {
        "provider_name": "Constellation",
        "provider_website": "https://www.constellation.com",
        "plan_name": "Constellation Business 36",
        "plan_type": "Fixed",
        "service_type": "Commercial",
        "zip_code": "75001",
        "contract_months": 36,
        "rate_1000_cents": 11.2,
        "rate_2000_cents": 10.9,
        "monthly_bill_1000": 112.0,
        "monthly_bill_2000": 218.0,
        "early_termination_fee": 250.0,
        "base_monthly_fee": 0.0,
        "renewable_percent": 0.0,
        "special_features": "Long-term savings"
    }
]

# Sample residential plans
RESIDENTIAL_PLANS = [
    {
        "provider_name": "TXU Energy",
        "provider_website": "https://www.txu.com",
        "plan_name": "TXU Energy Secure 12",
        "plan_type": "Fixed",
        "service_type": "Residential",
        "zip_code": "75001",
        "contract_months": 12,
        "rate_1000_cents": 13.5,
        "rate_2000_cents": 12.9,
        "monthly_bill_1000": 135.0,
        "monthly_bill_2000": 258.0,
        "early_termination_fee": 150.0,
        "base_monthly_fee": 0.0,
        "renewable_percent": 0.0,
        "special_features": "12-month fixed rate"
    },
    {
        "provider_name": "Direct Energy",
        "provider_website": "https://www.directenergy.com",
        "plan_name": "Direct Homeguard 12",
        "plan_type": "Fixed",
        "service_type": "Residential",
        "zip_code": "75001",
        "contract_months": 12,
        "rate_1000_cents": 13.8,
        "rate_2000_cents": 13.2,
        "monthly_bill_1000": 138.0,
        "monthly_bill_2000": 264.0,
        "early_termination_fee": 150.0,
        "base_monthly_fee": 0.0,
        "renewable_percent": 0.0,
        "special_features": "Reliable fixed rate"
    },
    {
        "provider_name": "Gexa Energy",
        "provider_website": "https://www.gexaenergy.com",
        "plan_name": "Gexa Saver Supreme 12",
        "plan_type": "Fixed",
        "service_type": "Residential",
        "zip_code": "75001",
        "contract_months": 12,
        "rate_1000_cents": 13.2,
        "rate_2000_cents": 12.7,
        "monthly_bill_1000": 132.0,
        "monthly_bill_2000": 254.0,
        "early_termination_fee": 150.0,
        "base_monthly_fee": 0.0,
        "renewable_percent": 10.0,
        "special_features": "10% renewable energy"
    },
    {
        "provider_name": "Reliant Energy",
        "provider_website": "https://www.reliant.com",
        "plan_name": "Reliant Basic Power 12",
        "plan_type": "Fixed",
        "service_type": "Residential",
        "zip_code": "75001",
        "contract_months": 12,
        "rate_1000_cents": 14.1,
        "rate_2000_cents": 13.5,
        "monthly_bill_1000": 141.0,
        "monthly_bill_2000": 270.0,
        "early_termination_fee": 150.0,
        "base_monthly_fee": 0.0,
        "renewable_percent": 0.0,
        "special_features": "Simple fixed rate"
    },
    {
        "provider_name": "Constellation",
        "provider_website": "https://www.constellation.com",
        "plan_name": "Constellation Standard 12",
        "plan_type": "Fixed",
        "service_type": "Residential",
        "zip_code": "75001",
        "contract_months": 12,
        "rate_1000_cents": 13.0,
        "rate_2000_cents": 12.5,
        "monthly_bill_1000": 130.0,
        "monthly_bill_2000": 250.0,
        "early_termination_fee": 150.0,
        "base_monthly_fee": 0.0,
        "renewable_percent": 0.0,
        "special_features": "Competitive rate"
    }
]

def load_data():
    """Load initial data into database."""
    db = SessionLocal()
    try:
        print("Loading initial data into database...")

        all_plans = COMMERCIAL_PLANS + RESIDENTIAL_PLANS
        added = 0
        updated = 0

        for plan_data in all_plans:
            # Get or create provider
            provider = crud.get_provider_by_name(db, plan_data["provider_name"])
            if not provider:
                provider_create = schemas.ProviderCreate(
                    name=plan_data["provider_name"],
                    website=plan_data.get("provider_website")
                )
                provider = crud.create_provider(db, provider_create)
                print(f"Created provider: {provider.name}")

            # Create plan schema
            plan_create = schemas.PlanCreate(
                provider_id=provider.id,
                plan_name=plan_data["plan_name"],
                plan_type=plan_data.get("plan_type", "Fixed"),
                service_type=plan_data["service_type"],
                zip_code=plan_data.get("zip_code", "75001"),
                contract_months=plan_data.get("contract_months", 12),
                rate_500_cents=plan_data.get("rate_500_cents"),
                rate_1000_cents=plan_data.get("rate_1000_cents"),
                rate_2000_cents=plan_data.get("rate_2000_cents"),
                monthly_bill_1000=plan_data.get("monthly_bill_1000"),
                monthly_bill_2000=plan_data.get("monthly_bill_2000"),
                early_termination_fee=plan_data.get("early_termination_fee", 0.0),
                base_monthly_fee=plan_data.get("base_monthly_fee", 0.0),
                renewable_percent=plan_data.get("renewable_percent", 0.0),
                special_features=plan_data.get("special_features", "")
            )

            # Check if exists
            from app.models import Plan
            existing = db.query(Plan).filter(
                Plan.provider_id == provider.id,
                Plan.plan_name == plan_create.plan_name
            ).first()

            if existing:
                updated += 1
            else:
                added += 1

            crud.create_or_update_plan(db, provider.id, plan_create)

        print(f"\n✅ SUCCESS!")
        print(f"Added {added} new plans")
        print(f"Updated {updated} existing plans")
        print(f"Total: {added + updated} plans loaded")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    load_data()
