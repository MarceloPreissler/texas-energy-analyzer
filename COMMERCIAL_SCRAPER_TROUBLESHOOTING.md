# Commercial Scraper Troubleshooting Guide

## Issue: Commercial scraper returns 0 plans

You're getting this when you call:
```bash
curl -X POST "https://web-production-665ac.up.railway.app/plans/scrape?source=energybot_enhanced"
```

## Most Likely Causes (in order of probability):

### 1. **EnergyBot Website Structure Changed** (80% likely)
**Problem**: The selectors in the scraper are hardcoded to specific HTML elements. If EnergyBot updated their website, the scraper can't find the buttons/inputs.

**How to verify**:
1. Visit https://www.energybot.com/ manually
2. Click "Business" tab
3. Check if the flow still works the same way
4. If the website looks different, selectors need updating

**Solution**: Update selectors in `energybot_business_enhanced.py`

---

### 2. **Bot Detection / Rate Limiting** (15% likely)
**Problem**: EnergyBot detects automated traffic and blocks/throttles requests.

**Signs**:
- Works occasionally but not consistently
- Works locally but fails on Railway
- Returns empty pages or redirects to CAPTCHA

**Solution**:
- Add more realistic browser behavior (mouse movements, scrolling)
- Use playwright-stealth (already in requirements.txt)
- Add longer delays between actions
- Rotate user agents

---

### 3. **Playwright Browser Not Installing** (4% likely)
**Problem**: Chromium browser didn't install on Railway.

**How to verify**: Check Railway build logs for:
```
playwright install chromium
Downloading Chromium...
✓ Chromium installed successfully
```

**Solution**: Ensure `railway.json` has correct build commands (it does)

---

### 4. **Timeout Issues** (1% likely)
**Problem**: Scraper times out before plans load.

**Signs**:
- Logs show "Timeout" errors
- Partial results but not complete

**Solution**: Increase timeout values in the scraper

---

## Diagnostic Steps

### Step 1: Check Railway Logs

Go to Railway Dashboard → Your Service → Logs

Look for:
```
[EnergyBot Enhanced] Starting scrape for 5 ZIP codes...
[EnergyBot Enhanced] Processing Dallas - 75214 (ONCOR)
[EnergyBot Enhanced] Clicking Business tab...
[EnergyBot Enhanced] Entering ZIP code: 75214...
```

**What to look for**:
- Does it get past "Clicking Business tab"?
- Are there error messages?
- Does it say "Successfully scraped X plans" (with X = 0)?

### Step 2: Run Diagnostic Script Locally

From YOUR computer (with the repo):
```bash
# Install dependencies
pip install playwright beautifulsoup4

# Install browsers
playwright install chromium

# Run diagnostic
python3 DIAGNOSE_COMMERCIAL_SCRAPER.py
```

This will:
- Take screenshots at each step
- Show exactly where navigation fails
- Save HTML output for inspection
- List all available clickable elements

Screenshots will be saved in: `/home/user/texas-energy-analyzer/scraper_debug_screenshots/`

### Step 3: Check EnergyBot Manually

1. Go to: https://www.energybot.com/
2. Click "Business" tab
3. Enter ZIP: 75214
4. Follow the flow

**Compare to expected flow**:
1. Business tab
2. ZIP code entry
3. "Yes - Power is on"
4. "Same business name"
5. Bill range selection
6. "Standard View"
7. "As Soon As Possible"
8. See plans

**If the flow is different**, the scraper needs updates.

---

## Quick Fixes to Try

### Fix 1: Test with Old v2 Scraper

The old scraper (`energybot_scraper_v2.py`) uses a simpler approach (just loads homepage and extracts JSON-LD).

Try:
```bash
curl -X POST "https://web-production-665ac.up.railway.app/plans/scrape?source=energybot"
```

If this works and returns plans:
- ✅ Problem is with the navigation flow
- ❌ Problem is NOT with data extraction

If this also returns 0:
- ❌ Problem is with data extraction or EnergyBot changed data structure
- ✅ Need to update JSON-LD parsing logic

