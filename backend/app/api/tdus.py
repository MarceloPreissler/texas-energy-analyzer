"""
TDU (Transmission and Distribution Utility) API endpoints.

This module provides endpoints for retrieving information about Texas TDUs,
including service areas, delivery charges, and cost calculations.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ..tdu_data import TDU_SUMMARY, calculate_tdu_cost, get_tdu_by_city

router = APIRouter(prefix="/tdus", tags=["tdus"])


@router.get("/", response_model=List[schemas.TDU])
def list_tdus(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
):
    """
    Get all Texas TDUs.

    Returns comprehensive information about all Transmission and Distribution
    Utilities operating in the Texas ERCOT market, including:
    - Service areas and major cities
    - Number of customers served
    - Monthly delivery charges
    - Per-kWh delivery rates
    """
    tdus = crud.get_tdus(db, skip=skip, limit=limit)
    return tdus


@router.get("/summary")
def get_tdu_summary():
    """
    Get comprehensive information about TDUs.

    Returns a text summary explaining what TDUs are, how they work,
    and their role in the Texas deregulated electricity market.
    """
    return {"summary": TDU_SUMMARY}


@router.get("/{tdu_id}", response_model=schemas.TDU)
def get_tdu(tdu_id: int, db: Session = Depends(get_db)):
    """
    Get a specific TDU by ID.

    Returns detailed information about a single TDU, including
    service area, delivery charges, and contact information.
    """
    tdu = crud.get_tdu(db, tdu_id)
    if not tdu:
        raise HTTPException(status_code=404, detail="TDU not found")
    return tdu


@router.get("/by-name/{name}", response_model=schemas.TDU)
def get_tdu_by_name(name: str, db: Session = Depends(get_db)):
    """
    Get a TDU by name.

    Examples:
    - /tdus/by-name/Oncor
    - /tdus/by-name/CenterPoint
    - /tdus/by-name/AEP%20Texas%20Central
    """
    tdu = crud.get_tdu_by_name(db, name)
    if not tdu:
        raise HTTPException(status_code=404, detail=f"TDU '{name}' not found")
    return tdu


@router.get("/by-city/{city}")
def find_tdu_by_city(city: str):
    """
    Find which TDU serves a specific city.

    Examples:
    - /tdus/by-city/Dallas → Oncor
    - /tdus/by-city/Houston → CenterPoint
    - /tdus/by-city/Corpus%20Christi → AEP Texas Central

    Note: This uses static data. For real-time lookups, use the official
    Power to Choose website or contact your local TDU.
    """
    tdu = get_tdu_by_city(city)
    if not tdu:
        return {
            "error": f"Could not find TDU for city '{city}'",
            "message": "This lookup uses approximate data. For accurate information, visit PowerToChoose.org or contact your TDU directly.",
        }
    return {
        "city": city,
        "tdu": tdu["name"],
        "full_name": tdu["full_name"],
        "website": tdu["website"],
        "monthly_charge": tdu["monthly_charge"],
        "delivery_charge_per_kwh": tdu["delivery_charge_per_kwh"],
    }


@router.get("/calculate-cost/{tdu_name}")
def calculate_delivery_cost(
    tdu_name: str,
    kwh: int = Query(..., ge=0, le=50000, description="Monthly electricity usage in kWh"),
):
    """
    Calculate TDU delivery cost for a given usage.

    Examples:
    - /tdus/calculate-cost/Oncor?kwh=1000
    - /tdus/calculate-cost/CenterPoint?kwh=2000

    Returns the total TDU delivery charges (monthly charge + per-kWh charges)
    that would be added to your retail electricity provider's energy charges.
    """
    try:
        total_cost = calculate_tdu_cost(tdu_name, kwh)
        if total_cost == 0.0:
            raise HTTPException(status_code=404, detail=f"TDU '{tdu_name}' not found")

        return {
            "tdu_name": tdu_name,
            "kwh_usage": kwh,
            "delivery_cost": total_cost,
            "currency": "USD",
            "note": "This is only the TDU delivery charge. Your total bill will also include your retail provider's energy charges.",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/compare-costs")
def compare_tdu_costs(
    kwh: int = Query(1000, ge=0, le=50000, description="Monthly electricity usage in kWh"),
):
    """
    Compare TDU delivery costs across all Texas TDUs.

    Example: /tdus/compare-costs?kwh=1000

    Useful for understanding how delivery charges vary by location.
    Remember: you cannot choose your TDU - it's determined by your address.
    """
    from ..tdu_data import get_all_tdus

    all_tdus = get_all_tdus()
    comparison = []

    for tdu in all_tdus:
        cost = calculate_tdu_cost(tdu["name"], kwh)
        comparison.append({
            "tdu_name": tdu["name"],
            "full_name": tdu["full_name"],
            "monthly_charge": tdu["monthly_charge"],
            "delivery_charge_per_kwh": tdu["delivery_charge_per_kwh"],
            "total_delivery_cost": cost,
            "major_cities": tdu["major_cities"],
        })

    # Sort by total cost
    comparison.sort(key=lambda x: x["total_delivery_cost"])

    return {
        "kwh_usage": kwh,
        "tdus": comparison,
        "note": "TDU is determined by your location. You cannot choose your TDU, only your retail electric provider (REP).",
    }
