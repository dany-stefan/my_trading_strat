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
# ADDITIONAL INDICATORS FOR TURBO COMPARISON (200-day MA, VIX)
# =============================================================================
print("Computing 200-day MA and fetching VIX for TURBO overlay...")
prices["MA_200"] = prices[INDEX_TICKER].rolling(200).mean()

# Fetch VIX daily close and align to price index
vix_series = fetch_series("^VIX", START_DATE, end_date)
if vix_series.empty:
    print("Warning: VIX series empty; defaulting to 20.0 (medium)")
    vix_series = pd.Series(20.0, index=prices.index)
vix_series = vix_series.reindex(prices.index).fillna(method="ffill").fillna(method="bfill")
prices["VIX"] = vix_series

# =============================================================================
# INDICATORS (RSI and RSI SMA)
# =============================================================================
print("Computing RSI(14) and RSI SMA(7) on SPY using Wilder's smoothing...")

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
    
    contrib_cum = contributions
    for dt, row in prices.iterrows():
        price_cad = row["SPY_CAD"]
        rsi_sma = row["RSI_SMA"]
        contrib_today = 0.0
        
        # Execution day logic
        if dt in execution_set:
            # Base investment (always)
            if price_cad > 0:
                shares += DCA_BASE_AMOUNT / price_cad
                contributions += DCA_BASE_AMOUNT
                contrib_cum += DCA_BASE_AMOUNT
                contrib_today += DCA_BASE_AMOUNT
            
            # Check for rainy day
            is_rainy = rsi_sma < RSI_THRESHOLD
            
            if is_rainy:
                total_rainy_days += 1
                
                # Deploy extra if we have cash
                if cash_pool >= RAINY_AMOUNT:
                    shares += RAINY_AMOUNT / price_cad
                    contributions += RAINY_AMOUNT
                    contrib_cum += RAINY_AMOUNT
                    contrib_today += RAINY_AMOUNT
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
            "cash_pool": cash_pool,
            "contrib_cum": contrib_cum,
            "contrib_today": contrib_today
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
        "strategy": f"PROD: RSI SMA({RSI_SMA_PERIOD}) < {RSI_THRESHOLD} & rainy ${RAINY_AMOUNT}",
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
# TURBO STRATEGY SIMULATION (Adaptive threshold + VIX sizing)
# =============================================================================
def simulate_turbo_strategy():
    def classify_regime(price: float, ma200: float) -> str:
        if pd.isna(ma200) or ma200 == 0:
            return "NEUTRAL"
        dev = (price - ma200) / ma200
        if dev > 0.05:
            return "BULL"
        elif dev < -0.05:
            return "BEAR"
        else:
            return "NEUTRAL"

    shares = 0.0
    cash_pool = max(INITIAL_CASH_POOL, 450.0)
    contributions = INITIAL_LUMP_SUM

    first_price = prices.loc[start_date, "SPY_CAD"]
    if first_price > 0:
        shares = INITIAL_LUMP_SUM / first_price

    equity_records = []
    rainy_buys = []
    total_rainy_days = 0
    successful_rainy_buys = 0

    contrib_cum = contributions
    for dt, row in prices.iterrows():
        price_cad = row["SPY_CAD"]
        rsi_sma = row["RSI_SMA"]
        spy_price = row[INDEX_TICKER]
        ma200 = row["MA_200"]
        vix_val = row["VIX"]
        contrib_today = 0.0

        if dt in execution_set:
            # Base investment (always)
            if price_cad > 0:
                shares += DCA_BASE_AMOUNT / price_cad
                contributions += DCA_BASE_AMOUNT
                contrib_cum += DCA_BASE_AMOUNT
                contrib_today += DCA_BASE_AMOUNT

            # Determine regime and threshold
            regime = classify_regime(spy_price, ma200)
            adaptive_thresh = 42 if regime == "BULL" else 48 if regime == "BEAR" else 45

            # VIX-based sizing
            if vix_val < 15:
                rainy_amt_today = 150
            elif vix_val < 25:
                rainy_amt_today = 180
            else:
                rainy_amt_today = 210

            is_rainy = rsi_sma < adaptive_thresh
            if is_rainy:
                total_rainy_days += 1
                if cash_pool >= rainy_amt_today:
                    shares += rainy_amt_today / price_cad
                    contributions += rainy_amt_today
                    contrib_cum += rainy_amt_today
                    contrib_today += rainy_amt_today
                    cash_pool -= rainy_amt_today
                    successful_rainy_buys += 1
                    rainy_buys.append({
                        "date": dt,
                        "rsi_sma": rsi_sma,
                        "price": price_cad,
                        "amount": rainy_amt_today,
                        "regime": regime,
                        "vix": vix_val,
                        "threshold": adaptive_thresh,
                        "cash_before": cash_pool + rainy_amt_today,
                        "cash_after": cash_pool
                    })

            cash_pool += CASH_ACCUMULATION

        equity_records.append({
            "date": dt,
            "equity": shares * price_cad + cash_pool,
            "shares_value": shares * price_cad,
            "cash_pool": cash_pool,
            "contrib_cum": contrib_cum,
            "contrib_today": contrib_today
        })

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
        "strategy": "TURBO: Adaptive RSI (42/45/48) + VIX sizing (150/180/210)",
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
print("RUNNING SIMULATIONS: PROD vs TURBO")
print("=" * 80)

