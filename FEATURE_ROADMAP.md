# Texas Energy Analyzer - Feature Implementation Roadmap

**Created:** October 15, 2025
**Status:** Planning Phase
**Priority Features:** 1, 2, 3, 4, 8, 9, 10 + Commercial Data Enhancement

---

## Phase 1: Data Infrastructure Enhancement (Week 1-2)

### Priority: HIGH - Foundation for all features

### 1.1 Fix EnergyBot Commercial Scraper
**Status:** Needs Update
**Goal:** Get EnergyBot v2 scraper working to pull commercial plans

**Tasks:**
- [ ] Debug JSON-LD parsing in energybot_scraper_v2.py
- [ ] Test with live EnergyBot.com page
- [ ] Update selectors if site structure changed
- [ ] Verify 20+ commercial plans scraped
- [ ] Add to scheduler for daily updates

**Technical Details:**
```python
# File: backend/app/scraping/energybot_scraper_v2.py
# Current issue: 0 plans parsed
# Fix: Update JSON-LD extraction logic
```

**Success Metrics:**
- Scrape 20+ commercial plans from EnergyBot
- Data quality: provider, plan name, rate, term
- < 10 second execution time

---

### 1.2 Add More Commercial Data Sources
**Status:** New Development
**Goal:** Expand commercial plan coverage beyond EnergyBot

**New Scrapers to Build:**
1. **Direct Energy Business**
   - URL: https://www.directenergy.com/texas/business
   - Target: 10-15 commercial plans

2. **TXU Energy Business**
   - URL: https://www.txu.com/business
   - Target: 8-12 commercial plans

3. **Gexa Energy Business**
   - URL: https://www.gexaenergy.com/business
   - Target: 5-10 commercial plans

4. **Constellation Energy (new provider)**
   - URL: https://www.constellation.com/solutions/for-your-business.html
   - Target: 10-15 commercial plans

**Implementation:**
```python
# Create new files:
# - backend/app/scraping/direct_business_scraper.py
# - backend/app/scraping/txu_business_scraper.py
# - backend/app/scraping/gexa_business_scraper.py
# - backend/app/scraping/constellation_scraper.py
```

**Success Metrics:**
- 50-70 total commercial plans from all sources
- Daily automated updates
- < 30 seconds total scraping time

---

### 1.3 Historical Rate Tracking (Feature #1)
**Status:** New Development
**Goal:** Track how electricity rates change over time

**Database Changes:**
```sql
-- New table: plan_history
CREATE TABLE plan_history (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER REFERENCES plans(id),
    rate_500_cents DECIMAL(10,3),
    rate_1000_cents DECIMAL(10,3),
    rate_2000_cents DECIMAL(10,3),
    monthly_bill_1000 DECIMAL(10,2),
    recorded_at TIMESTAMP DEFAULT NOW(),
    changed BOOLEAN DEFAULT FALSE
);

-- Index for fast queries
CREATE INDEX idx_plan_history_plan_date ON plan_history(plan_id, recorded_at DESC);
CREATE INDEX idx_plan_history_changed ON plan_history(plan_id, changed);
```

**Backend API:**
```python
# New endpoints in backend/app/api/plans.py

@router.get("/plans/{plan_id}/history")
def get_plan_history(plan_id: int, days: int = 30):
    """Get rate history for a specific plan"""
    pass

@router.get("/plans/trending")
def get_trending_plans(direction: str = "down"):
    """Get plans with significant rate changes"""
    pass

@router.get("/plans/alerts")
def get_rate_alerts():
    """Get alerts for significant rate drops"""
    pass
```

**Frontend Components:**
```tsx
// New components:
// - frontend/src/components/RateHistoryChart.tsx
// - frontend/src/components/PriceTrendIndicator.tsx
// - frontend/src/components/RateAlerts.tsx

// Features:
// - Line chart showing rate changes over time
// - Up/down arrows with percentage change
// - Color-coded indicators (green=down, red=up)
// - Historical comparison (30/60/90 days)
```

**Background Job:**
```python
# backend/app/scheduler.py - Add new job
# Daily at 3:00 AM (after scraping at 2:00 AM)

def record_rate_snapshots():
    """Record daily rate snapshots for trending analysis"""
    # Compare today's rates vs yesterday
    # Mark changed=True if rate differs > 0.5¢
    # Generate alerts for drops > 10%
```

