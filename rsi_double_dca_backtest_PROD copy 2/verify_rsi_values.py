"""
Verify RSI SMA(7) values against actual market data
Compare our calculated values with fresh market data
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
    
    avg_gain.iloc[period] = gain.iloc[:period+1].mean()
    avg_loss.iloc[period] = loss.iloc[:period+1].mean()
    
    for i in range(period + 1, len(series)):
        avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period-1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period-1) + loss.iloc[i]) / period
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

print("Fetching SPY data from Yahoo Finance (TradingView's data source)...")
df = yf.download("SPY", start="2025-01-01", end="2025-11-23", interval="1d", progress=False)

print("Computing RSI(14) and RSI SMA(7) with Wilder's method...")
df['RSI_14'] = compute_rsi_wilder(df['Close'], period=14)
df['RSI_SMA_7'] = compute_rsi_wilder(df['RSI_14'], period=7)

# Dates from the verification list
dates_to_verify = [
    # November 2025
    ("2025-11-21", 40.02),
    ("2025-11-20", 38.72),
    ("2025-11-19", 37.72),
    ("2025-11-18", 38.92),
    ("2025-11-15", 39.75),
    ("2025-11-14", 40.35),
    ("2025-11-13", 41.18),
    ("2025-11-12", 42.32),
    ("2025-11-11", 43.54),
    ("2025-11-08", 44.48),
    ("2025-11-07", 45.30),
    ("2025-11-06", 46.38),
    ("2025-11-05", 47.86),
    
    # October 2025
    ("2025-10-17", 42.52),
    ("2025-10-15", 41.28),
    ("2025-10-13", 37.45),
    ("2025-10-10", 19.76),
    ("2025-10-03", 59.28),
    
    # September 2025
    ("2025-09-17", 56.83),
    ("2025-09-15", 55.42),
    ("2025-09-10", 53.16),
    ("2025-09-05", 51.28),
    ("2025-09-03", 49.85),
    
    # August 2025
    ("2025-08-29", 48.12),
    ("2025-08-25", 46.73),
    ("2025-08-20", 44.25),
    ("2025-08-18", 43.18),
    ("2025-08-15", 42.56),
    ("2025-08-08", 38.42),
    ("2025-08-05", 35.89),
    ("2025-08-01", 33.16),
    
    # April 2025
    ("2025-04-17", 44.28),
    ("2025-04-15", 43.85),
    ("2025-04-10", 42.16),
    ("2025-04-07", 40.83),
    ("2025-04-03", 41.33),
    
    # March 2025
    ("2025-03-17", 33.35),
    ("2025-03-14", 32.48),
    ("2025-03-10", 30.92),
    ("2025-03-07", 29.55),
    ("2025-03-03", 28.16),
]

print("\n" + "="*80)
print("RSI SMA(7) VERIFICATION - ACTUAL vs CALCULATED")
print("="*80)
print(f"{'Date':<14} {'Expected':<10} {'Actual':<10} {'Diff':<8} {'Match?':<10}")
print("-"*80)

matches = 0
total = 0

for date_str, expected_value in dates_to_verify:
    date = pd.Timestamp(date_str)
    
    if date in df.index:
        actual_value = float(df.loc[date, 'RSI_SMA_7'])
        
        if not np.isnan(actual_value):
            diff = abs(actual_value - expected_value)
            match = "✅ MATCH" if diff <= 1.0 else "❌ NO MATCH"
            
            if diff <= 1.0:
                matches += 1
            total += 1
            
            print(f"{date_str:<14} {expected_value:<10.2f} {actual_value:<10.2f} {diff:<8.2f} {match:<10}")
        else:
            print(f"{date_str:<14} {expected_value:<10.2f} {'N/A':<10} {'N/A':<8} {'⚠️ NO DATA':<10}")
    else:
        print(f"{date_str:<14} {expected_value:<10.2f} {'N/A':<10} {'N/A':<8} {'⚠️ NO DATA':<10}")

print("-"*80)
print(f"\nVERIFICATION SUMMARY:")
print(f"Matches: {matches}/{total} ({100*matches/total:.1f}%)")
print(f"Tolerance: ±1.0 point")
print("="*80)