### Fix 2: Disable Enhanced Scraper Temporarily

Edit `/backend/app/scheduler.py` line 12:
```python
# Change from:
USE_ENHANCED_ENERGYBOT = os.getenv("USE_ENHANCED_ENERGYBOT", "true").lower() == "true"

# To:
USE_ENHANCED_ENERGYBOT = False
```

This switches to the old v2 scraper which might work if it's a navigation issue.

### Fix 3: Increase Timeouts

If you see timeout errors in logs, edit `energybot_business_enhanced.py`:

Change line 338:
```python
# From:
page.goto(url, wait_until="domcontentloaded", timeout=30000)

# To:
page.goto(url, wait_until="load", timeout=60000)
```

Change all `timeout=5000` to `timeout=10000`

---

## Detailed Debugging

### Check 1: Are browsers installed on Railway?

Railway logs should show during build:
```
Installing Playwright browsers...
Downloading Chromium 140.0...
✓ Chromium installed
```

If missing, browsers didn't install.

### Check 2: What does the scraper return?

Add debug logging to see what's happening:

Edit `/backend/app/api/plans.py` line 87:
```python
plans = energybot_business_enhanced.scrape_energybot_all_texas_enhanced()
print(f"[DEBUG] Scraper returned {len(plans)} plans")
print(f"[DEBUG] First plan: {plans[0] if plans else 'NO PLANS'}")
```

### Check 3: Is data extraction working?

The scraper tries two methods:
1. **JSON-LD extraction** (primary) - looks for `<script type="application/ld+json">`
2. **HTML parsing** (fallback) - looks for plan card elements

If both fail, returns 0 plans.

Test by checking page source manually:
1. Go to EnergyBot in browser
2. Complete business flow
3. Right-click → View Page Source
4. Search for `application/ld+json`
5. Check if plan data is there

---

## Common Selector Failures

If EnergyBot changed their website, these selectors might be wrong:

### Business Tab
```python
# Current selectors:
"#bus-tab"
"a#bus-tab"
"a.eb-property-selector:has-text('Business')"
```

**How to find new selector**:
1. Visit EnergyBot
2. Right-click Business tab → Inspect
3. Find the element's ID or class
4. Update selector in code

### ZIP Code Input
```python
# Current:
"#eb-zip-code-input-field-handlebars"
```

Same process - inspect element and find new ID/class.

---

## Emergency Fallback: Use PowerToChoose Only

If commercial scraper can't be fixed quickly:

```bash
# Just scrape residential for now:
curl -X POST "https://web-production-665ac.up.railway.app/plans/scrape?source=powertochoose"
```

This will give you 60-100 residential plans while you debug commercial.

---

## Need Help Debugging?

Run the diagnostic script and send me:

1. All screenshots from `scraper_debug_screenshots/`
2. The `final_page.html` file
3. Railway logs from the scrape attempt
4. Output from running diagnostic script

I can then tell you exactly what's wrong and how to fix it.

---

## Quick Check Commands

```bash
# Test if backend is up:
curl "https://web-production-665ac.up.railway.app/health"

# Check current plan count:
curl "https://web-production-665ac.up.railway.app/plans" | jq 'length'

# Test residential scraper (should work):
curl -X POST "https://web-production-665ac.up.railway.app/plans/scrape?source=powertochoose"

# Test old commercial scraper:
curl -X POST "https://web-production-665ac.up.railway.app/plans/scrape?source=energybot"

# Test new commercial scraper:
curl -X POST "https://web-production-665ac.up.railway.app/plans/scrape?source=energybot_enhanced"
```

---

## Most Likely Solution

Based on typical scraper failures, the issue is probably:

**EnergyBot changed their HTML structure** and the selectors need updating.

**To fix**:
1. Run the diagnostic script
2. Check where it fails (screenshots will show)
3. Visit EnergyBot manually and inspect elements
4. Update selectors in `energybot_business_enhanced.py`
5. Commit and push changes
6. Railway will auto-deploy
7. Test again

This happens with scrapers - websites update and break things. It's why companies pay for APIs! 😅