**Success Metrics:**
- Historical data stored for all plans
- Rate trend indicators on plan list
- Alerts for significant rate drops (> 10%)

---

## Phase 2: User Experience Features (Week 3-4)

### 2.1 User Favorites & Alerts (Feature #2)
**Status:** New Development
**Goal:** Let users save favorite plans and get notifications

**Database Changes:**
```sql
-- New tables
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    password_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    email_verified BOOLEAN DEFAULT FALSE
);

CREATE TABLE user_favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    plan_id INTEGER REFERENCES plans(id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, plan_id)
);

CREATE TABLE user_alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    alert_type VARCHAR(50), -- 'rate_drop', 'provider_new_plan', 'contract_expiring'
    provider_id INTEGER REFERENCES providers(id),
    threshold_cents DECIMAL(10,3), -- Alert if rate drops below this
    email_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE alert_history (
    id SERIAL PRIMARY KEY,
    user_alert_id INTEGER REFERENCES user_alerts(id),
    plan_id INTEGER REFERENCES plans(id),
    triggered_at TIMESTAMP DEFAULT NOW(),
    email_sent BOOLEAN DEFAULT FALSE
);
```

**Backend Implementation:**
```python
# New files:
# - backend/app/api/users.py (user auth endpoints)
# - backend/app/api/favorites.py (favorites CRUD)
# - backend/app/api/alerts.py (alert management)
# - backend/app/services/email_service.py (SendGrid/SMTP)
# - backend/app/services/alert_processor.py (check & send alerts)

# Example endpoint:
@router.post("/favorites")
def add_favorite(plan_id: int, user: User = Depends(get_current_user)):
    """Add plan to user's favorites"""
    pass

@router.post("/alerts")
def create_alert(alert: AlertCreate, user: User = Depends(get_current_user)):
    """Create custom rate alert"""
    pass
```

**Frontend Components:**
```tsx
// New pages:
// - frontend/src/pages/Login.tsx
// - frontend/src/pages/Signup.tsx
// - frontend/src/pages/Dashboard.tsx (user's favorites & alerts)

// New components:
// - frontend/src/components/FavoriteButton.tsx (heart icon)
// - frontend/src/components/AlertSetup.tsx (create custom alerts)
// - frontend/src/components/UserDashboard.tsx (view favorites & alerts)
```

**Email Notifications:**
```python
# Send emails when:
# 1. Favorite plan rate drops > 5%
# 2. New plan from favorite provider
# 3. Better rate available than favorited plan
# 4. User-defined threshold met

# Use SendGrid or AWS SES for production
```

**Success Metrics:**
- Users can favorite up to 10 plans
- Custom alerts with thresholds
- Email notifications working
- Alert history tracked

---

### 2.2 Enhanced Search & Filtering (Feature #3)
**Status:** Enhancement
**Goal:** More powerful search and filtering capabilities

**Backend Implementation:**
```python
# Upgrade existing search in backend/app/crud.py

# Add full-text search
@cache_result(ttl=600)
def search_plans(
    db: Session,
    query: str,  # Search in plan names, features, provider
    filters: PlanFilters,
    sort_by: str = "rate_asc",  # rate_asc, rate_desc, contract_asc, etc.
    renewable_only: bool = False,
    has_special_features: bool = False
):
    """Enhanced search with full-text and multiple filters"""

    # PostgreSQL full-text search
    search_vector = func.to_tsvector('english',
        plans.c.plan_name + ' ' +
        plans.c.special_features + ' ' +
        providers.c.name
    )

    query = db.query(Plan).join(Provider)

    if query:
        query = query.filter(search_vector.match(query))

    if renewable_only:
        query = query.filter(
            or_(
                Plan.plan_type.like('%Solar%'),
                Plan.special_features.like('%renewable%'),
                Plan.special_features.like('%100%')
            )
        )

    # Apply sorting
    if sort_by == "rate_asc":
        query = query.order_by(Plan.rate_1000_cents.asc())
    elif sort_by == "savings_desc":
        # Sort by potential savings
        pass

    return query.all()
```

