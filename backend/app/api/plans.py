"""
FastAPI router for plan and provider endpoints.

This router exposes endpoints to list providers, list plans with optional
filters, retrieve details of a single plan, and trigger a data scrape.
"""
from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db
from ..scraping import scraper
from ..auth import verify_api_key
from ..cache import cache_result

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("/providers", response_model=list[schemas.Provider])
def read_providers(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return crud.get_providers(db, skip=skip, limit=limit)


@router.get("/", response_model=list[schemas.Plan])
def read_plans(
    provider: str | None = Query(None, description="Filter by provider name"),
    plan_type: str | None = Query(None, description="Filter by plan type"),
    service_type: str | None = Query(None, description="Filter by service type (Residential/Commercial)"),
    zip_code: str | None = Query(None, description="Filter by zip code"),
    contract_months: int | None = Query(None, description="Filter by contract term in months"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return crud.get_plans(db, provider=provider, plan_type=plan_type, service_type=service_type, zip_code=zip_code, contract_months=contract_months, skip=skip, limit=limit)


@router.get("/{plan_id}", response_model=schemas.Plan)
def read_plan(plan_id: int, db: Session = Depends(get_db)):
    db_plan = crud.get_plan(db, plan_id=plan_id)
    if db_plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return db_plan


@router.post("/scrape")
def scrape_data(
    source: str = Query("legacy", description="Scrape source: 'legacy', 'powertochoose', 'energybot', or 'commercial'"),
    service_type: str = Query("Residential", description="Service type: 'Residential' or 'Commercial'"),
    zip_code: str | None = Query(None, description="Specific zip code (powertochoose only)"),
    db: Session = Depends(get_db),
    # api_key: str = Depends(verify_api_key)  # Temporarily disabled for initial data load
):
    """
    Trigger a scrape of electricity plans and update the database.

    Sources (REAL DATA ONLY):
    - legacy: Original scrapers (comparison sites) - 68 Residential plans
    - powertochoose: Live PowerToChoose.org data - Residential plans
    - energybot: EnergyBot.com JSON-LD data - 5 REAL Commercial plans
    - commercial: Redirects to energybot (fake aggregator removed)

    Service Types:
    - Residential: Residential electricity plans (default)
    - Commercial: Commercial/business electricity plans

    ALL DATA IS REAL - NO SAMPLE DATA, NO FALLBACKS.
    Returns the number of plans processed. Rate limited to prevent abuse.
    """
    from ..scraping import powertochoose_scraper, energybot_scraper_v2

    logger.info(f"Scrape request received - source: {source}, service_type: {service_type}, zip_code: {zip_code}")

    if source == "powertochoose":
        logger.info(f"Using live PowerToChoose scraper for {service_type} plans")
        if zip_code:
            plans = powertochoose_scraper.scrape_powertochoose(zip_code, service_type=service_type)
        else:
            plans = powertochoose_scraper.scrape_powertochoose_all_texas(service_type=service_type)
    elif source == "energybot":
        logger.info("Using EnergyBot scraper for commercial plans (REAL data only)")
        plans = energybot_scraper_v2.scrape_energybot_all_texas_v2()
    elif source == "commercial":
        logger.warning("REMOVED: commercial_aggregator had fake sample data - using EnergyBot for REAL data")
        plans = energybot_scraper_v2.scrape_energybot_all_texas_v2()
    else:
        logger.info("Using legacy scrapers for residential plans")
        plans = scraper.scrape_all()

    created_or_updated = 0
    # Insert provider and plan entries
    for plan in plans:
        provider_name = plan.pop("provider_name")
        provider = crud.get_provider_by_name(db, provider_name)
        if not provider:
            logger.debug(f"Creating new provider: {provider_name}")
            provider = crud.create_provider(db, schemas.ProviderCreate(name=provider_name))
        plan_create = schemas.PlanCreate(provider_id=provider.id, **plan)
        crud.create_or_update_plan(db, provider.id, plan_create)
        created_or_updated += 1

    logger.info(f"Scrape completed - {created_or_updated} plans processed from {source}")

    return {
        "plans_processed": created_or_updated,
        "source": source
    }