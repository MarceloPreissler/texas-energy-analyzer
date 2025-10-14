"""Test if we can scrape EnergyBot at all"""
from playwright.sync_api import sync_playwright

url = "https://www.energybot.com/electricity-rates/texas/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    page = context.new_page()

    try:
        print(f"Navigating to {url}...")
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
        print("✓ Page loaded successfully")

        # Get title
        title = page.title()
        print(f"Page title: {title}")

        # Check if page has plan data
        html = page.content()
        if 'kWh' in html:
            print("✓ Found kWh references")
        if 'plan' in html.lower():
            print("✓ Found plan references")

        # Try to find plan elements
        plan_cards = page.query_selector_all('[class*="plan"], [class*="rate"], article')
        print(f"Found {len(plan_cards)} potential plan elements")

    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        browser.close()
