# Deploy Frontend to Railway - Quick Guide

**Goal:** Get your React frontend deployed so you can access it from your work laptop

**Current Status:**
- ✅ Backend deployed: https://web-production-665ac.up.railway.app/
- ⏳ Frontend: Need to deploy (you're here!)

---

## Option A: Deploy via Railway Dashboard (EASIEST - No CLI needed)

### Step 1: Login to Railway
1. Go to: https://railway.app/dashboard
2. Login with your GitHub account

### Step 2: Create New Service
1. Click "+ New Project" or use existing project
2. Select "Deploy from GitHub repo"
3. Choose your repository: `texas-energy-analyzer`
4. Click "Add Service" → "GitHub Repo"

### Step 3: Configure Frontend Service
1. **Root Directory**: Set to `frontend`
2. **Build Command**: `npm run build`
3. **Start Command**: `npm run preview` (or use nginx - see below)
4. **Environment Variables** (under Settings → Variables):
   ```
   VITE_API_URL=https://web-production-665ac.up.railway.app
   ```

### Step 4: Deploy!
Railway will automatically:
- Install dependencies (`npm install`)
- Build your app (`npm run build`)
- Start serving it
- Give you a URL like: `https://texas-energy-frontend.up.railway.app`

### Step 5: Access Your App
Once deployed (2-3 minutes), you'll get a URL. Open it in any browser!

---

## Option B: Deploy via Railway CLI

### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
```

### Step 2: Login
```bash
railway login
```

### Step 3: Link Project
```bash
cd texas-energy-analyzer/frontend
railway link
```

### Step 4: Deploy
```bash
railway up
```

---

## Option C: Use Vercel (Alternative - Very Fast)

Vercel is optimized for React/Vite apps:

### Via Vercel Dashboard
1. Go to: https://vercel.com/
2. Click "Import Project"
3. Connect your GitHub repo
4. **Root Directory**: `frontend`
5. **Framework**: Vite
6. **Environment Variable**:
   ```
   VITE_API_URL=https://web-production-665ac.up.railway.app
   ```
7. Click "Deploy"

You'll get a URL like: `https://texas-energy-analyzer.vercel.app`

---

## Verifying Deployment

Once deployed, test these URLs:

**Frontend Home:**
```
https://your-frontend-url.up.railway.app/
```

**Should show:** Your Texas Energy Analyzer dashboard

**Test API Connection:**
1. Open browser developer tools (F12)
2. Go to Network tab
3. Refresh page
4. Look for calls to `/plans/providers`
5. Should see successful responses (200 status)

---

## Troubleshooting

### "Can't connect to API"

**Problem:** Frontend can't reach backend

**Solution 1:** Check CORS in backend
Your backend needs to allow the frontend URL. Update `backend/app/main.py`:

```python
origins = [
    "http://localhost:5173",
    "http://10.0.0.16:5173",
    "https://your-frontend-url.up.railway.app",  # Add this!
    "https://your-frontend-url.vercel.app",       # Or this if using Vercel
]
```

**Solution 2:** Check environment variable
Make sure `VITE_API_URL` is set correctly in Railway/Vercel dashboard

### "Page is blank"

**Problem:** Build might have failed

**Solution:** Check build logs in Railway dashboard
- Look for errors in "Deployments" tab
- Common issue: Missing dependencies
- Fix: Make sure `package.json` has all dependencies

### "API key required"

**Problem:** Scrape endpoint requires API key

**Good news:** Reading plans doesn't require API key!
Only the `/plans/scrape` endpoint (manual refresh) needs it.

**Solution:** For now, disable manual refresh or add API key to env:
```
VITE_API_KEY=your-key-here
```

---

## What You'll Get

Once deployed, you can:

✅ **Access from anywhere** - Work laptop, phone, tablet
✅ **Share with 2-5 people** - Send them the URL
✅ **Always up-to-date** - Data refreshes daily at 2 AM
✅ **No installation needed** - Just open browser

**Your URLs will be:**
- Backend: https://web-production-665ac.up.railway.app
- Frontend: https://texas-energy-frontend.up.railway.app (or similar)

---

## Recommended: Use Railway for Both

**Why?**
- Both services in one project
- Easy to manage
- Free tier is generous
- Auto-deploys on git push

**Cost:** Free tier includes:
- $5 credit per month
- Usually enough for small apps like this
- Backend + Frontend ~$3-4/month total

---

## Quick Commands Reference

**Railway:**
```bash
# Install CLI
npm install -g @railway/cli

# Login
railway login

# Deploy from frontend folder
cd frontend
railway up

# Check status
railway status

# View logs
railway logs
```

**Git Deploy (After Railway is set up):**
```bash
# Commit changes
git add .
git commit -m "Frontend deployment config"
git push origin main

# Railway auto-deploys!
```

---

## Next Steps After Deployment

1. ✅ Open your frontend URL in browser
2. ✅ Test filtering commercial plans
3. ✅ Share URL with 2-5 colleagues
4. ✅ Bookmark URL on work laptop
5. ✅ Proceed to Feature #3 (Enhanced Search) implementation

---

**Need Help?**
- Railway Docs: https://docs.railway.app/
- Vercel Docs: https://vercel.com/docs
- Your backend API docs: https://web-production-665ac.up.railway.app/docs
