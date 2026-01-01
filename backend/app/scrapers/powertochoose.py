"""PowerToChoose scraping helpers."""
from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, Iterable, List

import requests
from bs4 import BeautifulSoup

from .. import schemas

logger = logging.getLogger(__name__)

API_URL = os.getenv(
    "POWERS_TO_CHOOSE_API_URL",
    "https://api.powertochoose.org/api/PowerToChoose/plans",
)
HTML_URL = os.getenv(
    "POWERS_TO_CHOOSE_HTML_URL",
    "https://www.powertochoose.org/en-us/Plan/Results",
)
PAGE_SIZE = int(os.getenv("POWERS_TO_CHOOSE_PAGE_SIZE", "99999"))
USER_AGENT = os.getenv(
    "POWERS_TO_CHOOSE_USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
)

# Full browser-like headers to bypass Cloudflare
BROWSER_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Origin": "https://www.powertochoose.org",
    "Referer": "https://www.powertochoose.org/",
}


class _APIError(RuntimeError):
    """Internal marker for API failures."""


def scrape_power_to_choose(zip_code: str, estimated_use: int = 1000) -> List[schemas.PlanCreate]:
    """Fetch every available plan for ``zip_code`` from PowerToChoose."""

    if not zip_code or len(zip_code) != 5 or not zip_code.isdigit():
        raise ValueError("zip_code must be a valid 5-digit Texas ZIP code")

    logger.info("Scraping PowerToChoose for ZIP %s", zip_code)
    try:
        plans = _scrape_via_api(zip_code, estimated_use)
        if plans:
            logger.info("Fetched %s plans via JSON API", len(plans))
            return plans
        raise _APIError("Empty response from PowerToChoose API")
    except Exception as exc:  # pragma: no cover - re-raised for logging clarity
        logger.warning("PowerToChoose API failed (%s). Falling back to HTML scraper.", exc)

    plans = _scrape_via_html(zip_code)
    if not plans:
        raise RuntimeError("Unable to retrieve plans from PowerToChoose via API or HTML fallback")
    logger.info("Fetched %s plans via HTML fallback", len(plans))
    return plans


def _scrape_via_api(zip_code: str, estimated_use: int) -> List[schemas.PlanCreate]:
    params = {
        "zip_code": zip_code,
        "estimated_use": estimated_use,
        "page_num": 1,
        "page_size": PAGE_SIZE,
    }

    # Create a session with retry logic
    session = requests.Session()

    # Try with full browser headers first
    for attempt in range(3):
        try:
            response = session.get(
                API_URL,
                params=params,
                headers=BROWSER_HEADERS,
                timeout=60,
                verify=True
            )
            response.raise_for_status()
            payload = response.json()
            break
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
            logger.warning(f"API attempt {attempt + 1} failed: {e}")
            if attempt == 2:
                raise
            import time
            time.sleep(2)  # Wait before retry
    else:
        raise _APIError("All API attempts failed")
    plan_payload: Iterable[Dict[str, Any]]
    if isinstance(payload, dict):
        plan_payload = payload.get("data") or payload.get("plans") or payload.get("items") or []
    elif isinstance(payload, list):
        plan_payload = payload
    else:
        logger.debug("Unexpected API payload: %s", json.dumps(payload)[:200])
        plan_payload = []

    plans: List[schemas.PlanCreate] = []
    for raw_plan in plan_payload:
        if not isinstance(raw_plan, dict):
            continue
        plan = _plan_from_payload(raw_plan, zip_code)
        if plan:
            plans.append(plan)
    return plans


