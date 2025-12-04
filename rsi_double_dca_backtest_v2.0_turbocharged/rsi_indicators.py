"""
RSI Indicators Module - SINGLE SOURCE OF TRUTH
==============================================

This module contains the canonical RSI calculation logic used across all scripts.
DO NOT duplicate this logic - always import from this module to ensure consistency.

Used by:
- rsi_calendar_date_backtest.py (main backtest)
- monitor_strategy.py (live monitoring)
- update_rsi_verification.py (RSI verification list)
- simulate_payday_email.py (email simulation)
- All other scripts that need RSI calculations

RSI Calculation Method: Wilder's Smoothing (industry standard, matches TradingView)
"""

import pandas as pd


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate RSI using Wilder's smoothing method (industry standard).
    This matches TradingView and other platforms.
    
    Wilder's smoothing formula:
    - First avg: Simple Moving Average over initial period
    - Next avg: (Previous avg * (period-1) + Current value) / period
    
    Args:
        series: Price series (Close or Adj Close)
        period: RSI period (default 14)
    
    Returns:
        pd.Series: RSI values
    """
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    # Initialize arrays
    avg_gain = pd.Series(index=series.index, dtype=float)
    avg_loss = pd.Series(index=series.index, dtype=float)
    
    # First value: SMA over initial period
    avg_gain.iloc[period] = gain.iloc[1:period+1].mean()
    avg_loss.iloc[period] = loss.iloc[1:period+1].mean()
    
    # Subsequent values: Wilder's smoothing
    for i in range(period + 1, len(series)):
        avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period - 1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period - 1) + loss.iloc[i]) / period
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def compute_rsi_sma(rsi_series: pd.Series, period: int = 7) -> pd.Series:
    """
    Calculate Simple Moving Average of RSI values.
    
    Args:
        rsi_series: RSI values
        period: SMA period (default 7)
    
    Returns:
        pd.Series: RSI SMA values
    """
    return rsi_series.rolling(window=period).mean()


def compute_rsi_with_sma(price_series: pd.Series, rsi_period: int = 14, sma_period: int = 7) -> tuple[pd.Series, pd.Series]:
    """
    Calculate both RSI and RSI SMA in one call.
    
    Args:
        price_series: Price series (Close or Adj Close)
        rsi_period: RSI period (default 14)
        sma_period: RSI SMA period (default 7)
    
    Returns:
        tuple: (rsi_series, rsi_sma_series)
    """
    rsi = compute_rsi(price_series, rsi_period)
    rsi_sma = compute_rsi_sma(rsi, sma_period)
    return rsi, rsi_sma
