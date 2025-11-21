"""
Simulate Payday Email - Preview Email Content Without Sending

This script shows exactly what your payday email will look like,
without actually sending it. Perfect for testing the template.
"""

import os
import json
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd

# =============================================================================
# CONFIGURATION
# =============================================================================
TRACKING_FILE = "strategy_tracking.json"
INITIAL_CASH_POOL = 330.0

# Strategy parameters (Variant #2)
DCA_BASE_AMOUNT = 150.0
CASH_ACCUMULATION = 30.0
RAINY_AMOUNT = 150.0
RSI_THRESHOLD = 45
RSI_PERIOD = 14

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def get_rsi(ticker="SPY", period=14, lookback_days=100):
    """Fetch current RSI for a ticker."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_days)
    
    df = yf.download(ticker, start=start_date, end=end_date, interval="1d", progress=False)
    if df.empty:
        return None, None
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    col = "Adj Close" if "Adj Close" in df.columns else "Close"
    prices = df[col].copy()
    
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    current_rsi = rsi.iloc[-1]
    current_price = prices.iloc[-1]
    
    return current_rsi, current_price

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
    rsi, price = get_rsi("SPY", RSI_PERIOD)
    
    if rsi is None:
        print("❌ Error: Could not fetch RSI data")
        return
    
    print(f"✅ Current SPY RSI(14): {rsi:.2f}")
    print(f"✅ Current SPY Price: ${price:.2f}")
    
    # Load tracking
    tracking = load_tracking()
    cash_pool = tracking.get("cash_pool", INITIAL_CASH_POOL)
    total_contributions = tracking.get("total_contributions", 0.0)
    rainy_buys = tracking.get("rainy_buys", [])
    
    print(f"✅ Current cash pool: ${cash_pool:.2f}")
    print(f"✅ Total contributions to date: ${total_contributions:,.2f}")
    print(f"✅ Total rainy buys to date: {len(rainy_buys)}\n")
    
    # Simulate payday
    today = datetime.now()
    simulated_payday_date = today.strftime("%B %d, %Y")
    
    # Determine next payday (for email)
    if today.day < 15:
        next_payday_text = "15th of this month"
    else:
        next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
        next_payday_text = f"1st of {next_month.strftime('%B')}"
    
    # Check if rainy day
    is_rainy = rsi < RSI_THRESHOLD
    can_deploy = cash_pool >= RAINY_AMOUNT
    
    # Build email subject
    subject = f"📅 PAYDAY SIMULATION: Investment Metrics - {simulated_payday_date}"
    
    # Determine recommendation
    if is_rainy and can_deploy:
        recommendation = f"🔥 RECOMMENDATION: Buy extra ${RAINY_AMOUNT:.0f} from cash pool"
        total_investment_today = DCA_BASE_AMOUNT + RAINY_AMOUNT
        # IMPORTANT: Even on rainy days, you still save $30 to cash pool
        new_cash_pool = cash_pool - RAINY_AMOUNT + CASH_ACCUMULATION
        action_text = f"Total investment today: ${total_investment_today:.0f} (${DCA_BASE_AMOUNT:.0f} base + ${RAINY_AMOUNT:.0f} rainy)"
        cash_after_text = f"Cash pool after: ${new_cash_pool:.2f} (deployed ${RAINY_AMOUNT:.0f}, saved ${CASH_ACCUMULATION:.0f})"
    elif is_rainy and not can_deploy:
        recommendation = f"⚠️  Rainy day but insufficient cash (need ${RAINY_AMOUNT:.0f}, have ${cash_pool:.2f})"
        total_investment_today = DCA_BASE_AMOUNT
        new_cash_pool = cash_pool + CASH_ACCUMULATION
        action_text = f"Total investment today: ${total_investment_today:.0f} (base only)"
        cash_after_text = f"Cash pool after saving: ${new_cash_pool:.2f}"
    else:
        recommendation = f"💰 RECOMMENDATION: Save your cash for next rainy day"
        total_investment_today = DCA_BASE_AMOUNT
        new_cash_pool = cash_pool + CASH_ACCUMULATION
        action_text = f"Total investment today: ${total_investment_today:.0f} (base only)"
        cash_after_text = f"Cash pool after saving: ${new_cash_pool:.2f}"
    
    rainy_status = "✅ RAINY DAY - RSI < 45!" if is_rainy else "⛅ NOT RAINY - RSI ≥ 45"
    
    # Note about initial balance
    initial_note = ""
    if total_contributions == 0:
        initial_note = f"\n   📌 NOTE: Starting with ${INITIAL_CASH_POOL:.2f} initial cash pool (enough for 2 rainy buys)"
    
    # Print email preview
    print("=" * 80)
    print("EMAIL SUBJECT:")
    print("=" * 80)
    print(subject)
    print("\n" + "=" * 80)
    print("EMAIL BODY:")
    print("=" * 80)
    
    email_body = f"""
════════════════════════════════════════════════════════════════════
🎯 RSI STRATEGY MONITOR - PAYDAY SIMULATION
════════════════════════════════════════════════════════════════════

Date: {simulated_payday_date} (SIMULATED)
Current SPY Price: ${price:.2f} USD
Current RSI(14): {rsi:.2f}

════════════════════════════════════════════════════════════════════

📊 TODAY'S PAYDAY ACTIONS

1️⃣ BASE INVESTMENT (always):
   Invest: ${DCA_BASE_AMOUNT:.0f} CAD into SPY
   
2️⃣ RAINY DAY CHECK:
   Current RSI: {rsi:.2f}
   Rainy threshold: < {RSI_THRESHOLD}
   
   {rainy_status}
   
   {recommendation}
   
   {action_text}
   {cash_after_text}

Next payday: {next_payday_text}

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

CURRENT STATUS

Cash Pool: ${cash_pool:.2f}
Total Contributions to Date: ${total_contributions:,.2f}
Total Rainy Buys to Date: {len(rainy_buys)}{initial_note}

Expected Long-Term Results (22 years):
• CAGR: 33.54%
• Final Equity: $600,907
• Total Invested: $104,350
• Successful Rainy Buys: 112 / 140 opportunities (80%)

═══════════════════════════════════════════════════════════════════

This is a SIMULATED email for testing purposes.
Actual payday emails will be sent on the 1st and 15th of each month.

════════════════════════════════════════════════════════════════════
"""
    
    print(email_body)
    print("\n" + "=" * 80)
    print("✅ EMAIL PREVIEW COMPLETE")
    print("=" * 80)
    print("\nThis is what you'll receive on the 1st and 15th of each month!")
    print("The actual email will be sent via GitHub Actions workflow.\n")

if __name__ == "__main__":
    main()
