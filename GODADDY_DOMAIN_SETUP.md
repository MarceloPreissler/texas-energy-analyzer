# 🌐 GoDaddy Domain Setup Guide

**Quick guide for connecting your GoDaddy domain to your Texas Energy Analyzer app**

---

## Step 1: Check Domain Availability on GoDaddy

### Option A: Search on GoDaddy Website

1. **Login to GoDaddy**: https://www.godaddy.com/
2. **Search for your domain** in the search bar at the top:
   - Type: `texasenergyanalyzer` (without extension)
   - GoDaddy will show all available extensions

### Option B: Use GoDaddy WHOIS Lookup

1. Go to: https://www.godaddy.com/whois
2. Enter: `texasenergyanalyzer.com` (or `.io`, `.app`)
3. If available, you'll see "Available" with option to purchase

### Recommended Domain Options

**texasenergyanalyzer.com** (Best choice!)
- ✅ Most professional
- ✅ ~$12-20/year on GoDaddy
- ✅ Most trusted extension

**texasenergyanalyzer.io**
- ✅ Tech/startup vibe
- ⚠️ ~$40-50/year on GoDaddy (more expensive)

**texasenergyanalyzer.app**
- ✅ Modern, clearly an app
- ✅ ~$18-25/year on GoDaddy

---

## Step 2: Purchase Your Domain

1. **Add to cart** - Select your preferred domain
2. **Choose duration** - 1 year is fine (you can renew)
3. **Add Domain Privacy**
   - ⚠️ GoDaddy charges extra (~$10/year) for privacy protection
   - ✅ Worth it - hides your personal info from public WHOIS
