"""Test script to inspect EnergyBot commercial plans page"""
from playwright.sync_api import sync_playwright
import time

url = "https://www.energybot.com/electricity-rates/texas/business-commercial-electricity.html"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page = context.new_page()

    print(f"Navigating to {url}...")
    page.goto(url, wait_until="networkidle", timeout=30000)

    # Wait a bit for dynamic content
    time.sleep(3)

    print("\n=== Looking for plan containers ===")

    # Try to find plan elements
    selectors_to_try = [
        '.plan-card',
        '.plan-result',
        '.rate-card',
        'table tbody tr',
        '[class*="plan"]',
        '[class*="rate"]',
        'article',
    ]

    for selector in selectors_to_try:
        elements = page.query_selector_all(selector)
        if elements:
            print(f"\nFound {len(elements)} elements with selector: {selector}")
            if len(elements) > 0:
                # Print first element's text
                try:
                    text = elements[0].inner_text()
                    print(f"First element text (truncated): {text[:200]}")
                except:
                    pass

    # Get page HTML and look for plan data
    html = page.content()

    # Look for common patterns
    if 'kWh' in html or 'kwh' in html:
        print("\n✓ Found kWh references (likely has rate data)")
    if 'provider' in html.lower():
        print("✓ Found 'provider' references")
    if 'plan' in html.lower():
        print("✓ Found 'plan' references")

    # Save HTML for inspection
    with open('energybot_page.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("\n✓ Saved page HTML to energybot_page.html")

    print("\nPress Enter to close browser...")
    input()

    browser.close()
