"""
RSI Cash Strategy - Variant #2 Implementation
==============================================

Live monitoring script for:
- Bi-weekly $150 RSI SMA(7) < 45 strategy
- Schedule: 3rd and 17th of month (or next TSX trading day if weekend/holiday)
- Email alerts when rainy day conditions are met

REQUIREMENTS:
pip install yfinance pandas numpy
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import json
import os
from pathlib import Path
from email_formatter import convert_to_html
from email_generator import generate_email_content
from payday_scheduler import get_scheduler
from strategy_config import get_strategy_config
from update_rsi_verification import update_verification_list
from rsi_indicators import compute_rsi_with_sma

# =============================================================================
# CONFIGURATION - CHANGE STRATEGY HERE
# =============================================================================

# Select strategy variant (SINGLE SOURCE OF TRUTH)
# Options: 'VARIANT_1', 'VARIANT_2', 'VARIANT_3'
STRATEGY_VARIANT = 'VARIANT_2'

# Load strategy configuration (all parameters come from here)
strategy_config = get_strategy_config(STRATEGY_VARIANT)

# Email settings (configure with your credentials)
EMAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", 587)),
    "sender_email": os.getenv("SENDER_EMAIL", "d4388707373@gmail.com"),
    "sender_password": os.getenv("SENDER_PASSWORD", "kzuf dozw badx wwro"),
    "recipient_email": os.getenv("RECIPIENT_EMAIL", "d4388707373@gmail.com"),
}

# Initialize payday scheduler (polymorphic - uses strategy config)
payday_scheduler = get_scheduler(
    scheduler_type='BIWEEKLY_TSX',
    days=list(strategy_config.payday_days),
    exchange=strategy_config.trading_exchange
)

# Convenience constants from strategy config
STRATEGY_NAME = strategy_config.name
CASH_ACCUMULATION = strategy_config.cash_accumulation_per_payday
RSI_PERIOD = strategy_config.rsi_period

# Check if we should force email sending (for manual testing)
FORCE_EMAIL = os.getenv("FORCE_EMAIL", "false").lower() == "true"

# Tracking file
TRACKING_FILE = Path(__file__).parent / "strategy_tracking.json"

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_rsi(ticker="SPY", period=None, lookback_days=100):
    """
    Fetch SPY data and calculate RSI indicators.
    
    Uses strategy_config to determine which indicators to calculate.
    
    Args:
        ticker: Stock ticker symbol
        period: RSI period (defaults to strategy config)
        lookback_days: Days of historical data to fetch
    
    Returns:
        Tuple of (rsi, rsi_sma, price) or (None, None, None) on error
    """
    if period is None:
        period = strategy_config.rsi_period
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_days)
    
    try:
        df = yf.download(ticker, start=start_date, end=end_date, interval="1d", progress=False)
        if df.empty:
            return None, None, None
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        close = df["Close"] if "Close" in df.columns else df["Adj Close"]
        
        # Calculate RSI using shared module (SINGLE SOURCE OF TRUTH)
        rsi, rsi_sma = compute_rsi_with_sma(
            close, 
            rsi_period=period, 
            sma_period=strategy_config.rsi_sma_period
        )
        
        current_rsi = rsi.iloc[-1]
        current_rsi_sma = rsi_sma.iloc[-1]
        current_price = close.iloc[-1]
        
        return current_rsi, current_rsi_sma, current_price
    
    except Exception as e:
        print(f"Error fetching RSI: {e}")
        return None, None, None


def is_payday(date=None):
    """
    Check if given date (or today) is a payday.
    
    This is a wrapper around the modular payday_scheduler.
    All payday logic is delegated to the scheduler instance,
    which handles TSX calendar validation polymorphically.
    
    To change payday behavior (e.g., switch to NYSE calendar,
    change payday dates, or disable calendar validation),
    simply modify the scheduler configuration at the top of this file.
    
    Args:
        date: Date to check (defaults to today)
    
    Returns:
        True if date is a payday
    """
    return payday_scheduler.is_payday(date)


def load_tracking():
    """Load tracking data from JSON file."""
    if not TRACKING_FILE.exists():
        return {
            "cash_pool": strategy_config.initial_cash_pool,
            "total_contributions": 0.0,
            "rainy_buys": [],
            "last_payday": None,
            "last_check": None
        }
    
    with open(TRACKING_FILE, 'r') as f:
        data = json.load(f)
    
    # Ensure initial cash pool is set for first-time users
    if data.get("cash_pool", 0) == 0 and data.get("total_contributions", 0) == 0:
        data["cash_pool"] = strategy_config.initial_cash_pool
    
    return data


def save_tracking(data):
    """Save tracking data to JSON file."""
    with open(TRACKING_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def send_email(subject, body):
    """Send email notification with HTML formatting and chart attachments."""
    try:
        msg = MIMEMultipart('mixed')
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = EMAIL_CONFIG['recipient_email']
        msg['Subject'] = subject
        
        # Convert plain text body to HTML
        html_body = convert_to_html(body)
        
        # Create multipart alternative for text and HTML
        msg_alternative = MIMEMultipart('alternative')
        part1 = MIMEText(body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg_alternative.attach(part1)
        msg_alternative.attach(part2)
        msg.attach(msg_alternative)
        
        # Attach PNG charts
        chart_files = [
            'strategy_comparison_with_baseline.png',
            'rainy_day_analysis_detailed.png',
            'spy_price_rainy_periods_drawdown.png',
            'variant_2_equity_curve.png',
            'rsi_history_thresholds.png',
            'cash_pool_hit_miss.png',
            'spy_price_hit_miss.png',
            'rsi_hit_miss.png'
        ]
        
        for chart_file in chart_files:
            chart_path = Path(__file__).parent / chart_file
            if chart_path.exists():
                with open(chart_path, 'rb') as f:
                    img = MIMEImage(f.read())
                    img.add_header('Content-Disposition', 'attachment', filename=chart_file)
                    img.add_header('Content-ID', f'<{chart_file}>')
                    msg.attach(img)
        
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['recipient_email'], text)
        server.quit()
        
        print(f"✅ Email sent: {subject}")
        return True
    
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


# =============================================================================
# MAIN MONITORING LOGIC
# =============================================================================

def check_conditions():
    """Main function to check strategy conditions and send alerts."""
    
    print("=" * 80)
    print(f"{STRATEGY_NAME} - DAILY CHECK")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load tracking data
    tracking = load_tracking()
    cash_pool = tracking['cash_pool']
    today = datetime.now().date()
    today_str = today.strftime('%Y-%m-%d')
    
    # Get current RSI and RSI SMA(7)
    print("Fetching SPY RSI(14) and RSI SMA(7)...")
    rsi, rsi_sma, price = get_rsi(period=RSI_PERIOD)
    
    if rsi is None:
        print("❌ Failed to fetch RSI data")
        return
    
    print(f"Current SPY RSI(14): {rsi:.2f}")
    print(f"Current RSI SMA(7): {rsi_sma:.2f}")
    print(f"Current SPY Price: ${price:.2f}")
    print(f"Cash Pool: ${cash_pool:.2f}")
    
    if FORCE_EMAIL:
        print()
        print("🧪 FORCE_EMAIL mode enabled - will send email regardless of payday")
    
    print()
    
    # Check if it's payday (or force email mode)
    if is_payday() or FORCE_EMAIL:
        if FORCE_EMAIL and not is_payday():
            print("🧪 FORCE EMAIL MODE - Simulating payday email (today is NOT actually payday)")
        else:
            print("🗓️  TODAY IS PAYDAY!")
        
        # Check if we already processed this payday
        last_payday = tracking.get('last_payday')
        if last_payday == today_str and not FORCE_EMAIL:
            print("   (Already processed)")
        else:
            if FORCE_EMAIL and last_payday == today_str:
                print("   (Forcing email even though already processed today)")
            
            # Generate metrics snapshot markdown and email using shared function
            try:
                from market_metrics import calculate_market_metrics as _calc_metrics
                metrics_obj = _calc_metrics(
                    rsi_sma=rsi_sma,
                    price=price,
                    cash_pool=cash_pool,
                    total_contributions=tracking.get('total_contributions', 0),
                    rainy_buys=tracking.get('rainy_buys', [])
                )
                m = metrics_obj.get_all_metrics()
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                snapshot_lines = [
                    f"# Metrics Snapshot - {timestamp}",
                    "",
                    "| Metric | Value |",
                    "|---|---|",
                    f"| SPY Price | {m['price_display']} |",
                    f"| RSI SMA(7) | {m['rsi_sma_display']} |",
                    f"| Cash Pool | {m['cash_pool_display']} |",
                    f"| Threshold | {int(m['rsi_threshold'])} |",
                    f"| Rainy Today? | {'Yes' if m['is_rainy'] else 'No'} |",
                    "",
                ]
                snapshot_path = Path(__file__).parent / "METRICS_SNAPSHOT.md"
                snapshot_path.write_text("\n".join(snapshot_lines), encoding="utf-8")
                
                # Update README_MARKET_METRICS.md with live snapshot
                readme_path = Path(__file__).parent / "README_MARKET_METRICS.md"
                if readme_path.exists():
                    readme_content = readme_path.read_text(encoding="utf-8")
                    import re
                    pattern = r"(## 📊 Latest Snapshot.*?\*Last Updated:)[^\n]*(\n\n---)"
                    snapshot_block = f"""## 📊 Latest Snapshot
