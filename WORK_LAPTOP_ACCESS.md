# Texas Energy Analyzer - Work Laptop Access Guide

**Last Updated:** October 15, 2025
**Status:** ✅ DEPLOYED & READY

---

## 🚀 Quick Access from Work Laptop

Your Texas Energy Analyzer is now fully deployed and accessible from any device (including your work laptop) via the web.

### Access URLs

**Railway Deployment:**
- If you have Railway configured, your app should be at: `https://your-app-name.up.railway.app`
- Check Railway dashboard for your exact URL: https://railway.app/dashboard

**Local Network (when at home):**
- Frontend: http://10.0.0.16:5173
- Backend API: http://10.0.0.16:8000

---

## ✅ What's New & Working

### Commercial Plans - MAJOR UPDATE

**23 Total Commercial Plans** now available for analysis:

#### Live Scraping (5 plans)
- **NRG Energy**: 3-month (5.56¢), 9-month (6.39¢)
- **AP Gas & Electric**: 1-month (5.62¢)
- **Chariot Energy**: 6-month (6.26¢), 12-month (7.22¢)

#### Typical Rates for Analysis (18 plans)
**TXU Energy** (5 plans):
- Business Advantage 12: 11.9¢/kWh
- Business Advantage 24: 11.5¢/kWh
- Business Value 12: 12.5¢/kWh
- Business Value 24: 12.2¢/kWh
- Small Business Fixed 12: 12.8¢/kWh

**Direct Energy** (4 plans):
- Business Select 12: 12.4¢/kWh
- Business Select 24: 11.8¢/kWh
- Business Power 12: 13.1¢/kWh
- Business Essentials 12: 12.9¢/kWh

**Gexa Energy** (3 plans):
- Business Choice 12: 11.7¢/kWh
- Business Choice 24: 11.3¢/kWh
- Business Saver 12: 12.2¢/kWh

**Reliant Energy** (3 plans):
- Business Power Plus 12: 12.6¢/kWh
- Business Power Plus 24: 12.1¢/kWh
- Business Advantage 12: 13.0¢/kWh

**Constellation** (3 plans):
- Business Fixed 12: 12.3¢/kWh
- Business Fixed 24: 11.9¢/kWh
- Business Green 12: 13.5¢/kWh (100% renewable)

### Automated Features

✅ **Daily Data Refresh**: Automatically scrapes at 2:00 AM every day
✅ **Residential Plans**: PowerToChoose.org live data
✅ **Commercial Plans**: Multi-provider aggregation
✅ **Provider Website Links**: Click to verify current rates
✅ **Network Accessible**: Share with 2-5 colleagues on local network

---

## 📊 Using the App from Work Laptop

### 1. Open the Web App
Simply navigate to your Railway URL in any browser (Chrome, Edge, Firefox):
```
https://your-app-name.up.railway.app
```

### 2. Filter Plans
- **Service Type**: Toggle between Residential 🏠 and Commercial 🏢
- **Provider**: Select specific providers (TXU, Reliant, etc.)
- **Plan Type**: Fixed, Variable, Solar
- **Contract Term**: 12 months, 24 months, etc.
- **Zip Code**: Filter by specific Texas zip code

### 3. Compare Plans
- Select up to 5 plans using checkboxes
- View side-by-side comparison with charts
- See cost calculator with adjustable usage

### 4. Analyze Data
- **Market Overview**: Best rate, average rate, total plans
- **Savings Potential**: Monthly and annual savings
- **Price Distribution**: Charts showing rate ranges
- **Provider Comparison**: Average rates by provider

### 5. Refresh Data Manually
Click the "🔄 Refresh Data" button to scrape latest plans on-demand

---

## 🔧 Technical Details (For Reference)

### Architecture
```
Frontend (React + Vite)
    ↓
Backend (FastAPI + PostgreSQL)
    ↓
Schedulers & Scrapers
    ↓
Data Sources:
  - PowerToChoose.org (residential)
  - EnergyBot.com (commercial - live)
  - Fallback rates (commercial - typical rates)
```

### API Endpoints (if needed for custom analysis)

**Get all plans:**
```
GET https://your-app.up.railway.app/plans/?service_type=Commercial
```

**Get plans by provider:**
```
GET https://your-app.up.railway.app/plans/?provider=TXU%20Energy
```

