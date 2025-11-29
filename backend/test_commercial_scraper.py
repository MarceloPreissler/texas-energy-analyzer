from app.scraping.energybot_scraper_v2 import scrape_energybot_commercial_v2
import logging

# Configure logging to see scraper output
logging.basicConfig(level=logging.INFO)

print("Starting commercial scraper test...")
try:
    plans = scrape_energybot_commercial_v2(zip_code="75001", max_plans=5)
    print(f"Scraper finished. Found {len(plans)} plans.")
    for p in plans:
        print(f"- {p['provider_name']}: {p['plan_name']} ({p['rate_1000_cents']} cents)")
except Exception as e:
    print(f"Scraper failed: {e}")
