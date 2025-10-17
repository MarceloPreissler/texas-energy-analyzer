"""
Provider website URLs for Texas energy companies.

Maps provider names to their official websites where customers can
view and sign up for electricity plans.

This file contains 50+ Texas Retail Electric Providers (REPs) operating
in the deregulated ERCOT market as of 2025.
"""

# Provider homepage URLs - Comprehensive list of Texas REPs
PROVIDER_WEBSITES = {
    # Major Providers
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
    "Constellation": "https://www.constellation.com",
    "Constellation Energy": "https://www.constellation.com",

    # Mid-Size Providers
    "AP Gas & Electric": "https://www.apge.com",
    "Chariot Energy": "https://www.gochariot.com",
    "Green Mountain Energy": "https://www.greenmountainenergy.com",
    "Frontier Utilities": "https://www.frontierutilities.com",
    "Champion Energy": "https://www.championenergyservices.com",
    "Champion Energy Services": "https://www.championenergyservices.com",
    "Discount Power": "https://www.discountpowertx.com",
    "Cirro Energy": "https://www.cirroenergy.com",
    "Pulse Power": "https://www.pulsepower.com",
    "Express Energy": "https://www.expressenergy.com",
    "TriEagle Energy": "https://www.trieagleenergy.com",
    "StarTex Power": "https://www.startexpower.com",

    # Additional Texas REPs
    "4Change Energy": "https://www.4changeenergy.com",
    "Amigo Energy": "https://www.amigoenergy.com",
    "Just Energy": "https://www.justenergy.com",
    "Energy Texas": "https://www.energytexas.com",
    "Payless Power": "https://www.paylesspower.com",
    "Oncor": "https://www.oncor.com",
    "CenterPoint Energy": "https://www.centerpointenergy.com",
    "Veteran Energy": "https://www.veteranenergy.com",
    "Frontier Utilities": "https://www.frontierutilities.com",
    "Entrust Energy": "https://www.entrustenergy.com",
    "First Choice Power": "https://www.firstchoicepower.com",
    "Rhythm Energy": "https://www.rhythmenergy.com",
    "Octopus Energy": "https://www.octopusenergy.com",
    "WTU Retail Energy": "https://www.wturetailenergy.com",
    "True Power": "https://www.truepower.com",
    "Eligo Energy": "https://www.eligoenergy.com",
    "Energy Outlet": "https://www.energyoutlet.com",
    "Bounce Energy": "https://www.bounceenergy.com",
    "Brilliant Energy": "https://www.brilliantenergy.com",
    "Lower My Bills": "https://www.lowermybills.com",
    "Cheapest Energy": "https://www.cheapestenergy.com",
    "Lone Star Energy": "https://www.lonestarenergy.com",
    "Pennywise Power": "https://www.pennywisepower.com",
    "Now Power": "https://www.nowpower.com",
    "Value Power": "https://www.valuepower.com",
    "Spark Energy": "https://www.sparkenergy.com",
    "Mega Energy": "https://www.megaenergytx.com",
    "Tesla Energy": "https://www.tesla.com/energy",
    "Clearview Energy": "https://www.clearviewenergy.com",
    "Liberty Power": "https://www.libertypower.com",
    "Direct Energy Business": "https://www.directenergy.com/business",
}

# Provider plan search pages (where customers can see plans)
PROVIDER_PLAN_PAGES = {
    # Major Providers
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
    "Constellation": "https://www.constellation.com/solutions/for-your-home/electricity-plans.html",
    "Constellation Energy": "https://www.constellation.com/solutions/for-your-home/electricity-plans.html",

    # Mid-Size Providers
    "AP Gas & Electric": "https://www.apge.com/plans",
    "Chariot Energy": "https://www.gochariot.com/plans",
    "Green Mountain Energy": "https://www.greenmountainenergy.com/plans",
    "Frontier Utilities": "https://www.frontierutilities.com/electricity-plans",
    "Champion Energy": "https://www.championenergyservices.com/shop",
    "Champion Energy Services": "https://www.championenergyservices.com/shop",
    "Discount Power": "https://www.discountpowertx.com/electricity-plans",
    "Cirro Energy": "https://www.cirroenergy.com/plans",
    "Pulse Power": "https://www.pulsepower.com/plans",
    "Express Energy": "https://www.expressenergy.com/electricity-plans",

    # Additional REPs
    "4Change Energy": "https://www.4changeenergy.com/plans",
    "Amigo Energy": "https://www.amigoenergy.com/electricity-plans",
    "Payless Power": "https://www.paylesspower.com/electricity-plans",
    "First Choice Power": "https://www.firstchoicepower.com/shop",
    "Rhythm Energy": "https://www.rhythmenergy.com/plans",
    "Bounce Energy": "https://www.bounceenergy.com/plans",
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
