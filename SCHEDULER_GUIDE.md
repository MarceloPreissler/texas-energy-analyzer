# Automated Scraping Scheduler Guide

## Overview

The Texas Energy Analyzer uses APScheduler to automatically scrape PowerToChoose.org daily, keeping electricity plan data fresh without manual intervention.

## How It Works

### Architecture

```
┌─────────────────────┐
│   FastAPI Startup   │
│   (lifespan event)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  start_scheduler()  │
│  - Initialize jobs  │
│  - Set CronTrigger  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ BackgroundScheduler │
│  Daily at 2:00 AM   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    scrape_job()     │
│ - Scrape all Texas  │
│ - Update database   │
│ - Log results       │
└─────────────────────┘
```

### Default Configuration

- **Schedule**: Daily at 2:00 AM Central Time
- **Data Source**: PowerToChoose.org (official PUCT)
- **Coverage**: All major Texas cities
- **Automatic**: Runs on application startup

## Configuration

### Basic Setup

The scheduler is automatically enabled via the application lifespan in `backend/app/main.py`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("[App] Starting background scheduler...")
    start_scheduler()
    yield
    # Shutdown
    print("[App] Stopping background scheduler...")
    stop_scheduler()

app = FastAPI(
    title="Texas Commercial Energy Market Analyzer",
    lifespan=lifespan  # Enable background scheduler
)
```

### Scheduler Configuration

Edit `backend/app/scheduler.py` to customize:

#### Change Schedule Time

```python
from apscheduler.triggers.cron import CronTrigger

# Daily at 4:30 AM
scheduler.add_job(
    scrape_job,
    trigger=CronTrigger(hour=4, minute=30),
    id="daily_scrape",
    name="PowerToChoose Daily Scrape",
    replace_existing=True,
)

# Daily at midnight
scheduler.add_job(
    scrape_job,
    trigger=CronTrigger(hour=0, minute=0),
    id="daily_scrape",
    name="PowerToChoose Midnight Scrape",
    replace_existing=True,
)
```

#### Multiple Daily Scrapes

```python
# Morning scrape at 6 AM
scheduler.add_job(
    scrape_job,
    trigger=CronTrigger(hour=6, minute=0),
    id="morning_scrape",
    name="Morning Scrape",
)

# Evening scrape at 6 PM
scheduler.add_job(
    scrape_job,
    trigger=CronTrigger(hour=18, minute=0),
    id="evening_scrape",
    name="Evening Scrape",
)
```

#### Hourly Scraping

```python
# Every hour
scheduler.add_job(
    scrape_job,
    trigger=CronTrigger(minute=0),  # Top of every hour
    id="hourly_scrape",
    name="Hourly Scrape",
)

# Every 4 hours
scheduler.add_job(
    scrape_job,
    trigger=CronTrigger(hour='*/4', minute=0),
    id="four_hourly_scrape",
    name="Four Hour Scrape",
)
```

#### Weekly Scraping

```python
# Every Monday at 3 AM
scheduler.add_job(
    scrape_job,
    trigger=CronTrigger(day_of_week='mon', hour=3, minute=0),
    id="weekly_scrape",
    name="Weekly Monday Scrape",
)

# Monday, Wednesday, Friday at 2 AM
scheduler.add_job(
    scrape_job,
    trigger=CronTrigger(day_of_week='mon,wed,fri', hour=2, minute=0),
    id="mwf_scrape",
    name="Mon/Wed/Fri Scrape",
)
```

### Run on Startup

Uncomment this section in `backend/app/scheduler.py`:

```python
def start_scheduler():
    # ... existing code ...

    # Run immediately on startup
    scheduler.add_job(
        scrape_job,
        trigger='date',
        id='startup_scrape',
        name='Startup Scrape'
    )

    scheduler.start()
```

## Environment Variables

Configure via `.env`:

```env
# Scheduler Configuration
SCRAPE_SCHEDULE_HOUR=2
SCRAPE_SCHEDULE_MINUTE=0
SCRAPE_TIMEZONE=America/Chicago

# Enable/disable scheduler
SCHEDULER_ENABLED=true

# Run on startup
SCRAPE_ON_STARTUP=false
```

Use in code:

```python
import os

SCHEDULE_HOUR = int(os.getenv("SCRAPE_SCHEDULE_HOUR", 2))
SCHEDULE_MINUTE = int(os.getenv("SCRAPE_SCHEDULE_MINUTE", 0))
TIMEZONE = os.getenv("SCRAPE_TIMEZONE", "America/Chicago")

scheduler.add_job(
    scrape_job,
    trigger=CronTrigger(
        hour=SCHEDULE_HOUR,
        minute=SCHEDULE_MINUTE,
        timezone=TIMEZONE
    ),
    id="daily_scrape",
    name="PowerToChoose Daily Scrape",
    replace_existing=True,
)
```

## Monitoring

### Check Logs

```bash
# Docker logs
docker-compose logs -f backend | grep Scheduler

