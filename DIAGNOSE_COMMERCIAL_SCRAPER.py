#!/usr/bin/env python3
"""
DIAGNOSTIC TOOL: EnergyBot Commercial Scraper

This script helps diagnose why the commercial scraper is returning 0 plans.
It runs step-by-step with detailed logging and screenshots.
"""
import sys
import os
import time
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from playwright.sync_api import sync_playwright

# Create screenshots directory
SCREENSHOT_DIR = Path("/home/user/texas-energy-analyzer/scraper_debug_screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)

def diagnostic_scrape():
    """Run diagnostic scrape with detailed step-by-step logging."""

    print("="*80)
    print("ENERGYBOT COMMERCIAL SCRAPER DIAGNOSTIC")
    print("="*80)
    print()

    zip_code = "75214"  # Dallas

    with sync_playwright() as p:
        # Launch browser in headful mode to see what's happening
        print("[Step 1] Launching browser...")
        browser = p.chromium.launch(
            headless=True,  # Set to False to see the browser
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )

        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        try:
            # Step 1: Navigate to homepage
            print("[Step 2] Navigating to EnergyBot homepage...")
            page.goto("https://www.energybot.com/", wait_until="domcontentloaded", timeout=30000)
            time.sleep(2.0)
            page.screenshot(path=str(SCREENSHOT_DIR / "01_homepage.png"))
            print(f"   ✅ Screenshot saved: 01_homepage.png")
            print(f"   URL: {page.url}")

            # Step 2: Click Business tab
            print("[Step 3] Looking for Business tab...")
            business_selectors = [
                "#bus-tab",
                "a#bus-tab",
                "a.eb-property-selector:has-text('Business')",
                "button:has-text('Business')",
                "[data-property-type='business']"
            ]

            business_clicked = False
            for selector in business_selectors:
                try:
                    element = page.query_selector(selector)
                    if element:
                        print(f"   Found Business tab with selector: {selector}")
                        page.click(selector, timeout=3000)
                        business_clicked = True
                        break
                except Exception as e:
                    print(f"   Selector '{selector}' failed: {e}")
                    continue

            if not business_clicked:
                print("   ❌ Could not find Business tab!")
                page.screenshot(path=str(SCREENSHOT_DIR / "ERROR_no_business_tab.png"))

                # Show all clickable elements
                print("\n   Available links and buttons:")
                links = page.query_selector_all("a, button")
                for i, link in enumerate(links[:20]):
                    text = link.inner_text().strip()[:50] if link.inner_text() else ""
                    if text:
                        print(f"      {i+1}. {text}")

                return False

            time.sleep(1.5)
            page.screenshot(path=str(SCREENSHOT_DIR / "02_business_tab_clicked.png"))
            print(f"   ✅ Business tab clicked")

            # Step 3: Enter ZIP code
            print("[Step 4] Entering ZIP code...")
            zip_selectors = [
                "#eb-zip-code-input-field-handlebars",
                "#zip-code-input",
                "input[name='zipcode']",
                "input[type='text']",
            ]

            zip_entered = False
            for selector in zip_selectors:
                try:
                    element = page.query_selector(selector)
                    if element:
                        print(f"   Found ZIP input with selector: {selector}")
                        page.click(selector, timeout=3000)
                        page.fill(selector, zip_code)
                        zip_entered = True
                        break
                except Exception as e:
                    print(f"   Selector '{selector}' failed: {e}")
                    continue

            if not zip_entered:
                print("   ❌ Could not find ZIP code input!")
                page.screenshot(path=str(SCREENSHOT_DIR / "ERROR_no_zip_input.png"))
                return False

            time.sleep(0.3)
            page.screenshot(path=str(SCREENSHOT_DIR / "03_zip_entered.png"))
            print(f"   ✅ ZIP code entered: {zip_code}")

            # Step 4: Click ZIP submit button
            print("[Step 5] Clicking ZIP submit button...")
            submit_selectors = [
                "#eb-zip-code-submit-button-handlebars",
                "button#eb-zip-code-submit-button",
                "button:has-text('Continue')",
                "button[type='submit']",
            ]

            submit_clicked = False
            for selector in submit_selectors:
                try:
                    element = page.query_selector(selector)
                    if element:
                        print(f"   Found submit button with selector: {selector}")
                        page.click(selector, timeout=3000)
                        submit_clicked = True
                        break
                except Exception as e:
                    print(f"   Selector '{selector}' failed: {e}")
                    continue

            if not submit_clicked:
                print("   ❌ Could not find submit button!")
                page.screenshot(path=str(SCREENSHOT_DIR / "ERROR_no_submit_button.png"))
                return False

            time.sleep(2.5)
            page.screenshot(path=str(SCREENSHOT_DIR / "04_zip_submitted.png"))
            print(f"   ✅ ZIP submitted")
            print(f"   URL: {page.url}")

            # Step 5: Power status question
            print("[Step 6] Looking for 'Power is on' question...")
            yes_selectors = [
                "a.eb-app-choice-button:has-text('Yes')",
                "button:has-text('Yes')",
                "a:has-text('Yes')",
                "[data-power-status='on']"
            ]

            yes_clicked = False
            for selector in yes_selectors:
                try:
                    element = page.query_selector(selector)
                    if element:
                        print(f"   Found 'Yes' button with selector: {selector}")
                        page.click(selector, timeout=3000)
                        yes_clicked = True
                        break
                except Exception as e:
                    print(f"   Selector '{selector}' failed: {e}")
                    continue

            if not yes_clicked:
                print("   ⚠️  Could not find 'Yes' button (may not be required)")
            else:
                time.sleep(1.2)
                page.screenshot(path=str(SCREENSHOT_DIR / "05_power_status.png"))
                print(f"   ✅ Power status selected")

            # Step 6: Check for results
            print("[Step 7] Checking for plan results...")
            time.sleep(3.0)
            page.screenshot(path=str(SCREENSHOT_DIR / "06_final_page.png"))

            # Check for JSON-LD
            scripts = page.query_selector_all('script[type="application/ld+json"]')
            print(f"   Found {len(scripts)} JSON-LD scripts")

            if scripts:
                for i, script in enumerate(scripts[:3]):
                    text = script.inner_text()
                    print(f"\n   JSON-LD Script {i+1}:")
                    print(f"   {text[:200]}...")

            # Check for plan cards
            plan_cards = page.query_selector_all(".plan-card, .eb-plan-card, [data-plan-id]")
            print(f"\n   Found {len(plan_cards)} plan card elements")

            # Check page content
            html = page.content()
            print(f"\n   Page HTML size: {len(html)} characters")

            # Look for common error indicators
            if "no plans" in html.lower():
                print("   ⚠️  Page contains 'no plans' text")
            if "error" in html.lower():
                print("   ⚠️  Page contains 'error' text")
            if "zip code not found" in html.lower():
                print("   ⚠️  ZIP code not found")

            # Save full HTML for inspection
            html_file = SCREENSHOT_DIR / "final_page.html"
            with open(html_file, 'w') as f:
                f.write(html)
            print(f"\n   ✅ Full HTML saved: {html_file}")

            print("\n" + "="*80)
            print("DIAGNOSIS COMPLETE")
            print("="*80)
            print(f"\nScreenshots saved in: {SCREENSHOT_DIR}")
            print("\nReview the screenshots to see where the navigation is failing.")
            print("Check final_page.html to see what content EnergyBot is returning.")

            return True

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            page.screenshot(path=str(SCREENSHOT_DIR / "ERROR_exception.png"))
            return False

        finally:
            browser.close()

if __name__ == "__main__":
    diagnostic_scrape()
