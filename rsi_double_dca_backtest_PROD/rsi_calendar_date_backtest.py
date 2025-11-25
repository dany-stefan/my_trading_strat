"""
RSI Cash Strategy Backtest - Calendar Date Schedule (3rd & 17th)
================================================================

This backtest uses EXACT calendar dates (3rd and 17th of each month) 
instead of bi-weekly Mondays, matching your live monitoring schedule.

WHAT THIS DOES:
- Tests RSI SMA(7) < 45 strategy on 3rd and 17th of each month
- Automatically rolls to next TSX trading day if 3rd/17th is weekend/holiday
- Matches your exact live monitoring schedule for accurate projections
- All variants use:
  * $150 base investment on execution days (3rd and 17th)
  * $30 cash savings on execution days
  * Extra buy from cash pool on rainy days (RSI SMA(7) < 45)
"""

from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from trading_calendar import get_calendar
from strategy_config import get_strategy_config, STRATEGY_VARIANTS
from rsi_indicators import compute_rsi_with_sma

# =============================================================================
# PARAMETERS
# =============================================================================
START_DATE = "2003-01-01"
INDEX_TICKER = "SPY"
FX_TICKER = "CADUSD=X"
INITIAL_LUMP_SUM = 1000.0

# Get strategy configuration
strategy_config = get_strategy_config('VARIANT_2')

DCA_BASE_AMOUNT = strategy_config.dca_base_amount
CASH_ACCUMULATION = strategy_config.cash_accumulation_per_payday
RAINY_AMOUNT = strategy_config.rainy_extra_amount
RSI_THRESHOLD = strategy_config.rsi_threshold
RSI_PERIOD = strategy_config.rsi_period
RSI_SMA_PERIOD = strategy_config.rsi_sma_period
INITIAL_CASH_POOL = strategy_config.initial_cash_pool

# Execution days (payday is 1st/15th, execution is 3rd/17th)
EXECUTION_DAYS = [3, 17]

# Get TSX calendar
tsx_calendar = get_calendar('TSX')

# =============================================================================
# DATA FETCH
# =============================================================================
print("=" * 80)
print("RSI CASH STRATEGY BACKTEST - CALENDAR DATE SCHEDULE (3rd & 17th)")
print("=" * 80)
print(f"Fetching data from {START_DATE} to today...")

end_date = datetime.now().strftime("%Y-%m-%d")

def fetch_series(ticker: str, start: str, end: str) -> pd.Series:
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

spy = fetch_series(INDEX_TICKER, START_DATE, end_date)
fx = fetch_series(FX_TICKER, START_DATE, end_date)
prices = pd.concat([spy, fx], axis=1)
prices = prices.dropna(subset=[INDEX_TICKER, FX_TICKER])
prices.index = pd.to_datetime(prices.index)

if prices.empty:
    raise SystemExit("No overlapping SPY and FX data fetched.")

prices["SPY_CAD"] = prices[INDEX_TICKER] / prices[FX_TICKER]

# =============================================================================
# INDICATORS (RSI and RSI SMA)
# =============================================================================
print("Computing RSI(14) and RSI SMA(7) on SPY...")

# Use shared RSI calculation module (SINGLE SOURCE OF TRUTH)
prices["RSI"], prices["RSI_SMA"] = compute_rsi_with_sma(
    prices[INDEX_TICKER], 
    rsi_period=RSI_PERIOD, 
    sma_period=RSI_SMA_PERIOD
)
prices = prices.dropna(subset=["RSI", "RSI_SMA"])

start_date = prices.index[0]
end_date_dt = prices.index[-1]
print(f"Data range: {start_date.date()} to {end_date_dt.date()} ({len(prices)} trading days)")

# =============================================================================
# BUILD EXECUTION DAY SCHEDULE (3rd and 17th of each month)
# =============================================================================
print("Building execution day schedule (3rd & 17th with TSX trading day validation)...")

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
            # Create the execution date
            execution_date = datetime(current_year, current_month, day)
            
            # Skip if before our data range
            if execution_date < start_date:
                continue
            
            # Stop if beyond our data range
            if execution_date > end_date_dt:
                break
            
            # Roll to next TSX trading day if needed
            trading_day = get_next_tsx_trading_day(execution_date)
            
            # Make sure it's in our price data
            if trading_day in prices.index:
                execution_schedule.append(trading_day)
        except ValueError:
            # Invalid date (e.g., Feb 31st doesn't exist)
            pass
    
    # Move to next month
    current_month += 1
    if current_month > 12:
        current_month = 1
        current_year += 1
    
    # Stop if we've gone past our data range
    if datetime(current_year, current_month, 1) > end_date_dt:
        break

