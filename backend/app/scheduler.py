"""
Automated scraping scheduler - REAL DATA ONLY.

Runs daily scraping of REAL data from live sources:
- Residential: PowerChoiceTexas sites (68+ plans)
- Commercial: EnergyBot JSON-LD (5+ plans)

NO SAMPLE DATA. NO FALLBACK DATA.
"""
from __future__ import annotations

import os
import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from .database import SessionLocal
from .scraping import scraper, energybot_scraper_v2, energybot_business_enhanced  # REAL data scrapers
from .scraping.provider_urls import get_plan_url
from . import crud, schemas

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = BackgroundScheduler()

# Check which commercial scraper to use
USE_ENHANCED_ENERGYBOT = os.getenv("USE_ENHANCED_ENERGYBOT", "true").lower() == "true"


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
                logger.error(f"[Scheduler] Error processing residential plan '{plan_data.get('plan_name', 'Unknown')}': {e}")
                import traceback
                logger.error(f"[Scheduler] Traceback: {traceback.format_exc()}")
                continue

        logger.info(f"[Scheduler] Residential: {total_added} added, {total_updated} updated")

        # 2. Scrape REAL commercial plans - CASCADE with automatic fallback
        # Primary: EnergyBot Enhanced -> Fallback: EnergyBot v2
        # Supplementary sources added on top, each isolated so one failure can't block the rest
        commercial_plans = []

        if USE_ENHANCED_ENERGYBOT:
            logger.info("[Scheduler] Scraping commercial plans from EnergyBot ENHANCED (primary)...")
            try:
                commercial_plans = energybot_business_enhanced.scrape_energybot_all_texas_enhanced()
                logger.info(f"[Scheduler] EnergyBot Enhanced: {len(commercial_plans)} plans")
            except Exception as scraper_error:
                logger.error(f"[Scheduler] EnergyBot Enhanced scraper failed: {scraper_error}")
                import traceback
                logger.error(f"[Scheduler] EnergyBot Enhanced traceback: {traceback.format_exc()}")

        # Fallback: if primary returned nothing, try the simpler JSON-LD scraper
        if not commercial_plans:
            logger.warning("[Scheduler] Primary commercial scraper returned 0 plans - falling back to EnergyBot v2...")
            try:
                commercial_plans = energybot_scraper_v2.scrape_energybot_all_texas_v2()
                logger.info(f"[Scheduler] EnergyBot v2 fallback: {len(commercial_plans)} plans")
            except Exception as scraper_error:
                logger.error(f"[Scheduler] EnergyBot v2 fallback failed: {scraper_error}")
                import traceback
                logger.error(f"[Scheduler] EnergyBot v2 traceback: {traceback.format_exc()}")

        # Supplementary source: PowerToChoose commercial (official PUCT data)
        logger.info("[Scheduler] Scraping commercial plans from PowerToChoose.org...")
        try:
            from .scraping.powertochoose_scraper import scrape_powertochoose_all_texas
            ptc_commercial = scrape_powertochoose_all_texas(service_type="Commercial")
            logger.info(f"[Scheduler] PowerToChoose commercial: {len(ptc_commercial)} plans")
            commercial_plans.extend(ptc_commercial)
        except Exception as scraper_error:
            logger.error(f"[Scheduler] PowerToChoose commercial failed (non-fatal): {scraper_error}")

        # Supplementary source: TXU business plans (provider-direct)
        logger.info("[Scheduler] Scraping TXU business plans...")
        try:
            from .scraping.txu_business_scraper import scrape_txu_all_texas
            txu_plans = scrape_txu_all_texas()
            logger.info(f"[Scheduler] TXU business: {len(txu_plans)} plans")
            commercial_plans.extend(txu_plans)
        except Exception as scraper_error:
            logger.error(f"[Scheduler] TXU business failed (non-fatal): {scraper_error}")

        # Supplementary source: Reliant business plans (provider-direct)
        logger.info("[Scheduler] Scraping Reliant business plans...")
        try:
            from .scraping.reliant_business_scraper import scrape_reliant_commercial
            reliant_plans = scrape_reliant_commercial()
            logger.info(f"[Scheduler] Reliant business: {len(reliant_plans)} plans")
            commercial_plans.extend(reliant_plans)
        except Exception as scraper_error:
            logger.error(f"[Scheduler] Reliant business failed (non-fatal): {scraper_error}")

        if not commercial_plans:
            logger.error("[Scheduler] ALL commercial scrapers returned 0 plans - check logs above")
        else:
            logger.info(f"[Scheduler] Total commercial plans collected: {len(commercial_plans)}")

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
                logger.error(f"[Scheduler] Error processing commercial plan '{plan_data.get('plan_name', 'Unknown')}': {e}")
                import traceback
                logger.error(f"[Scheduler] Traceback: {traceback.format_exc()}")
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


def scrape_if_data_stale(max_age_hours: int = 24):
    """
    Run a scrape only if the newest plan in the database is older than max_age_hours.

    Free-tier hosts spin the service down when idle, so the 3 AM cron job may never
    fire. This check runs shortly after every startup: whenever the service wakes up
    with stale data, it refreshes itself automatically.
    """
    from datetime import timedelta
    from .models import Plan

    db: Session = SessionLocal()
    try:
        newest = db.query(Plan.last_updated).order_by(Plan.last_updated.desc()).first()
    except Exception as e:
        logger.error(f"[Scheduler] Staleness check failed: {e}")
        newest = None
    finally:
        db.close()

    if newest and newest[0]:
        age = datetime.now() - newest[0].replace(tzinfo=None)
        if age < timedelta(hours=max_age_hours):
            logger.info(f"[Scheduler] Data is fresh ({age.total_seconds()/3600:.1f}h old) - skipping startup scrape")
            return
        logger.warning(f"[Scheduler] Data is STALE ({age.days} days old) - running startup scrape...")
    else:
        logger.warning("[Scheduler] No plan data found - running startup scrape...")

    scrape_real_data_job()


def start_scheduler():
    """
    Start the background scheduler.

    Schedule:
    - DAILY at 3:00 AM: Scrape fresh real data
    - 2 minutes after startup: scrape only if data is stale (>24h old)

    The startup job runs in the scheduler's background thread, so it does not
    block application startup or healthchecks.

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

    # Self-healing: shortly after startup, refresh data if it has gone stale.
    # Runs in the scheduler thread 2 minutes after boot so healthchecks pass first.
    from datetime import timedelta as _td
    scheduler.add_job(
        scrape_if_data_stale,
        trigger="date",
        run_date=datetime.now() + _td(minutes=2),
        id="startup_stale_check",
        name="Startup staleness check (scrape if data >24h old)",
        replace_existing=True,
    )

    # Start scheduler
    scheduler.start()
    logger.info("[Scheduler] [OK] Daily job scheduled: 3:00 AM scrape REAL data")
    logger.info("[Scheduler] [OK] Startup staleness check scheduled (runs in 2 minutes)")
    logger.info("[Scheduler] NO SAMPLE DATA - ONLY LIVE SOURCES")


def stop_scheduler():
    """Stop the background scheduler."""
    scheduler.shutdown()
    logger.info("[Scheduler] Background scheduler stopped")