def _scrape_via_html(zip_code: str) -> List[schemas.PlanCreate]:
    headers = {"User-Agent": USER_AGENT}
    page = 1
    plans: List[schemas.PlanCreate] = []

    while True:
        params = {"zip_code": zip_code, "page": page}
        response = requests.get(HTML_URL, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.select_one("table")
        rows = table.select("tbody tr") if table else soup.select(".plan-result, .plan-card")
        if not rows:
            break

        for row in rows:
            plan = _plan_from_html_row(row, zip_code)
            if plan:
                plans.append(plan)

        pagination = soup.select_one("[data-total-pages]")
        if pagination:
            try:
                total_pages = int(pagination["data-total-pages"])
                if page >= total_pages:
                    break
            except (KeyError, ValueError):
                pass
        page += 1

    return plans


def _plan_from_payload(raw: Dict[str, Any], zip_code: str) -> schemas.PlanCreate | None:
    provider_name = _coalesce(raw, ["providerName", "provider", "repName", "rep"])
    plan_name = _coalesce(raw, ["planName", "plan_name", "name"])
    if not provider_name or not plan_name:
        return None

    plan_type = _coalesce(raw, ["planType", "plan_type", "type"])
    contract_months = _to_int(_coalesce(raw, ["termValue", "term", "contractTerm", "contract"]))
    renewable_percent = _to_int(_coalesce(raw, ["renewableValue", "renewable_percent", "renewable"]))
    cancellation_fee = _to_float(
        _coalesce(
            raw,
            ["cancellationFee", "cancellation_fee", "earlyTerminationFee", "etf", "terminationFee"],
        )
    )
    rate_500 = _to_float(_coalesce(raw, ["rate_500", "rate500", "rate500kwh", "fiveHundredRate"]))
    rate_1000 = _to_float(_coalesce(raw, ["rate_1000", "rate1000", "rate1000kwh", "oneThousandRate", "avgPrice"]))
    rate_2000 = _to_float(_coalesce(raw, ["rate_2000", "rate2000", "rate2000kwh", "twoThousandRate"]))
    plan_url = _coalesce(raw, ["planUrl", "planURL", "plan_url"])
    special_features = _coalesce(raw, ["specialFeatures", "features", "planFeatures"]) or raw.get("description")

    # Try to extract rate effective/start date
    rate_start_date = _parse_date(_coalesce(raw, [
        "effectiveDate", "effective_date", "startDate", "start_date",
        "rateEffectiveDate", "planStartDate", "validFrom"
    ]))

    monthly_bill_1000 = _calculate_monthly_bill(rate_1000, 1000)
    monthly_bill_2000 = _calculate_monthly_bill(rate_2000, 2000)

    return schemas.PlanCreate(
        provider_name=provider_name.strip(),
        plan_name=plan_name.strip(),
        plan_url=plan_url,
        plan_type=plan_type,
        service_type="Residential",
        zip_code=zip_code,
        contract_months=contract_months,
        rate_500_cents=rate_500,
        rate_1000_cents=rate_1000,
        rate_2000_cents=rate_2000,
        monthly_bill_1000=monthly_bill_1000,
        monthly_bill_2000=monthly_bill_2000,
        early_termination_fee=cancellation_fee,
        cancellation_fee=cancellation_fee,
        renewable_percent=renewable_percent,
        special_features=special_features,
        rate_start_date=rate_start_date,
    )


def _plan_from_html_row(row, zip_code: str) -> schemas.PlanCreate | None:
    text = row.get_text("\n", strip=True)
    cells = row.find_all("td")
    labeled: Dict[str, str] = {}
    for cell in cells:
        label = (cell.get("data-label") or "").strip().lower()
        if label:
            labeled[label] = cell.get_text(strip=True)
    provider_name = labeled.get("provider") or (cells[0].get_text(strip=True) if cells else None)
    plan_name = labeled.get("plan") or labeled.get("plan name")
    if not plan_name and len(cells) > 1:
        plan_name = cells[1].get_text(strip=True)
    if not provider_name or not plan_name:
        return None

    plan_type = labeled.get("type") or _infer_plan_type(text)
    term_text = labeled.get("term") or labeled.get("contract")
    contract_months = _to_int(term_text)
    renewable_percent = _to_int(labeled.get("renewable") or labeled.get("renewable content"))
    cancellation_fee = _parse_currency(labeled.get("cancellation fee") or labeled.get("early termination fee"))

    rate_500 = _parse_rate(labeled.get("500 kwh"), text)
    rate_1000 = _parse_rate(labeled.get("1000 kwh"), text)
    rate_2000 = _parse_rate(labeled.get("2000 kwh"), text)

    features = labeled.get("features") or labeled.get("details") or _extract_features(text)

    return schemas.PlanCreate(
        provider_name=provider_name,
        plan_name=plan_name,
        plan_type=plan_type,
        service_type="Residential",
        zip_code=zip_code,
        contract_months=contract_months,
        rate_500_cents=rate_500,
        rate_1000_cents=rate_1000,
        rate_2000_cents=rate_2000,
        monthly_bill_1000=_calculate_monthly_bill(rate_1000, 1000),
        monthly_bill_2000=_calculate_monthly_bill(rate_2000, 2000),
        early_termination_fee=cancellation_fee,
        cancellation_fee=cancellation_fee,
        renewable_percent=renewable_percent,
        special_features=features,
    )


def _coalesce(raw: Dict[str, Any], keys: Iterable[str]) -> Any:
    for key in keys:
        if key in raw and raw[key] not in (None, ""):
            return raw[key]
    return None


def _to_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    digits = re.search(r"(\d+)", str(value))
    return int(digits.group(1)) if digits else None


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = re.sub(r"[^0-9.]+", "", str(value))
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_currency(value: Any) -> float | None:
    if value is None:
        return None
    match = re.search(r"(\d+\.?\d*)", str(value))
    return float(match.group(1)) if match else None


def _parse_rate(value: Any, fallback_text: str) -> float | None:
    if value:
        return _to_float(value)
    match = re.search(r"(\d+\.?\d*)\s*(?:¢|cents|c/kWh)", fallback_text, re.IGNORECASE)
    return float(match.group(1)) if match else None


def _infer_plan_type(text: str) -> str | None:
    lowered = text.lower()
    if "time" in lowered or "free night" in lowered or "free weekend" in lowered:
        return "Time of Use"
    if "variable" in lowered:
        return "Variable"
    if "solar" in lowered or "green" in lowered:
        return "Renewable"
    return None


def _extract_features(text: str) -> str | None:
    snippets = []
    if "free night" in text.lower():
        snippets.append("Free Nights")
    if "weekend" in text.lower():
        snippets.append("Free Weekends")
    if "solar" in text.lower() or "renewable" in text.lower():
        snippets.append("High Renewable Content")
    return ", ".join(snippets) if snippets else None


def _parse_date(value: Any) -> datetime | None:
    """Parse a date string into a datetime object."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        # Try common date formats
        for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"]:
            try:
                return datetime.strptime(str(value).split("T")[0].split()[0], fmt)
            except ValueError:
                continue
        return None
    except Exception:
        return None


def _calculate_monthly_bill(rate_cents: float | None, usage_kwh: int) -> float | None:
    if rate_cents is None:
        return None
    return round((rate_cents / 100) * usage_kwh, 2)
