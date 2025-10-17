"""
Admin API endpoints for data management.
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from .. import crud, schemas
from ..database import get_db
from .comprehensive_plans import COMPREHENSIVE_PLANS

router = APIRouter(prefix="/admin", tags=["admin"])

# Use comprehensive plan list (120+ plans)
SAMPLE_PLANS = COMPREHENSIVE_PLANS


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


@router.post("/load-initial-data")
def load_initial_data(db: Session = Depends(get_db)):
    """
    Load initial sample data into the database.
    This endpoint is for initial setup and testing.
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
