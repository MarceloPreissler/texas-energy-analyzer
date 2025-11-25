# Use official Playwright image which includes Python and browsers
# This guarantees compatibility and missing dependencies are not an issue
FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

WORKDIR /app

# Install system dependencies
# build-essential and python3-dev are REQUIRED for compiling C extensions (psycopg2, cryptography, etc.)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    python3-dev \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (required because pip install overrides system playwright)
RUN playwright install chromium

# Copy application code
COPY . .

# Create database directory for SQLite (if used)
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Health check
# Health check removed to rely on Render's native checks and avoid timeouts
# HEALTHCHECK --interval=30s --timeout=15s --start-period=60s --retries=5 \
#     CMD python -c "import os, requests; port = os.getenv('PORT', '8000'); requests.get(f'http://localhost:{port}/health', timeout=10)"

# Run the application
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"
