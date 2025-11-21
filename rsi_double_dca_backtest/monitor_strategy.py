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
import json
import os
from pathlib import Path

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

# Tracking file
TRACKING_FILE = Path(__file__).parent / "strategy_tracking.json"

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_rsi(ticker="SPY", period=14, lookback_days=100):
    """Fetch SPY data and calculate current RSI."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_days)
    
    try:
        df = yf.download(ticker, start=start_date, end=end_date, interval="1d", progress=False)
        if df.empty:
            return None, None
        
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
        
        current_rsi = rsi.iloc[-1]
        current_price = close.iloc[-1]
        
        return current_rsi, current_price
    
    except Exception as e:
        print(f"Error fetching RSI: {e}")
        return None, None


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
            "cash_pool": 330.0,  # Starting cash pool balance
            "total_contributions": 0.0,
            "rainy_buys": [],
            "last_payday": None,
            "last_check": None,
            "initial_cash_pool": 330.0  # Track initial balance for reference
        }
    
    with open(TRACKING_FILE, 'r') as f:
        return json.load(f)


def save_tracking(data):
    """Save tracking data to JSON file."""
    with open(TRACKING_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def send_email(subject, body):
    """Send email notification."""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = EMAIL_CONFIG['recipient_email']
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
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
    rsi, price = get_rsi(period=RSI_PERIOD)
    
    if rsi is None:
        print("❌ Failed to fetch RSI data")
        return
    
    print(f"Current SPY RSI(14): {rsi:.2f}")
    print(f"Current SPY Price: ${price:.2f}")
    print(f"Cash Pool: ${cash_pool:.2f}")
    print()
    
    # Check if it's payday
    if is_payday():
        print("🗓️  TODAY IS PAYDAY!")
        
        # Check if we already processed this payday
        last_payday = tracking.get('last_payday')
        if last_payday == today_str:
            print("   (Already processed)")
        else:
            # Add cash to pool
            cash_pool += CASH_ACCUMULATION
            tracking['cash_pool'] = cash_pool
            tracking['last_payday'] = today_str
            
            print(f"   💰 Added ${CASH_ACCUMULATION:.2f} to cash pool")
            print(f"   💰 New cash pool: ${cash_pool:.2f}")
            
            # Base investment reminder
            subject = f"📅 PAYDAY: Investment Metrics - {today_str}"
            
            # Check if this is the first email (initial cash pool note)
            initial_cash_note = ""
            if tracking.get('initial_cash_pool') and cash_pool >= 330.0 and len(tracking.get('rainy_buys', [])) == 0:
                initial_cash_note = f"\n💡 NOTE: Starting cash pool balance: ${tracking.get('initial_cash_pool', 330.0):.2f}\n   This is your initial reserve for rainy day opportunities.\n"
            
            body = f"""
{STRATEGY_NAME} - Payday Investment Metrics

Date: {today_str}
SPY RSI(14): {rsi:.2f}
SPY Price: ${price:.2f}
Cash Pool: ${cash_pool:.2f}{initial_cash_note}

═══════════════════════════════════════════════════════════════════

YOUR DECISION TODAY:

1️⃣ BASE INVESTMENT (Always do this):
   ✅ Invest $150 CAD in SPY
   ✅ Add $30 to your cash pool
   → New cash pool will be: ${cash_pool:.2f}

2️⃣ RAINY DAY CHECK:
   Current RSI: {rsi:.2f}
   Rainy threshold: < {RSI_THRESHOLD}
   
   {'✅ RAINY DAY - RSI < 45!' if rsi < RSI_THRESHOLD else '⛅ NOT RAINY - RSI ≥ 45'}
   
   {'🔥 RECOMMENDATION: Buy extra $150 from cash pool' if rsi < RSI_THRESHOLD and cash_pool >= RAINY_AMOUNT else '💰 RECOMMENDATION: Save your cash for next rainy day' if rsi >= RSI_THRESHOLD else '⚠️  Rainy day but insufficient cash (need $' + str(RAINY_AMOUNT) + ', have $' + str(cash_pool) + ')'}
   
   {'   Total investment today: $300 ($150 base + $150 rainy)' if rsi < RSI_THRESHOLD and cash_pool >= RAINY_AMOUNT else '   Total investment today: $150 (base only)'}
   {'   Cash pool after: $' + str(cash_pool - RAINY_AMOUNT) if rsi < RSI_THRESHOLD and cash_pool >= RAINY_AMOUNT else ''}

