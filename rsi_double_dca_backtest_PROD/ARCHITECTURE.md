# Modular Architecture Guide

## Overview

The codebase uses **object-oriented design** with **polymorphism** and the **strategy pattern** to ensure maintainability and flexibility. Changing configuration in one place automatically propagates throughout the entire system.

## Core Design Principles

### 1. **Single Responsibility Principle**
Each module has one clear purpose:
- `trading_calendar.py` - Market calendar logic
- `payday_scheduler.py` - Payday scheduling logic  
- `monitor_strategy.py` - Production monitoring
- `email_generator.py` - Email content generation
- `email_formatter.py` - HTML formatting

### 2. **Polymorphism via Abstract Base Classes**
```python
# Base class defines interface
class TradingCalendar(ABC):
    @abstractmethod
    def is_trading_day(self, date: datetime) -> bool:
        pass

# Concrete implementations
class TSXCalendar(TradingCalendar):
    # TSX-specific logic
    
class NYSECalendar(TradingCalendar):
    # NYSE-specific logic
```

### 3. **Strategy Pattern for Flexibility**
The scheduler can be swapped without changing calling code:
```python
# In monitor_strategy.py - configuration section
SCHEDULER_TYPE = 'BIWEEKLY_TSX'  # Change this one line
payday_scheduler = get_scheduler(SCHEDULER_TYPE, days=[3, 17])

# Everywhere else in the code - no changes needed!
if is_payday():  # This delegates to the scheduler
    send_email()
```

## Module Architecture

### Trading Calendar Module (`trading_calendar.py`)

**Purpose:** Provide market calendar functionality

**Classes:**
- `TradingCalendar` (ABC) - Abstract base class
- `TSXCalendar` - Toronto Stock Exchange calendar
- `NYSECalendar` - New York Stock Exchange calendar

**Key Methods:**
```python
calendar = get_calendar('TSX')
calendar.is_trading_day(date)  # True if market open
calendar.is_holiday(date)  # True if holiday
calendar.get_next_trading_day(date)  # Next open day
```

**Extensibility:**
```python
# Add a new exchange
class LSECalendar(TradingCalendar):
    def is_trading_day(self, date):
        # London Stock Exchange logic
        pass

register_calendar('LSE', LSECalendar())
```

### Payday Scheduler Module (`payday_scheduler.py`)

**Purpose:** Determine payday dates with calendar awareness

**Classes:**
- `PaydayScheduler` (ABC) - Abstract base class
- `BiweeklyScheduler` - Biweekly payday implementation

**Key Methods:**
```python
scheduler = get_scheduler('BIWEEKLY_TSX', days=[3, 17])
scheduler.is_payday(date)  # True if payday
scheduler.get_next_payday(date)  # Next payday date
```

**Configuration Examples:**
```python
# TSX calendar validation (current production)
scheduler = get_scheduler('BIWEEKLY_TSX', days=[3, 17], exchange='TSX')

# NYSE calendar validation
scheduler = get_scheduler('BIWEEKLY_NYSE', days=[1, 15], exchange='NYSE')

# No calendar validation (any day valid)
scheduler = get_scheduler('BIWEEKLY_NONE', days=[1, 15])
```

## How Changes Propagate

### Example: Switch from TSX to NYSE Calendar

**Only change this in `monitor_strategy.py`:**
```python
# Before (TSX)
TRADING_EXCHANGE = 'TSX'

# After (NYSE)
TRADING_EXCHANGE = 'NYSE'
```

**Everything else stays the same:**
- `is_payday()` function - no changes needed
- All calling code - no changes needed
- Email logic - no changes needed
- Tracking logic - no changes needed

The `payday_scheduler` automatically uses the new calendar!

### Example: Change Payday Dates

**Only change this in `monitor_strategy.py`:**
```python
# Before (3rd and 17th)
PAYDAY_DAYS = [3, 17]

# After (1st and 15th)
PAYDAY_DAYS = [1, 15]
```

**Everything else stays the same:**
- All payday detection logic updates automatically
- No other code changes required

### Example: Disable Calendar Validation

**Only change this in `monitor_strategy.py`:**
```python
# Before (TSX validation)
SCHEDULER_TYPE = 'BIWEEKLY_TSX'

# After (no validation)
SCHEDULER_TYPE = 'BIWEEKLY_NONE'
```

Now paydays work on weekends and holidays (for testing/special scenarios).

## Dependency Flow

```
monitor_strategy.py (main)
    ↓
    ├── payday_scheduler.py (uses)
    │       ↓
    │       └── trading_calendar.py (uses)
    │
    ├── email_generator.py (uses)
    │
    └── email_formatter.py (uses)

simulate_payday_email.py (preview)
    ↓
    └── [same dependencies as monitor_strategy.py]
```

