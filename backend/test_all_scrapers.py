"""
Comprehensive test script for all three scrapers.
Tests each scraper and reports success/failure with details.
"""
import sys
import os

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime


def test_legacy_scraper():
    """Test the legacy scraper (comparison sites)."""
    print("\n" + "="*60)
    print("Testing Legacy Scraper (PowerChoiceTexas)")
    print("="*60)

    try:
        from app.scraping.scraper import scrape_all

        print("Starting legacy scrape...")
        start_time = datetime.now()
        plans = scrape_all()
        elapsed = (datetime.now() - start_time).total_seconds()

        print(f"✓ Success! Scraped {len(plans)} plans in {elapsed:.2f} seconds")

        if plans:
            print(f"\nSample plan:")
            sample = plans[0]
            print(f"  Provider: {sample.get('provider_name')}")
            print(f"  Plan: {sample.get('plan_name')}")
            print(f"  Rate: {sample.get('rate_1000_cents')}¢/kWh")
            print(f"  Type: {sample.get('plan_type')}")

        return True, len(plans)

    except Exception as e:
        print(f"✗ Failed: {e}")
        return False, 0


def test_powertochoose_scraper():
    """Test the PowerToChoose.org scraper."""
    print("\n" + "="*60)
    print("Testing PowerToChoose.org Scraper (Official PUCT)")
    print("="*60)

    try:
        from app.scraping.powertochoose_scraper import scrape_powertochoose

        print("Starting PowerToChoose scrape for Dallas (75001)...")
        start_time = datetime.now()
        plans = scrape_powertochoose(zip_code="75001", max_plans=20)
        elapsed = (datetime.now() - start_time).total_seconds()

        print(f"✓ Success! Scraped {len(plans)} plans in {elapsed:.2f} seconds")

        if plans:
            print(f"\nSample plan:")
            sample = plans[0]
            print(f"  Provider: {sample.get('provider_name')}")
            print(f"  Plan: {sample.get('plan_name')}")
            print(f"  Rate: {sample.get('rate_1000_cents')}¢/kWh")
            print(f"  Type: {sample.get('plan_type')}")
            print(f"  Service Type: {sample.get('service_type')}")

        return True, len(plans)

    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False, 0


def test_energybot_scraper():
    """Test the EnergyBot scraper."""
    print("\n" + "="*60)
    print("Testing EnergyBot Scraper (Commercial Plans)")
    print("="*60)

    try:
        from app.scraping.energybot_scraper import scrape_energybot_commercial

        print("Starting EnergyBot scrape for Dallas (75001)...")
        start_time = datetime.now()
        plans = scrape_energybot_commercial(zip_code="75001", max_plans=20)
        elapsed = (datetime.now() - start_time).total_seconds()

        print(f"✓ Success! Scraped {len(plans)} plans in {elapsed:.2f} seconds")

        if plans:
            print(f"\nSample plan:")
            sample = plans[0]
            print(f"  Provider: {sample.get('provider_name')}")
            print(f"  Plan: {sample.get('plan_name')}")
            print(f"  Rate: {sample.get('rate_1000_cents')}¢/kWh")
            print(f"  Type: {sample.get('plan_type')}")
            print(f"  Service Type: {sample.get('service_type')}")

        return True, len(plans)

    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False, 0


def main():
    """Run all tests and provide summary."""
    print("\n" + "#"*60)
    print("# Texas Energy Analyzer - Scraper Test Suite")
    print("# Testing all three data sources")
    print("#"*60)

    results = []

    # Test each scraper
    results.append(("Legacy Scraper", *test_legacy_scraper()))
    results.append(("PowerToChoose.org", *test_powertochoose_scraper()))
    results.append(("EnergyBot", *test_energybot_scraper()))

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    total_plans = 0
    passed = 0

    for name, success, count in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} - {name}: {count} plans")
        if success:
            passed += 1
            total_plans += count

    print("\n" + "-"*60)
    print(f"Tests Passed: {passed}/3")
    print(f"Total Plans Scraped: {total_plans}")
    print("-"*60)

    if passed == 3:
        print("\n🎉 All scrapers working perfectly!")
    elif passed > 0:
        print(f"\n⚠️  {3-passed} scraper(s) need attention")
    else:
        print("\n❌ All scrapers failed - check dependencies")

    return passed == 3


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
