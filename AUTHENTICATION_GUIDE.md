# Authentication & Security Guide

## Overview

The Texas Energy Analyzer uses API key authentication to protect sensitive endpoints like data scraping. This guide covers authentication setup, key management, and security best practices.

## Authentication System

### API Key Authentication

The application uses **API key authentication** via the `X-API-Key` HTTP header.

**Protected Endpoints:**
- `POST /plans/scrape` - Manual data scraping

**Public Endpoints:**
- `GET /` - API information
- `GET /health` - Health check
- `GET /plans/` - List plans
- `GET /plans/providers` - List providers
- `GET /plans/{id}` - Get single plan

## Setup Instructions

### 1. Generate API Key

Generate a secure random API key using OpenSSL:

```bash
# Generate 32-byte random key (256 bits)
openssl rand -hex 32
```

**Example output:**
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

### 2. Configure Environment

Add the API key to your `.env` file:

```bash
# Generate API key first
export API_KEY=$(openssl rand -hex 32)

# Add to .env file
echo "API_KEY=$API_KEY" >> .env
```

**Example `.env` file:**
```env
# Database
DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/texas_energy

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Security - CHANGE THESE IN PRODUCTION
SECRET_KEY=your_secret_key_here_minimum_32_characters_long_change_me
API_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

### 3. Restart Application

```bash
# If using Docker
docker-compose restart backend

# If running locally
# Stop the backend (Ctrl+C) and restart:
cd backend
.venv/Scripts/python -m uvicorn app.main:app --reload
```

## Using API Keys

### cURL Examples

```bash
# Trigger PowerToChoose scrape
curl -X POST "http://localhost:8000/plans/scrape?source=powertochoose" \
  -H "X-API-Key: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2"

# Legacy scraper
curl -X POST "http://localhost:8000/plans/scrape?source=legacy" \
  -H "X-API-Key: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2"
```

### Python Examples

```python
import requests
import os

# Load from environment
API_KEY = os.getenv("API_KEY")
BASE_URL = "http://localhost:8000"

# Set headers
headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Trigger scrape
response = requests.post(
    f"{BASE_URL}/plans/scrape?source=powertochoose",
    headers=headers
)

if response.status_code == 200:
    result = response.json()
    print(f"✓ Scraped {result['plans_processed']} plans")
else:
    print(f"✗ Error: {response.status_code} - {response.json()}")
```

### JavaScript/TypeScript Examples

```typescript
// Using fetch API
const API_KEY = process.env.API_KEY;

async function triggerScrape() {
  try {
    const response = await fetch(
      'http://localhost:8000/plans/scrape?source=powertochoose',
      {
        method: 'POST',
        headers: {
          'X-API-Key': API_KEY,
          'Content-Type': 'application/json'
        }
      }
    );

    if (response.ok) {
      const data = await response.json();
      console.log(`✓ Scraped ${data.plans_processed} plans`);
    } else {
      const error = await response.json();
      console.error(`✗ Error: ${response.status} - ${error.detail}`);
    }
  } catch (error) {
    console.error('✗ Request failed:', error);
  }
}

// Using axios
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'X-API-Key': process.env.API_KEY
  }
});

async function triggerScrape() {
  try {
    const { data } = await api.post('/plans/scrape?source=powertochoose');
    console.log(`✓ Scraped ${data.plans_processed} plans`);
  } catch (error) {
    console.error('✗ Error:', error.response?.data || error.message);
  }
}
```

### Postman Setup

1. Open Postman
2. Create new request
3. Set method to **POST**
4. Set URL: `http://localhost:8000/plans/scrape?source=powertochoose`
5. Go to **Headers** tab
6. Add header:
   - **Key**: `X-API-Key`
   - **Value**: `your-api-key-here`
7. Click **Send**

## Error Responses

### Missing API Key

**Status:** 401 Unauthorized

**Request:**
```bash
curl -X POST "http://localhost:8000/plans/scrape?source=powertochoose"
```

**Response:**
```json
{
  "detail": "Invalid or missing API key"
}
```

**Headers:**
```
WWW-Authenticate: ApiKey
```

### Invalid API Key

**Status:** 401 Unauthorized

**Request:**
```bash
curl -X POST "http://localhost:8000/plans/scrape?source=powertochoose" \
  -H "X-API-Key: wrong-key"
```

**Response:**
```json
{
  "detail": "Invalid or missing API key"
}
```

## Security Best Practices

### 1. Generate Strong Keys

```bash
# ✓ GOOD: 256-bit random key
openssl rand -hex 32

# ✓ GOOD: 512-bit random key (even stronger)
openssl rand -hex 64

# ✗ BAD: Short or predictable keys
API_KEY=12345
API_KEY=my-api-key
```

### 2. Store Keys Securely

**✓ DO:**
- Store in environment variables
- Use `.env` file (add to `.gitignore`)
- Use secrets management (AWS Secrets Manager, Azure Key Vault, etc.)
- Rotate keys regularly

**✗ DON'T:**
- Hardcode in source code
- Commit to version control
- Share via insecure channels (email, chat, etc.)
- Use same key across environments

### 3. Use HTTPS in Production

