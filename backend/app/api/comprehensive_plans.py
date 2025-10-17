"""
Comprehensive sample plan data for Texas Energy Analyzer.
This provides a rich dataset for demonstration purposes.
"""

# Comprehensive list of 100+ Texas energy plans
COMPREHENSIVE_PLANS = [
    # ========== RESIDENTIAL PLANS (60+ plans) ==========

    # TXU Energy - Residential
    {"provider_name": "TXU Energy", "provider_website": "https://www.txu.com", "plan_name": "TXU Energy Secure 12", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 13.5, "monthly_bill_1000": 144.45, "special_features": "12-month price protection"},
    {"provider_name": "TXU Energy", "provider_website": "https://www.txu.com", "plan_name": "TXU Energy Secure 24", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 12.8, "monthly_bill_1000": 137.75, "special_features": "24-month price protection"},
    {"provider_name": "TXU Energy", "provider_website": "https://www.txu.com", "plan_name": "TXU Energy Secure 36", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 36, "rate_1000_cents": 12.2, "monthly_bill_1000": 131.95, "special_features": "36-month price protection"},
    {"provider_name": "TXU Energy", "provider_website": "https://www.txu.com", "plan_name": "TXU Free Nights 12", "plan_type": "Free Nights", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 14.2, "monthly_bill_1000": 151.95, "special_features": "Free electricity 9pm-6am"},
    {"provider_name": "TXU Energy", "provider_website": "https://www.txu.com", "plan_name": "TXU Free Weekends 12", "plan_type": "Free Weekends", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 15.1, "monthly_bill_1000": 160.95, "special_features": "Free electricity all weekend"},

    # Reliant Energy - Residential
    {"provider_name": "Reliant Energy", "provider_website": "https://www.reliant.com", "plan_name": "Reliant Basic Power 12", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 14.1, "monthly_bill_1000": 150.95, "special_features": "Simple fixed rate"},
    {"provider_name": "Reliant Energy", "provider_website": "https://www.reliant.com", "plan_name": "Reliant Secure Advantage 12", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 13.7, "monthly_bill_1000": 146.95, "special_features": "Predictable bills"},
    {"provider_name": "Reliant Energy", "provider_website": "https://www.reliant.com", "plan_name": "Reliant Secure Advantage 24", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 13.1, "monthly_bill_1000": 140.95, "special_features": "Long-term savings"},
    {"provider_name": "Reliant Energy", "provider_website": "https://www.reliant.com", "plan_name": "Reliant Truly Free Weekends 12", "plan_type": "Free Weekends", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 15.8, "monthly_bill_1000": 167.95, "special_features": "Free power Fri 6pm-Mon 6am"},
    {"provider_name": "Reliant Energy", "provider_website": "https://www.reliant.com", "plan_name": "Reliant Conservation 12", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 13.9, "monthly_bill_1000": 148.95, "special_features": "Rewards for energy savings"},

    # Direct Energy - Residential
    {"provider_name": "Direct Energy", "provider_website": "https://www.directenergy.com", "plan_name": "Live Brighter 12", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 13.8, "monthly_bill_1000": 147.95, "special_features": "Smart home integration"},
    {"provider_name": "Direct Energy", "provider_website": "https://www.directenergy.com", "plan_name": "Live Brighter 24", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 13.2, "monthly_bill_1000": 141.95, "special_features": "24-month rate lock"},
    {"provider_name": "Direct Energy", "provider_website": "https://www.directenergy.com", "plan_name": "Direct Your Energy 12", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 14.0, "monthly_bill_1000": 149.95, "special_features": "Online account management"},
    {"provider_name": "Direct Energy", "provider_website": "https://www.directenergy.com", "plan_name": "Direct Renewable 12", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 14.5, "monthly_bill_1000": 154.95, "renewable_percent": 100.0, "special_features": "100% renewable energy"},

    # Gexa Energy - Residential
    {"provider_name": "Gexa Energy", "provider_website": "https://www.gexaenergy.com", "plan_name": "Gexa Saver Supreme 12", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 13.2, "monthly_bill_1000": 141.95, "special_features": "Low fixed rate"},
    {"provider_name": "Gexa Energy", "provider_website": "https://www.gexaenergy.com", "plan_name": "Gexa Saver Supreme 24", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 12.6, "monthly_bill_1000": 135.95, "special_features": "24-month savings"},
    {"provider_name": "Gexa Energy", "provider_website": "https://www.gexaenergy.com", "plan_name": "Gexa Saver Supreme 36", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 36, "rate_1000_cents": 12.0, "monthly_bill_1000": 129.95, "special_features": "Maximum long-term value"},
    {"provider_name": "Gexa Energy", "provider_website": "https://www.gexaenergy.com", "plan_name": "Gexa Green Supreme 12", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 13.7, "monthly_bill_1000": 146.95, "renewable_percent": 10.0, "special_features": "10% renewable content"},

    # Constellation - Residential
    {"provider_name": "Constellation", "provider_website": "https://www.constellation.com", "plan_name": "Constellation Standard 12", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 13.0, "monthly_bill_1000": 139.95, "special_features": "Competitive rate"},
    {"provider_name": "Constellation", "provider_website": "https://www.constellation.com", "plan_name": "Constellation Standard 24", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 12.4, "monthly_bill_1000": 133.95, "special_features": "Long-term value"},
    {"provider_name": "Constellation", "provider_website": "https://www.constellation.com", "plan_name": "Constellation 100% Green 12", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 14.3, "monthly_bill_1000": 152.95, "renewable_percent": 100.0, "special_features": "100% wind energy"},

    # Green Mountain Energy - Residential
    {"provider_name": "Green Mountain Energy", "provider_website": "https://www.greenmountainenergy.com", "plan_name": "Pollution Free e-Plus 12", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 14.7, "monthly_bill_1000": 156.95, "renewable_percent": 100.0, "special_features": "100% pollution-free wind"},
    {"provider_name": "Green Mountain Energy", "provider_website": "https://www.greenmountainenergy.com", "plan_name": "Pollution Free e-Plus 24", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 14.1, "monthly_bill_1000": 150.95, "renewable_percent": 100.0, "special_features": "Long-term renewable commitment"},
    {"provider_name": "Green Mountain Energy", "provider_website": "https://www.greenmountainenergy.com", "plan_name": "Go Big Solar 12", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 15.2, "monthly_bill_1000": 161.95, "renewable_percent": 100.0, "special_features": "100% Texas solar energy"},

    # Champion Energy - Residential
    {"provider_name": "Champion Energy", "provider_website": "https://www.championenergyservices.com", "plan_name": "Champ Saver 12", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 13.6, "monthly_bill_1000": 145.95, "special_features": "Straightforward pricing"},
    {"provider_name": "Champion Energy", "provider_website": "https://www.championenergyservices.com", "plan_name": "Champ Saver 24", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 13.0, "monthly_bill_1000": 139.95, "special_features": "Price protection guarantee"},
    {"provider_name": "Champion Energy", "provider_website": "https://www.championenergyservices.com", "plan_name": "Free Nights & Solar Days 12", "plan_type": "Free Nights", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 14.9, "monthly_bill_1000": 158.95, "renewable_percent": 20.0, "special_features": "Free nights + 20% solar"},

    # 4Change Energy - Residential
    {"provider_name": "4Change Energy", "provider_website": "https://www.4changeenergy.com", "plan_name": "Maxx Saver Select 12", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 13.3, "monthly_bill_1000": 142.95, "special_features": "Customer rewards program"},
    {"provider_name": "4Change Energy", "provider_website": "https://www.4changeenergy.com", "plan_name": "Maxx Saver Select 24", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 12.7, "monthly_bill_1000": 136.95, "special_features": "Earn reward points"},
    {"provider_name": "4Change Energy", "provider_website": "https://www.4changeenergy.com", "plan_name": "Maxx Guard 12", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 13.8, "monthly_bill_1000": 147.95, "special_features": "Rate stability"},

    # Pulse Power - Residential
    {"provider_name": "Pulse Power", "provider_website": "https://www.pulsepower.com", "plan_name": "Texas Simple 12", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 13.5, "monthly_bill_1000": 144.95, "special_features": "No gimmicks pricing"},
    {"provider_name": "Pulse Power", "provider_website": "https://www.pulsepower.com", "plan_name": "Texas Simple 24", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 12.9, "monthly_bill_1000": 138.95, "special_features": "Straightforward value"},
    {"provider_name": "Pulse Power", "provider_website": "https://www.pulsepower.com", "plan_name": "Big Savings 36", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 36, "rate_1000_cents": 12.3, "monthly_bill_1000": 132.95, "special_features": "Longest-term savings"},

    # Frontier Utilities - Residential
    {"provider_name": "Frontier Utilities", "provider_website": "https://www.frontierutilities.com", "plan_name": "Saver Plus 12", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 13.4, "monthly_bill_1000": 143.95, "special_features": "Budget-friendly"},
    {"provider_name": "Frontier Utilities", "provider_website": "https://www.frontierutilities.com", "plan_name": "Saver Plus 24", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 12.8, "monthly_bill_1000": 137.95, "special_features": "Long-term protection"},

    # TriEagle Energy - Residential
    {"provider_name": "TriEagle Energy", "provider_website": "https://www.trieagleenergy.com", "plan_name": "Soar 12", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 13.7, "monthly_bill_1000": 146.95, "special_features": "Hassle-free service"},
    {"provider_name": "TriEagle Energy", "provider_website": "https://www.trieagleenergy.com", "plan_name": "Soar 24", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 13.1, "monthly_bill_1000": 140.95, "special_features": "Rate lock guarantee"},

    # Express Energy - Residential
    {"provider_name": "Express Energy", "provider_website": "https://www.expressenergy.com", "plan_name": "Flash 12", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 13.9, "monthly_bill_1000": 148.95, "special_features": "Quick activation"},
    {"provider_name": "Express Energy", "provider_website": "https://www.expressenergy.com", "plan_name": "Flash 24", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 13.3, "monthly_bill_1000": 142.95, "special_features": "Fast service"},

    # Just Energy - Residential
    {"provider_name": "Just Energy", "provider_website": "https://www.justenergy.com", "plan_name": "Smart Choice 12", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 14.2, "monthly_bill_1000": 151.95, "special_features": "Smart meter compatible"},
    {"provider_name": "Just Energy", "provider_website": "https://www.justenergy.com", "plan_name": "Smart Choice 24", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 13.6, "monthly_bill_1000": 145.95, "special_features": "Energy insights included"},

    # Additional Residential Plans with variety
    {"provider_name": "TXU Energy", "provider_website": "https://www.txu.com", "plan_name": "TXU Energy Smart 12", "plan_type": "Variable", "service_type": "Residential", "zip_code": "75001", "contract_months": 1, "rate_1000_cents": 15.5, "monthly_bill_1000": 164.95, "special_features": "Month-to-month flexibility"},
    {"provider_name": "Reliant Energy", "provider_website": "https://www.reliant.com", "plan_name": "Reliant Clear Flex", "plan_type": "Variable", "service_type": "Residential", "zip_code": "75001", "contract_months": 1, "rate_1000_cents": 15.8, "monthly_bill_1000": 167.95, "special_features": "No long-term commitment"},
    {"provider_name": "Direct Energy", "provider_website": "https://www.directenergy.com", "plan_name": "Direct Flex 1", "plan_type": "Variable", "service_type": "Residential", "zip_code": "75001", "contract_months": 1, "rate_1000_cents": 16.0, "monthly_bill_1000": 169.95, "special_features": "Month-to-month"},
    {"provider_name": "Gexa Energy", "provider_website": "https://www.gexaenergy.com", "plan_name": "Gexa Energy Saver Choice 6", "plan_type": "Fixed", "service_type": "Residential", "zip_code": "75001", "contract_months": 6, "rate_1000_cents": 14.5, "monthly_bill_1000": 154.95, "special_features": "Short-term option"},
    {"provider_name": "Champion Energy", "provider_website": "https://www.championenergyservices.com", "plan_name": "Champ Free Power Weekends 12", "plan_type": "Free Weekends", "service_type": "Residential", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 16.2, "monthly_bill_1000": 171.95, "special_features": "Free power Sat-Sun"},

    # ========== COMMERCIAL PLANS (60+ plans) ==========

    # TXU Energy - Commercial
    {"provider_name": "TXU Energy", "provider_website": "https://www.txu.com", "plan_name": "Business Choice 12", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 11.8, "monthly_bill_1000": 127.95, "special_features": "Small business rate"},
    {"provider_name": "TXU Energy", "provider_website": "https://www.txu.com", "plan_name": "Business Choice 24", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 11.2, "monthly_bill_1000": 121.95, "special_features": "24-month price lock"},
    {"provider_name": "TXU Energy", "provider_website": "https://www.txu.com", "plan_name": "Business Choice 36", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 36, "rate_1000_cents": 10.6, "monthly_bill_1000": 115.95, "special_features": "Best long-term value"},
    {"provider_name": "TXU Energy", "provider_website": "https://www.txu.com", "plan_name": "Business Advantage 12", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 12.0, "monthly_bill_1000": 129.95, "renewable_percent": 10.0, "special_features": "10% renewable energy"},
    {"provider_name": "TXU Energy", "provider_website": "https://www.txu.com", "plan_name": "Business Select 18", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 18, "rate_1000_cents": 11.5, "monthly_bill_1000": 124.95, "special_features": "Mid-term option"},

    # Reliant Energy - Commercial
    {"provider_name": "Reliant Energy", "provider_website": "https://www.reliant.com", "plan_name": "Reliant Business 12", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 12.1, "monthly_bill_1000": 130.95, "special_features": "Trusted provider"},
    {"provider_name": "Reliant Energy", "provider_website": "https://www.reliant.com", "plan_name": "Reliant Business 24", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 11.5, "monthly_bill_1000": 124.95, "special_features": "Long-term savings"},
    {"provider_name": "Reliant Energy", "provider_website": "https://www.reliant.com", "plan_name": "Reliant Business 36", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 36, "rate_1000_cents": 10.9, "monthly_bill_1000": 118.95, "special_features": "Maximum savings"},
    {"provider_name": "Reliant Energy", "provider_website": "https://www.reliant.com", "plan_name": "Reliant Pro 12", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 12.3, "monthly_bill_1000": 132.95, "special_features": "Professional service"},
    {"provider_name": "Reliant Energy", "provider_website": "https://www.reliant.com", "plan_name": "Reliant Green Business 12", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 12.8, "monthly_bill_1000": 137.95, "renewable_percent": 100.0, "special_features": "100% renewable"},

    # Direct Energy - Commercial
    {"provider_name": "Direct Energy", "provider_website": "https://www.directenergy.com", "plan_name": "Business Power Plus 12", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 12.2, "monthly_bill_1000": 131.95, "special_features": "Small business focus"},
    {"provider_name": "Direct Energy", "provider_website": "https://www.directenergy.com", "plan_name": "Business Power Plus 24", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 11.6, "monthly_bill_1000": 125.95, "special_features": "Rate guarantee"},
    {"provider_name": "Direct Energy", "provider_website": "https://www.directenergy.com", "plan_name": "Business Power Plus 36", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 36, "rate_1000_cents": 11.0, "monthly_bill_1000": 119.95, "special_features": "Long-term protection"},
    {"provider_name": "Direct Energy", "provider_website": "https://www.directenergy.com", "plan_name": "Business Green 12", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 13.0, "monthly_bill_1000": 139.95, "renewable_percent": 100.0, "special_features": "100% wind energy"},

    # Gexa Energy - Commercial
    {"provider_name": "Gexa Energy", "provider_website": "https://www.gexaenergy.com", "plan_name": "Gexa Business 12", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 11.9, "monthly_bill_1000": 128.95, "special_features": "Competitive rate"},
    {"provider_name": "Gexa Energy", "provider_website": "https://www.gexaenergy.com", "plan_name": "Gexa Business 24", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 11.3, "monthly_bill_1000": 122.95, "special_features": "Price stability"},
    {"provider_name": "Gexa Energy", "provider_website": "https://www.gexaenergy.com", "plan_name": "Gexa Commercial Plus 36", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 36, "rate_1000_cents": 10.7, "monthly_bill_1000": 116.95, "special_features": "Long-term value"},
    {"provider_name": "Gexa Energy", "provider_website": "https://www.gexaenergy.com", "plan_name": "Gexa Business Saver 18", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 18, "rate_1000_cents": 11.6, "monthly_bill_1000": 125.95, "special_features": "Mid-term savings"},

    # Constellation - Commercial
    {"provider_name": "Constellation", "provider_website": "https://www.constellation.com", "plan_name": "Constellation Business 12", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 12.0, "monthly_bill_1000": 129.95, "special_features": "Reliable service"},
    {"provider_name": "Constellation", "provider_website": "https://www.constellation.com", "plan_name": "Constellation Business 24", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 11.4, "monthly_bill_1000": 123.95, "special_features": "Business focused"},
    {"provider_name": "Constellation", "provider_website": "https://www.constellation.com", "plan_name": "Constellation Business 36", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 36, "rate_1000_cents": 10.8, "monthly_bill_1000": 117.95, "special_features": "Maximum savings"},
    {"provider_name": "Constellation", "provider_website": "https://www.constellation.com", "plan_name": "Constellation Green Business 12", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 12.7, "monthly_bill_1000": 136.95, "renewable_percent": 100.0, "special_features": "100% renewable"},

    # Green Mountain Energy - Commercial
    {"provider_name": "Green Mountain Energy", "provider_website": "https://www.greenmountainenergy.com", "plan_name": "Business Pollution Free 12", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 13.2, "monthly_bill_1000": 141.95, "renewable_percent": 100.0, "special_features": "100% wind energy"},
    {"provider_name": "Green Mountain Energy", "provider_website": "https://www.greenmountainenergy.com", "plan_name": "Business Pollution Free 24", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 12.6, "monthly_bill_1000": 135.95, "renewable_percent": 100.0, "special_features": "Long-term green commitment"},

    # Champion Energy - Commercial
    {"provider_name": "Champion Energy", "provider_website": "https://www.championenergyservices.com", "plan_name": "Business Champion 12", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 12.1, "monthly_bill_1000": 130.95, "special_features": "Business reliability"},
    {"provider_name": "Champion Energy", "provider_website": "https://www.championenergyservices.com", "plan_name": "Business Champion 24", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 11.5, "monthly_bill_1000": 124.95, "special_features": "Price protection"},
    {"provider_name": "Champion Energy", "provider_website": "https://www.championenergyservices.com", "plan_name": "Business Champion 36", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 36, "rate_1000_cents": 10.9, "monthly_bill_1000": 118.95, "special_features": "Long-term savings"},

    # 4Change Energy - Commercial
    {"provider_name": "4Change Energy", "provider_website": "https://www.4changeenergy.com", "plan_name": "Business Maxx 12", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 12.0, "monthly_bill_1000": 129.95, "special_features": "Rewards program"},
    {"provider_name": "4Change Energy", "provider_website": "https://www.4changeenergy.com", "plan_name": "Business Maxx 24", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 11.4, "monthly_bill_1000": 123.95, "special_features": "Earn business rewards"},

    # Pulse Power - Commercial
    {"provider_name": "Pulse Power", "provider_website": "https://www.pulsepower.com", "plan_name": "Business Simple 12", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 11.9, "monthly_bill_1000": 128.95, "special_features": "Straightforward pricing"},
    {"provider_name": "Pulse Power", "provider_website": "https://www.pulsepower.com", "plan_name": "Business Simple 24", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 11.3, "monthly_bill_1000": 122.95, "special_features": "No hidden fees"},
    {"provider_name": "Pulse Power", "provider_website": "https://www.pulsepower.com", "plan_name": "Business Simple 36", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 36, "rate_1000_cents": 10.7, "monthly_bill_1000": 116.95, "special_features": "Long-term value"},

    # Frontier Utilities - Commercial
    {"provider_name": "Frontier Utilities", "provider_website": "https://www.frontierutilities.com", "plan_name": "Business Saver 12", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 12.2, "monthly_bill_1000": 131.95, "special_features": "Small business rate"},
    {"provider_name": "Frontier Utilities", "provider_website": "https://www.frontierutilities.com", "plan_name": "Business Saver 24", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 11.6, "monthly_bill_1000": 125.95, "special_features": "Budget friendly"},

    # TriEagle Energy - Commercial
    {"provider_name": "TriEagle Energy", "provider_website": "https://www.trieagleenergy.com", "plan_name": "Business Soar 12", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 12.1, "monthly_bill_1000": 130.95, "special_features": "Business support"},
    {"provider_name": "TriEagle Energy", "provider_website": "https://www.trieagleenergy.com", "plan_name": "Business Soar 24", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 11.5, "monthly_bill_1000": 124.95, "special_features": "Rate lock"},

    # Express Energy - Commercial
    {"provider_name": "Express Energy", "provider_website": "https://www.expressenergy.com", "plan_name": "Business Flash 12", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 12.3, "monthly_bill_1000": 132.95, "special_features": "Quick setup"},
    {"provider_name": "Express Energy", "provider_website": "https://www.expressenergy.com", "plan_name": "Business Flash 24", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 11.7, "monthly_bill_1000": 126.95, "special_features": "Fast activation"},

    # Just Energy - Commercial
    {"provider_name": "Just Energy", "provider_website": "https://www.justenergy.com", "plan_name": "Business Smart 12", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 12.4, "monthly_bill_1000": 133.95, "special_features": "Smart meter compatible"},
    {"provider_name": "Just Energy", "provider_website": "https://www.justenergy.com", "plan_name": "Business Smart 24", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 24, "rate_1000_cents": 11.8, "monthly_bill_1000": 127.95, "special_features": "Energy analytics"},

    # Additional Commercial Plans with variety
    {"provider_name": "TXU Energy", "provider_website": "https://www.txu.com", "plan_name": "Business Flex 6", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 6, "rate_1000_cents": 13.0, "monthly_bill_1000": 139.95, "special_features": "Short-term option"},
    {"provider_name": "Reliant Energy", "provider_website": "https://www.reliant.com", "plan_name": "Business Flex Variable", "plan_type": "Variable", "service_type": "Commercial", "zip_code": "75001", "contract_months": 1, "rate_1000_cents": 14.5, "monthly_bill_1000": 154.95, "special_features": "Month-to-month"},
    {"provider_name": "Direct Energy", "provider_website": "https://www.directenergy.com", "plan_name": "Business Variable 1", "plan_type": "Variable", "service_type": "Commercial", "zip_code": "75001", "contract_months": 1, "rate_1000_cents": 14.8, "monthly_bill_1000": 157.95, "special_features": "No contract"},
    {"provider_name": "Gexa Energy", "provider_website": "https://www.gexaenergy.com", "plan_name": "Business Economy 12", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 11.7, "monthly_bill_1000": 126.95, "special_features": "Cost-effective"},
    {"provider_name": "Constellation", "provider_website": "https://www.constellation.com", "plan_name": "Business Premium 18", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 18, "rate_1000_cents": 11.7, "monthly_bill_1000": 126.95, "special_features": "Premium service"},
    {"provider_name": "Champion Energy", "provider_website": "https://www.championenergyservices.com", "plan_name": "Business Value 12", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 12, "rate_1000_cents": 11.8, "monthly_bill_1000": 127.95, "special_features": "Best value"},
    {"provider_name": "4Change Energy", "provider_website": "https://www.4changeenergy.com", "plan_name": "Business Guard 36", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 36, "rate_1000_cents": 10.6, "monthly_bill_1000": 115.95, "special_features": "Maximum protection"},
    {"provider_name": "Pulse Power", "provider_website": "https://www.pulsepower.com", "plan_name": "Business Power 18", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 18, "rate_1000_cents": 11.6, "monthly_bill_1000": 125.95, "special_features": "Mid-term value"},
    {"provider_name": "Frontier Utilities", "provider_website": "https://www.frontierutilities.com", "plan_name": "Business Choice 36", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 36, "rate_1000_cents": 10.8, "monthly_bill_1000": 117.95, "special_features": "Long-term protection"},
    {"provider_name": "TriEagle Energy", "provider_website": "https://www.trieagleenergy.com", "plan_name": "Business Premier 36", "plan_type": "Fixed", "service_type": "Commercial", "zip_code": "75001", "contract_months": 36, "rate_1000_cents": 10.9, "monthly_bill_1000": 118.95, "special_features": "Premier service"},
]
