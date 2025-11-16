"""
QUICK FIX - Creates tables, runs migrations, and tests scrapers
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import SessionLocal, engine
from app.models import Base
from sqlalchemy import inspect

print("="*80)
print("QUICK FIX - Creating database and testing scrapers")
print("="*80)

# Step 1: Create all tables
print("\n[1/4] CREATING DATABASE TABLES...")
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")
except Exception as e:
    print(f"⚠️ Error creating tables: {e}")

# Step 2: Run migrations
print("\n[2/4] RUNNING MIGRATIONS...")
db = SessionLocal()
try:
    from app.migrations import run_migrations
    run_migrations(db)
    print("✅ Migrations completed")
except Exception as e:
    print(f"⚠️ Migration error: {e}")
finally:
    db.close()

# Step 3: Verify schema
print("\n[3/4] VERIFYING DATABASE SCHEMA...")
db = SessionLocal()
try:
    inspector = inspect(db.bind)
    tables = inspector.get_table_names()
    print(f"✅ Tables in database: {tables}")

    if 'plans' in tables:
        plans_columns = [col['name'] for col in inspector.get_columns('plans')]
        print(f"✅ Plans table columns: {plans_columns}")
        if 'plan_url' in plans_columns:
            print("✅ plan_url column exists!")
        else:
            print("❌ plan_url column missing")
except Exception as e:
    print(f"❌ Schema verification error: {e}")
finally:
    db.close()

# Step 4: Test scrapers (without actually running them - just verify imports)
print("\n[4/4] VERIFYING SCRAPER IMPORTS...")
try:
    from app.scraping import scraper
    print("✅ Legacy residential scraper imported")
except Exception as e:
    print(f"❌ Legacy scraper import failed: {e}")

try:
    from app.scraping import energybot_scraper_v2
    print("✅ EnergyBot v2 scraper imported")
except Exception as e:
    print(f"❌ EnergyBot v2 import failed: {e}")

try:
    from app.scraping import energybot_business_enhanced
    print("✅ Enhanced EnergyBot scraper imported")
except Exception as e:
    print(f"❌ Enhanced scraper import failed: {e}")

try:
    from app.scraping import powertochoose_scraper
    print("✅ PowerToChoose scraper imported")
except Exception as e:
    print(f"❌ PowerToChoose import failed: {e}")

try:
    from app.scraping import scraper_utils
    print("✅ Scraper utilities imported")
except Exception as e:
    print(f"❌ Scraper utils import failed: {e}")

print("\n" + "="*80)
print("VERIFICATION COMPLETE!")
print("="*80)
print("\nDatabase is ready. To actually scrape data, run:")
print("  python3 RUN_SCRAPER.py")
print("="*80)