## Benefits of This Architecture

### 1. **Maintainability**
- Each module has clear responsibility
- Changes are isolated to relevant modules
- Easy to locate and fix bugs

### 2. **Testability**
```python
# Easy to test individual components
def test_tsx_calendar():
    calendar = get_calendar('TSX')
    assert calendar.is_trading_day(datetime(2025, 12, 25)) == False  # Christmas
    
def test_payday_scheduler():
    scheduler = get_scheduler('BIWEEKLY_TSX', days=[3, 17])
    assert scheduler.is_payday(datetime(2025, 12, 3))
```

### 3. **Extensibility**
Adding new exchanges or scheduling strategies is straightforward:

```python
# Add German exchange
class XETRACalendar(TradingCalendar):
    STATIC_HOLIDAYS = [(1, 1), (10, 3), (12, 25), (12, 26)]
    def is_trading_day(self, date):
        return not self.is_weekend(date) and not self.is_holiday(date)
    def is_holiday(self, date):
        return (date.month, date.day) in self.STATIC_HOLIDAYS

register_calendar('XETRA', XETRACalendar())
```

### 4. **Reusability**
The calendar and scheduler modules can be used in:
- `monitor_strategy.py` (production)
- `simulate_payday_email.py` (preview)
- Backtest scripts
- Analysis tools
- Future applications

### 5. **Consistency**
Both production and simulation use **identical** payday logic:
```python
# Both files use the same configuration
PAYDAY_DAYS = [3, 17]
TRADING_EXCHANGE = 'TSX'
SCHEDULER_TYPE = 'BIWEEKLY_TSX'

payday_scheduler = get_scheduler(
    scheduler_type=SCHEDULER_TYPE,
    days=PAYDAY_DAYS,
    exchange=TRADING_EXCHANGE
)
```

No risk of logic drift between preview and production!

## Configuration Management

### Centralized Configuration Pattern

All configuration happens at the **top of each file**:

```python
# monitor_strategy.py
# =============================================================================
# CONFIGURATION
# =============================================================================

# Payday configuration - change these values to modify behavior
PAYDAY_DAYS = [3, 17]  # 3rd and 17th of each month
TRADING_EXCHANGE = 'TSX'  # Toronto Stock Exchange
SCHEDULER_TYPE = 'BIWEEKLY_TSX'  # Biweekly with TSX calendar validation

# Initialize scheduler (all logic delegated here)
payday_scheduler = get_scheduler(
    scheduler_type=SCHEDULER_TYPE,
    days=PAYDAY_DAYS,
    exchange=TRADING_EXCHANGE
)
```

### Wrapper Functions for Backward Compatibility

```python
def is_payday(date=None):
    """
    Check if given date (or today) is a payday.
    
    This is a wrapper around the modular payday_scheduler.
    All payday logic is delegated to the scheduler instance,
    which handles TSX calendar validation polymorphically.
    
    To change payday behavior, modify the scheduler configuration
    at the top of this file. No changes needed here.
    """
    return payday_scheduler.is_payday(date)
```

This ensures:
- Existing code continues to work (`is_payday()` still exists)
- All logic flows through the modular system
- Configuration changes propagate automatically

## Future Enhancements

### 1. Add Dynamic Holiday Support
```python
class TSXCalendar(TradingCalendar):
    def get_good_friday(self, year):
        # Calculate Good Friday for given year
        pass
    
    def is_holiday(self, date):
        if (date.month, date.day) in self.STATIC_HOLIDAYS:
            return True
        # Check dynamic holidays
        good_friday = self.get_good_friday(date.year)
        return date.date() == good_friday.date()
```

### 2. Add Different Scheduling Patterns
```python
class MonthlyScheduler(PaydayScheduler):
    """Monthly payday on last business day of month."""
    def is_payday(self, date):
        # Last trading day of month logic
        pass

# Use it
scheduler = get_scheduler('MONTHLY_TSX')
```

### 3. Add Market Hours Support
```python
class TradingCalendar(ABC):
    @abstractmethod
    def get_trading_hours(self, date):
        """Return (open_time, close_time) for date."""
        pass
```

## Summary

✅ **Modular** - Clear separation of concerns
✅ **Polymorphic** - Swap implementations via configuration
✅ **Maintainable** - Change one place, affect entire system
✅ **Testable** - Each component can be tested independently
✅ **Extensible** - Easy to add new calendars or schedules
✅ **Consistent** - Same logic across all scripts

**Key Principle:** Change configuration, not code. The system adapts automatically.
