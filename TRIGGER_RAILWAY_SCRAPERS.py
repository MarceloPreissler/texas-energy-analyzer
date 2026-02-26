#!/usr/bin/env python3
"""
TRIGGER RAILWAY SCRAPERS - Get Fresh Data

This script triggers Railway to scrape fresh data from all sources.
Run this after Railway is deployed and healthy.
"""

import requests
import time
import json

RAILWAY_URL = "https://web-production-665ac.up.railway.app"

print("="*80)
print("TRIGGERING RAILWAY SCRAPERS - FRESH DATA")
print("="*80)
print()

# Step 1: Check health
print("[1/4] Checking Railway health...")
try:
    response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
    if response.status_code == 200:
        print(f"   ✅ Railway is healthy: {response.json()}")
    else:
        print(f"   ❌ Railway returned {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)
except Exception as e:
    print(f"   ❌ Railway health check failed: {e}")
    print(f"   Make sure Railway is deployed and running!")
    exit(1)

print()

# Step 2: Trigger residential scraper
print("[2/4] Triggering residential scraper (PowerToChoose)...")
try:
    response = requests.post(
        f"{RAILWAY_URL}/plans/scrape",
        params={"source": "powertochoose"},
        timeout=300
    )
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Residential scrape initiated: {result}")
    else:
        print(f"   ⚠️ Status {response.status_code}: {response.text}")
except Exception as e:
    print(f"   ❌ Residential scraper failed: {e}")

print()

# Step 3: Trigger commercial scraper
print("[3/4] Triggering commercial scraper (EnergyBot Enhanced)...")
try:
    response = requests.post(
        f"{RAILWAY_URL}/plans/scrape",
        params={"source": "energybot_enhanced"},
        timeout=300
    )
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Commercial scrape initiated: {result}")
    else:
        print(f"   ⚠️ Status {response.status_code}: {response.text}")
except Exception as e:
    print(f"   ❌ Commercial scraper failed: {e}")

print()
print("Waiting 10 seconds for data to load...")
time.sleep(10)
print()

# Step 4: Verify data
print("[4/4] Verifying data loaded...")
try:
    # Check residential
    response = requests.get(
        f"{RAILWAY_URL}/plans",
        params={"service_type": "Residential"},
        timeout=10
    )
    residential_count = len(response.json()) if response.status_code == 200 else 0
    print(f"   • Residential plans: {residential_count}")

    # Check commercial
    response = requests.get(
        f"{RAILWAY_URL}/plans",
        params={"service_type": "Commercial"},
        timeout=10
    )
    commercial_count = len(response.json()) if response.status_code == 200 else 0
    print(f"   • Commercial plans: {commercial_count}")

    # Check total
    response = requests.get(f"{RAILWAY_URL}/plans", timeout=10)
    total_count = len(response.json()) if response.status_code == 200 else 0
    print(f"   • TOTAL plans: {total_count}")

    if total_count > 0:
        print()
        print("="*80)
        print("✅ SUCCESS! Fresh data loaded to Railway")
        print("="*80)
        print()
        print(f"Next step: Visit https://www.texasenergyanalyzer.com to see the data!")
    else:
        print()
        print("⚠️ No data loaded - check Railway logs for errors")

except Exception as e:
    print(f"   ❌ Data verification failed: {e}")

print()
print("="*80)
print("DONE")
print("="*80)
