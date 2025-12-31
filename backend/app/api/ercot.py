"""
FastAPI router for ERCOT real-time grid data.

Fetches live data from ERCOT's public APIs for grid conditions,
fuel mix, and settlement point prices.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ercot", tags=["ercot"])

# Cache for ERCOT data (simple in-memory cache)
_cache: dict[str, Any] = {}
_cache_expiry: dict[str, datetime] = {}
CACHE_TTL = timedelta(minutes=5)


class GridStatus(BaseModel):
    timestamp: str
    current_demand_mw: float
    total_capacity_mw: float
    available_reserve_mw: float
    reserve_margin_percent: float


class FuelMix(BaseModel):
    timestamp: str
    wind_mw: float
    solar_mw: float
    natural_gas_mw: float
    coal_mw: float
    nuclear_mw: float
    hydro_mw: float
    storage_mw: float
    other_mw: float
    total_mw: float
    renewable_percent: float


class ZonePrices(BaseModel):
    timestamp: str
    lz_houston: float
    lz_north: float
    lz_south: float
    lz_west: float
    hub_houston: float
    hub_north: float
    hub_west: float
    hub_average: float


class ErcotSummary(BaseModel):
    grid_status: GridStatus
    fuel_mix: FuelMix
    zone_prices: ZonePrices
    last_updated: str
    data_source: str


def _get_cached(key: str) -> Any | None:
    """Return cached data if still valid."""
    if key in _cache and key in _cache_expiry:
        if datetime.now() < _cache_expiry[key]:
            return _cache[key]
    return None


def _set_cached(key: str, data: Any) -> None:
    """Cache data with TTL."""
    _cache[key] = data
    _cache_expiry[key] = datetime.now() + CACHE_TTL


async def fetch_ercot_supply_demand() -> dict:
    """Fetch current supply/demand data from ERCOT."""
    cached = _get_cached("supply_demand")
    if cached:
        return cached

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://www.ercot.com/api/1/services/read/dashboards/supply-demand.json",
                headers={"User-Agent": "TexasEnergyAnalyzer/1.0"}
            )
            response.raise_for_status()
            data = response.json()
            _set_cached("supply_demand", data)
            return data
    except Exception as e:
        logger.error(f"Failed to fetch ERCOT supply/demand: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to fetch ERCOT data: {str(e)}")


async def fetch_ercot_fuel_mix() -> dict:
    """Fetch current fuel mix data from ERCOT."""
    cached = _get_cached("fuel_mix")
    if cached:
        return cached

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://www.ercot.com/api/1/services/read/dashboards/fuel-mix.json",
                headers={"User-Agent": "TexasEnergyAnalyzer/1.0"}
            )
            response.raise_for_status()
            data = response.json()
            _set_cached("fuel_mix", data)
            return data
    except Exception as e:
        logger.error(f"Failed to fetch ERCOT fuel mix: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to fetch ERCOT fuel mix: {str(e)}")


async def fetch_ercot_prices() -> dict:
    """Fetch current settlement point prices from ERCOT."""
    cached = _get_cached("prices")
    if cached:
        return cached

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://www.ercot.com/api/1/services/read/dashboards/system-wide-prices.json",
                headers={"User-Agent": "TexasEnergyAnalyzer/1.0"}
            )
            response.raise_for_status()
            data = response.json()
            _set_cached("prices", data)
            return data
    except Exception as e:
        logger.error(f"Failed to fetch ERCOT prices: {e}")
        # Return fallback data structure
        return {"error": str(e)}


def parse_supply_demand(data: dict) -> GridStatus:
    """Parse ERCOT supply/demand response into GridStatus."""
    try:
        # Find the most recent non-forecast data point
        records = data.get("data", [])
        current = None
        for record in reversed(records):
            if record.get("forecast", 0) == 0:
                current = record
                break

        if not current:
            current = records[-1] if records else {}

        capacity = float(current.get("capacity", 0))
        demand = float(current.get("demand", 0))
        available = capacity - demand
        margin = (available / capacity * 100) if capacity > 0 else 0

        timestamp = current.get("interval", datetime.now().isoformat())

        return GridStatus(
            timestamp=str(timestamp),
            current_demand_mw=round(demand, 1),
            total_capacity_mw=round(capacity, 1),
            available_reserve_mw=round(available, 1),
            reserve_margin_percent=round(margin, 1)
        )
    except Exception as e:
        logger.error(f"Error parsing supply/demand: {e}")
        return GridStatus(
            timestamp=datetime.now().isoformat(),
            current_demand_mw=0,
            total_capacity_mw=0,
            available_reserve_mw=0,
            reserve_margin_percent=0
        )


def parse_fuel_mix(data: dict) -> FuelMix:
    """Parse ERCOT fuel mix response into FuelMix."""
    try:
        # Get the most recent data point from each fuel type
        current_gen = data.get("currentGen", {})

        # Extract MW values for each fuel type
        def get_latest_mw(fuel_data: list) -> float:
            if not fuel_data:
                return 0.0
            latest = fuel_data[-1] if fuel_data else {}
            return float(latest.get("gen", 0))

        wind = get_latest_mw(current_gen.get("Wind", []))
        solar = get_latest_mw(current_gen.get("Solar", []))
        gas = get_latest_mw(current_gen.get("Gas", current_gen.get("Natural Gas", [])))
        coal = get_latest_mw(current_gen.get("Coal and Lignite", current_gen.get("Coal", [])))
        nuclear = get_latest_mw(current_gen.get("Nuclear", []))
        hydro = get_latest_mw(current_gen.get("Hydro", []))
        storage = get_latest_mw(current_gen.get("Power Storage", []))
        other = get_latest_mw(current_gen.get("Other", []))

        total = wind + solar + gas + coal + nuclear + hydro + max(0, storage) + other
        renewable = wind + solar + hydro
        renewable_pct = (renewable / total * 100) if total > 0 else 0

        return FuelMix(
            timestamp=datetime.now().isoformat(),
            wind_mw=round(wind, 1),
            solar_mw=round(solar, 1),
            natural_gas_mw=round(gas, 1),
            coal_mw=round(coal, 1),
            nuclear_mw=round(nuclear, 1),
            hydro_mw=round(hydro, 1),
            storage_mw=round(storage, 1),
            other_mw=round(other, 1),
            total_mw=round(total, 1),
            renewable_percent=round(renewable_pct, 1)
        )
    except Exception as e:
        logger.error(f"Error parsing fuel mix: {e}")
        return FuelMix(
            timestamp=datetime.now().isoformat(),
            wind_mw=0, solar_mw=0, natural_gas_mw=0, coal_mw=0,
            nuclear_mw=0, hydro_mw=0, storage_mw=0, other_mw=0,
            total_mw=0, renewable_percent=0
        )


def parse_prices(data: dict) -> ZonePrices:
    """Parse ERCOT prices response into ZonePrices."""
    try:
        # Extract latest prices from zones
        prices = data.get("rtSpp", data.get("prices", {}))

        def get_latest_price(zone_data: list) -> float:
            if not zone_data:
                return 0.0
            latest = zone_data[-1] if zone_data else {}
            return float(latest.get("price", latest.get("spp", 0)))

        return ZonePrices(
            timestamp=datetime.now().isoformat(),
            lz_houston=round(get_latest_price(prices.get("LZ_HOUSTON", [])), 2),
            lz_north=round(get_latest_price(prices.get("LZ_NORTH", [])), 2),
            lz_south=round(get_latest_price(prices.get("LZ_SOUTH", [])), 2),
            lz_west=round(get_latest_price(prices.get("LZ_WEST", [])), 2),
            hub_houston=round(get_latest_price(prices.get("HB_HOUSTON", [])), 2),
            hub_north=round(get_latest_price(prices.get("HB_NORTH", [])), 2),
            hub_west=round(get_latest_price(prices.get("HB_WEST", [])), 2),
            hub_average=round(get_latest_price(prices.get("HB_HUBAVG", prices.get("HB_BUSAVG", []))), 2)
        )
    except Exception as e:
        logger.error(f"Error parsing prices: {e}")
        return ZonePrices(
            timestamp=datetime.now().isoformat(),
            lz_houston=0, lz_north=0, lz_south=0, lz_west=0,
            hub_houston=0, hub_north=0, hub_west=0, hub_average=0
        )


@router.get("/summary", response_model=ErcotSummary)
async def get_ercot_summary():
    """
    Get comprehensive ERCOT grid summary including:
    - Current demand and capacity
    - Fuel mix breakdown
    - Zone/hub prices

    Data is sourced directly from ERCOT's public APIs and cached for 5 minutes.
    """
    supply_demand = await fetch_ercot_supply_demand()
    fuel_mix = await fetch_ercot_fuel_mix()
    prices = await fetch_ercot_prices()

    grid_status = parse_supply_demand(supply_demand)
    fuel_data = parse_fuel_mix(fuel_mix)
    price_data = parse_prices(prices)

    return ErcotSummary(
        grid_status=grid_status,
        fuel_mix=fuel_data,
        zone_prices=price_data,
        last_updated=datetime.now().isoformat(),
        data_source="ERCOT Public API (ercot.com)"
    )


@router.get("/grid-status", response_model=GridStatus)
async def get_grid_status():
    """Get current ERCOT grid status (demand, capacity, reserves)."""
    data = await fetch_ercot_supply_demand()
    return parse_supply_demand(data)


@router.get("/fuel-mix", response_model=FuelMix)
async def get_fuel_mix():
    """Get current ERCOT fuel mix breakdown."""
    data = await fetch_ercot_fuel_mix()
    return parse_fuel_mix(data)


@router.get("/prices", response_model=ZonePrices)
async def get_prices():
    """Get current ERCOT zone and hub prices."""
    data = await fetch_ercot_prices()
    return parse_prices(data)
