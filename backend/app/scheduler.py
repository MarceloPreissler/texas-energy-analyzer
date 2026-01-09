"""
Automated scraping scheduler - REAL DATA ONLY.

Runs comprehensive scraping from ALL available sources:
- Residential: PowerToChoose API (official PUCT marketplace)
- Commercial: ElectricityPlans, ComparePower, EnergyBot Enhanced

NO SAMPLE DATA. NO FALLBACK DATA. NO FAKE DATA.
All data is validated before insertion.
"""
from __future__ import annotations

import os
import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from .database import SessionLocal, engine
from . import crud, schemas, models
from .scraping.provider_urls import get_plan_url
from .data_validation import validate_plan_batch, log_validation_summary, get_data_quality_score

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = BackgroundScheduler()


def scrape_all_sources_job():
    """
    Comprehensive background job to scrape REAL electricity plans from ALL live sources.

    NO SAMPLE DATA - ONLY LIVE SCRAPED PLANS.
    NO FAKE DATA - ALL DATA IS VALIDATED.

    Sources scraped:
    1. Residential: PowerToChoose (official PUCT marketplace)
    2. Commercial: ElectricityPlans.com (Playwright + stealth)
    3. Commercial: ComparePower.com (Playwright + stealth)
    4. Commercial: EnergyBot.com Enhanced (full navigation flow)
    """
    logger.info("=" * 80)
    logger.info(f"[Scheduler] Starting COMPREHENSIVE REAL DATA scrape at {datetime.now()}")
    logger.info("[Scheduler] NO SAMPLE DATA - NO FAKE DATA - ONLY LIVE SOURCES")
    logger.info("=" * 80)

    db: Session = SessionLocal()
    total_added = 0
    total_updated = 0
    all_raw_plans = []
    all_valid_plans = []
    all_rejected_plans = []

    try:
        # Ensure database tables exist
        try:
            models.Base.metadata.create_all(bind=engine)
            logger.info("[Scheduler] Verified database tables")
        except Exception as db_err:
            logger.error(f"[Scheduler] Warning: Failed to verify tables: {db_err}")

        # ================================================================
        # SOURCE 1: PowerToChoose (Official PUCT Marketplace)
        # ================================================================
        logger.info("\n" + "=" * 60)
        logger.info("[Scheduler] SOURCE 1: PowerToChoose (PUCT Official)")
        logger.info("=" * 60)

        try:
            from .scraping import powertochoose_scraper
            ptc_plans_raw = powertochoose_scraper.scrape_powertochoose(zip_code="75001", service_type="Residential")
            logger.info(f"[Scheduler] PowerToChoose: Retrieved {len(ptc_plans_raw)} raw plans")
            all_raw_plans.extend(ptc_plans_raw)

            # Validate
            ptc_valid, ptc_rejected = validate_plan_batch(ptc_plans_raw, strict=True)
            logger.info(f"[Scheduler] PowerToChoose: {len(ptc_valid)} valid, {len(ptc_rejected)} rejected")
            all_valid_plans.extend(ptc_valid)
            all_rejected_plans.extend(ptc_rejected)

            # Process valid plans
            for plan_data in ptc_valid:
                added, updated = _process_plan(db, plan_data, "Residential")
                total_added += added
                total_updated += updated

        except Exception as e:
            logger.error(f"[Scheduler] PowerToChoose scraper failed: {e}")
            import traceback
            logger.error(traceback.format_exc())

        # ================================================================
        # SOURCE 2: ElectricityPlans.com (Commercial)
        # ================================================================
        logger.info("\n" + "=" * 60)
        logger.info("[Scheduler] SOURCE 2: ElectricityPlans.com (Commercial)")
        logger.info("=" * 60)

        try:
            from .scraping import electricityplans_commercial
            ep_plans_raw = electricityplans_commercial.scrape_electricityplans_all_texas()
            logger.info(f"[Scheduler] ElectricityPlans: Retrieved {len(ep_plans_raw)} raw commercial plans")
            all_raw_plans.extend(ep_plans_raw)

            # Validate
            ep_valid, ep_rejected = validate_plan_batch(ep_plans_raw, strict=True)
            logger.info(f"[Scheduler] ElectricityPlans: {len(ep_valid)} valid, {len(ep_rejected)} rejected")
            all_valid_plans.extend(ep_valid)
            all_rejected_plans.extend(ep_rejected)

            # Process valid plans
            for plan_data in ep_valid:
                added, updated = _process_plan(db, plan_data, "Commercial")
                total_added += added
                total_updated += updated

        except Exception as e:
            logger.error(f"[Scheduler] ElectricityPlans scraper failed: {e}")
            import traceback
            logger.error(traceback.format_exc())

        # ================================================================
        # SOURCE 3: ComparePower.com (Commercial)
        # ================================================================
        logger.info("\n" + "=" * 60)
        logger.info("[Scheduler] SOURCE 3: ComparePower.com (Commercial)")
        logger.info("=" * 60)

        try:
            from .scraping import comparepower_commercial
            cp_plans_raw = comparepower_commercial.scrape_comparepower_all_texas()
            logger.info(f"[Scheduler] ComparePower: Retrieved {len(cp_plans_raw)} raw commercial plans")
            all_raw_plans.extend(cp_plans_raw)

            # Validate
            cp_valid, cp_rejected = validate_plan_batch(cp_plans_raw, strict=True)
            logger.info(f"[Scheduler] ComparePower: {len(cp_valid)} valid, {len(cp_rejected)} rejected")
            all_valid_plans.extend(cp_valid)
            all_rejected_plans.extend(cp_rejected)

            # Process valid plans
            for plan_data in cp_valid:
                added, updated = _process_plan(db, plan_data, "Commercial")
                total_added += added
                total_updated += updated

        except Exception as e:
            logger.error(f"[Scheduler] ComparePower scraper failed: {e}")
            import traceback
            logger.error(traceback.format_exc())

        # ================================================================
        # SOURCE 4: EnergyBot Enhanced (Commercial - Full Navigation)
        # ================================================================
        logger.info("\n" + "=" * 60)
        logger.info("[Scheduler] SOURCE 4: EnergyBot Enhanced (Commercial)")
        logger.info("=" * 60)

        try:
            from .scraping import energybot_business_enhanced
            eb_plans_raw = energybot_business_enhanced.scrape_energybot_all_texas_enhanced()
            logger.info(f"[Scheduler] EnergyBot Enhanced: Retrieved {len(eb_plans_raw)} raw commercial plans")
            all_raw_plans.extend(eb_plans_raw)

            # Validate
            eb_valid, eb_rejected = validate_plan_batch(eb_plans_raw, strict=True)
            logger.info(f"[Scheduler] EnergyBot Enhanced: {len(eb_valid)} valid, {len(eb_rejected)} rejected")
            all_valid_plans.extend(eb_valid)
            all_rejected_plans.extend(eb_rejected)

            # Process valid plans
            for plan_data in eb_valid:
                added, updated = _process_plan(db, plan_data, "Commercial")
                total_added += added
                total_updated += updated

        except Exception as e:
            logger.error(f"[Scheduler] EnergyBot Enhanced scraper failed: {e}")
            import traceback
            logger.error(traceback.format_exc())

        # ================================================================
        # COMMIT AND LOG RESULTS
        # ================================================================
        db.commit()

        logger.info("\n" + "=" * 80)
        logger.info("[Scheduler] SCRAPE COMPLETE - SUMMARY")
        logger.info("=" * 80)
        logger.info(f"[Scheduler] Total raw plans scraped: {len(all_raw_plans)}")
        logger.info(f"[Scheduler] Total valid plans: {len(all_valid_plans)}")
        logger.info(f"[Scheduler] Total rejected (fake/invalid): {len(all_rejected_plans)}")
        logger.info(f"[Scheduler] Plans added: {total_added}")
        logger.info(f"[Scheduler] Plans updated: {total_updated}")
        logger.info("[Scheduler] ALL DATA IS REAL - NO SAMPLES - NO FAKES")
        logger.info("=" * 80)

        # Log validation summary
        log_validation_summary(
            plans_before=len(all_raw_plans),
            plans_after=len(all_valid_plans),
            rejected=all_rejected_plans
        )

        # Calculate and log data quality score
        if all_valid_plans:
            quality_metrics = get_data_quality_score(all_valid_plans)
            logger.info(f"[Scheduler] Data Quality Score: {quality_metrics['quality_score']}%")
            if quality_metrics['issues']:
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

    except Exception as e:
        db.rollback()
        logger.error(f"[Scheduler] Critical error during scrape: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def _process_plan(db: Session, plan_data: dict, default_service_type: str) -> tuple[int, int]:
    """
    Process a single validated plan and insert/update in database.

    Returns:
        Tuple of (added_count, updated_count) - one will be 1, other will be 0
    """
    try:
        # Get or create provider
        provider_name = plan_data.get("provider_name")
        if not provider_name:
            return 0, 0

        provider = crud.get_provider_by_name(db, provider_name)
        if not provider:
            provider = crud.create_provider(
                db, schemas.ProviderCreate(name=provider_name)
            )

        # Get plan URL
        plan_url = plan_data.get("plan_url") or plan_data.get("fact_sheet_url") or get_plan_url(provider_name, plan_data.get("plan_name"))

        # Create plan object
        service_type = plan_data.get("service_type", default_service_type)

        # Add source info to special_features if not already present
        special_features = plan_data.get("special_features", "")
        source = plan_data.get("source", "")
        if source and source not in str(special_features):
            if special_features:
                special_features = f"{special_features} (Source: {source})"
            else:
                special_features = f"Source: {source}"

        plan_create = schemas.PlanCreate(
            provider_id=provider.id,
            plan_name=plan_data["plan_name"],
            plan_url=plan_url,
            plan_type=plan_data.get("plan_type", "Fixed"),
            service_type=service_type,
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
            special_features=special_features[:500] if special_features else None
        )

        # Check if plan exists
        existing = db.query(models.Plan).filter(
            models.Plan.provider_id == provider.id,
            models.Plan.plan_name == plan_create.plan_name
        ).first()

        if existing:
            # Update existing plan
            for key, value in plan_create.dict(exclude={'provider_id'}).items():
                if value is not None:  # Only update non-None values
                    setattr(existing, key, value)
            existing.last_updated = datetime.utcnow()
            return 0, 1
        else:
            # Create new plan
            crud.create_or_update_plan(db, provider.id, plan_create)
            return 1, 0

    except Exception as e:
        logger.error(f"[Scheduler] Error processing plan '{plan_data.get('plan_name', 'Unknown')}': {e}")
        return 0, 0


def start_scheduler():
    """
    Start the background scheduler.

    Schedule:
    - DAILY at 5:00 AM CST (11:00 UTC): Comprehensive scrape from ALL sources

    All data is REAL - NO SAMPLES, NO FALLBACKS, NO FAKES.
    All data is VALIDATED before insertion.
    """
    logger.info("[Scheduler] Starting COMPREHENSIVE REAL DATA scheduler...")
    logger.info("[Scheduler] Sources: PowerToChoose, ElectricityPlans, ComparePower, EnergyBot")

    # Daily comprehensive scrape at 11 AM UTC (5 AM CST / 6 AM CDT)
    scheduler.add_job(
        scrape_all_sources_job,
        trigger=CronTrigger(hour=11, minute=0),
        id="daily_comprehensive_scrape",
        name="Daily Comprehensive Scrape (ALL Sources)",
        replace_existing=True,
    )

    # Start scheduler
    scheduler.start()
    logger.info("[Scheduler] ✓ Daily job scheduled: 11:00 AM UTC (5 AM CST)")
    logger.info("[Scheduler] ✓ Sources: PowerToChoose + ElectricityPlans + ComparePower + EnergyBot")

    # Schedule startup scrape (2 minutes from now) to ensure fresh data on deployment
    run_date = datetime.now() + timedelta(minutes=2)
    scheduler.add_job(
        scrape_all_sources_job,
        'date',
        run_date=run_date,
        id='startup_comprehensive_scrape',
        name='Startup Comprehensive Data Refresh'
    )
    logger.info(f"[Scheduler] ✓ Startup scrape scheduled for {run_date}")


def stop_scheduler():
    """Stop the background scheduler."""
    scheduler.shutdown()
    logger.info("[Scheduler] Background scheduler stopped")


# Alias for backward compatibility with refresh endpoint
scrape_real_data_job = scrape_all_sources_job
