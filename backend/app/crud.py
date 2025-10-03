"""
CRUD helper functions for interacting with the database.

These functions encapsulate common operations such as retrieving providers
and plans, creating new entries, and updating existing rows.  FastAPI
endpoints call these helpers to perform database actions.
"""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from . import models, schemas
from .cache import cache_result


def get_provider_by_name(db: Session, name: str) -> Optional[models.Provider]:
    return db.execute(select(models.Provider).where(models.Provider.name == name)).scalar_one_or_none()


def create_provider(db: Session, provider: schemas.ProviderCreate) -> models.Provider:
    db_provider = models.Provider(name=provider.name, website=provider.website)
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider


@cache_result(ttl=1800, key_prefix="providers")
def get_providers(db: Session, skip: int = 0, limit: int = 100) -> List[models.Provider]:
    return db.execute(select(models.Provider).offset(skip).limit(limit)).scalars().all()


@cache_result(ttl=3600, key_prefix="plans")
def get_plans(
    db: Session,
    provider: Optional[str] = None,
    plan_type: Optional[str] = None,
    contract_months: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[models.Plan]:
    query = select(models.Plan)
    if provider:
        query = query.join(models.Provider).where(models.Provider.name == provider)
    if plan_type:
        query = query.where(models.Plan.plan_type == plan_type)
    if contract_months:
        query = query.where(models.Plan.contract_months == contract_months)
    query = query.order_by(models.Plan.rate_1000_cents.asc().nulls_last()).offset(skip).limit(limit)
    return db.execute(query).scalars().all()


def get_plan(db: Session, plan_id: int) -> Optional[models.Plan]:
    return db.execute(select(models.Plan).where(models.Plan.id == plan_id)).scalar_one_or_none()


def create_or_update_plan(db: Session, provider_id: int, plan_data: schemas.PlanCreate) -> models.Plan:
    """
    Create a new plan or update an existing one if the provider and plan_name match.
    This function helps keep the database idempotent when scraping.
    """
    existing = db.execute(
        select(models.Plan).where(
            models.Plan.provider_id == provider_id,
            models.Plan.plan_name == plan_data.plan_name,
        )
    ).scalar_one_or_none()
    if existing:
        # Update fields on existing plan
        for field, value in plan_data.model_dump(exclude={"provider_id"}).items():
            setattr(existing, field, value)
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        new_plan = models.Plan(
            provider_id=provider_id,
            plan_name=plan_data.plan_name,
            plan_type=plan_data.plan_type,
            contract_months=plan_data.contract_months,
            rate_500_cents=plan_data.rate_500_cents,
            rate_1000_cents=plan_data.rate_1000_cents,
            rate_2000_cents=plan_data.rate_2000_cents,
            monthly_bill_1000=plan_data.monthly_bill_1000,
            monthly_bill_2000=plan_data.monthly_bill_2000,
            early_termination_fee=plan_data.early_termination_fee,
            base_monthly_fee=plan_data.base_monthly_fee,
            renewable_percent=plan_data.renewable_percent,
            special_features=plan_data.special_features,
        )
        db.add(new_plan)
        db.commit()
        db.refresh(new_plan)
        return new_plan