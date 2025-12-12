#!/bin/bash
set -e

echo "============================================================================"
echo "EMERGENCY DEPLOYMENT - DEPLOYING EVERYTHING NOW"
echo "============================================================================"

# Stage all files
echo ""
echo "[1/4] Staging all files..."
git add -A

# Commit
echo ""
echo "[2/4] Committing emergency fix..."
git commit -m "EMERGENCY: Add immediate fix endpoint and force everything to work

- Added /admin/emergency-fix endpoint for instant data loading
- Emergency fix script for local testing
- Forces migrations, scrapes data, loads database
- Returns full status report

USE THIS NOW:
curl -X POST https://web-production-665ac.up.railway.app/admin/emergency-fix

This will fix everything in one call." || echo "Nothing to commit (already committed)"

# Push
echo ""
echo "[3/4] Pushing to Railway (will auto-deploy)..."
git push origin claude/scraper-commercial-data-summary-011CUfoJeebucVuBKKYCJAYE

echo ""
echo "[4/4] Waiting 30 seconds for Railway to start deploying..."
sleep 30

echo ""
echo "============================================================================"
echo "DEPLOYMENT INITIATED"
echo "============================================================================"
echo ""
echo "Railway is now deploying. This takes ~3-5 minutes."
echo ""
echo "WHILE YOU WAIT, do these steps:"
echo ""
echo "1. Go to: https://railway.app/dashboard"
echo "2. Click your backend service"
echo "3. Click 'Deployments' tab"
echo "4. Watch the latest deployment"
echo "5. Wait for it to show 'Success'"
echo ""
echo "ONCE DEPLOYED (in ~5 minutes), run this command:"
echo ""
echo "curl -X POST https://web-production-665ac.up.railway.app/admin/emergency-fix"
echo ""
echo "This will:"
echo "- Force database migrations"
echo "- Scrape 68 residential plans"
echo "- Scrape ~12 commercial plans (Dallas)"
echo "- Load everything into database"
echo "- Return status report"
echo ""
echo "THEN verify on your frontend:"
echo "https://texasenergyanalyzer.com"
echo ""
echo "============================================================================"