prod_strategy = simulate_rainy_day_strategy()
turbo_strategy = simulate_turbo_strategy()

# =============================================================================
# RESULTS
# =============================================================================
print("\n" + "=" * 80)
print("BACKTEST RESULTS - PROD vs TURBO (3rd & 17th)")
print("=" * 80)
print(f"\nExecution Schedule: 3rd and 17th of each month (or next TSX trading day)")
print(f"Total execution days: {prod_strategy['execution_days']}")
print(f"Period: {prod_strategy['years']:.2f} years")

print("\n" + "-" * 80)
print(f"PROD STRATEGY: RSI SMA({RSI_SMA_PERIOD}) < {RSI_THRESHOLD} & rainy ${RAINY_AMOUNT}")
print("-" * 80)
print(f"Total contributions: ${prod_strategy['contributions']:,.2f}")
print(f"Final equity: ${prod_strategy['end_equity']:,.2f}")
print(f"Final cash pool: ${prod_strategy['final_cash_pool']:,.2f}")
print(f"CAGR: {prod_strategy['cagr']*100:.2f}%")
print(f"Max drawdown: {prod_strategy['max_drawdown']*100:.2f}%")
print(f"Hit rate: {prod_strategy['hit_rate']*100:.1f}% | Rainy freq: {prod_strategy['rainy_frequency']*100:.1f}%")

print("\n" + "-" * 80)
print("TURBO STRATEGY: Adaptive (42/45/48) + VIX sizing (150/180/210)")
print("-" * 80)
print(f"Total contributions: ${turbo_strategy['contributions']:,.2f}")
print(f"Final equity: ${turbo_strategy['end_equity']:,.2f}")
print(f"Final cash pool: ${turbo_strategy['final_cash_pool']:,.2f}")
print(f"CAGR: {turbo_strategy['cagr']*100:.2f}%")
print(f"Max drawdown: {turbo_strategy['max_drawdown']*100:.2f}%")
print(f"Hit rate: {turbo_strategy['hit_rate']*100:.1f}% | Rainy freq: {turbo_strategy['rainy_frequency']*100:.1f}%")

print("\n" + "-" * 80)
print("PERFORMANCE COMPARISON (TURBO vs PROD)")
print("-" * 80)
outperformance = turbo_strategy['end_equity'] - prod_strategy['end_equity']
outperformance_pct = (outperformance / prod_strategy['end_equity']) * 100
print(f"TURBO minus PROD: +${outperformance:,.2f} ({outperformance_pct:+.1f}%)")
print(f"Extra capital deployed (TURBO - PROD): ${turbo_strategy['contributions'] - prod_strategy['contributions']:,.2f}")

# =============================================================================
# YEARLY PERFORMANCE (ROI/Profit) - PROD vs TURBO
# =============================================================================
print("\n" + "=" * 80)
print("YEARLY PERFORMANCE (ROI/Profit) - PROD vs TURBO")
print("=" * 80)

def compute_yearly_stats(eq_df: pd.DataFrame) -> pd.DataFrame:
    df = eq_df.copy()
    df = df[['equity', 'contrib_cum']].copy()
    df['year'] = df.index.year
    # Take first and last entries per year
    first = df.groupby('year').first().rename(columns={'equity':'equity_start','contrib_cum':'contrib_start'})
    last = df.groupby('year').last().rename(columns={'equity':'equity_end','contrib_cum':'contrib_end'})
    out = first.join(last, how='inner')
    out['contrib_year'] = out['contrib_end'] - out['contrib_start']
    out['profit_year'] = (out['equity_end'] - out['equity_start']) - out['contrib_year']
    out['roi_pct'] = np.where(out['equity_start']>0, out['profit_year'] / out['equity_start'] * 100.0, np.nan)
    return out.reset_index()