**Frontend Components:**
```tsx
// Enhance existing EnhancedPlanList.tsx

// Add:
// - Full-text search input (searches plan names, features, providers)
// - Multi-column sorting (click column headers)
// - Saved filter presets (save your common searches)
// - Advanced filters panel:
//   - Renewable energy % slider
//   - Has free nights/weekends toggle
//   - Min/max rate sliders
//   - Multiple providers selection
// - Filter tags (show active filters with X to remove)
```

**Saved Filter Presets:**
```tsx
// Examples:
// - "Best Green Energy Plans" (renewable only, sort by rate)
// - "Short-term Fixed" (12 months or less, fixed plans)
// - "My Providers" (TXU, Reliant, Gexa only)
// - "Free Nights" (plans with free nights feature)

// Store in localStorage or user account
```

**Success Metrics:**
- Full-text search working
- 5+ sorting options
- Users can save filter presets
- Filter by renewable energy %

---

### 2.3 Data Export (Feature #4)
**Status:** New Development
**Goal:** Export data for external analysis and reporting

**Backend Implementation:**
```python
# New file: backend/app/api/exports.py

from fastapi.responses import StreamingResponse
import csv
import io
from openpyxl import Workbook
from reportlab.pdfgen import canvas

@router.get("/plans/export/csv")
def export_plans_csv(filters: PlanFilters, user: User = Depends(get_current_user)):
    """Export filtered plans to CSV"""

    plans = crud.get_plans(db, **filters.dict())

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        'Provider', 'Plan Name', 'Type', 'Rate (¢/kWh)',
        'Contract (months)', 'Monthly Bill @1000kWh', 'Features'
    ])
    writer.writeheader()

    for plan in plans:
        writer.writerow({
            'Provider': plan.provider.name,
            'Plan Name': plan.plan_name,
            # ... more fields
        })

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=plans.csv"}
    )

@router.get("/plans/export/excel")
def export_plans_excel(filters: PlanFilters):
    """Export to Excel with formatting"""
    # Use openpyxl to create formatted Excel file
    # Include:
    # - Multiple sheets (Summary, All Plans, Best Deals)
    # - Color coding (green=good rate, red=high rate)
    # - Charts (rate distribution, provider comparison)
    pass

@router.get("/plans/export/pdf")
def export_analysis_pdf(filters: PlanFilters):
    """Generate PDF report with analysis"""
    # Use reportlab to create professional PDF
    # Include:
    # - Executive summary
    # - Best plans table
    # - Charts and graphs
    # - Recommendations
    pass

@router.post("/plans/share")
def create_shareable_link(plan_ids: List[int]):
    """Create shareable link for plan comparison"""
    # Generate unique ID, store in Redis with 7-day expiry
    # Return short URL like: /share/abc123
    pass
```

**Frontend Components:**
```tsx
// Add export buttons to EnhancedPlanList.tsx

<div className="export-buttons">
  <button onClick={() => exportData('csv')}>
    📊 Export to CSV
  </button>
  <button onClick={() => exportData('excel')}>
    📈 Export to Excel
  </button>
  <button onClick={() => exportData('pdf')}>
    📄 Generate PDF Report
  </button>
  <button onClick={() => createShareLink()}>
    🔗 Share Analysis
  </button>
</div>

// New component: frontend/src/components/ShareableLink.tsx
// Shows QR code and short link for sharing
```

**Shareable Links:**
```typescript
// When user clicks "Share", create shareable link
// URL format: https://yourdomain.com/share/abc123
// Includes:
// - Selected plans
// - Current filters
// - User's usage settings
// - Expiry: 7 days

// Recipient can view comparison without login
```

**Success Metrics:**
- Export to CSV, Excel, PDF working
- Formatted Excel with charts
- Professional PDF reports
- Shareable links with 7-day expiry

---

## Phase 3: Community & Mobile (Week 5-6)

### 3.1 Plan Reviews & Ratings (Feature #8)
**Status:** New Development
**Goal:** Community-driven plan ratings and reviews

