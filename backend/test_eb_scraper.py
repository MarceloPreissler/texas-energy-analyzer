"""Test the EnergyBot scraper"""
import sys
from app.scraping import energybot_scraper

try:
    print("Testing EnergyBot commercial scraper...")
    plans = energybot_scraper.scrape_energybot_commercial("75001", max_plans=10)

    print(f"\nFound {len(plans)} plans")

    if plans:
        print("\nSample plan:")
        for key, value in plans[0].items():
            print(f"  {key}: {value}")
    else:
        print("\nNo plans found - check energybot_debug.html for page content")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
