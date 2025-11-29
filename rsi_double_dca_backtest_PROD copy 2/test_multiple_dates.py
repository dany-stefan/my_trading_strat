"""
Test RSI(14) and RSI SMA(7) for multiple dates
Quick lookup tool for comparing with charts
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_rsi_for_dates(ticker="SPY", target_dates=None, period=14, lookback_days=100):
    """
    Get RSI(14) and RSI SMA(7) for specific dates.
    
    Args:
        ticker: Stock ticker (default SPY)
        target_dates: List of date strings in 'YYYY-MM-DD' format
        period: RSI period (default 14)
        lookback_days: Days of historical data to fetch
    
    Returns:
        DataFrame with date, price, RSI(14), and RSI SMA(7)
    """
    if target_dates is None:
        target_dates = []
    
    # Get latest date for end_date calculation
    latest_date = max([datetime.strptime(d, "%Y-%m-%d") for d in target_dates])
    end_date = latest_date + timedelta(days=1)
    start_date = latest_date - timedelta(days=lookback_days)
    
    # Fetch data
    print(f"Fetching {ticker} data from {start_date.date()} to {end_date.date()}...")
    df = yf.download(ticker, start=start_date, end=end_date, interval="1d", progress=False)
    
    if df.empty:
        print("❌ No data fetched")
        return None
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    close = df["Close"] if "Close" in df.columns else df["Adj Close"]
    
    # Calculate RSI using Wilder's smoothing (industry standard)
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    # Initialize arrays for Wilder's smoothing
    avg_gain = pd.Series(index=close.index, dtype=float)
    avg_loss = pd.Series(index=close.index, dtype=float)
    
    # First value: SMA
    avg_gain.iloc[period] = gain.iloc[1:period+1].mean()
    avg_loss.iloc[period] = loss.iloc[1:period+1].mean()
    
    # Subsequent values: Wilder's smoothing
    for i in range(period + 1, len(close)):
        avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period - 1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period - 1) + loss.iloc[i]) / period
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # Calculate SMA(7) of RSI
    rsi_sma = rsi.rolling(window=7).mean()
    
    # Create results DataFrame
    results = pd.DataFrame({
        'date': df.index,
        'close': close,
        'rsi': rsi,
        'rsi_sma': rsi_sma
    })
    
    # Filter for target dates
    results = results[results['date'].dt.strftime('%Y-%m-%d').isin(target_dates)]
    
    return results


if __name__ == "__main__":
    # Target dates to check
    test_dates = [
        "2025-10-31",  # October 31, 2025
        "2025-11-06",  # November 6, 2025
        "2025-11-14",  # November 14, 2025
    ]
    
    print("=" * 80)
    print("RSI(14) & RSI SMA(7) Test - Multiple Dates")
    print("=" * 80)
    print()
    
    results = get_rsi_for_dates("SPY", test_dates, period=14, lookback_days=120)
    
    if results is not None and len(results) > 0:
        print()
        print("=" * 80)
        print("RESULTS")
        print("=" * 80)
        print()
        print(f"{'Date':<12} {'Day':<10} {'SPY Price':<12} {'RSI(14)':<10} {'RSI SMA(7)':<12} {'Status'}")
        print("-" * 80)
        
        for _, row in results.iterrows():
            date_str = row['date'].strftime('%Y-%m-%d')
            day_str = row['date'].strftime('%A')
            price = row['close']
            rsi = row['rsi']
            rsi_sma = row['rsi_sma']
            
            # Determine status
            rsi_status = "RAINY" if rsi < 45 else "NOT RAINY"
            sma_status = "RAINY" if rsi_sma < 45 else "NOT RAINY"
            
            if rsi < 45 and rsi_sma < 45:
                status = "Both RAINY ✅"
            elif rsi < 45 and rsi_sma >= 45:
                status = "RSI only 📊"
            elif rsi >= 45 and rsi_sma < 45:
                status = "SMA only 📈"
            else:
                status = "Both clear ⛅"
            
            print(f"{date_str:<12} {day_str:<10} ${price:>9.2f}   {rsi:>7.2f}    {rsi_sma:>9.2f}     {status}")
        
        print()
        print("=" * 80)
        print("INTERPRETATION")
        print("=" * 80)
        print()
        
        for _, row in results.iterrows():
            date_str = row['date'].strftime('%Y-%m-%d')
            rsi = row['rsi']
            rsi_sma = row['rsi_sma']
            diff = rsi - rsi_sma
            
            print(f"{date_str}:")
            print(f"  RSI(14):     {rsi:.2f} {'< 45 (RAINY)' if rsi < 45 else '>= 45 (NOT RAINY)'}")
            print(f"  RSI SMA(7):  {rsi_sma:.2f} {'< 45 (RAINY)' if rsi_sma < 45 else '>= 45 (NOT RAINY)'}")
            print(f"  Difference:  RSI - SMA = {diff:+.2f}")
            
            if diff < 0:
                print(f"  → RSI below its SMA (potentially weakening momentum)")
            elif diff > 0:
                print(f"  → RSI above its SMA (potentially strengthening momentum)")
            else:
                print(f"  → RSI equals its SMA")
            
            # Agreement analysis
            if (rsi < 45 and rsi_sma < 45) or (rsi >= 45 and rsi_sma >= 45):
                print(f"  ✅ Agreement: Both indicators say same thing")
            else:
                print(f"  ⚠️  Disagreement: Indicators give different signals")
            print()
        
    else:
        print("❌ No data available for the requested dates")
        print("Note: Market may be closed on these dates (weekends/holidays)")
