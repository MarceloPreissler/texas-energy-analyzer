#!/usr/bin/env python3
"""
Refresh production data WITHOUT a browser.

Sources:
- Residential: official PowerToChoose API (api.powertochoose.org) - JSON, no scraping
- Commercial: EnergyBot JSON-LD structured data (server-rendered, plain HTTP)

Loads results into production via POST /admin/load-real-data.
Run from anywhere: python3 REFRESH_PRODUCTION_DATA.py
"""
import json
import re
import requests

BACKEND = "https://texas-energy-backend.onrender.com"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

# Deregulated-market ZIPs only. Austin (78701) and San Antonio (78201) are
# municipal utilities (Austin Energy / CPS) and never return PowerToChoose plans.
ZIP_CODES = {
    "75201": "Dallas",
    "77002": "Houston",
    "76102": "Fort Worth",
    "78401": "Corpus Christi",
    "79401": "Lubbock",
    "75701": "Tyler",
}

ENERGYBOT_URLS = [
    "https://www.energybot.com/electricity-rates/texas/business-commercial-electricity.html",
    "https://www.energybot.com/electricity-rates/texas/",
]


def fetch_residential():
    """Fetch residential plans from the official PowerToChoose API."""
    plans = []
    seen = set()
    for zip_code, city in ZIP_CODES.items():
        try:
            r = requests.get(
                "https://api.powertochoose.org/api/PowerToChoose/plans",
                params={"zip_code": zip_code},
                headers=HEADERS,
                timeout=45,
            )
            data = r.json().get("data") or []
            print(f"  [PTC] {city} ({zip_code}): {len(data)} plans")
            for p in data:
                provider = (p.get("company_name") or "").strip()
                name = (p.get("plan_name") or "").strip()
                if not provider or not name:
                    continue
                key = (provider.lower(), name.lower())
                if key in seen:
                    continue
                seen.add(key)

                def cents(v):
                    try:
                        return int(round(float(v) * 100))
                    except (TypeError, ValueError):
                        return None

                rate_1000 = cents(p.get("price_kwh1000"))
                if not rate_1000 or rate_1000 <= 0:
                    continue

                etf = 0.0
                m = re.search(r"\$(\d+(?:\.\d+)?)", p.get("pricing_details") or "")
                if m:
                    etf = float(m.group(1))

                renewable = 0.0
                try:
                    renewable = float(p.get("renewable_energy_id") or 0)
                except (TypeError, ValueError):
                    pass

                plans.append({
                    "provider_name": provider,
                    "provider_website": p.get("website") or None,
                    "plan_name": name,
                    "plan_type": p.get("rate_type") or "Fixed",
                    "service_type": "Residential",
                    "zip_code": zip_code,
                    "contract_months": p.get("term_value") or 12,
                    "rate_500_cents": cents(p.get("price_kwh500")),
                    "rate_1000_cents": rate_1000,
                    "rate_2000_cents": cents(p.get("price_kwh2000")),
                    "monthly_bill_1000": round(rate_1000 / 100 * 1000 / 100, 2),
                    "early_termination_fee": etf,
                    "renewable_percent": renewable,
                    "special_features": (p.get("special_terms") or "")[:300],
                })
        except Exception as e:
            print(f"  [PTC] {city} ({zip_code}) FAILED: {e}")
    return plans


def fetch_commercial():
    """Fetch commercial plans from EnergyBot's server-rendered JSON-LD."""
    plans = []
    seen = set()
    for url in ENERGYBOT_URLS:
        try:
            r = requests.get(url, headers=HEADERS, timeout=45)
            scripts = re.findall(
                r'<script type="application/ld\+json">(.*?)</script>', r.text, re.DOTALL
            )
            offers = []
            for s in scripts:
                try:
                    d = json.loads(s)
                except json.JSONDecodeError:
                    continue
                if d.get("@type") == "OfferCatalog":
                    offers.extend(d.get("itemListElement") or [])
                elif d.get("@type") == "Product":
                    agg = d.get("offers") or {}
                    offers.extend(agg.get("offers") or [])
            is_business = "business" in url
            print(f"  [EnergyBot] {url.rsplit('/', 1)[-1] or 'texas'}: {len(offers)} offers")
            for o in offers:
                spec = o.get("priceSpecification") or {}
                seller = o.get("seller") or o.get("offeredBy") or {}
                provider = (seller.get("name") or "").strip()
                raw_name = spec.get("name") or ""
                price = spec.get("price")
                if not provider or price is None:
                    continue
                rate_cents = int(round(float(price) * 100 * 100))  # $/kWh -> hundredths of a cent
                if rate_cents < 300 or rate_cents > 5000:
                    continue
                m = re.search(r"(\d+)\s*month", raw_name, re.IGNORECASE)
                months = int(m.group(1)) if m else 12
                service_type = "Commercial" if is_business else "Residential"
                name = f"{months} Month {'Business' if is_business else 'Fixed'} Plan"
                key = (provider.lower(), name.lower(), service_type)
                if key in seen:
                    continue
                seen.add(key)
                plans.append({
                    "provider_name": provider,
                    "provider_website": seller.get("url") or None,
                    "plan_name": name,
                    "plan_type": "Fixed",
                    "service_type": service_type,
                    "zip_code": "75001",
                    "contract_months": months,
                    "rate_1000_cents": rate_cents,
                    "monthly_bill_1000": round(rate_cents / 100 * 1000 / 100, 2),
                    "early_termination_fee": 0.0,
                    "renewable_percent": 0.0,
                    "special_features": "Statewide Texas rate via EnergyBot",
                })
        except Exception as e:
            print(f"  [EnergyBot] {url} FAILED: {e}")
    return plans


def load_to_production(plans, batch_size=50):
    total = 0
    for i in range(0, len(plans), batch_size):
        batch = plans[i:i + batch_size]
        r = requests.post(f"{BACKEND}/admin/load-real-data", json=batch, headers=HEADERS, timeout=120)
        ok = r.status_code == 200
        body = r.json() if ok else r.text[:200]
        print(f"  batch {i // batch_size + 1}: HTTP {r.status_code} {body}")
        if ok:
            total += len(batch)
    return total


if __name__ == "__main__":
    print("=" * 70)
    print("REFRESHING PRODUCTION DATA (no browser required)")
    print("=" * 70)

    print("\n[1/3] Residential via official PowerToChoose API...")
    residential = fetch_residential()
    print(f"  -> {len(residential)} unique residential plans")

    print("\n[2/3] Commercial via EnergyBot JSON-LD...")
    commercial = fetch_commercial()
    print(f"  -> {len(commercial)} unique commercial plans")

    all_plans = residential + commercial
    if not all_plans:
        print("\nNo plans fetched - aborting (production data left untouched)")
        raise SystemExit(1)

    print(f"\n[3/3] Loading {len(all_plans)} plans to {BACKEND} ...")
    loaded = load_to_production(all_plans)
    print(f"\nDONE: {loaded} plans loaded to production")

    r = requests.get(f"{BACKEND}/plans/", headers=HEADERS, timeout=60)
    data = r.json()
    comm = sum(1 for p in data if p.get("service_type") == "Commercial")
    res = sum(1 for p in data if p.get("service_type") == "Residential")
    print(f"Production now has: {len(data)} total | {comm} commercial | {res} residential")