*Auto-updated on each monitor run*

| Metric | Value |
|---|---|
| SPY Price | {m['price_display']} |
| RSI SMA(7) | {m['rsi_sma_display']} |
| Cash Pool | {m['cash_pool_display']} |
| Threshold | {int(m['rsi_threshold'])} |
| Rainy Today? | {'Yes' if m['is_rainy'] else 'No'} |

*Last Updated: {timestamp}*\n\n---"""
                    readme_content = re.sub(pattern, snapshot_block, readme_content, flags=re.DOTALL)
                    readme_path.write_text(readme_content, encoding="utf-8")
            except Exception as _e:
                print(f"Warning: failed to write metrics snapshot markdown: {_e}")

            # Use is_simulation=True when FORCE_EMAIL is enabled (local test run)
            subject, body = generate_email_content(
                rsi_sma=rsi_sma,  # Using RSI SMA(7) as threshold indicator
                price=price,
                cash_pool=cash_pool,
                total_contributions=tracking.get('total_contributions', 0),
                rainy_buys=tracking.get('rainy_buys', []),
                is_simulation=FORCE_EMAIL,  # True for local test runs, False for production
                rsi_14=rsi  # Include RSI(14) for display in email
            )
            
            send_email(subject, body)
            
            # Update tracking: add cash to pool (only if actually payday, not test mode)
            if is_payday() and not FORCE_EMAIL:
                tracking['cash_pool'] += CASH_ACCUMULATION
                tracking['last_payday'] = today_str
                print(f"   💰 Added ${CASH_ACCUMULATION:.2f} to cash pool")
                print(f"   💰 New cash pool: ${tracking['cash_pool']:.2f}")
            elif FORCE_EMAIL:
                print(f"   🧪 Test mode - cash pool NOT updated (remains ${tracking['cash_pool']:.2f})")
    
    # Check for rainy day conditions (ONLY on payday) and update tracking
    if (is_payday() or FORCE_EMAIL) and not (last_payday == today_str and not FORCE_EMAIL):
        print()
        print("☔ PROCESSING RAINY DAY CHECK...")
        print(f"   Threshold: {strategy_config.get_threshold_description()}")
        print(f"   Current {strategy_config.get_indicator_display_name()}: {rsi_sma:.2f}")
        print(f"   Cash Required: ${strategy_config.rainy_extra_amount:.2f}")
        print(f"   Cash Available: ${tracking['cash_pool']:.2f}")
        print()
        
        # Use modular rainy day evaluation (SINGLE SOURCE OF TRUTH)
        is_rainy = strategy_config.is_rainy_day(rsi=rsi, rsi_sma=rsi_sma)
        
        if is_rainy:
            print(f"   ✅ {strategy_config.get_threshold_description()} - RAINY DAY DETECTED!")
            
            if tracking['cash_pool'] >= strategy_config.rainy_extra_amount:
                print(f"   ✅ Cash pool sufficient (${tracking['cash_pool']:.2f} >= ${strategy_config.rainy_extra_amount:.2f})")
                print("   📝 Recording rainy buy in tracking...")
                
                # Use modular cash pool update
                cash_before_rainy = tracking['cash_pool']
                cash_after_rainy = strategy_config.update_cash_pool(
                    current_pool=tracking['cash_pool'],
                    is_payday=True,
                    was_rainy_buy=True
                )
                
                if not FORCE_EMAIL:
                    tracking['rainy_buys'].append({
                        'date': today_str,
                        'rsi_sma': float(rsi_sma),  # Record indicator value
                        'price': float(price),
                        'amount': strategy_config.rainy_extra_amount,
                        'cash_before': cash_before_rainy,
                        'cash_after': cash_after_rainy
                    })
                    
                    # Update cash pool using modular calculation
                    tracking['cash_pool'] = cash_after_rainy
                    
                    print(f"   💸 Final cash pool: ${tracking['cash_pool']:.2f}")
                    print("   ✅ Rainy buy recorded!")
                else:
                    print(f"   🧪 Test mode - rainy buy NOT recorded")
                    print(f"   💸 Would be final cash pool: ${cash_after_rainy:.2f}")
            
            else:
                print(f"   ❌ Insufficient cash (${tracking['cash_pool']:.2f} < ${strategy_config.rainy_extra_amount:.2f})")
                print(f"   📊 MISSED OPPORTUNITY - This is expected (~{strategy_config.expected_hit_rate*100:.0f}% hit rate)")
        
        else:
            print(f"   ℹ️  {strategy_config.get_indicator_display_name()} {rsi_sma:.2f} >= {strategy_config.rsi_threshold} - No rainy day signal")
            print(f"   💰 Cash pool preserved: ${tracking['cash_pool']:.2f}")
    
    # Update last check timestamp
    tracking['last_check'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Save tracking data
    save_tracking(tracking)
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Cash pool: ${tracking['cash_pool']:.2f}")
    print(f"Total rainy buys: {len(tracking['rainy_buys'])}")
    print(f"Last check: {tracking['last_check']}")
    print("=" * 80)


# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    # Update RSI verification list before checking conditions
    print("=" * 80)
    print("UPDATING RSI VERIFICATION LIST")
    print("=" * 80)
    # NOTE: RSI Verification List is manually verified against TradingView
    # Auto-updates disabled because yfinance gives inconsistent intraday data
    # To update manually, verify values on TradingView and edit RSI_VERIFICATION_LIST.txt
    # try:
    #     entries_added = update_verification_list()
    #     if entries_added > 0:
    #         print(f"✅ Added {entries_added} new verification entries")
    #     else:
    #         print("✅ Verification list already up to date")
    # except Exception as e:
    #     print(f"⚠️  Could not update verification list: {e}")
    #     print("   Continuing with strategy check...")
    # print()
    
    # Setup instructions
    if EMAIL_CONFIG['sender_email'] == "your_email@gmail.com":
        print("=" * 80)
        print("⚠️  EMAIL CONFIGURATION REQUIRED")
        print("=" * 80)
        print()
        print("Please edit this script and update EMAIL_CONFIG with your credentials:")
        print()
        print("For Gmail:")
        print("1. Go to Google Account settings")
        print("2. Security → 2-Step Verification → App Passwords")
        print("3. Generate an app password for 'Mail'")
        print("4. Use that password (not your regular Gmail password)")
        print()
        print("EMAIL_CONFIG = {")
        print('    "smtp_server": "smtp.gmail.com",')
        print('    "smtp_port": 587,')
        print('    "sender_email": "your_email@gmail.com",')
        print('    "sender_password": "your_16_char_app_password",')
        print('    "recipient_email": "your_email@gmail.com",')
        print("}")
        print()
        print("=" * 80)
        print()
        print("Running check without email notifications...")
        print()
    
    check_conditions()
    
    print()
    print("💡 TIP: Schedule this script to run daily using cron (macOS/Linux):")
    print()
    print("   crontab -e")
    print()
    print("   Add this line (runs at 10 AM every day):")
    print(f"   0 10 * * * cd {Path(__file__).parent} && {Path(__file__).parent.parent / '.venv/bin/python'} {Path(__file__).name}")
    print()
    print("   Or use launchd on macOS for more control.")
