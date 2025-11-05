"""
Email notification system for daily scraping reports.

Sends automated status reports with commercial plan rate summaries.
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def format_commercial_rates_table(plans: List[Dict[str, Any]]) -> str:
    """Format commercial plans into a clean text table."""
    if not plans:
        return "No commercial plans available."

    # Sort by rate
    sorted_plans = sorted(plans, key=lambda x: x.get('rate_1000_cents', 999))

    table = """
Commercial Plan Rate Summary (sorted by rate)
===============================================

Provider              | Plan Name                    | Rate (¢/kWh) | Term (months)
--------------------- | ---------------------------- | ------------ | -------------
"""

    for plan in sorted_plans[:20]:  # Top 20 plans
        provider = plan.get('provider_name', 'Unknown')[:20].ljust(21)
        plan_name = plan.get('plan_name', 'Unknown')[:28].ljust(29)
        rate = plan.get('rate_1000_cents', 0)
        term = plan.get('contract_months', 0)

        table += f"{provider}| {plan_name}| {rate:>12.2f} | {term:>13}\n"

    if len(sorted_plans) > 20:
        table += f"\n... and {len(sorted_plans) - 20} more plans\n"

    return table


def generate_status_report(
    total_plans: int,
    residential_count: int,
    commercial_count: int,
    commercial_plans: List[Dict[str, Any]],
    quality_score: float,
    suspicious_count: int,
    scrape_errors: List[str] = None
) -> str:
    """Generate HTML email body for status report."""

    now = datetime.now().strftime("%B %d, %Y at %I:%M %p CT")

    # Calculate rate statistics
    if commercial_plans:
        rates = [p.get('rate_1000_cents', 0) for p in commercial_plans if p.get('rate_1000_cents')]
        avg_rate = sum(rates) / len(rates) if rates else 0
        min_rate = min(rates) if rates else 0
        max_rate = max(rates) if rates else 0
    else:
        avg_rate = min_rate = max_rate = 0

    # Format commercial rates table
    rates_table = format_commercial_rates_table(commercial_plans)

    # Build email body
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background-color: #0066cc; color: white; padding: 20px; }}
            .content {{ padding: 20px; }}
            .metrics {{ background-color: #f4f4f4; padding: 15px; margin: 20px 0; border-radius: 5px; }}
            .metric-item {{ margin: 10px 0; }}
            .metric-label {{ font-weight: bold; color: #0066cc; }}
            .status-good {{ color: #28a745; }}
            .status-warning {{ color: #ffc107; }}
            .status-error {{ color: #dc3545; }}
            .rates-table {{ background-color: #f9f9f9; padding: 15px; margin: 20px 0; }}
            pre {{ background-color: #f5f5f5; padding: 15px; overflow-x: auto; }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔌 Texas Energy Analyzer - Daily Report</h1>
            <p>Generated: {now}</p>
        </div>

        <div class="content">
            <h2>📊 Scraping Status</h2>
            <div class="metrics">
                <div class="metric-item">
                    <span class="metric-label">Total Plans:</span>
                    <span class="status-good">{total_plans}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Residential Plans:</span> {residential_count}
                </div>
                <div class="metric-item">
                    <span class="metric-label">Commercial Plans:</span>
                    <span class="{'status-warning' if commercial_count < 10 else 'status-good'}">{commercial_count}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Data Quality Score:</span>
                    <span class="{'status-good' if quality_score > 95 else 'status-warning' if quality_score > 85 else 'status-error'}">{quality_score:.1f}%</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Suspicious Plans:</span>
                    <span class="{'status-good' if suspicious_count == 0 else 'status-error'}">{suspicious_count}</span>
                </div>
            </div>

            <h2>💰 Commercial Rate Summary</h2>
            <div class="metrics">
                <div class="metric-item">
                    <span class="metric-label">Average Rate:</span> {avg_rate:.2f}¢/kWh
                </div>
                <div class="metric-item">
                    <span class="metric-label">Lowest Rate:</span> <span class="status-good">{min_rate:.2f}¢/kWh</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Highest Rate:</span> {max_rate:.2f}¢/kWh
                </div>
            </div>

            <h2>📋 Top Commercial Plans</h2>
            <div class="rates-table">
                <pre>{rates_table}</pre>
            </div>

            {'<h2 class="status-error">⚠️ Scraping Errors</h2><ul>' + ''.join([f'<li>{err}</li>' for err in scrape_errors]) + '</ul>' if scrape_errors else ''}

            <div class="footer">
                <p>This is an automated report from Texas Energy Analyzer.</p>
                <p>Visit your dashboard: <a href="https://web-production-665ac.up.railway.app/docs">API Docs</a></p>
            </div>
        </div>
    </body>
    </html>
    """

    return html


