#!/usr/bin/env python3
"""
Verification script to confirm all fixes are in place.
"""
import os

def check_file(filepath, checks):
    """Check if a file contains expected fixes."""
    print(f"\n{'='*60}")
    print(f"Checking: {filepath}")
    print('='*60)

    if not os.path.exists(filepath):
        print(f"❌ FILE NOT FOUND: {filepath}")
        return False

    with open(filepath, 'r') as f:
        content = f.read()

    print(f"✅ File exists ({len(content)} bytes)")

    all_passed = True
    for check_name, search_string in checks.items():
        if search_string in content:
            print(f"  ✅ {check_name}")
        else:
            print(f"  ❌ {check_name} - NOT FOUND")
            all_passed = False

    return all_passed

def main():
    base = "/home/user/texas-energy-analyzer/backend"

    results = []

    # Check 1: PowerToChoose scraper fixes
    results.append(check_file(
        f"{base}/app/scraping/powertochoose_scraper.py",
        {
            "Uses 'load' instead of 'networkidle'": 'wait_until="load"',
            "Has 45-second timeout": "timeout=45000",
            "Multiple ZIP code selectors": "zip_selectors = [",
            "Multiple search button selectors": "search_selectors = [",
            "Graceful timeout handling": "PlaywrightTimeout:",
        }
    ))

    # Check 2: Enhanced EnergyBot scraper
    results.append(check_file(
        f"{base}/app/scraping/energybot_business_enhanced.py",
        {
            "Navigation flow function": "def navigate_business_flow",
            "5 ZIP codes configured": 'ZIPCODES = [',
            "JSON-LD extraction": "def extract_plans_from_json_ld",
            "HTML fallback extraction": "def extract_plans_from_html",
            "TDU metadata": '"tdu":',
        }
    ))

    # Check 3: Scraper utilities
    results.append(check_file(
        f"{base}/app/scraping/scraper_utils.py",
        {
            "Retry with exponential backoff": "def retry_with_backoff",
            "Browser fingerprint evasion": "def get_stealth_context",
            "Smart caching": "@cached_scrape",
            "Data validation": "def validate_commercial_plan",
            "Health monitoring": "class ScraperHealthMonitor",
        }
    ))

    # Check 4: Emergency fix endpoint
    results.append(check_file(
        f"{base}/app/api/admin.py",
        {
            "Emergency fix route": '@router.post("/emergency-fix")',
            "Runs migrations": "ensure_migrations",
            "Scrapes residential": "scraper.scrape_all()",
            "Scrapes commercial": "scrape_energybot_business_enhanced",
        }
    ))

    # Check 5: Automatic migrations
    results.append(check_file(
        f"{base}/app/main.py",
        {
            "Imports migrations": "from .migrations import ensure_migrations",
            "Runs on startup": "ensure_migrations(db)",
            "NO conditional check": "# Removed RUN_MIGRATIONS env var requirement",
        }
    ))

    # Check 6: Enhanced scheduler
    results.append(check_file(
        f"{base}/app/scheduler.py",
        {
            "Full traceback logging": "traceback.format_exc()",
            "Plan name in errors": "plan_data.get('plan_name'",
            "Enhanced scraper option": "USE_ENHANCED_ENERGYBOT",
            "Conditional scraper selection": "if USE_ENHANCED_ENERGYBOT:",
        }
    ))

    print(f"\n\n{'='*60}")
    print("VERIFICATION SUMMARY")
    print('='*60)

    if all(results):
        print("✅ ALL FIXES ARE IN PLACE!")
        print("\nNext steps:")
        print("1. Railway should auto-deploy from the git pushes")
        print("2. Automatic migrations will run on Railway startup")
        print("3. Daily scraper will run at 3 AM with all fixes")
        print("\nTo load data immediately:")
        print("   curl -X POST https://web-production-665ac.up.railway.app/plans/scrape?source=powertochoose")
        print("   curl -X POST https://web-production-665ac.up.railway.app/plans/scrape?source=energybot_enhanced")
        return 0
    else:
        print("❌ SOME FIXES ARE MISSING")
        print("Please review the checks above")
        return 1

if __name__ == "__main__":
    exit(main())