**Database Changes:**
```sql
CREATE TABLE plan_reviews (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER REFERENCES plans(id),
    user_id INTEGER REFERENCES users(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    review_text TEXT,
    verified_customer BOOLEAN DEFAULT FALSE,
    helpful_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(plan_id, user_id) -- One review per user per plan
);

CREATE TABLE review_votes (
    id SERIAL PRIMARY KEY,
    review_id INTEGER REFERENCES plan_reviews(id),
    user_id INTEGER REFERENCES users(id),
    helpful BOOLEAN, -- true=helpful, false=not helpful
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(review_id, user_id)
);

CREATE TABLE provider_ratings (
    id SERIAL PRIMARY KEY,
    provider_id INTEGER REFERENCES providers(id),
    user_id INTEGER REFERENCES users(id),
    category VARCHAR(50), -- 'customer_service', 'billing', 'reliability'
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(provider_id, user_id, category)
);
```

**Backend API:**
```python
# New file: backend/app/api/reviews.py

@router.post("/plans/{plan_id}/reviews")
def create_review(plan_id: int, review: ReviewCreate, user: User = Depends(get_current_user)):
    """Submit a plan review"""
    pass

@router.get("/plans/{plan_id}/reviews")
def get_plan_reviews(plan_id: int, sort_by: str = "helpful"):
    """Get reviews for a plan"""
    # Sort options: recent, helpful, rating_high, rating_low
    pass

@router.post("/reviews/{review_id}/vote")
def vote_review(review_id: int, helpful: bool, user: User = Depends(get_current_user)):
    """Mark review as helpful or not"""
    pass

@router.get("/providers/{provider_id}/ratings")
def get_provider_ratings(provider_id: int):
    """Get aggregated provider ratings"""
    # Return average ratings by category:
    # - Customer Service: 4.2/5
    # - Billing Accuracy: 3.8/5
    # - Reliability: 4.5/5
    pass
```

**Frontend Components:**
```tsx
// New components:
// - frontend/src/components/PlanReviews.tsx
// - frontend/src/components/ReviewForm.tsx
// - frontend/src/components/ProviderRatings.tsx
// - frontend/src/components/RatingStars.tsx

// Features:
// - 5-star rating system
// - Title + detailed review text
// - "Verified Customer" badge
// - Helpful votes (like Reddit upvotes)
// - Filter reviews by rating
// - Report inappropriate reviews
```

**Moderation System:**
```python
# Prevent spam/abuse:
# - Rate limit: 3 reviews per day per user
# - Profanity filter on review text
# - Flag system for inappropriate content
# - Admin panel to moderate reviews
```

**Success Metrics:**
- Users can rate plans 1-5 stars
- Written reviews with 500 char limit
- Helpful voting system
- Provider reliability scores

---

### 3.2 Mobile Progressive Web App (Feature #9)
**Status:** New Development
**Goal:** Mobile-optimized, installable web app

**PWA Setup:**
```typescript
// New files:
// - frontend/public/manifest.json
// - frontend/public/service-worker.js
// - frontend/src/registerServiceWorker.ts

// manifest.json
{
  "name": "Texas Energy Analyzer",
  "short_name": "TXEnergy",
  "description": "Compare Texas electricity plans",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#2c5364",
  "theme_color": "#2c5364",
  "orientation": "portrait",
  "icons": [
    {
      "src": "/icons/icon-72x72.png",
      "sizes": "72x72",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ],
  "categories": ["utilities", "finance"],
  "screenshots": [
    {
      "src": "/screenshots/mobile-home.png",
      "sizes": "540x720",
      "type": "image/png"
    }
  ]
}
```

**Service Worker (Offline Support):**
```javascript
// service-worker.js
// Cache strategy:
// - Cache-first for static assets (CSS, JS, images)
// - Network-first for API calls with fallback
// - Offline page when network unavailable

const CACHE_NAME = 'tx-energy-v1';
const urlsToCache = [
  '/',
  '/index.html',
  '/static/css/main.css',
  '/static/js/main.js',
  '/offline.html'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.url.includes('/api/')) {
    // Network-first for API calls
    event.respondWith(
      fetch(event.request)
        .catch(() => caches.match(event.request))
    );
  } else {
    // Cache-first for static assets
    event.respondWith(
      caches.match(event.request)
        .then(response => response || fetch(event.request))
    );
  }
});
```

