"""
Web scraping routines for Texas retail energy plans.

The functions defined in this module download HTML from publicly available
web pages and extract pricing and plan details.  Each scraper returns a
list of dictionaries that map directly to the `PlanCreate` schema.  If a
provider does not yet exist in the database it will be created on the fly
when inserting plans.

Important: Websites change frequently.  These scrapers were written
against pages available in September 2025.  If parsing errors occur
you may need to inspect the pages and update the CSS selectors.

Scraping is subject to each site's terms of service.  Use these
functions responsibly and consider caching results to limit requests.
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import List, Dict

import requests
from bs4 import BeautifulSoup


def _clean_float(text: str) -> float:
    """
    Convert a textual representation of cents per kWh or a dollar amount into
    a float.  Removes non‑numeric characters and returns None if conversion
    fails.
    """
    if text is None:
        return None
    cleaned = re.sub(r"[^0-9\.]+", "", text)
    return float(cleaned) if cleaned else None


def scrape_gexa_txu() -> List[Dict]:
    """
    Scrape sample Gexa and TXU plans from the comparison article on
    PowerChoiceTexas.  The article contains a table with plan names,
    contract lengths, price (cents per kWh) and monthly bill estimates.

    Returns a list of dictionaries keyed according to PlanCreate.
    """
    url = "https://www.choosetexaspower.org/electricity-providers/gexa-energy-vs-txu-energy-review/"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    plans: List[Dict] = []

    # Locate the table rows that contain plan data.  The tables list plan
    # name, contract length, price in cents/kWh and estimated monthly bill.
    # We'll search for rows where there are exactly four <td> children.
    rows = soup.find_all("tr")
    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
        # We expect at least 4 columns: plan, contract length, price, bill + details
        if len(cols) >= 4 and re.match(r"\d+\s*months", cols[1]):
            plan_name = cols[0]
            contract_text = cols[1]
            price_text = cols[2]
            bill_text = cols[3]
            # Extract months from contract length
            match = re.search(r"(\d+)", contract_text)
            contract_months = int(match.group(1)) if match else None
            rate = _clean_float(price_text)
            monthly_bill = _clean_float(bill_text)

            # Determine provider from plan name prefix (Gexa or TXU)
            provider_name = "Gexa" if plan_name.lower().startswith("gexa") else "TXU"
            special_features = None
            # If plan includes credit, look for $ and kWh in details
            if "credit" in row.get_text().lower():
                special_features = row.get_text(strip=True)

            plans.append({
                "provider_name": provider_name,
                "plan_name": plan_name,
                "plan_type": "Fixed",  # sample comparison table only lists fixed plans
                "contract_months": contract_months,
                "rate_1000_cents": rate,
                "monthly_bill_1000": monthly_bill,
                "special_features": special_features,
            })
    return plans


def scrape_direct_energy() -> List[Dict]:
    """
    Scrape Direct Energy plans from PowerChoiceTexas.  There are separate
    tables for Houston and Dallas.  We parse both and normalize them.
    """
    url = "https://www.powerchoicetexas.org/providers/direct-energy"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    plans: List[Dict] = []

    # The Direct Energy page contains plan tables where each row has
    # plan name, term and rate.  There may be multiple tables; parse all rows.
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cols = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
            if len(cols) >= 3 and re.match(r"\d+/months", cols[1]):
                plan_name = cols[0]
                term_text = cols[1]
                price_text = cols[2]
                # Extract months from '12/months'
                months_match = re.search(r"(\d+)", term_text)
                contract_months = int(months_match.group(1)) if months_match else None
                rate = _clean_float(price_text)
                plan_type = "Fixed"
                special_features = None
                # Twelve Hour Power offers free nights
                if "Twelve Hour Power" in plan_name:
                    special_features = "Free power between 9 p.m. and 9 a.m."
                plans.append({
                    "provider_name": "Direct Energy",
                    "plan_name": plan_name,
                    "plan_type": plan_type,
                    "contract_months": contract_months,
                    "rate_1000_cents": rate,
                    "special_features": special_features,
                    "early_termination_fee": 135.0 if plan_name == "Live Brighter 12" else None,
                })
    return plans


def scrape_reliant() -> List[Dict]:
    """
    Scrape Reliant Energy plans from PowerChoiceTexas.  Extract plan name,
    term and rate at the 1,000 kWh tier.  Note that some plans like
    'Truly Free Weekends' and 'Truly Free Nights' have no simple rate but
    include special features; we capture the plan name and mark rate as None.
    """
    url = "https://www.powerchoicetexas.org/providers/reliant-energy"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    plans: List[Dict] = []
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cols = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
            # Rows with plan name, term and rate
            if len(cols) >= 3 and re.match(r"\d+/months", cols[1]):
                plan_name = cols[0]
                term_text = cols[1]
                price_text = cols[2]
                months_match = re.search(r"(\d+)", term_text)
                contract_months = int(months_match.group(1)) if months_match else None
                rate = _clean_float(price_text)
                plans.append({
                    "provider_name": "Reliant Energy",
                    "plan_name": plan_name,
                    "plan_type": "Fixed",
                    "contract_months": contract_months,
                    "rate_1000_cents": rate,
                })
    # Add manually known speciality plans; these may not appear in the rate tables
    plans.append({
        "provider_name": "Reliant Energy",
        "plan_name": "Truly Free Weekends",
        "plan_type": "Free Nights/Weekends",
        "special_features": "Free electricity on weekends; higher weekday rates",
    })
    plans.append({
        "provider_name": "Reliant Energy",
        "plan_name": "Truly Free Nights",
        "plan_type": "Free Nights/Weekends",
        "special_features": "Free electricity at night; higher daytime rates",
    })
    return plans


def scrape_txu() -> List[Dict]:
    """
    Scrape TXU Energy plans from PowerChoiceTexas.  Parse the plan name,
    term and rate.  Also look for text describing bill credits and free
    periods for certain plans.
    """
    url = "https://www.powerchoicetexas.org/providers/txu-energy"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    plans: List[Dict] = []
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cols = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
            if len(cols) >= 3 and re.match(r"\d+/months|\d+/month|\d+/year|\d+/\w+", cols[1]):
                plan_name = cols[0]
                term_text = cols[1]
                price_text = cols[2]
                months_match = re.search(r"(\d+)", term_text)
                contract_months = int(months_match.group(1)) if months_match else None
                rate = _clean_float(price_text)
                # Determine plan type based on name
                plan_type = "Fixed"
                special_features = None
                if "Free Nights" in plan_name:
                    plan_type = "Free Nights/Weekends"
                    special_features = "Free electricity at night between 8 p.m. and 5 a.m."
                elif "Flex Forward" in plan_name:
                    plan_type = "Variable"
                    special_features = "3% cash‑back loyalty reward"
                elif "Solar" in plan_name:
                    plan_type = "Solar"
                    special_features = "Includes bill credit when usage exceeds 800 or 1,200 kWh"
                plans.append({
                    "provider_name": "TXU Energy",
                    "plan_name": plan_name,
                    "plan_type": plan_type,
                    "contract_months": contract_months,
                    "rate_1000_cents": rate,
                    "special_features": special_features,
                })
    return plans


def scrape_all() -> List[Dict]:
    """
    Aggregate all provider scrapers into a single list.  This function can
    be called to refresh the entire dataset.
    """
    all_plans: List[Dict] = []
    for scraper in (scrape_gexa_txu, scrape_direct_energy, scrape_reliant, scrape_txu):
        try:
            all_plans.extend(scraper())
        except Exception as exc:
            print(f"Scraper {scraper.__name__} failed: {exc}")
    # Add timestamp to each plan
    now = datetime.utcnow()
    for plan in all_plans:
        plan["last_updated"] = now
    return all_plans