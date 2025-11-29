"""
Production Data Quality Audit Script
Run this to check for fake/estimated data in your production database.

Usage:
    python audit_production_data.py
"""
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.models import Plan, Provider, Base
from app.database import DATABASE_URL

# Use production database URL if available
DB_URL = os.getenv("DATABASE_URL", DATABASE_URL)

print(f"🔍 Auditing database: {DB_URL[:50]}...")
print("=" * 80)

# Create engine and session
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
db = Session()


def audit_fake_data_markers():
    """Check for plans with fake data indicators."""
    print("\n📋 AUDIT 1: Checking for fake data markers...")
    print("-" * 80)

    fake_markers = ['estimate', 'typical', 'verify', 'fallback', 'sample', 'demo', 'call for']

    suspicious_plans = []
    for marker in fake_markers:
        plans = db.query(Plan).filter(
            Plan.special_features.ilike(f'%{marker}%')
        ).all()

        for plan in plans:
            suspicious_plans.append({
                'id': plan.id,
                'provider': plan.provider.name if plan.provider else 'Unknown',
                'plan_name': plan.plan_name,
                'service_type': plan.service_type,
                'rate': plan.rate_1000_cents,
                'special_features': plan.special_features,
                'marker': marker
            })

    if suspicious_plans:
        print(f"⚠️  FOUND {len(suspicious_plans)} SUSPICIOUS PLANS:")
        for plan in suspicious_plans:
            print(f"   ID {plan['id']}: {plan['provider']} - {plan['plan_name']}")
            print(f"      Rate: {plan['rate']}¢/kWh | Type: {plan['service_type']}")
            print(f"      🚩 Marker: '{plan['marker']}' in: {plan['special_features'][:100]}")
            print()
    else:
        print("✅ No plans with fake data markers found")

    return suspicious_plans


def audit_round_numbers():
    """Check for suspiciously round rates (often indicates fake data)."""
    print("\n📋 AUDIT 2: Checking for suspiciously round rates...")
    print("-" * 80)

    # Commercial plans with perfectly round numbers are suspicious
    round_commercial = db.query(Plan).filter(
        Plan.service_type == 'Commercial',
        Plan.rate_1000_cents.isnot(None),
        Plan.rate_1000_cents % 1 == 0  # Perfectly round
    ).all()

    if round_commercial:
        print(f"⚠️  FOUND {len(round_commercial)} COMMERCIAL PLANS WITH ROUND RATES:")
        for plan in round_commercial:
            print(f"   {plan.provider.name if plan.provider else 'Unknown'} - {plan.plan_name}")
            print(f"      Rate: {plan.rate_1000_cents}¢/kWh (suspiciously round)")
            print()
    else:
        print("✅ No suspiciously round commercial rates found")

    return round_commercial


def audit_data_freshness():
    """Check when plans were last updated."""
    print("\n📋 AUDIT 3: Checking data freshness...")
    print("-" * 80)

    from datetime import timedelta

    # Plans not updated in last 7 days
    week_ago = datetime.utcnow() - timedelta(days=7)
    stale_plans = db.query(Plan).filter(
        Plan.last_updated < week_ago
    ).count()

    # Get newest and oldest plans
    newest = db.query(Plan).order_by(Plan.last_updated.desc()).first()
    oldest = db.query(Plan).order_by(Plan.last_updated.asc()).first()

    print(f"   Total plans: {db.query(Plan).count()}")
    print(f"   Stale plans (>7 days old): {stale_plans}")
    if newest:
        print(f"   Newest plan updated: {newest.last_updated}")
    if oldest:
        print(f"   Oldest plan updated: {oldest.last_updated}")

    if stale_plans > 0:
        print(f"   ⚠️  {stale_plans} plans are over 7 days old")
    else:
        print("   ✅ All plans are fresh (< 7 days old)")