**Mobile-Optimized UI:**
```css
/* Responsive design improvements */
/* Already have some, but enhance: */

@media (max-width: 768px) {
  /* Stack cards vertically */
  .dashboard {
    flex-direction: column;
  }

  /* Simplified table for mobile */
  .plans-table {
    font-size: 0.85rem;
  }

  /* Bottom navigation for mobile */
  .mobile-nav {
    position: fixed;
    bottom: 0;
    width: 100%;
    /* Home, Search, Favorites, Profile */
  }

  /* Touch-friendly buttons (44x44px minimum) */
  button, .filter-group select {
    min-height: 44px;
    font-size: 16px; /* Prevents zoom on iOS */
  }
}
```

**Mobile Features:**
```tsx
// Mobile-specific components:
// - Swipeable plan cards
// - Pull-to-refresh
// - Bottom sheet filters (instead of sidebar)
// - Native share API integration
// - Geolocation for zip code detection

// Example:
if (navigator.share) {
  navigator.share({
    title: 'Check out this energy plan',
    text: `${plan.provider} - ${plan.plan_name} at ${plan.rate}¢/kWh`,
    url: window.location.href
  });
}

// Geolocation for zip:
if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(async (position) => {
    const zip = await reverseGeocode(position.coords);
    setZipCode(zip);
  });
}
```

**Push Notifications:**
```typescript
// Request permission for notifications
async function requestNotificationPermission() {
  const permission = await Notification.requestPermission();

  if (permission === 'granted') {
    // Subscribe to push notifications
    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: VAPID_PUBLIC_KEY
    });

    // Send subscription to backend
    await fetch('/api/push/subscribe', {
      method: 'POST',
      body: JSON.stringify(subscription)
    });
  }
}

// Backend sends push when:
// - Favorite plan rate drops
// - New plan from favorite provider
// - Rate alert triggered
```

**App Install Prompt:**
```typescript
// Show custom "Add to Home Screen" prompt
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;

  // Show custom install button
  document.getElementById('install-button').style.display = 'block';
});

document.getElementById('install-button').addEventListener('click', async () => {
  deferredPrompt.prompt();
  const { outcome } = await deferredPrompt.userChoice;

  if (outcome === 'accepted') {
    console.log('User installed the app');
  }

  deferredPrompt = null;
});
```

**Success Metrics:**
- Installable on iOS and Android
- Offline support (view cached data)
- Push notifications working
- < 3 second load time on 3G
- Lighthouse PWA score > 90

---

## Phase 4: API & Integration (Week 7)

### 4.1 API Enhancements (Feature #10)
**Status:** Enhancement
**Goal:** Public API with webhooks and integrations

**Public API Documentation:**
```python
# Upgrade FastAPI docs with better descriptions
# Add examples to all endpoints
# Include rate limiting info
# Add authentication section

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Texas Energy Analyzer API",
        version="2.0.0",
        description="""
        ## Texas Energy Market Data API

        Access real-time electricity plan data for Texas.

        ### Features
        - 🔍 Search and filter electricity plans
        - 📊 Historical rate tracking
        - ⚡ Real-time market data
        - 🔔 Webhooks for rate changes
        - 📈 Analytics and insights

        ### Authentication
        API requires an API key. Get yours at /api/keys/create

        Include in header: `X-API-Key: your-key-here`

        ### Rate Limits
        - Free tier: 100 requests/hour
        - Pro tier: 1000 requests/hour
        - Enterprise: Unlimited

        ### Support
        Email: api@texasenergy.com
        Docs: https://docs.texasenergy.com
        """,
        routes=app.routes,
    )

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

**API Key Management:**
```python
# New file: backend/app/api/api_keys.py

from secrets import token_urlsafe

CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    key_prefix VARCHAR(10), -- First 8 chars for display
    name VARCHAR(255), -- "Production Server", "Test App"
    tier VARCHAR(50) DEFAULT 'free', -- free, pro, enterprise
    rate_limit INTEGER DEFAULT 100, -- requests per hour
    enabled BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

CREATE TABLE api_usage (
    id SERIAL PRIMARY KEY,
    api_key_id INTEGER REFERENCES api_keys(id),
    endpoint VARCHAR(255),
    method VARCHAR(10),
    status_code INTEGER,
    response_time_ms INTEGER,
    timestamp TIMESTAMP DEFAULT NOW()
);

