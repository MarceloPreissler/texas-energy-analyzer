# 🌐 Custom Domain Setup Guide

**Goal**: Change from default URL to your custom domain like `texasenergyanalyzer.com` or `texasenergyanalyzer.io`

---

## Step 1: Check Domain Availability & Purchase

### Quick Domain Check
Visit any of these registrars to check availability:
- **Namecheap**: https://www.namecheap.com/ (Recommended - usually cheapest)
- **Google Domains**: https://domains.google/ (Simple, trusted)
- **GoDaddy**: https://www.godaddy.com/
- **Cloudflare**: https://www.cloudflare.com/products/registrar/ (At-cost pricing)

### Domain Options & Pricing

**Option 1: texasenergyanalyzer.com**
- Cost: ~$10-15/year
- Best for: Professional look, most trusted TLD
- Renewal: $12-15/year typically

**Option 2: texasenergyanalyzer.io**
- Cost: ~$30-40/year (more expensive)
- Best for: Tech/startup vibe, popular with developers
- Renewal: $35-40/year typically

**Option 3: texasenergyanalyzer.app**
- Cost: ~$15-20/year
- Best for: Modern, clearly indicates it's an application
- Includes free SSL (required by Google)

**Budget Alternative: texasenergyanalyzer.xyz**
- Cost: ~$1-3/year (very cheap!)
- Renewal: $10-12/year after first year
- Less professional but works fine

### Recommended Registrar: Namecheap

**Why Namecheap?**
- ✅ Cheapest pricing (often 20-30% less than GoDaddy)
- ✅ Free WHOIS privacy (hides your personal info)
- ✅ No upselling pressure
- ✅ Easy DNS management
- ✅ Works perfectly with Vercel and Railway

**How to Buy:**
1. Go to: https://www.namecheap.com/
2. Search for: `texasenergyanalyzer.com` (or .io, .app)
3. If available, click "Add to Cart"
4. **Important**: Enable "WhoisGuard" (free privacy protection)
5. Checkout (usually $10-40 depending on extension)
6. Create account or login
7. Complete purchase

---

## Step 2: Connect Domain to Vercel or Railway

### 🚀 OPTION A: Connect to Vercel (Recommended - Easiest)

#### 2A-1: In Vercel Dashboard

1. Deploy your frontend to Vercel first (if not done yet)
2. Go to your project: https://vercel.com/dashboard
3. Click your `texas-energy-analyzer` project
4. Go to **Settings** → **Domains**
5. Click **"Add Domain"**
6. Enter your domain: `texasenergyanalyzer.com` (or .io)
7. Click **"Add"**

Vercel will show you DNS records to configure.

#### 2A-2: In Namecheap Dashboard

1. Login to Namecheap: https://www.namecheap.com/myaccount/login/
2. Go to **Domain List**
3. Click **"Manage"** next to your domain
4. Go to **Advanced DNS** tab
5. Add these DNS records (provided by Vercel):

**For Root Domain (texasenergyanalyzer.com):**
```
Type: A Record
Host: @
Value: 76.76.21.21
TTL: Automatic
```

**For WWW Subdomain:**
```
Type: CNAME Record
Host: www
Value: cname.vercel-dns.com
TTL: Automatic
```

6. **Remove** any existing A or CNAME records for @ and www
7. Click **"Save All Changes"**

#### 2A-3: Wait for Propagation
- DNS changes take 5-60 minutes
- Vercel will automatically issue SSL certificate
- You'll see a green checkmark when ready

#### 2A-4: Test Your Domain
```
https://texasenergyanalyzer.com/
https://www.texasenergyanalyzer.com/
```

Both should work and redirect to HTTPS automatically!

---

### 🚆 OPTION B: Connect to Railway

#### 2B-1: In Railway Dashboard

