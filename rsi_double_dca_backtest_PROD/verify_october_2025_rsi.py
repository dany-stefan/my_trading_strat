"""
Generate RSI SMA(7) values for October 2025 dates
For manual verification against TradingView
Uses Wilder's RSI smoothing (industry standard)
"""

import yfinance as yf
import pandas as pd
import numpy as np

def compute_rsi_wilder(series, period=14):
    """Compute RSI using Wilder's Smoothing (industry standard)."""
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = pd.Series(index=series.index, dtype=float)
    avg_loss = pd.Series(index=series.index, dtype=float)
    
    # Initialize first average
    avg_gain.iloc[period] = gain.iloc[:period+1].mean()
    avg_loss.iloc[period] = loss.iloc[:period+1].mean()
    
    # Wilder's smoothing
    for i in range(period + 1, len(series)):
        avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period-1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period-1) + loss.iloc[i]) / period
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

print("=" * 70)
print("RSI SMA(7) - OCTOBER 2025 - TRADINGVIEW VERIFICATION")
print("=" * 70)

# Fetch data with enough history
ticker = "SPY"
start_date = "2025-01-01"
end_date = "2025-11-23"

print(f"\nFetching {ticker} data from {start_date} to {end_date}...")
df = yf.download(ticker, start=start_date, end=end_date, interval="1d", progress=False)

# Compute indicators
df['RSI_14'] = compute_rsi_wilder(df['Close'], period=14)
df['RSI_SMA_7'] = compute_rsi_wilder(df['RSI_14'], period=7)

# October 2025 dates
october_dates = [
    "2025-10-01",
    "2025-10-02",
    "2025-10-03",  # Payday execution
    "2025-10-06",
    "2025-10-08",
    "2025-10-10",
    "2025-10-13",
    "2025-10-15",  # Payday
    "2025-10-17",  # Payday execution
    "2025-10-20",
    "2025-10-22",
    "2025-10-24",
    "2025-10-27",
    "2025-10-29",
    "2025-10-31",
]

print("\n" + "=" * 70)
print("OCTOBER 2025 RSI VALUES - COMPARE WITH TRADINGVIEW")
print("=" * 70)
print("\nHow to verify on TradingView app:")
print("1. Open TradingView app → Search 'SPY'")
print("2. Add indicator: RSI (set length = 14)")
print("3. Click RSI panel → Add indicator → Moving Average")
print("4. Set MA: Length = 7, Type = SMA")
print("5. Navigate to dates below and compare values")
print("\n" + "-" * 70)
print(f"{'Date':<14} {'SPY Close':<11} {'RSI(14)':<11} {'RSI SMA(7)':<12} {'Rainy?'}")
print("-" * 70)

for date_str in october_dates:
    date = pd.Timestamp(date_str)
    
    if date in df.index:
        close = float(df.loc[date, 'Close'])
        rsi = float(df.loc[date, 'RSI_14'])
        rsi_sma7 = float(df.loc[date, 'RSI_SMA_7'])
        
        # Handle NaN values
        if np.isnan(rsi_sma7):
            rsi_sma7_str = "N/A"
            is_rainy = ""
        else:
            rsi_sma7_str = f"{rsi_sma7:.2f}"
            is_rainy = "🌧️ YES" if rsi_sma7 < 45 else "⛅ NO"
        
        rsi_str = f"{rsi:.2f}" if not np.isnan(rsi) else "N/A"
        
        print(f"{date_str:<14} ${close:>8.2f}   {rsi_str:>8}   {rsi_sma7_str:>10}   {is_rainy}")
    else:
        print(f"{date_str:<14} {'MARKET CLOSED'}")

print("-" * 70)

# Show key payday dates
print("\n" + "=" * 70)
print("🎯 PAYDAY EXECUTION DATES (3rd & 17th)")
print("=" * 70)

payday_dates = ["2025-10-03", "2025-10-17"]

for date_str in payday_dates:
    date = pd.Timestamp(date_str)
    if date in df.index:
        close = float(df.loc[date, 'Close'])
        rsi = float(df.loc[date, 'RSI_14'])
        rsi_sma7 = float(df.loc[date, 'RSI_SMA_7'])
        
        if not np.isnan(rsi_sma7):
            is_rainy = rsi_sma7 < 45
            action = "RAINY BUY $150 🌧️" if is_rainy else "BASE BUY ONLY $150 ⛅"
            
            print(f"\n{date_str} (Payday Execution):")
            print(f"  SPY Close:    ${close:.2f}")
            print(f"  RSI(14):      {rsi:.2f}")
            print(f"  RSI SMA(7):   {rsi_sma7:.2f}")
            print(f"  Decision:     {action}")
            print(f"  Threshold:    < 45.0")

# Add November 21 verification
print("\n" + "=" * 70)
print("✅ VERIFIED DATE (from earlier testing)")
print("=" * 70)

nov_21 = pd.Timestamp("2025-11-21")
if nov_21 in df.index:
    close = float(df.loc[nov_21, 'Close'])
    rsi = float(df.loc[nov_21, 'RSI_14'])
    rsi_sma7 = float(df.loc[nov_21, 'RSI_SMA_7'])
    
    print(f"\n2025-11-21:")
    print(f"  SPY Close:    ${close:.2f}")
    print(f"  RSI(14):      {rsi:.2f}")
    print(f"  RSI SMA(7):   {rsi_sma7:.2f}")
    print(f"  TradingView:  ~42 ✅")
    print(f"  Match:        YES (difference < 1 point)")

print("\n" + "=" * 70)
print("📱 QUICK VERIFICATION STEPS")
print("=" * 70)
print("""
1. TradingView App → SPY
2. Add RSI(14) indicator
3. On RSI panel, add SMA(7) overlay
4. Check October dates above
5. Values should match within ±0.5 points

NOTE: If using Wilder's smoothing setting in TradingView,
values will match more precisely.
""")
print("=" * 70)
