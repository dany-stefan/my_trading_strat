"""
Test script to get RSI and RSI SMA(7) value for November 14, 2025
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_rsi_for_date(ticker="SPY", target_date="2025-11-14", period=14, lookback_days=100):
    """Get RSI and RSI EMA for a specific date."""
    
    target = datetime.strptime(target_date, "%Y-%m-%d")
    end_date = target + timedelta(days=1)  # Include the target date
    start_date = end_date - timedelta(days=lookback_days)
    
    print(f"Fetching data from {start_date.date()} to {end_date.date()}...")
    
    try:
        df = yf.download(ticker, start=start_date, end=end_date, interval="1d", progress=False)
        if df.empty:
            print("❌ No data fetched")
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
        
        # Calculate SMA(7) of RSI
        rsi_ema = rsi.rolling(window=7).mean()
        
        # Get values for target date
        target_str = target.strftime("%Y-%m-%d")
        
        # Find the closest date (in case target_date was a weekend)
        available_dates = [d.strftime("%Y-%m-%d") for d in df.index]
        
        if target_str in available_dates:
            idx = df.index[df.index == target]
            rsi_value = rsi.loc[idx].iloc[0]
            rsi_ema_value = rsi_ema.loc[idx].iloc[0]
            price_value = close.loc[idx].iloc[0]
            actual_date = target_str
        else:
            # Find nearest date
            print(f"⚠️  {target_str} not in data (likely weekend). Finding nearest trading day...")
            nearest_idx = df.index[df.index >= target].min()
            if pd.isna(nearest_idx):
                nearest_idx = df.index[-1]
            
            actual_date = nearest_idx.strftime("%Y-%m-%d")
            rsi_value = rsi.loc[nearest_idx]
            rsi_ema_value = rsi_ema.loc[nearest_idx]
            price_value = close.loc[nearest_idx]
        
        return actual_date, rsi_value, rsi_ema_value, price_value
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None, None, None


if __name__ == "__main__":
    print("=" * 80)
    print("RSI & RSI SMA(7) Test for November 14, 2025")
    print("=" * 80)
    print()
    
    actual_date, rsi, rsi_ema, price = get_rsi_for_date("SPY", "2025-11-14", period=14)
    
    if rsi is not None:
        print(f"✅ Date: {actual_date}")
        print(f"✅ SPY Price: ${price:.2f}")
        print(f"✅ RSI(14): {rsi:.2f}")
        print(f"✅ RSI SMA(7): {rsi_ema:.2f}")
        print()
        print("=" * 80)
        print("INTERPRETATION:")
        print("=" * 80)
        
        if rsi < 45:
            print(f"🌧️  RAINY DAY: RSI({rsi:.2f}) < 45")
        else:
            print(f"☀️  NOT RAINY: RSI({rsi:.2f}) >= 45")
        
        if rsi_ema < 45:
            print(f"🌧️  RSI SMA RAINY: RSI SMA({rsi_ema:.2f}) < 45")
        else:
            print(f"☀️  RSI SMA NOT RAINY: RSI SMA({rsi_ema:.2f}) >= 45")
            
        print()
        print(f"Difference: RSI - RSI SMA = {rsi - rsi_ema:.2f}")
        
        if rsi < rsi_ema:
            print("📉 RSI is below its SMA (potentially weakening momentum)")
        else:
            print("📈 RSI is above its SMA (potentially strengthening momentum)")
    else:
        print("❌ Failed to get data")