1. Deploy your frontend to Railway first
2. Go to: https://railway.app/dashboard
3. Click your frontend service
4. Go to **Settings** → **Domains**
5. Click **"Custom Domain"**
6. Enter: `texasenergyanalyzer.com` (or .io)
7. Railway shows DNS records

#### 2B-2: In Namecheap Dashboard

1. Login to Namecheap
2. Go to **Domain List** → **Manage** → **Advanced DNS**
3. Add these records (from Railway):

**Railway typically provides:**
```
Type: CNAME Record
Host: @
Value: [your-app].up.railway.app
TTL: Automatic

Type: CNAME Record
Host: www
Value: [your-app].up.railway.app
TTL: Automatic
```

4. **Note**: Some registrars don't allow CNAME for root (@). If this happens:
   - Use Railway's IP address as A record instead
   - Or use Cloudflare (see below)

5. Click **"Save All Changes"**

#### 2B-3: Wait & Test
- DNS propagation: 5-60 minutes
- Railway auto-issues SSL certificate
- Test: https://texasenergyanalyzer.com/

---

## Step 3: Update Backend CORS Settings

After your domain is live, update backend to allow requests from it:

### 3-1: Update Railway Backend Environment Variable

1. Go to Railway dashboard: https://railway.app/dashboard
2. Click your **backend service**
3. Go to **Variables** tab
4. Add or update:
   ```
   ALLOWED_ORIGINS=http://localhost:5173,https://texasenergyanalyzer.com,https://www.texasenergyanalyzer.com
   ```
5. Backend will auto-redeploy

### 3-2: OR Update Code Directly

Edit `backend/app/main.py`:

```python
origins = [
    "http://localhost:5173",
    "http://10.0.0.16:5173",
    "https://texasenergyanalyzer.com",        # Add this!
    "https://www.texasenergyanalyzer.com",    # And this!
    "https://texas-energy-analyzer.vercel.app",  # Keep Vercel URL as backup
]
```

Commit and push:
```bash
git add backend/app/main.py
git commit -m "Add custom domain to CORS origins"
git push origin main
```

---

## Step 4: Verification Checklist

After setup (wait 5-60 minutes for DNS), test:

**✅ Domain loads:**
- https://texasenergyanalyzer.com/ → Should show your app
- https://www.texasenergyanalyzer.com/ → Should redirect to non-www (or vice versa)

**✅ SSL works:**
- Look for padlock 🔒 in browser address bar
- Should say "Connection is secure"

**✅ API connection works:**
1. Open browser DevTools (F12)
2. Network tab
3. Refresh page
4. Check `/plans/providers` request
5. Should be 200 status (not CORS error)

**✅ Data loads:**
- Select "Commercial" → Should see 23 plans
- Try filtering → Should work normally

---

## 🔥 Pro Tips

### Use Cloudflare (Optional - Advanced)

**Benefits:**
- Free SSL certificate
- Free DDoS protection
- Free CDN (faster loading worldwide)
- Allows CNAME flattening for root domain
- Analytics dashboard

**Setup:**
1. Go to: https://www.cloudflare.com/
2. Click "Sign Up"
3. Add your domain
4. Cloudflare scans existing DNS records
5. Update nameservers at Namecheap to Cloudflare's
6. Enable "Proxy" (orange cloud) for A/CNAME records
7. Done!

### Domain Privacy Protection

**Always enable** WHOIS privacy protection:
- Hides your personal info (name, address, phone, email)
- Usually free at Namecheap (included)
- GoDaddy charges extra (~$10/year) - avoid them for this reason

### Email Forwarding (Optional)

Want email like `contact@texasenergyanalyzer.com`?

**Free Options:**
- **Cloudflare Email Routing**: Free, unlimited addresses
- **ImprovMX**: Free, up to 3 email aliases
- **Namecheap Email Forwarding**: Free (included with domain)

**Setup at Namecheap:**
1. Domain List → Manage → Email Forwarding
2. Forward: `contact@texasenergyanalyzer.com` → your personal email
3. Done!

---

## 🆘 Troubleshooting

