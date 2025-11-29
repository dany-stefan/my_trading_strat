"""
Simulate Payday Email - Preview Email Content With HTML Formatting

This script shows exactly what your payday email will look like,
including HTML table formatting, without actually sending it.

Uses the same modular components as monitor_strategy.py for consistency.
"""

import os
import json
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
from email.mime.image import MIMEImage
from pathlib import Path
from email_formatter import convert_to_html
from email_generator import generate_email_content
from payday_scheduler import get_scheduler

# =============================================================================
# CONFIGURATION (should match monitor_strategy.py)
# =============================================================================
TRACKING_FILE = "strategy_tracking.json"
INITIAL_CASH_POOL = 330.0

# Strategy parameters (Variant #2)
DCA_BASE_AMOUNT = 150.0
CASH_ACCUMULATION = 30.0
RAINY_AMOUNT = 150.0
RSI_THRESHOLD = 45
RSI_PERIOD = 14

# Payday configuration - uses same modular scheduler as production
PAYDAY_DAYS = [3, 17]  # 3rd and 17th of each month
TRADING_EXCHANGE = 'TSX'  # Toronto Stock Exchange
SCHEDULER_TYPE = 'BIWEEKLY_TSX'  # Biweekly with TSX calendar validation

# Initialize payday scheduler (polymorphic - matches production configuration)
payday_scheduler = get_scheduler(
    scheduler_type=SCHEDULER_TYPE,
    days=PAYDAY_DAYS,
    exchange=TRADING_EXCHANGE
)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def get_rsi(ticker="SPY", period=14, lookback_days=100):
    """Fetch current RSI and RSI SMA(7) for a ticker."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_days)
    
    df = yf.download(ticker, start=start_date, end=end_date, interval="1d", progress=False)
    if df.empty:
        return None, None, None
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    col = "Adj Close" if "Adj Close" in df.columns else "Close"
    prices = df[col].copy()
    
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    # Wilder's smoothing for RSI
    avg_gain = pd.Series(index=prices.index, dtype=float)
    avg_loss = pd.Series(index=prices.index, dtype=float)
    
    # First value: SMA over initial period
    avg_gain.iloc[period] = gain.iloc[1:period+1].mean()
    avg_loss.iloc[period] = loss.iloc[1:period+1].mean()
    
    # Subsequent values: Wilder's smoothing
    for i in range(period + 1, len(prices)):
        avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period - 1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period - 1) + loss.iloc[i]) / period
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # Calculate SMA(7) of RSI
    rsi_sma = rsi.rolling(window=7).mean()
    
    current_rsi = rsi.iloc[-1]
    current_rsi_sma = rsi_sma.iloc[-1]
    current_price = prices.iloc[-1]
    
    return current_rsi, current_rsi_sma, current_price

def load_tracking():
    """Load tracking data or initialize if not exists."""
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, 'r') as f:
            data = json.load(f)
    else:
        data = {
            "cash_pool": INITIAL_CASH_POOL,
            "total_contributions": 0.0,
            "rainy_buys": [],
            "last_payday": None,
            "last_check": None
        }
    
    # Ensure initial cash pool is set
    if data.get("cash_pool", 0) == 0 and data.get("total_contributions", 0) == 0:
        data["cash_pool"] = INITIAL_CASH_POOL
    
    return data

# =============================================================================
# MAIN SIMULATION
# =============================================================================
def main():
    print("=" * 80)
    print("SIMULATED PAYDAY EMAIL PREVIEW - November 21, 2025")
    print("=" * 80)
    print("\nFetching current market data...")
    
    # Fetch current market data
    rsi, rsi_sma, price = get_rsi("SPY", RSI_PERIOD)
    
    if rsi is None:
        print("❌ Error: Could not fetch RSI data")
        return
    
    print(f"✅ Current SPY RSI(14): {rsi:.2f}")
    print(f"✅ Current RSI SMA(7): {rsi_sma:.2f}")
    print(f"✅ Current SPY Price: ${price:.2f}")
    
    # Load tracking
    tracking = load_tracking()
    cash_pool = tracking.get("cash_pool", INITIAL_CASH_POOL)
    total_contributions = tracking.get("total_contributions", 0.0)
    rainy_buys = tracking.get("rainy_buys", [])
    
    print(f"✅ Current cash pool: ${cash_pool:.2f}")
    print(f"✅ Total contributions to date: ${total_contributions:,.2f}")
    print(f"✅ Total rainy buys to date: {len(rainy_buys)}\n")
    
    # Generate email content using shared function
    subject, email_body = generate_email_content(
        rsi_sma=rsi_sma,  # Using RSI SMA(7) as threshold indicator
        price=price,
        cash_pool=cash_pool,
        total_contributions=total_contributions,
        rainy_buys=rainy_buys,
        is_simulation=True,
        rsi_14=rsi  # Include RSI(14) for display in email
    )
    
    # Print email preview
    print("=" * 80)
    print("EMAIL SUBJECT:")
    print("=" * 80)
    print(subject)
    print("\n" + "=" * 80)
    print("EMAIL BODY:")
    print("=" * 80)
    
    # Print plain text version
    print(email_body)
    print("\n" + "=" * 80)
    print("✅ EMAIL PREVIEW COMPLETE (Plain Text Version)")
    print("=" * 80)
    
    # Generate and save HTML version
    html_body = convert_to_html(email_body)
    html_file = "simulated_email_preview.html"
    with open(html_file, 'w') as f:
        f.write(html_body)
    
    print(f"\n📧 HTML email preview saved to: {html_file}")
    print("   Open this file in your browser to see the formatted email!\n")
    print("=" * 80)
    print("This is what you'll receive on the 1st and 15th of each month!")
    print("The actual email will be sent via GitHub Actions workflow.\n")

if __name__ == "__main__":
    main()
