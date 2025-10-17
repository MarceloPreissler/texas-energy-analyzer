"""
Master scraper - REAL DATA ONLY from live sources.

NO sample data. NO fallback data. ONLY scraped real plans.

Sources:
- Residential: Legacy scraper (PowerChoiceTexas, provider sites) - 68+ plans
- Commercial: EnergyBot v2 (JSON-LD structured data) - 5+ plans

Total: 73+ REAL plans
"""
import json
from datetime import datetime
from app.scraping.scraper import scrape_all  # Residential scraper
from app.scraping.energybot_scraper_v2 import scrape_energybot_all_texas_v2  # Commercial scraper


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def scrape_all_real_plans():
    """
    Scrape ALL REAL plans from live sources.
    NO sample data. NO fallback data.

    Returns:
        dict with residential_plans, commercial_plans, and total count
    """
    print("="*60)
    print("SCRAPING REAL DATA FROM LIVE SOURCES")
    print("NO SAMPLE DATA - ONLY LIVE SCRAPED PLANS")
    print("="*60)

    # 1. Scrape REAL residential plans
    print("\n[1/2] Scraping RESIDENTIAL plans from PowerChoiceTexas...")
    residential_plans = scrape_all()
    print(f"SUCCESS: Scraped {len(residential_plans)} REAL residential plans")

    # 2. Scrape REAL commercial plans
    print("\n[2/2] Scraping COMMERCIAL plans from EnergyBot...")
    commercial_plans = scrape_energybot_all_texas_v2()
    print(f"SUCCESS: Scraped {len(commercial_plans)} REAL commercial plans")

    # Combine all plans
    all_plans = residential_plans + commercial_plans

    print("\n" + "="*60)
    print(f"TOTAL REAL PLANS SCRAPED: {len(all_plans)}")
    print(f"  - Residential: {len(residential_plans)}")
    print(f"  - Commercial: {len(commercial_plans)}")
    print("="*60)

    return {
        "residential_plans": residential_plans,
        "commercial_plans": commercial_plans,
        "all_plans": all_plans,
        "total": len(all_plans),
        "scraped_at": datetime.now().isoformat()
    }


def save_real_plans_to_json():
    """Save all REAL scraped plans to JSON file"""
    print("\nScraping and saving REAL plans to JSON...")

    result = scrape_all_real_plans()

    # Save to JSON with datetime handling
    with open('all_real_plans.json', 'w') as f:
        json.dump(result['all_plans'], f, indent=2, cls=DateTimeEncoder)

    print(f"\nSUCCESS: Saved {result['total']} REAL plans to all_real_plans.json")

    # Print sample plans from each category
    print("\n" + "-"*60)
    print("SAMPLE RESIDENTIAL PLANS:")
    for i, plan in enumerate(result['residential_plans'][:3], 1):
        print(f"  {i}. {plan['provider_name']} - {plan['plan_name']}")
        print(f"     Rate: {plan.get('rate_1000_cents', 'N/A')}¢/kWh")

    print("\n" + "-"*60)
    print("SAMPLE COMMERCIAL PLANS:")
    for i, plan in enumerate(result['commercial_plans'][:3], 1):
        print(f"  {i}. {plan['provider_name']} - {plan['plan_name']}")
        print(f"     Rate: {plan.get('rate_1000_cents', 'N/A')}¢/kWh")
    print("-"*60)

    return result


if __name__ == "__main__":
    save_real_plans_to_json()