prod_yearly = compute_yearly_stats(prod_strategy['equity_curve'])
turbo_yearly = compute_yearly_stats(turbo_strategy['equity_curve'])

yearly = prod_yearly.merge(turbo_yearly, on='year', suffixes=('_prod','_turbo'))
yearly['diff_profit'] = yearly['profit_year_turbo'] - yearly['profit_year_prod']
yearly['winner'] = np.where(yearly['diff_profit']>0, 'TURBO', np.where(yearly['diff_profit']<0, 'PROD', 'TIE'))

yearly_cols = [
    'year',
    'equity_start_prod','equity_end_prod','contrib_year_prod','profit_year_prod','roi_pct_prod',
    'equity_start_turbo','equity_end_turbo','contrib_year_turbo','profit_year_turbo','roi_pct_turbo',
    'diff_profit','winner'
]
yearly[yearly_cols].to_csv('yearly_prod_vs_turbo.csv', index=False)
print("✅ Saved: yearly_prod_vs_turbo.csv")

# Yearly visuals: profit comparison and profit difference
try:
    fig_y, (ay1, ay2) = plt.subplots(2, 1, figsize=(16, 10))

    years_idx = yearly['year']
    width = 0.4

    # Subplot 1: Profit by year (PROD vs TURBO)
    ay1.bar(years_idx - 0.2, yearly['profit_year_prod'], width=0.4, label='PROD Profit', color='#2E86AB', alpha=0.85)
    ay1.bar(years_idx + 0.2, yearly['profit_year_turbo'], width=0.4, label='TURBO Profit', color='#06A77D', alpha=0.85)
    ay1.set_title('Yearly Profit (CAD): PROD vs TURBO', fontsize=13, fontweight='bold')
    ay1.set_ylabel('Profit (CAD)')
    ay1.grid(True, axis='y', alpha=0.3)
    ay1.legend(loc='upper left')

    # Subplot 2: Profit difference (TURBO - PROD)
    colors = np.where(yearly['diff_profit'] >= 0, '#06A77D', '#D62828')
    ay2.bar(years_idx, yearly['diff_profit'], color=colors, alpha=0.8)
    ay2.axhline(0, color='black', linewidth=1)
    ay2.set_title('Yearly Profit Difference: TURBO - PROD (CAD)', fontsize=13, fontweight='bold')
    ay2.set_xlabel('Year')
    ay2.set_ylabel('Diff (CAD)')
    ay2.grid(True, axis='y', alpha=0.3)

    # Format x-axis ticks to show every year clearly
    ay1.set_xticks(years_idx)
    ay2.set_xticks(years_idx)
    for ax in (ay1, ay2):
        ax.set_xticklabels([str(y) for y in years_idx], rotation=45, ha='right')

    plt.tight_layout()
    plt.savefig('yearly_prod_vs_turbo.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: yearly_prod_vs_turbo.png")
except Exception as e:
    print(f"⚠️  Failed to generate yearly charts: {e}")

# =============================================================================
# SAVE RESULTS
# =============================================================================
print("\n" + "=" * 80)
print("SAVING RESULTS")
print("=" * 80)

# Save equity curves
prod_strategy['equity_curve'].to_csv('equity_prod_rainy_calendar_dates.csv')
turbo_strategy['equity_curve'].to_csv('equity_turbo_rainy_calendar_dates.csv')
print(f"✅ Saved: equity_prod_rainy_calendar_dates.csv")
print(f"✅ Saved: equity_turbo_rainy_calendar_dates.csv")

# Save rainy buys logs
if prod_strategy['rainy_buys']:
    pd.DataFrame(prod_strategy['rainy_buys']).to_csv('rainy_buys_prod_calendar_dates.csv', index=False)
    print(f"✅ Saved: rainy_buys_prod_calendar_dates.csv ({len(prod_strategy['rainy_buys'])} records)")
if turbo_strategy['rainy_buys']:
    pd.DataFrame(turbo_strategy['rainy_buys']).to_csv('rainy_buys_turbo_calendar_dates.csv', index=False)
    print(f"✅ Saved: rainy_buys_turbo_calendar_dates.csv ({len(turbo_strategy['rainy_buys'])} records)")

# =============================================================================
# VISUALIZATION
# =============================================================================
print("\n" + "=" * 80)
print("GENERATING VISUALIZATIONS")
print("=" * 80)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))

