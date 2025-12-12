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
from .database import SessionLocal, engine
from .scraping import scraper, energybot_scraper_v2, powertochoose_scraper  # REAL data scrapers
from .scraping.provider_urls import get_plan_url
from . import crud, schemas, models
from .data_validation import validate_plan_batch, log_validation_summary, get_data_quality_score

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
        # Ensure database tables exist (in case app started while DB was paused)
        try:
            models.Base.metadata.create_all(bind=engine)
            logger.info("[Scheduler] Verified/Created database tables")
        except Exception as db_err:
            logger.error(f"[Scheduler] Warning: Failed to verify tables: {db_err}")

        # 1. Scrape REAL residential plans
        logger.info("[Scheduler] Scraping REAL residential plans from PowerChoiceTexas...")
        residential_plans_raw = scraper.scrape_all()
        logger.info(f"[Scheduler] Retrieved {len(residential_plans_raw)} raw residential plans")

        # VALIDATE: Remove any fake/estimated data
        residential_plans, rejected_residential = validate_plan_batch(residential_plans_raw, strict=True)
        logger.info(f"[Scheduler] Validated: {len(residential_plans)} REAL residential plans accepted")
        if rejected_residential:
            logger.warning(f"[Scheduler] Rejected {len(rejected_residential)} residential plans with fake data markers")

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
                    existing.last_updated = datetime.utcnow()  # Force update timestamp
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

        # 2. Scrape REAL commercial plans
        if USE_ENHANCED_ENERGYBOT:
            logger.info("[Scheduler] Scraping REAL commercial plans from EnergyBot ENHANCED (full navigation)...")
            try:
                commercial_plans = energybot_business_enhanced.scrape_energybot_all_texas_enhanced()
                logger.info(f"[Scheduler] Retrieved {len(commercial_plans)} REAL commercial plans (enhanced)")
            except Exception as scraper_error:
                logger.error(f"[Scheduler] EnergyBot Enhanced scraper failed: {scraper_error}")
                import traceback
                logger.error(f"[Scheduler] EnergyBot Enhanced traceback: {traceback.format_exc()}")
                commercial_plans = []  # Continue with empty list
                logger.warning("[Scheduler] Continuing with 0 commercial plans due to enhanced scraper failure")
        else:
            logger.info("[Scheduler] Scraping REAL commercial plans from EnergyBot v2 (JSON-LD only)...")
            try:
                commercial_plans = energybot_scraper_v2.scrape_energybot_all_texas_v2()
                logger.info(f"[Scheduler] Retrieved {len(commercial_plans)} REAL commercial plans (v2)")
            except Exception as scraper_error:
                logger.error(f"[Scheduler] EnergyBot v2 scraper failed: {scraper_error}")
                import traceback
                logger.error(f"[Scheduler] EnergyBot v2 traceback: {traceback.format_exc()}")
                commercial_plans = []  # Continue with empty list
                logger.warning("[Scheduler] Continuing with 0 commercial plans due to v2 scraper failure")
        logger.info("[Scheduler] Scraping REAL commercial plans from EnergyBot...")
        commercial_plans_raw = energybot_scraper_v2.scrape_energybot_all_texas_v2()
        logger.info(f"[Scheduler] Retrieved {len(commercial_plans_raw)} raw commercial plans")

        # VALIDATE: Remove any fake/estimated data
        commercial_plans, rejected_commercial = validate_plan_batch(commercial_plans_raw, strict=True)
        logger.info(f"[Scheduler] Validated: {len(commercial_plans)} REAL commercial plans accepted")
        if rejected_commercial:
            logger.warning(f"[Scheduler] Rejected {len(rejected_commercial)} commercial plans with fake data markers")

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
                    existing.last_updated = datetime.utcnow()  # Force update timestamp
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

        # 3. Scrape REAL PowerToChoose plans
        logger.info("[Scheduler] Scraping REAL PowerToChoose plans...")
        ptc_plans_raw = powertochoose_scraper.scrape_powertochoose(zip_code="75001", service_type="Residential")
        logger.info(f"[Scheduler] Retrieved {len(ptc_plans_raw)} raw PowerToChoose plans")

        # VALIDATE: Remove any fake/estimated data
        ptc_plans, rejected_ptc = validate_plan_batch(ptc_plans_raw, strict=True)
        logger.info(f"[Scheduler] Validated: {len(ptc_plans)} REAL PowerToChoose plans accepted")
        if rejected_ptc:
            logger.warning(f"[Scheduler] Rejected {len(rejected_ptc)} PowerToChoose plans with fake data markers")

        for plan_data in ptc_plans:
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
                plan_url = plan_data.get("fact_sheet_url") or get_plan_url(provider_name, plan_data.get("plan_name"))

                # Create plan object
                plan_create = schemas.PlanCreate(
                    provider_id=provider.id,
                    plan_name=plan_data["plan_name"],
                    plan_url=plan_url,
                    plan_type=plan_data.get("plan_type", "Fixed"),
                    service_type="Residential",
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
                    existing.last_updated = datetime.utcnow()  # Force update timestamp
                    total_updated += 1
                else:
                    # Create new plan
                    crud.create_or_update_plan(db, provider.id, plan_create)
                    total_added += 1

            except Exception as e:
                logger.error(f"[Scheduler] Error processing PowerToChoose plan: {e}")
                continue

        logger.info(f"[Scheduler] PowerToChoose: {total_added} added (cumulative), {total_updated} updated (cumulative)")

        db.commit()
        logger.info(f"[Scheduler] SUCCESS! Total: {total_added} added, {total_updated} updated")
        logger.info(f"[Scheduler] ALL DATA IS REAL - NO SAMPLES")

        # Log validation summary
        log_validation_summary(
            plans_before=len(residential_plans_raw) + len(commercial_plans_raw) + len(ptc_plans_raw),
            plans_after=len(residential_plans) + len(commercial_plans) + len(ptc_plans),
            rejected=rejected_residential + rejected_commercial + rejected_ptc
        )

        # Calculate and log data quality score
        all_valid_plans = residential_plans + commercial_plans + ptc_plans
        if all_valid_plans:
            quality_metrics = get_data_quality_score(all_valid_plans)
            logger.info(f"[Scheduler] Data Quality Score: {quality_metrics['quality_score']}%")
            logger.info(f"[Scheduler] Quality Issues: {', '.join(quality_metrics['issues'])}")

        # Send email notification after successful scrape
        logger.info("[Scheduler] Sending daily email report...")
        try:
            from .email_notifications import send_daily_report
            email_sent = send_daily_report(db)
            if email_sent:
                logger.info("[Scheduler] ✓ Daily email report sent successfully")
            else:
                logger.warning("[Scheduler] ⚠ Daily email report not sent (check REPORT_EMAIL config)")
        except Exception as email_error:
            logger.error(f"[Scheduler] Failed to send email report: {email_error}")
            # Don't fail the whole scrape job if email fails

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
    - DAILY at 3:00 AM: Scrape fresh real data

    NOTE: Startup scraping is DISABLED to prevent Railway healthcheck timeouts.
    Use the /admin/delete-fake-commercial-plans endpoint or /plans/scrape for manual data loading.

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

    # Start scheduler
    scheduler.start()
    logger.info("[Scheduler] [OK] Daily job scheduled: 3:00 AM scrape REAL data")
    
    # Schedule an immediate scrape (2 minutes from now) to ensure fresh data on deployment
    run_date = datetime.now()
    from datetime import timedelta
    run_date += timedelta(minutes=2)
    scheduler.add_job(
        scrape_real_data_job,
        'date',
        run_date=run_date,
        id='startup_scrape',
        name='Startup Data Refresh'
    )
    logger.info(f"[Scheduler] [INFO] Scheduled startup data refresh for {run_date}")


def stop_scheduler():
    """Stop the background scheduler."""
    scheduler.shutdown()
    logger.info("[Scheduler] Background scheduler stopped")