@router.post("/api-keys")
def create_api_key(name: str, user: User = Depends(get_current_user)):
    """Create a new API key"""
    key = token_urlsafe(32)
    key_hash = hash_api_key(key)

    # Store in database
    db_key = crud.create_api_key(db, user.id, key_hash, name)

    # Return key ONCE (user must save it)
    return {
        "key": key,
        "prefix": key[:8],
        "message": "Save this key securely. It won't be shown again."
    }

@router.get("/api-keys")
def list_api_keys(user: User = Depends(get_current_user)):
    """List user's API keys (only show prefix, not full key)"""
    pass

@router.delete("/api-keys/{key_id}")
def revoke_api_key(key_id: int, user: User = Depends(get_current_user)):
    """Revoke an API key"""
    pass

@router.get("/api-keys/{key_id}/usage")
def get_api_usage(key_id: int, days: int = 7):
    """Get API usage statistics"""
    pass
```

**Webhook System:**
```python
# New file: backend/app/services/webhooks.py

CREATE TABLE webhooks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    url VARCHAR(500) NOT NULL,
    event_type VARCHAR(100), -- 'rate_change', 'new_plan', 'provider_update'
    secret VARCHAR(255), -- For signature verification
    enabled BOOLEAN DEFAULT TRUE,
    retry_count INTEGER DEFAULT 3,
    timeout_seconds INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE webhook_deliveries (
    id SERIAL PRIMARY KEY,
    webhook_id INTEGER REFERENCES webhooks(id),
    payload JSONB,
    status VARCHAR(50), -- 'success', 'failed', 'retry'
    status_code INTEGER,
    response_body TEXT,
    delivered_at TIMESTAMP,
    retry_count INTEGER DEFAULT 0
);

class WebhookService:
    @staticmethod
    async def trigger_webhook(webhook: Webhook, event_data: dict):
        """Send webhook POST request"""

        # Create signature for verification
        signature = hmac.new(
            webhook.secret.encode(),
            json.dumps(event_data).encode(),
            hashlib.sha256
        ).hexdigest()

        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': signature,
            'X-Event-Type': webhook.event_type
        }

        try:
            async with httpx.AsyncClient(timeout=webhook.timeout_seconds) as client:
                response = await client.post(
                    webhook.url,
                    json=event_data,
                    headers=headers
                )

                # Log delivery
                crud.create_webhook_delivery(
                    db,
                    webhook_id=webhook.id,
                    payload=event_data,
                    status='success' if response.status_code < 400 else 'failed',
                    status_code=response.status_code,
                    response_body=response.text[:1000]
                )

                return response.status_code < 400

        except Exception as e:
            # Retry with exponential backoff
            if retry_count < webhook.retry_count:
                await asyncio.sleep(2 ** retry_count)
                return await WebhookService.trigger_webhook(webhook, event_data, retry_count + 1)

            return False

# Trigger webhooks when:
# 1. Plan rate changes > threshold
# 2. New plan added from favorite provider
# 3. Provider information updates
# 4. Custom user-defined triggers

# Example payload:
{
  "event": "rate_change",
  "timestamp": "2025-10-15T10:30:00Z",
  "plan": {
    "id": 123,
    "provider": "TXU Energy",
    "plan_name": "TXU Energy Secure 12",
    "old_rate": 14.5,
    "new_rate": 12.9,
    "change_percent": -11.03
  }
}
```

**Third-Party Integrations:**
```python
# Zapier Integration
# Create Zapier app to connect with 3000+ services
# - New plan → Send Slack message
# - Rate drop → Create Google Sheet row
# - Alert triggered → Send SMS via Twilio

# Make.com (Integromat) Integration
# Visual workflow builder for complex automations

# Direct API Integrations:
@router.post("/integrations/slack")
def connect_slack(code: str, user: User):
    """OAuth callback for Slack"""
    # Exchange code for token
    # Store token in user's integrations
    pass

@router.post("/integrations/google-sheets")
def connect_google_sheets(credentials: dict, user: User):
    """Connect Google Sheets for auto-export"""
    # Store credentials
    # Set up daily export to user's sheet
    pass
```

**GraphQL API (Optional):**
```python
# Alternative to REST API
# Install: pip install strawberry-graphql

import strawberry
from strawberry.fastapi import GraphQLRouter

