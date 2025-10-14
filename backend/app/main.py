"""
Entry point for the FastAPI application with full production features.

Features:
- Database initialization
- Rate limiting and security middleware
- Scheduled background scraping
- Redis caching layer
- API key authentication
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .database import engine
from . import models
from .api import plans as plans_router
from .scheduler import start_scheduler, stop_scheduler
from .logging_config import setup_logging

# Initialize logging
setup_logging(log_level="INFO")
logger = logging.getLogger(__name__)

# Create database tables on startup
models.Base.metadata.create_all(bind=engine)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/hour"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Application starting up...")
    logger.info("Starting background scheduler...")
    start_scheduler()
    yield
    # Shutdown
    logger.info("Application shutting down...")
    logger.info("Stopping background scheduler...")
    stop_scheduler()

app = FastAPI(
    title="Texas Commercial Energy Market Analyzer",
    description="Secure API for Texas electricity plan comparison",
    version="2.0.0",
    docs_url="/docs",  # Can disable in production
    redoc_url="/redoc",
    lifespan=lifespan  # Enable background scheduler
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS - restrict in production
allowed_origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Alternative
    "http://127.0.0.1:5173",
    # Add your production domain here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Only allow needed methods
    allow_headers=["Content-Type", "Authorization"],
)

# Prevent host header attacks
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.local"]
)

# Include routers
app.include_router(plans_router.router)


@app.get("/")
@limiter.limit("10/minute")
async def read_root(request: Request):
    """API root endpoint with rate limiting."""
    return {
        "message": "Welcome to the Texas Commercial Energy Market Analyzer API",
        "version": "1.0.0",
        "endpoints": {
            "plans": "/plans",
            "providers": "/plans/providers",
            "scrape": "/plans/scrape (POST)",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "texas-energy-analyzer", "version": "2.0.0"}