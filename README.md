# Texas Commercial Energy Market Analyzer

This repository contains a full‑stack application for comparing small‑commercial energy plans in Texas.  The project includes a Python back‑end built with FastAPI and SQLAlchemy, a React front‑end, and a set of scrapers that gather plan data from public websites such as PowerChoiceTexas.  Use this application to benchmark plans from providers like Reliant, Gexa, Direct Energy and TXU.

## Project layout

```
texas-energy-analyzer/
├── backend/
│   ├── requirements.txt        # Python dependencies
│   └── app/
│       ├── main.py             # FastAPI application
│       ├── database.py         # SQLAlchemy session and engine
│       ├── models.py           # ORM definitions
│       ├── schemas.py          # Pydantic models
│       ├── crud.py             # CRUD helper functions
│       ├── api/
│       │   └── plans.py        # Plan API endpoints
│       └── scraping/
│           └── scraper.py      # Web scraping routines
└── frontend/
    ├── package.json            # Node dependencies
    ├── tsconfig.json           # TypeScript configuration
    ├── vite.config.ts          # Vite configuration for development
    └── src/
        ├── index.tsx           # Front‑end entry point
        ├── App.tsx             # Main application component
        ├── components/
        │   ├── PlanList.tsx    # List and filter plans
        │   └── PlanComparison.tsx # Compare selected plans
        └── services/
            └── api.ts          # API helpers for HTTP calls
```

## Getting started

### Back‑end

1. Install Python dependencies:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create an environment file `.env` in `backend/` with your database configuration (see `.env.example`).  By default, the application uses SQLite; to use PostgreSQL provide `DATABASE_URL` in the form `postgresql+psycopg2://user:password@host:port/dbname`.

3. Run database migrations (tables will be created automatically on startup) and start the server:

```bash
uvicorn app.main:app --reload
```

### Front‑end

1. Install Node dependencies:

```bash
cd frontend
npm install
```

2. Start the development server:

```bash
npm run dev
```

The React application will be available at <http://localhost:5173> and will call the FastAPI server at <http://localhost:8000> by default.

## Scraping data

The scraper is triggered manually via the `/scrape` API endpoint or by running the function in `scraper.py`.  It fetches plan information from several public pages:

- **Gexa vs TXU comparison** – sample plans include Gexa Eco Saver Plus 12 & 24 with 8.7–8.9 ¢/kWh and a $125 credit at 1,000 kWh, as well as TXU Smart Edge plans around 13.5 ¢/kWh with a $50 credit at 800 kWh【198457865270454†L229-L271】.
- **Direct Energy** – includes Live Brighter Lite (15.9 ¢/kWh), Bright Secure (16.5 ¢/kWh), and Twelve Hour Power (23.6 ¢/kWh) with free electricity from 9 p.m. to 9 a.m. and a $135 early termination fee【829592562675793†L74-L113】.
- **Reliant Energy** – offers plans like Power Savings 24 (14.9 ¢/kWh), Power Savings 12 (15.5 ¢/kWh), Basic Power 12 (17.2 ¢/kWh)【421074460517785†L110-L131】, and specialty plans such as Truly Free Weekends and Truly Free Nights【421074460517785†L110-L115】【421074460517785†L189-L207】.
- **TXU Energy** – includes Clear Deal, Solar Value, Flex Forward, Free Nights & Solar Days, and Saver’s Discount plans with rates ranging from ~14 ¢/kWh to 23 ¢/kWh【636460671967574†L75-L108】【636460671967574†L113-L160】.

The scraping routines parse these pages, extract plan names, contract terms, rates at the 1,000 kWh tier, and special features, and insert or update entries in the database.