def audit_by_source():
    """Analyze plan counts by provider and service type."""
    print("\n📋 AUDIT 4: Plan distribution by provider and type...")
    print("-" * 80)

    # Group by service type
    residential_count = db.query(Plan).filter(Plan.service_type == 'Residential').count()
    commercial_count = db.query(Plan).filter(Plan.service_type == 'Commercial').count()

    print(f"   Residential: {residential_count} plans")
    print(f"   Commercial: {commercial_count} plans")
    print()

    # Group by provider for commercial
    print("   Commercial plans by provider:")
    commercial_providers = db.query(
        Provider.name,
        func.count(Plan.id).label('count')
    ).join(Plan).filter(
        Plan.service_type == 'Commercial'
    ).group_by(Provider.name).all()

    for provider, count in commercial_providers:
        print(f"      {provider}: {count} plans")

    # Expected counts based on working scrapers
    print()
    print("   📊 EXPECTED COUNTS (based on working scrapers):")
    print("      Residential: 68+ plans (PowerChoiceTexas)")
    print("      Commercial: 5+ plans (EnergyBot only)")

    if commercial_count > 10:
        print(f"   ⚠️  Commercial count ({commercial_count}) is higher than expected")
        print("       This might indicate fake/sample data is present")


def audit_missing_data():
    """Check for plans with missing critical fields."""
    print("\n📋 AUDIT 5: Checking for incomplete plans...")
    print("-" * 80)

    missing_rate = db.query(Plan).filter(
        Plan.rate_1000_cents.is_(None)
    ).count()

    missing_provider = db.query(Plan).filter(
        Plan.provider_id.is_(None)
    ).count()

    print(f"   Plans missing rate: {missing_rate}")
    print(f"   Plans missing provider: {missing_provider}")

    if missing_rate > 0 or missing_provider > 0:
        print("   ⚠️  Some plans have missing critical data")
    else:
        print("   ✅ All plans have complete data")


def generate_cleanup_sql(suspicious_plans):
    """Generate SQL to delete fake data."""
    if not suspicious_plans:
        return None

    plan_ids = [p['id'] for p in suspicious_plans]

    sql = f"""
-- SQL to delete fake/suspicious plans
-- Review this carefully before running!

DELETE FROM plans
WHERE id IN ({', '.join(map(str, plan_ids))});

-- This will delete {len(plan_ids)} plans
"""
    return sql


def main():
    print("\n" + "=" * 80)
    print("🔍 TEXAS ENERGY ANALYZER - PRODUCTION DATA AUDIT")
    print("=" * 80)

    try:
        # Run all audits
        suspicious = audit_fake_data_markers()
        round_rates = audit_round_numbers()
        audit_data_freshness()
        audit_by_source()
        audit_missing_data()

        # Summary
        print("\n" + "=" * 80)
        print("📊 AUDIT SUMMARY")
        print("=" * 80)

        total_issues = len(suspicious) + len(round_rates)

        if total_issues == 0:
            print("✅ NO ISSUES FOUND - Your data appears to be 100% real!")
        else:
            print(f"⚠️  FOUND {total_issues} POTENTIAL ISSUES")
            print(f"   - {len(suspicious)} plans with fake data markers")
            print(f"   - {len(round_rates)} commercial plans with suspiciously round rates")
            print()
            print("💡 RECOMMENDATIONS:")
            print("   1. Review the flagged plans above")
            print("   2. Delete fake data using the cleanup script")
            print("   3. Fix the TXU scraper to remove fallback data")
            print("   4. Re-run scrapers to populate with real data")

        # Generate cleanup script
        if suspicious:
            cleanup_sql = generate_cleanup_sql(suspicious)
            with open('cleanup_fake_data.sql', 'w') as f:
                f.write(cleanup_sql)
            print(f"\n📝 Generated cleanup script: cleanup_fake_data.sql")

        print("\n" + "=" * 80)

    except Exception as e:
        print(f"\n❌ ERROR during audit: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    main()