execution_schedule = sorted(list(set(execution_schedule)))
execution_set = set(execution_schedule)

print(f"Total execution days (3rd & 17th): {len(execution_schedule)}")
print(f"First execution: {execution_schedule[0].date()}")
print(f"Last execution: {execution_schedule[-1].date()}")
print(f"Average days between executions: {(execution_schedule[-1] - execution_schedule[0]).days / len(execution_schedule):.1f}")

# =============================================================================
# BASELINE DCA SIMULATION (No Rainy Days)
# =============================================================================
def simulate_baseline_dca():
    """
    Simulate simple DCA on 3rd and 17th with no rainy day strategy.
    Just $150 on each execution day, no cash accumulation or rainy buys.
    """
    shares = 0.0
    contributions = INITIAL_LUMP_SUM
    
    # Initial lump sum
    first_price = prices.loc[start_date, "SPY_CAD"]
    if first_price > 0:
        shares = INITIAL_LUMP_SUM / first_price
    
    equity_records = []
    
    for dt, row in prices.iterrows():
        price_cad = row["SPY_CAD"]
        
        # Execution day: base investment only
        if dt in execution_set:
            if price_cad > 0:
                shares += DCA_BASE_AMOUNT / price_cad
                contributions += DCA_BASE_AMOUNT
        
        # Track equity
        equity_records.append({"date": dt, "equity": shares * price_cad})
    
    # Calculate metrics
    eq_df = pd.DataFrame(equity_records).set_index("date")
    eq = eq_df["equity"]
    
    start_val = eq.iloc[0]
    end_val = eq.iloc[-1]
    years = (eq.index[-1] - eq.index[0]).days / 365.25
    cagr = (end_val / start_val) ** (1/years) - 1 if start_val > 0 and years > 0 else np.nan
    
    roll_max = eq.cummax()
    drawdown = (eq / roll_max) - 1
    max_dd = drawdown.min()
    
    return {
        "strategy": "Baseline DCA (3rd & 17th)",
        "contributions": contributions,
        "end_equity": end_val,
        "cagr": cagr,
        "max_drawdown": max_dd,
        "equity_curve": eq_df,
        "years": years
    }

# =============================================================================
# RSI SMA RAINY DAY STRATEGY SIMULATION
# =============================================================================
def simulate_rainy_day_strategy():
    """
    Simulate RSI SMA(7) < 45 rainy day strategy on 3rd and 17th.
    """
    shares = 0.0
    cash_pool = INITIAL_CASH_POOL
    contributions = INITIAL_LUMP_SUM
    
    # Initial lump sum
    first_price = prices.loc[start_date, "SPY_CAD"]
    if first_price > 0:
        shares = INITIAL_LUMP_SUM / first_price
    
    equity_records = []
    rainy_buys = []
    total_rainy_days = 0
    successful_rainy_buys = 0
    
    for dt, row in prices.iterrows():
        price_cad = row["SPY_CAD"]
        rsi_sma = row["RSI_SMA"]
        
        # Execution day logic
        if dt in execution_set:
            # Base investment (always)
            if price_cad > 0:
                shares += DCA_BASE_AMOUNT / price_cad
                contributions += DCA_BASE_AMOUNT
            
            # Check for rainy day
            is_rainy = rsi_sma < RSI_THRESHOLD
            
            if is_rainy:
                total_rainy_days += 1
                
                # Deploy extra if we have cash
                if cash_pool >= RAINY_AMOUNT:
                    shares += RAINY_AMOUNT / price_cad
                    contributions += RAINY_AMOUNT
                    cash_pool -= RAINY_AMOUNT
                    successful_rainy_buys += 1
                    
                    rainy_buys.append({
                        "date": dt,
                        "rsi_sma": rsi_sma,
                        "price": price_cad,
                        "amount": RAINY_AMOUNT,
                        "cash_before": cash_pool + RAINY_AMOUNT,
                        "cash_after": cash_pool
                    })
            
            # Add cash savings
            cash_pool += CASH_ACCUMULATION
        
        # Track total equity (shares + cash pool)
        equity_records.append({
            "date": dt, 
            "equity": shares * price_cad + cash_pool,
            "shares_value": shares * price_cad,
            "cash_pool": cash_pool
        })
    
    # Calculate metrics
    eq_df = pd.DataFrame(equity_records).set_index("date")
    eq = eq_df["equity"]
    
    start_val = eq.iloc[0]
    end_val = eq.iloc[-1]
    years = (eq.index[-1] - eq.index[0]).days / 365.25
    cagr = (end_val / start_val) ** (1/years) - 1 if start_val > 0 and years > 0 else np.nan
    
    roll_max = eq.cummax()
    drawdown = (eq / roll_max) - 1
    max_dd = drawdown.min()
    
    hit_rate = successful_rainy_buys / total_rainy_days if total_rainy_days > 0 else 0
    rainy_frequency = total_rainy_days / len(execution_schedule)
    
    return {
        "strategy": f"RSI SMA({RSI_SMA_PERIOD}) < {RSI_THRESHOLD}",
        "contributions": contributions,
        "end_equity": end_val,
        "final_cash_pool": cash_pool,
        "cagr": cagr,
        "max_drawdown": max_dd,
        "equity_curve": eq_df,
        "years": years,
        "total_rainy_days": total_rainy_days,
        "successful_rainy_buys": successful_rainy_buys,
        "hit_rate": hit_rate,
        "rainy_frequency": rainy_frequency,
        "rainy_buys": rainy_buys,
        "execution_days": len(execution_schedule)
    }

