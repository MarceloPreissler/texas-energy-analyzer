"""
Enhanced EnergyBot Commercial Scraper with Full Navigation Flow

This scraper combines the best of both approaches:
1. Comprehensive navigation through EnergyBot's business flow (from Selenium version)
2. Reliable JSON-LD extraction (from Playwright v2)
3. HTML parsing fallback for plan cards
4. Multi-ZIP code support with TDU tracking

Uses Playwright instead of Selenium for better performance and Railway compatibility.
"""
from __future__ import annotations

import json
import re
import time
from typing import List, Dict
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup


# Target ZIP codes with TDU information
ZIPCODES = [
    ("77539", "TNMP", "Dickinson"),
    ("75214", "ONCOR", "Dallas"),
    ("77379", "CENTERPOINT", "Spring"),
    ("78541", "AEP CENTRAL", "Edinburg"),
    ("79605", "AEP NORTH", "Abilene"),
]


def navigate_business_flow(page, zip_code: str) -> bool:
    """
    Navigate through EnergyBot's business electricity flow.

    Steps:
    1. Click Business tab
    2. Enter ZIP code
    3. Select "Yes - Power is on"
    4. Select "Same business name"
    5. Select bill range "I don't know"
    6. Select "Standard View"
    7. Select "As Soon As Possible" start date

    Returns:
        bool: True if navigation succeeded, False otherwise
    """
    try:
        # Step 1: Click Business tab
        print(f"[EnergyBot Enhanced] Clicking Business tab...")
        try:
            page.click("#bus-tab", timeout=5000)
        except:
            # Fallback selector
            page.click("a#bus-tab, a.eb-property-selector:has-text('Business')", timeout=5000)
        time.sleep(1.5)

        # Step 2: Enter ZIP code
        print(f"[EnergyBot Enhanced] Entering ZIP code: {zip_code}...")
        page.click("#eb-zip-code-input-field-handlebars", timeout=5000)
        time.sleep(0.2)
        page.fill("#eb-zip-code-input-field-handlebars", "")
        time.sleep(0.1)
        page.fill("#eb-zip-code-input-field-handlebars", zip_code)
        time.sleep(0.3)
        page.click("#eb-zip-code-submit-button-handlebars", timeout=5000)
        time.sleep(2.5)

        # Step 3: Select "Yes - Power is on"
        print(f"[EnergyBot Enhanced] Selecting 'Yes - Power is on'...")
        try:
            page.click("a.eb-app-choice-button:has-text('Yes')", timeout=5000)
        except:
            # Fallback
            page.click("a:has-text('Yes'), button:has-text('Yes')", timeout=5000)
        time.sleep(1.2)

        # Step 4: Select "Same business name"
        print(f"[EnergyBot Enhanced] Selecting 'Same business name'...")
        try:
            page.click("a.eb-app-choice-button:has-text('Same business name')", timeout=5000)
        except:
            page.click("a:has-text('Same business name'), button:has-text('Same business name')", timeout=5000)
        time.sleep(1.2)

        # Step 5: Bill range - "I don't know"
        print(f"[EnergyBot Enhanced] Selecting bill range...")
        try:
            page.select_option("select#bill-select-field", value="1", timeout=5000)
            time.sleep(0.4)
        except:
            print(f"[EnergyBot Enhanced] Bill select skipped (may not be required)")

        page.click("#eb-nav-button-next", timeout=5000)
        time.sleep(1.5)

        # Step 6: Select "Standard View"
        print(f"[EnergyBot Enhanced] Selecting 'Standard View'...")
        try:
            page.click("a.eb-app-choice-button:has-text('Standard View')", timeout=5000)
        except:
            page.click("a:has-text('Standard View'), button:has-text('Standard View')", timeout=5000)
        time.sleep(10)  # Longer wait for plan loading

        # Step 7: ASAP date + Continue
        print(f"[EnergyBot Enhanced] Selecting 'As Soon As Possible'...")
        try:
            page.click("#select-asap-date-radio-label, #select-asap-date-radio", timeout=5000)
        except:
            page.click("label:has-text('As Soon As Possible'), span:has-text('As Soon As Possible')", timeout=5000)
        time.sleep(0.6)

        page.click("#eb-nav-button-next", timeout=5000)
        time.sleep(2.0)

        print(f"[EnergyBot Enhanced] Navigation flow completed successfully")
        return True

    except Exception as e:
        print(f"[EnergyBot Enhanced] Navigation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def expand_all_plans(page, max_tries: int = 3) -> None:
    """
    Expand all plans by clicking "Show All Plans" button if present.
    """
    for attempt in range(max_tries):
        try:
            # Check if button exists
            show_all_button = page.query_selector("#eb-show-all-plans, a:has-text('Show All Plans')")
            if not show_all_button:
                print(f"[EnergyBot Enhanced] No 'Show All Plans' button found (all plans may be visible)")
                break

            # Click to expand
            print(f"[EnergyBot Enhanced] Clicking 'Show All Plans' (attempt {attempt + 1})...")
            page.click("#eb-show-all-plans, a:has-text('Show All Plans')", timeout=3000)
            time.sleep(1.2)

            # Scroll to load lazy content
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1.0)

        except Exception as e:
            if attempt == max_tries - 1:
                print(f"[EnergyBot Enhanced] Could not expand all plans: {e}")
            break


