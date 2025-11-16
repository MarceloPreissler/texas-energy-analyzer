"""
Professional-grade scraping utilities for industry-leading reliability.

This module provides enterprise-level scraping infrastructure including:
- Exponential backoff retry logic
- Browser fingerprint evasion
- Smart caching
- Health monitoring
- Rate limiting
- Data validation
"""
from __future__ import annotations

import time
import random
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Callable, Any, Optional, Dict, List
from functools import wraps
from playwright.sync_api import Page, BrowserContext

logger = logging.getLogger(__name__)


# ============================================================================
# RETRY LOGIC WITH EXPONENTIAL BACKOFF
# ============================================================================

def retry_with_backoff(
    max_retries: int = 5,
    initial_delay: float = 2.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
):
    """
    Decorator that retries a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential backoff (2 = double each time)
        jitter: Add random jitter to prevent thundering herd

    Example:
        @retry_with_backoff(max_retries=3)
        def scrape_provider():
            # Will retry up to 3 times with delays: 2s, 4s, 8s
            return fetch_data()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(
                            f"[Retry] {func.__name__} failed after {max_retries} attempts: {e}"
                        )
                        raise

                    # Calculate next delay with exponential backoff
                    delay = min(delay * exponential_base, max_delay)

                    # Add jitter to prevent synchronization
                    if jitter:
                        delay = delay * (0.5 + random.random())

                    logger.warning(
                        f"[Retry] {func.__name__} failed (attempt {attempt + 1}/{max_retries}), "
                        f"retrying in {delay:.1f}s: {e}"
                    )
                    time.sleep(delay)

            return None

        return wrapper
    return decorator


# ============================================================================
# BROWSER FINGERPRINT EVASION
# ============================================================================

# Realistic user agents from different browsers/OS
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# Common screen resolutions
SCREEN_RESOLUTIONS = [
    {'width': 1920, 'height': 1080},  # Full HD
    {'width': 1366, 'height': 768},   # Common laptop
    {'width': 1536, 'height': 864},   # HD+
    {'width': 1440, 'height': 900},   # MacBook Pro 13"
    {'width': 2560, 'height': 1440},  # 2K
]


def get_stealth_context(playwright_browser) -> BrowserContext:
    """
    Create a browser context with fingerprint evasion.

    Returns a context that appears as a normal human user.
    """
    user_agent = random.choice(USER_AGENTS)
    viewport = random.choice(SCREEN_RESOLUTIONS)

    context = playwright_browser.new_context(
        user_agent=user_agent,
        viewport=viewport,
        locale='en-US',
        timezone_id='America/Chicago',  # Texas timezone
        permissions=['geolocation'],
        geolocation={'latitude': 32.7767, 'longitude': -96.7970},  # Dallas coords
        color_scheme='light',
        reduced_motion='no-preference',
        forced_colors='none',
    )

    return context


def add_stealth_scripts(page: Page) -> None:
    """
    Add JavaScript to evade bot detection.

    Modifies navigator properties and other fingerprinting vectors.
    """
    stealth_js = """
    // Override the navigator.webdriver property
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });

    // Override the navigator.plugins to appear as real browser
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5]
    });

    // Override navigator.languages
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en']
    });

    // Add chrome property if missing
    if (!window.chrome) {
        window.chrome = { runtime: {} };
    }

    // Override permissions API
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission }) :
            originalQuery(parameters)
    );
    """

    page.add_init_script(stealth_js)


def human_like_delay(min_ms: int = 100, max_ms: int = 500) -> None:
    """
    Add random human-like delay between actions.

    Humans don't click instantly - they have reaction time.
    """
    delay_ms = random.randint(min_ms, max_ms)
    time.sleep(delay_ms / 1000.0)


# ============================================================================
# SMART CACHING
# ============================================================================

# Simple in-memory cache (could be Redis in production)
_CACHE: Dict[str, tuple[Any, datetime]] = {}


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments."""
    key_str = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key_str.encode()).hexdigest()


