"""
Save real scraped data to JSON file with proper datetime handling
"""
import json
from datetime import datetime
from app.scraping.scraper import scrape_all

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def save_real_data():
    """Scrape real data and save to JSON"""
    print("Scraping REAL data from PowerChoiceTexas...")
    plans = scrape_all()

    if not plans:
        print("ERROR: No plans scraped!")
        return

    print(f"SUCCESS: Scraped {len(plans)} REAL plans")

    # Save to JSON with datetime handling
    with open('real_plans.json', 'w') as f:
        json.dump(plans, f, indent=2, cls=DateTimeEncoder)

    print(f"Saved {len(plans)} REAL plans to real_plans.json")

if __name__ == "__main__":
    save_real_data()
