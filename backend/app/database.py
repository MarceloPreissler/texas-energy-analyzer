"""
Database configuration and session management.

This module initializes a SQLAlchemy engine and session factory.  The engine
configuration is controlled via an environment variable `DATABASE_URL`.  If
`DATABASE_URL` is not defined, an in‑memory SQLite database is used by
default.  A helper function `get_db()` yields a session for use in FastAPI
dependencies.
"""
from __future__ import annotations

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Read database URL from environment; fall back to SQLite.  SQLite is
# convenient for local development but Postgres is recommended in
# production.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./plans.db")

# When using SQLite, we must enable check_same_thread to allow multiple
# threads to access the connection.  With other databases this is ignored.
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

# Create a session factory.  Sessions are not thread‑safe; each request
# should use its own session instance.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Yield a new SQLAlchemy session for FastAPI dependencies."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()