4. **Disable auto-upsells** - Uncheck email, website builder, etc. (you don't need them)
5. **Complete purchase**

**Total Cost**: ~$20-30/year for .com with privacy

---

## Step 3: Connect Domain to Vercel (Recommended Method)

### 3A: Add Domain in Vercel

1. **Deploy your frontend first** (if not done yet):
   - Go to: https://vercel.com/
   - Click "Import Project"
   - Select `texas-energy-analyzer` repo
   - Root directory: `frontend`
   - Add environment variable:
     - Name: `VITE_API_URL`
     - Value: `https://web-production-665ac.up.railway.app`
   - Click "Deploy"

2. **Add custom domain**:
   - In Vercel dashboard, go to your project
   - Click **Settings** → **Domains**
   - Click **"Add Domain"**
   - Enter your domain: `texasenergyanalyzer.com`
   - Click **"Add"**

3. **Vercel shows DNS records** - Keep this tab open!
   - You'll see something like:
     ```
     Type: A
     Name: @
     Value: 76.76.21.21
     ```

### 3B: Configure DNS in GoDaddy

1. **Login to GoDaddy**: https://account.godaddy.com/
2. **Go to My Products** → **Domains**
3. **Click on your domain** (e.g., `texasenergyanalyzer.com`)
4. **Click "Manage DNS"** or **"DNS"** button

5. **Remove existing records** (important!):
   - Look for existing A records with Host "@"
   - Click the **trash/delete icon** to remove them
   - Look for existing CNAME records with Host "www"
   - Delete those too

6. **Add new A record** (for root domain):
   - Click **"Add"** or **"Add New Record"**
   - Type: **A**
   - Host: **@** (this represents your root domain)
   - Points to: **76.76.21.21** (Vercel's IP - copy from Vercel dashboard)
   - TTL: **1 Hour** (or 600 seconds)
   - Click **"Save"**

7. **Add CNAME record** (for www subdomain):
   - Click **"Add"** again
   - Type: **CNAME**
   - Host: **www**
   - Points to: **cname.vercel-dns.com** (copy from Vercel dashboard)
   - TTL: **1 Hour**
   - Click **"Save"**

### 3C: Verify in Vercel

1. **Go back to Vercel** dashboard
2. **Click "Refresh"** button next to your domain
3. Wait 5-60 minutes for DNS to propagate
4. You'll see **green checkmarks** when ready
5. Vercel automatically issues SSL certificate

---

## Step 4: Update Backend CORS

Your backend needs to allow requests from your new domain.

### Method A: Update via Railway Dashboard (Easiest)

1. Go to: https://railway.app/dashboard
2. Click your **backend service**
3. Go to **Variables** tab
4. Find **ALLOWED_ORIGINS** or add it if missing:
   ```
   ALLOWED_ORIGINS=http://localhost:5173,https://texasenergyanalyzer.com,https://www.texasenergyanalyzer.com,https://web-production-665ac.up.railway.app
   ```
5. Click **"Add"** or **"Update"**
6. Backend will auto-redeploy (takes 1-2 minutes)

### Method B: Update Code (Alternative)

Edit `backend/app/main.py`:

```python
origins = [
    "http://localhost:5173",
    "http://10.0.0.16:5173",
    "https://texasenergyanalyzer.com",        # Add your domain!
    "https://www.texasenergyanalyzer.com",    # Add www version!
    "https://texas-energy-analyzer.vercel.app",
]
```

Then commit and push:
```bash
cd texas-energy-analyzer
git add backend/app/main.py
git commit -m "Add custom domain to CORS origins"
git push origin main
```

---

## Step 5: Test Your Domain

**Wait 5-60 minutes** for DNS propagation, then test:

### ✅ Domain loads
- Go to: **https://texasenergyanalyzer.com/**
- Should show your Texas Energy Analyzer app

### ✅ SSL works
- Look for padlock 🔒 in browser address bar
- Click it - should say "Connection is secure"

### ✅ WWW redirect works
- Go to: **https://www.texasenergyanalyzer.com/**
- Should redirect to non-www (or work independently)

### ✅ API connection works
1. Open browser DevTools (press **F12**)
2. Go to **Network** tab
3. Refresh the page
4. Look for `/plans/providers` request
5. Should show **200** status (not CORS error)

### ✅ Data loads
- Select "Commercial" service type
- Should see 23 commercial plans
- Try filtering by provider
- Everything should work normally

---

## 🆘 Troubleshooting

### "Invalid Configuration" in Vercel

**Cause**: DNS records not propagated yet

**Fix**:
- Wait 5-60 minutes
- Click "Refresh" in Vercel dashboard
- Check DNS with: https://www.whatsmydns.net/
  - Enter your domain
  - Select "A" record type
  - Should show green checkmarks with Vercel's IP

### "CORS Error" in Browser Console

**Cause**: Backend doesn't allow your domain

**Fix**:
- Update backend CORS (see Step 4)
- Make sure you included BOTH:
  - `https://texasenergyanalyzer.com`
  - `https://www.texasenergyanalyzer.com`
- Wait for backend to redeploy (~2 minutes)

### "This site can't be reached"

**Cause**: DNS records not correct

**Fix**:
- Go back to GoDaddy → Manage DNS
- Verify A record:
  - Host: @ (not empty, not domain name)
  - Points to: 76.76.21.21
- Verify CNAME record:
  - Host: www
  - Points to: cname.vercel-dns.com (not your domain)
- Save and wait 10 minutes

### "Not Secure" or SSL Certificate Error

**Cause**: SSL not issued yet

**Fix**:
- Wait up to 24 hours (usually 5-10 minutes)
- In Vercel: Settings → Domains → Click "Refresh"
- If still failing after 24h:
  - Remove domain from Vercel
  - Wait 5 minutes
  - Re-add domain

### Domain Works but Shows Old Website

**Cause**: GoDaddy parked page or previous website

**Fix**:
- GoDaddy → My Products → Your domain
- Look for "Website" or "Hosting" section
- Click "Manage" or "Settings"
- **Disable** or **Delete** any existing website/parking page
- DNS records will now take effect

---

## 🎯 Alternative: Connect to Railway Instead

If you prefer Railway over Vercel:

### Railway Custom Domain Setup

1. **Deploy frontend to Railway** (if not on Vercel):
   - Go to: https://railway.app/dashboard
   - Add new service → GitHub Repo
   - Select `texas-energy-analyzer`
   - Root directory: `frontend`

2. **Add custom domain**:
   - Go to your frontend service
   - Settings → **Domains** → **Custom Domain**
   - Enter: `texasenergyanalyzer.com`

3. **Configure DNS in GoDaddy**:
   - **CNAME record**:
     - Type: CNAME
     - Host: @
     - Points to: `[your-app-name].up.railway.app`

   ⚠️ **Note**: Some registrars (including GoDaddy) don't allow CNAME for root (@). If you get an error:

   **Use A record instead**:
   - Railway will show you an IP address
   - Type: A
   - Host: @
   - Points to: [IP from Railway]

4. **Add www record**:
   - Type: CNAME
   - Host: www
   - Points to: `[your-app-name].up.railway.app`

---

## 💡 Pro Tips for GoDaddy Users

### Save Money on Renewals

- GoDaddy first-year prices are promotional
- Renewals can be 2-3x higher
- Check renewal price BEFORE buying
- Consider transferring to Cloudflare or Namecheap after first year for lower renewals

### Use Cloudflare (Free CDN + Lower Costs)

After purchasing domain on GoDaddy:

1. Sign up at: https://www.cloudflare.com/ (free)
2. Add your domain
3. Cloudflare scans DNS records
4. Update nameservers at GoDaddy to Cloudflare's
5. Benefits:
   - Free SSL certificate
   - Free CDN (faster loading worldwide)
   - Free DDoS protection
   - Better DNS management interface
   - Can transfer registration to Cloudflare later (at-cost pricing)

### Email Forwarding

Want `contact@texasenergyanalyzer.com`?

**GoDaddy Email Forwarding** (included free):
1. My Products → Your domain
2. Email → **Forwarding**
3. Create forwarding address
4. Forward `contact@texasenergyanalyzer.com` → your personal email

---

## 📊 Cost Summary

**Initial Purchase** (First Year):
- Domain: ~$12-20 (.com)
- Domain Privacy: ~$10 (optional but recommended)
- **Total**: ~$22-30

**Annual Renewal** (After First Year):
- Domain: ~$18-25 (.com) ⚠️ Higher than first year
- Domain Privacy: ~$10
- **Total**: ~$28-35/year

**Hosting Costs**:
- Vercel: **$0** (free forever for personal projects)
- Railway backend: **$0-5/month** ($5 free credit)
- **Total hosting**: $0-60/year

**Grand Total**: ~$30-95/year

---

## ✅ Quick Checklist

Before you start:
- [ ] Have GoDaddy account (you have this!)
- [ ] Domain name decided
- [ ] Frontend deployed to Vercel or Railway

Purchase & Setup:
- [ ] Search domain on GoDaddy
- [ ] Purchase with privacy protection
- [ ] Add domain in Vercel/Railway
- [ ] Configure DNS in GoDaddy (A record + CNAME)
- [ ] Update backend CORS
- [ ] Wait for DNS propagation (5-60 min)
- [ ] Test domain loads
- [ ] Verify SSL certificate
- [ ] Test API connection
- [ ] Confirm data loads

---

## 🎉 Success!

Once complete, you'll have:
- ✅ Professional custom domain (texasenergyanalyzer.com)
- ✅ Automatic HTTPS/SSL
- ✅ Accessible from anywhere (work laptop, mobile, etc.)
- ✅ Easy to share with colleagues
- ✅ Auto-deploys on git push

**Your new URLs:**
- Frontend: https://texasenergyanalyzer.com
- Backend API: https://web-production-665ac.up.railway.app
- API Docs: https://web-production-665ac.up.railway.app/docs

---

## 📞 Need Help?

**GoDaddy Support:**
- Phone: 1-480-505-8877
- Chat: Available in your GoDaddy account
- Help: https://www.godaddy.com/help

**Vercel Support:**
- Docs: https://vercel.com/docs
- Discord: https://vercel.com/discord

**Railway Support:**
- Docs: https://docs.railway.app/
- Discord: https://discord.gg/railway

---

**Ready to check domain availability?**

Go to: https://www.godaddy.com/ and search for `texasenergyanalyzer`!

Let me know what domains are available and I'll help with the next steps!
