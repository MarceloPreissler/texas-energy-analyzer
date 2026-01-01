# Troubleshooting Guide

This document contains common issues encountered and their solutions for the Texas Energy Analyzer project.

## Table of Contents
- [Frontend Issues](#frontend-issues)
- [Backend Issues](#backend-issues)
- [Scraper Issues](#scraper-issues)
- [Deployment Issues](#deployment-issues)
- [Database Issues](#database-issues)

---

## Frontend Issues

### UI Reverts to White Background / Changes Not Persisting

**Symptom:** Dark theme and other UI changes disappear after deployment or page refresh.

**Cause:** Frontend changes were deployed to Vercel but never committed to git.

**Solution:**
1. Always commit and push changes before deploying:
```bash
cd frontend
git add src/
git commit -m "Your commit message"
git push origin main
```

2. Then build and deploy:
```bash
npm run build
cd dist && npx vercel --prod --yes
npx vercel alias [deployment-url] texasenergyanalyzer.com
```

### ERCOT Dashboard Shows Error / No Data

**Symptom:** ERCOT section displays error or loading state indefinitely.

**Cause:** ERCOT API may be temporarily unavailable, or backend ERCOT endpoint not deployed.

**Solution:**
1. The frontend now has a fallback - it will show Texas Market Statistics from the plans database instead
2. If backend ERCOT endpoint is 404:
   - Ensure `httpx` is in `backend/requirements.txt`
   - Redeploy backend to Railway

### Emojis Appearing in UI

**Symptom:** Unwanted emojis appearing in headers or cards.

**Solution:** Search for and remove emoji characters from component files:
```bash
grep -r "[\x{1F300}-\x{1F9FF}]" frontend/src/
```

---

## Backend Issues

### ERCOT Routes Not Loading (404)

**Symptom:** `/ercot/summary` and `/ercot/current` return 404.

**Cause:** Missing `httpx` dependency or import error in ercot.py.

**Solution:**
1. Add httpx to requirements.txt:
```
httpx
```

2. Redeploy to Railway:
```bash
git add backend/requirements.txt
git commit -m "Add httpx dependency"
git push origin main
```

3. Force redeploy in Railway dashboard if needed.

### Database Connection Errors

**Symptom:** "Connection refused" or "Database not found" errors.

**Cause:** Railway PostgreSQL may be paused or DATABASE_URL incorrect.

**Solution:**
1. Check Railway dashboard for database status
2. Verify DATABASE_URL environment variable is set correctly
3. Database tables are auto-created on startup via:
```python
models.Base.metadata.create_all(bind=engine)
```

### CORS Errors

**Symptom:** Frontend cannot call backend API, browser shows CORS error.

**Solution:** Ensure these origins are in `backend/app/main.py`:
```python
origins = [
    "https://texasenergyanalyzer.com",
    "https://www.texasenergyanalyzer.com",
    "http://localhost:5173",
    "http://localhost:3000",
]
```

---

## Scraper Issues

### PowerToChoose Scraper Failing

**Symptom:** No plans returned from PowerToChoose scrape.

**Cause:** SSL issues, API changes, or rate limiting.

**Solution:**
1. The scraper has multiple fallbacks:
   - Primary: PowerToChoose JSON API with page_size=99999
   - Fallback: HTML scraping with pagination

2. For SSL issues, ensure these are in the scraper:
```python
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
```

3. Manual scrape trigger:
```bash
curl -X POST https://web-production-665ac.up.railway.app/plans/scrape/powertochoose \
  -H "Content-Type: application/json" \
  -d '{"zip_code": "75214"}'
```

### EnergyBot Scraper Failing

**Symptom:** No commercial plans returned.

**Cause:** Playwright issues, website changes, or blocked requests.

**Solution:**
1. Check `USE_ENHANCED_ENERGYBOT` environment variable
2. Ensure Playwright browsers are installed:
```bash
playwright install chromium
```

3. Review scraper logs in Railway dashboard

---

## Deployment Issues

### Vercel Deployment Not Updating

**Symptom:** Changes not appearing on live site after vercel deploy.

**Solution:**
1. Ensure you're deploying from the correct directory:
```bash
cd frontend
npm run build
cd dist
npx vercel --prod --yes
```

2. Set the correct alias:
```bash
npx vercel alias [new-deployment-url] texasenergyanalyzer.com
```

3. Clear browser cache or check in incognito mode.

### Railway Backend Not Redeploying

**Symptom:** Backend changes not reflected in production.

**Solution:**
1. Ensure changes are pushed to main branch
2. Force redeploy in Railway dashboard:
   - Open project > Select backend service > Click "Deploy"
3. Check logs for startup errors

### Domain Not Resolving

**Symptom:** texasenergyanalyzer.com not loading.

**Solution:**
1. Verify DNS settings in GoDaddy:
   - A record pointing to Vercel IP
   - Or CNAME pointing to Vercel deployment
2. Run alias command after each deployment:
```bash
npx vercel alias [deployment-url] texasenergyanalyzer.com
```

---

## Database Issues

### Missing Columns Error

**Symptom:** "Column X does not exist" errors.

**Cause:** New columns added to models but not migrated.

**Solution:**
1. Tables auto-create on startup, but columns need migration
2. For new columns, add migration or recreate table:
```python
# In main.py startup
models.Base.metadata.create_all(bind=engine)
```

### Duplicate Key Errors

**Symptom:** Plans not updating, duplicate key violations.

**Cause:** Upsert logic not matching correctly.

**Solution:** The system checks for existing plans by provider_id + plan_name:
```python
existing = db.query(Plan).filter(
    Plan.provider_id == provider.id,
    Plan.plan_name == plan_create.plan_name
).first()
```

---

## Scheduler Status

The automated scraper runs on this schedule:

| Job | Time | Description |
|-----|------|-------------|
| Daily Scrape | 3:00 AM UTC | Scrapes all sources (Residential + Commercial + PowerToChoose) |
| Startup Scrape | +2 minutes after deploy | Ensures fresh data on deployment |

### Verify Scheduler is Running

Check Railway logs for these messages:
```
[Scheduler] Starting automated REAL DATA scheduler...
[Scheduler] [OK] Daily job scheduled: 3:00 AM scrape REAL data
```

### Manual Trigger

If scheduler didn't run, trigger manually:
```bash
# PowerToChoose scrape
curl -X POST https://web-production-665ac.up.railway.app/plans/scrape/powertochoose \
  -H "Content-Type: application/json" \
  -d '{"zip_code": "75214", "service_type": "Residential"}'

# General scrape
curl -X POST https://web-production-665ac.up.railway.app/plans/scrape
```

---

## Quick Diagnostic Commands

### Check Backend Health
```bash
curl https://web-production-665ac.up.railway.app/health
```

### Check API Documentation
```
https://web-production-665ac.up.railway.app/docs
```

### Count Plans in Database
```bash
curl "https://web-production-665ac.up.railway.app/plans/?limit=1" | jq length
```

### View Recent Commits
```bash
git log --oneline -10
```

### Check Git Status
```bash
git status
```

---

## Contact & Resources

- **Live Site:** https://texasenergyanalyzer.com
- **API Docs:** https://web-production-665ac.up.railway.app/docs
- **Railway Dashboard:** https://railway.app
- **Vercel Dashboard:** https://vercel.com
- **GitHub Repo:** https://github.com/MarceloPreissler/texas-energy-analyzer