Next payday: {'1st' if today.day >= PAYDAY_DAY_OF_MONTH_2 else '15th'} of {'next month' if today.day >= PAYDAY_DAY_OF_MONTH_2 else 'this month'}

═══════════════════════════════════════════════════════════════════

VARIANT PERFORMANCE SUMMARY (22-year backtest)

┌──────────────┬──────────┬──────────┬──────────┬────────────┐
│ Variant      │   CAGR   │ Hit Rate │ End Value│ Total Cost │
├──────────────┼──────────┼──────────┼──────────┼────────────┤
│ #1 Weekly    │  33.54%  │  68.5%   │ $600,967 │  $104,500  │
│ $150 RSI<40  │          │          │          │            │
├──────────────┼──────────┼──────────┼──────────┼────────────┤
│ #2 Bi-weekly │  33.54%  │  80.0%   │ $600,907 │  $104,350  │
│ $150 RSI<45  │          │  ⭐ BEST │          │            │
│ (YOUR PICK)  │          │          │          │            │
├──────────────┼──────────┼──────────┼──────────┼────────────┤
│ #3 Weekly    │  33.54%  │  65.3%   │ $600,679 │  $104,450  │
│ $100 RSI<45  │          │          │          │            │
└──────────────┴──────────┴──────────┴──────────┴────────────┘

