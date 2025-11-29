"""
EnergyBot.com scraper v2 - SPA Navigation Version.

This version navigates the EnergyBot SPA wizard to reach the commercial plans page
and extracts plan data from the plan cards.
"""
from __future__ import annotations

import json
import re
import time
import logging
from typing import List, Dict
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configure logging
logger = logging.getLogger(__name__)

def scrape_energybot_commercial_v2(zip_code: str = "75001", max_plans: int = 100) -> List[Dict]:
    """
    Scrape commercial electricity plans from EnergyBot.com by navigating the SPA.

    Args:
        zip_code: Texas zip code (default 75001)
        max_plans: Maximum number of plans to scrape

    Returns:
        List of plan dictionaries with provider_name, plan_name, rate, etc.
    """
    plans: List[Dict] = []

    with sync_playwright() as p:
        # Launch browser (headful can be useful for debugging, but headless is faster)
        # Using headless=True for production, but stealth is handled by playwright-stealth if needed.
        # Here we just use standard playwright with a user agent.
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        try:
            # Navigate to the SPA URL directly
            # This URL initiates the wizard for business contract type
            url = f"https://www.energybot.com/app.html#/redirect?ftype=ZIP_CODE&zip_code={zip_code}&contract_type=BUSINESS"
            logger.info(f"[EnergyBot v2] Navigating to {url}...")
            page.goto(url, timeout=60000)

            # SPA Navigation Steps
            
            # Step 1: Current Electric Status -> Yes
            logger.info("[EnergyBot v2] Step 1: Waiting for 'Yes' button...")
            try:
                page.wait_for_selector("text=Yes", timeout=20000)
                page.click("text=Yes")
            except:
                logger.warning("[EnergyBot v2] 'Yes' button not found, checking if already on next step...")

            # Step 2: Business Name -> Same business name
            logger.info("[EnergyBot v2] Step 2: Waiting for 'Same business name' button...")
            try:
                page.wait_for_selector("text=Same business name", timeout=20000)
                page.click("text=Same business name")
            except:
                logger.warning("[EnergyBot v2] 'Same business name' button not found...")

            # Step 3: Bill Amount -> Select 250 and Continue
            logger.info("[EnergyBot v2] Step 3: Waiting for bill select field...")
            try:
                page.wait_for_selector("#bill-select-field", timeout=20000)
                page.select_option("#bill-select-field", "250")
                page.click("#eb-nav-button-next")
            except:
                logger.warning("[EnergyBot v2] Bill select field not found...")

            # Step 4: View Preference -> Standard View
            logger.info("[EnergyBot v2] Step 4: Waiting for 'Standard View' button...")
            try:
                page.wait_for_selector("text=Standard View", timeout=20000)
                page.click("text=Standard View")
            except:
                logger.warning("[EnergyBot v2] 'Standard View' button not found...")

            # Step 5: Start Date -> As Soon As Possible and Continue
            logger.info("[EnergyBot v2] Step 5: Waiting for 'As Soon As Possible' radio...")
            try:
                page.wait_for_selector("label[for='select-asap-date-radio']", timeout=20000)
                page.click("label[for='select-asap-date-radio']")
                page.click("#eb-nav-button-next")
            except:
                logger.warning("[EnergyBot v2] 'As Soon As Possible' radio not found...")

            # Wait for results
            logger.info("[EnergyBot v2] Waiting for results to load...")
            page.wait_for_selector(".eb-plan-card", timeout=30000)
            
            # Scroll to load more plans
            logger.info("[EnergyBot v2] Scrolling to load all plans...")
            for _ in range(5):
                page.mouse.wheel(0, 2000)
                page.wait_for_timeout(1000)
                
            # Extract Plans
            logger.info("[EnergyBot v2] Extracting plan data...")
            plan_cards = page.query_selector_all(".eb-plan-card")
            logger.info(f"[EnergyBot v2] Found {len(plan_cards)} plan cards.")
            
            for card in plan_cards:
                try:
                    # Extract Provider
                    provider_img = card.query_selector("img.eb-supplier-logo")
                    provider = provider_img.get_attribute("alt") if provider_img else "Unknown Provider"
                    
                    # Extract Term
                    term_el = card.query_selector(".eb-label")
                    term_text = term_el.inner_text() if term_el else "Unknown Term"
                    term_match = re.search(r"(\d+)", term_text)
                    term = int(term_match.group(1)) if term_match else 0
                    
                    # Extract Rate
                    rate_el = card.query_selector(".eb-plan-rate")
                    rate_text = rate_el.inner_text() if rate_el else "0"
                    rate_match = re.search(r"(\d+\.?\d*)", rate_text)
                    rate = float(rate_match.group(1)) if rate_match else 0.0
                    
                    # Construct Plan Name
                    plan_name = f"{provider} {term} Month"
                    
                    # Fact Sheet (Link)
                    link_el = card.query_selector("a.eb-residential-plan-button")
                    fact_sheet = link_el.get_attribute("href") if link_el else url
                    if fact_sheet and not fact_sheet.startswith("http"):
                        fact_sheet = f"https://www.energybot.com{fact_sheet}"
                    
                    plan = {
                        "provider_name": provider,
                        "plan_name": plan_name,
                        "rate_1000_cents": rate,
                        "contract_months": term,
                        "cancellation_fee": "See Fact Sheet",
                        "fact_sheet_url": fact_sheet,
                        "plan_type": "Fixed", # Assuming fixed for now
                        "service_type": "Commercial",
                        "zip_code": zip_code,
                        "last_updated": datetime.now(timezone.utc).isoformat()
                    }
                    plans.append(plan)
                    # logger.debug(f"[EnergyBot v2] Scraped: {plan}")
                    
                except Exception as e:
                    # logger.error(f"[EnergyBot v2] Error parsing card: {e}")
                    continue

        except Exception as e:
            logger.error(f"[EnergyBot v2] Navigation/Extraction error: {e}")
            # Save screenshot for debugging (if logs directory exists)
            try:
                import os
                if os.path.exists("logs"):
                    page.screenshot(path="logs/energybot_error.png")
            except Exception as screenshot_err:
                logger.debug(f"Could not save screenshot: {screenshot_err}")
        finally:
            try:
                browser.close()
            except Exception as close_err:
                logger.debug(f"Error closing browser: {close_err}")

    logger.info(f"[EnergyBot v2] Successfully scraped {len(plans)} commercial plans")
    return plans[:max_plans]


def scrape_energybot_all_texas_v2() -> List[Dict]:
    """
    Scrape commercial plans for Texas.

    Returns:
        List of unique commercial plans.
    """
    logger.info("[EnergyBot v2] Scraping Texas commercial plans")
    plans = scrape_energybot_commercial_v2(zip_code="75001", max_plans=100)

    logger.info(f"[EnergyBot v2] Total commercial plans: {len(plans)}")
    return plans


# For testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Testing EnergyBot v2 scraper...")
    plans = scrape_energybot_commercial_v2()

    print(f"\nScraped {len(plans)} plans:")
    for i, plan in enumerate(plans, 1):
        print(f"\n{i}. {plan['provider_name']} - {plan['plan_name']}")
        print(f"   Rate: {plan['rate_1000_cents']}¢/kWh")
        print(f"   Contract: {plan['contract_months']} months")
        print(f"   Type: {plan['plan_type']}")
