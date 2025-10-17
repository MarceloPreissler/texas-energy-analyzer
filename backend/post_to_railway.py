"""
POST real scraped data to Railway production API
"""
import json
import requests
import time

RAILWAY_API_URL = "https://web-production-665ac.up.railway.app"

def post_to_railway():
    """Load real data from JSON and POST to Railway"""

    # Load JSON data
    print("Loading REAL plans from JSON...")
    with open('real_plans.json', 'r') as f:
        plans = json.load(f)

    print(f"Loaded {len(plans)} REAL plans from JSON")

    # Wait for Railway deployment (give it 60 seconds)
    print("Waiting 60 seconds for Railway to deploy new endpoint...")
    time.sleep(60)

    # POST to Railway endpoint
    print(f"POSTing REAL data to Railway: {RAILWAY_API_URL}/admin/load-real-data")

    try:
        response = requests.post(
            f"{RAILWAY_API_URL}/admin/load-real-data",
            json=plans,
            headers={"Content-Type": "application/json"},
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\nSUCCESS! {result['message']}")
            print(f"   - Added: {result['added']} new plans")
            print(f"   - Updated: {result['updated']} existing plans")
            print(f"   - Total: {result['total']} REAL plans in Railway database")
            print(f"\nREAL DATA IS NOW LIVE ON: https://texasenergyanalyzer.com")
        else:
            print(f"ERROR: HTTP {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    post_to_railway()
