"""
Deploy REAL data to Railway production database.

Steps:
1. Wait for Railway deployment
2. Delete ALL sample data
3. Upload 73 REAL plans (68 residential + 5 commercial)
"""
import json
import requests
import time

RAILWAY_API_URL = "https://web-production-665ac.up.railway.app"

def deploy_real_data():
    """Deploy REAL data to Railway"""

    # Load the REAL plans
    print("Loading REAL plans from JSON...")
    with open('all_real_plans.json', 'r') as f:
        real_plans = json.load(f)
    print(f"Loaded {len(real_plans)} REAL plans")

    # Wait for Railway deployment
    print("\nWaiting 60 seconds for Railway to deploy latest code...")
    time.sleep(60)

    # Step 1: Delete ALL sample data
    print("\n" + "="*60)
    print("STEP 1: Deleting ALL sample/demonstration data...")
    print("="*60)

    try:
        response = requests.post(
            f"{RAILWAY_API_URL}/admin/delete-all-plans",
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: Deleted {result['deleted_count']} sample plans")
        else:
            print(f"ERROR: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            print("\nTrying to continue anyway...")

    except Exception as e:
        print(f"ERROR deleting sample data: {e}")
        print("Continuing to upload real data...")

    # Step 2: Upload REAL data
    print("\n" + "="*60)
    print("STEP 2: Uploading 73 REAL plans to Railway...")
    print("="*60)

    try:
        response = requests.post(
            f"{RAILWAY_API_URL}/admin/load-real-data",
            json=real_plans,
            headers={"Content-Type": "application/json"},
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n{'='*60}")
            print("SUCCESS! REAL DATA IS NOW LIVE ON PRODUCTION!")
            print(f"{'='*60}")
            print(f"  - Added: {result['added']} new plans")
            print(f"  - Updated: {result['updated']} existing plans")
            print(f"  - Total: {result['total']} REAL plans in Railway")
            print(f"\nProduction site: https://texasenergyanalyzer.com")
            print(f"{'='*60}\n")
        else:
            print(f"ERROR: HTTP {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"ERROR uploading real data: {e}")

if __name__ == "__main__":
    deploy_real_data()
