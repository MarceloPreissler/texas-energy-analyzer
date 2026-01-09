"""
Commercial Electricity Plan Aggregator for Texas.

This scraper aggregates REAL commercial electricity plan data from multiple
reliable sources that don't require API keys or formal agreements:

1. ElectricChoice.com - Direct table scraping (23+ plans)
2. ElectricityPlans.com - Table scraping by TDU region (39+ plans)

Combined, this provides 60+ unique commercial plans with real pricing data.

Author: Texas Energy Analyzer
Last Updated: January 2026
"""
from __future__ import annotations

import re
from typing import List, Dict
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from playwright_stealth.stealth import Stealth


def scrape_electricchoice_commercial() -> List[Dict]:
    """
    Scrape commercial electricity plans from ElectricChoice.com.

    This site provides a simple HTML table with commercial rates
    that is easy to parse reliably.

    Returns:
        List of plan dictionaries with provider, rate, term, etc.
    """
    plans: List[Dict] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        # Apply stealth mode
        Stealth().apply_stealth_sync(page)

        try:
            url = 'https://www.electricchoice.com/electricity-prices-by-state/texas/business-electricity/'
            print(f"[ElectricChoice] Navigating to {url}...")

            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            page.wait_for_timeout(3000)

            # Find all tables
            tables = page.query_selector_all('table')
            print(f"[ElectricChoice] Found {len(tables)} tables")

            for table in tables:
                rows = table.query_selector_all('tr')

                for ri, row in enumerate(rows):
                    if ri == 0:
                        continue  # Skip header row

                    cells = row.query_selector_all('td')
                    cell_texts = [c.inner_text().strip() for c in cells]

                    # Check if this looks like a plan row (has kWh in rate)
                    if len(cell_texts) >= 3 and 'kWh' in cell_texts[2]:
                        provider = cell_texts[0]
                        term_text = cell_texts[1]
                        rate_text = cell_texts[2]

                        # Parse contract term
                        term_match = re.search(r'(\d+)', term_text)
                        term_months = int(term_match.group(1)) if term_match else None

                        # Parse rate
                        rate_match = re.search(r'([\d.]+)', rate_text)
                        rate = float(rate_match.group(1)) if rate_match else None

                        if provider and rate and rate > 0:
                            plans.append({
                                "provider_name": provider,
                                "plan_name": f"{provider} Commercial {term_months}mo",
                                "plan_type": "Fixed",
                                "service_type": "Commercial",
                                "zip_code": None,  # Statewide rates
                                "contract_months": term_months,
                                "rate_1000_cents": rate,
                                "special_features": None,
                                "source": "ElectricChoice",
                                "last_updated": datetime.now(timezone.utc),
                            })

            print(f"[ElectricChoice] Scraped {len(plans)} commercial plans")

        except PlaywrightTimeout:
            print("[ElectricChoice] Timeout - site may be slow")
        except Exception as e:
            print(f"[ElectricChoice] Error: {e}")
        finally:
            browser.close()

    return plans


def scrape_electricityplans_commercial() -> List[Dict]:
    """
    Scrape commercial electricity plans from ElectricityPlans.com.

    This site provides plans organized by TDU region (Oncor, CenterPoint, etc.)
    with detailed pricing tables.

    Returns:
        List of plan dictionaries with provider, rate, term, etc.
    """
    plans: List[Dict] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        # Apply stealth mode
        Stealth().apply_stealth_sync(page)

        try:
            url = 'https://electricityplans.com/texas/compare/business-electricity/'
            print(f"[ElectricityPlans] Navigating to {url}...")

            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            page.wait_for_timeout(5000)

            # Scroll to load dynamic content
            for _ in range(3):
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                page.wait_for_timeout(1000)

            # Find all tables
            tables = page.query_selector_all('table')
            print(f"[ElectricityPlans] Found {len(tables)} tables")

            for table in tables:
                rows = table.query_selector_all('tr')

                for ri, row in enumerate(rows):
                    if ri == 0:
                        continue  # Skip header

                    cells = row.query_selector_all('td')
                    cell_texts = [c.inner_text().strip() for c in cells]

                    if len(cell_texts) >= 3:
                        plan_name = cell_texts[0]
                        term_text = cell_texts[1]
                        rate_text = cell_texts[2]

                        # Extract provider from plan name
                        # Format is usually "Provider Name X Months"
                        provider = plan_name.split()[0] if plan_name else 'Unknown'

                        # Handle special cases like "APG&E APG&E"
                        if plan_name.startswith("APG&E"):
                            provider = "APG&E"
                        elif "Gexa" in plan_name:
                            provider = "Gexa Energy"
                        elif "ENGIE" in plan_name:
                            provider = "ENGIE Resources"
                        elif "Constellation" in plan_name:
                            provider = "Constellation"

                        # Parse term
                        term_match = re.search(r'(\d+)', term_text)
                        term_months = int(term_match.group(1)) if term_match else None

                        # Parse rate
                        rate_match = re.search(r'([\d.]+)', rate_text)
                        rate = float(rate_match.group(1)) if rate_match else None

                        if rate and rate > 0:
                            plans.append({
                                "provider_name": provider,
                                "plan_name": plan_name[:100],
                                "plan_type": "Fixed",
                                "service_type": "Commercial",
                                "zip_code": None,
                                "contract_months": term_months,
                                "rate_1000_cents": rate,
                                "special_features": None,
                                "source": "ElectricityPlans",
                                "last_updated": datetime.now(timezone.utc),
                            })

            print(f"[ElectricityPlans] Scraped {len(plans)} commercial plans")

        except PlaywrightTimeout:
            print("[ElectricityPlans] Timeout - site may be slow")
        except Exception as e:
            print(f"[ElectricityPlans] Error: {e}")
        finally:
            browser.close()

    return plans


