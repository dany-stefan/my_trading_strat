"""
Generate RSI Timeline Chart with Rainy Day Markers
===================================================

Creates a dual-panel chart showing:
1. RSI SMA(7) over time with rainy day threshold and buy markers
2. SPY price over time with rainy day buy markers

Similar to Chart 4 in the copy folder backtest.
"""

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from trading_calendar import get_calendar
from strategy_config import get_strategy_config

# =============================================================================
# PARAMETERS
# =============================================================================
START_DATE = "2003-10-17"
END_DATE = datetime.now().strftime("%Y-%m-%d")
INDEX_TICKER = "SPY"
FX_TICKER = "CADUSD=X"
EXECUTION_DAYS = [3, 17]

# Strategy config
variant_config = get_strategy_config('VARIANT_2')
RSI_THRESHOLD = variant_config.rsi_threshold
RSI_PERIOD = variant_config.rsi_period
RSI_SMA_PERIOD = variant_config.rsi_sma_period
RAINY_AMOUNT = variant_config.rainy_extra_amount
CASH_ACCUMULATION = variant_config.cash_accumulation_per_payday
INITIAL_CASH_POOL = variant_config.initial_cash_pool

# Get TSX calendar
tsx_calendar = get_calendar('TSX')

# =============================================================================
# DATA FETCH
# =============================================================================
print("=" * 80)
print("RSI TIMELINE CHART GENERATOR")
print("=" * 80)
print(f"\nFetching data from {START_DATE} to {END_DATE}...")

def fetch_series(ticker: str, start: str, end: str) -> pd.Series:
    """Fetch price series from Yahoo Finance."""
    try:
        df = yf.download(ticker, start=start, end=end, interval="1d", progress=False)
        if df.empty:
            print(f"Warning: Empty data for {ticker}")
            return pd.Series(dtype=float)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        col = "Adj Close" if "Adj Close" in df.columns else "Close"
        s = df[col].copy()
        s.name = ticker
        return s
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return pd.Series(dtype=float)

spy = fetch_series(INDEX_TICKER, START_DATE, END_DATE)
fx = fetch_series(FX_TICKER, START_DATE, END_DATE)

prices = pd.concat([spy, fx], axis=1)
prices = prices.dropna(subset=[INDEX_TICKER, FX_TICKER])
prices.index = pd.to_datetime(prices.index)

if prices.empty:
    raise SystemExit("No overlapping SPY and FX data fetched.")

prices["SPY_CAD"] = prices[INDEX_TICKER] / prices[FX_TICKER]

print(f"✅ Fetched {len(prices)} trading days of data")

# =============================================================================
# COMPUTE RSI AND RSI SMA
# =============================================================================
print("\nComputing RSI(14) and RSI SMA(7)...")

