"""
Reliant Energy small business/commercial plan scraper.

Scrapes commercial electricity plans from Reliant's business site.
"""
from __future__ import annotations

import re
from typing import List, Dict
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


def scrape_reliant_commercial(zip_code: str = "75001", max_plans: int = 50) -> List[Dict]:
    """
    Scrape Reliant's small business commercial plans.

    Args:
        zip_code: Texas zip code
        max_plans: Maximum number of plans to scrape

    Returns:
        List of plan dictionaries
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
            # Try the shop page for business
            url = "https://shop.reliant.com/business"
            print(f"[Reliant Business] Navigating to {url}...")

            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)

            # Try to enter ZIP code if there's an input
            try:
                zip_input = page.query_selector('input[name*="zip"], input[placeholder*="ZIP"], input[type="text"]')
                if zip_input and zip_input.is_visible():
                    print(f"[Reliant Business] Entering ZIP code: {zip_code}")
                    zip_input.fill(zip_code)
                    page.wait_for_timeout(1000)

                    # Look for and click submit/search button
                    submit_selectors = [
                        'button[type="submit"]',
                        'button:has-text("Shop")',
                        'button:has-text("Search")',
                        'button:has-text("Continue")',
                        'input[type="submit"]'
                    ]

                    for selector in submit_selectors:
                        try:
                            btn = page.query_selector(selector)
                            if btn and btn.is_visible():
                                print(f"[Reliant Business] Clicking: {selector}")
                                btn.click()
                                page.wait_for_timeout(3000)
                                break
                        except:
                            continue
            except Exception as e:
                print(f"[Reliant Business] ZIP entry failed: {e}, continuing...")

            # Look for plan cards/elements
            print(f"[Reliant Business] Looking for plan data...")

            # Try multiple selectors for plan cards
            plan_selectors = [
                '[class*="plan"]',
                '[class*="card"]',
                '[class*="product"]',
                'article',
                '.plan-tile',
                '.product-card'
            ]

            plan_elements = []
            for selector in plan_selectors:
                elements = page.query_selector_all(selector)
                if elements and len(elements) > 2:
                    plan_elements = elements
                    print(f"[Reliant Business] Found {len(elements)} potential plans with: {selector}")
                    break

            if not plan_elements:
                print("[Reliant Business] No plan elements found")
                # Save HTML for inspection
                html = page.content()
                with open('reliant_business_debug.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                print("[Reliant Business] Saved HTML to reliant_business_debug.html")
                return plans

            # Parse each plan
            for idx, element in enumerate(plan_elements[:max_plans]):
                try:
                    text = element.inner_text()

                    # Look for plan name (usually in heading)
                    plan_lines = [line.strip() for line in text.split('\n') if line.strip()]
                    plan_name = plan_lines[0] if plan_lines else "Unknown Plan"

                    # Look for Reliant-specific plan names
                    if 'reliant' not in plan_name.lower():
                        # Check if any line contains known Reliant plan names
                        for line in plan_lines:
                            if any(name in line.lower() for name in ['flextra', 'secure', 'advantage', 'apartment', 'power plus']):
                                plan_name = line
                                break

                    # Look for rate (cents per kWh)
                    rate = None
                    rate_patterns = [
                        r'(\d+\.?\d*)\s*¢\s*(?:per\s*)?(?:kWh)?',
                        r'(\d+\.?\d*)\s*cents?\s*(?:per\s*)?(?:kWh)?',
                        r'(\d+\.?\d*)\s*¢/kWh',
                    ]

                    for pattern in rate_patterns:
                        rate_match = re.search(pattern, text, re.IGNORECASE)
                        if rate_match:
                            rate = float(rate_match.group(1))
                            break

                    # Look for contract term
                    contract_months = None
                    term_match = re.search(r'(\d+)\s*(?:mo|month|mos)', text, re.IGNORECASE)
                    if term_match:
                        contract_months = int(term_match.group(1))

                    # Determine plan type
                    plan_type = "Fixed"
                    if "variable" in text.lower():
                        plan_type = "Variable"
                    elif "solar" in text.lower() or "100%" in text:
                        plan_type = "Solar"

                    # Only add if we have meaningful data
                    if rate and "Unknown" not in plan_name:
                        plans.append({
                            "provider_name": "Reliant Energy",
                            "plan_name": plan_name[:200],
                            "plan_type": plan_type,
                            "service_type": "Commercial",
                            "zip_code": zip_code,
                            "contract_months": contract_months,
                            "rate_1000_cents": round(rate, 3),
                            "special_features": None,
                            "last_updated": datetime.utcnow(),
                        })
                        print(f"[Reliant Business] Found plan: {plan_name} - {rate}¢/kWh")

                except Exception as e:
                    print(f"[Reliant Business] Error parsing plan {idx}: {e}")
                    continue

        except PlaywrightTimeout:
            print("[Reliant Business] Timeout - site may be slow or blocking")
        except Exception as e:
            print(f"[Reliant Business] Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()

    print(f"[Reliant Business] Successfully scraped {len(plans)} commercial plans")
    return plans


# For testing
if __name__ == "__main__":
    print("Testing Reliant Business scraper...")
    plans = scrape_reliant_commercial()

    print(f"\nScraped {len(plans)} plans:")
    for i, plan in enumerate(plans, 1):
        print(f"\n{i}. {plan['plan_name']}")
        print(f"   Rate: {plan['rate_1000_cents']}¢/kWh")
        print(f"   Contract: {plan['contract_months']} months")
        print(f"   Type: {plan['plan_type']}")
