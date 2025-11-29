import sys
import os

# Add the current directory to the Python path
sys.path.append(os.getcwd())

from app.scraping.powertochoose_scraper import scrape_powertochoose

if __name__ == "__main__":
    print("Starting PowerToChoose debug...")
    try:
        plans = scrape_powertochoose("75001")
        print(f"Final Result: {len(plans)} plans found.")
        for plan in plans[:5]:
            print(f"- {plan['provider_name']}: {plan['plan_name']} ({plan['rate_1000_cents']} cents)")
    except Exception as e:
        print(f"Debug failed: {e}")
