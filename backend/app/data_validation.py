"""
Data Validation Layer - Ensures ONLY real data enters the database.

This module prevents fake, estimated, or sample data from contaminating
the production database.
"""
from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Markers that indicate fake/estimated data
FAKE_DATA_MARKERS = [
    'estimate',
    'estimated',
    'typical',
    'verify',
    'fallback',
    'sample',
    'demo',
    'demonstration',
    'call for pricing',
    'call for quote',
    'contact for rate',
    'tbd',
    'to be determined',
    'approximate',
    'approx'
]


def validate_plan_data(plan: Dict[str, Any], strict: bool = True) -> tuple[bool, Optional[str]]:
    """
    Validate that plan data is real and complete.

    Args:
        plan: Plan data dictionary from scraper
        strict: If True, reject plans with any suspicious indicators

    Returns:
        Tuple of (is_valid, reason_for_rejection)
    """
    # Check 1: Required fields
    required_fields = ['provider_name', 'plan_name', 'rate_1000_cents']
    for field in required_fields:
        if not plan.get(field):
            return False, f"Missing required field: {field}"

    # Check 2: Fake data markers in special_features
    special_features = str(plan.get('special_features', '')).lower()
    for marker in FAKE_DATA_MARKERS:
        if marker in special_features:
            return False, f"Fake data marker found: '{marker}' in special_features"

    # Check 3: Fake data markers in plan_name
    plan_name = str(plan.get('plan_name', '')).lower()
    for marker in ['sample', 'demo', 'test']:
        if marker in plan_name:
            return False, f"Fake data marker in plan_name: '{marker}'"

    # Check 4: Valid rate.
    # NOTE: rate_1000_cents is stored in HUNDREDTHS of a cent per kWh
    # (e.g. 1390 = 13.9¢/kWh) - the convention used by the scrapers, database
    # and frontend. Convert before range-checking, otherwise every real plan
    # gets rejected and the database silently stops updating.
    rate = plan.get('rate_1000_cents')
    if rate:
        if rate <= 0:
            return False, f"Invalid rate: {rate} (must be positive)"

        cents_per_kwh = rate / 100.0
        service_type = plan.get('service_type', 'Residential')
        if service_type == 'Commercial':
            # Commercial rates outside 3-30¢/kWh are suspicious
            if cents_per_kwh < 3 or cents_per_kwh > 30:
                if strict:
                    return False, f"Commercial rate {cents_per_kwh:.1f}¢/kWh outside expected range (3-30¢)"
                else:
                    logger.warning(f"Suspicious commercial rate: {cents_per_kwh:.1f}¢/kWh for {plan['plan_name']}")

        elif service_type == 'Residential':
            # Residential rates outside 5-35¢/kWh are suspicious
            if cents_per_kwh < 5 or cents_per_kwh > 35:
                if strict:
                    return False, f"Residential rate {cents_per_kwh:.1f}¢/kWh outside expected range (5-35¢)"
                else:
                    logger.warning(f"Suspicious residential rate: {cents_per_kwh:.1f}¢/kWh for {plan['plan_name']}")

    # Check 5: Suspiciously round numbers (often fake)
    if strict and plan.get('service_type') == 'Commercial':
        rate = plan.get('rate_1000_cents', 0)
        if rate > 0 and rate % 1 == 0:  # Perfectly round
            # Allow some known real plans with round numbers
            provider = plan.get('provider_name', '')
            if provider not in ['TXU Energy', 'Reliant Energy']:  # These sometimes have round rates
                logger.warning(
                    f"Suspicious round rate for {plan['provider_name']} - {plan['plan_name']}: {rate}¢/kWh"
                )

    # Check 6: Valid contract term
    contract_months = plan.get('contract_months')
    if contract_months:
        if contract_months <= 0 or contract_months > 60:
            return False, f"Invalid contract term: {contract_months} months"

    # All checks passed
    return True, None


def validate_plan_batch(plans: List[Dict[str, Any]], strict: bool = True) -> tuple[List[Dict], List[Dict]]:
    """
    Validate a batch of plans and separate valid from invalid.

    Args:
        plans: List of plan dictionaries
        strict: Use strict validation mode

    Returns:
        Tuple of (valid_plans, rejected_plans_with_reasons)
    """
    valid_plans = []
    rejected_plans = []

    for plan in plans:
        is_valid, reason = validate_plan_data(plan, strict=strict)

        if is_valid:
            valid_plans.append(plan)
        else:
            rejected_plans.append({
                'plan': plan,
                'reason': reason
            })
            logger.warning(
                f"REJECTED: {plan.get('provider_name', 'Unknown')} - "
                f"{plan.get('plan_name', 'Unknown')}: {reason}"
            )

    logger.info(f"Validation complete: {len(valid_plans)} valid, {len(rejected_plans)} rejected")

    return valid_plans, rejected_plans


def get_data_quality_score(plans: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate data quality metrics for a set of plans.

    Args:
        plans: List of plan dictionaries

    Returns:
        Dictionary with quality metrics
    """
    if not plans:
        return {
            'total_plans': 0,
            'quality_score': 0.0,
            'issues': ['No plans provided']
        }

    total = len(plans)
    issues = []

    # Count plans with complete data
    complete_plans = sum(
        1 for p in plans
        if all([p.get('provider_name'), p.get('plan_name'), p.get('rate_1000_cents')])
    )

    # Count plans with suspicious markers
    suspicious = sum(
        1 for p in plans
        if any(marker in str(p.get('special_features', '')).lower() for marker in FAKE_DATA_MARKERS)
    )

    # Count plans with rates in expected ranges
    valid_rates = 0
    for plan in plans:
        rate = plan.get('rate_1000_cents')
        service_type = plan.get('service_type', 'Residential')

        if rate:
            if service_type == 'Commercial' and 5 <= rate <= 20:
                valid_rates += 1
            elif service_type == 'Residential' and 8 <= rate <= 25:
                valid_rates += 1

    # Calculate score
    completeness = complete_plans / total
    authenticity = (total - suspicious) / total
    rate_validity = valid_rates / total

    quality_score = (completeness * 0.4 + authenticity * 0.4 + rate_validity * 0.2) * 100

    # Identify issues
    if completeness < 1.0:
        issues.append(f"{total - complete_plans} plans missing required fields")
    if suspicious > 0:
        issues.append(f"{suspicious} plans have fake data markers")
    if rate_validity < 1.0:
        issues.append(f"{total - valid_rates} plans have rates outside expected range")

    return {
        'total_plans': total,
        'complete_plans': complete_plans,
        'suspicious_plans': suspicious,
        'valid_rates': valid_rates,
        'quality_score': round(quality_score, 1),
        'issues': issues if issues else ['No issues detected']
    }


def log_validation_summary(plans_before: int, plans_after: int, rejected: List[Dict]):
    """Log a summary of validation results."""
    logger.info("=" * 80)
    logger.info("DATA VALIDATION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Plans before validation: {plans_before}")
    logger.info(f"Plans after validation: {plans_after}")
    logger.info(f"Plans rejected: {len(rejected)}")

    if rejected:
        logger.info("\nRejection reasons:")
        rejection_reasons = {}
        for item in rejected:
            reason = item['reason']
            rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1

        for reason, count in rejection_reasons.items():
            logger.info(f"  - {reason}: {count} plans")

    logger.info("=" * 80)
