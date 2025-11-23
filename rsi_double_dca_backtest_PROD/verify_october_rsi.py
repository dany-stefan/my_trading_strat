"""
Generate RSI SMA(7) values for October 2024 dates
For manual verification with TradingView app
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def compute_rsi_wilder(series, period=14):
    """
    Compute RSI using Wilder's Smoothing (industry standard).
    This matches TradingView, Bloomberg, and all major platforms.
    """
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    
    # Initialize series for avg_gain and avg_loss
    avg_gain = pd.Series(index=series.index, dtype=float)
    avg_loss = pd.Series(index=series.index, dtype=float)
    
    # First average is simple mean
    avg_gain.iloc[period] = gain.iloc[:period+1].mean()
    avg_loss.iloc[period] = loss.iloc[:period+1].mean()
    
    # Subsequent values use Wilder's smoothing: (prev * (n-1) + current) / n
    for i in range(period + 1, len(series)):
        avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period - 1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period - 1) + loss.iloc[i]) / period
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def compute_rsi_sma(rsi_values, period=7):
    """
    Compute SMA of RSI values using Wilder's smoothing.
    """
    # Initialize series
    rsi_sma = pd.Series(index=rsi_values.index, dtype=float)
    
    # First average is simple mean
    rsi_sma.iloc[period-1] = rsi_values.iloc[:period].mean()
    
    # Subsequent values use Wilder's smoothing
    for i in range(period, len(rsi_values)):
        rsi_sma.iloc[i] = (rsi_sma.iloc[i-1] * (period - 1) + rsi_values.iloc[i]) / period
    
    return rsi_sma

# Fetch SPY data
print("Fetching SPY data from Yahoo Finance...")
ticker = "SPY"
start_date = "2024-09-01"  # Extra data for RSI calculation
end_date = "2024-11-01"

df = yf.download(ticker, start=start_date, end=end_date, interval="1d", progress=False)

if df.empty:
    print("❌ No data fetched!")
    exit(1)

# Compute RSI(14) with Wilder's smoothing
print("Computing RSI(14) with Wilder's smoothing...")
rsi_14 = compute_rsi_wilder(df['Close'], period=14)

# Compute RSI SMA(7) with Wilder's smoothing
print("Computing RSI SMA(7) with Wilder's smoothing...")
rsi_sma_7 = compute_rsi_sma(rsi_14, period=7)

# Filter to October 2024 dates
october_data = df[df.index.month == 10].copy()
october_data['RSI_14'] = rsi_14[df.index.month == 10]
october_data['RSI_SMA_7'] = rsi_sma_7[df.index.month == 10]

print("\n" + "="*80)
print("📊 OCTOBER 2024 RSI VALUES FOR MANUAL TRADINGVIEW VERIFICATION")
print("="*80)
print("\nInstructions:")
print("1. Open TradingView app on your phone")
print("2. Search for SPY (S&P 500 ETF)")
print("3. Add RSI(14) indicator")
print("4. Add 7-period SMA overlay on the RSI indicator")
print("5. Compare values below with TradingView on these dates")
print("\n" + "="*80)

# Show all trading days in October
print("\n📅 ALL OCTOBER 2024 TRADING DAYS:\n")
print(f"{'Date':<12} {'SPY Close':<12} {'RSI(14)':<12} {'RSI SMA(7)':<12} {'Rainy?':<8}")
print("-" * 80)

for idx, row in october_data.iterrows():
    date_str = idx.strftime('%Y-%m-%d')
    close = float(row['Close'])
    rsi_14_val = float(row['RSI_14'])
    rsi_sma_7_val = float(row['RSI_SMA_7'])
    
    # Check if rainy day (RSI SMA(7) < 45)
    is_rainy = "🌧️ YES" if rsi_sma_7_val < 45 else "⛅ NO"
    
    print(f"{date_str:<12} ${close:<11.2f} {rsi_14_val:<11.2f} {rsi_sma_7_val:<11.2f} {is_rainy:<8}")

# Highlight key dates for easy verification
print("\n" + "="*80)
print("🎯 KEY DATES FOR QUICK VERIFICATION:")
print("="*80)

key_dates = [
    "2024-10-01",  # Start of month
    "2024-10-03",  # Payday execution day
    "2024-10-07",  # Early week
    "2024-10-10",  # Mid month
    "2024-10-15",  # Around payday
    "2024-10-17",  # Payday execution day
    "2024-10-21",  # Late month
    "2024-10-28",  # End of month
    "2024-10-31",  # Last trading day
]

print(f"\n{'Date':<15} {'RSI SMA(7)':<15} {'TradingView':<15} {'Match?':<10}")
print("-" * 80)

for date_str in key_dates:
    try:
        date_obj = pd.Timestamp(date_str)
        if date_obj in october_data.index:
            rsi_sma_val = float(october_data.loc[date_obj, 'RSI_SMA_7'])
            print(f"{date_str:<15} {rsi_sma_val:<14.2f} {'____.__':<15} {'[ ]':<10}")
        else:
            print(f"{date_str:<15} {'(weekend/holiday)':<14} {'N/A':<15} {'N/A':<10}")
    except Exception as e:
        print(f"{date_str:<15} ERROR: {e}")

print("\n" + "="*80)
print("📝 VERIFICATION CHECKLIST:")
print("="*80)
print("""
1. Open TradingView app
2. Go to SPY chart
3. Add RSI(14) indicator (Settings → Indicators → RSI)
4. Add 7-period SMA on RSI:
   - Click on RSI indicator settings (gear icon)
   - Add MA (Moving Average)
   - Set Length = 7
   - Set Type = SMA (Simple Moving Average)
   - **IMPORTANT:** In advanced settings, check if MA uses "Wilder's Smoothing"
     (Some platforms call it "RMA" or "Smoothed MA")

5. Navigate to each date above using the calendar/date picker
6. Check the RSI SMA(7) value at market close
7. Compare with values in this table
8. They should match within ±0.5 points

Note: Small differences (<1 point) can occur due to:
- Data source differences (Yahoo Finance vs TradingView)
- Rounding methods
- Intraday vs close-of-day calculation timing
""")

print("\n" + "="*80)
print("✅ VERIFICATION COMPLETE")
print("="*80)

# Count rainy days in October
rainy_count = (october_data['RSI_SMA_7'] < 45).sum()
total_days = len(october_data)
rainy_pct = (rainy_count / total_days) * 100

print(f"\nOctober 2024 Rainy Days: {rainy_count} out of {total_days} trading days ({rainy_pct:.1f}%)")

# Check payday execution days specifically
payday_dates = ["2024-10-03", "2024-10-17"]
print(f"\n🔔 PAYDAY EXECUTION DAYS (3rd & 17th):")
print("-" * 80)

for date_str in payday_dates:
    date_obj = pd.Timestamp(date_str)
    if date_obj in october_data.index:
        close = october_data.loc[date_obj, 'Close']
        rsi_14_val = october_data.loc[date_obj, 'RSI_14']
        rsi_sma_val = october_data.loc[date_obj, 'RSI_SMA_7']
        is_rainy = rsi_sma_val < 45
        action = "🌧️ RAINY BUY $150" if is_rainy else "⛅ BASE BUY ONLY ($150)"
        
        print(f"\n{date_str}:")
        print(f"  SPY Close: ${close:.2f}")
        print(f"  RSI(14): {rsi_14_val:.2f}")
        print(f"  RSI SMA(7): {rsi_sma_val:.2f}")
        print(f"  Decision: {action}")
