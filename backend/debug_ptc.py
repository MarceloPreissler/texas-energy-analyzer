"""Debug script to inspect PowerToChoose.org page structure"""
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Show browser
    page = browser.new_page()

    print("Navigating to PowerToChoose.org...")
    page.goto("https://www.powertochoose.org/", wait_until="networkidle")

    # Accept cookies
    try:
        page.click('button:has-text("Accept")', timeout=2000)
    except:
        pass

    print("\n=== Looking for service type selectors ===")

    # Get all radio buttons
    radios = page.query_selector_all('input[type="radio"]')
    print(f"\nFound {len(radios)} radio buttons:")
    for i, radio in enumerate(radios):
        attrs = {
            'id': radio.get_attribute('id'),
            'name': radio.get_attribute('name'),
            'value': radio.get_attribute('value'),
            'class': radio.get_attribute('class'),
        }
        print(f"  Radio {i}: {attrs}")

    # Get all labels
    labels = page.query_selector_all('label')
    print(f"\nFound {len(labels)} labels:")
    for i, label in enumerate(labels[:10]):  # First 10
        text = label.inner_text()
        for_attr = label.get_attribute('for')
        print(f"  Label {i}: text='{text}', for='{for_attr}'")

    print("\nPress Enter when ready to close browser...")
    input()

    browser.close()
