"""
Admin API endpoints for data management.
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from .. import crud, schemas
from ..database import get_db
from .comprehensive_plans import COMPREHENSIVE_PLANS
from ..data_validation import validate_plan_batch, get_data_quality_score

router = APIRouter(prefix="/admin", tags=["admin"])

# Use comprehensive plan list (120+ plans)
SAMPLE_PLANS = COMPREHENSIVE_PLANS


@router.post("/emergency-fix")
def emergency_fix(db: Session = Depends(get_db)):
    """
    EMERGENCY FIX - Force migrations and load real data immediately.

    This endpoint will:
    1. Force database migrations
    2. Scrape real data (residential + commercial)
    3. Load into database
    4. Return status

    Use this when nothing is working and you need data NOW.
    """
    import logging
    logger = logging.getLogger(__name__)

    results = {
        "migrations": "pending",
        "residential_scrape": "pending",
        "commercial_scrape": "pending",
        "data_load": "pending",
        "final_counts": {}
    }

    try:
        # Step 1: Force migrations
        logger.info("[EMERGENCY] Running migrations...")
        from ..migrations import run_migrations
        run_migrations(db)
        results["migrations"] = "success"
        logger.info("[EMERGENCY] Migrations completed")

    except Exception as e:
        results["migrations"] = f"failed: {str(e)}"
        logger.error(f"[EMERGENCY] Migration failed: {e}")

    try:
        # Step 2: Scrape residential (quick - 68 plans)
        logger.info("[EMERGENCY] Scraping residential...")
        from ..scraping import scraper
        residential_plans = scraper.scrape_all()
        results["residential_scrape"] = f"success ({len(residential_plans)} plans)"
        logger.info(f"[EMERGENCY] Scraped {len(residential_plans)} residential plans")

        # Load residential into DB
        loaded_res = 0
        for plan_data in residential_plans:
            try:
                provider_name = plan_data.get("provider_name")
                if not provider_name:
                    continue

                provider = crud.get_provider_by_name(db, provider_name)
                if not provider:
                    provider = crud.create_provider(db, schemas.ProviderCreate(name=provider_name))

                plan_create = schemas.PlanCreate(
                    provider_id=provider.id,
                    plan_name=plan_data.get("plan_name", "Unknown"),
                    plan_url=plan_data.get("plan_url"),
                    plan_type=plan_data.get("plan_type", "Fixed"),
                    service_type="Residential",
                    zip_code=plan_data.get("zip_code", "75001"),
                    contract_months=plan_data.get("contract_months"),
                    rate_1000_cents=plan_data.get("rate_1000_cents"),
                    rate_500_cents=plan_data.get("rate_500_cents"),
                    rate_2000_cents=plan_data.get("rate_2000_cents"),
                )

                crud.create_or_update_plan(db, provider.id, plan_create)
                loaded_res += 1
            except Exception as e:
                logger.warning(f"[EMERGENCY] Error loading residential plan: {e}")
                continue

        db.commit()
        results["data_load"] = f"residential: {loaded_res} plans loaded"
        logger.info(f"[EMERGENCY] Loaded {loaded_res} residential plans")

    except Exception as e:
        results["residential_scrape"] = f"failed: {str(e)}"
        logger.error(f"[EMERGENCY] Residential scrape failed: {e}")

    try:
        # Step 3: Scrape commercial (1 ZIP for speed - Dallas)
        logger.info("[EMERGENCY] Scraping commercial (Dallas only for speed)...")
        from ..scraping.energybot_business_enhanced import scrape_energybot_business_enhanced
        commercial_plans = scrape_energybot_business_enhanced("75214", "ONCOR", "Dallas")
        results["commercial_scrape"] = f"success ({len(commercial_plans)} plans)"
        logger.info(f"[EMERGENCY] Scraped {len(commercial_plans)} commercial plans")

        # Load commercial into DB
        loaded_com = 0
        for plan_data in commercial_plans:
            try:
                provider_name = plan_data.get("provider_name")
                if not provider_name:
                    continue

                provider = crud.get_provider_by_name(db, provider_name)
                if not provider:
                    provider = crud.create_provider(db, schemas.ProviderCreate(name=provider_name))

                plan_create = schemas.PlanCreate(
                    provider_id=provider.id,
                    plan_name=plan_data.get("plan_name", "Unknown"),
                    plan_url=plan_data.get("plan_url"),
                    plan_type=plan_data.get("plan_type", "Fixed"),
                    service_type="Commercial",
                    zip_code=plan_data.get("zip_code", "75001"),
                    contract_months=plan_data.get("contract_months"),
                    rate_1000_cents=plan_data.get("rate_1000_cents"),
                )

                crud.create_or_update_plan(db, provider.id, plan_create)
                loaded_com += 1
            except Exception as e:
                logger.warning(f"[EMERGENCY] Error loading commercial plan: {e}")
                continue

        db.commit()
        results["data_load"] = f"residential: {loaded_res}, commercial: {loaded_com}"
        logger.info(f"[EMERGENCY] Loaded {loaded_com} commercial plans")

    except Exception as e:
        results["commercial_scrape"] = f"failed: {str(e)}"
        logger.error(f"[EMERGENCY] Commercial scrape failed: {e}")

    # Final counts
    try:
        from ..models import Plan, Provider
        results["final_counts"] = {
            "providers": db.query(Provider).count(),
            "residential_plans": db.query(Plan).filter(Plan.service_type == "Residential").count(),
            "commercial_plans": db.query(Plan).filter(Plan.service_type == "Commercial").count(),
        }
        results["final_counts"]["total_plans"] = (
            results["final_counts"]["residential_plans"] +
            results["final_counts"]["commercial_plans"]
        )
    except Exception as e:
        results["final_counts"] = {"error": str(e)}

    return {
        "status": "completed",
        "results": results,
        "message": "Emergency fix completed. Check final_counts to verify data was loaded."
    }


@router.post("/delete-all-plans")
def delete_all_plans(db: Session = Depends(get_db)):
    """
    Delete ALL plans from database.
    Use with caution - this will wipe all plan data!
    """
    try:
        from ..models import Plan
        deleted_count = db.query(Plan).delete()
        db.commit()

        return {
            "status": "success",
            "message": "All plans deleted",
            "deleted_count": deleted_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/delete-fake-commercial-plans")
def delete_fake_commercial_plans(db: Session = Depends(get_db)):
    """
    Delete FAKE commercial plans from database.
    Removes plans with "verify" or "Typical" in special_features.
    """
    try:
        from ..models import Plan

        # Delete fake commercial plans (those with "verify" or "Typical" markers)
        deleted_count = db.query(Plan).filter(
            Plan.service_type == "Commercial",
            (Plan.special_features.like("%verify%") | Plan.special_features.like("%Typical%"))
        ).delete(synchronize_session=False)

        db.commit()

        # Count remaining commercial plans
        remaining = db.query(Plan).filter(Plan.service_type == "Commercial").count()

        return {
            "status": "success",
            "message": "Fake commercial plans deleted",
            "deleted_count": deleted_count,
            "remaining_commercial_plans": remaining
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/load-real-data")
def load_real_data(plans_data: List[Dict[str, Any]] = Body(...), db: Session = Depends(get_db)):
    """
    Load REAL scraped plan data into the database.
    Accepts a JSON array of plan objects.
    """
    try:
        added = 0
        updated = 0

        for plan_data in plans_data:
            # Get or create provider
            provider = crud.get_provider_by_name(db, plan_data["provider_name"])
            if not provider:
                provider_create = schemas.ProviderCreate(
                    name=plan_data["provider_name"],
                    website=plan_data.get("provider_website")
                )
                provider = crud.create_provider(db, provider_create)

            # Create plan
            plan_create = schemas.PlanCreate(
                provider_id=provider.id,
                plan_name=plan_data["plan_name"],
                plan_type=plan_data.get("plan_type", "Fixed"),
                service_type=plan_data.get("service_type", "Residential"),  # Default to Residential if missing
                zip_code=plan_data.get("zip_code", "75001"),
                contract_months=plan_data.get("contract_months", 12),
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

            # Check if exists
            from ..models import Plan
            existing = db.query(Plan).filter(
                Plan.provider_id == provider.id,
                Plan.plan_name == plan_create.plan_name
            ).first()

            if existing:
                updated += 1
            else:
                added += 1

            crud.create_or_update_plan(db, provider.id, plan_create)

        return {
            "status": "success",
            "message": "REAL data loaded successfully",
            "added": added,
            "updated": updated,
            "total": added + updated
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-migrations")
def run_migrations_manually(db: Session = Depends(get_db)):
    """
    Manually run database migrations.
    Safe to call multiple times - only applies missing changes.
    """
    try:
        from ..migrations import run_migrations

        run_migrations(db)

        return {
            "status": "success",
            "message": "Database migrations completed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")


@router.post("/load-tdus")
def load_tdu_data(db: Session = Depends(get_db)):
    """
    Load TDU data into the database.
    Loads all 6 Texas TDUs with delivery charges.
    """
    try:
        from ..tdu_data import get_all_tdus
        from .. import schemas, crud

        tdus = get_all_tdus()
        loaded_count = 0

        for tdu_data in tdus:
            tdu_create = schemas.TDUCreate(**tdu_data)
            crud.create_or_update_tdu(db, tdu_create)
            loaded_count += 1

        return {
            "status": "success",
            "message": f"Loaded {loaded_count} TDUs",
            "tdus_loaded": loaded_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TDU loading failed: {str(e)}")


@router.get("/audit-data-quality")
def audit_data_quality(db: Session = Depends(get_db)):
    """
    Audit production database for fake or estimated data.
    Returns suspicious plans that may need to be removed.
    """
    try:
        from ..models import Plan

        # Find plans with fake data markers
        fake_markers = ['estimate', 'typical', 'verify', 'fallback', 'sample', 'demo', 'call for']
        suspicious_plans = []

        for marker in fake_markers:
            plans = db.query(Plan).filter(
                Plan.special_features.ilike(f'%{marker}%')
            ).all()

            for plan in plans:
                suspicious_plans.append({
                    'id': plan.id,
                    'provider': plan.provider.name if plan.provider else 'Unknown',
                    'plan_name': plan.plan_name,
                    'service_type': plan.service_type,
                    'rate_1000_cents': plan.rate_1000_cents,
                    'special_features': plan.special_features,
                    'marker': marker,
                    'last_updated': plan.last_updated.isoformat()
                })

        # Get all plans for quality scoring
        all_plans = db.query(Plan).all()
        plans_data = [
            {
                'provider_name': p.provider.name if p.provider else 'Unknown',
                'plan_name': p.plan_name,
                'service_type': p.service_type,
                'rate_1000_cents': p.rate_1000_cents,
                'special_features': p.special_features
            }
            for p in all_plans
        ]

        quality_metrics = get_data_quality_score(plans_data)

        return {
            'status': 'success',
            'total_plans': len(all_plans),
            'suspicious_plans_count': len(suspicious_plans),
            'suspicious_plans': suspicious_plans,
            'quality_metrics': quality_metrics,
            'recommendation': 'DELETE suspicious plans' if suspicious_plans else 'Data quality is good'
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/delete-fake-data-markers")
def delete_fake_data_markers(db: Session = Depends(get_db)):
    """
    Delete ALL plans containing fake data markers.
    This includes: estimated, verify, typical, fallback, sample, demo.
    """
    try:
        from ..models import Plan

        # Delete plans with fake data markers
        fake_markers = ['estimate', 'typical', 'verify', 'fallback', 'sample', 'demo', 'call for']

        deleted_ids = []
        total_deleted = 0

        for marker in fake_markers:
            plans = db.query(Plan).filter(
                Plan.special_features.ilike(f'%{marker}%')
            ).all()

            for plan in plans:
                deleted_ids.append({
                    'id': plan.id,
                    'provider': plan.provider.name if plan.provider else 'Unknown',
                    'plan_name': plan.plan_name,
                    'marker': marker
                })
                db.delete(plan)
                total_deleted += 1

        db.commit()

        return {
            'status': 'success',
            'deleted_count': total_deleted,
            'deleted_plans': deleted_ids,
            'message': f'Deleted {total_deleted} plans with fake data markers'
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-daily-report")
def send_daily_email_report(db: Session = Depends(get_db)):
    """
    Manually trigger daily email report.
    Sends comprehensive status report with commercial rate summary to configured email.
    """
    try:
        from ..email_notifications import send_daily_report

        email_sent = send_daily_report(db)

        if email_sent:
            return {
                "status": "success",
                "message": "Daily report email sent successfully"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to send email. Check REPORT_EMAIL and SMTP configuration."
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email error: {str(e)}")


@router.post("/send-test-email")
def send_test_email(email: str, db: Session = Depends(get_db)):
    """
    Send a test email to verify SMTP configuration.

    Args:
        email: Email address to send test to (query parameter)
    """
    try:
        from ..email_notifications import send_email_report

        test_body = """
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #0066cc;">🔌 Texas Energy Analyzer - Test Email</h2>
            <p>If you're reading this, your email configuration is working correctly!</p>
            <p><strong>Next steps:</strong></p>
            <ol>
                <li>Set REPORT_EMAIL environment variable in Railway</li>
                <li>Daily reports will be sent automatically at 3 AM CT</li>
                <li>Or trigger manually via /admin/send-daily-report</li>
            </ol>
            <hr>
            <p style="color: #666; font-size: 12px;">
                This is a test email from Texas Energy Analyzer.
            </p>
        </body>
        </html>
        """

        success = send_email_report(
            to_email=email,
            subject="Texas Energy Analyzer - Test Email",
            html_body=test_body
        )

        if success:
            return {
                "status": "success",
                "message": f"Test email sent successfully to {email}",
                "note": "Check your inbox (and spam folder)"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to send test email. Check SMTP configuration in environment variables."
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email error: {str(e)}")


@router.post("/load-initial-data")
def load_initial_data(db: Session = Depends(get_db)):
    """
    ⚠️ WARNING: Load initial sample data into the database.
    This endpoint loads FAKE demonstration data and should ONLY be used for testing.
    DO NOT USE IN PRODUCTION!
    """
    try:
        added = 0
        updated = 0

        for plan_data in SAMPLE_PLANS:
            # Get or create provider
            provider = crud.get_provider_by_name(db, plan_data["provider_name"])
            if not provider:
                provider_create = schemas.ProviderCreate(
                    name=plan_data["provider_name"],
                    website=plan_data.get("provider_website")
                )
                provider = crud.create_provider(db, provider_create)

            # Create plan
            plan_create = schemas.PlanCreate(
                provider_id=provider.id,
                plan_name=plan_data["plan_name"],
                plan_type=plan_data.get("plan_type", "Fixed"),
                service_type=plan_data.get("service_type", "Residential"),  # Default to Residential if missing
                zip_code=plan_data.get("zip_code", "75001"),
                contract_months=plan_data.get("contract_months", 12),
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

            # Check if exists
            from ..models import Plan
            existing = db.query(Plan).filter(
                Plan.provider_id == provider.id,
                Plan.plan_name == plan_create.plan_name
            ).first()

            if existing:
                updated += 1
            else:
                added += 1

            crud.create_or_update_plan(db, provider.id, plan_create)

        return {
            "status": "success",
            "added": added,
            "updated": updated,
            "total": added + updated
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
