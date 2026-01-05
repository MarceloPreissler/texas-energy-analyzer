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

# Verify browsers are available at /ms-playwright (pre-installed in base image)
# Also install deps to ensure all system libraries are present
RUN playwright install-deps chromium

# Create symlinks to ensure both paths work (belt and suspenders)
RUN mkdir -p /root/.cache && \
    ln -sf /ms-playwright /root/.cache/ms-playwright 2>/dev/null || true && \
    echo "Playwright browsers path: $PLAYWRIGHT_BROWSERS_PATH" && \
    ls -la /ms-playwright/ 2>/dev/null || echo "Checking /ms-playwright..." && \
    playwright --version

# Copy application code
COPY . .

# Create database directory for SQLite (if used)
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Run the application - browsers should already be installed
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
