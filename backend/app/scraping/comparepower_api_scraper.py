"""
ComparePower.com API scraper - Direct API approach (most reliable).

This scraper calls ComparePower's internal API directly instead of parsing HTML.
Find the API endpoint using Chrome DevTools → Network tab.
"""
from __future__ import annotations

import requests
import re
from typing import List, Dict
from datetime import datetime, timezone


def scrape_comparepower_api(zip_code: str = "75001") -> List[Dict]:
    """
    Scrape commercial plans by calling ComparePower's API directly.

    SETUP REQUIRED:
    1. Open https://comparepower.com/electricity-rates/texas/business-commercial-electricity/
    2. Open Chrome DevTools (F12) → Network tab → Filter: Fetch/XHR
    3. Enter zip code and search
    4. Find the API request that returns plan data (look in Preview tab)
    5. Right-click → Copy → Copy as cURL
    6. Update the endpoint, headers, and payload below

    Args:
        zip_code: Texas zip code

    Returns:
        List of plan dictionaries
    """

    print(f"[ComparePower API] Searching for commercial plans in {zip_code}...")

    # STEP 1: Update this URL with the real API endpoint
    # (Find it using DevTools Network tab)
    api_url = "https://comparepower.com/api/v1/plans/search"  # PLACEHOLDER - UPDATE THIS!

    # STEP 2: Update headers (copy from DevTools)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Referer': 'https://comparepower.com/electricity-rates/texas/business-commercial-electricity/',
        # Add any API keys or auth tokens found in DevTools
        # 'x-api-key': 'YOUR_KEY_HERE',
        # 'Authorization': 'Bearer YOUR_TOKEN',
    }

    # STEP 3: Update payload (the data sent to the API)
    payload = {
        "zip": zip_code,
        "serviceType": "commercial",
        "usage": 5000,  # 5000 kWh (typical small business)
    }

    plans = []

    try:
        # Make the API request
        response = requests.post(
            api_url,
            json=payload,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()
        data = response.json()

        print(f"[ComparePower API] Received response: {len(str(data))} characters")

        # STEP 4: Parse the JSON response
        # The structure depends on the API's response format
        # Common patterns:

        # Pattern 1: Array at root
        if isinstance(data, list):
            raw_plans = data

        # Pattern 2: Nested in a key
        elif isinstance(data, dict):
            # Try common keys
            raw_plans = (
                data.get('plans') or
                data.get('results') or
                data.get('data') or
                data.get('items') or
                []
            )
        else:
            print("[ComparePower API] Unexpected response format")
            return []

        print(f"[ComparePower API] Found {len(raw_plans)} raw plan entries")

        # STEP 5: Transform API response to our format
        for item in raw_plans:
            try:
                # Extract fields (adjust based on actual API response)
                plan = {
                    "provider_name": item.get('provider') or item.get('providerName') or 'Unknown',
                    "plan_name": item.get('name') or item.get('planName') or 'Unknown Plan',
                    "plan_type": item.get('type') or 'Fixed',
                    "service_type": "Commercial",
                    "zip_code": zip_code,
                    "contract_months": item.get('term') or item.get('contractLength'),
                    "rate_1000_cents": item.get('rate') or item.get('pricePerKwh'),
                    "special_features": item.get('features') or item.get('description') or '',
                    "last_updated": datetime.now(timezone.utc),
                }

                # Validate required fields
                if plan['provider_name'] and plan['plan_name'] and plan['rate_1000_cents']:
                    plans.append(plan)
                    print(f"[ComparePower API] ✓ {plan['provider_name']} - {plan['plan_name']}: {plan['rate_1000_cents']}¢/kWh")

            except Exception as e:
                print(f"[ComparePower API] Error parsing item: {e}")
                continue

        print(f"[ComparePower API] Successfully parsed {len(plans)} plans")

    except requests.exceptions.RequestException as e:
        print(f"[ComparePower API] Request failed: {e}")
    except Exception as e:
        print(f"[ComparePower API] Error: {e}")
        import traceback
        traceback.print_exc()

    return plans


def discover_api_endpoint():
    """
    Helper function to discover the API endpoint.

    Returns instructions for finding the real API endpoint.
    """
    instructions = """
    🔍 HOW TO FIND THE COMPAREPOWER API ENDPOINT:

    1. Open Chrome browser

    2. Visit: https://comparepower.com/electricity-rates/texas/business-commercial-electricity/

    3. Open DevTools (F12 or Ctrl+Shift+I)

    4. Go to Network tab

    5. Click "Fetch/XHR" filter button (to see only API calls)

    6. Clear existing requests (trash can icon)

    7. On the website, enter zip code "75001" and click search

    8. Watch the Network tab - you'll see API requests appear

    9. Click on each request and check the "Preview" tab
       - Look for JSON data containing plan information
       - Should have fields like: provider, name, rate, etc.

    10. Once you find the right request:
        - Note the Request URL
        - Check Headers tab for any API keys
        - Check Payload tab for the data being sent
        - Right-click → Copy → Copy as cURL

    11. Use https://curlconverter.com to convert cURL to Python

    12. Update scrape_comparepower_api() with the real endpoint

    COMMON API PATTERNS:
    - /api/plans
    - /api/v1/search
    - /api/rates
    - /graphql (if using GraphQL)

    WHAT TO LOOK FOR IN RESPONSE:
    {
      "plans": [
        {
          "provider": "TXU Energy",
          "name": "Business Advantage 12",
          "rate": 11.5,
          "term": 12
        }
      ]
    }
    """
    print(instructions)


# Test the discovery process
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--discover":
        discover_api_endpoint()
    else:
        print("Testing ComparePower API scraper...")
        print("=" * 60)
        print()
        print("⚠️  NOTE: This is a TEMPLATE. You must first discover the real API endpoint.")
        print("   Run: python comparepower_api_scraper.py --discover")
        print()
        print("   Then update the api_url, headers, and payload in the code.")
        print("=" * 60)

        # Uncomment when you've updated the API details:
        # plans = scrape_comparepower_api()
        # print(f"\nResult: {len(plans)} plans scraped")
