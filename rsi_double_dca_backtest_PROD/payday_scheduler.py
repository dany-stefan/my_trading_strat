"""
Payday Scheduler Module
========================

Provides payday scheduling logic with trading calendar integration.
Uses strategy pattern for flexible payday calculation.

Usage:
    from payday_scheduler import get_scheduler
    
    scheduler = get_scheduler('BIWEEKLY_TSX', days=[3, 17])
    if scheduler.is_payday(datetime.now()):
        print("It's payday!")
"""

from datetime import datetime
from abc import ABC, abstractmethod
from typing import List, Optional
from trading_calendar import get_calendar, TradingCalendar


class PaydayScheduler(ABC):
    """Abstract base class for payday scheduling strategies."""
    
    def __init__(self, calendar: Optional[TradingCalendar] = None):
        """
        Initialize scheduler with optional trading calendar.
        
        Args:
            calendar: TradingCalendar instance for trading day validation
        """
        self.calendar = calendar
    
    @abstractmethod
    def is_payday(self, date: Optional[datetime] = None) -> bool:
        """Check if given date (or today) is a payday."""
        pass
    
    @abstractmethod
    def get_next_payday(self, date: Optional[datetime] = None) -> datetime:
        """Get the next payday after given date."""
        pass


class BiweeklyScheduler(PaydayScheduler):
    """
    Biweekly payday scheduler with trading calendar support.
    
    Supports configurable day-of-month scheduling with automatic
    rollover to next trading day when payday falls on non-trading day.
    """
    
    def __init__(
        self, 
        payday_days: List[int], 
        calendar: Optional[TradingCalendar] = None
    ):
        """
        Initialize biweekly scheduler.
        
        Args:
            payday_days: List of day-of-month for paydays (e.g., [3, 17])
            calendar: Optional TradingCalendar for trading day validation.
                     If None, any day is considered valid.
        
        Example:
            >>> scheduler = BiweeklyScheduler([3, 17], get_calendar('TSX'))
            >>> scheduler.is_payday(datetime(2025, 12, 3))
            True
        """
        super().__init__(calendar)
        self.payday_days = sorted(payday_days)
    
    def _should_rollover(self, date: datetime) -> bool:
        """Check if date should rollover to next trading day."""
        if self.calendar is None:
            return False
        return not self.calendar.is_trading_day(date)
    
    def _get_actual_payday(self, target_date: datetime) -> datetime:
        """
        Get actual payday date, accounting for trading calendar rollover.
        
        Args:
            target_date: The target payday date (e.g., 3rd or 17th)
        
        Returns:
            Actual payday date (may be rolled forward to next trading day)
        """
        if self._should_rollover(target_date):
            return self.calendar.get_next_trading_day(target_date)
        return target_date
    
    def is_payday(self, date: Optional[datetime] = None) -> bool:
        """
        Check if given date (or today) is a payday.
        
        Logic:
        1. If date is exactly a scheduled payday AND trading day → True
        2. If scheduled payday was non-trading day and date is the
           next trading day after it → True
        3. Otherwise → False
        
        Args:
            date: Date to check (defaults to today)
        
        Returns:
            True if date is a payday
        """
        if date is None:
            date = datetime.now()
        
        day = date.day
        
        # Check if today is exactly a scheduled payday day
        if day in self.payday_days:
            # If no calendar, or if it's a trading day, it's payday
            if self.calendar is None or self.calendar.is_trading_day(date):
                return True
        
        # Check if any scheduled payday in this month rolled over to today
        for payday_day in self.payday_days:
            try:
                target_payday = date.replace(day=payday_day)
                actual_payday = self._get_actual_payday(target_payday)
                
                # Compare dates (not datetimes) for match
                if date.date() == actual_payday.date():
                    return True
            except ValueError:
                # Invalid day for this month (e.g., Feb 30)
                continue
        
        return False
    
    def get_next_payday(self, date: Optional[datetime] = None) -> datetime:
        """
        Get the next payday after given date.
        
        Args:
            date: Reference date (defaults to today)
        
        Returns:
            Next payday date
        """
        if date is None:
            date = datetime.now()
        
        # Find next scheduled payday in current month
        for payday_day in self.payday_days:
            if payday_day > date.day:
                try:
                    target = date.replace(day=payday_day)
                    return self._get_actual_payday(target)
                except ValueError:
                    continue
        
        # No more paydays this month, go to first payday of next month
        next_month = date.replace(day=1)
        if date.month == 12:
            next_month = next_month.replace(year=date.year + 1, month=1)
        else:
            next_month = next_month.replace(month=date.month + 1)
        
        target = next_month.replace(day=self.payday_days[0])
        return self._get_actual_payday(target)


# Scheduler factory
_schedulers = {}


def get_scheduler(
    scheduler_type: str = 'BIWEEKLY_TSX',
    days: Optional[List[int]] = None,
    exchange: str = 'TSX'
) -> PaydayScheduler:
    """
    Get a payday scheduler instance.
    
    Args:
        scheduler_type: Type of scheduler ('BIWEEKLY_TSX', 'BIWEEKLY_NYSE', 'BIWEEKLY_NONE')
        days: List of payday days (defaults to [3, 17])
        exchange: Exchange for calendar lookup (default: 'TSX')
    
    Returns:
        PaydayScheduler instance
    
    Example:
        >>> scheduler = get_scheduler('BIWEEKLY_TSX', days=[1, 15])
        >>> scheduler.is_payday(datetime(2025, 12, 1))
    """
    if days is None:
        days = [3, 17]  # Default biweekly schedule
    
    key = f"{scheduler_type}_{tuple(days)}_{exchange}"
    
    if key not in _schedulers:
        if scheduler_type == 'BIWEEKLY_NONE':
            # No calendar validation
            _schedulers[key] = BiweeklyScheduler(days, calendar=None)
        elif scheduler_type.startswith('BIWEEKLY_'):
            # With calendar validation
            calendar = get_calendar(exchange)
            _schedulers[key] = BiweeklyScheduler(days, calendar=calendar)
        else:
            raise ValueError(f"Unsupported scheduler type: {scheduler_type}")
    
    return _schedulers[key]


def register_scheduler(name: str, scheduler: PaydayScheduler) -> None:
    """Register a custom payday scheduler."""
    _schedulers[name] = scheduler