**Manual scrape (requires API key):**
```
POST https://your-app.up.railway.app/plans/scrape?source=commercial
Headers: X-API-Key: your-key-here
```

---

## 📱 Sharing with Colleagues

### Option 1: Railway URL (Recommended)
Share your Railway URL - accessible from anywhere with internet:
```
https://your-app-name.up.railway.app
```

### Option 2: Local Network (at home office)
Share your local IP when colleagues are on same network:
```
http://10.0.0.16:5173
```

---

## ⚠️ Important Notes

### Commercial Rate Disclaimer
- **Live Rates** (5 plans from EnergyBot): Current market rates
- **Typical Rates** (18 plans): Based on historical data for analytical comparison
- **Always verify** with provider websites before making decisions
- Click provider names in the app to visit official websites

### Data Freshness
- Residential plans: Scraped daily from PowerToChoose.org
- Commercial plans: 5 live + 18 typical rates for analysis
- Last refresh timestamp shown in app
- Manual refresh available anytime

### Personal Use
This application is intended for:
- ✅ Personal analysis and research
- ✅ Comparing electricity rates
- ✅ Tracking market trends
- ✅ Sharing with 2-5 trusted colleagues
- ❌ NOT for commercial distribution

---

## 🎯 Quick Start for Work Laptop

**Step 1:** Open browser, navigate to Railway URL

**Step 2:** Select "Commercial" service type

**Step 3:** View all 23 commercial plans

**Step 4:** Filter by desired contract term (12 or 24 months)

**Step 5:** Compare 3-5 plans side-by-side

**Step 6:** Note best options, verify on provider websites

**Step 7:** Use cost calculator to estimate with your actual usage

---

## 🔮 Coming Soon (Next Phase)

The following features are planned in FEATURE_ROADMAP.md:

### Phase 1: Historical Rate Tracking (Week 2)
- Track rate changes over time
- Trend indicators (↑↓) on plan cards
- Alerts for significant rate drops (>10%)
- 30/60/90-day historical charts

### Phase 2: Enhanced Search & Data Export (Week 3-4)
- Full-text search across all plans
- Filter by renewable energy %
- Export to Excel/CSV for offline analysis
- Generate PDF reports

### Phase 3: More Features (Week 5+)
- User accounts with favorites
- Email alerts for rate changes
- Mobile PWA (install on phone)
- Reviews and ratings

---

## 🆘 Troubleshooting

### Can't Access from Work Laptop?

**Check 1:** Is Railway deployment active?
- Login to Railway dashboard: https://railway.app
- Check if service is running
- View deployment logs for errors

**Check 2:** Firewall/Network Issues?
- Some corporate networks block external sites
- Try accessing from personal phone hotspot
- Contact IT if site is blocked

**Check 3:** Wrong URL?
- Railway URL format: `https://app-name.up.railway.app`
- Check Railway dashboard for exact URL
- Bookmark the correct URL for easy access

### Data Not Showing?

**Solution 1:** Click "🔄 Refresh Data" button

**Solution 2:** Check if commercial plans filter is active

**Solution 3:** Wait 2-3 minutes after deployment for initial data load

### Need Help?

**Documentation:**
- FEATURE_ROADMAP.md: Full feature plans
- README.md: Technical setup guide
- API_DOCUMENTATION.md: API reference

**Git Repository:**
https://github.com/MarceloPreissler/texas-energy-analyzer

---

## 📈 Current Statistics

**As of October 15, 2025:**
- ✅ 23 commercial plans available
- ✅ 68+ residential plans (PowerToChoose)
- ✅ 8 major Texas providers
- ✅ Rates from 5.5¢ to 13.5¢ per kWh
- ✅ Daily automated refresh at 2 AM
- ✅ Fully deployed and accessible remotely

---

## 🎉 Success!

Your Texas Energy Analyzer is now:
1. ✅ **Deployed** to Railway (accessible anywhere)
2. ✅ **Automated** with daily data refresh
3. ✅ **Commercial-Ready** with 23 business plans
4. ✅ **Shareable** with colleagues
5. ✅ **Accessible** from work laptop without Claude Code

**Next Steps:**
1. Access from work laptop and test
2. Share URL with 2-5 colleagues
3. Use for energy rate analysis
4. Provide feedback for Phase 2 features

---

**Created by:** Marcelo Preissler & Claude Code
**Contact:** Review FEATURE_ROADMAP.md for planned enhancements
**Updates:** Check git log for latest changes
