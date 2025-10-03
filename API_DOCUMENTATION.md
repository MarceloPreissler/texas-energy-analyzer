# Texas Energy Analyzer - API Documentation

## Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://yourdomain.com/api`

## Authentication

### API Key Authentication

Protected endpoints require an API key passed via the `X-API-Key` header.

**Example:**
```bash
curl -H "X-API-Key: your-api-key-here" http://localhost:8000/plans/scrape
```

### Generating API Keys

```bash
# Generate a secure random API key
openssl rand -hex 32
```

Set in environment:
```bash
export API_KEY=your_generated_key_here
```

## Endpoints

### 1. Root Endpoint

**GET** `/`

Get API information and available endpoints.

**Rate Limit:** 10 requests/minute

**Response:**
```json
{
  "message": "Welcome to the Texas Commercial Energy Market Analyzer API",
  "version": "2.0.0",
  "endpoints": {
    "plans": "/plans",
    "providers": "/plans/providers",
    "scrape": "/plans/scrape (POST)",
    "docs": "/docs"
  }
}
```

---

### 2. Health Check

**GET** `/health`

Check API health status.

**Rate Limit:** None

**Response:**
```json
{
  "status": "healthy",
  "service": "texas-energy-analyzer"
}
```

---

### 3. List Providers

**GET** `/plans/providers`

Get all electricity providers.

**Rate Limit:** 100 requests/hour

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Maximum records to return (default: 100)

**Example Request:**
```bash
curl http://localhost:8000/plans/providers?skip=0&limit=10
```

**Example Response:**
```json
[
  {
    "id": 1,
    "name": "TXU Energy",
    "website": "https://www.txu.com",
    "plans": []
  },
  {
    "id": 2,
    "name": "Reliant Energy",
    "website": "https://www.reliant.com",
    "plans": []
  }
]
```

**Response Fields:**
- `id` (integer): Unique provider identifier
- `name` (string): Provider name
- `website` (string, nullable): Provider website URL
- `plans` (array): Associated plans (empty by default)

---

### 4. List Plans

**GET** `/plans/`

Get electricity plans with optional filters.

**Rate Limit:** 100 requests/hour

**Query Parameters:**
- `provider` (string, optional): Filter by provider name
- `plan_type` (string, optional): Filter by plan type (e.g., "Fixed", "Variable")
- `contract_months` (integer, optional): Filter by contract term in months
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Maximum records to return (default: 100)

**Example Requests:**
```bash
# Get all plans
curl http://localhost:8000/plans/

# Filter by provider
curl "http://localhost:8000/plans/?provider=TXU+Energy"

# Filter by plan type
curl "http://localhost:8000/plans/?plan_type=Fixed"

# Filter by contract length
curl "http://localhost:8000/plans/?contract_months=12"

# Combine filters
curl "http://localhost:8000/plans/?provider=TXU+Energy&plan_type=Fixed&contract_months=12"
```

**Example Response:**
```json
[
  {
    "id": 1,
    "provider_id": 1,
    "plan_name": "TXU Energy Secure Value 12",
    "plan_type": "Fixed",
    "contract_months": 12,
    "rate_500_cents": 13.5,
    "rate_1000_cents": 12.8,
    "rate_2000_cents": 12.2,
    "monthly_bill_1000": 128.00,
    "monthly_bill_2000": 244.00,
    "early_termination_fee": 150.00,
    "base_monthly_fee": 9.95,
    "renewable_percent": 23,
    "special_features": "Free nights and weekends",
    "last_updated": "2025-10-03T14:30:00",
    "provider": {
      "id": 1,
      "name": "TXU Energy",
      "website": "https://www.txu.com"
    }
  }
]
```

**Response Fields:**
- `id` (integer): Unique plan identifier
- `provider_id` (integer): Associated provider ID
- `plan_name` (string): Name of the plan
- `plan_type` (string): Type (Fixed, Variable, Indexed, etc.)
- `contract_months` (integer): Contract term in months
- `rate_500_cents` (float): Rate at 500 kWh usage (¢/kWh)
- `rate_1000_cents` (float): Rate at 1000 kWh usage (¢/kWh)
- `rate_2000_cents` (float): Rate at 2000 kWh usage (¢/kWh)
- `monthly_bill_1000` (float, nullable): Estimated bill at 1000 kWh
- `monthly_bill_2000` (float, nullable): Estimated bill at 2000 kWh
- `early_termination_fee` (float, nullable): Fee for early cancellation
- `base_monthly_fee` (float, nullable): Fixed monthly charge
- `renewable_percent` (integer, nullable): % of renewable energy
- `special_features` (string, nullable): Plan features/benefits
- `last_updated` (datetime): Last scrape timestamp
- `provider` (object): Provider details

---

### 5. Get Single Plan

**GET** `/plans/{plan_id}`

Get details for a specific plan.

**Rate Limit:** 100 requests/hour

**Path Parameters:**
- `plan_id` (integer, required): Plan ID

**Example Request:**
```bash
curl http://localhost:8000/plans/1
```

**Example Response:**
```json
{
  "id": 1,
  "provider_id": 1,
  "plan_name": "TXU Energy Secure Value 12",
  "plan_type": "Fixed",
  "contract_months": 12,
  "rate_500_cents": 13.5,
  "rate_1000_cents": 12.8,
  "rate_2000_cents": 12.2,
  "monthly_bill_1000": 128.00,
  "monthly_bill_2000": 244.00,
  "early_termination_fee": 150.00,
  "base_monthly_fee": 9.95,
  "renewable_percent": 23,
  "special_features": "Free nights and weekends",
  "last_updated": "2025-10-03T14:30:00",
  "provider": {
    "id": 1,
    "name": "TXU Energy",
    "website": "https://www.txu.com"
  }
}
```