# Top panel: Equity curves (PROD vs TURBO)
ax1.plot(prod_strategy['equity_curve'].index, prod_strategy['equity_curve']['equity'], 
         label=f'PROD: RSI SMA < {RSI_THRESHOLD} & rainy ${RAINY_AMOUNT}', color='#2E86AB', linewidth=2, alpha=0.85)
ax1.plot(turbo_strategy['equity_curve'].index, turbo_strategy['equity_curve']['equity'],
         label='TURBO: Adaptive (42/45/48) + VIX sizing', color='#06A77D', linewidth=2.5)

ax1.set_ylabel('Portfolio Value (CAD)', fontsize=12, fontweight='bold')
ax1.set_title('PROD vs TURBO: Calendar Date Schedule (3rd & 17th)\nPayday: 1st & 15th, Execution: 3rd & 17th (2 days later)', 
              fontsize=14, fontweight='bold', pad=15)
ax1.legend(loc='upper left', fontsize=11)
ax1.grid(True, alpha=0.3)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))

# Bottom panel: Outperformance (TURBO - PROD)
outperformance_series = turbo_strategy['equity_curve']['equity'] - prod_strategy['equity_curve']['equity']
ax2.fill_between(outperformance_series.index, 0, outperformance_series, 
                  where=(outperformance_series >= 0), color='#06A77D', alpha=0.3, label='TURBO > PROD')
ax2.fill_between(outperformance_series.index, 0, outperformance_series,
                  where=(outperformance_series < 0), color='#D62828', alpha=0.3, label='TURBO < PROD')
ax2.plot(outperformance_series.index, outperformance_series, color='#1A1A1A', linewidth=1.5)
ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)

ax2.set_xlabel('Date', fontsize=12, fontweight='bold')
ax2.set_ylabel('TURBO - PROD (CAD)', fontsize=12, fontweight='bold')
ax2.set_title('Cumulative Outperformance (TURBO vs PROD)', fontsize=12, fontweight='bold')
ax2.legend(loc='upper left', fontsize=10)
ax2.grid(True, alpha=0.3)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))

# Format x-axis
for ax in [ax1, ax2]:
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.savefig('strategy_comparison_prod_vs_turbo.png', dpi=300, bbox_inches='tight')
print(f"✅ Saved: strategy_comparison_prod_vs_turbo.png")

