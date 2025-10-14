"""
EnergyBot.com scraper for Texas commercial electricity plans.

This scraper fetches commercial plan data from EnergyBot, which has
better commercial plan coverage than PowerToChoose.org.
"""
from __future__ import annotations

import re
from typing import List, Dict
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


def scrape_energybot_commercial(zip_code: str = "75001", max_plans: int = 100) -> List[Dict]:
    """
    Scrape commercial electricity plans from EnergyBot.com.

    Args:
        zip_code: Texas zip code to search
        max_plans: Maximum number of plans to scrape

    Returns:
        List of plan dictionaries with provider_name, plan_name, rate, etc.
    """
    plans: List[Dict] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        try:
            url = "https://www.energybot.com/electricity-rates/texas/business-commercial-electricity.html"
            print(f"[EnergyBot] Navigating to {url}...")

            # Try with longer timeout and load event instead of networkidle
            page.goto(url, wait_until="load", timeout=45000)
            print("[EnergyBot] Page loaded")

            # Wait for dynamic content
            page.wait_for_timeout(5000)

            # Try to find zip code input and enter it
            try:
                zip_input = page.query_selector('input[name*="zip"], input[placeholder*="ZIP"], input[type="text"]')
                if zip_input:
                    print(f"[EnergyBot] Entering zip code: {zip_code}")
                    zip_input.fill(zip_code)

                    # Look for search/submit button
                    submit_btn = page.query_selector('button[type="submit"], button:has-text("Search"), button:has-text("Compare")')
                    if submit_btn:
                        submit_btn.click()
                        page.wait_for_timeout(3000)
            except Exception as e:
                print(f"[EnergyBot] Could not enter zip code: {e}")

            # Try multiple strategies to find plan elements
            plan_elements = []

            selectors = [
                'article',
                '.plan-card',
                '.rate-card',
                '[class*="plan"]',
                'table tbody tr',
                'div[data-plan]',
            ]

            for selector in selectors:
                elements = page.query_selector_all(selector)
                if elements and len(elements) > 2:  # At least a few elements
                    plan_elements = elements
                    print(f"[EnergyBot] Found {len(plan_elements)} plan elements with selector: {selector}")
                    break

            if not plan_elements:
                # Fallback: get all visible text and try to parse it
                html = page.content()
                print(f"[EnergyBot] No plan elements found via selectors, trying text parsing")

                # Save HTML for debugging
                with open('energybot_debug.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                print("[EnergyBot] Saved page HTML to energybot_debug.html for inspection")

            # Parse each plan element
            for idx, element in enumerate(plan_elements[:max_plans]):
                try:
                    text = element.inner_text()

                    # Look for provider name (usually capitalized or in header)
                    provider_match = re.search(r'([A-Z][A-Za-z\s&]+(?:Energy|Electric|Power))', text)
                    provider_name = provider_match.group(1).strip() if provider_match else "Unknown Provider"

                    # Look for plan name
                    plan_lines = [line.strip() for line in text.split('\n') if line.strip()]
                    plan_name = plan_lines[0] if plan_lines else "Unknown Plan"

                    # Look for rate (cents per kWh)
                    rate_match = re.search(r'(\d+\.?\d*)\s*[¢c]\s*(?:per\s*)?(?:kWh)?', text, re.IGNORECASE)
                    rate = None
                    if rate_match:
                        rate = float(rate_match.group(1))

                    # Look for contract term
                    term_match = re.search(r'(\d+)\s*(?:mo|month|mos)', text, re.IGNORECASE)
                    contract_months = int(term_match.group(1)) if term_match else None

                    # Determine plan type
                    plan_type = "Fixed"
                    if "variable" in text.lower():
                        plan_type = "Variable"
                    elif "solar" in text.lower() or "renewable" in text.lower():
                        plan_type = "Solar"

                    # Only add if we have meaningful data
                    if rate and provider_name != "Unknown Provider":
                        plans.append({
                            "provider_name": provider_name,
                            "plan_name": plan_name[:200],
                            "plan_type": plan_type,
                            "service_type": "Commercial",
                            "zip_code": zip_code,
                            "contract_months": contract_months,
                            "rate_1000_cents": rate,
                            "special_features": None,
                            "last_updated": datetime.utcnow(),
                        })

                except Exception as e:
                    print(f"[EnergyBot] Error parsing plan {idx}: {e}")
                    continue

        except PlaywrightTimeout:
            print("[EnergyBot] Timeout - site may be slow or blocking automated access")
        except Exception as e:
            print(f"[EnergyBot] Error: {e}")
        finally:
            browser.close()

    print(f"[EnergyBot] Successfully scraped {len(plans)} commercial plans")
    return plans


def scrape_energybot_all_texas() -> List[Dict]:
    """
    Scrape commercial plans from multiple Texas zip codes.

    Returns:
        Aggregated list of unique commercial plans.
    """
    zip_codes = [
        "75001",  # Dallas
        "77001",  # Houston
        "78701",  # Austin
    ]

    all_plans = []
    seen_plans = set()

    for zip_code in zip_codes:
        print(f"[EnergyBot] Scraping Commercial plans for zip code: {zip_code}")
        plans = scrape_energybot_commercial(zip_code, max_plans=50)

        # Deduplicate
        for plan in plans:
            key = (plan['provider_name'], plan['plan_name'], plan.get('rate_1000_cents'))
            if key not in seen_plans:
                seen_plans.add(key)
                all_plans.append(plan)

    print(f"[EnergyBot] Total unique Commercial plans: {len(all_plans)}")
    return all_plans