def scrape_all_commercial() -> List[Dict]:
    """
    Aggregate commercial plans from all sources and deduplicate.

    Returns:
        List of unique commercial plans sorted by rate.
    """
    print("=" * 60)
    print("COMMERCIAL ELECTRICITY PLAN AGGREGATOR")
    print("=" * 60)

    all_plans = []

    # Scrape ElectricChoice
    print("\n[1/2] Scraping ElectricChoice.com...")
    try:
        ec_plans = scrape_electricchoice_commercial()
        all_plans.extend(ec_plans)
        print(f"      Found {len(ec_plans)} plans")
    except Exception as e:
        print(f"      Error: {e}")

    # Scrape ElectricityPlans
    print("\n[2/2] Scraping ElectricityPlans.com...")
    try:
        ep_plans = scrape_electricityplans_commercial()
        all_plans.extend(ep_plans)
        print(f"      Found {len(ep_plans)} plans")
    except Exception as e:
        print(f"      Error: {e}")

    # Deduplicate by provider + term + rate (within 0.1 cents)
    seen = set()
    unique_plans = []

    for plan in all_plans:
        key = (
            plan['provider_name'].lower().split()[0],  # First word of provider
            plan['contract_months'],
            round(plan['rate_1000_cents'], 1)
        )
        if key not in seen:
            seen.add(key)
            unique_plans.append(plan)

    # Sort by rate
    unique_plans.sort(key=lambda x: x['rate_1000_cents'])

    print("\n" + "=" * 60)
    print(f"TOTAL: {len(unique_plans)} unique commercial plans")
    print("=" * 60)

    return unique_plans


def get_commercial_plans_summary() -> Dict:
    """
    Get a summary of commercial plan data.

    Returns:
        Dictionary with statistics about available plans.
    """
    plans = scrape_all_commercial()

    if not plans:
        return {"error": "No plans found", "count": 0}

    rates = [p['rate_1000_cents'] for p in plans]
    providers = set(p['provider_name'] for p in plans)

    return {
        "count": len(plans),
        "providers": len(providers),
        "provider_list": sorted(providers),
        "lowest_rate": min(rates),
        "highest_rate": max(rates),
        "average_rate": round(sum(rates) / len(rates), 2),
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "sources": ["ElectricChoice.com", "ElectricityPlans.com"]
    }


# For testing
if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    plans = scrape_all_commercial()

    print("\n" + "=" * 70)
    print("COMMERCIAL PLANS (sorted by rate)")
    print("=" * 70)

    for p in plans:
        print(f"{p['provider_name'][:25]:25} | {p['contract_months'] or '?':>3}mo | {p['rate_1000_cents']:.2f}c/kWh | {p['source']}")

    print("\n" + "-" * 70)
    summary = get_commercial_plans_summary()
    print(f"Summary: {summary['count']} plans from {summary['providers']} providers")
    print(f"Rate range: {summary['lowest_rate']:.2f}c - {summary['highest_rate']:.2f}c/kWh")
    print(f"Average: {summary['average_rate']:.2f}c/kWh")
