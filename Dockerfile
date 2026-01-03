# Use official Playwright image which includes Python and pre-installed browsers
# Version: 2026-01-03-v2 (root Dockerfile for Railway - fix commercial scraping)
FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

WORKDIR /app

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

# Copy requirements from backend folder and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers to default location AND set up symlinks
# This ensures browsers are found regardless of which path Playwright checks
RUN playwright install chromium && playwright install-deps chromium

# Create symlink from default cache location to /ms-playwright if needed
RUN if [ -d "/ms-playwright" ]; then \
        ln -sf /ms-playwright /root/.cache/ms-playwright 2>/dev/null || true; \
    fi

# Also set env var for runtime (some Playwright versions check this)
ENV PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright

# Copy backend application code
COPY backend/ .

# Create database directory for SQLite (if used)
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Run the application - browsers should already be installed
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
