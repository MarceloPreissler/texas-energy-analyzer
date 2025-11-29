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

# Set fixed location for Playwright browsers
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Install Playwright browsers
RUN pip install --user playwright && \
    mkdir -p /ms-playwright && \
    python -m playwright install chromium && \
    python -m playwright install-deps chromium

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Set fixed location for Playwright browsers
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local
COPY --from=builder /ms-playwright /ms-playwright

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH
# Install Playwright browsers (required because pip install overrides system playwright)
# Install Playwright browsers and dependencies
RUN playwright install-deps
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
