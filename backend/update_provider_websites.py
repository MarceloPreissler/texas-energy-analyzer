"""
Update provider websites in the database.

Run this script to add website URLs to existing providers.
"""
from app.database import SessionLocal
from app import models

# Provider website mappings
PROVIDER_WEBSITES = {
    "Gexa": "https://www.gexaenergy.com",
    "Gexa Energy": "https://www.gexaenergy.com",
    "TXU": "https://www.txu.com",
    "TXU Energy": "https://www.txu.com",
    "Direct Energy": "https://www.directenergy.com",
    "Reliant": "https://www.reliant.com",
    "Reliant Energy": "https://www.reliant.com",
    "Constellation": "https://www.constellation.com/solutions/for-your-home/electricity-in-texas.html",
    "Green Mountain Energy": "https://www.greenmountainenergy.com",
    "Champion Energy": "https://www.championenergyservices.com",
    "4Change Energy": "https://www.4changeenergy.com",
    "Pulse Power": "https://www.pulsepower.com",
    "Cirro Energy": "https://www.cirroenergy.com",
    "Frontier Utilities": "https://www.frontierutilities.com",
    "Discount Power": "https://www.discountpower.com",
    "Just Energy": "https://www.justenergy.com",
    "Amigo Energy": "https://www.amigoenergy.com",
    "TriEagle Energy": "https://www.trieagleenergy.com",
    "Veteran Energy": "https://www.veteranenergy.com",
    "Express Energy": "https://www.expressenergy.com",
    "Startex Power": "https://www.startexpower.com",
    "Payless Power": "https://www.paylesspower.com",
    "Entrust Energy": "https://www.entrustenergy.com",
    "First Choice Power": "https://www.firstchoicepower.com",
}

def update_websites():
    """Update provider websites in database."""
    db = SessionLocal()
    try:
        providers = db.query(models.Provider).all()
        updated_count = 0

        for provider in providers:
            # Try exact match first
            if provider.name in PROVIDER_WEBSITES:
                provider.website = PROVIDER_WEBSITES[provider.name]
                updated_count += 1
                print(f"[OK] Updated {provider.name}: {provider.website}")
            # Try partial match
            else:
                for key, url in PROVIDER_WEBSITES.items():
                    if key.lower() in provider.name.lower() or provider.name.lower() in key.lower():
                        provider.website = url
                        updated_count += 1
                        print(f"[OK] Updated {provider.name} (matched {key}): {url}")
                        break
                else:
                    print(f"[WARN] No website found for: {provider.name}")

        db.commit()
        print(f"\n[SUCCESS] Updated {updated_count} providers with websites")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    update_websites()
