# Email Notification Setup Guide

## Overview

Your Texas Energy Analyzer now sends automated daily email reports with:
- Scraping status summary
- Data quality scores
- Commercial plan rate summary (sorted by rate)
- Top 20 lowest-rate commercial plans

## Setup Instructions

### Step 1: Configure Environment Variables

Add these environment variables to your Railway service:

```bash
# Required - Your email address to receive reports
REPORT_EMAIL=your.email@example.com

# Required - SMTP credentials (using Gmail as example)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your.gmail@gmail.com
SMTP_PASSWORD=your-app-password

# Optional - Sender email (defaults to noreply@texasenergyanalyzer.com)
SMTP_FROM_EMAIL=noreply@texasenergyanalyzer.com
```

### Step 2: Set Up Gmail App Password (Recommended)

If using Gmail:

1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification (if not already enabled)
3. Go to **App Passwords**: https://myaccount.google.com/apppasswords
4. Select **Mail** and **Other (Custom name)**
5. Name it "Texas Energy Analyzer"
6. Copy the 16-character password
7. Use this as your `SMTP_PASSWORD` (not your regular Gmail password)

### Step 3: Configure in Railway Dashboard

1. Go to https://railway.app/dashboard
2. Click your **texas-energy-analyzer** project
3. Click the **web** service
4. Go to **Variables** tab
5. Add the environment variables:

```
REPORT_EMAIL = your.email@example.com
SMTP_SERVER = smtp.gmail.com
SMTP_PORT = 587
SMTP_USERNAME = your.gmail@gmail.com
SMTP_PASSWORD = (your 16-char app password)
```

6. Click **Redeploy** to apply changes

### Step 4: Test Email Sending

Test your configuration using the API:

```bash
# Send a test email immediately
curl -X POST "https://web-production-665ac.up.railway.app/admin/send-test-email?email=your.email@example.com"
```

Or visit the API docs and use the interactive form:
https://web-production-665ac.up.railway.app/docs#/admin/send_test_email

## Alternative SMTP Providers

### Using SendGrid (Free Tier: 100 emails/day)

1. Sign up at https://sendgrid.com
2. Create an API key
3. Configure:

```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=(your SendGrid API key)
```

### Using Mailgun (Free Tier: 1,000 emails/month)

1. Sign up at https://mailgun.com
2. Verify your domain or use sandbox
3. Get SMTP credentials
4. Configure:

```bash
SMTP_SERVER=smtp.mailgun.org
SMTP_PORT=587
SMTP_USERNAME=(your Mailgun SMTP username)
SMTP_PASSWORD=(your Mailgun SMTP password)
```

### Using Outlook/Office 365

```bash
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your.email@outlook.com
SMTP_PASSWORD=(your Outlook password)
```

## Email Schedule

Emails are sent automatically:
- **Time**: Daily at 3:00 AM Central Time
- **After**: The automated scraping job completes
- **Content**: Status report + commercial rate summary

## Email Report Contents

### Summary Metrics
- Total plans in database
- Residential plan count
- Commercial plan count
- Data quality score (0-100%)
- Number of suspicious/fake plans detected

### Commercial Rate Statistics
- Average rate across all commercial plans
- Lowest available rate
- Highest rate
- Full table of top 20 plans sorted by rate

### Example Email

```
Texas Energy Analyzer - Daily Report
Generated: November 4, 2025 at 3:05 AM CT

📊 Scraping Status
------------------
Total Plans: 47
Residential Plans: 42
Commercial Plans: 5
Data Quality Score: 97.4%
Suspicious Plans: 0

💰 Commercial Rate Summary
--------------------------
Average Rate: 6.08¢/kWh
Lowest Rate: 5.38¢/kWh
Highest Rate: 7.14¢/kWh

📋 Top Commercial Plans
-----------------------
Provider       | Plan Name          | Rate (¢/kWh) | Term (months)
-------------- | ------------------ | ------------ | -------------
NRG Energy     | 3 month            |        5.38  |      3
AP Gas         | 1 month            |        5.50  |      1
...
```

## Troubleshooting

### Email not sending

1. **Check Railway logs**:
   - Go to Railway → Deployments → Click latest → Logs
   - Search for "email" or "SMTP"
   - Look for error messages

2. **Verify environment variables**:
   - Railway → Variables tab
   - Ensure all SMTP_* and REPORT_EMAIL variables are set

3. **Test SMTP connection**:
   ```bash
   curl -X POST "https://web-production-665ac.up.railway.app/admin/send-test-email?email=your.email@example.com"
   ```

4. **Check spam folder**: First email might go to spam

### Gmail "Less secure app" error

- Gmail requires an **App Password**, not your regular password
- Make sure 2-Step Verification is enabled first
- Generate a new App Password if the current one doesn't work

### "Authentication failed" error

- Double-check SMTP_USERNAME and SMTP_PASSWORD
- Ensure no extra spaces in environment variables
- Try regenerating App Password

## Manual Testing

You can manually trigger email reports anytime:

```bash
# Via API
curl -X POST "https://web-production-665ac.up.railway.app/admin/send-daily-report"

# Or use the interactive API docs
# Visit: https://web-production-665ac.up.railway.app/docs
```

## Security Notes

- ✅ Use App Passwords (not your main email password)
- ✅ Keep SMTP credentials in Railway environment variables (never in code)
- ✅ Emails sent over encrypted TLS connection
- ✅ No sensitive data in email (only summary statistics)

## Customization

To customize the email template, edit:
```
backend/app/email_notifications.py
```

Functions to modify:
- `generate_status_report()` - Change email HTML
- `format_commercial_rates_table()` - Modify table format
- `send_daily_report()` - Adjust what data is included