@strawberry.type
class Plan:
    id: int
    provider_name: str
    plan_name: str
    rate_1000_cents: float
    contract_months: Optional[int]

@strawberry.type
class Query:
    @strawberry.field
    def plans(
        self,
        provider: Optional[str] = None,
        max_rate: Optional[float] = None,
        limit: int = 100
    ) -> List[Plan]:
        """Query plans with flexible filtering"""
        return get_plans(provider=provider, max_rate=max_rate, limit=limit)

    @strawberry.field
    def plan(self, id: int) -> Optional[Plan]:
        """Get single plan by ID"""
        return get_plan(id)

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app.include_router(graphql_app, prefix="/graphql")

# Usage:
# POST /graphql
# {
#   "query": "{ plans(provider: \"TXU Energy\", maxRate: 15.0) { planName, rate1000Cents } }"
# }
```

**API Sandbox:**
```typescript
// Interactive API playground
// frontend/src/pages/APIDocs.tsx

// Features:
// - Try API endpoints in browser
// - Generate code snippets (Python, JavaScript, curl)
// - View request/response in real-time
// - Test webhooks
// - Monitor API usage

// Code generation example:
function generateCode(endpoint: string, params: any, language: 'python' | 'javascript' | 'curl') {
  if (language === 'python') {
    return `
import requests

response = requests.get(
    "https://api.texasenergy.com${endpoint}",
    headers={"X-API-Key": "your-api-key"},
    params=${JSON.stringify(params, null, 2)}
)

data = response.json()
print(data)
    `;
  }
  // ... more languages
}
```

**Rate Limiting Tiers:**
```python
# Implement tiered rate limiting

class RateLimitTier(Enum):
    FREE = (100, 'hour')      # 100 req/hour
    PRO = (1000, 'hour')      # 1000 req/hour
    ENTERPRISE = (None, None)  # Unlimited