def cached_scrape(ttl_minutes: int = 60):
    """
    Cache scraping results to avoid unnecessary re-scraping.

    Args:
        ttl_minutes: Time to live in minutes
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            key = f"{func.__name__}_{cache_key(*args, **kwargs)}"

            # Check cache
            if key in _CACHE:
                result, timestamp = _CACHE[key]
                age = datetime.now() - timestamp

                if age < timedelta(minutes=ttl_minutes):
                    logger.info(
                        f"[Cache] HIT for {func.__name__} "
                        f"(age: {age.total_seconds():.0f}s, ttl: {ttl_minutes}m)"
                    )
                    return result

            # Cache miss - scrape
            logger.info(f"[Cache] MISS for {func.__name__}, scraping...")
            result = func(*args, **kwargs)

            # Store in cache
            _CACHE[key] = (result, datetime.now())

            # Clean old entries (simple LRU)
            _clean_cache()

            return result

        return wrapper
    return decorator


def _clean_cache(max_entries: int = 100) -> None:
    """Remove oldest cache entries if cache is too large."""
    if len(_CACHE) > max_entries:
        # Sort by timestamp and keep newest
        sorted_items = sorted(_CACHE.items(), key=lambda x: x[1][1], reverse=True)
        _CACHE.clear()
        for key, value in sorted_items[:max_entries]:
            _CACHE[key] = value


def clear_cache() -> None:
    """Clear all cached scraping results."""
    _CACHE.clear()
    logger.info("[Cache] Cleared all cached results")


# ============================================================================
# DATA VALIDATION
# ============================================================================

def validate_commercial_plan(plan: Dict) -> tuple[bool, Optional[str]]:
    """
    Validate that a commercial plan has reasonable data.

    Returns:
        (is_valid, error_message)
    """
    # Check required fields
    required_fields = ['provider_name', 'plan_name', 'rate_1000_cents']
    for field in required_fields:
        if not plan.get(field):
            return False, f"Missing required field: {field}"

    # Validate provider name
    provider = plan.get('provider_name', '')
    if len(provider) < 3 or len(provider) > 100:
        return False, f"Invalid provider name length: {provider}"

    # Validate rate (commercial rates typically 5-25¢/kWh)
    rate = plan.get('rate_1000_cents')
    if rate is None:
        return False, "Missing rate"

    try:
        rate = float(rate)
        if rate < 3.0 or rate > 50.0:  # Sanity check
            return False, f"Rate out of reasonable range: {rate}¢/kWh"
    except (ValueError, TypeError):
        return False, f"Invalid rate format: {rate}"

    # Validate contract months if present
    months = plan.get('contract_months')
    if months is not None:
        try:
            months = int(months)
            if months < 1 or months > 60:
                return False, f"Contract months out of range: {months}"
        except (ValueError, TypeError):
            return False, f"Invalid contract months: {months}"

    return True, None


def filter_valid_plans(plans: List[Dict]) -> tuple[List[Dict], List[Dict]]:
    """
    Filter plans into valid and invalid lists.

    Returns:
        (valid_plans, invalid_plans_with_reasons)
    """
    valid = []
    invalid = []

    for plan in plans:
        is_valid, error = validate_commercial_plan(plan)
        if is_valid:
            valid.append(plan)
        else:
            invalid.append({'plan': plan, 'reason': error})
            logger.warning(f"[Validation] Invalid plan filtered out: {error} - {plan.get('plan_name', 'Unknown')}")

    return valid, invalid


# ============================================================================
# HEALTH MONITORING
# ============================================================================

class ScraperHealthMonitor:
    """Track scraper success rates and performance."""

    def __init__(self):
        self.stats: Dict[str, Dict] = {}

    def record_success(self, scraper_name: str, plan_count: int, duration_seconds: float):
        """Record a successful scrape."""
        if scraper_name not in self.stats:
            self.stats[scraper_name] = {
                'total_runs': 0,
                'successful_runs': 0,
                'failed_runs': 0,
                'total_plans': 0,
                'total_duration': 0.0,
                'last_success': None,
                'last_failure': None,
            }

        stats = self.stats[scraper_name]
        stats['total_runs'] += 1
        stats['successful_runs'] += 1
        stats['total_plans'] += plan_count
        stats['total_duration'] += duration_seconds
        stats['last_success'] = datetime.now()

    def record_failure(self, scraper_name: str, error: str):
        """Record a failed scrape."""
        if scraper_name not in self.stats:
            self.stats[scraper_name] = {
                'total_runs': 0,
                'successful_runs': 0,
                'failed_runs': 0,
                'total_plans': 0,
                'total_duration': 0.0,
                'last_success': None,
                'last_failure': None,
                'last_error': None,
            }

        stats = self.stats[scraper_name]
        stats['total_runs'] += 1
        stats['failed_runs'] += 1
        stats['last_failure'] = datetime.now()
        stats['last_error'] = str(error)

    def get_success_rate(self, scraper_name: str) -> float:
        """Get success rate as percentage."""
        if scraper_name not in self.stats:
            return 0.0

        stats = self.stats[scraper_name]
        total = stats['total_runs']
        if total == 0:
            return 0.0

        return (stats['successful_runs'] / total) * 100

    def get_average_duration(self, scraper_name: str) -> float:
        """Get average scraping duration in seconds."""
        if scraper_name not in self.stats:
            return 0.0

        stats = self.stats[scraper_name]
        successful = stats['successful_runs']
        if successful == 0:
            return 0.0

        return stats['total_duration'] / successful

    def get_report(self) -> Dict:
        """Get full health report for all scrapers."""
        report = {}
        for name, stats in self.stats.items():
            report[name] = {
                **stats,
                'success_rate': self.get_success_rate(name),
                'avg_duration': self.get_average_duration(name),
                'avg_plans_per_run': stats['total_plans'] / max(stats['successful_runs'], 1),
            }
        return report


# Global health monitor instance
health_monitor = ScraperHealthMonitor()


# ============================================================================
# RATE LIMITING
# ============================================================================

class RateLimiter:
    """Simple rate limiter to avoid overwhelming provider sites."""

    def __init__(self):
        self.last_request: Dict[str, datetime] = {}

    def wait_if_needed(self, domain: str, min_delay_seconds: float = 1.0):
        """
        Wait if necessary to respect rate limits.

        Args:
            domain: Domain being scraped (e.g., "txu.com")
            min_delay_seconds: Minimum time between requests
        """
        if domain in self.last_request:
            elapsed = (datetime.now() - self.last_request[domain]).total_seconds()
            if elapsed < min_delay_seconds:
                wait_time = min_delay_seconds - elapsed
                logger.debug(f"[RateLimit] Waiting {wait_time:.1f}s for {domain}")
                time.sleep(wait_time)

        self.last_request[domain] = datetime.now()


# Global rate limiter instance
rate_limiter = RateLimiter()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def truncate_string(s: str, max_length: int = 200) -> str:
    """Truncate string to max length."""
    if not s:
        return ""
    return s[:max_length] if len(s) > max_length else s