# Look for these messages:
# [App] Starting background scheduler...
# [Scheduler] Background scheduler started. Next run: 2:00 AM
# [Scheduler] Starting automated scrape at 2025-10-04 02:00:00
# [Scheduler] Successfully processed 247 plans
```

### View Next Run Time

Add to `backend/app/scheduler.py`:

```python
def get_next_run_time():
    """Get next scheduled run time."""
    jobs = scheduler.get_jobs()
    for job in jobs:
        print(f"Job: {job.name}")
        print(f"Next run: {job.next_run_time}")
```

### Add Status Endpoint

Add to `backend/app/main.py`:

```python
from .scheduler import scheduler

@app.get("/scheduler/status")
async def scheduler_status():
    """Get scheduler status and next run times."""
    jobs = scheduler.get_jobs()
    return {
        "running": scheduler.running,
        "jobs": [
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            }
            for job in jobs
        ]
    }
```

Check status:
```bash
curl http://localhost:8000/scheduler/status
```

Response:
```json
{
  "running": true,
  "jobs": [
    {
      "id": "daily_scrape",
      "name": "PowerToChoose Daily Scrape",
      "next_run": "2025-10-04T02:00:00"
    }
  ]
}
```

## Advanced Features

### Email Notifications

```python
import smtplib
from email.mime.text import MIMEText

def send_notification(subject, body):
    """Send email notification."""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = os.getenv("EMAIL_FROM")
    msg['To'] = os.getenv("EMAIL_TO")

    with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT"))) as server:
        server.starttls()
        server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
        server.send_message(msg)

def scrape_job():
    """Background job with email notifications."""
    logger.info(f"[Scheduler] Starting automated scrape at {datetime.now()}")

    try:
        # ... scraping logic ...

        # Success notification
        send_notification(
            subject="Scrape Successful",
            body=f"Successfully processed {created_or_updated} plans"
        )
        logger.info(f"[Scheduler] Successfully processed {created_or_updated} plans")

    except Exception as e:
        # Error notification
        send_notification(
            subject="Scrape Failed",
            body=f"Error during scrape: {str(e)}"
        )
        logger.error(f"[Scheduler] Error during scrape: {e}")
```

### Conditional Scraping

Only scrape if data is stale:

```python
from datetime import datetime, timedelta

def should_scrape(db: Session) -> bool:
    """Check if scraping is needed."""
    latest_plan = db.query(models.Plan).order_by(
        models.Plan.last_updated.desc()
    ).first()

    if not latest_plan:
        return True  # No data, scrape

    # Scrape if data is older than 12 hours
    age = datetime.now() - latest_plan.last_updated
    return age > timedelta(hours=12)

def scrape_job():
    """Conditional scraping job."""
    db: Session = SessionLocal()
    try:
        if not should_scrape(db):
            logger.info("[Scheduler] Data is fresh, skipping scrape")
            return

        # Proceed with scraping...
    finally:
        db.close()
```

### Retry on Failure

```python
from apscheduler.triggers.interval import IntervalTrigger

MAX_RETRIES = 3
retry_count = 0

def scrape_job():
    """Scraping job with retry logic."""
    global retry_count

    try:
        # ... scraping logic ...
        retry_count = 0  # Reset on success

    except Exception as e:
        retry_count += 1
        logger.error(f"[Scheduler] Error (attempt {retry_count}/{MAX_RETRIES}): {e}")

        if retry_count < MAX_RETRIES:
            # Schedule retry in 10 minutes
            scheduler.add_job(
                scrape_job,
                trigger='date',
                run_date=datetime.now() + timedelta(minutes=10),
                id=f'retry_scrape_{retry_count}',
            )
        else:
            logger.error("[Scheduler] Max retries exceeded")
            retry_count = 0
```

### Performance Monitoring

```python
import time

def scrape_job():
    """Scraping job with performance tracking."""
    start_time = time.time()
    logger.info(f"[Scheduler] Starting automated scrape at {datetime.now()}")

    db: Session = SessionLocal()
    try:
        plans = powertochoose_scraper.scrape_powertochoose_all_texas()

        created_or_updated = 0
        for plan in plans:
            # ... process plans ...
            created_or_updated += 1

        duration = time.time() - start_time
        logger.info(
            f"[Scheduler] Successfully processed {created_or_updated} plans "
            f"in {duration:.2f} seconds"
        )

    except Exception as e:
        logger.error(f"[Scheduler] Error during scrape: {e}")
    finally:
        db.close()
