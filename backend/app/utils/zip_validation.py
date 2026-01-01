"""
Texas ZIP Code Validation Utility
Provides server-side validation for Texas ZIP codes
"""
import re
from typing import Tuple

# Texas ZIP code ranges (ERCOT service territory)
TEXAS_ZIP_RANGES = [
    (75001, 79999),  # Main Texas
    (88510, 88589),  # El Paso area
]


def sanitize_zip(zip_code: str) -> str:
    """Remove non-digits and trim to 5 characters."""
    return re.sub(r'\D', '', zip_code)[:5]


def is_texas_zip(zip_code: str) -> bool:
    """Check if a ZIP code is within Texas ranges."""
    try:
        numeric = int(zip_code)
        return any(low <= numeric <= high for low, high in TEXAS_ZIP_RANGES)
    except (ValueError, TypeError):
        return False


def validate_texas_zip(zip_code: str) -> Tuple[bool, str]:
    """
    Validate a ZIP code for Texas electricity plans.

    Returns:
        Tuple of (is_valid, error_message)
        error_message is empty string if valid
    """
    if not zip_code:
        return False, "ZIP code is required"

    sanitized = sanitize_zip(zip_code)

    if len(sanitized) != 5:
        return False, "ZIP code must be exactly 5 digits"

    if not sanitized.isdigit():
        return False, "ZIP code must contain only numbers"

    if not is_texas_zip(sanitized):
        return False, f"ZIP code {sanitized} is not in the Texas ERCOT service territory (75xxx-79xxx)"

    return True, ""


def get_approximate_tdu(zip_code: str) -> str:
    """
    Get approximate TDU (Transmission/Distribution Utility) for a ZIP code.
    This is an approximation - actual TDU is determined by the utility.
    """
    try:
        numeric = int(zip_code)
        prefix = numeric // 100

        # Dallas/Fort Worth area - Oncor
        if 750 <= prefix <= 769:
            return "Oncor"

        # Houston area - CenterPoint
        if 770 <= prefix <= 779:
            return "CenterPoint"

        # Austin area
        if 786 <= prefix <= 789:
            return "Oncor/TNMP"

        # San Antonio / Corpus Christi area
        if 780 <= prefix <= 785:
            return "AEP Texas"

        # West Texas
        if 790 <= prefix <= 799:
            return "AEP Texas/Oncor"

        # El Paso
        if 885 <= prefix <= 889 or prefix >= 799:
            return "El Paso Electric"

        return "Unknown"
    except (ValueError, TypeError):
        return "Unknown"