def send_email_report(
    to_email: str,
    subject: str,
    html_body: str,
    from_email: str = None,
    smtp_server: str = None,
    smtp_port: int = None,
    smtp_username: str = None,
    smtp_password: str = None
) -> bool:
    """
    Send email report using SMTP.

    Args:
        to_email: Recipient email address
        subject: Email subject line
        html_body: HTML content for email body
        from_email: Sender email (defaults to SMTP_FROM_EMAIL env var)
        smtp_server: SMTP server (defaults to SMTP_SERVER env var)
        smtp_port: SMTP port (defaults to SMTP_PORT env var or 587)
        smtp_username: SMTP username (defaults to SMTP_USERNAME env var)
        smtp_password: SMTP password (defaults to SMTP_PASSWORD env var)

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # Get config from environment variables if not provided
    from_email = from_email or os.getenv('SMTP_FROM_EMAIL', 'noreply@texasenergyanalyzer.com')
    smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
    smtp_username = smtp_username or os.getenv('SMTP_USERNAME')
    smtp_password = smtp_password or os.getenv('SMTP_PASSWORD')

    # Validate required config
    if not all([smtp_username, smtp_password]):
        logger.error("SMTP credentials not configured. Set SMTP_USERNAME and SMTP_PASSWORD environment variables.")
        return False

    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email

        # Attach HTML body
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)

        # Send email
        logger.info(f"Sending email to {to_email} via {smtp_server}:{smtp_port}")

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)

        logger.info(f"✓ Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"✗ Failed to send email: {e}")
        return False


def send_daily_report(
    db_session,
    recipient_email: str = None
) -> bool:
    """
    Generate and send daily scraping status report.

    Args:
        db_session: SQLAlchemy database session
        recipient_email: Email to send to (defaults to REPORT_EMAIL env var)

    Returns:
        bool: True if email sent successfully
    """
    from .models import Plan
    from .data_validation import get_data_quality_score

    recipient_email = recipient_email or os.getenv('REPORT_EMAIL')

    if not recipient_email:
        logger.warning("No recipient email configured. Set REPORT_EMAIL environment variable.")
        return False

    try:
        # Get plan counts
        all_plans = db_session.query(Plan).all()
        residential_plans = [p for p in all_plans if p.service_type == 'Residential']
        commercial_plans = [p for p in all_plans if p.service_type == 'Commercial']

        # Convert to dicts for quality check
        plans_data = [
            {
                'provider_name': p.provider.name if p.provider else 'Unknown',
                'plan_name': p.plan_name,
                'service_type': p.service_type,
                'rate_1000_cents': p.rate_1000_cents,
                'contract_months': p.contract_months,
                'special_features': p.special_features
            }
            for p in all_plans
        ]

        commercial_plans_data = [p for p in plans_data if p['service_type'] == 'Commercial']

        # Get quality metrics
        quality_metrics = get_data_quality_score(plans_data)

        # Check for suspicious plans
        fake_markers = ['estimate', 'typical', 'verify', 'fallback', 'sample']
        suspicious_plans = [
            p for p in all_plans
            if p.special_features and any(marker in p.special_features.lower() for marker in fake_markers)
        ]

        # Generate report
        subject = f"Texas Energy Analyzer Daily Report - {datetime.now().strftime('%b %d, %Y')}"

        html_body = generate_status_report(
            total_plans=len(all_plans),
            residential_count=len(residential_plans),
            commercial_count=len(commercial_plans),
            commercial_plans=commercial_plans_data,
            quality_score=quality_metrics.get('quality_score', 0),
            suspicious_count=len(suspicious_plans),
            scrape_errors=[]  # Could add error tracking here
        )

        # Send email
        return send_email_report(
            to_email=recipient_email,
            subject=subject,
            html_body=html_body
        )

    except Exception as e:
        logger.error(f"Failed to generate/send daily report: {e}")
        return False
