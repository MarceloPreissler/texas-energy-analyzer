"""
ElectricityPlans.com commercial electricity plan scraper using Playwright.

Scrapes business electricity plans from ElectricityPlans.com,
which provides structured data and tables with plan information.
Uses playwright-stealth to bypass bot detection.
"""
from __future__ import annotations

import json
import re
from typing import List, Dict
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from playwright_stealth import stealth_sync


def scrape_electricityplans_commercial(zip_code: str = "75001", max_plans: int = 100) -> List[Dict]:
    """
    Scrape commercial electricity plans from ElectricityPlans.com.

    This scraper uses two strategies:
    1. Extract JSON-LD structured data (most reliable)
    2. Scrape HTML tables (fallback)

    Args:
        zip_code: Texas zip code to search (default: 75001 - Dallas)
        max_plans: Maximum number of plans to scrape (default: 100)

    Returns:
        List of plan dictionaries with provider_name, plan_name, rate, etc.
    """
    plans: List[Dict] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']  # Additional stealth
        )
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        # STEALTH MODE: Makes browser undetectable as automation
        stealth_sync(page)
        print("[ElectricityPlans] Stealth mode activated - bypassing bot detection")

        try:
            url = "https://electricityplans.com/texas/compare/business-electricity/"
            print(f"[ElectricityPlans] Navigating to {url}...")

            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)  # Wait for dynamic content

            # Accept cookies if present
            try:
                cookie_selectors = [
                    'button:has-text("Accept")',
                    'button:has-text("I Accept")',
                    '.cookie-accept'
                ]
                for selector in cookie_selectors:
                    try:
                        page.click(selector, timeout=2000)
                        print("[ElectricityPlans] Accepted cookies")
                        break
                    except:
                        continue
            except:
                pass

            # Try to enter zip code if there's a form
            try:
                zip_input_selectors = [
                    'input[name="zip"]',
                    'input[placeholder*="zip" i]',
                    'input[type="text"][name*="zip"]',
                    '#zip-code'
                ]

                for selector in zip_input_selectors:
                    try:
                        if page.query_selector(selector):
                            print(f"[ElectricityPlans] Entering zip code: {zip_code}")
                            page.fill(selector, zip_code)

                            # Click submit button
                            submit_selectors = [
                                'button[type="submit"]',
                                'button:has-text("Compare")',
                                'button:has-text("Search")',
                                'input[type="submit"]'
                            ]
                            for submit_selector in submit_selectors:
                                try:
                                    page.click(submit_selector, timeout=2000)
                                    page.wait_for_timeout(3000)
                                    break
                                except:
                                    continue
                            break
                    except:
                        continue
            except Exception as e:
                print(f"[ElectricityPlans] No zip input found: {e}")

            # Scroll to load dynamic content
            print("[ElectricityPlans] Scrolling to load all content...")
            for _ in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1500)

            print("[ElectricityPlans] Extracting data...")

            # Strategy 1: Extract JSON-LD structured data
            print("[ElectricityPlans] Looking for JSON-LD structured data...")
            scripts = page.query_selector_all('script[type="application/ld+json"]')
            print(f"[ElectricityPlans] Found {len(scripts)} JSON-LD scripts")

            for script in scripts:
                try:
                    json_text = script.inner_text()
                    data = json.loads(json_text)

                    # Look for itemList or offers
                    items = []
                    if isinstance(data, dict):
                        if data.get('@type') == 'ItemList' and 'itemListElement' in data:
                            items = data['itemListElement']
                        elif 'offers' in data:
                            items = data['offers'] if isinstance(data['offers'], list) else [data['offers']]

                    for item in items:
                        try:
                            # Handle different JSON-LD structures
                            if '@type' in item and item['@type'] == 'ListItem':
                                item = item.get('item', {})

                            # Extract plan details
                            provider_name = "Unknown Provider"
                            plan_name = "Unknown Plan"
                            rate = None
                            contract_months = None

                            # Try different field names
                            if 'seller' in item:
                                provider_name = item['seller'].get('name', provider_name)
                            elif 'brand' in item:
                                provider_name = item['brand'].get('name', provider_name)
                            elif 'provider' in item:
                                provider_name = item.get('provider', provider_name)

                            if 'name' in item:
                                plan_name = item['name']

                            # Extract price/rate
                            price_data = item.get('offers', item.get('priceSpecification', {}))
                            if isinstance(price_data, dict):
                                # Try to get price in cents/kWh
                                price = price_data.get('price', price_data.get('priceComponent', {}).get('price'))
                                if price:
                                    rate = float(price) if price < 1 else float(price) * 100

                            # Extract term length
                            if 'duration' in item:
                                duration_str = item['duration']
                                match = re.search(r'(\d+)\s*month', str(duration_str), re.IGNORECASE)
                                if match:
                                    contract_months = int(match.group(1))

                            if rate and provider_name != "Unknown Provider":
                                plans.append({
                                    "provider_name": provider_name,
                                    "plan_name": plan_name[:200],
                                    "plan_type": "Fixed",  # Assume fixed unless specified
                                    "service_type": "Commercial",
                                    "zip_code": zip_code,
                                    "contract_months": contract_months,
                                    "rate_1000_cents": round(rate, 3),
                                    "special_features": None,
                                    "last_updated": datetime.now(timezone.utc),
                                })
                                print(f"[ElectricityPlans] (JSON-LD) Found: {provider_name} - {plan_name}")

                        except Exception as e:
                            print(f"[ElectricityPlans] Error parsing JSON item: {e}")
                            continue

                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"[ElectricityPlans] Error processing JSON-LD: {e}")
                    continue

            # Strategy 2: Scrape HTML tables
            print("[ElectricityPlans] Looking for HTML tables...")
            table_selectors = [
                'table',
                'table.rates',
                'table.plans',
                '.rate-table',
                '[class*="table"]'
            ]

            tables = []
            for selector in table_selectors:
                elements = page.query_selector_all(selector)
                if elements:
                    tables.extend(elements)

            print(f"[ElectricityPlans] Found {len(tables)} tables")

            for table_idx, table in enumerate(tables):
                try:
                    # Get all rows
                    rows = table.query_selector_all('tr')
                    print(f"[ElectricityPlans] Table {table_idx + 1}: {len(rows)} rows")

                    # Find header row to understand column structure
                    headers = []
                    header_row = table.query_selector('thead tr, tr:first-child')
                    if header_row:
                        header_cells = header_row.query_selector_all('th, td')
                        headers = [cell.inner_text().strip().lower() for cell in header_cells]
                        print(f"[ElectricityPlans] Headers: {headers}")

                    # Process data rows
                    data_rows = table.query_selector_all('tbody tr, tr:not(:first-child)')

                    for row in data_rows:
                        try:
                            cells = row.query_selector_all('td')
                            if len(cells) < 2:
                                continue

                            cell_texts = [cell.inner_text().strip() for cell in cells]

                            # Try to identify columns
                            provider_name = "Unknown Provider"
                            plan_name = None
                            rate = None
                            contract_months = None

                            # Look for rate (with ¢ or cents)
                            for text in cell_texts:
                                rate_match = re.search(r'(\d+\.?\d*)\s*[¢c]', text, re.IGNORECASE)
                                if not rate_match:
                                    rate_match = re.search(r'(\d+\.\d+)', text)
                                if rate_match:
                                    rate_candidate = float(rate_match.group(1))
                                    # Ensure it's in a reasonable range
                                    if rate_candidate < 1:
                                        rate_candidate *= 100
                                    if 5 <= rate_candidate <= 20:
                                        rate = rate_candidate
                                        break

                            # Look for term (months)
                            for text in cell_texts:
                                term_match = re.search(r'(\d+)\s*(?:month|mo)', text, re.IGNORECASE)
                                if term_match:
                                    contract_months = int(term_match.group(1))
                                    break

                            # Use known provider names from the cell texts
                            provider_patterns = [
                                'reliant', 'engie', 'apg&e', 'constellation',
                                'gexa', 'txu', 'direct energy', 'green mountain',
                                'champion', 'cirro', 'frontier'
                            ]

                            for text in cell_texts:
                                for provider_pattern in provider_patterns:
                                    if provider_pattern in text.lower():
                                        provider_name = text
                                        break
                                if provider_name != "Unknown Provider":
                                    break

                            # First cell is often the plan name
                            if len(cell_texts) > 0 and not any(p in cell_texts[0].lower() for p in ['plan', 'provider', 'rate', 'term']):
                                plan_name = cell_texts[0]

                            # If no plan name, construct one
                            if not plan_name:
                                plan_name = f"{provider_name} Commercial Plan"
                                if contract_months:
                                    plan_name += f" ({contract_months} months)"

                            # Only add if we have a rate
                            if rate:
                                # Check for duplicates before adding
                                is_duplicate = False
                                for existing_plan in plans:
                                    if (existing_plan['provider_name'] == provider_name and
                                        existing_plan['plan_name'] == plan_name and
                                        abs(existing_plan['rate_1000_cents'] - rate) < 0.01):
                                        is_duplicate = True
                                        break

                                if not is_duplicate:
                                    plans.append({
                                        "provider_name": provider_name,
                                        "plan_name": plan_name[:200],
                                        "plan_type": "Fixed",
                                        "service_type": "Commercial",
                                        "zip_code": zip_code,
                                        "contract_months": contract_months,
                                        "rate_1000_cents": round(rate, 3),
                                        "special_features": None,
                                        "last_updated": datetime.now(timezone.utc),
                                    })
                                    print(f"[ElectricityPlans] (Table) Found: {provider_name} - {plan_name} ({rate}¢)")

                        except Exception as e:
                            print(f"[ElectricityPlans] Error parsing table row: {e}")
                            continue

                except Exception as e:
                    print(f"[ElectricityPlans] Error processing table {table_idx}: {e}")
                    continue

        except PlaywrightTimeout:
            print("[ElectricityPlans] Timeout - site may be slow or down")
        except Exception as e:
            print(f"[ElectricityPlans] Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()

    print(f"[ElectricityPlans] Successfully scraped {len(plans)} commercial plans")
    return plans[:max_plans]


def scrape_electricityplans_all_texas() -> List[Dict]:
    """
    Scrape commercial plans from multiple Texas zip codes for broader coverage.

    Returns:
        Aggregated list of unique commercial plans from major Texas cities.
    """
    zip_codes = [
        "75001",  # Dallas
        "77001",  # Houston
        "78701",  # Austin
        "78201",  # San Antonio
        "76101",  # Fort Worth
    ]

    all_plans = []
    seen_plans = set()

    for zip_code in zip_codes:
        print(f"\n[ElectricityPlans] Scraping commercial plans for zip code: {zip_code}")
        plans = scrape_electricityplans_commercial(zip_code, max_plans=50)

        # Deduplicate by provider + plan name + rate
        for plan in plans:
            key = (plan['provider_name'], plan['plan_name'], plan.get('rate_1000_cents'))
            if key not in seen_plans:
                seen_plans.add(key)
                all_plans.append(plan)

    print(f"\n[ElectricityPlans] ==========================================")
    print(f"[ElectricityPlans] Total unique commercial plans: {len(all_plans)}")
    print(f"[ElectricityPlans] ==========================================")
    return all_plans


# For testing
if __name__ == "__main__":
    print("Testing ElectricityPlans commercial scraper...")
    print("=" * 60)

    plans = scrape_electricityplans_commercial(zip_code="75001", max_plans=50)

    print(f"\n{'=' * 60}")
    print(f"RESULTS: Scraped {len(plans)} commercial plans")
    print(f"{'=' * 60}\n")

    if plans:
        print("Sample plans:")
        for i, plan in enumerate(plans[:10], 1):
            print(f"\n{i}. {plan['provider_name']} - {plan['plan_name']}")
            print(f"   Rate: {plan['rate_1000_cents']} cents/kWh")
            print(f"   Contract: {plan['contract_months']} months" if plan['contract_months'] else "   Contract: N/A")
            print(f"   Type: {plan['plan_type']}")
    else:
        print("WARNING: No plans found - website structure may have changed")
        print("         Run with browser inspection to debug")
