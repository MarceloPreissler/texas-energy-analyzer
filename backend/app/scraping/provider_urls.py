"""
Provider website URLs for Texas energy companies.

Maps provider names to their official websites where customers can
view and sign up for electricity plans.
"""

# Provider homepage URLs
PROVIDER_WEBSITES = {
    "Gexa Energy": "https://www.gexaenergy.com",
    "Gexa": "https://www.gexaenergy.com",
    "TXU Energy": "https://www.txu.com",
    "TXU": "https://www.txu.com",
    "Direct Energy": "https://www.directenergy.com",
    "Reliant Energy": "https://www.reliant.com",
    "Reliant": "https://www.reliant.com",
    "NRG Energy, Inc.": "https://www.nrg.com",
    "NRG Energy": "https://www.nrg.com",
    "NRG": "https://www.nrg.com",
    "AP Gas & Electric": "https://www.apge.com",
    "Chariot Energy": "https://www.gochariot.com",
    "Constellation": "https://www.constellation.com",
    "Green Mountain Energy": "https://www.greenmountainenergy.com",
    "Frontier Utilities": "https://www.frontierutilities.com",
    "Just Energy": "https://www.justenergy.com",
    "Cirro Energy": "https://www.cirroenergy.com",
    "Champion Energy": "https://www.championenergyservices.com",
    "Discount Power": "https://www.discountpowertx.com",
    "4Change Energy": "https://www.4changeenergy.com",
    "Amigo Energy": "https://www.amigoenergy.com",
    "Express Energy": "https://www.expressenergy.com",
    "Pulse Power": "https://www.pulsepower.com",
    "TriEagle Energy": "https://www.trieagleenergy.com",
    "StarTex Power": "https://www.startexpower.com",
}

# Provider plan search pages (where customers can see plans)
PROVIDER_PLAN_PAGES = {
    "Gexa Energy": "https://www.gexaenergy.com/electricity-plans",
    "Gexa": "https://www.gexaenergy.com/electricity-plans",
    "TXU Energy": "https://www.txu.com/shop/electricity-plans.html",
    "TXU": "https://www.txu.com/shop/electricity-plans.html",
    "Direct Energy": "https://www.directenergy.com/electricity-plans",
    "Reliant Energy": "https://shop.reliant.com/shop/residential",
    "Reliant": "https://shop.reliant.com/shop/residential",
    "NRG Energy, Inc.": "https://www.nrg.com/switch",
    "NRG Energy": "https://www.nrg.com/switch",
    "NRG": "https://www.nrg.com/switch",
    "AP Gas & Electric": "https://www.apge.com/plans",
    "Chariot Energy": "https://www.gochariot.com/plans",
    "Constellation": "https://www.constellation.com/solutions/for-your-home/electricity-plans.html",
}


def get_provider_website(provider_name: str) -> str:
    """
    Get the main website URL for a provider.

    Args:
        provider_name: Name of the energy provider

    Returns:
        Provider website URL, or empty string if not found
    """
    return PROVIDER_WEBSITES.get(provider_name, "")


def get_provider_plans_page(provider_name: str) -> str:
    """
    Get the plans/shop page URL for a provider.

    Args:
        provider_name: Name of the energy provider

    Returns:
        Provider plans page URL, or homepage if specific page not known
    """
    return PROVIDER_PLAN_PAGES.get(provider_name, PROVIDER_WEBSITES.get(provider_name, ""))


def get_plan_url(provider_name: str, plan_name: str = None) -> str:
    """
    Get a URL where customers can view/sign up for a plan.

    For now, returns the provider's plans page. In the future, this could
    be enhanced to return direct plan URLs if available.

    Args:
        provider_name: Name of the energy provider
        plan_name: Name of the specific plan (optional)

    Returns:
        URL where customers can find the plan
    """
    # For now, return the provider's plans page
    # Future enhancement: add specific plan URLs when available
    return get_provider_plans_page(provider_name)
