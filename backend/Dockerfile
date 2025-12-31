# Use official Playwright image which includes Python and pre-installed browsers
# Version: 2024-12-30-v2 (force rebuild)
FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

WORKDIR /app

# Set Playwright browser path to use the pre-installed browsers
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

# Ensure Playwright browsers are installed (image has them, but verify)
RUN playwright install chromium && playwright install-deps chromium

# Copy application code
COPY . .

# Create database directory for SQLite (if used)
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Run the application with browser check/install at startup
CMD sh -c "playwright install chromium 2>/dev/null || true && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"
