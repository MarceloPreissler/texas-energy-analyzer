# Texas Energy Analyzer - Production Deployment Guide

## Overview

This guide covers deploying the Texas Energy Analyzer to production with full security features, automated scraping, caching, and monitoring.

## Features Implemented

### 1. Automated Scraping
- **Schedule**: Daily at 2:00 AM Central Time
- **Source**: PowerToChoose.org (official PUCT data)
- **Coverage**: All major Texas cities (Dallas, Houston, Austin, San Antonio, Fort Worth)
- **Technology**: APScheduler with background jobs

### 2. Authentication & Security
- **API Key Authentication**: Required for scraper endpoint
- **Rate Limiting**: 100 requests/hour default, 10/minute for root endpoint
- **CORS Protection**: Restricted to whitelisted domains
- **Host Validation**: Prevents host header attacks
- **Password Hashing**: bcrypt for secure password storage

### 3. Caching Layer
- **Technology**: Redis with in-memory fallback
- **TTL**: 1 hour for plans, 30 minutes for providers
- **Automatic**: Decorator-based caching on expensive queries

### 4. Docker Deployment
- **Multi-service**: Backend, Frontend, PostgreSQL, Redis
- **Health Checks**: Automated monitoring for all services
- **Persistent Storage**: Volume mounting for database and cache
- **Production-ready**: Optimized builds with nginx for frontend

## Quick Start (Docker)

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB RAM minimum
- 10GB disk space

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/texas-energy-analyzer.git
cd texas-energy-analyzer
```

### Step 2: Configure Environment
```bash
# Copy production environment template
cp .env.production .env

# Edit .env and update:
# 1. POSTGRES_PASSWORD - Strong database password
# 2. SECRET_KEY - Run: openssl rand -hex 32
# 3. API_KEY - Run: openssl rand -hex 32
# 4. ALLOWED_ORIGINS - Your production domain(s)
```

### Step 3: Generate Security Keys
```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate API_KEY
openssl rand -hex 32

# Update .env file with these values
```

### Step 4: Deploy with Docker Compose
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### Step 5: Initialize Database
```bash
# Database tables are auto-created on startup
# To manually trigger a scrape (requires API key):
curl -X POST http://localhost:8000/plans/scrape?source=powertochoose \
  -H "X-API-Key: YOUR_API_KEY_HERE"
```

### Step 6: Access Application
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Cloud Deployment

### AWS (Elastic Beanstalk + RDS)

1. **Install AWS CLI and EB CLI**
```bash
pip install awscli awsebcli
```

2. **Initialize EB Application**
```bash
cd backend
eb init -p docker texas-energy-analyzer
```

3. **Create RDS PostgreSQL Instance**
```bash
eb create production --database.engine postgres --database.username energyuser
```

4. **Set Environment Variables**
```bash
eb setenv SECRET_KEY=your_secret_key \
  API_KEY=your_api_key \
  DATABASE_URL=your_rds_url \
  REDIS_HOST=your_redis_host
```

5. **Deploy**
```bash
eb deploy
```

### Azure (Container Instances)

1. **Create Resource Group**
```bash
az group create --name texas-energy-rg --location eastus
```

2. **Create Container Registry**
```bash
az acr create --resource-group texas-energy-rg \
  --name texasenergyregistry --sku Basic
```

3. **Build and Push Images**
```bash
az acr build --registry texasenergyregistry \
  --image texas-energy-backend:latest ./backend
az acr build --registry texasenergyregistry \
  --image texas-energy-frontend:latest ./frontend
```

4. **Create Container Instances**
```bash
az container create --resource-group texas-energy-rg \
  --name texas-energy-backend \
  --image texasenergyregistry.azurecr.io/texas-energy-backend:latest \
  --environment-variables DATABASE_URL=... API_KEY=... \
  --ports 8000
```

### Heroku

1. **Install Heroku CLI**
```bash
# See https://devcenter.heroku.com/articles/heroku-cli
```

2. **Create App**
```bash
heroku create texas-energy-analyzer
```

3. **Add PostgreSQL and Redis**
```bash
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini
```

4. **Set Environment Variables**
```bash
heroku config:set SECRET_KEY=your_secret_key
heroku config:set API_KEY=your_api_key
```

5. **Deploy**
```bash
git push heroku main
```

## API Authentication

### Using API Key

All scraper endpoints require authentication via `X-API-Key` header.

**Example: Trigger Manual Scrape**
```bash
curl -X POST http://localhost:8000/plans/scrape?source=powertochoose \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json"
```

**Example: Python**
```python
import requests

headers = {
    "X-API-Key": "your-api-key-here"
}

