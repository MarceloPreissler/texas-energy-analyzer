"""
Test commercial scraping sources to see which ones work.
"""
from app.scraping.powertochoose_scraper import scrape_powertochoose
from app.scraping.energybot_scraper_v2 import scrape_energybot_commercial_v2

print("=" * 70)
print("TESTING COMMERCIAL ELECTRICITY PLAN SOURCES")
print("=" * 70)

# Test 1: PowerToChoose with Commercial service type
print("\n[TEST 1] PowerToChoose.org (Official PUCT) - Commercial Plans")
print("-" * 70)
try:
    ptc_plans = scrape_powertochoose(zip_code="75001", service_type="Commercial", max_plans=50)
    print(f"RESULT: Found {len(ptc_plans)} commercial plans\n")
    if ptc_plans:
        print("Sample plans:")
        for i, plan in enumerate(ptc_plans[:5], 1):
            print(f"  {i}. {plan['provider_name']} - {plan['plan_name']}")
            print(f"     Rate: {plan['rate_1000_cents']}cents/kWh, Term: {plan.get('contract_months', 'N/A')} months")
    else:
        print("  WARNING: No plans found")
except Exception as e:
    print(f"  ERROR: {e}")

# Test 2: EnergyBot v2
print("\n[TEST 2] EnergyBot.com - Commercial Plans")
print("-" * 70)
try:
    eb_plans = scrape_energybot_commercial_v2(zip_code="75001", max_plans=50)
    print(f"RESULT: Found {len(eb_plans)} commercial plans\n")
    if eb_plans:
        print("Sample plans:")
        for i, plan in enumerate(eb_plans[:5], 1):
            print(f"  {i}. {plan['provider_name']} - {plan['plan_name']}")
            print(f"     Rate: {plan['rate_1000_cents']}cents/kWh, Term: {plan.get('contract_months', 'N/A')} months")
except Exception as e:
    print(f"  ERROR: {e}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"PowerToChoose.org: {len(ptc_plans) if 'ptc_plans' in locals() else 0} plans")
print(f"EnergyBot.com: {len(eb_plans) if 'eb_plans' in locals() else 0} plans")
print(f"\nTOTAL COMMERCIAL PLANS: {len(ptc_plans if 'ptc_plans' in locals() else []) + len(eb_plans if 'eb_plans' in locals() else [])}")
print("=" * 70)