def extract_plans_from_json_ld(page) -> List[Dict]:
    """
    Extract plans from JSON-LD structured data (most reliable method).
    """
    plans = []

    try:
        # Get all JSON-LD scripts
        scripts = page.query_selector_all('script[type="application/ld+json"]')
        print(f"[EnergyBot Enhanced] Found {len(scripts)} JSON-LD scripts")

        for script in scripts:
            try:
                json_text = script.inner_text()
                data = json.loads(json_text)

                # Look for Product with offers
                if data.get('@type') == 'Product' and 'offers' in data:
                    aggregate_offers = data['offers']

                    if 'offers' in aggregate_offers:
                        offers = aggregate_offers['offers']
                        print(f"[EnergyBot Enhanced] Found {len(offers)} plans in JSON-LD")

                        for offer in offers:
                            try:
                                # Extract provider
                                provider_name = offer.get('offeredBy', {}).get('name', 'Unknown Provider')

                                # Extract plan details
                                price_spec = offer.get('priceSpecification', {})
                                raw_plan_name = price_spec.get('name', 'Unknown Plan')

                                # Clean plan name
                                plan_name = raw_plan_name.replace(provider_name, '').strip(' -')
                                if not plan_name or len(plan_name) < 3:
                                    term_match = re.search(r'(\d+)\s*month', raw_plan_name, re.IGNORECASE)
                                    plan_name = f"Commercial {term_match.group(0).title()}" if term_match else "Commercial Plan"

                                # Extract rate (convert dollars to cents)
                                price_dollars = price_spec.get('price', 0)
                                rate_cents = price_dollars * 100

                                # Extract contract term
                                contract_months = None
                                term_match = re.search(r'(\d+)\s*month', plan_name, re.IGNORECASE)
                                if term_match:
                                    contract_months = int(term_match.group(1))

                                # Determine plan type
                                plan_type = "Fixed"
                                if "variable" in plan_name.lower():
                                    plan_type = "Variable"
                                elif "solar" in plan_name.lower() or "green" in plan_name.lower():
                                    plan_type = "Solar"

                                plans.append({
                                    "provider_name": provider_name,
                                    "plan_name": plan_name,
                                    "rate_1000_cents": round(rate_cents, 3),
                                    "contract_months": contract_months,
                                    "plan_type": plan_type,
                                    "special_features": offer.get('description', None),
                                    "source": "json_ld"
                                })

                            except Exception as e:
                                print(f"[EnergyBot Enhanced] Error parsing JSON-LD offer: {e}")
                                continue

            except (json.JSONDecodeError, Exception) as e:
                continue

    except Exception as e:
        print(f"[EnergyBot Enhanced] Error extracting JSON-LD: {e}")

    return plans


def extract_plans_from_html(page) -> List[Dict]:
    """
    Extract plans from HTML plan cards (fallback method).
    """
    plans = []

    try:
        html_content = page.content()
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find plan cards by ID pattern
        cards = soup.select("div[id^='e-plan-card-']")

        # Fallback to class-based selection
        if not cards:
            cards = soup.select("div.eb-plan-card")

        print(f"[EnergyBot Enhanced] Found {len(cards)} plan cards in HTML")

        for idx, card in enumerate(cards):
            try:
                # Extract provider from logo alt text
                provider = "Unknown Provider"
                logo = card.select_one("img.eb-supplier-logo[alt]")
                if logo and logo.get("alt"):
                    provider = logo.get("alt", "").strip()

                # Extract contract months
                months = None
                label = card.select_one(".eb-label")
                if label:
                    month_match = re.search(r'(\d+)\s*(?:mo|month|mos)', label.get_text(" ", strip=True), re.IGNORECASE)
                    if month_match:
                        months = int(month_match.group(1))

                if not months:
                    # Try full card text
                    month_match = re.search(r'(\d+)\s*(?:mo|month|mos)', card.get_text(" ", strip=True), re.IGNORECASE)
                    if month_match:
                        months = int(month_match.group(1))

                # Extract rate
                rate = None
                rate_elem = card.select_one(".eb-plan-rate")
                if rate_elem:
                    rate_match = re.search(r'(\d+(?:\.\d+)?)\s*¢', rate_elem.get_text(" ", strip=True))
                    if rate_match:
                        rate = float(rate_match.group(1))

                if not rate:
                    # Try full card text
                    rate_match = re.search(r'(\d+(?:\.\d+)?)\s*¢', card.get_text(" ", strip=True))
                    if rate_match:
                        rate = float(rate_match.group(1))

                # Only add if we have essential data
                if rate and provider != "Unknown Provider":
                    plan_name = f"{months} Month Plan" if months else "Commercial Plan"

                    plans.append({
                        "provider_name": provider,
                        "plan_name": plan_name,
                        "rate_1000_cents": round(rate, 3),
                        "contract_months": months,
                        "plan_type": "Fixed",
                        "special_features": None,
                        "source": "html"
                    })

            except Exception as e:
                print(f"[EnergyBot Enhanced] Error parsing HTML card {idx}: {e}")
                continue

    except Exception as e:
        print(f"[EnergyBot Enhanced] Error extracting from HTML: {e}")

    return plans