```python
# Production configuration
ALLOWED_ORIGINS = [
    "https://yourdomain.com",  # HTTPS only
]

# Force HTTPS redirect (nginx)
server {
    listen 80;
    return 301 https://$host$request_uri;
}
```

### 4. Rotate Keys Regularly

```bash
# Generate new key
NEW_API_KEY=$(openssl rand -hex 32)

# Update .env
echo "API_KEY=$NEW_API_KEY" >> .env

# Restart services
docker-compose restart backend

# Update all clients with new key
```

### 5. Monitor Usage

```bash
# Check backend logs for auth failures
docker-compose logs backend | grep "Invalid or missing API key"

# Monitor rate limiting
docker-compose logs backend | grep "Rate limit exceeded"
```

## Key Rotation Procedure

### Step 1: Generate New Key
```bash
NEW_KEY=$(openssl rand -hex 32)
echo "New API Key: $NEW_KEY"
```

### Step 2: Update Configuration
```bash
# Update .env file
sed -i "s/API_KEY=.*/API_KEY=$NEW_KEY/" .env

# Or manually edit .env
nano .env
```

### Step 3: Restart Services
```bash
docker-compose restart backend
```

### Step 4: Update Clients
Update all applications/scripts using the old key with the new key.

### Step 5: Verify
```bash
# Test with new key
curl -X POST "http://localhost:8000/plans/scrape?source=powertochoose" \
  -H "X-API-Key: $NEW_KEY"

# Should see: {"plans_processed": N, ...}
```

## Multi-Key Support (Future Enhancement)

To support multiple API keys (e.g., per client):

### Database Schema
```sql
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    key_hash VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit INTEGER DEFAULT 100
);
```

### Implementation
```python
# backend/app/auth.py

import hashlib
from sqlalchemy.orm import Session
from .database import get_db
from .models import APIKey

def verify_api_key_db(
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_db)
) -> APIKey:
    """Verify API key against database."""
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    db_key = db.query(APIKey).filter(
        APIKey.key_hash == key_hash,
        APIKey.is_active == True
    ).first()

    if not db_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )

    # Check expiration
    if db_key.expires_at and db_key.expires_at < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key expired"
        )

    return db_key
```

## JWT Tokens (Future Enhancement)

For user sessions and more complex auth:

### Generate Token
```python
from app.auth import create_access_token
from datetime import timedelta

# Create token
access_token = create_access_token(
    data={"sub": "user@example.com"},
    expires_delta=timedelta(hours=24)
)
```

### Verify Token
```python
from app.auth import verify_token

# Verify token
payload = verify_token(token)
user_email = payload.get("sub")
```

## Password Hashing (User Auth)

For future user authentication:

```python
from app.auth import hash_password, verify_password

# Hash password
hashed = hash_password("MySecurePassword123!")

# Verify password
is_valid = verify_password("MySecurePassword123!", hashed)
```

## Environment-Specific Keys

### Development (.env.development)
```env
API_KEY=dev-key-insecure-for-testing-only
SECRET_KEY=dev-secret-insecure-for-testing-only
```

### Production (.env.production)
```env
API_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
SECRET_KEY=x9y8z7a6b5c4d3e2f1g0h9i8j7k6l5m4n3o2p1q0r9s8t7u6v5w4x3y2z1a0b9c8
```

### Staging (.env.staging)
```env
API_KEY=staging-key-different-from-production
SECRET_KEY=staging-secret-different-from-production
```

## Troubleshooting

### API key not working after restart

**Problem:** Changed API_KEY in `.env` but still getting 401 errors

**Solution:**
1. Verify `.env` is in correct directory
2. Restart backend completely: `docker-compose restart backend`
3. Check logs: `docker-compose logs backend | grep API_KEY`
4. Ensure no spaces around `=` in `.env`: `API_KEY=value` not `API_KEY = value`

### Different keys in different files

**Problem:** Multiple `.env` files with different keys

**Solution:**
- Use single `.env` for local development
- Use `.env.production` for production (load explicitly)
- Add all `.env*` to `.gitignore` except `.env.example`

### Key leaked to version control

**Problem:** Accidentally committed API key to Git

**Solution:**
1. Generate new key immediately: `openssl rand -hex 32`
2. Update `.env` and restart services
3. Remove from Git history:
```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all
```
4. Force push: `git push origin --force --all`
5. Notify all team members to pull fresh copy

## Summary

**Quick Reference:**

```bash
# Generate key
openssl rand -hex 32

# Add to .env
API_KEY=your_generated_key_here

# Use in requests
curl -H "X-API-Key: your_key" http://localhost:8000/plans/scrape

# Rotate key
NEW_KEY=$(openssl rand -hex 32)
sed -i "s/API_KEY=.*/API_KEY=$NEW_KEY/" .env
docker-compose restart backend
```

**Security Checklist:**
- ✓ Use strong random keys (32+ bytes)
- ✓ Store in environment variables
- ✓ Add `.env` to `.gitignore`
- ✓ Use HTTPS in production
- ✓ Rotate keys regularly (quarterly)
- ✓ Monitor for auth failures
- ✓ Different keys per environment
