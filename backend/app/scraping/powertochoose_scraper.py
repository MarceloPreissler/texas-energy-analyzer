"""
Live PowerToChoose.org scraper using Playwright for real-time pricing data.

This scraper uses browser automation to fetch current electricity plans
directly from the official PUCT website, ensuring data is always up-to-date.
"""
from __future__ import annotations

import re
from typing import List, Dict
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


def scrape_powertochoose(zip_code: str = "75001", service_type: str = "Residential", max_plans: int = 100) -> List[Dict]:
    """
    Scrape live electricity plan data from PowerToChoose.org using Playwright.

    Args:
        zip_code: Texas zip code to search (default: 75001 - Dallas)
        service_type: "Residential" or "Commercial" (default: Residential)
        max_plans: Maximum number of plans to scrape (default: 100)

    Returns:
        List of plan dictionaries with provider_name, plan_name, rate, etc.
    """
    plans: List[Dict] = []

    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()

        try:
            print(f"[PowerToChoose] Navigating to site...")
            page.goto("https://www.powertochoose.org/", wait_until="networkidle", timeout=30000)

            # Accept cookies if present
            try:
                page.click('button:has-text("Accept")', timeout=2000)
            except:
                pass

            # Select service type (Residential or Commercial)
            try:
                if service_type == "Commercial":
                    print(f"[PowerToChoose] Selecting Commercial service type...")
                    # Try multiple selectors for Commercial
                    selectors = [
                        'input[value="Commercial"]',
                        'input#commercial',
                        'label:has-text("Commercial")',
                        'radio:has-text("Commercial")',
                        '[for="commercial"]',
                    ]
                    clicked = False
                    for selector in selectors:
                        try:
                            page.click(selector, timeout=2000)
                            clicked = True
                            print(f"[PowerToChoose] Successfully selected Commercial")
                            break
                        except:
                            continue
                    if not clicked:
                        print(f"[PowerToChoose] Could not find Commercial selector, using default")
            except Exception as e:
                print(f"[PowerToChoose] Error selecting Commercial: {e}")

            # Enter zip code
            print(f"[PowerToChoose] Entering zip code: {zip_code}")
            page.fill('input[name="zip_code"]', zip_code)

            # Click search button
            page.click('button[type="submit"]:has-text("Shop")', timeout=5000)

            # Wait for results to load
            print(f"[PowerToChoose] Waiting for results...")
            page.wait_for_selector('.plan-details, .plan-result, table tr', timeout=15000)

            # Give extra time for dynamic content
            page.wait_for_timeout(2000)

            # Try multiple selector strategies
            plan_rows = page.query_selector_all('table.table tbody tr')

            if not plan_rows:
                plan_rows = page.query_selector_all('.plan-result, .plan-card')

            print(f"[PowerToChoose] Found {len(plan_rows)} plans")

            for idx, row in enumerate(plan_rows[:max_plans]):
                try:
                    # Extract text content
                    text = row.inner_text()

                    # Parse provider name (usually first or in bold)
                    provider_match = re.search(r'^([A-Za-z\s&]+)', text)
                    provider_name = provider_match.group(1).strip() if provider_match else "Unknown"

                    # Parse plan name (usually after provider)
                    plan_lines = text.split('\n')
                    plan_name = plan_lines[1] if len(plan_lines) > 1 else plan_lines[0]

                    # Parse rate (look for patterns like "10.5¢", "10.5 cents", "0.105")
                    rate_match = re.search(r'(\d+\.?\d*)\s*[¢c]|(\d+\.\d+)\s+cents?', text, re.IGNORECASE)
                    rate = None
                    if rate_match:
                        rate = float(rate_match.group(1) or rate_match.group(2))
                        # If rate is like 0.105, convert to cents
                        if rate < 1:
                            rate = rate * 100

                    # Parse contract term
                    term_match = re.search(r'(\d+)\s*(?:mo|month|mos)', text, re.IGNORECASE)
                    contract_months = int(term_match.group(1)) if term_match else None

                    # Determine plan type
                    plan_type = "Fixed"
                    if "variable" in text.lower():
                        plan_type = "Variable"
                    elif "solar" in text.lower() or "renewable" in text.lower():
                        plan_type = "Solar"
                    elif "free nights" in text.lower() or "free weekends" in text.lower():
                        plan_type = "Free Nights/Weekends"

                    # Only add if we have at least provider and rate
                    if provider_name != "Unknown" and rate:
                        plans.append({
                            "provider_name": provider_name,
                            "plan_name": plan_name[:200],  # Limit length
                            "plan_type": plan_type,
                            "service_type": service_type,  # Store service type
                            "zip_code": zip_code,  # Store zip code
                            "contract_months": contract_months,
                            "rate_1000_cents": rate,
                            "special_features": None,
                            "last_updated": datetime.utcnow(),
                        })

                except Exception as e:
                    print(f"[PowerToChoose] Error parsing row {idx}: {e}")
                    continue

        except PlaywrightTimeout:
            print("[PowerToChoose] Timeout - site may be slow or down")
        except Exception as e:
            print(f"[PowerToChoose] Error: {e}")
        finally:
            browser.close()

    print(f"[PowerToChoose] Successfully scraped {len(plans)} plans")
    return plans


def scrape_powertochoose_all_texas(service_type: str = "Residential") -> List[Dict]:
    """
    Scrape plans from multiple Texas zip codes to get broader coverage.

    Args:
        service_type: "Residential" or "Commercial" (default: Residential)

    Returns:
        Aggregated list of unique plans from major Texas cities.
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
        print(f"[PowerToChoose] Scraping {service_type} plans for zip code: {zip_code}")
        plans = scrape_powertochoose(zip_code, service_type=service_type, max_plans=50)

        # Deduplicate by provider + plan name + rate + service_type
        for plan in plans:
            key = (plan['provider_name'], plan['plan_name'], plan.get('rate_1000_cents'), plan.get('service_type'))
            if key not in seen_plans:
                seen_plans.add(key)
                all_plans.append(plan)

    print(f"[PowerToChoose] Total unique {service_type} plans: {len(all_plans)}")
    return all_plans