response = requests.post(
    "http://localhost:8000/plans/scrape?source=powertochoose",
    headers=headers
)
print(response.json())
```

**Example: JavaScript**
```javascript
fetch('http://localhost:8000/plans/scrape?source=powertochoose', {
  method: 'POST',
  headers: {
    'X-API-Key': 'your-api-key-here',
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

## Scheduler Configuration

### Default Schedule
- **Time**: 2:00 AM Central Time daily
- **Job**: Full PowerToChoose.org scrape
- **Coverage**: All Texas zip codes

### Customize Schedule

Edit `backend/app/scheduler.py`:

```python
# Change schedule time
scheduler.add_job(
    scrape_job,
    trigger=CronTrigger(hour=4, minute=30),  # 4:30 AM
    id="daily_scrape",
    name="PowerToChoose Daily Scrape",
    replace_existing=True,
)

# Add hourly scrape
scheduler.add_job(
    scrape_job,
    trigger=CronTrigger(minute=0),  # Every hour
    id="hourly_scrape",
    name="Hourly Scrape",
    replace_existing=True,
)
```

### Run Scrape on Startup

Uncomment in `backend/app/scheduler.py`:

```python
scheduler.add_job(
    scrape_job,
    trigger='date',
    id='startup_scrape',
    name='Startup Scrape'
)
```

## Redis Caching

### Connection

The application automatically connects to Redis if available, falls back to in-memory cache if not.

### Configuration

Environment variables (`.env`):
```
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
CACHE_TTL=3600  # 1 hour default
```

### Monitoring Cache

```bash
# Connect to Redis CLI
docker exec -it texas-energy-redis redis-cli

# View all keys
KEYS *

# Get cache value
GET plans:provider=TXU:plan_type=Fixed

# Clear all cache
FLUSHDB
```

### Manual Cache Control

```python
from app.cache import get_cache, set_cache, delete_cache, clear_cache

# Get cached value
value = get_cache("my_key")

# Set cache with custom TTL
set_cache("my_key", {"data": "value"}, ttl=7200)

# Delete specific key
delete_cache("my_key")

# Clear all cache
clear_cache()
```

## Monitoring & Maintenance

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Database connectivity
curl http://localhost:8000/plans/providers

# Redis status
docker exec texas-energy-redis redis-cli ping
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Database Backup

```bash
# Backup PostgreSQL
docker exec texas-energy-db pg_dump -U energyuser texas_energy > backup.sql

# Restore
docker exec -i texas-energy-db psql -U energyuser texas_energy < backup.sql
```

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

## Security Best Practices

### 1. API Key Rotation
```bash
# Generate new API key
openssl rand -hex 32

# Update .env
# Restart services
docker-compose restart backend
```

### 2. Database Security
- Use strong passwords (16+ characters)
- Restrict PostgreSQL to internal network
- Enable SSL for production databases
- Regular backups (daily minimum)

### 3. CORS Configuration

Edit `backend/app/main.py`:
```python
allowed_origins = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
```

### 4. Rate Limiting

Adjust limits in `backend/app/main.py`:
```python
limiter = Limiter(key_func=get_remote_address, default_limits=["200/hour"])
```

### 5. HTTPS/SSL
- Use nginx or cloud load balancer for SSL termination
- Obtain certificate from Let's Encrypt
- Redirect HTTP to HTTPS

## Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Database connection failure: Check DATABASE_URL
# - Port already in use: Change port in docker-compose.yml
# - Permission errors: Check file permissions
```

### Redis connection fails
```bash
# Check Redis status
docker-compose ps redis

# Restart Redis
docker-compose restart redis

# Application will fall back to in-memory cache
```

### Playwright scraper fails
```bash
# Install browser dependencies
docker exec -it texas-energy-backend python -m playwright install-deps

# Increase timeout in scraper.py
# Change: timeout=30000 to timeout=60000
```

### High memory usage
```bash
# Clear Redis cache
docker exec texas-energy-redis redis-cli FLUSHDB

# Reduce cache TTL in .env
CACHE_TTL=1800  # 30 minutes
```

## Support

For issues or questions:
1. Check application logs: `docker-compose logs -f`
2. Review health endpoints: `/health`
3. Check Redis connectivity: `redis-cli ping`
4. Review documentation: `/docs`

## Cost Estimates

### AWS (Elastic Beanstalk)
- **EC2 (t3.small)**: $15/month
- **RDS PostgreSQL (db.t3.micro)**: $15/month
- **ElastiCache Redis (cache.t3.micro)**: $12/month
- **Total**: ~$42/month

### Azure (Container Instances)
- **Container Instances**: $30/month
- **Azure Database for PostgreSQL**: $25/month
- **Azure Cache for Redis**: $20/month
- **Total**: ~$75/month

### Heroku
- **Dyno (Hobby)**: $7/month
- **PostgreSQL (Mini)**: $5/month
- **Redis (Mini)**: $3/month
- **Total**: ~$15/month (best for testing)
