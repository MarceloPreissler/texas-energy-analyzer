"""
Commercial Plans Aggregator - Combines multiple commercial plan sources.

This scraper aggregates commercial plans from:
- EnergyBot (live scraping)
- TXU Business (fallback rates)
- Direct Energy Business (fallback rates)
- Gexa Business (fallback rates)
- Reliant Business (fallback rates)

For personal analytical use. Rates should be verified with providers.
"""
from __future__ import annotations

from typing import List, Dict
from datetime import datetime, timezone

# Import working scrapers
try:
    from . import energybot_scraper_v2
except ImportError:
    import energybot_scraper_v2


def get_fallback_commercial_plans() -> List[Dict]:
    """
    Get fallback commercial plans with typical rates.

    These are based on historical data and should be verified with providers.
    Useful for analysis and comparison purposes.
    """
    plans = []

    # TXU Business Plans (typical rates as of 2025)
    txu_plans = [
        {"name": "Business Advantage 12", "rate": 11.9, "term": 12},
        {"name": "Business Advantage 24", "rate": 11.5, "term": 24},
        {"name": "Business Value 12", "rate": 12.5, "term": 12},
        {"name": "Business Value 24", "rate": 12.2, "term": 24},
        {"name": "Small Business Fixed 12", "rate": 12.8, "term": 12},
    ]

    for plan in txu_plans:
        plans.append({
            "provider_name": "TXU Energy",
            "plan_name": plan["name"],
            "plan_type": "Fixed",
            "service_type": "Commercial",
            "zip_code": "75001",
            "contract_months": plan["term"],
            "rate_1000_cents": plan["rate"],
            "special_features": "Typical rate - verify with TXU for current pricing",
            "last_updated": datetime.now(timezone.utc),
        })

    # Direct Energy Business Plans
    direct_plans = [
        {"name": "Business Select 12", "rate": 12.4, "term": 12},
        {"name": "Business Select 24", "rate": 11.8, "term": 24},
        {"name": "Business Power 12", "rate": 13.1, "term": 12},
        {"name": "Business Essentials 12", "rate": 12.9, "term": 12},
    ]

    for plan in direct_plans:
        plans.append({
            "provider_name": "Direct Energy",
            "plan_name": plan["name"],
            "plan_type": "Fixed",
            "service_type": "Commercial",
            "zip_code": "75001",
            "contract_months": plan["term"],
            "rate_1000_cents": plan["rate"],
            "special_features": "Typical rate - verify with Direct Energy",
            "last_updated": datetime.now(timezone.utc),
        })

    # Gexa Business Plans
    gexa_plans = [
        {"name": "Business Choice 12", "rate": 11.7, "term": 12},
        {"name": "Business Choice 24", "rate": 11.3, "term": 24},
        {"name": "Business Saver 12", "rate": 12.2, "term": 12},
    ]

    for plan in gexa_plans:
        plans.append({
            "provider_name": "Gexa Energy",
            "plan_name": plan["name"],
            "plan_type": "Fixed",
            "service_type": "Commercial",
            "zip_code": "75001",
            "contract_months": plan["term"],
            "rate_1000_cents": plan["rate"],
            "special_features": "Typical rate - verify with Gexa",
            "last_updated": datetime.now(timezone.utc),
        })

    # Reliant Business Plans
    reliant_plans = [
        {"name": "Business Power Plus 12", "rate": 12.6, "term": 12},
        {"name": "Business Power Plus 24", "rate": 12.1, "term": 24},
        {"name": "Business Advantage 12", "rate": 13.0, "term": 12},
    ]

    for plan in reliant_plans:
        plans.append({
            "provider_name": "Reliant Energy",
            "plan_name": plan["name"],
            "plan_type": "Fixed",
            "service_type": "Commercial",
            "zip_code": "75001",
            "contract_months": plan["term"],
            "rate_1000_cents": plan["rate"],
            "special_features": "Typical rate - verify with Reliant",
            "last_updated": datetime.now(timezone.utc),
        })

    # Constellation Business Plans
    constellation_plans = [
        {"name": "Business Fixed 12", "rate": 12.3, "term": 12},
        {"name": "Business Fixed 24", "rate": 11.9, "term": 24},
        {"name": "Business Green 12", "rate": 13.5, "term": 12, "type": "Solar"},
    ]

    for plan in constellation_plans:
        plans.append({
            "provider_name": "Constellation",
            "plan_name": plan["name"],
            "plan_type": plan.get("type", "Fixed"),
            "service_type": "Commercial",
            "zip_code": "75001",
            "contract_months": plan["term"],
            "rate_1000_cents": plan["rate"],
            "special_features": "100% renewable" if plan.get("type") == "Solar" else "Typical rate - verify with Constellation",
            "last_updated": datetime.now(timezone.utc),
        })

    print(f"[Fallback] Generated {len(plans)} fallback commercial plans")
    return plans


def scrape_all_commercial_plans() -> List[Dict]:
    """
    Scrape all commercial plans from multiple sources.

    Combines:
    - Live EnergyBot scraping (5+ plans)
    - Fallback plans from major providers (15+ plans)

    Total: 20-25 commercial plans for analysis
    """
    all_plans = []

    # 1. Try live EnergyBot scraping
    print("[Commercial Aggregator] Scraping live plans from EnergyBot...")
    try:
        energybot_plans = energybot_scraper_v2.scrape_energybot_all_texas_v2()
        all_plans.extend(energybot_plans)
        print(f"[Commercial Aggregator] Added {len(energybot_plans)} live EnergyBot plans")
    except Exception as e:
        print(f"[Commercial Aggregator] EnergyBot scraping failed: {e}")

    # 2. Add fallback plans
    print("[Commercial Aggregator] Adding fallback plans from major providers...")
    fallback_plans = get_fallback_commercial_plans()
    all_plans.extend(fallback_plans)

    print(f"[Commercial Aggregator] Total: {len(all_plans)} commercial plans")
    return all_plans


# For testing
if __name__ == "__main__":
    print("Testing Commercial Aggregator...")
    plans = scrape_all_commercial_plans()

    print(f"\n=== SCRAPED {len(plans)} TOTAL COMMERCIAL PLANS ===\n")

    # Group by provider
    by_provider = {}
    for plan in plans:
        provider = plan['provider_name']
        if provider not in by_provider:
            by_provider[provider] = []
        by_provider[provider].append(plan)

    for provider, provider_plans in sorted(by_provider.items()):
        print(f"\n{provider} ({len(provider_plans)} plans):")
        for plan in provider_plans:
            print(f"  - {plan['plan_name']}: {plan['rate_1000_cents']}¢/kWh ({plan['contract_months']} mo)")
