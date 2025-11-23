"""
Live PowerToChoose.org scraper using Playwright for real-time pricing data.

This scraper uses browser automation to fetch current electricity plans
directly from the official PUCT website, ensuring data is always up-to-date.
"""
from __future__ import annotations

import re
from typing import List, Dict
from datetime import datetime, timezone
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

    # Ensure logs directory exists
    import os
    if not os.path.exists("logs"):
        os.makedirs("logs")

    with sync_playwright() as p:
        # Launch browser in headful mode for better debugging/stealth
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        
        # Add stealth mode if available (optional but recommended)
        try:
            from playwright_stealth import stealth_sync
            stealth_sync(page)
        except ImportError:
            pass

        try:
            print(f"[PowerToChoose] Navigating to site...")
            page.goto("https://www.powertochoose.org/", wait_until="domcontentloaded", timeout=60000)

            # Accept cookies if present
            try:
                page.click('button:has-text("Accept")', timeout=5000)
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
            
            # Small delay
            page.wait_for_timeout(2000)

            # Save HTML for inspection
            with open('ptc_debug.html', 'w', encoding='utf-8') as f:
                f.write(page.content())
            print("[PowerToChoose] Saved HTML to ptc_debug.html")

            # Submit form directly via JS to avoid click issues
            print("[PowerToChoose] Submitting form directly...")
            page.evaluate('document.getElementById("planForm").submit()')

            # Wait for navigation to results page
            try:
                page.wait_for_url("**/Plan/Results", timeout=15000)
                print(f"[PowerToChoose] Navigated to: {page.url}")
            except:
                print(f"[PowerToChoose] URL did not change to /Plan/Results. Current: {page.url}")

            # Check for distributor selection modal (it might appear after submit if JS intercepts?)
            # Actually, if we submitted the form, we might be on the new page or the same page if validation failed.
            
            # Wait for results to load
            print(f"[PowerToChoose] Waiting for results...")
            try:
                page.wait_for_selector('#dataTable tr.row', timeout=30000)
            except PlaywrightTimeout:
                print("[PowerToChoose] Timeout waiting for plan selectors.")
                # Save HTML for inspection
                with open('ptc_results_debug.html', 'w', encoding='utf-8') as f:
                    f.write(page.content())
                print("[PowerToChoose] Saved results page HTML to ptc_results_debug.html")
                raise # Re-raise to trigger the outer exception handler (screenshot)

            # Give extra time for dynamic content
            page.wait_for_timeout(2000)

            # Parse results
            plan_rows = page.query_selector_all('#dataTable tbody tr.row')
            print(f"[PowerToChoose] Found {len(plan_rows)} plans")

            for idx, row in enumerate(plan_rows[:max_plans]):
                try:
                    # Provider Name
                    provider_el = row.query_selector('td.td-company .logotype a')
                    provider_name = "Unknown"
                    if provider_el:
                        title = provider_el.get_attribute('title')
                        if title:
                            provider_name = title.replace("External link to company website for ", "").strip()
                        else:
                            img_el = row.query_selector('td.td-company .logotype img')
                            if img_el:
                                alt = img_el.get_attribute('alt')
                                if alt:
                                    provider_name = alt.replace("logo for ", "").strip()

                    # Plan Name
                    plan_name_el = row.query_selector('td.td-plan ul.plan-info li:first-child')
                    plan_name = plan_name_el.inner_text().strip() if plan_name_el else "Unknown Plan"

                    # Rate
                    rate_el = row.query_selector('td.td-price .price')
                    rate = 0.0
                    if rate_el:
                        rate_text = rate_el.inner_text().strip()
                        # Remove '¢' and convert to float
                        rate = float(re.sub(r'[^\d.]', '', rate_text))

                    # Contract Term & Plan Type
                    contract_months = None
                    plan_type = "Fixed"
                    
                    info_lis = row.query_selector_all('td.td-plan ul.plan-info li.grid-element')
                    for li in info_lis:
                        text = li.inner_text().strip()
                        if "Month" in text:
                            match = re.search(r'(\d+)', text)
                            if match:
                                contract_months = int(match.group(1))
                        elif "Fixed" in text:
                            plan_type = "Fixed"
                        elif "Variable" in text:
                            plan_type = "Variable"
                        elif "Indexed" in text:
                            plan_type = "Indexed"

                    # Fact Sheet URL
                    fact_sheet_el = row.query_selector('a#el_fact_sheet')
                    fact_sheet_url = fact_sheet_el.get_attribute('href') if fact_sheet_el else None

                    # Only add if we have at least provider and rate
                    if provider_name != "Unknown" and rate > 0:
                        plans.append({
                            "provider_name": provider_name,
                            "plan_name": plan_name,
                            "plan_type": plan_type,
                            "service_type": service_type,
                            "zip_code": zip_code,
                            "contract_months": contract_months,
                            "rate_1000_cents": rate,
                            "special_features": None,
                            "fact_sheet_url": fact_sheet_url,
                            "last_updated": datetime.now(timezone.utc),
                        })

                except Exception as e:
                    print(f"[PowerToChoose] Error parsing row {idx}: {e}")
                    continue

        except PlaywrightTimeout:
            print("[PowerToChoose] Timeout - site may be slow or down")
            page.screenshot(path="logs/ptc_timeout.png")
            print("[PowerToChoose] Saved screenshot to logs/ptc_timeout.png")
        except Exception as e:
            print(f"[PowerToChoose] Error: {e}")
            page.screenshot(path="logs/ptc_error.png")
            print("[PowerToChoose] Saved screenshot to logs/ptc_error.png")
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
