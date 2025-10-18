# After You Click "Deploy Blueprint"

## What Happens Next (Automatic):

1. **Render creates PostgreSQL database** (~30 seconds)
   - Database name: texas-energy-db
   - Free tier: 1GB storage

2. **Render builds and deploys backend** (~3-5 minutes)
   - Installs Python dependencies
   - Installs Playwright + Chromium
   - Starts your API server
   - Runs health checks

## How to Know When It's Done:

Watch the Render dashboard. When you see:
- **Green "Live" badge** on texas-energy-backend service
- Status shows "Deploy succeeded"

The backend URL will be something like:
`https://texas-energy-backend.onrender.com`

## After Deployment Completes:

### Step 1: Get Your Backend URL

1. Click on the **texas-energy-backend** service
2. Copy the URL at the top (looks like: https://texas-energy-backend.onrender.com)

### Step 2: Run These 3 Setup Commands

Open PowerShell and run (replace YOUR_URL with your actual backend URL):

```powershell
# 1. Run database migrations (creates tables, adds columns)
Invoke-RestMethod -Uri "https://YOUR_URL.onrender.com/admin/run-migrations" -Method POST

# 2. Load TDU data (6 Texas utilities)
Invoke-RestMethod -Uri "https://YOUR_URL.onrender.com/admin/load-tdus" -Method POST

# 3. Clean any fake data
Invoke-RestMethod -Uri "https://YOUR_URL.onrender.com/admin/delete-fake-commercial-plans" -Method POST
```

### Step 3: Load Fresh Data (Optional)

If you want to load plan data now (or wait for the 3 AM daily job):

```powershell
# Load residential plans (5-10 minutes)
Invoke-RestMethod -Uri "https://YOUR_URL.onrender.com/plans/scrape?source=legacy" -Method POST -TimeoutSec 600

# Load commercial plans (1-2 minutes)
Invoke-RestMethod -Uri "https://YOUR_URL.onrender.com/plans/scrape?source=energybot" -Method POST -TimeoutSec 600
```

### Step 4: Update Vercel Frontend

1. Go to https://vercel.com/dashboard
2. Select your **texas-energy-analyzer** project
3. Go to **Settings** → **Environment Variables**
4. Find `VITE_API_URL` and change it to: `https://YOUR_URL.onrender.com`
5. Go to **Deployments** tab
6. Click **...** menu on latest deployment → **Redeploy**

### Step 5: Verify Everything Works

Test your backend:
```powershell
# Check health
Invoke-RestMethod -Uri "https://YOUR_URL.onrender.com/health"

# Check plans
Invoke-RestMethod -Uri "https://YOUR_URL.onrender.com/plans" | Measure-Object | Select-Object Count

# Check TDUs
Invoke-RestMethod -Uri "https://YOUR_URL.onrender.com/tdus" | Measure-Object | Select-Object Count
```

Test your frontend:
- Go to https://texas-energy-analyzer.vercel.app
- Should load plans and show data

## If Deployment Fails:

Check the build logs in Render dashboard:
1. Click on **texas-energy-backend**
2. Click **Logs** tab
3. Look for errors

Common issues:
- Playwright installation timeout: Just redeploy, it usually works on retry
- Database connection: Check environment variables

## Pricing:

**Free Tier Includes:**
- PostgreSQL: 1GB storage, 1GB bandwidth
- Web Service: 750 hours/month (enough for 24/7)
- Automatic HTTPS
- No credit card required

**Paid Features** ($7/month shown):
- Faster builds
- More resources
- Custom domains
- Priority support

**You can start with FREE tier** - just select "Free" plan if prompted.

## Support:

If you need help:
- Render Docs: https://render.com/docs
- Render Community: https://community.render.com

---

**After setup, your app will be:**
- ✅ 100% clean (zero fake data)
- ✅ All data from REAL sources
- ✅ Automated daily updates
- ✅ Fully legitimate and accurate