def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate RSI using Wilder's smoothing (industry standard).
    Matches TradingView and other platforms.
    """
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    # Initialize arrays for Wilder's smoothing
    avg_gain = pd.Series(index=series.index, dtype=float)
    avg_loss = pd.Series(index=series.index, dtype=float)
    
    # First value: SMA
    avg_gain.iloc[period] = gain.iloc[1:period+1].mean()
    avg_loss.iloc[period] = loss.iloc[1:period+1].mean()
    
    # Subsequent values: Wilder's smoothing
    for i in range(period + 1, len(series)):
        avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period - 1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period - 1) + loss.iloc[i]) / period
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

prices["RSI"] = compute_rsi(prices[INDEX_TICKER], RSI_PERIOD)
prices["RSI_SMA"] = prices["RSI"].rolling(RSI_SMA_PERIOD).mean()
prices = prices.dropna(subset=["RSI", "RSI_SMA"])

start_date = prices.index[0]
end_date_dt = prices.index[-1]

print(f"✅ Data range: {start_date.date()} to {end_date_dt.date()}")

# =============================================================================
# BUILD EXECUTION SCHEDULE
# =============================================================================
print("\nBuilding execution schedule (3rd & 17th with TSX trading day validation)...")

def get_next_tsx_trading_day(date: datetime) -> datetime:
    """Get next TSX trading day on or after the given date."""
    current = pd.Timestamp(date)
    while not tsx_calendar.is_trading_day(current):
        current += timedelta(days=1)
    return current

execution_schedule = []
current_year = start_date.year
current_month = start_date.month

while True:
    for day in EXECUTION_DAYS:
        try:
            execution_date = datetime(current_year, current_month, day)
            
            if execution_date < start_date:
                continue
            
            if execution_date > end_date_dt:
                break
            
            trading_day = get_next_tsx_trading_day(execution_date)
            
            if trading_day in prices.index:
                execution_schedule.append(trading_day)
        except ValueError:
            pass
    
    current_month += 1
    if current_month > 12:
        current_month = 1
        current_year += 1
    
    if datetime(current_year, current_month, 1) > end_date_dt:
        break

execution_schedule = sorted(list(set(execution_schedule)))
execution_set = set(execution_schedule)

print(f"✅ {len(execution_schedule)} execution days scheduled")

# =============================================================================
# SIMULATE RAINY DAY STRATEGY TO FIND BUY POINTS
# =============================================================================
print("\nSimulating rainy day strategy to identify buy points...")

cash_pool = INITIAL_CASH_POOL
rainy_buys = []

for dt in execution_schedule:
    if dt not in prices.index:
        continue
    
    row = prices.loc[dt]
    price_cad = row["SPY_CAD"]
    rsi_sma = row["RSI_SMA"]
    
    # Check for rainy day
    is_rainy = rsi_sma < RSI_THRESHOLD
    
    if is_rainy and cash_pool >= RAINY_AMOUNT:
        rainy_buys.append({
            "date": dt,
            "rsi_sma": rsi_sma,
            "price": price_cad
        })
        cash_pool -= RAINY_AMOUNT
    
    # Add cash savings
    cash_pool += CASH_ACCUMULATION

print(f"✅ Found {len(rainy_buys)} rainy day buys")

# =============================================================================
# GENERATE CHART
# =============================================================================
print("\nGenerating RSI timeline chart...")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), sharex=True)

# Top panel: RSI SMA with threshold
ax1.plot(prices.index, prices['RSI_SMA'], color='#2E86AB', linewidth=1.5, label='RSI SMA(7)')
ax1.axhline(y=RSI_THRESHOLD, color='#D62828', linestyle='--', linewidth=2, 
            label=f'Rainy Threshold ({RSI_THRESHOLD})')

# Mark rainy execution days
if rainy_buys:
    rainy_dates = [rb['date'] for rb in rainy_buys]
    rainy_rsi = [rb['rsi_sma'] for rb in rainy_buys]
    ax1.scatter(rainy_dates, rainy_rsi, color='#06A77D', s=100, zorder=5, 
                marker='v', edgecolor='black', linewidth=1.5, label='Rainy Buy Executed')

ax1.set_ylabel('RSI SMA(7)', fontsize=12, fontweight='bold')
ax1.set_title(f'RSI SMA(7) Timeline & Rainy Day Buys\n{start_date.date()} to {end_date_dt.date()}',
              fontsize=14, fontweight='bold', pad=15)
ax1.legend(loc='upper right', fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0, 100)

# Bottom panel: SPY price
ax2.plot(prices.index, prices['SPY_CAD'], color='#1A1A1A', linewidth=1.5, label='SPY Price (CAD)')

# Mark rainy execution days
if rainy_buys:
    rainy_dates = [rb['date'] for rb in rainy_buys]
    rainy_prices = [rb['price'] for rb in rainy_buys]
    ax2.scatter(rainy_dates, rainy_prices, color='#06A77D', s=100, zorder=5,
                marker='v', edgecolor='black', linewidth=1.5, label='Rainy Buy Executed')

ax2.set_xlabel('Date', fontsize=12, fontweight='bold')
ax2.set_ylabel('SPY Price (CAD)', fontsize=12, fontweight='bold')
ax2.set_title('SPY Price & Rainy Day Buy Points',
              fontsize=12, fontweight='bold')
ax2.legend(loc='upper left', fontsize=10)
ax2.grid(True, alpha=0.3)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:.2f}'))

# Format x-axis
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax2.xaxis.set_major_locator(mdates.YearLocator(2))
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.savefig('rsi_timeline_rainy_days.png', dpi=300, bbox_inches='tight')
print(f"✅ Saved: rsi_timeline_rainy_days.png")

# =============================================================================
# SUMMARY STATS
# =============================================================================
print("\n" + "=" * 80)
print("RAINY DAY SUMMARY")
print("=" * 80)
print(f"Total execution days: {len(execution_schedule)}")
print(f"Total rainy buys: {len(rainy_buys)}")
print(f"Rainy frequency: {(len(rainy_buys)/len(execution_schedule))*100:.1f}%")

if rainy_buys:
    avg_rsi = np.mean([rb['rsi_sma'] for rb in rainy_buys])
    avg_price = np.mean([rb['price'] for rb in rainy_buys])
    print(f"Average RSI SMA on rainy days: {avg_rsi:.2f}")
    print(f"Average price on rainy days: ${avg_price:.2f} CAD")
    
    # Count consecutive rainy days
    rainy_dates = [rb['date'] for rb in rainy_buys]
    rainy_indices = [execution_schedule.index(rd) for rd in rainy_dates if rd in execution_schedule]
    
    consecutive_counts = {}
    if rainy_indices:
        current_streak = 1
        for i in range(1, len(rainy_indices)):
            if rainy_indices[i] == rainy_indices[i-1] + 1:
                current_streak += 1
            else:
                consecutive_counts[current_streak] = consecutive_counts.get(current_streak, 0) + 1
                current_streak = 1
        consecutive_counts[current_streak] = consecutive_counts.get(current_streak, 0) + 1
    
    if consecutive_counts:
        print(f"\nConsecutive Rainy Day Periods:")
        for streak_length in sorted(consecutive_counts.keys()):
            count = consecutive_counts[streak_length]
            print(f"  {streak_length} consecutive: {count} occurrence(s)")

print("\n" + "=" * 80)
print("CHART GENERATION COMPLETE")
print("=" * 80)
