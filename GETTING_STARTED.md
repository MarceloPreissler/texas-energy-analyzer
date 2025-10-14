# Getting Started - Texas Energy Analyzer

**Quick start guide to get the application running in under 10 minutes**

---

## What is This?

A web application that compares Texas electricity plans with:
- Automatic data scraping from multiple sources
- Interactive dashboard and comparison charts
- Real-time cost calculator
- REST API for integration

---

## Prerequisites

- Python 3.12 (already installed: `C:\Users\marce\AppData\Local\Programs\Python\Python312\python.exe`)
- Node.js (for frontend)
- Git (optional, for version control)

---

## Quick Start (3 Steps)

### Step 1: Start the Backend (2 minutes)

```bash
# Navigate to backend
cd texas-energy-analyzer/backend

# Activate virtual environment (already set up)
.venv\Scripts\activate

# Start the API server
uvicorn app.main:app --reload
```

**You should see:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

✅ Backend is now running at http://localhost:8000

---

### Step 2: Start the Frontend (2 minutes)

**Open a NEW terminal/PowerShell window:**

```bash
# Navigate to frontend
cd texas-energy-analyzer/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

**You should see:**
```
  VITE ready in XXX ms
  ➜  Local:   http://localhost:5173/
```

✅ Frontend is now running at http://localhost:5173

---

### Step 3: Open the Application

Open your browser and go to: **http://localhost:5173**

You should see the Texas Energy Analyzer dashboard!

---

## Using the Application

### View Available Plans

The homepage shows all electricity plans currently in the database.

**Features:**
- Filter by provider
- Filter by plan type (Fixed, Variable, Solar)
- Filter by contract term (12, 24, 36 months)
- Sort by rate or contract length

### Compare Plans

1. Select up to 5 plans by clicking the checkboxes
2. Click "Compare Selected Plans" button
3. View side-by-side comparison with charts

### Calculate Your Cost

Use the usage slider to see estimated costs based on your consumption.

---

## Loading Data (Scraping Plans)

### Option 1: API Endpoint (Recommended)

**Using the API docs:**
1. Go to http://localhost:8000/docs
2. Find the `/plans/scrape` endpoint
3. Click "Try it out"
4. Set `source` to `legacy`
5. Add your API key in the `X-API-Key` header
6. Click "Execute"

**Using curl:**
```bash
curl -X POST "http://localhost:8000/plans/scrape?source=legacy" \
  -H "X-API-Key: your-api-key-here"
```

**Expected response:**
```json
{
  "plans_processed": 68,
  "source": "legacy",
  "timestamp": "2025-10-09T14:30:00"
}
```

### Option 2: Automated Daily Scraping

The application automatically scrapes data daily at 2:00 AM.

**Configure in:** `backend/app/scheduler.py`

---

## Checking if Everything Works

### Test the Backend

**Health Check:**
```bash
curl http://localhost:8000/health
```

Expected: `{"status":"healthy","service":"texas-energy-analyzer"}`

**Get Plans:**
```bash
curl http://localhost:8000/plans/
```

Expected: JSON array of plans

### Test the Frontend

1. Open http://localhost:5173
2. You should see the dashboard
3. Plans should load (or be empty if database is new)

### Test Scrapers

```bash
cd backend
.venv\Scripts\activate
python test_all_scrapers.py
```

Expected: "Tests Passed: 3/3"

---

## Common Issues

### Backend won't start

**Error:** "ModuleNotFoundError"
**Fix:**
```bash
cd backend
.venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend won't start

**Error:** "command not found: npm"
**Fix:** Install Node.js from https://nodejs.org

**Error:** Dependencies not installed
**Fix:**
```bash
cd frontend
npm install
```

### No plans showing

**Issue:** Database is empty
**Fix:** Run a scrape:
```bash
curl -X POST "http://localhost:8000/plans/scrape?source=legacy" \
  -H "X-API-Key: your-api-key-here"
```

### Port already in use

**Error:** "Address already in use"
**Fix:** Kill the process or use a different port:
```bash
# Backend on different port
uvicorn app.main:app --reload --port 8001

# Frontend on different port
npm run dev -- --port 5174
```

---

## API Endpoints Reference

### Public Endpoints (No Authentication)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/plans/` | List all plans |
| GET | `/plans/{id}` | Get specific plan |
| GET | `/plans/providers` | List providers |

### Protected Endpoints (Require API Key)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/plans/scrape` | Trigger data scrape |

**API Key Header:** `X-API-Key: your-key-here`

---

## Environment Configuration

### Backend (.env file)

Create `backend/.env`:
```env
# Database
DATABASE_URL=sqlite:///./plans.db

# Security
SECRET_KEY=your-secret-key-here
API_KEY=your-api-key-here

# Optional: Redis caching
REDIS_HOST=localhost
REDIS_PORT=6379

# Optional: Rate limiting
RATE_LIMIT_ENABLED=true
```

### Frontend (.env file)

Create `frontend/.env`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## Project Structure

```
texas-energy-analyzer/
│
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── main.py         # Entry point
│   │   ├── models.py       # Database models
│   │   ├── schemas.py      # Pydantic schemas
│   │   ├── crud.py         # Database operations
│   │   ├── api/            # API routes
│   │   └── scraping/       # Scraper modules
│   ├── requirements.txt    # Python dependencies
│   └── .venv/              # Virtual environment
│
├── frontend/               # React application
│   ├── src/
│   │   ├── App.tsx         # Main component
│   │   ├── components/     # UI components
│   │   └── services/       # API client
│   ├── package.json        # Node dependencies
│   └── vite.config.ts      # Vite configuration
│
└── Documentation/
    ├── README.md                    # Overview
    ├── GETTING_STARTED.md          # This file
    ├── SCRAPER_STATUS_REPORT.md    # Scraper testing results
    ├── API_DOCUMENTATION.md        # Complete API reference
    ├── PRODUCTION_DEPLOYMENT.md    # Deployment guide
    └── QUICK_DEPLOY.md             # ngrok/Heroku quick deploy
```

---

## Next Steps

### For Development
1. ✅ Start backend and frontend (you just did this!)
2. Load data with scraper
3. Explore the dashboard
4. Test the API endpoints
5. Customize the UI

### For Production
1. Review `PRODUCTION_DEPLOYMENT.md`
2. Set up PostgreSQL database
3. Configure environment variables
4. Deploy to cloud (Heroku, AWS, Azure)
5. Set up domain name

### For Sharing
1. Use ngrok for instant internet sharing
2. See `QUICK_DEPLOY.md` for instructions

---

## Getting Help

### Documentation
- **API Reference:** `API_DOCUMENTATION.md`
- **Scraper Status:** `SCRAPER_STATUS_REPORT.md`
- **Deployment:** `PRODUCTION_DEPLOYMENT.md`

### Interactive API Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Health & Status
- Health Check: http://localhost:8000/health
- API Version: http://localhost:8000/

---

## Quick Command Reference

```bash
# Backend
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev

# Test Scrapers
cd backend
.venv\Scripts\activate
python test_all_scrapers.py

# Scrape Data
curl -X POST "http://localhost:8000/plans/scrape?source=legacy" \
  -H "X-API-Key: your-api-key"

# Check Health
curl http://localhost:8000/health

# Get Plans
curl http://localhost:8000/plans/
```

---

**You're ready to go! 🎉**

Open http://localhost:5173 and start comparing electricity plans!
