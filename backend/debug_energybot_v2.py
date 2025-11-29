from playwright.sync_api import sync_playwright
import time

def debug_spa():
    print("Running EnergyBot SPA Debug...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()

        try:
            # Navigate to the SPA app URL with zip code
            url = "https://www.energybot.com/app.html#/redirect?ftype=ZIP_CODE&zip_code=75001&contract_type=BUSINESS"
            print(f"[EnergyBot v2] Navigating to {url}...")
            page.goto(url)
            
            # Wait for redirect and load
            print("[EnergyBot v2] Waiting for 'Yes' button...")
            page.wait_for_selector("text=Yes", timeout=20000)
            
            # Click 'Yes' (Power is on)
            print("[EnergyBot v2] Clicking 'Yes'...")
            page.click("text=Yes")

            # Wait for next step
            print("[EnergyBot v2] Waiting for next step (10s)...")
            page.wait_for_timeout(10000)
            
            # Save screenshot 2
            page.screenshot(path="logs/energybot_spa_step2.png")
            print("[EnergyBot v2] Saved screenshot to logs/energybot_spa_step2.png")
            
            # Save HTML 2
            content = page.content()
            with open("energybot_spa_step2.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("[EnergyBot v2] Saved HTML to energybot_spa_step2.html")

            # Step 3: Business Name Change? -> Same business name
            print("[EnergyBot v2] Waiting for 'Same business name' button...")
            page.wait_for_selector("text=Same business name", timeout=20000)
            
            print("[EnergyBot v2] Clicking 'Same business name'...")
            page.click("text=Same business name")

            # Wait for next step
            print("[EnergyBot v2] Waiting for next step (10s)...")
            page.wait_for_timeout(10000)

            # Save screenshot 3
            page.screenshot(path="logs/energybot_spa_step3.png")
            print("[EnergyBot v2] Saved screenshot to logs/energybot_spa_step3.png")
            
            # Save HTML 3
            content = page.content()
            with open("energybot_spa_step3.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("[EnergyBot v2] Saved HTML to energybot_spa_step3.html")

            # Step 4: Monthly Bill Amount -> Select $0 - $500 and Continue
            print("[EnergyBot v2] Waiting for bill select field...")
            page.wait_for_selector("#bill-select-field", timeout=20000)
            
            print("[EnergyBot v2] Selecting bill amount '250'...")
            page.select_option("#bill-select-field", "250")
            
            print("[EnergyBot v2] Waiting for 'Continue' button...")
            page.wait_for_selector("#eb-nav-button-next", timeout=20000)
            
            print("[EnergyBot v2] Clicking 'Continue'...")
            page.click("#eb-nav-button-next")

            # Wait for next step
            print("[EnergyBot v2] Waiting for next step (10s)...")
            page.wait_for_timeout(10000)

            # Save screenshot 4
            page.screenshot(path="logs/energybot_spa_step4.png")
            print("[EnergyBot v2] Saved screenshot to logs/energybot_spa_step4.png")
            
            # Save HTML 4
            content = page.content()
            with open("energybot_spa_step4.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("[EnergyBot v2] Saved HTML to energybot_spa_step4.html")

            # Step 5: How would you like to proceed? -> Standard View
            print("[EnergyBot v2] Waiting for 'Standard View' button...")
            page.wait_for_selector("text=Standard View", timeout=20000)
            
            print("[EnergyBot v2] Clicking 'Standard View'...")
            page.click("text=Standard View")

            # Wait for results to load
            print("[EnergyBot v2] Waiting for results (15s)...")
            page.wait_for_timeout(15000)

            # Save screenshot 5
            page.screenshot(path="logs/energybot_spa_step5.png")
            print("[EnergyBot v2] Saved screenshot to logs/energybot_spa_step5.png")
            
            # Save HTML 5
            content = page.content()
            with open("energybot_spa_step5.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("[EnergyBot v2] Saved HTML to energybot_spa_step5.html")

            # Step 6: Start Date -> As Soon As Possible and Continue
            print("[EnergyBot v2] Waiting for 'As Soon As Possible' radio...")
            page.wait_for_selector("label[for='select-asap-date-radio']", timeout=20000)
            
            print("[EnergyBot v2] Clicking 'As Soon As Possible'...")
            page.click("label[for='select-asap-date-radio']")
            
            print("[EnergyBot v2] Waiting for 'Continue' button...")
            page.wait_for_selector("#eb-nav-button-next", timeout=20000)
            
            print("[EnergyBot v2] Clicking 'Continue'...")
            page.click("#eb-nav-button-next")

            # Wait for results to load
            print("[EnergyBot v2] Waiting for results (15s)...")
            page.wait_for_timeout(15000)

            # Save screenshot 6
            page.screenshot(path="logs/energybot_spa_step6.png")
            print("[EnergyBot v2] Saved screenshot to logs/energybot_spa_step6.png")
            
            # Save HTML 6
            content = page.content()
            with open("energybot_spa_step6.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("[EnergyBot v2] Saved HTML to energybot_spa_step6.html")
            
        except Exception as e:
            print(f"[EnergyBot v2] Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    debug_spa()
