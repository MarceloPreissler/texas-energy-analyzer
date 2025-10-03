"""
Automated scraping scheduler using APScheduler.

Runs PowerToChoose scraper daily at 2 AM to keep data fresh.
"""
from __future__ import annotations

import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from .database import SessionLocal
from .scraping import powertochoose_scraper
from . import crud, schemas

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = BackgroundScheduler()


def scrape_job():
    """
    Background job to scrape PowerToChoose.org data.

    Runs automatically at configured intervals.
    """
    logger.info(f"[Scheduler] Starting automated scrape at {datetime.now()}")

    db: Session = SessionLocal()
    try:
        # Scrape live data from PowerToChoose
        plans = powertochoose_scraper.scrape_powertochoose_all_texas()

        created_or_updated = 0
        for plan in plans:
            provider_name = plan.pop("provider_name")
            provider = crud.get_provider_by_name(db, provider_name)
            if not provider:
                provider = crud.create_provider(
                    db, schemas.ProviderCreate(name=provider_name)
                )
            plan_create = schemas.PlanCreate(provider_id=provider.id, **plan)
            crud.create_or_update_plan(db, provider.id, plan_create)
            created_or_updated += 1

        logger.info(f"[Scheduler] Successfully processed {created_or_updated} plans")

    except Exception as e:
        logger.error(f"[Scheduler] Error during scrape: {e}")
    finally:
        db.close()


def start_scheduler():
    """
    Start the background scheduler.

    Schedule:
    - Daily at 2:00 AM: Full PowerToChoose scrape
    - Can add more jobs as needed
    """
    # Daily scrape at 2 AM
    scheduler.add_job(
        scrape_job,
        trigger=CronTrigger(hour=2, minute=0),
        id="daily_scrape",
        name="PowerToChoose Daily Scrape",
        replace_existing=True,
    )

    # Optional: Run immediately on startup (uncomment if needed)
    # scheduler.add_job(
    #     scrape_job,
    #     trigger='date',
    #     id='startup_scrape',
    #     name='Startup Scrape'
    # )

    scheduler.start()
    logger.info("[Scheduler] Background scheduler started. Next run: 2:00 AM")


def stop_scheduler():
    """Stop the background scheduler."""
    scheduler.shutdown()
    logger.info("[Scheduler] Background scheduler stopped")
