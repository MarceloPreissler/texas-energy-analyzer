#!/usr/bin/env python3
"""
Quick database viewer - Shows what's in the local database
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import SessionLocal
from app.models import Plan, Provider

db = SessionLocal()

print("\n" + "="*70)
print("DATABASE CONTENTS")
print("="*70)

# Count providers and plans
providers = db.query(Provider).all()
commercial = db.query(Plan).filter(Plan.service_type == "Commercial").all()
residential = db.query(Plan).filter(Plan.service_type == "Residential").all()

print(f"\n📊 Summary:")
print(f"   Providers: {len(providers)}")
print(f"   Commercial Plans: {len(commercial)}")
print(f"   Residential Plans: {len(residential)}")
print(f"   TOTAL: {len(commercial) + len(residential)} plans")

if providers:
    print(f"\n🏢 Providers:")
    for p in providers:
        plan_count = db.query(Plan).filter(Plan.provider_id == p.id).count()
        print(f"   • {p.name} ({plan_count} plans)")

if commercial:
    print(f"\n💼 Commercial Plans:")
    for plan in commercial[:10]:
        provider = db.query(Provider).filter(Provider.id == plan.provider_id).first()
        rate = f"{plan.rate_1000_cents/100:.1f}¢" if plan.rate_1000_cents else "N/A"
        print(f"   • {provider.name}: {plan.plan_name[:50]}")
        print(f"     {rate}/kWh | {plan.contract_months} months")

if residential:
    print(f"\n🏠 Residential Plans:")
    for plan in residential[:10]:
        provider = db.query(Provider).filter(Provider.id == plan.provider_id).first()
        rate = f"{plan.rate_1000_cents/100:.1f}¢" if plan.rate_1000_cents else "N/A"
        print(f"   • {provider.name}: {plan.plan_name[:50]}")
        print(f"     {rate}/kWh | {plan.contract_months} months")

print("\n" + "="*70 + "\n")

db.close()