```

## Troubleshooting

### Scheduler not starting

**Check logs:**
```bash
docker-compose logs backend | grep "Starting background scheduler"
```

**Verify lifespan is enabled:**
```python
# In main.py
app = FastAPI(
    lifespan=lifespan  # Must be set
)
```

### Jobs not running at scheduled time

**Check timezone:**
```python
from apscheduler.triggers.cron import CronTrigger
import pytz

scheduler.add_job(
    scrape_job,
    trigger=CronTrigger(
        hour=2,
        minute=0,
        timezone=pytz.timezone('America/Chicago')  # Explicit timezone
    ),
    id="daily_scrape",
)
```

**Verify scheduler is running:**
```bash
# Add to main.py
@app.get("/scheduler/status")
async def scheduler_status():
    from .scheduler import scheduler
    return {"running": scheduler.running}

# Check
curl http://localhost:8000/scheduler/status
```

### Scrape job failing silently

**Add better error handling:**
```python
def scrape_job():
    """Background job with detailed error logging."""
    db: Session = SessionLocal()
    try:
        logger.info(f"[Scheduler] Starting scrape at {datetime.now()}")

        plans = powertochoose_scraper.scrape_powertochoose_all_texas()
        logger.info(f"[Scheduler] Scraped {len(plans)} plans")

        # ... process plans ...

        logger.info(f"[Scheduler] Completed successfully")

    except Exception as e:
        logger.exception(f"[Scheduler] Fatal error during scrape: {e}")
        # Send alert, log to external service, etc.
    finally:
        db.close()
```

### Database locks during scrape

**Use separate database connection:**
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Dedicated engine for background jobs
background_engine = create_engine(
    os.getenv("DATABASE_URL"),
    pool_pre_ping=True,
    pool_recycle=3600,
)
BackgroundSession = sessionmaker(bind=background_engine)

def scrape_job():
    """Use dedicated connection pool."""
    db = BackgroundSession()
    try:
        # ... scraping logic ...
    finally:
        db.close()
```

## Testing

### Test Scheduler Locally

```python
# backend/test_scheduler.py
from app.scheduler import scrape_job

if __name__ == "__main__":
    print("Running scrape job manually...")
    scrape_job()
    print("Done!")
```

Run:
```bash
cd backend
.venv/Scripts/python test_scheduler.py
```

### Dry Run Mode

```python
# Add environment variable
DRY_RUN = os.getenv("SCHEDULER_DRY_RUN", "false").lower() == "true"

def scrape_job():
    """Scraping job with dry run support."""
    if DRY_RUN:
        logger.info("[Scheduler] DRY RUN - No data will be saved")

    # ... scraping logic ...

    if not DRY_RUN:
        db.commit()
    else:
        db.rollback()
        logger.info("[Scheduler] DRY RUN - Changes rolled back")
```

Test:
```bash
export SCHEDULER_DRY_RUN=true
python test_scheduler.py
```

## Best Practices

### 1. Log Everything
```python
logger.info(f"[Scheduler] Starting scrape at {datetime.now()}")
logger.info(f"[Scheduler] Scraped {len(plans)} plans")
logger.info(f"[Scheduler] Created/updated {count} records")
logger.info(f"[Scheduler] Completed in {duration:.2f}s")
```

### 2. Handle Errors Gracefully
```python
try:
    # Scraping logic
except Exception as e:
    logger.exception(f"[Scheduler] Error: {e}")
    # Don't crash the scheduler
```

### 3. Use Database Transactions
```python
try:
    # Multiple database operations
    db.commit()
except Exception:
    db.rollback()
    raise
```

### 4. Monitor Performance
```python
import time

start = time.time()
# ... work ...
duration = time.time() - start
logger.info(f"Completed in {duration:.2f}s")
```

### 5. Avoid Peak Hours
```python
# Scrape at 2 AM when traffic is low
trigger=CronTrigger(hour=2, minute=0)
```

## Summary

**Quick Reference:**

```python
# Default configuration (2 AM daily)
scheduler.add_job(
    scrape_job,
    trigger=CronTrigger(hour=2, minute=0),
    id="daily_scrape",
)

# Check status
curl http://localhost:8000/scheduler/status

# View logs
docker-compose logs -f backend | grep Scheduler

# Disable scheduler
# Remove lifespan=lifespan from FastAPI() call
```

**Common Schedules:**

| Schedule | Cron Expression |
|----------|----------------|
| Daily at 2 AM | `CronTrigger(hour=2, minute=0)` |
| Every hour | `CronTrigger(minute=0)` |
| Every 6 hours | `CronTrigger(hour='*/6', minute=0)` |
| Twice daily | Two separate jobs with different hours |
| Weekdays only | `CronTrigger(day_of_week='mon-fri', hour=2)` |
| First of month | `CronTrigger(day=1, hour=2, minute=0)` |
