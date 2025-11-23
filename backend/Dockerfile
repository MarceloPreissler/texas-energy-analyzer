# Single-stage build for reliability
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and dependencies
# We install directly into the system to avoid path issues
RUN pip install playwright && \
    playwright install chromium && \
    playwright install-deps chromium

# Copy application code
COPY . .

# Create database directory for SQLite (if used)
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=15s --start-period=60s --retries=5 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=10)"

# Run the application
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"
