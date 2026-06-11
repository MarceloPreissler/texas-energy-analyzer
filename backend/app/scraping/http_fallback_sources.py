"""
No-browser data sources - plain HTTP, no Playwright required.

These sources keep data flowing even when Chromium is unavailable or every
browser-based scraper breaks:

1. PowerToChoose official JSON API (api.powertochoose.org) - the same data the
   PUCT website renders, returned as structured JSON. ~150 residential plans
   per deregulated ZIP.
2. EnergyBot server-rendered JSON-LD - schema.org OfferCatalog embedded in the
   static HTML of EnergyBot's Texas pages. Commercial + statewide rates.

Both run in seconds and depend only on `requests`.
"""
from __future__ import annotations

import json
import re
import logging
from typing import Dict, List

import requests

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Deregulated-market ZIPs only. Austin and San Antonio are municipal utilities
# (Austin Energy / CPS) and never return PowerToChoose plans.
PTC_ZIP_CODES = {
    "75201": "Dallas",
    "77002": "Houston",
    "76102": "Fort Worth",
    "78401": "Corpus Christi",
    "79401": "Lubbock",
    "75701": "Tyler",
}

ENERGYBOT_URLS = [
    ("https://www.energybot.com/electricity-rates/texas/business-commercial-electricity.html", "Commercial"),
    ("https://www.energybot.com/electricity-rates/texas/", "Residential"),
]


def _cents(value) -> int | None:
    """Convert a cents-per-kWh float (e.g. 13.9) to hundredths of a cent (1390)."""
    try:
        cents = int(round(float(value) * 100))
        return cents if cents > 0 else None
    except (TypeError, ValueError):
        return None


def fetch_powertochoose_api() -> List[Dict]:
    """Fetch residential plans from the official PowerToChoose JSON API."""
    plans: List[Dict] = []
    seen = set()

    for zip_code, city in PTC_ZIP_CODES.items():
        try:
            r = requests.get(
                "https://api.powertochoose.org/api/PowerToChoose/plans",
                params={"zip_code": zip_code},
                headers=HEADERS,
                timeout=45,
            )
            data = r.json().get("data") or []
            logger.info(f"[PTC API] {city} ({zip_code}): {len(data)} plans")
        except Exception as e:
            logger.error(f"[PTC API] {city} ({zip_code}) failed: {e}")
            continue

        for p in data:
            provider = (p.get("company_name") or "").strip()
            name = (p.get("plan_name") or "").strip()
            if not provider or not name:
                continue
            key = (provider.lower(), name.lower())
            if key in seen:
                continue
            seen.add(key)

            rate_1000 = _cents(p.get("price_kwh1000"))
            if not rate_1000:
                continue

            etf = 0.0
            m = re.search(r"\$(\d+(?:\.\d+)?)", p.get("pricing_details") or "")
            if m:
                etf = float(m.group(1))

            try:
                renewable = float(p.get("renewable_energy_id") or 0)
            except (TypeError, ValueError):
                renewable = 0.0

            plans.append({
                "provider_name": provider,
                "plan_name": name,
                "plan_url": p.get("go_to_plan") or p.get("website") or None,
                "fact_sheet_url": p.get("fact_sheet") or None,
                "plan_type": p.get("rate_type") or "Fixed",
                "service_type": "Residential",
                "zip_code": zip_code,
                "contract_months": p.get("term_value") or 12,
                "rate_500_cents": _cents(p.get("price_kwh500")),
                "rate_1000_cents": rate_1000,
                "rate_2000_cents": _cents(p.get("price_kwh2000")),
                "monthly_bill_1000": round(rate_1000 / 100 * 1000 / 100, 2),
                "early_termination_fee": etf,
                "renewable_percent": renewable,
                "special_features": (p.get("special_terms") or "")[:300],
                "source": "PowerToChoose API",
            })

    logger.info(f"[PTC API] Total unique residential plans: {len(plans)}")
    return plans


def fetch_energybot_jsonld() -> List[Dict]:
    """Fetch plans from EnergyBot's server-rendered schema.org JSON-LD."""
    plans: List[Dict] = []
    seen = set()

    for url, service_type in ENERGYBOT_URLS:
        try:
            r = requests.get(url, headers=HEADERS, timeout=45)
            scripts = re.findall(
                r'<script type="application/ld\+json">(.*?)</script>', r.text, re.DOTALL
            )
        except Exception as e:
            logger.error(f"[EnergyBot JSON-LD] {url} failed: {e}")
            continue

        offers = []
        for s in scripts:
            try:
                d = json.loads(s)
            except json.JSONDecodeError:
                continue
            if d.get("@type") == "OfferCatalog":
                offers.extend(d.get("itemListElement") or [])
            elif d.get("@type") == "Product":
                offers.extend((d.get("offers") or {}).get("offers") or [])
        logger.info(f"[EnergyBot JSON-LD] {url}: {len(offers)} offers ({service_type})")

        for o in offers:
            spec = o.get("priceSpecification") or {}
            seller = o.get("seller") or o.get("offeredBy") or {}
            provider = (seller.get("name") or "").strip()
            price = spec.get("price")
            if not provider or price is None:
                continue
            # price is $/kWh -> hundredths of a cent per kWh
            try:
                rate_cents = int(round(float(price) * 100 * 100))
            except (TypeError, ValueError):
                continue
            if rate_cents < 300 or rate_cents > 5000:
                continue

            m = re.search(r"(\d+)\s*month", spec.get("name") or "", re.IGNORECASE)
            months = int(m.group(1)) if m else 12
            name = f"{months} Month {'Business' if service_type == 'Commercial' else 'Fixed'} Plan"
            key = (provider.lower(), name.lower(), service_type)
            if key in seen:
                continue
            seen.add(key)

            plans.append({
                "provider_name": provider,
                "plan_name": name,
                "plan_url": seller.get("url") or None,
                "plan_type": "Fixed",
                "service_type": service_type,
                "zip_code": "75001",
                "contract_months": months,
                "rate_1000_cents": rate_cents,
                "monthly_bill_1000": round(rate_cents / 100 * 1000 / 100, 2),
                "early_termination_fee": 0.0,
                "renewable_percent": 0.0,
                "special_features": "Statewide Texas rate",
                "source": "EnergyBot JSON-LD",
            })

    logger.info(f"[EnergyBot JSON-LD] Total unique plans: {len(plans)}")
    return plans
