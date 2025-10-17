"""
Texas TDU (Transmission and Distribution Utility) data.

This file contains comprehensive information about all TDUs operating in the
deregulated ERCOT market in Texas. TDUs are regulated utilities that own and
maintain the power lines and infrastructure that deliver electricity to homes
and businesses.

TDU delivery charges change twice per year: March 1 and September 1.
These rates are regulated by the Public Utility Commission of Texas (PUCT).

Current rates are effective as of March 1, 2025.
"""
from datetime import datetime

# All Texas TDUs with comprehensive information
TEXAS_TDUS = [
    {
        "name": "Oncor",
        "full_name": "Oncor Electric Delivery",
        "website": "https://www.oncor.com",
        "service_area": (
            "Oncor is the largest TDU in Texas, serving over 10 million customers "
            "across Dallas, Fort Worth, and much of North and West Texas."
        ),
        "major_cities": "Dallas, Fort Worth, Arlington, Plano, Irving, Garland, Frisco, McKinney, Denton, Waco, Tyler, Odessa, Midland",
        "customers": 10000000,
        "monthly_charge": 4.23,
        "delivery_charge_per_kwh": 5.0339,
        "rate_effective_date": "2025-03-01",
    },
    {
        "name": "CenterPoint",
        "full_name": "CenterPoint Energy",
        "website": "https://www.centerpointenergy.com",
        "service_area": (
            "CenterPoint Energy delivers electricity to over 2.2 million customers "
            "in the greater Houston metropolitan area and surrounding communities."
        ),
        "major_cities": "Houston, Katy, League City, Sugar Land, Pearland, Baytown, The Woodlands, Galveston",
        "customers": 2200000,
        "monthly_charge": 4.39,
        "delivery_charge_per_kwh": 5.46944,
        "rate_effective_date": "2025-03-01",
    },
    {
        "name": "AEP Texas Central",
        "full_name": "AEP Texas Central",
        "website": "https://www.aeptexas.com",
        "service_area": (
            "AEP Texas Central serves over 2 million customers across 41 counties "
            "in South and Central Texas, including Corpus Christi, the Rio Grande Valley, "
            "and portions of the San Antonio area."
        ),
        "major_cities": "Corpus Christi, McAllen, Brownsville, Laredo, Harlingen, Edinburg, Pharr, Mission, San Benito, Kerrville",
        "customers": 2000000,
        "monthly_charge": 5.88,
        "delivery_charge_per_kwh": 5.5226,
        "rate_effective_date": "2025-03-01",
    },
    {
        "name": "AEP Texas North",
        "full_name": "AEP Texas North",
        "website": "https://www.aeptexas.com",
        "service_area": (
            "AEP Texas North delivers power to customers in the Abilene area "
            "and surrounding regions of West-Central Texas."
        ),
        "major_cities": "Abilene, San Angelo, Sweetwater, Brownwood",
        "customers": 250000,
        "monthly_charge": 5.88,
        "delivery_charge_per_kwh": 5.1265,
        "rate_effective_date": "2025-03-01",
    },
    {
        "name": "TNMP",
        "full_name": "Texas-New Mexico Power Company",
        "website": "https://www.tnmp.com",
        "service_area": (
            "TNMP serves over 260,000 homes and businesses across various regions "
            "of Texas, including areas in West Texas, south of Houston, and portions "
            "of the Dallas-Fort Worth metroplex."
        ),
        "major_cities": "Texas City, Alvin, Pecos, Fort Stockton, Clifton, Bryson, Lewisville",
        "customers": 260000,
        "monthly_charge": 7.85,
        "delivery_charge_per_kwh": 6.0465,
        "rate_effective_date": "2025-03-01",
    },
    {
        "name": "LP&L",
        "full_name": "Lubbock Power & Light",
        "website": "https://www.lpandl.com",
        "service_area": (
            "LP&L serves over 100,000 customers in Lubbock and joined the ERCOT "
            "grid in early 2024, bringing energy choice to Lubbock residents."
        ),
        "major_cities": "Lubbock",
        "customers": 100000,
        "monthly_charge": 3.50,  # Approximate - LP&L rates may vary
        "delivery_charge_per_kwh": 4.50,  # Approximate - LP&L rates may vary
        "rate_effective_date": "2024-01-01",
    },
]


def get_all_tdus() -> list:
    """
    Get all Texas TDU data.

    Returns:
        List of dictionaries containing TDU information
    """
    return TEXAS_TDUS


def get_tdu_by_name(name: str) -> dict:
    """
    Get TDU data by name.

    Args:
        name: TDU name (e.g., "Oncor", "CenterPoint")

    Returns:
        Dictionary with TDU information, or None if not found
    """
    for tdu in TEXAS_TDUS:
        if tdu["name"].lower() == name.lower():
            return tdu
    return None


def calculate_tdu_cost(tdu_name: str, kwh_usage: int) -> float:
    """
    Calculate TDU delivery cost for a given usage.

    Args:
        tdu_name: Name of the TDU (e.g., "Oncor")
        kwh_usage: Monthly electricity usage in kWh

    Returns:
        Total TDU delivery cost in dollars
    """
    tdu = get_tdu_by_name(tdu_name)
    if not tdu:
        return 0.0

    monthly_charge = tdu["monthly_charge"]
    per_kwh_charge = tdu["delivery_charge_per_kwh"] / 100  # Convert cents to dollars

    total_cost = monthly_charge + (kwh_usage * per_kwh_charge)
    return round(total_cost, 2)


def get_tdu_by_city(city: str) -> dict:
    """
    Find TDU by city name.

    Args:
        city: City name (e.g., "Dallas", "Houston")

    Returns:
        Dictionary with TDU information, or None if not found
    """
    city_lower = city.lower()
    for tdu in TEXAS_TDUS:
        if city_lower in tdu["major_cities"].lower():
            return tdu
    return None


# TDU information summary
TDU_SUMMARY = """
## What are TDUs?

Transmission and Distribution Utilities (TDUs), also called TDSPs (Transmission and
Distribution Service Providers), are regulated utilities that own and maintain the
physical infrastructure that delivers electricity to your home or business.

## Key Facts:

- **You don't choose your TDU** - It's determined by your location
- **TDU charges are the same regardless of which retail provider you choose**
- **TDU fees now account for about 40% of your total electricity bill**
- **Rates change twice per year**: March 1 and September 1
- **All rates are regulated by the Public Utility Commission of Texas (PUCT)**

## What TDUs Do:

- Maintain power lines, poles, and transformers
- Restore power during outages
- Read meters and manage connections
- Deliver electricity from power plants to your location

## What TDUs Don't Do:

- Sell electricity (that's your retail electric provider's job)
- Set energy rates (only delivery rates)
- Handle billing for energy charges

When comparing electricity plans, remember to account for TDU delivery charges,
which are added to your retail provider's energy charges.
"""


if __name__ == "__main__":
    # Display all TDU information
    print("Texas TDUs:\n")
    for tdu in TEXAS_TDUS:
        print(f"{tdu['full_name']} ({tdu['name']})")
        print(f"  Customers: {tdu['customers']:,}")
        print(f"  Monthly Charge: ${tdu['monthly_charge']}")
        print(f"  Delivery Charge: {tdu['delivery_charge_per_kwh']}¢/kWh")
        print(f"  Major Cities: {tdu['major_cities']}")
        print()

    # Example cost calculation
    print("\nExample: 1000 kWh usage")
    for tdu in TEXAS_TDUS:
        cost = calculate_tdu_cost(tdu["name"], 1000)
        print(f"  {tdu['name']}: ${cost}")
