"""
Initialize production database with tables and sample data.
Run this once after deploying to Railway.
"""
import sys
import os

# Create tables
print("Creating database tables...")
from app.database import engine, Base
from app.models import Provider, Plan

Base.metadata.create_all(bind=engine)
print("✓ Tables created successfully")

# Populate with data
print("\nPopulating database with plans...")
from app.database import SessionLocal
from app import crud, schemas

# Sample data to get started
providers_data = [
    {"name": "Gexa Energy", "website": "https://www.gexaenergy.com"},
    {"name": "TXU Energy", "website": "https://www.txu.com"},
    {"name": "Reliant Energy", "website": "https://www.reliant.com"},
    {"name": "Direct Energy", "website": "https://www.directenergy.com"},
    {"name": "NRG Energy, Inc.", "website": "https://www.nrg.com"},
]

sample_plans = [
    {
        "provider_name": "Gexa Energy",
        "plan_name": "Gexa Saver Supreme 12",
        "plan_type": "Fixed",
        "service_type": "Residential",
        "zip_code": "75001",
        "contract_months": 12,
        "rate_1000_cents": 9.9,
    },
    {
        "provider_name": "TXU Energy",
        "plan_name": "TXU Energy Secure 12",
        "plan_type": "Fixed",
        "service_type": "Residential",
        "zip_code": "75001",
        "contract_months": 12,
        "rate_1000_cents": 10.5,
    },
    {
        "provider_name": "Reliant Energy",
        "plan_name": "Reliant Secure 12 Advantage",
        "plan_type": "Fixed",
        "service_type": "Residential",
        "zip_code": "75001",
        "contract_months": 12,
        "rate_1000_cents": 11.2,
    },
]

db = SessionLocal()

try:
    # Create providers
    for prov_data in providers_data:
        existing = crud.get_provider_by_name(db, prov_data["name"])
        if not existing:
            crud.create_provider(db, schemas.ProviderCreate(**prov_data))
            print(f"✓ Created provider: {prov_data['name']}")

    # Create sample plans
    for plan_data in sample_plans:
        provider_name = plan_data.pop("provider_name")
        provider = crud.get_provider_by_name(db, provider_name)

        if provider:
            plan_create = schemas.PlanCreate(provider_id=provider.id, **plan_data)
            crud.create_or_update_plan(db, provider.id, plan_create)
            print(f"✓ Created plan: {plan_data['plan_name']}")

    print(f"\n✅ Database initialized successfully!")
    print(f"   Providers: {len(providers_data)}")
    print(f"   Sample plans: {len(sample_plans)}")
    print(f"\nNote: Run populate_database.py to scrape full plan data")

finally:
    db.close()