# =============================================================================
# RUN SIMULATIONS
# =============================================================================
print("\n" + "=" * 80)
print("RUNNING SIMULATIONS")
print("=" * 80)

baseline = simulate_baseline_dca()
rainy_strategy = simulate_rainy_day_strategy()

# =============================================================================
# RESULTS
# =============================================================================
print("\n" + "=" * 80)
print("BACKTEST RESULTS - CALENDAR DATE SCHEDULE (3rd & 17th)")
print("=" * 80)
print(f"\nExecution Schedule: 3rd and 17th of each month (or next TSX trading day)")
print(f"Total execution days: {rainy_strategy['execution_days']}")
print(f"Period: {rainy_strategy['years']:.2f} years")

print("\n" + "-" * 80)
print("BASELINE DCA (No Rainy Day Strategy)")
print("-" * 80)
print(f"Total contributions: ${baseline['contributions']:,.2f}")
print(f"Final equity: ${baseline['end_equity']:,.2f}")
print(f"CAGR: {baseline['cagr']*100:.2f}%")
print(f"Max drawdown: {baseline['max_drawdown']*100:.2f}%")
print(f"ROI: {(baseline['end_equity']/baseline['contributions']-1)*100:.1f}%")

print("\n" + "-" * 80)
print(f"RAINY DAY STRATEGY: RSI SMA({RSI_SMA_PERIOD}) < {RSI_THRESHOLD}")
print("-" * 80)
print(f"Total contributions: ${rainy_strategy['contributions']:,.2f}")
print(f"Final equity: ${rainy_strategy['end_equity']:,.2f}")
print(f"Final cash pool: ${rainy_strategy['final_cash_pool']:,.2f}")
print(f"CAGR: {rainy_strategy['cagr']*100:.2f}%")
print(f"Max drawdown: {rainy_strategy['max_drawdown']*100:.2f}%")
print(f"ROI: {(rainy_strategy['end_equity']/rainy_strategy['contributions']-1)*100:.1f}%")

print(f"\nRainy Day Statistics:")
print(f"  Total rainy days (RSI SMA < {RSI_THRESHOLD}): {rainy_strategy['total_rainy_days']}")
print(f"  Successful deployments: {rainy_strategy['successful_rainy_buys']}")
print(f"  Hit rate: {rainy_strategy['hit_rate']*100:.1f}%")
print(f"  Rainy day frequency: {rainy_strategy['rainy_frequency']*100:.1f}%")
print(f"  Missed opportunities: {rainy_strategy['total_rainy_days'] - rainy_strategy['successful_rainy_buys']}")

print("\n" + "-" * 80)
print("PERFORMANCE COMPARISON")
print("-" * 80)
outperformance = rainy_strategy['end_equity'] - baseline['end_equity']
outperformance_pct = (outperformance / baseline['end_equity']) * 100
print(f"Rainy strategy vs Baseline: +${outperformance:,.2f} ({outperformance_pct:+.1f}%)")
print(f"Extra capital deployed: ${rainy_strategy['contributions'] - baseline['contributions']:,.2f}")
print(f"Return on rainy capital: {(outperformance / (rainy_strategy['contributions'] - baseline['contributions']))*100:.1f}%")