### "Domain not working after 2 hours"

**Check DNS propagation:**
- Go to: https://www.whatsmydns.net/
- Enter your domain
- Select "A" or "CNAME" record type
- Should show green checkmarks worldwide

**If not propagating:**
- Verify DNS records are correct (no typos)
- Check nameservers point to your registrar
- Wait up to 24 hours (rare, but possible)

### "CORS error" in browser console

**Fix:**
- Update backend CORS origins (see Step 3)
- Must include BOTH `https://texasenergyanalyzer.com` and `https://www.texasenergyanalyzer.com`
- Redeploy backend after changing

### "SSL certificate error"

**Vercel:**
- Usually auto-fixes within 24 hours
- Go to Settings → Domains → Click "Refresh Certificate"

**Railway:**
- Check domain is correctly pointed
- May need to remove and re-add custom domain

### "www not working" or "non-www not working"

**Fix:**
- Make sure you have BOTH @ and www DNS records
- Vercel/Railway should handle redirects automatically
- If not, add redirect rule in Vercel/Railway settings

---

## 📊 Cost Summary

### One-Time Costs
- Domain purchase: $10-40 (depends on extension)

### Annual Costs
- Domain renewal: $10-40/year
- Vercel: $0 (free for personal projects)
- Railway: $0-5/month ($0-60/year) - includes $5 free credit
- **Total**: ~$10-100/year depending on choices

### Best Budget Setup
1. Buy .com domain from Namecheap: ~$10/year
2. Use Cloudflare (free): $0
3. Deploy to Vercel (free): $0
4. Backend on Railway (free tier): $0-5/month
**Total: ~$10-70/year**

---

## 🎉 After Setup

Once your custom domain is live:

**Update documentation:**
- Bookmark: https://texasenergyanalyzer.com
- Share this URL with colleagues (much better than vercel.app!)
- Update any references in your code/docs

**Business cards/LinkedIn** (optional):
- "Texas Energy Analyzer: https://texasenergyanalyzer.com"
- Looks way more professional!

**Monitor uptime** (optional free tools):
- UptimeRobot: https://uptimerobot.com/ (free)
- StatusCake: https://www.statuscake.com/ (free)
- Get email alerts if site goes down

---

## ⚡ Quick Start Commands

**Check if domain is available:**
```bash
# Using nslookup (built into Windows)
nslookup texasenergyanalyzer.com
# If returns "can't find", domain might be available!
```

**Check DNS propagation after setup:**
```bash
nslookup texasenergyanalyzer.com 8.8.8.8
```

**Test SSL certificate:**
```bash
curl -I https://texasenergyanalyzer.com
# Should return 200 OK with SSL info
```

---

## 📚 Recommended Domain Registrars (Ranked)

1. **Namecheap** ⭐ Best overall
   - Cheapest prices
   - Free WHOIS privacy
   - Good interface
   - https://www.namecheap.com/

2. **Cloudflare** ⭐ Best for advanced users
   - At-cost pricing (no markup)
   - Free SSL, DDoS protection, CDN
   - Must already have domain or transfer
   - https://www.cloudflare.com/products/registrar/

3. **Google Domains** (Now Squarespace)
   - Simple interface
   - Trusted brand
   - Slightly more expensive
   - https://domains.google/

4. **Porkbun** 🐷 Hidden gem
   - Very cheap
   - Free WHOIS privacy
   - Good support
   - https://porkbun.com/

**AVOID:**
- GoDaddy (expensive renewals, pushy upsells)
- Hostinger (lock-in tactics)
- Any registrar without free WHOIS privacy

---

**Ready to buy your domain?**

1. Go to Namecheap: https://www.namecheap.com/
2. Search for `texasenergyanalyzer.com` or `.io`
3. Buy it (with WHOIS privacy enabled)
4. Come back here and follow Step 2!

**Questions?** Let me know which domain you picked and I'll help with the DNS setup!
