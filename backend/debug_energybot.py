"""
Debug script to inspect EnergyBot's actual HTML structure.
"""
from playwright.sync_api import sync_playwright
import re

url = "https://www.energybot.com/electricity-rates/texas/business-commercial-electricity.html"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Visible browser for debugging
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    page = context.new_page()

    try:
        print(f"Navigating to {url}...")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)

        # Wait for content to load
        page.wait_for_timeout(5000)

        print("\n=== PAGE INFO ===")
        print(f"Title: {page.title()}")
        print(f"URL: {page.url}")

        # Save full HTML
        html = page.content()
        with open('energybot_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"\n✓ Saved full HTML to: energybot_page.html")

        # Look for common plan indicators
        print("\n=== SEARCHING FOR PLAN DATA ===")

        # Check for rate mentions
        if 'kWh' in html:
            kwh_count = html.count('kWh')
            print(f"✓ Found 'kWh' {kwh_count} times")

        if '¢' in html or 'cents' in html.lower():
            print(f"✓ Found rate symbols (¢ or cents)")

        # Try to find plan elements
        selectors_to_try = [
            'table tr',
            'div[class*="plan"]',
            'div[class*="rate"]',
            'article',
            '.plan-card',
            '.rate-card',
            '[data-plan]',
            'tbody tr',
        ]

        print("\n=== TESTING SELECTORS ===")
        for selector in selectors_to_try:
            elements = page.query_selector_all(selector)
            if elements:
                print(f"✓ '{selector}': Found {len(elements)} elements")

                # Print first element's text
                if elements:
                    first_text = elements[0].inner_text()[:200]
                    print(f"  First element sample: {first_text}...")
            else:
                print(f"✗ '{selector}': No elements found")

        # Look for tables specifically
        tables = page.query_selector_all('table')
        print(f"\n=== TABLES ===")
        print(f"Found {len(tables)} table(s)")

        for i, table in enumerate(tables):
            rows = table.query_selector_all('tr')
            print(f"\nTable {i+1}: {len(rows)} rows")

            if rows:
                # Print first few rows
                for j, row in enumerate(rows[:3]):
                    cols = row.query_selector_all('td, th')
                    col_texts = [col.inner_text().strip() for col in cols]
                    print(f"  Row {j+1}: {col_texts}")

        # Take screenshot
        page.screenshot(path='energybot_screenshot.png', full_page=True)
        print(f"\n✓ Saved screenshot to: energybot_screenshot.png")

        print("\n=== DONE ===")
        print("Check the files:")
        print("  - energybot_page.html (full HTML)")
        print("  - energybot_screenshot.png (visual)")

        input("\nPress Enter to close browser...")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        browser.close()