def scrape_energybot_business_enhanced(zip_code: str = "75001", tdu: str = "ONCOR", city: str = "Dallas") -> List[Dict]:
    """
    Enhanced EnergyBot business scraper with full navigation flow.

    Args:
        zip_code: Texas ZIP code
        tdu: Transmission & Distribution Utility name
        city: City name

    Returns:
        List of plan dictionaries
    """
    plans = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        try:
            # Navigate to homepage
            url = "https://www.energybot.com/"
            print(f"[EnergyBot Enhanced] Navigating to {url}...")
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(2.0)

            # Navigate through business flow
            if not navigate_business_flow(page, zip_code):
                print(f"[EnergyBot Enhanced] Navigation failed for ZIP {zip_code}")
                return []

            # Expand all plans
            expand_all_plans(page)

            # Scroll to ensure all content is loaded
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1.0)

            # Extract plans using JSON-LD (primary method)
            plans = extract_plans_from_json_ld(page)

            # If JSON-LD fails, fall back to HTML parsing
            if not plans:
                print(f"[EnergyBot Enhanced] JSON-LD extraction failed, trying HTML parsing...")
                plans = extract_plans_from_html(page)

            # Add metadata to all plans
            for plan in plans:
                plan.update({
                    "service_type": "Commercial",
                    "zip_code": zip_code,
                    "tdu": tdu,
                    "city": city,
                    "last_updated": datetime.now(timezone.utc),
                })

            print(f"[EnergyBot Enhanced] Successfully scraped {len(plans)} plans for {city} ({zip_code})")

        except PlaywrightTimeout:
            print(f"[EnergyBot Enhanced] Timeout for ZIP {zip_code}")
        except Exception as e:
            print(f"[EnergyBot Enhanced] Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()

    return plans


def scrape_energybot_all_texas_enhanced() -> List[Dict]:
    """
    Scrape EnergyBot business plans for all major Texas cities.

    Returns:
        Aggregated list of unique plans from multiple TDUs
    """
    all_plans = []
    seen_plans = set()

    print(f"[EnergyBot Enhanced] Starting scrape for {len(ZIPCODES)} ZIP codes...")

    for zip_code, tdu, city in ZIPCODES:
        print(f"\n[EnergyBot Enhanced] {'='*60}")
        print(f"[EnergyBot Enhanced] Processing {city} - {zip_code} ({tdu})")
        print(f"[EnergyBot Enhanced] {'='*60}\n")

        plans = scrape_energybot_business_enhanced(zip_code, tdu, city)

        # Deduplicate by provider + plan name + rate
        for plan in plans:
            key = (plan['provider_name'], plan['plan_name'], plan.get('rate_1000_cents'))
            if key not in seen_plans:
                seen_plans.add(key)
                all_plans.append(plan)

        # Small delay between ZIP codes to avoid rate limiting
        time.sleep(2.0)

    print(f"\n[EnergyBot Enhanced] Total unique plans: {len(all_plans)}")
    return all_plans


# For testing
if __name__ == "__main__":
    print("Testing Enhanced EnergyBot Business Scraper...")
    print("="*60)

    # Test single ZIP
    plans = scrape_energybot_business_enhanced("75214", "ONCOR", "Dallas")

    print(f"\nScraped {len(plans)} plans:")
    for i, plan in enumerate(plans, 1):
        print(f"\n{i}. {plan['provider_name']} - {plan['plan_name']}")
        print(f"   Rate: {plan['rate_1000_cents']}¢/kWh")
        print(f"   Contract: {plan['contract_months']} months")
        print(f"   Type: {plan['plan_type']}")
        print(f"   TDU: {plan['tdu']}")
        print(f"   Source: {plan.get('source', 'unknown')}")

    # Uncomment to test all ZIPs:
    # all_plans = scrape_energybot_all_texas_enhanced()
