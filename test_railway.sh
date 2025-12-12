#!/bin/bash

# TEST RAILWAY DEPLOYMENT
# Run this script from YOUR computer (not the Claude environment)

echo "════════════════════════════════════════════════════════════"
echo "TESTING RAILWAY DEPLOYMENT"
echo "════════════════════════════════════════════════════════════"
echo ""

RAILWAY_URL="https://web-production-665ac.up.railway.app"

# Test 1: Health check
echo "[1/5] Testing health endpoint..."
HEALTH=$(curl -s -w "\n%{http_code}" "$RAILWAY_URL/health" --connect-timeout 10 --max-time 15)
HTTP_CODE=$(echo "$HEALTH" | tail -1)
RESPONSE=$(echo "$HEALTH" | head -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Health endpoint working (HTTP $HTTP_CODE)"
    echo "   Response: $RESPONSE"
else
    echo "❌ Health endpoint failed (HTTP $HTTP_CODE)"
    echo "   Response: $RESPONSE"
    echo ""
    echo "⚠️  Railway may still be deploying. Wait 5-10 minutes and try again."
    exit 1
fi

# Test 2: Check if plans exist
echo ""
echo "[2/5] Checking for existing plans..."
PLANS=$(curl -s "$RAILWAY_URL/plans?limit=5")
PLAN_COUNT=$(echo "$PLANS" | grep -o '"id"' | wc -l)

echo "   Found $PLAN_COUNT plans in database"

# Test 3: Trigger residential scrape
echo ""
echo "[3/5] Triggering PowerToChoose scraper (residential)..."
echo "   This may take 60-120 seconds..."

SCRAPE_RES=$(curl -s -X POST "$RAILWAY_URL/plans/scrape?source=powertochoose" -w "\n%{http_code}")
HTTP_CODE=$(echo "$SCRAPE_RES" | tail -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Residential scraper completed (HTTP $HTTP_CODE)"
    SCRAPED=$(echo "$SCRAPE_RES" | head -1)
    echo "   Response: $SCRAPED"
else
    echo "⚠️  Scraper response (HTTP $HTTP_CODE)"
    echo "   Response: $(echo "$SCRAPE_RES" | head -1)"
fi

# Wait before next scrape
echo ""
echo "   Waiting 30 seconds before next scrape..."
sleep 30

# Test 4: Trigger commercial scrape
echo ""
echo "[4/5] Triggering Enhanced EnergyBot scraper (commercial)..."
echo "   This may take 60-120 seconds..."

SCRAPE_COM=$(curl -s -X POST "$RAILWAY_URL/plans/scrape?source=energybot_enhanced" -w "\n%{http_code}")
HTTP_CODE=$(echo "$SCRAPE_COM" | tail -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Commercial scraper completed (HTTP $HTTP_CODE)"
    SCRAPED=$(echo "$SCRAPE_COM" | head -1)
    echo "   Response: $SCRAPED"
else
    echo "⚠️  Scraper response (HTTP $HTTP_CODE)"
    echo "   Response: $(echo "$SCRAPE_COM" | head -1)"
fi

# Test 5: Check final plan count
echo ""
echo "[5/5] Verifying final plan count..."

PLANS_FINAL=$(curl -s "$RAILWAY_URL/plans")
PLAN_COUNT_FINAL=$(echo "$PLANS_FINAL" | grep -o '"id"' | wc -l)

echo "   Total plans in database: $PLAN_COUNT_FINAL"

# Get counts by type
COMMERCIAL=$(curl -s "$RAILWAY_URL/plans?service_type=Commercial" | grep -o '"id"' | wc -l)
RESIDENTIAL=$(curl -s "$RAILWAY_URL/plans?service_type=Residential" | grep -o '"id"' | wc -l)

echo "   • Commercial: $COMMERCIAL"
echo "   • Residential: $RESIDENTIAL"

echo ""
echo "════════════════════════════════════════════════════════════"

if [ "$PLAN_COUNT_FINAL" -gt "50" ]; then
    echo "✅✅✅ SUCCESS! RAILWAY IS FULLY OPERATIONAL! ✅✅✅"
    echo ""
    echo "You now have $PLAN_COUNT_FINAL real electricity plans!"
    echo "The system will automatically update daily at 3 AM."
else
    echo "⚠️  Expected 100+ plans, but only found $PLAN_COUNT_FINAL"
    echo ""
    echo "Possible issues:"
    echo "1. Scrapers may still be running (check Railway logs)"
    echo "2. Websites may have blocked the requests"
    echo "3. Playwright browsers may not have installed"
    echo ""
    echo "Check Railway logs: https://railway.app/dashboard"
fi

echo "════════════════════════════════════════════════════════════"
