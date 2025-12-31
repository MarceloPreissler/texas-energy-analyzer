# Use official Playwright image which includes Python and pre-installed browsers
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

# Run the application
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"
