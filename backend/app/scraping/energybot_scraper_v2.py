"""
EnergyBot.com scraper v2 - Uses JSON-LD structured data.

This version extracts plan data from the JSON-LD structured data
embedded in the page, which is more reliable than HTML parsing.
"""
from __future__ import annotations

import json
import re
from typing import List, Dict
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


def scrape_energybot_commercial_v2(zip_code: str = "75001", max_plans: int = 100) -> List[Dict]:
    """
    Scrape commercial electricity plans from EnergyBot.com using JSON-LD data.

    Args:
        zip_code: Texas zip code (not used yet, but kept for future)
        max_plans: Maximum number of plans to scrape

    Returns:
        List of plan dictionaries with provider_name, plan_name, rate, etc.
    """
    plans: List[Dict] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()

        try:
            url = "https://www.energybot.com/electricity-rates/texas/business-commercial-electricity.html"
            print(f"[EnergyBot v2] Navigating to {url}...")

            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)  # Wait for dynamic content

            # Try to load more plans by scrolling
            print("[EnergyBot v2] Scrolling to load more plans...")
            for _ in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1500)

            # Try clicking "Show More" or "Load More" button if it exists
            try:
                show_more_selectors = [
                    'button:has-text("Show More")',
                    'button:has-text("Load More")',
                    'a:has-text("Show More")',
                    '.show-more',
                    '.load-more'
                ]
                for selector in show_more_selectors:
                    button = page.query_selector(selector)
                    if button and button.is_visible():
                        print(f"[EnergyBot v2] Clicking: {selector}")
                        button.click()
                        page.wait_for_timeout(2000)
                        break
            except Exception as e:
                print(f"[EnergyBot v2] No load more button found: {e}")

            print("[EnergyBot v2] Page loaded, extracting JSON-LD data...")

            # Get all JSON-LD scripts
            scripts = page.query_selector_all('script[type="application/ld+json"]')
            print(f"[EnergyBot v2] Found {len(scripts)} JSON-LD scripts")

            for script in scripts:
                try:
                    json_text = script.inner_text()
                    data = json.loads(json_text)

                    # Look for Product with offers (this is where plan data is)
                    if data.get('@type') == 'Product' and 'offers' in data:
                        aggregate_offers = data['offers']

                        if 'offers' in aggregate_offers:
                            offers = aggregate_offers['offers']
                            print(f"[EnergyBot v2] Found {len(offers)} plans in structured data")

                            for offer in offers:
                                try:
                                    # Extract provider name
                                    provider_name = offer.get('offeredBy', {}).get('name', 'Unknown Provider')

                                    # Extract plan details from priceSpecification
                                    price_spec = offer.get('priceSpecification', {})
                                    raw_plan_name = price_spec.get('name', 'Unknown Plan')

                                    # Clean up plan name - format is often "Provider - Provider - Term"
                                    # Remove all occurrences of provider name
                                    plan_name = raw_plan_name
                                    if provider_name:
                                        # Replace all occurrences of provider name with empty string
                                        plan_name = plan_name.replace(provider_name, '')
                                        # Clean up multiple dashes/spaces
                                        plan_name = re.sub(r'\s*-\s*-\s*', ' - ', plan_name)
                                        plan_name = plan_name.strip(' -')

                                    # If we removed too much, create a descriptive name
                                    if not plan_name or len(plan_name) < 3:
                                        term_match = re.search(r'(\d+)\s*month', raw_plan_name, re.IGNORECASE)
                                        if term_match:
                                            plan_name = f"Commercial {term_match.group(0).title()}"
                                        else:
                                            plan_name = "Commercial Plan"

                                    # Price is in dollars per kWh, convert to cents
                                    price_dollars = price_spec.get('price', 0)
                                    rate_cents = price_dollars * 100

                                    # Extract contract term from plan name
                                    contract_months = None
                                    term_match = re.search(r'(\d+)\s*month', plan_name, re.IGNORECASE)
                                    if term_match:
                                        contract_months = int(term_match.group(1))

                                    # Determine plan type (assume Fixed unless variable detected)
                                    plan_type = "Fixed"
                                    if "variable" in plan_name.lower():
                                        plan_type = "Variable"
                                    elif "solar" in plan_name.lower() or "green" in plan_name.lower():
                                        plan_type = "Solar"

                                    # Extract special features from description if available
                                    special_features = offer.get('description', None)
                                    if special_features and len(special_features) > 200:
                                        special_features = special_features[:200] + '...'

                                    plans.append({
                                        "provider_name": provider_name,
                                        "plan_name": plan_name,
                                        "plan_type": plan_type,
                                        "service_type": "Commercial",
                                        "zip_code": zip_code,
                                        "contract_months": contract_months,
                                        "rate_1000_cents": round(rate_cents, 3),
                                        "special_features": special_features,
                                        "last_updated": datetime.now(timezone.utc),
                                    })

                                except Exception as e:
                                    print(f"[EnergyBot v2] Error parsing offer: {e}")
                                    continue

                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"[EnergyBot v2] Error processing script: {e}")
                    continue

        except PlaywrightTimeout:
            print("[EnergyBot v2] Timeout - site may be slow or down")
        except Exception as e:
            print(f"[EnergyBot v2] Error: {e}")
        finally:
            browser.close()

    print(f"[EnergyBot v2] Successfully scraped {len(plans)} commercial plans")
    return plans[:max_plans]


def scrape_energybot_all_texas_v2() -> List[Dict]:
    """
    Scrape commercial plans for Texas.

    Returns:
        List of unique commercial plans.
    """
    print("[EnergyBot v2] Scraping Texas commercial plans")
    plans = scrape_energybot_commercial_v2(zip_code="75001", max_plans=50)

    print(f"[EnergyBot v2] Total commercial plans: {len(plans)}")
    return plans


# For testing
if __name__ == "__main__":
    print("Testing EnergyBot v2 scraper...")
    plans = scrape_energybot_commercial_v2()

    print(f"\nScraped {len(plans)} plans:")
    for i, plan in enumerate(plans, 1):
        print(f"\n{i}. {plan['provider_name']} - {plan['plan_name']}")
        print(f"   Rate: {plan['rate_1000_cents']}¢/kWh")
        print(f"   Contract: {plan['contract_months']} months")
        print(f"   Type: {plan['plan_type']}")