# Additional visualization: Rainy amount over time (PROD vs TURBO)
try:
    exec_idx = pd.DatetimeIndex(execution_schedule)
    rainy_prod = pd.Series(0.0, index=exec_idx)
    rainy_turbo = pd.Series(0.0, index=exec_idx)

    if prod_strategy['rainy_buys']:
        dfp = pd.DataFrame(prod_strategy['rainy_buys'])
        dfp['date'] = pd.to_datetime(dfp['date'])
        dfp = dfp.set_index('date').sort_index()
        for dt_i, row_i in dfp.iterrows():
            if dt_i in rainy_prod.index:
                rainy_prod.loc[dt_i] = float(row_i['amount'])

    if turbo_strategy['rainy_buys']:
        dft = pd.DataFrame(turbo_strategy['rainy_buys'])
        dft['date'] = pd.to_datetime(dft['date'])
        dft = dft.set_index('date').sort_index()
        for dt_i, row_i in dft.iterrows():
            if dt_i in rainy_turbo.index:
                rainy_turbo.loc[dt_i] = float(row_i['amount'])

    rainy_df = pd.DataFrame({
        'rainy_prod': rainy_prod,
        'rainy_turbo': rainy_turbo
    })
    # Rolling-average overlays (3-execution window)
    rainy_df['rainy_prod_roll3'] = rainy_df['rainy_prod'].rolling(window=3, min_periods=1).mean()
    rainy_df['rainy_turbo_roll3'] = rainy_df['rainy_turbo'].rolling(window=3, min_periods=1).mean()
    rainy_df.to_csv('rainy_amounts_timeseries.csv')

    fig_r, ar = plt.subplots(figsize=(16, 6))
    ar.plot(rainy_df.index, rainy_df['rainy_prod'], label='PROD Rainy Amount', color='#2E86AB', linewidth=1.5, marker='o', alpha=0.8)
    ar.plot(rainy_df.index, rainy_df['rainy_turbo'], label='TURBO Rainy Amount', color='#06A77D', linewidth=1.8, marker='o', alpha=0.9)
    ar.plot(rainy_df.index, rainy_df['rainy_prod_roll3'], label='PROD 3-Exec Avg', color='#2E86AB', linewidth=2.0, linestyle='--', alpha=0.9)
    ar.plot(rainy_df.index, rainy_df['rainy_turbo_roll3'], label='TURBO 3-Exec Avg', color='#06A77D', linewidth=2.2, linestyle='--', alpha=0.9)
    ar.axhline(150, color='#999999', linestyle='--', linewidth=1, alpha=0.7, label='PROD Fixed Rainy ($150)')
    ar.set_title('Rainy Amount Over Time: PROD vs TURBO', fontsize=13, fontweight='bold')
    ar.set_xlabel('Execution Date')
    ar.set_ylabel('Rainy Amount (CAD)')
    ar.grid(True, alpha=0.3)
    ar.legend(loc='upper left')
    ar.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ar.xaxis.set_major_locator(mdates.YearLocator(2))
    plt.setp(ar.xaxis.get_majorticklabels(), rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('rainy_amount_over_time_prod_vs_turbo.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: rainy_amount_over_time_prod_vs_turbo.png")
    print("✅ Saved: rainy_amounts_timeseries.csv")
except Exception as e:
    print(f"⚠️  Failed to generate rainy-amount-over-time chart: {e}")

print("\n" + "=" * 80)
print("GENERATING ENHANCED VISUALIZATIONS (TURBOCHARGED)")
print("=" * 80)

# Import enhanced visualizations
try:
    from enhanced_visualizations import (
        create_interactive_dashboard,
        create_regime_performance_breakdown,
        create_monte_carlo_cash_pool_simulation,
        create_consecutive_rainy_day_heatmap
    )
    
    # Prepare data for enhanced visualizations
    equity_df = turbo_strategy['equity_curve'].copy()
    equity_df['spy_price'] = prices['SPY_CAD']
    equity_df['rsi_sma'] = prices['RSI_SMA']
    
    rainy_buys_df = pd.DataFrame(turbo_strategy['rainy_buys'])
    if len(rainy_buys_df) > 0:
        rainy_buys_df['date'] = pd.to_datetime(rainy_buys_df['date'])
    
    cash_pool_df = turbo_strategy['equity_curve'][['cash_pool']].copy()
    
    execution_schedule_index = pd.DatetimeIndex(execution_schedule)
    
    # Generate enhanced charts
    print("📊 Creating interactive performance dashboard...")
    create_interactive_dashboard(equity_df, rainy_buys_df, cash_pool_df,
                                 output_path="dashboard_interactive_turbo.png")
    
    print("📊 Creating regime performance breakdown...")
    create_regime_performance_breakdown(equity_df,
                                       output_path="regime_performance_turbo.png")
    
    print("📊 Creating Monte Carlo cash pool simulation...")
    create_monte_carlo_cash_pool_simulation(
        initial_pool=max(INITIAL_CASH_POOL, 450.0),
        accumulation=CASH_ACCUMULATION,
        rainy_amount=180,
        rainy_frequency=turbo_strategy['rainy_frequency'],
        n_simulations=1000,
        n_execution_days=turbo_strategy['execution_days'],
        output_path="monte_carlo_cash_pool_turbo.png"
    )
    
    print("📊 Creating consecutive rainy day heatmap...")
    create_consecutive_rainy_day_heatmap(
        rainy_buys_df,
        execution_schedule_index,
        prices['RSI_SMA'],
        output_path="consecutive_rainy_heatmap_turbo.png"
    )
    
    print("✅ All enhanced visualizations created!")
    
except Exception as e:
    print(f"⚠️  Enhanced visualizations failed: {e}")
    print("   Continuing with standard charts...")

print("\n" + "=" * 80)
print("BACKTEST COMPLETE - PROD vs TURBO (TURBOCHARGED)")
print("=" * 80)
print(f"\n📊 Summary:")
print(f"   Execution schedule: 3rd & 17th (payday: 1st & 15th)")
print(f"   Total executions: {prod_strategy['execution_days']}")
print(f"   PROD final value: ${prod_strategy['end_equity']:,.2f}")
print(f"   TURBO final value: ${turbo_strategy['end_equity']:,.2f}")
print(f"   Outperformance (TURBO-PROD): +${outperformance:,.2f} ({outperformance_pct:+.1f}%)")
print(f"   PROD CAGR: {prod_strategy['cagr']*100:.2f}% | TURBO CAGR: {turbo_strategy['cagr']*100:.2f}%")
print(f"\n📈 Enhanced Charts Generated:")
print(f"   ✅ dashboard_interactive_turbo.png")
print(f"   ✅ regime_performance_turbo.png")
print(f"   ✅ monte_carlo_cash_pool_turbo.png")
print(f"   ✅ consecutive_rainy_heatmap_turbo.png")
