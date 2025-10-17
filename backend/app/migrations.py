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
                logger.info("[Migrations] Successfully added plan_url column")
            else:
                logger.info("[Migrations] plan_url column already exists")

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
            logger.info("[Migrations] Successfully created tdus table")

            # Load TDU data
            logger.info("[Migrations] Loading TDU data...")
            from .tdu_data import get_all_tdus
            from . import schemas, crud

            tdus = get_all_tdus()
            for tdu_data in tdus:
                try:
                    tdu_create = schemas.TDUCreate(**tdu_data)
                    crud.create_or_update_tdu(db, tdu_create)
                    logger.info(f"[Migrations] Loaded TDU: {tdu_data['name']}")
                except Exception as e:
                    logger.error(f"[Migrations] Error loading TDU {tdu_data.get('name')}: {e}")

            logger.info("[Migrations] Successfully loaded all TDU data")
        else:
            logger.info("[Migrations] tdus table already exists")

        logger.info("[Migrations] All migrations completed successfully")

    except Exception as e:
        logger.error(f"[Migrations] Error during migration: {e}")
        import traceback
        traceback.print_exc()
        raise


def ensure_migrations(db: Session):
    """
    Ensure all migrations are applied before starting the application.

    This is called during application startup to make sure the database
    schema is up to date.
    """
    try:
        run_migrations(db)
    except Exception as e:
        logger.error(f"[Migrations] Failed to apply migrations: {e}")
        # Don't crash the app - migrations might have partially succeeded
        # The error is logged and can be investigated
