"""
Test ALL commercial scraping sources.
"""
from app.scraping.energybot_scraper_v2 import scrape_energybot_commercial_v2
from app.scraping.txu_business_scraper import scrape_txu_commercial
from app.scraping.reliant_business_scraper import scrape_reliant_commercial

print("=" * 80)
print("TESTING ALL COMMERCIAL ELECTRICITY PLAN SOURCES")
print("=" * 80)

all_plans = []

# Test 1: EnergyBot (KNOWN TO WORK)
print("\n[SOURCE 1] EnergyBot.com - Commercial Plans")
print("-" * 80)
try:
    eb_plans = scrape_energybot_commercial_v2(zip_code="75001", max_plans=50)
    all_plans.extend(eb_plans)
    print(f"RESULT: {len(eb_plans)} plans\n")
    if eb_plans:
        for i, plan in enumerate(eb_plans[:3], 1):
            print(f"  {i}. {plan['provider_name']} - {plan['plan_name']} ({plan['rate_1000_cents']}cents/kWh)")
except Exception as e:
    print(f"  ERROR: {e}")

# Test 2: TXU Business
print("\n[SOURCE 2] TXU Energy - Business Plans")
print("-" * 80)
try:
    txu_plans = scrape_txu_commercial(zip_code="75001", max_plans=50)
    all_plans.extend(txu_plans)
    print(f"RESULT: {len(txu_plans)} plans\n")
    if txu_plans:
        for i, plan in enumerate(txu_plans[:3], 1):
            print(f"  {i}. {plan['plan_name']} ({plan['rate_1000_cents']}cents/kWh)")
            if plan.get('special_features'):
                print(f"      Note: {plan['special_features']}")
except Exception as e:
    print(f"  ERROR: {e}")

# Test 3: Reliant Business
print("\n[SOURCE 3] Reliant Energy - Business Plans")
print("-" * 80)
try:
    reliant_plans = scrape_reliant_commercial(zip_code="75001", max_plans=50)
    all_plans.extend(reliant_plans)
    print(f"RESULT: {len(reliant_plans)} plans\n")
    if reliant_plans:
        for i, plan in enumerate(reliant_plans[:3], 1):
            print(f"  {i}. {plan['plan_name']} ({plan['rate_1000_cents']}cents/kWh)")
except Exception as e:
    print(f"  ERROR: {e}")

# Summary
print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)
print(f"EnergyBot.com: {len(eb_plans) if 'eb_plans' in locals() else 0} plans")
print(f"TXU Energy: {len(txu_plans) if 'txu_plans' in locals() else 0} plans")
print(f"Reliant Energy: {len(reliant_plans) if 'reliant_plans' in locals() else 0} plans")
print(f"\nTOTAL COMMERCIAL PLANS: {len(all_plans)}")
print("=" * 80)

# Breakdown by provider
if all_plans:
    providers = {}
    for plan in all_plans:
        provider = plan['provider_name']
        if provider not in providers:
            providers[provider] = 0
        providers[provider] += 1

    print("\nBreakdown by Provider:")
    for provider, count in sorted(providers.items()):
        print(f"  {provider}: {count} plans")
