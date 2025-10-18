"""
Automated scraping scheduler - REAL DATA ONLY.

Runs daily scraping of REAL data from live sources:
- Residential: PowerChoiceTexas sites (68+ plans)
- Commercial: EnergyBot JSON-LD (5+ plans)

NO SAMPLE DATA. NO FALLBACK DATA.
"""
from __future__ import annotations

import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from .database import SessionLocal
from .scraping import scraper, energybot_scraper_v2  # REAL data scrapers
from .scraping.provider_urls import get_plan_url
from . import crud, schemas

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = BackgroundScheduler()


def scrape_real_data_job():
    """
    Background job to scrape REAL electricity plans from live sources.

    NO SAMPLE DATA - ONLY LIVE SCRAPED PLANS.

    Sources:
    - Residential: Legacy scraper (PowerChoiceTexas, provider sites)
    - Commercial: EnergyBot v2 (JSON-LD structured data)
    """
    logger.info(f"[Scheduler] Starting REAL DATA scrape at {datetime.now()}")
    logger.info("[Scheduler] NO SAMPLE DATA - ONLY LIVE SOURCES")

    db: Session = SessionLocal()
    total_added = 0
    total_updated = 0

    try:
        # 1. Scrape REAL residential plans
        logger.info("[Scheduler] Scraping REAL residential plans from PowerChoiceTexas...")
        residential_plans = scraper.scrape_all()
        logger.info(f"[Scheduler] Retrieved {len(residential_plans)} REAL residential plans")

        for plan_data in residential_plans:
            try:
                # Get or create provider
                provider_name = plan_data.get("provider_name")
                if not provider_name:
                    continue

                provider = crud.get_provider_by_name(db, provider_name)
                if not provider:
                    provider = crud.create_provider(
                        db, schemas.ProviderCreate(name=provider_name)
                    )

                # Get plan URL
                plan_url = get_plan_url(provider_name, plan_data.get("plan_name"))

                # Create plan object
                plan_create = schemas.PlanCreate(
                    provider_id=provider.id,
                    plan_name=plan_data["plan_name"],
                    plan_url=plan_url,
                    plan_type=plan_data.get("plan_type", "Fixed"),
                    service_type=plan_data.get("service_type", "Residential"),
                    zip_code=plan_data.get("zip_code", "75001"),
                    contract_months=plan_data.get("contract_months"),
                    rate_500_cents=plan_data.get("rate_500_cents"),
                    rate_1000_cents=plan_data.get("rate_1000_cents"),
                    rate_2000_cents=plan_data.get("rate_2000_cents"),
                    monthly_bill_1000=plan_data.get("monthly_bill_1000"),
                    monthly_bill_2000=plan_data.get("monthly_bill_2000"),
                    early_termination_fee=plan_data.get("early_termination_fee", 0.0),
                    base_monthly_fee=plan_data.get("base_monthly_fee", 0.0),
                    renewable_percent=plan_data.get("renewable_percent", 0.0),
                    special_features=plan_data.get("special_features", "")
                )

                # Check if plan exists
                from .models import Plan
                existing = db.query(Plan).filter(
                    Plan.provider_id == provider.id,
                    Plan.plan_name == plan_create.plan_name
                ).first()

                if existing:
                    # Update existing plan
                    for key, value in plan_create.dict(exclude={'provider_id'}).items():
                        setattr(existing, key, value)
                    total_updated += 1
                else:
                    # Create new plan
                    crud.create_or_update_plan(db, provider.id, plan_create)
                    total_added += 1

            except Exception as e:
                logger.error(f"[Scheduler] Error processing residential plan: {e}")
                continue

        logger.info(f"[Scheduler] Residential: {total_added} added, {total_updated} updated")

        # 2. Scrape REAL commercial plans
        logger.info("[Scheduler] Scraping REAL commercial plans from EnergyBot...")
        commercial_plans = energybot_scraper_v2.scrape_energybot_all_texas_v2()
        logger.info(f"[Scheduler] Retrieved {len(commercial_plans)} REAL commercial plans")

        for plan_data in commercial_plans:
            try:
                # Get or create provider
                provider_name = plan_data.get("provider_name")
                if not provider_name:
                    continue

                provider = crud.get_provider_by_name(db, provider_name)
                if not provider:
                    provider = crud.create_provider(
                        db, schemas.ProviderCreate(name=provider_name)
                    )

                # Get plan URL
                plan_url = get_plan_url(provider_name, plan_data.get("plan_name"))

                # Create plan object
                plan_create = schemas.PlanCreate(
                    provider_id=provider.id,
                    plan_name=plan_data["plan_name"],
                    plan_url=plan_url,
                    plan_type=plan_data.get("plan_type", "Fixed"),
                    service_type="Commercial",
                    zip_code=plan_data.get("zip_code", "75001"),
                    contract_months=plan_data.get("contract_months"),
                    rate_500_cents=plan_data.get("rate_500_cents"),
                    rate_1000_cents=plan_data.get("rate_1000_cents"),
                    rate_2000_cents=plan_data.get("rate_2000_cents"),
                    monthly_bill_1000=plan_data.get("monthly_bill_1000"),
                    monthly_bill_2000=plan_data.get("monthly_bill_2000"),
                    early_termination_fee=plan_data.get("early_termination_fee", 0.0),
                    base_monthly_fee=plan_data.get("base_monthly_fee", 0.0),
                    renewable_percent=plan_data.get("renewable_percent", 0.0),
                    special_features=plan_data.get("special_features", "")
                )

                # Check if plan exists
                from .models import Plan
                existing = db.query(Plan).filter(
                    Plan.provider_id == provider.id,
                    Plan.plan_name == plan_create.plan_name
                ).first()

                if existing:
                    # Update existing plan
                    for key, value in plan_create.dict(exclude={'provider_id'}).items():
                        setattr(existing, key, value)
                    total_updated += 1
                else:
                    # Create new plan
                    crud.create_or_update_plan(db, provider.id, plan_create)
                    total_added += 1

            except Exception as e:
                logger.error(f"[Scheduler] Error processing commercial plan: {e}")
                continue

        logger.info(f"[Scheduler] Commercial: {total_added} added, {total_updated} updated")

        db.commit()
        logger.info(f"[Scheduler] SUCCESS! Total: {total_added} added, {total_updated} updated")
        logger.info(f"[Scheduler] ALL DATA IS REAL - NO SAMPLES")

    except Exception as e:
        db.rollback()
        logger.error(f"[Scheduler] Error during scrape: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def delete_sample_data_and_load_real():
    """
    ONE-TIME startup job: Delete all sample data and load real data.

    This runs once on application startup to ensure production
    starts with REAL data only.
    """
    logger.info("[Startup] Deleting sample data and loading REAL plans...")

    db: Session = SessionLocal()

    try:
        # Delete ALL existing plans (sample data)
        from .models import Plan
        deleted_count = db.query(Plan).delete()
        db.commit()
        logger.info(f"[Startup] Deleted {deleted_count} sample plans")

        # Run the scraper to load real data
        scrape_real_data_job()

        logger.info("[Startup] REAL data loaded successfully!")

    except Exception as e:
        db.rollback()
        logger.error(f"[Startup] Error during initialization: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def start_scheduler():
    """
    Start the background scheduler.

    Schedule:
    - STARTUP: Delete sample data, load real data (runs in background)
    - DAILY at 3:00 AM: Scrape fresh real data

    All data is REAL - NO SAMPLES, NO FALLBACKS.
    """
    logger.info("[Scheduler] Starting automated REAL DATA scheduler...")

    # Daily scrape at 3 AM - REAL DATA ONLY
    scheduler.add_job(
        scrape_real_data_job,
        trigger=CronTrigger(hour=3, minute=0),
        id="daily_real_data_scrape",
        name="Daily REAL Data Scrape (Residential + Commercial)",
        replace_existing=True,
    )

    # Start scheduler FIRST so app can finish startup
    scheduler.start()
    logger.info("[Scheduler] [OK] Daily job: 3:00 AM scrape REAL data")
    logger.info("[Scheduler] NO SAMPLE DATA - ONLY LIVE SOURCES")

    # Run startup data load in background (non-blocking)
    # This allows the app to finish startup and pass healthchecks
    # while data is being loaded in the background
    scheduler.add_job(
        delete_sample_data_and_load_real,
        trigger='date',
        id='startup_real_data_load',
        name='Startup: Load REAL Data',
        replace_existing=True
    )
    logger.info("[Scheduler] [OK] Startup job scheduled: Load REAL data in background")


def stop_scheduler():
    """Stop the background scheduler."""
    scheduler.shutdown()
    logger.info("[Scheduler] Background scheduler stopped")
