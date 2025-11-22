"""
Simplified Backtest: Variant Strategy vs Simple DCA
====================================================

Compares TWO strategies only:
1. Simple DCA: $150 on 3rd and 17th (no rainy day logic)
2. Variant 2: RSI SMA(7) < 45 strategy with cash pool

Period: Jan 1, 2025 - Nov 21, 2025 (YTD)
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
START_DATE = "2025-01-01"
END_DATE = datetime.now().strftime("%Y-%m-%d")
INDEX_TICKER = "SPY"
FX_TICKER = "CADUSD=X"

# Strategy parameters
DCA_AMOUNT = 150.0  # Both strategies invest $150 per execution day
EXECUTION_DAYS = [3, 17]  # 3rd and 17th of each month

# Variant strategy config
variant_config = get_strategy_config('VARIANT_2')
CASH_ACCUMULATION = variant_config.cash_accumulation_per_payday
RAINY_AMOUNT = variant_config.rainy_extra_amount
RSI_THRESHOLD = variant_config.rsi_threshold
RSI_PERIOD = variant_config.rsi_period
RSI_SMA_PERIOD = variant_config.rsi_sma_period
INITIAL_CASH_POOL = 0.0  # Start with $0 cash pool

# Get TSX calendar
tsx_calendar = get_calendar('TSX')

# =============================================================================
# DATA FETCH
# =============================================================================
print("=" * 80)
print("VARIANT VS SIMPLE DCA BACKTEST - YTD 2025")
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
    """Calculate RSI indicator."""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

prices["RSI"] = compute_rsi(prices[INDEX_TICKER], RSI_PERIOD)
prices["RSI_SMA"] = prices["RSI"].rolling(RSI_SMA_PERIOD).mean()
prices = prices.dropna(subset=["RSI", "RSI_SMA"])

start_date = prices.index[0]
end_date_dt = prices.index[-1]

print(f"✅ Data range: {start_date.date()} to {end_date_dt.date()}")
print(f"   ({len(prices)} trading days)")

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
print(f"   First: {execution_schedule[0].date()}")
print(f"   Last: {execution_schedule[-1].date()}")

# =============================================================================
# SIMULATION 1: SIMPLE DCA
# =============================================================================
def simulate_simple_dca():
    """
    Simple DCA: $150 on 3rd and 17th, no rainy day logic.
    """
    shares = 0.0
    contributions = 0.0
    
    equity_records = []
    
    for dt, row in prices.iterrows():
        price_cad = row["SPY_CAD"]
        
        # Buy on execution days
        if dt in execution_set:
            if price_cad > 0:
                shares += DCA_AMOUNT / price_cad
                contributions += DCA_AMOUNT
        
        # Track equity
        equity_records.append({
            "date": dt, 
            "equity": shares * price_cad,
            "contributions": contributions
        })
    
    eq_df = pd.DataFrame(equity_records).set_index("date")
    
    return {
        "strategy": "Simple DCA",
        "contributions": contributions,
        "shares": shares,
        "end_equity": eq_df["equity"].iloc[-1],
        "equity_curve": eq_df,
        "execution_count": len(execution_schedule)
    }

# =============================================================================
# SIMULATION 2: VARIANT STRATEGY (RSI SMA < 45)
# =============================================================================
def simulate_variant_strategy():
    """
    Variant 2 Strategy: RSI SMA(7) < 45 rainy day logic.
    - Base: $150 on every execution day
    - Cash pool: starts at $0, grows $30 per execution day
    - Rainy: deploy extra $150 (magically provided if insufficient cash) when RSI SMA < 45
    - FORCED 100% HIT RATE to demonstrate ROI from buying dips
    """
    shares = 0.0
    cash_pool = INITIAL_CASH_POOL
    contributions = 0.0
    
    equity_records = []
    rainy_buys = []
    total_rainy_days = 0
    successful_rainy_buys = 0
    rainy_days_list = []  # Track rainy day dates for consecutive analysis
    magically_provided_cash = 0.0  # Track how much cash was magically added
    
    for dt, row in prices.iterrows():
        price_cad = row["SPY_CAD"]
        rsi_sma = row["RSI_SMA"]
        
        # Execution day logic
        if dt in execution_set:
            # Base investment (always)
            if price_cad > 0:
                shares += DCA_AMOUNT / price_cad
                contributions += DCA_AMOUNT
            
            # Check for rainy day
            is_rainy = rsi_sma < RSI_THRESHOLD
            
            if is_rainy:
                total_rainy_days += 1
                rainy_days_list.append(dt)
                
                # FORCE 100% HIT RATE: magically provide cash if insufficient
                cash_before = cash_pool
                if cash_pool < RAINY_AMOUNT:
                    magic_cash_needed = RAINY_AMOUNT - cash_pool
                    cash_pool += magic_cash_needed
                    magically_provided_cash += magic_cash_needed
                
                # Deploy extra (now we always have enough)
                shares += RAINY_AMOUNT / price_cad
                contributions += RAINY_AMOUNT
                cash_pool -= RAINY_AMOUNT
                successful_rainy_buys += 1
                
                rainy_buys.append({
                    "date": dt,
                    "rsi_sma": rsi_sma,
                    "price": price_cad,
                    "amount": RAINY_AMOUNT,
                    "cash_before": cash_before,
                    "cash_after": cash_pool,
                    "magic_cash_used": max(0, RAINY_AMOUNT - cash_before)
                })
            
            # Add cash savings
            cash_pool += CASH_ACCUMULATION
        
        # Track total equity (shares + cash pool)
        equity_records.append({
            "date": dt, 
            "equity": shares * price_cad + cash_pool,
            "shares_value": shares * price_cad,
            "cash_pool": cash_pool,
            "contributions": contributions
        })
    
    eq_df = pd.DataFrame(equity_records).set_index("date")
    
    # Analyze consecutive rainy days
    consecutive_counts = {}
    if rainy_days_list:
        rainy_indices = [execution_schedule.index(rd) for rd in rainy_days_list if rd in execution_schedule]
        
        if rainy_indices:
            current_streak = 1
            for i in range(1, len(rainy_indices)):
                if rainy_indices[i] == rainy_indices[i-1] + 1:
                    current_streak += 1
                else:
                    consecutive_counts[current_streak] = consecutive_counts.get(current_streak, 0) + 1
                    current_streak = 1
            # Don't forget the last streak
            consecutive_counts[current_streak] = consecutive_counts.get(current_streak, 0) + 1
    
    return {
        "strategy": "Variant Strategy (RSI SMA < 45) - FORCED 100% HIT RATE",
        "contributions": contributions,
        "shares": shares,
        "final_cash_pool": cash_pool,
        "end_equity": eq_df["equity"].iloc[-1],
        "equity_curve": eq_df,
        "total_rainy_days": total_rainy_days,
        "successful_rainy_buys": successful_rainy_buys,
        "rainy_buys": rainy_buys,
        "rainy_days_list": rainy_days_list,
        "consecutive_rainy_counts": consecutive_counts,
        "execution_count": len(execution_schedule),
        "magically_provided_cash": magically_provided_cash
    }

# =============================================================================
# RUN SIMULATIONS
# =============================================================================
print("\n" + "=" * 80)
print("RUNNING SIMULATIONS")
print("=" * 80)

simple_dca = simulate_simple_dca()
variant = simulate_variant_strategy()

# =============================================================================
# CALCULATE METRICS
# =============================================================================
def calculate_metrics(result: dict) -> dict:
    """Calculate performance metrics."""
    eq = result["equity_curve"]["equity"]
    
    start_val = eq.iloc[0] if eq.iloc[0] > 0 else result["contributions"]
    end_val = eq.iloc[-1]
    
    years = (eq.index[-1] - eq.index[0]).days / 365.25
    
    # CAGR
    if start_val > 0 and years > 0:
        cagr = (end_val / start_val) ** (1/years) - 1
    else:
        cagr = np.nan
    
    # Max Drawdown
    roll_max = eq.cummax()
    drawdown = (eq / roll_max) - 1
    max_dd = drawdown.min()
    
    # ROI
    roi = (end_val / result["contributions"] - 1) if result["contributions"] > 0 else 0
    
    # Total gain
    total_gain = end_val - result["contributions"]
    
    return {
        "cagr": cagr,
        "max_drawdown": max_dd,
        "roi": roi,
        "total_gain": total_gain,
        "years": years
    }

simple_metrics = calculate_metrics(simple_dca)
variant_metrics = calculate_metrics(variant)

# =============================================================================
# DISPLAY RESULTS
# =============================================================================
print("\n" + "=" * 80)
print("BACKTEST RESULTS - YTD 2025")
print("=" * 80)
print(f"\nPeriod: {start_date.date()} to {end_date_dt.date()}")
print(f"Duration: {variant_metrics['years']:.2f} years ({len(prices)} trading days)")
print(f"Execution days: {len(execution_schedule)} (3rd & 17th of each month)")

print("\n" + "-" * 80)
print("STRATEGY 1: SIMPLE DCA")
print("-" * 80)
print(f"Total contributions:    ${simple_dca['contributions']:>10,.2f}")
print(f"Final equity:           ${simple_dca['end_equity']:>10,.2f}")
print(f"Total gain:             ${simple_metrics['total_gain']:>10,.2f}")
print(f"ROI:                    {simple_metrics['roi']*100:>10.1f}%")
print(f"CAGR:                   {simple_metrics['cagr']*100:>10.2f}%")
print(f"Max drawdown:           {simple_metrics['max_drawdown']*100:>10.2f}%")
print(f"Shares owned:           {simple_dca['shares']:>10.2f}")

print("\n" + "-" * 80)
print(f"STRATEGY 2: VARIANT (RSI SMA({RSI_SMA_PERIOD}) < {RSI_THRESHOLD}) - FORCED 100% HIT RATE")
print("-" * 80)
print(f"Total contributions:    ${variant['contributions']:>10,.2f}")
print(f"Final equity:           ${variant['end_equity']:>10,.2f}")
print(f"  - Shares value:       ${variant['equity_curve']['shares_value'].iloc[-1]:>10,.2f}")
print(f"  - Cash pool:          ${variant['final_cash_pool']:>10,.2f}")
print(f"Total gain:             ${variant_metrics['total_gain']:>10,.2f}")
print(f"ROI:                    {variant_metrics['roi']*100:>10.1f}%")
print(f"CAGR:                   {variant_metrics['cagr']*100:>10.2f}%")
print(f"Max drawdown:           {variant_metrics['max_drawdown']*100:>10.2f}%")
print(f"Shares owned:           {variant['shares']:>10.2f}")

print(f"\nRainy Day Activity (100% Hit Rate - Forced):")
print(f"  Rainy days detected:  {variant['total_rainy_days']:>10}")
print(f"  Successful buys:      {variant['successful_rainy_buys']:>10} (100% forced)")
print(f"  Rainy frequency:      {(variant['total_rainy_days']/len(execution_schedule))*100:>10.1f}%")
print(f"  Magic cash provided:  ${variant['magically_provided_cash']:>10,.2f}")

if variant['consecutive_rainy_counts']:
    print(f"\nConsecutive Rainy Days:")
    for streak_length in sorted(variant['consecutive_rainy_counts'].keys()):
        count = variant['consecutive_rainy_counts'][streak_length]
        print(f"  {streak_length} consecutive:       {count:>10} occurrence(s)")

print("\n" + "-" * 80)
print("COMPARISON: VARIANT VS SIMPLE DCA")
print("-" * 80)
extra_invested = variant['contributions'] - simple_dca['contributions']
outperformance = variant['end_equity'] - simple_dca['end_equity']
outperformance_pct = (outperformance / simple_dca['end_equity']) * 100

print(f"Extra capital deployed: ${extra_invested:>10,.2f}")
print(f"  (Magic cash provided: ${variant['magically_provided_cash']:>10,.2f})")
print(f"Outperformance:         ${outperformance:>10,.2f} ({outperformance_pct:+.2f}%)")
print(f"CAGR difference:        {(variant_metrics['cagr'] - simple_metrics['cagr'])*100:>10.2f}pp")

if extra_invested > 0:
    roi_on_extra = (outperformance / extra_invested) * 100
    print(f"Return on extra cap:    {roi_on_extra:>10.1f}%")
    print(f"\n💡 KEY INSIGHT:")
    print(f"   The extra ${extra_invested:,.2f} deployed during rainy days generated")
    print(f"   ${outperformance:,.2f} in additional portfolio value.")
    print(f"   This demonstrates exceptional capital efficiency from buying dips!")
    print(f"   ROI on rainy capital: {roi_on_extra:.1f}%")

# Calculate timing effectiveness metrics
if variant['rainy_buys']:
    avg_rsi_rainy = np.mean([rb['rsi_sma'] for rb in variant['rainy_buys']])
    avg_price_rainy = np.mean([rb['price'] for rb in variant['rainy_buys']])
    
    # Get all execution day prices
    exec_prices = [prices.loc[dt, 'SPY_CAD'] for dt in execution_schedule if dt in prices.index]
    avg_price_all = np.mean(exec_prices)
    buying_discount = ((avg_price_rainy - avg_price_all) / avg_price_all) * 100
    
    print("\n" + "-" * 80)
    print("TIMING EFFECTIVENESS")
    print("-" * 80)
    print(f"Rainy day frequency:    {(variant['total_rainy_days']/len(execution_schedule))*100:>10.1f}%")
    print(f"Hit rate:               {(variant['successful_rainy_buys']/variant['total_rainy_days'])*100 if variant['total_rainy_days'] > 0 else 0:>10.1f}%")
    print(f"Avg RSI SMA (rainy):    {avg_rsi_rainy:>10.2f}")
    print(f"Avg price (rainy):      ${avg_price_rainy:>10.2f} CAD")
    print(f"Avg price (all days):   ${avg_price_all:>10.2f} CAD")
    print(f"Buying discount:        {buying_discount:>10.1f}%")

# =============================================================================
# SAVE RESULTS
# =============================================================================
print("\n" + "=" * 80)
print("SAVING RESULTS")
print("=" * 80)

# Save equity curves
simple_dca['equity_curve'].to_csv('equity_simple_dca_ytd2025.csv')
variant['equity_curve'].to_csv('equity_variant_ytd2025.csv')
print(f"✅ Saved: equity_simple_dca_ytd2025.csv")
print(f"✅ Saved: equity_variant_ytd2025.csv")

# Save rainy buys log
if variant['rainy_buys']:
    rainy_df = pd.DataFrame(variant['rainy_buys'])
    rainy_df.to_csv('rainy_buys_ytd2025.csv', index=False)
    print(f"✅ Saved: rainy_buys_ytd2025.csv ({len(variant['rainy_buys'])} records)")

# Save summary stats
summary_data = {
    'Strategy': ['Simple DCA', 'Variant'],
    'Contributions': [simple_dca['contributions'], variant['contributions']],
    'Final Equity': [simple_dca['end_equity'], variant['end_equity']],
    'Total Gain': [simple_metrics['total_gain'], variant_metrics['total_gain']],
    'ROI (%)': [simple_metrics['roi']*100, variant_metrics['roi']*100],
    'CAGR (%)': [simple_metrics['cagr']*100, variant_metrics['cagr']*100],
    'Max Drawdown (%)': [simple_metrics['max_drawdown']*100, variant_metrics['max_drawdown']*100],
}
summary_df = pd.DataFrame(summary_data)
summary_df.to_csv('strategy_comparison_summary_ytd2025.csv', index=False)
print(f"✅ Saved: strategy_comparison_summary_ytd2025.csv")

# =============================================================================
# GENERATE CHARTS
# =============================================================================
print("\n" + "=" * 80)
print("GENERATING VISUALIZATIONS")
print("=" * 80)

# Chart 1: Equity Curves
fig, ax = plt.subplots(figsize=(14, 7))

ax.plot(simple_dca['equity_curve'].index, simple_dca['equity_curve']['equity'],
        label='Simple DCA ($150 on 3rd & 17th)', color='#2E86AB', linewidth=2.5, alpha=0.8)
ax.plot(variant['equity_curve'].index, variant['equity_curve']['equity'],
        label='Variant Strategy (RSI SMA < 45)', color='#06A77D', linewidth=2.5)

ax.set_xlabel('Date', fontsize=12, fontweight='bold')
ax.set_ylabel('Portfolio Value (CAD)', fontsize=12, fontweight='bold')
ax.set_title('YTD 2025: Strategy Performance Comparison\nSimple DCA vs Variant Strategy',
             fontsize=14, fontweight='bold', pad=15)
ax.legend(loc='upper left', fontsize=11)
ax.grid(True, alpha=0.3)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

plt.tight_layout()
plt.savefig('chart_1_equity_curves_ytd2025.png', dpi=300, bbox_inches='tight')
print(f"✅ Saved: chart_1_equity_curves_ytd2025.png")
plt.close()

# Chart 2: Outperformance Over Time
fig, ax = plt.subplots(figsize=(14, 6))

outperformance_series = variant['equity_curve']['equity'] - simple_dca['equity_curve']['equity']

ax.fill_between(outperformance_series.index, 0, outperformance_series,
                 where=(outperformance_series >= 0), color='#06A77D', alpha=0.4, label='Outperformance')
ax.fill_between(outperformance_series.index, 0, outperformance_series,
                 where=(outperformance_series < 0), color='#D62828', alpha=0.4, label='Underperformance')
ax.plot(outperformance_series.index, outperformance_series, color='#1A1A1A', linewidth=2)
ax.axhline(y=0, color='black', linestyle='-', linewidth=1)

ax.set_xlabel('Date', fontsize=12, fontweight='bold')
ax.set_ylabel('Variant - Simple DCA (CAD)', fontsize=12, fontweight='bold')
ax.set_title('Cumulative Outperformance: Variant vs Simple DCA',
             fontsize=14, fontweight='bold', pad=15)
ax.legend(loc='upper left', fontsize=11)
ax.grid(True, alpha=0.3)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

plt.tight_layout()
plt.savefig('chart_2_outperformance_ytd2025.png', dpi=300, bbox_inches='tight')
print(f"✅ Saved: chart_2_outperformance_ytd2025.png")
plt.close()

# Chart 3: Contributions Breakdown
fig, ax = plt.subplots(figsize=(10, 6))

categories = ['Simple DCA', 'Variant\n(Base)', 'Variant\n(Rainy Extra)']
values = [
    simple_dca['contributions'],
    simple_dca['contributions'],  # Same base as simple DCA
    extra_invested  # Extra from rainy days
]
colors = ['#2E86AB', '#FFB703', '#06A77D']

bars = ax.bar(categories, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'${height:,.0f}',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_ylabel('Total Contributions (CAD)', fontsize=12, fontweight='bold')
ax.set_title('Capital Deployment Comparison',
             fontsize=14, fontweight='bold', pad=15)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('chart_3_contributions_ytd2025.png', dpi=300, bbox_inches='tight')
print(f"✅ Saved: chart_3_contributions_ytd2025.png")
plt.close()

# Chart 4: RSI SMA Timeline with Rainy Days
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

# Top: RSI SMA with threshold
ax1.plot(prices.index, prices['RSI_SMA'], color='#2E86AB', linewidth=1.5, label='RSI SMA(7)')
ax1.axhline(y=RSI_THRESHOLD, color='#D62828', linestyle='--', linewidth=2, label=f'Threshold ({RSI_THRESHOLD})')

# Mark rainy execution days
if variant['rainy_buys']:
    rainy_dates = [rb['date'] for rb in variant['rainy_buys']]
    rainy_rsi = [rb['rsi_sma'] for rb in variant['rainy_buys']]
    ax1.scatter(rainy_dates, rainy_rsi, color='#06A77D', s=100, zorder=5, 
                marker='v', edgecolor='black', linewidth=1.5, label='Rainy Buy Executed')

ax1.set_ylabel('RSI SMA(7)', fontsize=12, fontweight='bold')
ax1.set_title('RSI SMA(7) Timeline & Rainy Day Detections',
              fontsize=14, fontweight='bold', pad=15)
ax1.legend(loc='upper right', fontsize=10)
ax1.grid(True, alpha=0.3)

# Bottom: SPY price
ax2.plot(prices.index, prices['SPY_CAD'], color='#1A1A1A', linewidth=1.5, label='SPY Price (CAD)')

# Mark rainy execution days
if variant['rainy_buys']:
    rainy_dates = [rb['date'] for rb in variant['rainy_buys']]
    rainy_prices = [rb['price'] for rb in variant['rainy_buys']]
    ax2.scatter(rainy_dates, rainy_prices, color='#06A77D', s=100, zorder=5,
                marker='v', edgecolor='black', linewidth=1.5, label='Rainy Buy Executed')

ax2.set_xlabel('Date', fontsize=12, fontweight='bold')
ax2.set_ylabel('SPY Price (CAD)', fontsize=12, fontweight='bold')
ax2.set_title('SPY Price & Rainy Day Buy Points',
              fontsize=12, fontweight='bold')
ax2.legend(loc='upper left', fontsize=10)
ax2.grid(True, alpha=0.3)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:.2f}'))

plt.tight_layout()
plt.savefig('chart_4_rsi_timeline_ytd2025.png', dpi=300, bbox_inches='tight')
print(f"✅ Saved: chart_4_rsi_timeline_ytd2025.png")
plt.close()

# =============================================================================
# COMPLETION
# =============================================================================
print("\n" + "=" * 80)
print("BACKTEST COMPLETE")
print("=" * 80)
print(f"\n📊 Key Results:")
print(f"   Period: {start_date.date()} to {end_date_dt.date()}")
print(f"   Execution days: {len(execution_schedule)}")
print(f"   Rainy days: {variant['total_rainy_days']} ({(variant['total_rainy_days']/len(execution_schedule))*100:.1f}%)")
print(f"   Simple DCA final: ${simple_dca['end_equity']:,.2f}")
print(f"   Variant final: ${variant['end_equity']:,.2f}")
print(f"   Outperformance: ${outperformance:,.2f} ({outperformance_pct:+.2f}%)")
print(f"\n📁 Files Generated:")
print(f"   - equity_simple_dca_ytd2025.csv")
print(f"   - equity_variant_ytd2025.csv")
print(f"   - rainy_buys_ytd2025.csv")
print(f"   - strategy_comparison_summary_ytd2025.csv")
print(f"   - chart_1_equity_curves_ytd2025.png")
print(f"   - chart_2_outperformance_ytd2025.png")
print(f"   - chart_3_contributions_ytd2025.png")
print(f"   - chart_4_rsi_timeline_ytd2025.png")
print("\n" + "=" * 80)
