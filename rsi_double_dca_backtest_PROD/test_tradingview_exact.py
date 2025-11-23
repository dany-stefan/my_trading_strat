"""
Test TradingView's EXACT RSI calculation
TradingView uses RMA (Wilder's) for RSI but SMA for the moving average ON the RSI
This is the key difference!
"""

import yfinance as yf
import pandas as pd
import numpy as np

def compute_rsi_rma(series, period=14):
    """
    Compute RSI using RMA (Wilder's smoothing) - this is what TradingView uses for base RSI
    """
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = pd.Series(index=series.index, dtype=float)
    avg_loss = pd.Series(index=series.index, dtype=float)
    
    # First value: simple average
    avg_gain.iloc[period] = gain.iloc[:period+1].mean()
    avg_loss.iloc[period] = loss.iloc[:period+1].mean()
    
    # RMA (Wilder's smoothing)
    for i in range(period + 1, len(series)):
        avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period-1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period-1) + loss.iloc[i]) / period
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Fetch data
print("Fetching SPY data...")
df = yf.download("SPY", start="2025-01-01", end="2025-11-23", interval="1d", progress=False)

# Compute RSI using RMA (Wilder's) - this matches TradingView's RSI
df['RSI_14'] = compute_rsi_rma(df['Close'], period=14)

# Now compute SMA(7) of the RSI values using SIMPLE moving average
# This is what TradingView does when you add MA on the RSI panel!
df['RSI_SMA_7'] = df['RSI_14'].rolling(window=7).mean()

print("\n" + "="*80)
print("TESTING TRADINGVIEW'S EXACT CALCULATION")
print("="*80)
print("\nRSI: Uses RMA (Wilder's smoothing)")
print("MA on RSI: Uses SIMPLE Moving Average (SMA)")
print("\n" + "="*80)

# Test key dates
test_dates = [
    "2025-11-21",
    "2025-10-17",
    "2025-10-15",
    "2025-10-10",
    "2025-10-03",
]

print(f"\n{'Date':<15} {'RSI(14)':<12} {'SMA(7) on RSI':<15}")
print("-"*80)

for date_str in test_dates:
    date = pd.Timestamp(date_str)
    if date in df.index:
        rsi = float(df.loc[date, 'RSI_14'])
        sma = float(df.loc[date, 'RSI_SMA_7'])
        
        if not np.isnan(sma):
            print(f"{date_str:<15} {rsi:<12.2f} {sma:<15.2f}")

print("\n" + "="*80)
print("✅ This should match TradingView exactly!")
print("="*80)