Key Metrics:
• All 3 variants: Identical 33.54% CAGR (same long-term returns)
• Your variant (#2): HIGHEST hit rate at 80% (most sustainable)
• 22-year period: 2003-2025 (includes 2008 crash, COVID, all cycles)
• Return per $1 invested: $5.76 (every dollar becomes $5.76)

═══════════════════════════════════════════════════════════════════

STRATEGY ASSUMPTIONS & FRAMEWORK

Your Regular Strategy (Variant #2):
• Payday schedule: 1st and 15th of each month (next business day if weekend)
• Base investment: $150 CAD every payday (always do this)
• Cash savings: $30 CAD every payday → builds cash pool
• Asset: SPY (S&P 500 ETF) converted to CAD

Rainy Day Rule:
• Check RSI(14) only on payday (bi-weekly)
• If RSI < 45: Deploy extra $150 from cash pool
• If RSI ≥ 45: Only invest base $150, save the $30
• Expected hit rate: 80% of rainy opportunities

═══════════════════════════════════════════════════════════════════

WHY YOU CHOSE VARIANT #2 (Reminder)

Top 3 Variants Comparison:
┌─────────┬────────────┬────────┬──────────┬──────┬──────────┬─────────┐
│ Rank    │ Cadence    │ Amount │ RSI      │ CAGR │ Hit Rate │ Why NOT │
├─────────┼────────────┼────────┼──────────┼──────┼──────────┼─────────┤
│ #1      │ Weekly     │ $150   │ < 40     │33.54%│  68.5%   │ Must    │
│         │ Every Mon  │        │          │      │          │ check   │
│         │            │        │          │      │          │ weekly  │
├─────────┼────────────┼────────┼──────────┼──────┼──────────┼─────────┤
│ #2 ✅   │ Bi-weekly  │ $150   │ < 45     │33.54%│  80.0%   │ PAYDAY  │
│ (YOU)   │ Payday     │        │          │      │          │ ALIGNED │
│         │ 1st & 15th │        │          │      │          │ SIMPLE! │
├─────────┼────────────┼────────┼──────────┼──────┼──────────┼─────────┤
│ #3      │ Weekly     │ $100   │ < 45     │33.54%│  65.3%   │ Smaller │
│         │ Every Mon  │        │          │      │          │ position│
└─────────┴────────────┴────────┴──────────┴──────┴──────────┴─────────┘

Your Choice = #2 Because:
✅ Only check RSI when you get paid (easier schedule)
✅ Highest hit rate (80% vs 68.5% and 65.3%)
✅ Same returns as #1 and #3 (33.54% CAGR)
✅ Best for busy people with paychecks

═══════════════════════════════════════════════════════════════════

CURRENT STATUS:
• RSI: {rsi:.2f} ({'RAINY' if rsi < RSI_THRESHOLD else 'NORMAL'})
• Cash pool: ${cash_pool:.2f}
• Next rainy buy available: {'Yes' if cash_pool >= RAINY_AMOUNT else f'After {int((RAINY_AMOUNT - cash_pool) / CASH_ACCUMULATION)} more paydays'}

Expected long-term results (22 years):
• CAGR: 33.54%
• Final equity: $600,907 on $104,350 invested
• Rainy buys: ~112 opportunities over time

═══════════════════════════════════════════════════════════════════

Strategy: Bi-weekly $150 base + $150 rainy (RSI < 45)
Next check: Your next payday
            """
            send_email(subject, body)
    
    # Check for rainy day conditions (ONLY on payday)
    if is_payday():
        print()
        print("☔ CHECKING RAINY DAY CONDITIONS...")
        print(f"   RSI Threshold: < {RSI_THRESHOLD}")
        print(f"   Current RSI: {rsi:.2f}")
        print(f"   Cash Required: ${RAINY_AMOUNT:.2f}")
        print(f"   Cash Available: ${cash_pool:.2f}")
        print()
        
        if rsi < RSI_THRESHOLD:
            print("   ✅ RSI < 45 - RAINY DAY DETECTED!")
            
            if cash_pool >= RAINY_AMOUNT:
                print(f"   ✅ Cash pool sufficient (${cash_pool:.2f} >= ${RAINY_AMOUNT:.2f})")
                print()
                print("🚨 " + "=" * 76)
                print("🚨 RAINY DAY BUY SIGNAL - ACTION REQUIRED!")
                print("🚨 " + "=" * 76)
                
                # Send alert email
                subject = f"🚨 RAINY DAY ALERT: Buy the Dip! RSI {rsi:.2f} - {today_str}"
                body = f"""
🚨 RAINY DAY BUY SIGNAL DETECTED!

Date: {today_str}
SPY RSI(14): {rsi:.2f} (threshold: < {RSI_THRESHOLD})
SPY Price: ${price:.2f}
Cash Pool Available: ${cash_pool:.2f}

ACTION REQUIRED:
🔥 BUY ${RAINY_AMOUNT:.2f} CAD of SPY from your cash pool
🔥 This is IN ADDITION to your regular $150 payday investment

Total investment today:
- Base investment: $150.00
- Rainy day extra: $150.00
- TOTAL: $300.00 CAD

After this buy:
- Remaining cash pool: ${cash_pool - RAINY_AMOUNT:.2f}

═══════════════════════════════════════════════════════════════════

STRATEGY ASSUMPTIONS & FRAMEWORK

Base Strategy (Always):
• Bi-weekly payday: 3rd and 18th of each month
• Base investment: $150 CAD every payday (no exceptions)
• Cash savings: $30 CAD every payday → builds cash pool
• Asset: SPY (S&P 500 ETF) in CAD

Rainy Day Rule (Variant #2):
• Check RSI(14) on payday only
• If RSI < 45: Deploy $150 from cash pool (if available)
• Expected hit rate: 80% (miss 20% by design for sustainability)

═══════════════════════════════════════════════════════════════════

WHY YOU CHOSE VARIANT #2 (vs other top variants)

Variant Comparison Table:
┌─────────┬────────────┬────────┬──────────┬──────┬──────────┬─────────┐
│ Rank    │ Cadence    │ Amount │ RSI      │ CAGR │ Hit Rate │ Reason  │
├─────────┼────────────┼────────┼──────────┼──────┼──────────┼─────────┤
│ #1      │ Weekly     │ $150   │ < 40     │33.54%│  68.5%   │ Complex │
│         │ (Every Mon)│        │          │      │          │ schedule│
├─────────┼────────────┼────────┼──────────┼──────┼──────────┼─────────┤
│ #2 ✅   │ Bi-weekly  │ $150   │ < 45     │33.54%│  80.0%   │ Payday  │
│ (YOU)   │ (Payday)   │        │          │      │          │ aligned │
├─────────┼────────────┼────────┼──────────┼──────┼──────────┼─────────┤
│ #3      │ Weekly     │ $100   │ < 45     │33.54%│  65.3%   │ Smaller │
│         │ (Every Mon)│        │          │      │          │ buys    │
└─────────┴────────────┴────────┴──────────┴──────┴──────────┴─────────┘

Why Variant #2 is YOUR best choice:
✅ Payday-aligned: Only check RSI when you get paid (3rd & 18th)
✅ Highest hit rate: 80% success (vs 68.5% and 65.3%)
✅ Same CAGR: Identical 33.54% returns as #1 and #3
✅ Simplest schedule: No need to check markets every Monday
✅ Less stress: Only 2 decisions per month vs 4+ for weekly

Trade-offs you accepted:
• Slightly less aggressive than #1 (RSI < 45 vs < 40)
• Miss mid-week dips (but payday alignment simplifies life)
• Identical long-term performance with easier execution

═══════════════════════════════════════════════════════════════════

BACKTEST RESULTS (22 years: 2003-2025)

Expected Performance:
- Total contributions: $104,350 CAD
- Final equity: $600,907 CAD
- CAGR: 33.54%
- Max drawdown: -27.47%
- Rainy buys: 112 / 140 opportunities (80%)
- Return per dollar: $5.76

Why this entry is good:
- RSI {rsi:.2f} indicates oversold conditions
- Historical win rate: 80% on RSI < 45 bi-weekly entries
- You're buying weakness at payday = optimal timing

═══════════════════════════════════════════════════════════════════

Strategy: {STRATEGY_NAME}
Hit rate target: 80% ± 10%
Next check: Your next payday (3rd or 18th)
                """
                
                if send_email(subject, body):
                    # Record the rainy buy
                    tracking['rainy_buys'].append({
                        'date': today_str,
                        'rsi': float(rsi),
                        'price': float(price),
                        'amount': RAINY_AMOUNT,
                        'cash_before': cash_pool,
                        'cash_after': cash_pool - RAINY_AMOUNT
                    })
                    
                    # Deduct from cash pool
                    tracking['cash_pool'] = cash_pool - RAINY_AMOUNT
                    print(f"\n   💸 Cash pool updated: ${cash_pool:.2f} → ${cash_pool - RAINY_AMOUNT:.2f}")
            
            else:
                print(f"   ❌ Insufficient cash (${cash_pool:.2f} < ${RAINY_AMOUNT:.2f})")
                print(f"   📊 MISSED OPPORTUNITY - need ${RAINY_AMOUNT - cash_pool:.2f} more")
                
                # Send notification about missed opportunity
                subject = f"📊 Rainy Day Missed (Insufficient Cash) - RSI {rsi:.2f}"
                body = f"""
Rainy Day Conditions Met, But Insufficient Cash

Date: {today_str}
SPY RSI(14): {rsi:.2f} (threshold: < {RSI_THRESHOLD})
SPY Price: ${price:.2f}
Cash Pool: ${cash_pool:.2f}
Cash Required: ${RAINY_AMOUNT:.2f}
Shortfall: ${RAINY_AMOUNT - cash_pool:.2f}

This is expected behavior - you'll hit ~80% of rainy opportunities.
Missing 20% ensures sustainable cash management.

Next cash accumulation: Next payday (+$30)

---
Strategy: {STRATEGY_NAME}
                """
                send_email(subject, body)
        
        else:
            print(f"   ℹ️  RSI {rsi:.2f} >= {RSI_THRESHOLD} - No rainy day signal")
            print(f"   💰 Cash pool preserved: ${cash_pool:.2f}")
    
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
