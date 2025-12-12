# Texas Commercial Energy Market Analyzer

This repository contains a full‑stack application for comparing small‑commercial energy plans in Texas.  The project includes a Python back‑end built with FastAPI and SQLAlchemy, a React front‑end, and scrapers that now talk directly to the public PUCTX PowerToChoose API (with an HTML fallback) so every plan for a ZIP code can be imported on demand.

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
│       ├── scrapers/
│       │   └── powertochoose.py # PowerToChoose API + HTML fallback
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

> **API endpoint overrides**
>
> The front-end automatically detects whether it should talk to the local FastAPI server, the public Railway deployment, or an ngrok tunnel.  If you need to point a build at a different environment (for example, a staging API), set `VITE_API_BASE_URL` before running `npm run dev`/`npm run build`, or inject `window.__API_BASE_URL` on the page hosting the compiled bundle.

## Scraping data

### PowerToChoose ZIP imports

The application now uses `backend/app/scrapers/powertochoose.py`, which first calls the public `https://api.powertochoose.org/api/PowerToChoose/plans` endpoint with `page_size=99999` and then falls back to an HTML parser that paginates through every table row on the results site.  Configure the scraper with optional environment variables:

- `POWERS_TO_CHOOSE_API_URL` – override the default API endpoint.
- `POWERS_TO_CHOOSE_HTML_URL` – override the HTML results page URL.
- `POWERS_TO_CHOOSE_PAGE_SIZE` – change the requested page size (defaults to `99999`).

Trigger a live import with a JSON POST request:

```bash
curl -X POST http://localhost:8000/plans/scrape/powertochoose \
  -H "Content-Type: application/json" \
  -d '{"zip_code": "75214"}'
```

The endpoint upserts every returned plan (provider + plan name match) and responds with the number of rows processed.  Add `RUN_MIGRATIONS=true` if you need the automated migration runner to add the `cancellation_fee`, `renewable_percent`, and `ix_plans_zip_code` index to an existing database.

### Legacy scrapers

The general `/plans/scrape` route is still available for other sources (e.g., legacy residential feeds or EnergyBot commercial plans).  Supply the `source` query parameter (`legacy`, `powertochoose`, `energybot`, or `commercial`) and optional `zip_code` just as before.

### Front‑end workflow

Once both servers are running, open the dashboard at <http://localhost:5173>, enter a ZIP in the “View All Plans” card, and click the button.  The UI calls the new POST endpoint, refreshes the cache, and automatically fetches `/plans?zip_code=ZIP`.  All matching rows are displayed in the enhanced table with sorting, filtering, pagination, and the new renewable/cancellation columns.

## Promoting changes to production

Follow this short checklist whenever you need the public deployment (currently hosted on Railway and surfaced at <https://www.texasenergyanalyzer.com>) to pick up the latest code or data:

1. **Merge and push** – land your changes in the default branch of this repository.  Railway watches the backend directory, so a push to the branch that the service is tracking is enough to trigger a build.
2. **Force a backend redeploy (if necessary)** – in the Railway dashboard open the `Texas Energy Analyzer` project, select the backend service (`1f5f65cd-4ea4-4513-a335-4aa09828e1d8`), and click **Deploy**.  This step ensures the new CORS defaults (which already include `https://texasenergyanalyzer.com` and its `www` variant) are running in production.
3. **Verify the API** – hit `https://web-production-665ac.up.railway.app/health` (or the custom domain’s `/health`) and `https://web-production-665ac.up.railway.app/docs` to confirm the FastAPI app started cleanly.  Watch the Railway logs for any migration output or traceback.
4. **Run a scrape for the ZIP you care about** – from your workstation (or Railway’s web shell) issue:

   ```bash
   curl -X POST https://web-production-665ac.up.railway.app/plans/scrape/powertochoose \
     -H "Content-Type: application/json" \
     -d '{"zip_code": "75214"}'
   ```

   Wait for the JSON response that reports how many plans were upserted.
5. **Reload the front-end** – visit <https://www.texasenergyanalyzer.com>, enter the same ZIP, and click **View All Plans**.  You should see the renewable/cancellation columns populate with the exact number of rows imported in the prior step.

Because the API now whitelists both the apex domain and `www`, no additional environment tweaks are required after the redeploy—just follow the sequence above any time the live site appears empty.

## Data sources & integrity

- **PowerToChoose.org** – the official PUCT marketplace.  Every ZIP import first calls the JSON API and falls back to parsing the published HTML tables, so each rate, fee, and renewable percentage is exactly what providers file with the commission.
- **EnergyBot.com** – used for additional commercial comparison data when available so we can validate provider names and plan URLs.

No placeholder or assumed values are injected into the dataset.  If a field is missing from the upstream response it remains `null` in the database and UI, ensuring all surfaced information can be traced back to a verifiable public source.