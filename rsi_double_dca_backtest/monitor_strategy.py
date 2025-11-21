"""
RSI Cash Strategy - Variant #2 Implementation
==============================================

Live monitoring script for:
- Bi-weekly $150 RSI < 45 strategy
- Schedule: 3rd day of month + 3rd day after mid-month
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

# =============================================================================
# CONFIGURATION
# =============================================================================

# Email settings (configure with your credentials)
EMAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", 587)),
    "sender_email": os.getenv("SENDER_EMAIL", "d4388707373@gmail.com"),
    "sender_password": os.getenv("SENDER_PASSWORD", "kzuf dozw badx wwro"),
    "recipient_email": os.getenv("RECIPIENT_EMAIL", "d4388707373@gmail.com"),
}

# Strategy parameters (Variant #2)
STRATEGY_NAME = "RSI Cash Variant #2"
DCA_BASE_AMOUNT = 150.0  # CAD
RAINY_AMOUNT = 150.0  # CAD
RSI_THRESHOLD = 45.0
CASH_ACCUMULATION = 30.0  # CAD per payday
RSI_PERIOD = 14

# Bi-weekly schedule: 1st and 15th of month (or next business day if weekend)
PAYDAY_DAY_OF_MONTH_1 = 1  # 1st of each month
PAYDAY_DAY_OF_MONTH_2 = 15  # 15th of each month

# Initial cash pool balance
INITIAL_CASH_POOL = 330.0  # Starting cash pool (enough for 2 rainy buys)

# Check if we should force email sending (for manual testing)
FORCE_EMAIL = os.getenv("FORCE_EMAIL", "false").lower() == "true"

# Tracking file
TRACKING_FILE = Path(__file__).parent / "strategy_tracking.json"

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_rsi(ticker="SPY", period=14, lookback_days=100):
    """Fetch SPY data and calculate current RSI and EMA of RSI."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_days)
    
    try:
        df = yf.download(ticker, start=start_date, end=end_date, interval="1d", progress=False)
        if df.empty:
            return None, None, None
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        close = df["Close"] if "Close" in df.columns else df["Adj Close"]
        
        # Calculate RSI
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # Calculate EMA(14) of RSI
        rsi_ema = rsi.ewm(span=14, adjust=False).mean()
        
        current_rsi = rsi.iloc[-1]
        current_rsi_ema = rsi_ema.iloc[-1]
        current_price = close.iloc[-1]
        
        return current_rsi, current_rsi_ema, current_price
    
    except Exception as e:
        print(f"Error fetching RSI: {e}")
        return None, None, None


def is_payday(date=None):
    """Check if today (or given date) is a payday (1st or 15th, or next business day if weekend)."""
    if date is None:
        date = datetime.now()
    
    day = date.day
    weekday = date.weekday()  # 0=Monday, 6=Sunday
    
    # Check if today is exactly the 1st or 15th
    if day == PAYDAY_DAY_OF_MONTH_1 or day == PAYDAY_DAY_OF_MONTH_2:
        return True
    
    # Check if it's Monday and the 1st/15th was on a weekend
    if weekday == 0:  # Monday
        # Check if 1st was Saturday (day=3) or Sunday (day=2)
        if day == 3 and date.replace(day=1).weekday() == 6:  # 1st was Sunday
            return True
        if day == 2 and date.replace(day=1).weekday() == 5:  # 1st was Saturday
            return True
        
        # Check if 15th was Saturday (day=17) or Sunday (day=16)
        if day == 17 and date.replace(day=15).weekday() == 6:  # 15th was Sunday
            return True
        if day == 16 and date.replace(day=15).weekday() == 5:  # 15th was Saturday
            return True
    
    return False


def load_tracking():
    """Load tracking data from JSON file."""
    if not TRACKING_FILE.exists():
        return {
            "cash_pool": INITIAL_CASH_POOL,
            "total_contributions": 0.0,
            "rainy_buys": [],
            "last_payday": None,
            "last_check": None
        }
    
    with open(TRACKING_FILE, 'r') as f:
        data = json.load(f)
    
    # Ensure initial cash pool is set for first-time users
    if data.get("cash_pool", 0) == 0 and data.get("total_contributions", 0) == 0:
        data["cash_pool"] = INITIAL_CASH_POOL
    
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
            'rsi_history_thresholds.png'
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
    
    # Get current RSI
    print("Fetching SPY RSI(14)...")
    rsi, rsi_ema, price = get_rsi(period=RSI_PERIOD)
    
    if rsi is None:
        print("❌ Failed to fetch RSI data")
        return
    
    print(f"Current SPY RSI(14): {rsi:.2f}")
    print(f"Current RSI EMA(14): {rsi_ema:.2f}")
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
            
            # Generate email using shared function
            # Use is_simulation=True when FORCE_EMAIL is enabled (local test run)
            subject, body = generate_email_content(
                rsi=rsi,
                price=price,
                cash_pool=cash_pool,
                total_contributions=tracking.get('total_contributions', 0),
                rainy_buys=tracking.get('rainy_buys', []),
                is_simulation=FORCE_EMAIL  # True for local test runs, False for production
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
        print(f"   RSI Threshold: < {RSI_THRESHOLD}")
        print(f"   Current RSI: {rsi:.2f}")
        print(f"   Cash Required: ${RAINY_AMOUNT:.2f}")
        print(f"   Cash Available: ${tracking['cash_pool']:.2f}")
        print()
        
        if rsi < RSI_THRESHOLD:
            print("   ✅ RSI < 45 - RAINY DAY DETECTED!")
            
            if tracking['cash_pool'] >= RAINY_AMOUNT:
                print(f"   ✅ Cash pool sufficient (${tracking['cash_pool']:.2f} >= ${RAINY_AMOUNT:.2f})")
                print("   📝 Recording rainy buy in tracking...")
                
                # Record the rainy buy (only if not test mode)
                cash_before_rainy = tracking['cash_pool']
                cash_after_rainy = tracking['cash_pool'] - RAINY_AMOUNT + CASH_ACCUMULATION
                
                if not FORCE_EMAIL:
                    tracking['rainy_buys'].append({
                        'date': today_str,
                        'rsi': float(rsi),
                        'price': float(price),
                        'amount': RAINY_AMOUNT,
                        'cash_before': cash_before_rainy,
                        'cash_after': cash_after_rainy
                    })
                    
                    # Update cash pool: already added $30 in payday section, now subtract rainy buy
                    tracking['cash_pool'] = cash_after_rainy
                    
                    print(f"   💸 Final cash pool: ${tracking['cash_pool']:.2f}")
                    print("   ✅ Rainy buy recorded!")
                else:
                    print(f"   🧪 Test mode - rainy buy NOT recorded")
                    print(f"   💸 Would be final cash pool: ${cash_after_rainy:.2f}")
            
            else:
                print(f"   ❌ Insufficient cash (${tracking['cash_pool']:.2f} < ${RAINY_AMOUNT:.2f})")
                print(f"   📊 MISSED OPPORTUNITY - This is expected (80% hit rate target)")
        
        else:
            print(f"   ℹ️  RSI {rsi:.2f} >= {RSI_THRESHOLD} - No rainy day signal")
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