**Error Response (404):**
```json
{
  "detail": "Plan not found"
}
```

---

### 6. Trigger Data Scrape

**POST** `/plans/scrape`

🔒 **Authentication Required** - Requires `X-API-Key` header

Manually trigger a scrape to update plan data.

**Rate Limit:** 100 requests/hour

**Query Parameters:**
- `source` (string, optional): Scrape source
  - `powertochoose` (recommended): Live PowerToChoose.org data
  - `legacy` (default): Legacy comparison sites

**Example Requests:**
```bash
# Scrape PowerToChoose.org (recommended)
curl -X POST "http://localhost:8000/plans/scrape?source=powertochoose" \
  -H "X-API-Key: your-api-key-here"

# Legacy scrapers
curl -X POST "http://localhost:8000/plans/scrape?source=legacy" \
  -H "X-API-Key: your-api-key-here"
```

**Example Response:**
```json
{
  "plans_processed": 247,
  "source": "powertochoose",
  "timestamp": "2025-10-03T14:30:00"
}
```

**Response Fields:**
- `plans_processed` (integer): Number of plans created/updated
- `source` (string): Data source used
- `timestamp` (string, nullable): Last update time

**Error Responses:**

**401 Unauthorized** (Missing/Invalid API Key):
```json
{
  "detail": "Invalid or missing API key"
}
```

**429 Too Many Requests** (Rate limit exceeded):
```json
{
  "detail": "Rate limit exceeded"
}
```

---

## Rate Limiting

All endpoints are rate-limited to prevent abuse.

**Default Limits:**
- General endpoints: 100 requests/hour per IP
- Root endpoint: 10 requests/minute per IP

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1696348200
```

**Rate Limit Exceeded Response:**
```json
{
  "detail": "Rate limit exceeded: 100 per 1 hour"
}
```

---

## Caching

Expensive queries are automatically cached with Redis:

- **Providers**: 30 minute TTL
- **Plans**: 1 hour TTL

Cache keys include query parameters, so different filters are cached separately.

**Cache Headers:**
```
X-Cache-Status: HIT  # or MISS
```

---

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error message here"
}
```

### HTTP Status Codes
- `200 OK`: Successful request
- `401 Unauthorized`: Missing or invalid API key
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Invalid parameters
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

---

## Code Examples

### Python
```python
import requests

# Base configuration
BASE_URL = "http://localhost:8000"
API_KEY = "your-api-key-here"

# Get all plans
response = requests.get(f"{BASE_URL}/plans/")
plans = response.json()

# Filter plans
params = {
    "provider": "TXU Energy",
    "plan_type": "Fixed",
    "contract_months": 12
}
response = requests.get(f"{BASE_URL}/plans/", params=params)
filtered_plans = response.json()

# Trigger scrape (requires API key)
headers = {"X-API-Key": API_KEY}
response = requests.post(
    f"{BASE_URL}/plans/scrape?source=powertochoose",
    headers=headers
)
result = response.json()
print(f"Processed {result['plans_processed']} plans")
```

### JavaScript/TypeScript
```typescript
const BASE_URL = 'http://localhost:8000';
const API_KEY = 'your-api-key-here';

// Get all plans
async function getPlans() {
  const response = await fetch(`${BASE_URL}/plans/`);
  const plans = await response.json();
  return plans;
}

// Filter plans
async function getFilteredPlans() {
  const params = new URLSearchParams({
    provider: 'TXU Energy',
    plan_type: 'Fixed',
    contract_months: '12'
  });

  const response = await fetch(`${BASE_URL}/plans/?${params}`);
  const plans = await response.json();
  return plans;
}

// Trigger scrape (requires API key)
async function triggerScrape() {
  const response = await fetch(
    `${BASE_URL}/plans/scrape?source=powertochoose`,
    {
      method: 'POST',
      headers: {
        'X-API-Key': API_KEY
      }
    }
  );
  const result = await response.json();
  console.log(`Processed ${result.plans_processed} plans`);
}
```

### cURL
```bash
# Get all plans
curl http://localhost:8000/plans/

# Filter by provider
curl "http://localhost:8000/plans/?provider=TXU+Energy"

# Get single plan
curl http://localhost:8000/plans/1

# Trigger scrape (with API key)
curl -X POST "http://localhost:8000/plans/scrape?source=powertochoose" \
  -H "X-API-Key: your-api-key-here"

# Check health
curl http://localhost:8000/health
```

---

## Interactive Documentation

The API provides interactive Swagger UI documentation:

**Swagger UI**: http://localhost:8000/docs

**ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Browse all endpoints
- View request/response schemas
- Test API calls directly in browser
- Download OpenAPI specification

---

## Versioning

Current version: **2.0.0**

The API follows semantic versioning:
- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes

---

## Support

For issues or questions:
1. Check interactive docs: `/docs`
2. Review health status: `/health`
3. Check application logs
4. Review this documentation

## Changelog

### v2.0.0 (2025-10-03)
- Added API key authentication
- Implemented rate limiting
- Added Redis caching layer
- Added PowerToChoose.org scraper
- Added automated daily scraping
- Enhanced security (CORS, host validation)
- Added health check endpoint

### v1.0.0 (Initial Release)
- Basic CRUD operations for plans and providers
- Legacy scraper support
- SQLAlchemy ORM with PostgreSQL
- FastAPI framework
