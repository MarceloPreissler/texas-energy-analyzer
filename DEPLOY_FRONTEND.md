# 🚀 Deploy Frontend - 3-Minute Guide

**Your backend is already live:** https://web-production-665ac.up.railway.app/

**Now let's deploy the frontend so you can access it from your work laptop!**

---

## ⚡ FASTEST METHOD - Railway Dashboard (3 clicks!)

### Step 1: Open Railway Dashboard
Click this link: **https://railway.app/new**

Or go to: https://railway.app/dashboard → Click your existing project

### Step 2: Add New Service
1. Click **"+ New Service"**
2. Select **"GitHub Repo"**
3. Choose: **texas-energy-analyzer**
4. Railway detects it's a monorepo
5. Select **ROOT DIRECTORY: `frontend`**

### Step 3: Configure (Railway auto-detects most settings!)
Railway will automatically use the `railway.json` file I created.

Just add this ONE environment variable:
- Go to **Settings → Variables**
- Click **"+ New Variable"**
- Name: `VITE_API_URL`
- Value: `https://web-production-665ac.up.railway.app`
- Click **"Add"**

### Step 4: Deploy!
Railway will:
- ✅ Install dependencies (npm install)
- ✅ Build your app (npm run build)
- ✅ Start serving it
- ✅ Give you a URL!

**Deployment takes 2-3 minutes.**

### Step 5: Get Your URL
Once deployed, Railway gives you a URL like:
```
https://texas-energy-frontend-production-xyz.up.railway.app
```

**THAT'S IT! Open that URL from any device including your work laptop!**

---

## 🎯 Alternative - One-Click Deploy Button

I've prepared your repo for one-click deployment. Just click this button:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/MarceloPreissler/texas-energy-analyzer&envs=VITE_API_URL&VITE_API_URLDefault=https://web-production-665ac.up.railway.app)

This will:
1. Create a new Railway project
2. Deploy your frontend
3. Configure environment variables
4. Give you a URL

---

## 📱 What You Get

Once deployed, you can:

✅ **Access from work laptop** - Just bookmark the URL
✅ **Share with colleagues** - Send them the link
✅ **View 23 commercial plans** - Filter by provider, term, etc.
✅ **Compare plans side-by-side** - Up to 5 at once
✅ **Calculate costs** - Adjust usage and see estimates
✅ **Always current data** - Auto-refreshes daily at 2 AM

---

## 🔧 Technical Details (If Needed)

**Files Created for Easy Deployment:**
- `frontend/railway.json` - Railway configuration
- `frontend/nixpacks.toml` - Build configuration
- `frontend/.env.production` - Production environment variables
- `frontend/dist/` - Pre-built production bundle (backup)

**Railway Auto-Configuration:**
- ✅ Node.js 18
- ✅ Build command: `npm install && npm run build`
- ✅ Start command: `npm run preview -- --host 0.0.0.0 --port $PORT`
- ✅ Auto-restart on failure

---

## ✅ Verification Checklist

After deployment, test these:

**Frontend loads:**
```
https://your-frontend-url.up.railway.app/
```
Should see: Texas Energy Market Analyzer dashboard

**Data loads:**
1. Select "Commercial" service type
2. Should see 23 commercial plans
3. Try filtering by provider (e.g., "TXU Energy")
4. Should see 5 TXU plans

**API connection works:**
1. Open browser DevTools (F12)
2. Go to Network tab
3. Refresh page
4. Look for `/plans/providers` request
5. Should see 200 status (success)

---

## 🆘 Troubleshooting

### "Can't connect to API"

**Fix:** Check CORS in backend

Your backend at `https://web-production-665ac.up.railway.app/` needs to allow your frontend URL.

**Quick Fix:**
1. Go to your backend service in Railway
2. Add environment variable:
   ```
   ALLOWED_ORIGINS=https://your-frontend-url.up.railway.app
   ```
3. Or update `backend/app/main.py` CORS settings and redeploy

### "Build failed"

**Most common issue:** Missing dependencies

**Fix:**
1. Check Railway deployment logs
2. Look for error messages
3. Usually fixed by redeploying (click "Redeploy")

### "Page is blank"

**Fix:** Check browser console (F12)
- Look for JavaScript errors
- Usually means environment variable `VITE_API_URL` is missing
- Add it in Railway Settings → Variables

---

## 📊 Current Setup Summary

**Your Project Structure:**
```
Backend (Python/FastAPI)
https://web-production-665ac.up.railway.app/
    ↓ API calls
Frontend (React/Vite)
https://your-frontend-url.up.railway.app/
    ↓ Users access this
Your Work Laptop / Mobile / Share with colleagues
```

**Data Flow:**
1. User opens frontend URL
2. Frontend calls backend API
3. Backend returns plan data (23 commercial + 68 residential)
4. Frontend displays interactive dashboard
5. Data auto-refreshes daily at 2 AM

---

## 🎉 Success Metrics

Once deployed, you should have:
- ✅ Frontend accessible from anywhere
- ✅ Backend responding to API calls
- ✅ 91+ total plans (23 commercial + 68 residential)
- ✅ Filters working (provider, plan type, contract term)
- ✅ Comparison charts displaying
- ✅ Cost calculator functional
- ✅ Provider website links clickable

---

## 🚀 Next Steps After Deployment

1. **Bookmark your URLs**
   - Frontend: `https://your-frontend-url.up.railway.app`
   - Backend: `https://web-production-665ac.up.railway.app`

2. **Test from work laptop**
   - Open frontend URL
   - Test filtering commercial plans
   - Verify data loads correctly

3. **Share with 2-5 colleagues**
   - Send them the frontend URL
   - No login required (for viewing)
   - Read-only access (can't modify data)

4. **Proceed to Phase 2 Features**
   - Historical Rate Tracking (Feature #1)
   - Enhanced Search & Filtering (Feature #3)
   - User Favorites & Alerts (Feature #2)

---

**Files to Commit (Already Done!):**
- ✅ frontend/railway.json
- ✅ frontend/nixpacks.toml
- ✅ frontend/.env.production
- ✅ frontend/src/services/api.ts (updated)

**Ready to deploy!** Just follow Step 1 above.

---

**Need Help?**
- Railway Docs: https://docs.railway.app/
- Your Backend API Docs: https://web-production-665ac.up.railway.app/docs
- This guide: RAILWAY_FRONTEND_DEPLOY.md (more detailed)

**Questions?** Let me know and I'll help!
