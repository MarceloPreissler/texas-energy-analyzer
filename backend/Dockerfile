# Use official Playwright image which includes Python and pre-installed browsers
# Version: 2026-01-04-v1 (fix Playwright browser path - use /ms-playwright directly)
FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

WORKDIR /app

# CRITICAL: Set Playwright browser path to use pre-installed browsers FIRST
# The base image has browsers in /ms-playwright - we must use this path
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Install system dependencies for psycopg2 and other packages
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

# Install Playwright browsers to match the installed pip package version
# This ensures the browser version matches what playwright-stealth expects
RUN playwright install chromium && \
    playwright install-deps chromium

# Verify installation
RUN echo "Playwright version:" && playwright --version && \
    echo "Browsers installed at:" && ls -la /root/.cache/ms-playwright/ 2>/dev/null || ls -la /ms-playwright/ 2>/dev/null || echo "Checking paths..."

# Copy application code
COPY . .

# Create database directory for SQLite (if used)
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Run the application - browsers should already be installed.
# Bind to $PORT when the platform provides it (Render/Railway set PORT).
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
