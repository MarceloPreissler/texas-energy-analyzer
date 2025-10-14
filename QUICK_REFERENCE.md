# Texas Energy Analyzer - Quick Reference Card

**One-page reference for daily operations**

---

## 🚀 Start the Application

```bash
# Terminal 1 - Backend
cd texas-energy-analyzer/backend
.venv\Scripts\activate
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd texas-energy-analyzer/frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 📊 Common Tasks

### Scrape Data (Manual)
```bash
curl -X POST "http://localhost:8000/plans/scrape?source=legacy" \
  -H "X-API-Key: your-api-key"
```

### Check Health
```bash
curl http://localhost:8000/health
```

### View Logs
```bash
# Main log
tail -f backend/logs/texas_energy_analyzer.log

# Errors only
tail -f backend/logs/errors.log

# Scraper activity
tail -f backend/logs/scraper.log
```

### Run Tests
```bash
cd backend
.venv\Scripts\activate
python test_all_scrapers.py
```

---

## 🔍 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | No | API info |
| GET | `/health` | No | Health check |
| GET | `/plans/` | No | List plans |
| GET | `/plans/{id}` | No | Get plan |
| GET | `/plans/providers` | No | List providers |
| POST | `/plans/scrape` | Yes | Trigger scrape |

**Authentication:** Add header `X-API-Key: your-key`

---

## 🛠️ Troubleshooting

### Backend Issues

**Port 8000 in use:**
```bash
uvicorn app.main:app --reload --port 8001
```

**Dependencies missing:**
```bash
cd backend
.venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Issues

**Port 5173 in use:**
```bash
npm run dev -- --port 5174
```

**Dependencies missing:**
```bash
cd frontend
npm install
```

### Database Issues

**Reset database:**
```bash
cd backend
rm plans.db
# Restart backend to recreate
```

**Check database:**
```bash
cd backend
python check_db.py
```

---

## 📁 Key Files

```
texas-energy-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py              # Entry point
│   │   ├── api/plans.py         # API routes
│   │   ├── scraping/
│   │   │   ├── scraper.py       # Legacy scraper ✅
│   │   │   ├── powertochoose_scraper.py
│   │   │   └── energybot_scraper.py
│   │   └── logging_config.py    # Logging setup
│   ├── requirements.txt         # Dependencies
│   ├── plans.db                 # SQLite database
│   └── logs/                    # Log files
├── frontend/
│   └── src/
│       ├── App.tsx              # Main UI
│       └── components/
│           └── EnhancedPlanList.tsx
└── Documentation/
    ├── GETTING_STARTED.md       # Setup guide
    ├── SCRAPER_STATUS_REPORT.md # Test results
    ├── TEAM_PRESENTATION.md     # Full presentation
    └── API_DOCUMENTATION.md     # API reference
```

---

## 🔒 Security

**Environment Variables** (backend/.env):
```env
SECRET_KEY=generate-with-openssl-rand-hex-32
API_KEY=generate-with-openssl-rand-hex-32
DATABASE_URL=sqlite:///./plans.db
```

**Generate Keys:**
```bash
openssl rand -hex 32
```

---

## 📦 Deployment

### Quick Share (ngrok)
```bash
ngrok http 5173
# Share the https:// URL
```

### Production (Heroku)
```bash
heroku create app-name
heroku addons:create heroku-postgresql
git push heroku main
heroku open
```

---

## 📊 Status Check

**Scrapers:**
- ✅ Legacy: 68+ plans, 4.5s
- ⚠️ PowerToChoose: Needs timeout fix
- ⚠️ EnergyBot: Needs parser update

**Recommendation:** Use Legacy scraper for production

---

## 💡 Quick Tips

1. **First time setup?** → Read `GETTING_STARTED.md`
2. **Need full docs?** → See `API_DOCUMENTATION.md`
3. **Preparing demo?** → Use `TEAM_PRESENTATION.md`
4. **Deployment?** → Check `PRODUCTION_DEPLOYMENT.md`
5. **Scraper issues?** → Read `SCRAPER_STATUS_REPORT.md`

---

## 🆘 Emergency Contacts

**Logs Location:** `backend/logs/`
**Test Script:** `backend/test_all_scrapers.py`
**Health Check:** http://localhost:8000/health
**API Status:** http://localhost:8000/

---

## 📞 Support

- Documentation folder contains 7 comprehensive guides
- Interactive API docs: http://localhost:8000/docs
- Test suite: `python test_all_scrapers.py`
