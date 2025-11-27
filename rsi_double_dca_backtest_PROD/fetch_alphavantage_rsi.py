"""
Alpha Vantage RSI Fetcher
=========================

Fetches RSI data from Alpha Vantage API for external verification.
This provides an independent source to compare against local yfinance calculations.

API Key: Store in ALPHAVANTAGE_API_KEY environment variable
Free tier: 25 requests/day, 5 requests/minute
"""

import requests
import os
from datetime import datetime
import time
import pandas as pd


def fetch_alphavantage_rsi(symbol='SPY', api_key=None):
    """
    Fetch RSI(14) data from Alpha Vantage API.
    
    Args:
        symbol: Stock symbol (default: SPY)
        api_key: Alpha Vantage API key (or use ALPHAVANTAGE_API_KEY env var)
    
    Returns:
        dict: {date: rsi_value} or None if error
    """
    if api_key is None:
        api_key = os.getenv('ALPHAVANTAGE_API_KEY')
    
    if not api_key:
        print("❌ No API key provided. Set ALPHAVANTAGE_API_KEY environment variable")
        print("   or pass api_key parameter.")
        print("   Get free key at: https://www.alphavantage.co/support/#api-key")
        return None
    
    url = f'https://www.alphavantage.co/query'
    params = {
        'function': 'RSI',
        'symbol': symbol,
        'interval': 'daily',
        'time_period': 14,
        'series_type': 'close',
        'apikey': api_key
    }
    
    print(f"📡 Fetching RSI data from Alpha Vantage for {symbol}...")
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Check for API errors
        if 'Error Message' in data:
            print(f"❌ API Error: {data['Error Message']}")
            return None
        
        if 'Note' in data:
            print(f"⚠️  API Limit: {data['Note']}")
            return None
        
        if 'Information' in data:
            print(f"ℹ️  {data['Information']}")
            return None
        
        # Extract RSI data
        if 'Technical Analysis: RSI' not in data:
            print(f"❌ Unexpected response format: {list(data.keys())}")
            return None
        
        rsi_data = data['Technical Analysis: RSI']
        
        # Convert to {date: rsi_value} format, but only keep the most recent 7 days
        result = {}
        # Sort dates descending (most recent first)
        sorted_dates = sorted(rsi_data.keys(), reverse=True)
        for date_str in sorted_dates[:7]:
            result[date_str] = float(rsi_data[date_str]['RSI'])

        print(f"✅ Fetched {len(result)} days of RSI data (most recent 7 days only)")
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def get_rsi_for_date(date_str, api_key=None):
    """
    Get RSI value for a specific date from Alpha Vantage.
    
    Args:
        date_str: Date in YYYY-MM-DD format
        api_key: Alpha Vantage API key
    
    Returns:
        float: RSI value or None if not available
    """
    rsi_data = fetch_alphavantage_rsi(api_key=api_key)
    
    if rsi_data is None:
        return None
    
    return rsi_data.get(date_str)


def calculate_rsi_sma(rsi_data, sma_period=7):
    """
    Calculate Simple Moving Average of RSI values.
    
    Args:
        rsi_data: dict of {date: rsi_value}
        sma_period: SMA period (default 7)
    
    Returns:
        dict: {date: rsi_sma_value}
    """
    # Convert to DataFrame for easier calculation
    df = pd.DataFrame.from_dict(rsi_data, orient='index', columns=['RSI'])
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    
    # Calculate SMA
    df['RSI_SMA'] = df['RSI'].rolling(window=sma_period, min_periods=sma_period).mean()
    
    # Convert back to dict
    result = {}
    for date, row in df.iterrows():
        if pd.notna(row['RSI_SMA']):
            result[date.strftime('%Y-%m-%d')] = row['RSI_SMA']
    
    return result


def get_rsi_and_sma_for_date(date_str, api_key=None, sma_period=7):
    """
    Get both RSI and RSI SMA for a specific date from Alpha Vantage.
    
    Args:
        date_str: Date in YYYY-MM-DD format
        api_key: Alpha Vantage API key
        sma_period: SMA period (default 7)
    
    Returns:
        tuple: (rsi, rsi_sma) or (None, None) if not available
    """
    rsi_data = fetch_alphavantage_rsi(api_key=api_key)
    
    if rsi_data is None:
        return None, None
    
    # Calculate SMA
    sma_data = calculate_rsi_sma(rsi_data, sma_period=sma_period)
    
    rsi = rsi_data.get(date_str)
    sma = sma_data.get(date_str)
    
    return rsi, sma


if __name__ == "__main__":
    # Test the API
    print("═" * 75)
    print("ALPHA VANTAGE RSI FETCHER - TEST")
    print("═" * 75)
    print()
    
    # Check for API key
    api_key = os.getenv('ALPHAVANTAGE_API_KEY')
    if not api_key:
        print("⚠️  No ALPHAVANTAGE_API_KEY environment variable found")
        print()
        print("To set it:")
        print("  export ALPHAVANTAGE_API_KEY='your_key_here'")
        print()
        print("Get your free API key at:")
        print("  https://www.alphavantage.co/support/#api-key")
        print()
    else:
        print(f"✅ API Key found: {api_key[:8]}...")
        print()
        
        # Fetch data
        rsi_data = fetch_alphavantage_rsi()
        
        if rsi_data:
            print()
            print("Sample RSI values (last 10 days):")
            print("-" * 75)
            for date_str in sorted(rsi_data.keys(), reverse=True)[:10]:
                print(f"  {date_str}: RSI = {rsi_data[date_str]:.2f}")
            
            # Calculate and show SMA
            print()
            print("Calculating RSI SMA(7)...")
            sma_data = calculate_rsi_sma(rsi_data, sma_period=7)
            print(f"✅ Calculated SMA for {len(sma_data)} days")
            print()
            print("Sample RSI + SMA values (last 10 days):")
            print("-" * 75)
            for date_str in sorted(sma_data.keys(), reverse=True)[:10]:
                rsi = rsi_data.get(date_str)
                sma = sma_data.get(date_str)
                if rsi and sma:
                    print(f"  {date_str}: RSI = {rsi:5.2f}, SMA = {sma:5.2f}")
    
    print()
    print("═" * 75)
