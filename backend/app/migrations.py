"""
Automatic database migrations for production deployments.

This module handles schema changes that need to be applied to existing databases
when deploying new versions. It runs automatically on application startup.
"""
import logging
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def run_migrations(db: Session):
    """
    Run all pending database migrations.

    This function checks for missing columns and tables and adds them if needed.
    Safe to run multiple times - will only apply changes that are missing.
    """
    logger.info("[Migrations] Checking for pending database migrations...")

    try:
        # Get database inspector
        inspector = inspect(db.bind)

        # Migration 1: Add plan_url column to plans table
        if 'plans' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('plans')]
            if 'plan_url' not in columns:
                logger.info("[Migrations] Adding plan_url column to plans table...")
                db.execute(text("ALTER TABLE plans ADD COLUMN plan_url VARCHAR"))
                db.commit()
                logger.info("[Migrations] OK - Added plan_url column")
            else:
                logger.info("[Migrations] OK - plan_url column exists")

            if 'renewable_percent' not in columns:
                logger.info("[Migrations] Adding renewable_percent column to plans table...")
                db.execute(text("ALTER TABLE plans ADD COLUMN renewable_percent INTEGER"))
                db.commit()
                logger.info("[Migrations] OK - Added renewable_percent column")
            else:
                logger.info("[Migrations] OK - renewable_percent column exists")

            if 'cancellation_fee' not in columns:
                logger.info("[Migrations] Adding cancellation_fee column to plans table...")
                db.execute(text("ALTER TABLE plans ADD COLUMN cancellation_fee FLOAT"))
                db.commit()
                logger.info("[Migrations] OK - Added cancellation_fee column")
            else:
                logger.info("[Migrations] OK - cancellation_fee column exists")

            indexes = [idx['name'] for idx in inspector.get_indexes('plans')]
            if 'ix_plans_zip_code' not in indexes:
                logger.info("[Migrations] Adding ix_plans_zip_code index...")
                db.execute(text("CREATE INDEX ix_plans_zip_code ON plans (zip_code)"))
                db.commit()
                logger.info("[Migrations] OK - Added ix_plans_zip_code index")
            else:
                logger.info("[Migrations] OK - ix_plans_zip_code index exists")

        # Migration 2: Create tdus table if it doesn't exist
        if 'tdus' not in inspector.get_table_names():
            logger.info("[Migrations] Creating tdus table...")
            db.execute(text("""
                CREATE TABLE tdus (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR NOT NULL UNIQUE,
                    full_name VARCHAR,
                    website VARCHAR,
                    service_area TEXT,
                    major_cities TEXT,
                    customers INTEGER,
                    monthly_charge FLOAT,
                    delivery_charge_per_kwh FLOAT,
                    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    rate_effective_date VARCHAR
                )
            """))
            db.commit()
            logger.info("[Migrations] OK - Created tdus table")
            logger.info("[Migrations] TDU data loading skipped - use /admin/load-tdus endpoint")
        else:
            logger.info("[Migrations] OK - tdus table exists")

        logger.info("[Migrations] All migrations completed")

    except Exception as e:
        logger.error(f"[Migrations] Migration error: {e}")
        # Log but don't crash - some migrations may have succeeded
        import traceback
        traceback.print_exc()


def ensure_migrations(db: Session):
    """
    Ensure all migrations are applied before starting the application.

    This is called during application startup to make sure the database
    schema is up to date.

    IMPORTANT: This function never raises exceptions - it only logs errors.
    This ensures the app can start even if migrations fail.
    """
    try:
        run_migrations(db)
    except Exception as e:
        logger.error(f"[Migrations] FAILED - migrations did not complete: {e}")
        logger.error("[Migrations] App will continue startup - check logs for details")
        # Don't crash the app - migrations might have partially succeeded
        # The app can still run with the old schema
