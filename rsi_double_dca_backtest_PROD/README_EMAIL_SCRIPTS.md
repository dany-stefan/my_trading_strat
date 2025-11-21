# Email Scripts Documentation

## Overview

The email notification system has been refactored to follow the DRY (Don't Repeat Yourself) principle with shared modules for HTML formatting and email content generation.

## File Structure

```
rsi_double_dca_backtest/
├── email_formatter.py          # Shared: HTML conversion with mobile-optimized CSS
├── email_generator.py          # Shared: Email content generation logic
├── monitor_strategy.py         # Production: Sends real emails via GitHub Actions
├── simulate_payday_email.py    # Testing: Generates HTML preview only
└── local_email_send_test.sh    # Shell script for testing
```

## Shared Modules

### email_formatter.py
- **Purpose**: Convert plain text to mobile-optimized HTML email
- **Function**: `convert_to_html(text) → html_string`
- **Features**:
  - Mobile-first CSS (17px body text, 15px tables)
  - Responsive tables with horizontal scrolling
  - Markdown table detection and styling
  - Gmail iOS optimizations (-webkit properties)

### email_generator.py
- **Purpose**: Generate email subject and body content
- **Function**: `generate_email_content(rsi, price, cash_pool, total_contributions, rainy_buys, is_simulation) → (subject, body)`
- **Logic**:
  - Determines rainy day status (RSI SMA(7) < 45)
  - Calculates recommendations (buy extra vs save)
  - Formats next payday date
  - Includes all strategy tables and metrics
- **Modes**: 
  - `is_simulation=True`: Adds "SIMULATED" labels for testing
  - `is_simulation=False`: Production email format

## Production vs Testing

### monitor_strategy.py (Production Sender)
- **Purpose**: Production email sender for GitHub Actions workflow
- **Behavior**: Actually SENDS real emails via SMTP
- **Schedule**: Runs on 1st and 15th of each month (or next business day)
- **Environment Variables**:
  - `FORCE_EMAIL=true`: Sends email even if not payday (for testing)
  - `FORCE_EMAIL=false` or unset: Only sends on actual paydays

**⚠️ IMPORTANT**: 
- This script SENDS REAL EMAILS when run with `FORCE_EMAIL=true`
- Use with caution - it will deliver to your inbox
- Primarily intended for GitHub Actions automated runs

### simulate_payday_email.py (Preview Only)
- **Purpose**: Local email preview and testing
- **Behavior**: NEVER sends emails - only generates HTML preview
- **Output**: Creates `simulated_email_preview.html` file
- **Use**: Safe for local testing - just generates a file you can open in browser

## Usage Examples

### Local Preview (Safe - No Email Sent)
```bash
cd rsi_double_dca_backtest
python simulate_payday_email.py
# Opens simulated_email_preview.html in your browser to see how it looks
```

### Production Email (Caution - Sends Real Email)
```bash
cd rsi_double_dca_backtest
FORCE_EMAIL=true python monitor_strategy.py
# ⚠️ This SENDS a real email to your Gmail inbox
```

### GitHub Actions (Automated)
The workflow runs `monitor_strategy.py` on 1st and 15th:
- No `FORCE_EMAIL` needed
- Script detects it's payday and sends automatically
- Updates tracking.json with cash pool and rainy buys

## local_email_send_test.sh Clarification

**Current behavior**:
```bash
#!/bin/bash
FORCE_EMAIL=true python monitor_strategy.py
```

This script **SENDS A REAL EMAIL** because:
1. It sets `FORCE_EMAIL=true`
2. It runs `monitor_strategy.py` (the production sender)
3. Result: Email arrives in your Gmail inbox

**If you want preview only**, run this instead:
```bash
python simulate_payday_email.py
```

## Email Configuration

Both scripts use the same credentials (from `monitor_strategy.py`):
- **SMTP Server**: smtp.gmail.com:587
- **Sender**: d4388707373@gmail.com
- **Password**: kzuf dozw badx wwro (Gmail app password)
- **Recipient**: d4388707373@gmail.com

## Strategy Parameters

Configured in `email_generator.py`:
- **Base DCA**: $150 CAD every payday
- **Rainy Amount**: $150 CAD extra (when RSI SMA(7) < 45)
- **Cash Accumulation**: $30 CAD per payday
- **RSI Threshold**: 45.0
- **Schedule**: 1st and 15th of each month

## Mobile Optimization

All emails are optimized for Gmail iOS app:
- Large touch-friendly text (17px body)
- Responsive tables with horizontal scroll
- Bold first column for easy scanning
- Color-coded headers (blue) and highlight rows (yellow)
- No hover effects (not needed on mobile)

## Development Workflow

1. **Make changes** to strategy logic → Update `email_generator.py`
2. **Test locally** → Run `simulate_payday_email.py` → Open HTML preview
3. **Verify on mobile** → Email HTML file to yourself or test via FORCE_EMAIL
4. **Deploy** → Commit changes, GitHub Actions handles production emails

## Troubleshooting

### "I ran the shell script and got a real email!"
- That's expected - `local_email_send_test.sh` uses `FORCE_EMAIL=true` with `monitor_strategy.py`
- For preview only, use: `python simulate_payday_email.py`

### "Tables look cramped on iPhone"
- Already optimized with 15px font, horizontal scrolling, and touch-friendly padding
- Open `simulated_email_preview.html` on desktop to verify mobile @media queries

### "Email not sending from GitHub Actions"
- Check workflow schedule (1st and 15th only)
- Verify `SENDER_PASSWORD` secret is set correctly
- Review workflow logs for SMTP errors
