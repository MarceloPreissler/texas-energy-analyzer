"""
Entry point for the FastAPI application.

This module initializes the database, includes routers, and creates the
application instance.  When run directly, it ensures that all tables
exist.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine
from . import models
from .api import plans as plans_router

# Create database tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Texas Commercial Energy Market Analyzer")

# Allow CORS in development; restrict origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(plans_router.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Texas Commercial Energy Market Analyzer API"}