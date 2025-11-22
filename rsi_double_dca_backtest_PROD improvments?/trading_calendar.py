"""
Trading Calendar Module
========================

Provides market calendar functionality for TSX (Toronto Stock Exchange).
This module uses a strategy pattern to allow different calendar implementations.

Usage:
    from trading_calendar import get_calendar
    
    calendar = get_calendar('TSX')
    if calendar.is_trading_day(datetime.now()):
        print("Market is open!")
"""

from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from typing import List, Tuple


class TradingCalendar(ABC):
    """Abstract base class for trading calendar implementations."""
    
    @abstractmethod
    def is_trading_day(self, date: datetime) -> bool:
        """Check if given date is a trading day."""
        pass
    
    @abstractmethod
    def is_holiday(self, date: datetime) -> bool:
        """Check if given date is a market holiday."""
        pass
    
    def is_weekend(self, date: datetime) -> bool:
        """Check if given date falls on a weekend."""
        weekday = date.weekday()  # 0=Monday, 6=Sunday
        return weekday >= 5  # Saturday=5, Sunday=6
    
    def get_next_trading_day(self, date: datetime) -> datetime:
        """Get the next trading day after given date."""
        next_day = date + timedelta(days=1)
        while not self.is_trading_day(next_day):
            next_day = next_day + timedelta(days=1)
        return next_day
    
    def get_previous_trading_day(self, date: datetime) -> datetime:
        """Get the previous trading day before given date."""
        prev_day = date - timedelta(days=1)
        while not self.is_trading_day(prev_day):
            prev_day = prev_day - timedelta(days=1)
        return prev_day


class TSXCalendar(TradingCalendar):
    """Toronto Stock Exchange (TSX) trading calendar."""
    
    # Static holidays (month, day) - these are fixed dates
    STATIC_HOLIDAYS: List[Tuple[int, int]] = [
        (1, 1),   # New Year's Day
        (7, 1),   # Canada Day
        (12, 25), # Christmas Day
        (12, 26), # Boxing Day
    ]
    
    # Note: TSX also closed for Good Friday, Victoria Day, Civic Holiday,
    # Labour Day, Thanksgiving. For production, consider pandas_market_calendars.
    
    def is_holiday(self, date: datetime) -> bool:
        """Check if date is a TSX statutory holiday (static dates only)."""
        return (date.month, date.day) in self.STATIC_HOLIDAYS
    
    def is_trading_day(self, date: datetime) -> bool:
        """Check if date is a TSX trading day (not weekend or holiday)."""
        return not self.is_weekend(date) and not self.is_holiday(date)


class NYSECalendar(TradingCalendar):
    """New York Stock Exchange (NYSE) trading calendar."""
    
    # Static holidays (month, day)
    STATIC_HOLIDAYS: List[Tuple[int, int]] = [
        (1, 1),   # New Year's Day
        (7, 4),   # Independence Day
        (12, 25), # Christmas Day
    ]
    
    def is_holiday(self, date: datetime) -> bool:
        """Check if date is an NYSE holiday (static dates only)."""
        return (date.month, date.day) in self.STATIC_HOLIDAYS
    
    def is_trading_day(self, date: datetime) -> bool:
        """Check if date is an NYSE trading day (not weekend or holiday)."""
        return not self.is_weekend(date) and not self.is_holiday(date)


# Calendar factory (Singleton pattern)
_calendars = {
    'TSX': TSXCalendar(),
    'NYSE': NYSECalendar(),
}


def get_calendar(exchange: str = 'TSX') -> TradingCalendar:
    """
    Get a trading calendar instance for the specified exchange.
    
    Args:
        exchange: Exchange name ('TSX' or 'NYSE')
    
    Returns:
        TradingCalendar instance
    
    Raises:
        ValueError: If exchange is not supported
    
    Example:
        >>> calendar = get_calendar('TSX')
        >>> calendar.is_trading_day(datetime(2025, 1, 1))
        False  # New Year's Day
    """
    if exchange not in _calendars:
        raise ValueError(f"Unsupported exchange: {exchange}. Supported: {list(_calendars.keys())}")
    return _calendars[exchange]


def register_calendar(exchange: str, calendar: TradingCalendar) -> None:
    """
    Register a custom trading calendar.
    
    Args:
        exchange: Exchange name identifier
        calendar: TradingCalendar instance
    
    Example:
        >>> class CustomCalendar(TradingCalendar):
        ...     def is_trading_day(self, date): return True
        ...     def is_holiday(self, date): return False
        >>> register_calendar('CUSTOM', CustomCalendar())
    """
    _calendars[exchange] = calendar