# =============================================================================
# SAVE RESULTS
# =============================================================================
print("\n" + "=" * 80)
print("SAVING RESULTS")
print("=" * 80)

# Save equity curves
baseline['equity_curve'].to_csv('equity_baseline_calendar_dates.csv')
rainy_strategy['equity_curve'].to_csv('equity_rainy_strategy_calendar_dates.csv')
print(f"✅ Saved: equity_baseline_calendar_dates.csv")
print(f"✅ Saved: equity_rainy_strategy_calendar_dates.csv")

# Save rainy buys log
if rainy_strategy['rainy_buys']:
    rainy_df = pd.DataFrame(rainy_strategy['rainy_buys'])
    rainy_df.to_csv('rainy_buys_calendar_dates.csv', index=False)
    print(f"✅ Saved: rainy_buys_calendar_dates.csv ({len(rainy_strategy['rainy_buys'])} records)")
    
    # Generate rainy analytics JSON from CSV
    print("Generating rainy analytics JSON...")
    from rainy_analytics import generate_rainy_analytics
    current_price = prices[INDEX_TICKER].iloc[-1]
    generate_rainy_analytics(current_spy_price=float(current_price))
    print(f"✅ Saved: rainy_analytics.json")

# =============================================================================
# VISUALIZATION
# =============================================================================
print("\n" + "=" * 80)
print("GENERATING VISUALIZATIONS")
print("=" * 80)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))

# Top panel: Equity curves
ax1.plot(baseline['equity_curve'].index, baseline['equity_curve']['equity'], 
         label='Baseline DCA (3rd & 17th)', color='#2E86AB', linewidth=2, alpha=0.7)
ax1.plot(rainy_strategy['equity_curve'].index, rainy_strategy['equity_curve']['equity'],
         label=f'Rainy Day Strategy (RSI SMA < {RSI_THRESHOLD})', color='#06A77D', linewidth=2.5)

ax1.set_ylabel('Portfolio Value (CAD)', fontsize=12, fontweight='bold')
ax1.set_title('Strategy Performance: Calendar Date Schedule (3rd & 17th)\nPayday: 1st & 15th, Execution: 3rd & 17th (2 days later)', 
              fontsize=14, fontweight='bold', pad=15)
ax1.legend(loc='upper left', fontsize=11)
ax1.grid(True, alpha=0.3)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))

# Bottom panel: Outperformance
outperformance_series = rainy_strategy['equity_curve']['equity'] - baseline['equity_curve']['equity']
ax2.fill_between(outperformance_series.index, 0, outperformance_series, 
                  where=(outperformance_series >= 0), color='#06A77D', alpha=0.3, label='Outperformance')
ax2.fill_between(outperformance_series.index, 0, outperformance_series,
                  where=(outperformance_series < 0), color='#D62828', alpha=0.3, label='Underperformance')
ax2.plot(outperformance_series.index, outperformance_series, color='#1A1A1A', linewidth=1.5)
ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)

ax2.set_xlabel('Date', fontsize=12, fontweight='bold')
ax2.set_ylabel('Rainy Strategy - Baseline (CAD)', fontsize=12, fontweight='bold')
ax2.set_title('Cumulative Outperformance', fontsize=12, fontweight='bold')
ax2.legend(loc='upper left', fontsize=10)
ax2.grid(True, alpha=0.3)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))

# Format x-axis
for ax in [ax1, ax2]:
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.savefig('strategy_comparison_calendar_dates.png', dpi=300, bbox_inches='tight')
print(f"✅ Saved: strategy_comparison_calendar_dates.png")

print("\n" + "=" * 80)
print("BACKTEST COMPLETE")
print("=" * 80)
print(f"\n📊 Summary:")
print(f"   Execution schedule: 3rd & 17th (payday: 1st & 15th)")
print(f"   Total executions: {rainy_strategy['execution_days']}")
print(f"   Rainy days: {rainy_strategy['total_rainy_days']} ({rainy_strategy['rainy_frequency']*100:.1f}%)")
print(f"   Hit rate: {rainy_strategy['hit_rate']*100:.1f}%")
print(f"   Final value: ${rainy_strategy['end_equity']:,.2f}")
print(f"   Outperformance: +${outperformance:,.2f} ({outperformance_pct:+.1f}%)")
print(f"   CAGR: {rainy_strategy['cagr']*100:.2f}%")
