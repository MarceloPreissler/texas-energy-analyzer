# Deploy to Render.com - Complete Guide

This guide will deploy your Texas Energy Analyzer to Render.com - a more reliable alternative to Railway.

## Why Render.com?

- ✅ More reliable than Railway for Python apps
- ✅ Free tier includes PostgreSQL database
- ✅ Automatic HTTPS
- ✅ Simple deployment from GitHub
- ✅ Better healthcheck handling

## One-Click Deployment (Easiest Method)

### Step 1: Deploy via Render Dashboard

1. Go to https://render.com and sign up/login (free account)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository: `MarceloPreissler/texas-energy-analyzer`
4. Render will automatically detect `render.yaml` and create:
   - PostgreSQL database (`texas-energy-db`)
   - Backend API service (`texas-energy-backend`)
5. Click **"Apply"** and wait ~3-5 minutes for deployment

### Step 2: After Deployment Succeeds

Once the backend shows "Live" (green status):

1. Click on `texas-energy-backend` service
2. Copy the URL (e.g., `https://texas-energy-backend.onrender.com`)
3. Test the API:
   ```
   https://your-backend-url.onrender.com/health
   ```
   Should return: `{"status":"healthy","service":"texas-energy-analyzer","version":"2.0.0"}`

### Step 3: Setup Database & Clean Fake Data

Run these commands in order (replace `YOUR_BACKEND_URL`):

```bash
# 1. Run migrations (creates tables, adds columns)
curl -X POST https://YOUR_BACKEND_URL/admin/run-migrations

# 2. Load TDU data (6 Texas utilities)
curl -X POST https://YOUR_BACKEND_URL/admin/load-tdus

# 3. Delete fake commercial plans
curl -X POST https://YOUR_BACKEND_URL/admin/delete-fake-commercial-plans

# 4. Optionally: Load fresh data
curl -X POST "https://YOUR_BACKEND_URL/plans/scrape?source=legacy"
curl -X POST "https://YOUR_BACKEND_URL/plans/scrape?source=energybot"
```

### Step 4: Update Frontend

1. Go to Vercel dashboard
2. Update environment variable:
   - `VITE_API_URL` = `https://your-backend-url.onrender.com`
3. Redeploy frontend

## Alternative: Manual Deployment (More Control)

### Backend Deployment

1. **Create PostgreSQL Database:**
   - Dashboard → **New +** → **PostgreSQL**
   - Name: `texas-energy-db`
   - Plan: Free
   - Click **Create Database**
   - Copy the **Internal Database URL**

2. **Create Web Service:**
   - Dashboard → **New +** → **Web Service**
   - Connect repository: `MarceloPreissler/texas-energy-analyzer`
   - Name: `texas-energy-backend`
   - Root Directory: `backend`
   - Environment: **Python 3**
   - Build Command:
     ```
     pip install -r requirements.txt && playwright install chromium && playwright install-deps chromium
     ```
   - Start Command:
     ```
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - Plan: **Free**

3. **Add Environment Variables:**
   - `DATABASE_URL` = (paste Internal Database URL from step 1)
   - `RUN_MIGRATIONS` = `true`
   - `ALLOWED_ORIGINS` = `*` (or specific domains)
   - `PYTHON_VERSION` = `3.12.0`

4. Click **Create Web Service**

### Frontend Deployment (Vercel Already Set Up)

Your frontend is already on Vercel. Just update:
- Environment variable: `VITE_API_URL` = `https://your-render-backend.onrender.com`
- Redeploy

## Post-Deployment Verification

```bash
# Check health
curl https://your-backend-url.onrender.com/health

# Check data
curl https://your-backend-url.onrender.com/plans | jq '.[] | length'

# Check TDUs
curl https://your-backend-url.onrender.com/tdus | jq '.[] | .name'

# Verify no fake data
curl https://your-backend-url.onrender.com/plans?service_type=Commercial | jq '.[] | select(.special_features | contains("verify"))'
```

Should return empty array if all fake data is cleaned.

## Scheduled Jobs

Render supports cron jobs. To enable daily scraping at 3 AM:

1. Go to your backend service
2. Add **Cron Job**:
   - Schedule: `0 3 * * *` (3 AM daily)
   - Command: `curl -X POST http://localhost:$PORT/plans/scrape?source=legacy && curl -X POST http://localhost:$PORT/plans/scrape?source=energybot`

## Troubleshooting

### Deployment Fails
- Check build logs in Render dashboard
- Playwright installation can take 2-3 minutes (this is normal)

### Database Connection Issues
- Verify `DATABASE_URL` environment variable is set
- Check database is in same region as web service

### Frontend Not Connecting
- Verify `VITE_API_URL` in Vercel
- Check CORS settings in backend (ALLOWED_ORIGINS)

## Cost

Everything is **FREE**:
- PostgreSQL: 1GB storage (free tier)
- Web Service: 750 hours/month (free tier - enough for 24/7)
- Automatic HTTPS included
- No credit card required for free tier

## Performance

Expected:
- Cold start: ~10-20 seconds (free tier)
- Warm requests: <100ms
- Database queries: <50ms
- Daily scraping: ~5-10 minutes

## Support

Render Docs: https://render.com/docs
Render Community: https://community.render.com
