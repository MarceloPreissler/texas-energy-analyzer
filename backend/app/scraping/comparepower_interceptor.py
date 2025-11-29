"""
ComparePower.com scraper using Network Request Interception.

This is the MOST RELIABLE approach - it captures API responses automatically
without needing to parse HTML or manually find API endpoints.

NO COST - Uses only free tools (Playwright).
"""
from __future__ import annotations

import json
import re
from typing import List, Dict
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright, Route, Request


def scrape_comparepower_with_interception(zip_code: str = "75001", max_plans: int = 100) -> List[Dict]:
    """
    Scrape ComparePower using network request interception.

    This approach:
    1. Launches a real browser
    2. Intercepts ALL network requests
    3. Captures API responses that contain plan data
    4. Parses the JSON directly (no HTML parsing!)

    This is IMMUNE to website redesigns because we're capturing
    the underlying data, not the visual presentation.

    Args:
        zip_code: Texas zip code
        max_plans: Maximum plans to return

    Returns:
        List of plan dictionaries
    """
    plans = []
    captured_responses = []

    def intercept_handler(route: Route, request: Request):
        """
        Intercept network requests and capture API responses.

        This runs for EVERY network request the page makes.
        """
        # Let the request proceed normally
        response = route.fetch()

        # Only process JSON responses (API calls)
        content_type = response.headers.get('content-type', '')
        if 'json' in content_type.lower():
            try:
                # Try to parse as JSON
                body = response.body()
                data = json.loads(body)

                # Check if this looks like plan data
                # (contains arrays or objects with plan-like fields)
                if contains_plan_data(data, request.url):
                    print(f"[Interceptor] 📡 Captured API response from: {request.url}")
                    captured_responses.append({
                        'url': request.url,
                        'data': data
                    })

            except (json.JSONDecodeError, Exception) as e:
                # Not JSON or couldn't parse - ignore
                pass

        # Always fulfill the request (don't block the page)
        route.fulfill(response=response)

    with sync_playwright() as p:
        print(f"[Interceptor] Launching browser...")

        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']  # Stealth mode
        )

        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        page = context.new_page()

        # CRITICAL: Set up interception BEFORE navigating
        print(f"[Interceptor] Setting up network interception...")
        page.route("**/*", intercept_handler)

        try:
            # Navigate to the page
            url = "https://comparepower.com/electricity-rates/texas/business-commercial-electricity/"
            print(f"[Interceptor] Navigating to {url}...")

            page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Try to enter zip code
            try:
                # Look for zip input
                zip_input = page.locator('input[name="zip"], input[placeholder*="zip" i]').first
                if zip_input.is_visible(timeout=5000):
                    print(f"[Interceptor] Entering zip code: {zip_code}")
                    zip_input.fill(zip_code)

                    # Submit the form
                    submit_btn = page.locator('button[type="submit"], button:has-text("Search")').first
                    submit_btn.click()

                    # Wait for API responses
                    print(f"[Interceptor] Waiting for API responses...")
                    page.wait_for_timeout(5000)
            except Exception as e:
                print(f"[Interceptor] Couldn't interact with form: {e}")
                # Still might have captured some data from initial page load

            # Scroll to trigger lazy loading
            print(f"[Interceptor] Scrolling to load more data...")
            for i in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)

            print(f"[Interceptor] Captured {len(captured_responses)} API responses")

            # Parse captured API responses
            for response_data in captured_responses:
                parsed = parse_api_response(response_data['data'], zip_code)
                plans.extend(parsed)

        except Exception as e:
            print(f"[Interceptor] Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()

    # Deduplicate plans
    unique_plans = deduplicate_plans(plans)

    print(f"[Interceptor] Successfully captured {len(unique_plans)} unique commercial plans")
    return unique_plans[:max_plans]


def contains_plan_data(data: any, url: str) -> bool:
    """
    Check if API response contains electricity plan data.

    Heuristic: Look for arrays/objects with plan-like fields.
    """
    # URLs that likely contain plan data
    url_keywords = ['plan', 'rate', 'search', 'compare', 'quote', 'offer']
    if any(keyword in url.lower() for keyword in url_keywords):
        # Check data structure
        if isinstance(data, list) and len(data) > 0:
            return True
        if isinstance(data, dict):
            # Common keys for plan data
            plan_keys = ['plans', 'results', 'data', 'items', 'offers']
            if any(key in data for key in plan_keys):
                return True

    # Deep check: look for plan-like fields in the data
    data_str = json.dumps(data).lower()
    plan_indicators = ['provider', 'kwh', 'rate', 'cents', 'month', 'contract', 'term']

    matches = sum(1 for indicator in plan_indicators if indicator in data_str)
    return matches >= 3  # If 3+ indicators found, likely plan data


def parse_api_response(data: any, zip_code: str) -> List[Dict]:
    """
    Parse API response and extract plan data.

    Handles multiple JSON structures automatically.
    """
    plans = []

    # Extract array from various structures
    raw_items = []

    if isinstance(data, list):
        raw_items = data
    elif isinstance(data, dict):
        # Try common keys
        for key in ['plans', 'results', 'data', 'items', 'offers', 'products']:
            if key in data:
                value = data[key]
                if isinstance(value, list):
                    raw_items = value
                    break

    print(f"[Interceptor] Parsing {len(raw_items)} items from API response...")

    for item in raw_items:
        try:
            if not isinstance(item, dict):
                continue

            # Extract fields with multiple possible names
            provider = (
                item.get('provider') or
                item.get('providerName') or
                item.get('provider_name') or
                item.get('company') or
                'Unknown Provider'
            )

            plan_name = (
                item.get('name') or
                item.get('planName') or
                item.get('plan_name') or
                item.get('title') or
                'Unknown Plan'
            )

            rate = (
                item.get('rate') or
                item.get('pricePerKwh') or
                item.get('rate_1000') or
                item.get('price') or
                item.get('cents_per_kwh')
            )

            term = (
                item.get('term') or
                item.get('contractLength') or
                item.get('contract_months') or
                item.get('months')
            )

            plan_type = item.get('type') or item.get('planType') or 'Fixed'

            # Convert rate to float if needed
            if rate:
                try:
                    rate = float(rate)
                except (ValueError, TypeError):
                    # Try to extract number from string
                    rate_match = re.search(r'(\d+\.?\d*)', str(rate))
                    if rate_match:
                        rate = float(rate_match.group(1))
                    else:
                        rate = None

            # Validate rate range
            if rate and (rate < 5 or rate > 20):
                continue  # Skip invalid rates

            if provider and plan_name and rate:
                plans.append({
                    "provider_name": str(provider)[:100],
                    "plan_name": str(plan_name)[:200],
                    "plan_type": str(plan_type),
                    "service_type": "Commercial",
                    "zip_code": zip_code,
                    "contract_months": int(term) if term else None,
                    "rate_1000_cents": round(float(rate), 3),
                    "special_features": item.get('features') or item.get('description') or '',
                    "last_updated": datetime.now(timezone.utc),
                })

                print(f"[Interceptor]   ✓ {provider} - {plan_name}: {rate}¢/kWh")

        except Exception as e:
            print(f"[Interceptor] Error parsing item: {e}")
            continue

    return plans


def deduplicate_plans(plans: List[Dict]) -> List[Dict]:
    """Remove duplicate plans based on provider + name + rate."""
    seen = set()
    unique = []

    for plan in plans:
        key = (
            plan['provider_name'],
            plan['plan_name'],
            plan.get('rate_1000_cents')
        )

        if key not in seen:
            seen.add(key)
            unique.append(plan)

    return unique


# Test the interceptor
if __name__ == "__main__":
    print("Testing ComparePower Network Interceptor...")
    print("=" * 60)

    plans = scrape_comparepower_with_interception(zip_code="75001", max_plans=50)

    print(f"\n{'=' * 60}")
    print(f"RESULTS: Captured {len(plans)} commercial plans")
    print(f"{'=' * 60}\n")

    if plans:
        print("Sample plans:")
        for i, plan in enumerate(plans[:10], 1):
            print(f"\n{i}. {plan['provider_name']} - {plan['plan_name']}")
            print(f"   Rate: {plan['rate_1000_cents']}¢/kWh")
            if plan['contract_months']:
                print(f"   Term: {plan['contract_months']} months")
    else:
        print("⚠️  No plans captured")
        print("This might mean:")
        print("  1. The site doesn't use API calls (unlikely)")
        print("  2. The API endpoints are different than expected")
        print("  3. Need to adjust the detection heuristics")
        print("\nTry running with headless=False to debug visually")
