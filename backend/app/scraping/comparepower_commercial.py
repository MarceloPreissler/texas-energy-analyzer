"""
ComparePower.com commercial electricity plan scraper using Playwright.

Scrapes business/commercial electricity plans from ComparePower.com,
which aggregates plans from 30+ Texas providers.
Uses playwright-stealth to bypass bot detection.
"""
from __future__ import annotations

import re
from typing import List, Dict
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from playwright_stealth.stealth import Stealth


def scrape_comparepower_commercial(zip_code: str = "75001", max_plans: int = 100) -> List[Dict]:
    """
    Scrape commercial electricity plans from ComparePower.com using Playwright.

    Args:
        zip_code: Texas zip code to search (default: 75001 - Dallas)
        max_plans: Maximum number of plans to scrape (default: 100)

    Returns:
        List of plan dictionaries with provider_name, plan_name, rate, etc.
    """
    plans: List[Dict] = []

    with sync_playwright() as p:
        # Launch browser in headless mode
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
        Stealth().apply_stealth_sync(page)
        print("[ComparePower] Stealth mode activated - bypassing bot detection")

        try:
            url = "https://comparepower.com/electricity-rates/texas/business-commercial-electricity/"
            print(f"[ComparePower] Navigating to {url}...")

            page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Accept cookies if present
            try:
                cookie_selectors = [
                    'button:has-text("Accept")',
                    'button:has-text("I Accept")',
                    'button:has-text("OK")',
                    '.cookie-accept',
                    '#cookie-accept'
                ]
                for selector in cookie_selectors:
                    try:
                        page.click(selector, timeout=2000)
                        print("[ComparePower] Accepted cookies")
                        break
                    except:
                        continue
            except:
                pass

            # Look for zip code input and enter it if found
            try:
                zip_selectors = [
                    'input[name="zip"]',
                    'input[placeholder*="zip" i]',
                    'input[type="text"][name*="zip" i]',
                    '#zip-code',
                    '#zipcode'
                ]

                zip_entered = False
                for selector in zip_selectors:
                    try:
                        if page.query_selector(selector):
                            print(f"[ComparePower] Entering zip code: {zip_code}")
                            page.fill(selector, zip_code)

                            # Try to click submit/search button
                            submit_selectors = [
                                'button[type="submit"]',
                                'button:has-text("Search")',
                                'button:has-text("Compare")',
                                'input[type="submit"]'
                            ]
                            for submit_selector in submit_selectors:
                                try:
                                    page.click(submit_selector, timeout=2000)
                                    print("[ComparePower] Clicked search button")
                                    break
                                except:
                                    continue

                            zip_entered = True
                            break
                    except:
                        continue

                if zip_entered:
                    # Wait for results to load after zip code submission
                    page.wait_for_timeout(3000)
            except Exception as e:
                print(f"[ComparePower] No zip code input found or error: {e}")

            # Scroll to load dynamic content
            print("[ComparePower] Scrolling to load all plans...")
            for i in range(5):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1500)

            # Try clicking "Load More" or "Show More" buttons
            try:
                load_more_selectors = [
                    'button:has-text("Load More")',
                    'button:has-text("Show More")',
                    'a:has-text("Load More")',
                    '.load-more',
                    '.show-more',
                    '#load-more'
                ]
                for selector in load_more_selectors:
                    try:
                        button = page.query_selector(selector)
                        if button and button.is_visible():
                            print(f"[ComparePower] Clicking load more button")
                            button.click()
                            page.wait_for_timeout(2000)
                    except:
                        continue
            except Exception as e:
                print(f"[ComparePower] No load more button: {e}")

            print("[ComparePower] Searching for plan elements...")

            # Try multiple selector strategies to find plan cards/rows
            plan_elements = []
            selectors = [
                '.plan-card',
                '.plan-result',
                '.plan-item',
                '.electricity-plan',
                '.rate-card',
                'table.plans tbody tr',
                'table.rates tbody tr',
                '[class*="plan"]',
                '[class*="rate-card"]',
                'article',
                '.wp-block-kadence-rowlayout',  # Kadence theme blocks
                '[data-plan-id]',
                '[data-provider]'
            ]

            for selector in selectors:
                elements = page.query_selector_all(selector)
                if len(elements) > 5:  # Only consider if we found a reasonable number
                    print(f"[ComparePower] Found {len(elements)} elements with selector: {selector}")
                    plan_elements = elements
                    break

            if not plan_elements:
                # Fallback: get all visible text and try to parse
                print("[ComparePower] No plan elements found, trying text extraction...")
                page_text = page.inner_text('body')
                print(f"[ComparePower] Page text length: {len(page_text)} characters")

                # Look for patterns that indicate plans in the text
                # This is a fallback and might not work well, but worth trying
                lines = page_text.split('\n')
                for line in lines[:50]:  # Debug: print first 50 lines
                    if any(keyword in line.lower() for keyword in ['kwh', 'cents', 'month', 'plan', 'rate']):
                        print(f"[ComparePower DEBUG] {line[:100]}")

            print(f"[ComparePower] Processing {len(plan_elements)} plan elements...")

            for idx, element in enumerate(plan_elements[:max_plans]):
                try:
                    # Extract all text from the element
                    text = element.inner_text()

                    # Skip if too short (probably not a plan)
                    if len(text) < 20:
                        continue

                    # Parse provider name (look for common Texas providers)
                    provider_patterns = [
                        r'(TXU Energy|Reliant|Direct Energy|Gexa|Green Mountain|Champion|Cirro|Frontier|Ambit|TriEagle|Pulse|4Change|Discount Power|Octopus|First Choice)',
                        r'^([A-Z][A-Za-z\s&]+?)\s*[-:]',  # Provider at start followed by dash/colon
                        r'Provider:\s*([A-Za-z\s&]+)',
                    ]

                    provider_name = "Unknown Provider"
                    for pattern in provider_patterns:
                        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                        if match:
                            provider_name = match.group(1).strip()
                            break

                    # Parse plan name
                    plan_lines = text.split('\n')
                    plan_name = None

                    # Look for a line that looks like a plan name (not too short, not a provider name)
                    for line in plan_lines:
                        line = line.strip()
                        if (len(line) > 5 and
                            len(line) < 150 and
                            line != provider_name and
                            not re.match(r'^\d+\.?\d*\s*[¢c]', line) and  # Not just a rate
                            not line.lower().startswith('contract:')):
                            plan_name = line
                            break

                    if not plan_name:
                        # Fallback: use provider name + "Commercial Plan"
                        plan_name = f"{provider_name} Commercial Plan"

                    # Parse rate (look for patterns like "10.5¢", "10.5 cents", "$0.105")
                    rate = None
                    rate_patterns = [
                        r'(\d+\.?\d*)\s*¢',  # 10.5¢
                        r'(\d+\.?\d*)\s*cents?',  # 10.5 cents
                        r'\$0\.(\d+)',  # $0.105
                        r'Rate:\s*(\d+\.?\d*)',  # Rate: 10.5
                    ]

                    for pattern in rate_patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            if pattern == r'\$0\.(\d+)':
                                # Convert from decimal to cents (0.105 -> 10.5)
                                rate = float(match.group(1)) / 10
                            else:
                                rate = float(match.group(1))

                            # Ensure rate is in reasonable range (5-20 cents)
                            if rate < 1:
                                rate = rate * 100

                            if 5 <= rate <= 20:
                                break
                            else:
                                rate = None

                    # Skip if no rate found (probably not a valid plan)
                    if not rate:
                        continue

                    # Parse contract term
                    contract_months = None
                    term_patterns = [
                        r'(\d+)\s*(?:month|mo|mos)',
                        r'Contract:\s*(\d+)',
                        r'Term:\s*(\d+)',
                    ]

                    for pattern in term_patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            contract_months = int(match.group(1))
                            # Ensure reasonable term (1-36 months)
                            if 1 <= contract_months <= 36:
                                break
                            else:
                                contract_months = None

                    # Determine plan type
                    plan_type = "Fixed"
                    text_lower = text.lower()
                    if "variable" in text_lower:
                        plan_type = "Variable"
                    elif any(word in text_lower for word in ["solar", "renewable", "green", "wind"]):
                        plan_type = "Solar"
                    elif any(word in text_lower for word in ["free nights", "free weekends", "time of use"]):
                        plan_type = "Free Nights/Weekends"

                    # Add to plans list
                    plans.append({
                        "provider_name": provider_name,
                        "plan_name": plan_name[:200],  # Limit length
                        "plan_type": plan_type,
                        "service_type": "Commercial",
                        "zip_code": zip_code,
                        "contract_months": contract_months,
                        "rate_1000_cents": round(rate, 3),
                        "special_features": None,
                        "last_updated": datetime.now(timezone.utc),
                    })

                    print(f"[ComparePower] ✓ Scraped: {provider_name} - {plan_name} ({rate}¢/kWh)")

                except Exception as e:
                    print(f"[ComparePower] Error parsing element {idx}: {e}")
                    continue

        except PlaywrightTimeout:
            print("[ComparePower] Timeout - site may be slow or down")
        except Exception as e:
            print(f"[ComparePower] Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()

    print(f"[ComparePower] Successfully scraped {len(plans)} commercial plans")
    return plans


def scrape_comparepower_all_texas() -> List[Dict]:
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
        print(f"\n[ComparePower] Scraping commercial plans for zip code: {zip_code}")
        plans = scrape_comparepower_commercial(zip_code, max_plans=50)

        # Deduplicate by provider + plan name + rate
        for plan in plans:
            key = (plan['provider_name'], plan['plan_name'], plan.get('rate_1000_cents'))
            if key not in seen_plans:
                seen_plans.add(key)
                all_plans.append(plan)

    print(f"\n[ComparePower] ==========================================")
    print(f"[ComparePower] Total unique commercial plans: {len(all_plans)}")
    print(f"[ComparePower] ==========================================")
    return all_plans


# For testing
if __name__ == "__main__":
    print("Testing ComparePower commercial scraper...")
    print("=" * 60)

    plans = scrape_comparepower_commercial(zip_code="75001", max_plans=50)

    print(f"\n{'=' * 60}")
    print(f"RESULTS: Scraped {len(plans)} commercial plans")
    print(f"{'=' * 60}\n")

    if plans:
        print("Sample plans:")
        for i, plan in enumerate(plans[:5], 1):
            print(f"\n{i}. {plan['provider_name']} - {plan['plan_name']}")
            print(f"   Rate: {plan['rate_1000_cents']}¢/kWh")
            print(f"   Contract: {plan['contract_months']} months" if plan['contract_months'] else "   Contract: N/A")
            print(f"   Type: {plan['plan_type']}")
    else:
        print("⚠️  No plans found - website structure may have changed")
        print("    Run with manual browser inspection to debug")