# Pricing:
# - Free: $0/month (100 req/hour)
# - Pro: $49/month (1000 req/hour, webhooks, priority support)
# - Enterprise: Custom pricing (unlimited, SLA, dedicated support)
```

**Success Metrics:**
- Public API documentation published
- API key management working
- Webhooks with retry logic
- 3+ third-party integrations
- GraphQL endpoint (optional)
- API usage analytics dashboard

---

## Implementation Timeline

### Week 1-2: Data Infrastructure
- [x] Fix EnergyBot scraper
- [x] Add 3+ commercial data sources
- [x] Implement historical rate tracking
- [x] Set up background jobs

### Week 3-4: User Experience
- [ ] User authentication & favorites
- [ ] Alert system with emails
- [ ] Enhanced search & filtering
- [ ] Data export (CSV, Excel, PDF)

### Week 5-6: Community & Mobile
- [ ] Reviews & ratings system
- [ ] PWA setup (manifest, service worker)
- [ ] Mobile UI optimization
- [ ] Push notifications

### Week 7: API & Integration
- [ ] Public API documentation
- [ ] API key management
- [ ] Webhook system
- [ ] Third-party integrations

---

## Technical Requirements

### Backend Dependencies
```
# Add to requirements.txt
sendgrid==6.11.0           # Email notifications
celery==5.4.0              # Background task queue (alternative to APScheduler)
openpyxl==3.1.5            # Excel export
reportlab==4.2.5           # PDF generation
stripe==10.17.0            # Payment processing (for Pro/Enterprise)
httpx==0.28.0              # Async HTTP for webhooks
python-jose[cryptography]  # JWT tokens (already have)
```

### Frontend Dependencies
```json
// Add to package.json
{
  "workbox-webpack-plugin": "^7.0.0",  // Service worker
  "react-swipeable": "^7.0.1",         // Swipe gestures
  "file-saver": "^2.0.5",              // File downloads
  "jspdf": "^2.5.2",                   // Client-side PDF
  "react-star-ratings": "^2.3.0",      // Star ratings
  "react-share": "^5.1.0"              // Social sharing
}
```

### Infrastructure
- **Database**: PostgreSQL 14+ (for full-text search)
- **Cache**: Redis 7+ (for sessions, API cache, webhooks queue)
- **Storage**: AWS S3 or similar (for PDF reports, user uploads)
- **Email**: SendGrid or AWS SES (for notifications)
- **Monitoring**: Sentry (error tracking), Datadog (metrics)

---

## Priority Order (Recommended)

### Phase 1A: Commercial Data (HIGHEST PRIORITY)
1. Fix EnergyBot scraper (2-3 days)
2. Add 2-3 more commercial scrapers (3-4 days)
3. Test and verify 50+ commercial plans (1 day)

### Phase 1B: Historical Tracking (HIGH PRIORITY)
1. Database schema for plan_history (1 day)
2. Background job to record snapshots (1 day)
3. API endpoints for history (1 day)
4. Frontend charts for trends (2 days)

### Phase 2: User Features (MEDIUM PRIORITY)
1. Data export (CSV/Excel) - quickest win (2 days)
2. Enhanced search & filtering (3 days)
3. User auth & favorites (4 days)
4. Alert system (3 days)

### Phase 3: Community (MEDIUM-LOW PRIORITY)
1. Reviews & ratings (5 days)
2. Moderation system (2 days)

### Phase 4: Mobile & API (LOW PRIORITY but HIGH IMPACT)
1. PWA setup (3 days)
2. Mobile UI polish (3 days)
3. API enhancements (4 days)
4. Webhooks (3 days)

---

## Success Metrics (KPIs)

### Data Quality
- ✅ 50+ commercial plans scraped
- ✅ 100+ residential plans total
- ✅ Daily data refresh success rate > 95%
- ✅ Historical data for 90+ days

### User Engagement
- 🎯 500+ registered users in 3 months
- 🎯 20% of users favorite at least 1 plan
- 🎯 10% of users set up rate alerts
- 🎯 50+ plan reviews submitted

### Technical Performance
- ⚡ API response time < 200ms (95th percentile)
- ⚡ Page load time < 2 seconds
- ⚡ PWA Lighthouse score > 90
- ⚡ API uptime > 99.5%

### Business Metrics
- 💰 10+ Pro API subscribers ($49/mo)
- 💰 2+ Enterprise customers
- 💰 1000+ CSV/Excel exports per month
- 💰 100+ installations (PWA)

---

## Risk Assessment

### Technical Risks
1. **Scraper Reliability** - Websites change layouts
   - Mitigation: Automated tests, fallback scrapers, alerts

2. **Database Performance** - Large historical tables
   - Mitigation: Partitioning, indexes, caching

3. **API Abuse** - DoS attacks, scrapers
   - Mitigation: Rate limiting, API keys, Cloudflare

### Business Risks
1. **Data Accuracy** - Wrong rates harm users
   - Mitigation: Multi-source verification, user reports

2. **Legal Compliance** - PUCT regulations
   - Mitigation: Disclaimer, link to official sources

3. **User Privacy** - Email addresses, usage data
   - Mitigation: GDPR compliance, encryption, opt-out

---

## Next Steps

### Immediate Actions (This Week)
1. ✅ Review and approve roadmap
2. [ ] Fix EnergyBot v2 scraper
3. [ ] Test commercial data collection
4. [ ] Set up development database for historical tracking

### Sprint 1 (Week 1)
- Fix all commercial scrapers
- Add 2 new commercial sources
- Verify 50+ commercial plans

### Sprint 2 (Week 2)
- Implement historical rate tracking
- Add trend indicators to UI
- Set up daily snapshot job

### Sprint 3-7
- Follow roadmap phases 2-4
- Iterate based on user feedback
- Monitor metrics and adjust

---

## Questions & Decisions Needed

1. **Email Service**: SendGrid vs AWS SES?
   - Recommendation: SendGrid (easier setup, good free tier)

2. **Payment Processing**: Stripe vs PayPal for Pro/Enterprise tiers?
   - Recommendation: Stripe (better API, modern UX)

3. **Mobile First**: Should we prioritize PWA (phase 3) earlier?
   - Decision needed: If users are mostly mobile, move PWA to Week 3

4. **Hosting**: Stay on Railway or move to AWS/Azure?
   - Recommendation: Stay on Railway for now, easy scaling

5. **Open Source**: Make API client libraries open source?
   - Recommendation: Yes, boosts adoption

---

**Last Updated:** October 15, 2025
**Author:** Marcelo Preissler & Claude Code
**Status:** Pending Approval
