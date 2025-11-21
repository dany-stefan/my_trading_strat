"""
RSI Cash Strategy Parameter Optimization (SPY CAD Backtest Since 2000)
======================================================================

WHAT THIS DOES
- Tests multiple RSI Cash Strategy variants with different parameters:
  * Cadence: bi-weekly vs weekly Monday buys
  * Rainy buy amounts: $50, $100, $150
  * RSI thresholds: 50, 45, 40, 35
- All variants use:
  * $150 base bi-weekly investment (always)
  * $30 bi-weekly cash savings (always)
  * Extra buy from cash pool on rainy Mondays (RSI < threshold)
- Filters variants by hit rate (target 75% ± 10%)
- Compares final returns to find optimal parameters
"""

from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from itertools import product

# =============================================================================
# PARAMETERS
# =============================================================================
START_DATE = "2000-01-01"
INDEX_TICKER = "SPY"
FX_TICKER = "CADUSD=X"
DCA_BASE_AMOUNT = 150.0        # Regular bi-weekly contribution (CAD)
CASH_ACCUMULATION = 30.0       # Cash saved every 2 weeks
INITIAL_LUMP_SUM = 1000.0      # Initial investment at first trading day
RSI_PERIOD = 14

# Parameter grid for RSI Cash Strategy variants
CADENCES = ["biweekly", "weekly"]
RAINY_AMOUNTS = [50.0, 100.0, 150.0]
RSI_THRESHOLDS = [50, 45, 40, 35]
TARGET_HIT_RATE = 0.75  # 75%
HIT_RATE_TOLERANCE = 0.10  # ±10%

# =============================================================================
# DATA FETCH
# =============================================================================
print("=" * 80)
print("RSI CASH STRATEGY PARAMETER OPTIMIZATION (SPY in CAD)")
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
# INDICATORS (RSI on SPY USD)
# =============================================================================
print("Computing RSI(14) on SPY...")

def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

prices["RSI"] = compute_rsi(prices[INDEX_TICKER], RSI_PERIOD)
prices = prices.dropna(subset=["RSI"])

start_date = prices.index[0]
end_date_dt = prices.index[-1]
print(f"Data range: {start_date.date()} to {end_date_dt.date()} ({len(prices)} trading days)")

# =============================================================================
# SCHEDULES (bi-weekly and weekly Mondays)
# =============================================================================
print("Building buy schedules...")

def next_trading_day_on_or_after(dt: pd.Timestamp) -> pd.Timestamp:
    if dt in prices.index:
        return dt
    idx = prices.index.get_indexer([dt], method="backfill")[0]
    if idx == -1:
        return prices.index[-1]
    return prices.index[idx]

# Bi-weekly Mondays (for base investment + cash savings)
biweekly_schedule = []
current = start_date
days_until_monday = (7 - current.weekday()) % 7
if days_until_monday > 0:
    current = current + timedelta(days=days_until_monday)
while current <= end_date_dt:
    biweekly_schedule.append(next_trading_day_on_or_after(current))
    current += timedelta(weeks=2)
biweekly_schedule = sorted(pd.unique(biweekly_schedule))
biweekly_set = set(biweekly_schedule)

# Weekly Mondays (all Mondays for weekly rainy buy opportunities)
weekly_schedule = [d for d in prices.index if d.weekday() == 0]
weekly_set = set(weekly_schedule)

print(f"Bi-weekly Mondays (payday): {len(biweekly_schedule)}")
print(f"Weekly Mondays (all): {len(weekly_schedule)}")

# =============================================================================
# BASELINE DCA SIMULATION (No Rainy Days)
# =============================================================================
def simulate_baseline_dca():
    """
    Simulate simple bi-weekly DCA with no rainy day strategy.
    Just $150 every bi-weekly Monday, no cash accumulation or rainy buys.
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
        
        # Bi-weekly payday: base investment only (no cash savings, no rainy buys)
        if dt in biweekly_set:
            if price_cad > 0:
                shares += DCA_BASE_AMOUNT / price_cad
                contributions += DCA_BASE_AMOUNT
        
        # Track equity (shares only, no cash pool)
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
        "strategy": "Baseline DCA",
        "contributions": contributions,
        "end_equity": end_val,
        "cagr": cagr,
        "max_drawdown": max_dd,
        "equity_curve": eq_df,
        "years": years
    }

# =============================================================================
# RSI VARIANT SIMULATION FUNCTION
# =============================================================================
def simulate_variant(cadence: str, rainy_amount: float, rsi_threshold: float):
    """
    Simulate one RSI Cash Strategy variant.
    
    Returns:
        dict with metrics: contributions, end_equity, cagr, max_dd, hit_rate, rainy_count, etc.
    """
    shares = 0.0
    cost = 0.0
    cash_pool = 0.0
    contributions = INITIAL_LUMP_SUM
    
    # Initial lump sum
    first_price = prices.loc[start_date, "SPY_CAD"]
    if first_price > 0:
        shares = INITIAL_LUMP_SUM / first_price
        cost = INITIAL_LUMP_SUM
    
    equity_records = []
    rainy_hits = 0
    rainy_misses = 0
    rainy_total = 0
    
    # Determine which schedule to use for rainy buy opportunities
    rainy_schedule = weekly_set if cadence == "weekly" else biweekly_set
    
    for dt, row in prices.iterrows():
        price_cad = row["SPY_CAD"]
        rsi_val = row["RSI"]
        
        # Bi-weekly payday: base investment + cash savings (ALWAYS bi-weekly)
        if dt in biweekly_set:
            if price_cad > 0:
                # Base $150 investment
                shares += DCA_BASE_AMOUNT / price_cad
                cost += DCA_BASE_AMOUNT
                contributions += DCA_BASE_AMOUNT
                
                # Save $30 to cash pool
                cash_pool += CASH_ACCUMULATION
        
        # Rainy Monday opportunity (cadence-dependent)
        if dt in rainy_schedule:
            if pd.notna(rsi_val) and rsi_val < rsi_threshold:
                rainy_total += 1
                
                # Try to deploy extra cash
                if cash_pool >= rainy_amount:
                    shares += rainy_amount / price_cad
                    cost += rainy_amount
                    contributions += rainy_amount
                    cash_pool -= rainy_amount
                    rainy_hits += 1
                else:
                    rainy_misses += 1
        
        # Track equity (shares + cash pool)
        equity_records.append({"date": dt, "equity": shares * price_cad + cash_pool})
    
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
    
    hit_rate = (rainy_hits / rainy_total) if rainy_total > 0 else 0.0
    
    return {
        "cadence": cadence,
        "rainy_amount": rainy_amount,
        "rsi_threshold": rsi_threshold,
        "contributions": contributions,
        "end_equity": end_val,
        "cagr": cagr,
        "max_drawdown": max_dd,
        "rainy_total": rainy_total,
        "rainy_hits": rainy_hits,
        "rainy_misses": rainy_misses,
        "hit_rate": hit_rate,
        "equity_curve": eq_df,
        "years": years
    }

# =============================================================================
# PARAMETER SWEEP
# =============================================================================
print("\n" + "=" * 80)
print("RUNNING PARAMETER SWEEP")
print("=" * 80)

# First, simulate baseline DCA
print("\n--- Baseline DCA (No Rainy Strategy) ---")
baseline = simulate_baseline_dca()
print(f"Baseline DCA: CAGR={baseline['cagr']*100:.2f}%, End=${baseline['end_equity']:,.0f}, Invested=${baseline['contributions']:,.0f}")

results = []
total_variants = len(CADENCES) * len(RAINY_AMOUNTS) * len(RSI_THRESHOLDS)
print(f"\n--- Testing {total_variants} RSI Strategy Variants ---")

for i, (cadence, rainy_amt, rsi_thresh) in enumerate(product(CADENCES, RAINY_AMOUNTS, RSI_THRESHOLDS), 1):
    print(f"[{i}/{total_variants}] {cadence}, ${int(rainy_amt)}, RSI<{rsi_thresh}...", end=" ")
    result = simulate_variant(cadence, rainy_amt, rsi_thresh)
    results.append(result)
    print(f"CAGR={result['cagr']*100:.2f}%, Hit={result['hit_rate']*100:.1f}%")

# =============================================================================
# FILTER BY HIT RATE
# =============================================================================
print("\n" + "=" * 80)
print("FILTERING BY HIT RATE (75% ± 10%)")
print("=" * 80)

min_hit = TARGET_HIT_RATE - HIT_RATE_TOLERANCE
max_hit = TARGET_HIT_RATE + HIT_RATE_TOLERANCE

filtered_results = [
    r for r in results 
    if min_hit <= r['hit_rate'] <= max_hit
]

print(f"Variants within target hit rate: {len(filtered_results)} / {total_variants}")

if not filtered_results:
    print("WARNING: No variants meet hit rate criteria. Showing all results.")
    filtered_results = results

# Sort by CAGR (descending)
filtered_results.sort(key=lambda x: x['cagr'], reverse=True)

# =============================================================================
# DISPLAY RESULTS
# =============================================================================
print("\n" + "=" * 80)
print("TOP VARIANTS (sorted by CAGR)")
print("=" * 80)
print(f"{'Rank':<6} {'Cadence':<10} {'Amount':<8} {'RSI<':<6} {'CAGR':<8} {'Hit%':<8} {'Rainy':<8} {'End Equity':<12} {'Contrib':<12}")
print("-" * 80)

for rank, r in enumerate(filtered_results[:15], 1):  # Top 15
    print(f"{rank:<6} {r['cadence']:<10} ${r['rainy_amount']:<7.0f} {r['rsi_threshold']:<6} "
          f"{r['cagr']*100:>6.2f}% {r['hit_rate']*100:>6.1f}% {r['rainy_hits']:<8} "
          f"${r['end_equity']:>11,.0f} ${r['contributions']:>11,.0f}")

# =============================================================================
# EXPORT RESULTS
# =============================================================================
out_dir = Path(__file__).resolve().parent

# Summary CSV
summary_df = pd.DataFrame([
    {
        "rank": rank,
        "cadence": r["cadence"],
        "rainy_amount": r["rainy_amount"],
        "rsi_threshold": r["rsi_threshold"],
        "contributions_cad": r["contributions"],
        "end_equity_cad": r["end_equity"],
        "cagr": r["cagr"],
        "max_drawdown": r["max_drawdown"],
        "hit_rate": r["hit_rate"],
        "rainy_total": r["rainy_total"],
        "rainy_hits": r["rainy_hits"],
        "rainy_misses": r["rainy_misses"],
        "years": r["years"]
    }
    for rank, r in enumerate(filtered_results, 1)
])
summary_df.to_csv(out_dir / "rsi_variants_summary.csv", index=False)
print(f"\nExported: rsi_variants_summary.csv")

# Export baseline equity curve
baseline["equity_curve"].to_csv(out_dir / "equity_baseline_dca.csv")
print(f"Exported: equity_baseline_dca.csv")

# Export top 3 equity curves (focus on your chosen variants)
for rank, r in enumerate(filtered_results[:3], 1):
    filename = f"equity_variant_{rank}_{r['cadence']}_{int(r['rainy_amount'])}_{r['rsi_threshold']}.csv"
    r["equity_curve"].to_csv(out_dir / filename)
    print(f"Exported: {filename}")

# =============================================================================
# VISUALIZATION 1 - SPY Price with Rainy Periods
# =============================================================================
print("\nGenerating SPY price chart with rainy periods...")

# Identify rainy periods (RSI < 45) with consecutive period lengths
rainy_45 = prices[prices['RSI'] < 45].copy()
rainy_periods = []
if not rainy_45.empty:
    period_start = None
    period_end = None
    
    for i, dt in enumerate(rainy_45.index):
        if period_start is None:
            period_start = dt
            period_end = dt
        else:
            # Check if consecutive (within 5 trading days to account for weekends)
            if (dt - period_end).days <= 5:
                period_end = dt
            else:
                # Save previous period
                period_length = len(rainy_45[(rainy_45.index >= period_start) & (rainy_45.index <= period_end)])
                rainy_periods.append({
                    'start': period_start,
                    'end': period_end,
                    'length': period_length
                })
                period_start = dt
                period_end = dt
    
    # Don't forget the last period
    if period_start is not None:
        period_length = len(rainy_45[(rainy_45.index >= period_start) & (rainy_45.index <= period_end)])
        rainy_periods.append({
            'start': period_start,
            'end': period_end,
            'length': period_length
        })

# Create SPY drawdown
spy_peak = prices[INDEX_TICKER].cummax()
spy_drawdown = ((prices[INDEX_TICKER] / spy_peak) - 1) * 100

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(18, 10), sharex=True, 
                                gridspec_kw={'height_ratios': [3, 1]})

# Top panel: SPY Price with rainy periods
ax1.plot(prices.index, prices[INDEX_TICKER], color='#1f77b4', linewidth=1.5, label='SPY Price (USD)')
ax1.fill_between(prices.index, 0, prices[INDEX_TICKER], alpha=0.1, color='#1f77b4')

# Highlight rainy periods
for period in rainy_periods:
    ax1.axvspan(period['start'], period['end'], alpha=0.2, color='red', 
                label='Rainy Period (RSI < 45)' if period == rainy_periods[0] else '')

ax1.set_ylabel('SPY Price (USD)', fontsize=12, fontweight='bold')
ax1.set_title('SPY Price History with Rainy Periods (RSI < 45)', fontsize=14, fontweight='bold', pad=15)
ax1.grid(alpha=0.3, linestyle='--')
ax1.legend(loc='upper left', fontsize=10)
ax1.set_yscale('log')

# Bottom panel: Drawdown
ax2.fill_between(prices.index, spy_drawdown, 0, where=(spy_drawdown < 0), 
                 color='#d62728', alpha=0.4, label='Drawdown')
ax2.plot(prices.index, spy_drawdown, color='#d62728', linewidth=1, alpha=0.8)
ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax2.set_ylabel('Drawdown (%)', fontsize=12, fontweight='bold')
ax2.set_xlabel('Date', fontsize=12, fontweight='bold')
ax2.grid(alpha=0.3, linestyle='--')
ax2.legend(loc='lower left', fontsize=10)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

plt.tight_layout()
plt.savefig(out_dir / "spy_price_rainy_periods_drawdown.png", dpi=150, bbox_inches='tight')
plt.close()
print("Exported: spy_price_rainy_periods_drawdown.png")

# =============================================================================
# VISUALIZATION 2 - RSI Chart with Threshold Lines
# =============================================================================
print("\nGenerating RSI chart...")

fig, ax = plt.subplots(figsize=(18, 6))
ax.plot(prices.index, prices['RSI'], color='#2ca02c', linewidth=1, alpha=0.8, label='RSI(14)')

# Threshold lines
ax.axhline(y=50, color='orange', linestyle='--', linewidth=1.5, alpha=0.7, label='RSI < 50')
ax.axhline(y=45, color='red', linestyle='--', linewidth=2, alpha=0.7, label='RSI < 45 (Your Threshold)')
ax.axhline(y=40, color='darkred', linestyle='--', linewidth=1.5, alpha=0.7, label='RSI < 40')
ax.axhline(y=35, color='purple', linestyle='--', linewidth=1.5, alpha=0.7, label='RSI < 35')
ax.axhline(y=30, color='black', linestyle=':', linewidth=1, alpha=0.5, label='Oversold (30)')

# Fill rainy zones
ax.fill_between(prices.index, 0, 45, alpha=0.1, color='red', label='Rainy Zone (< 45)')

ax.set_ylabel('RSI(14)', fontsize=12, fontweight='bold')
ax.set_xlabel('Date', fontsize=12, fontweight='bold')
ax.set_title('RSI(14) History with Threshold Levels', fontsize=14, fontweight='bold', pad=15)
ax.set_ylim(0, 100)
ax.grid(alpha=0.3, linestyle='--')
ax.legend(loc='upper right', fontsize=9, ncol=2)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

plt.tight_layout()
plt.savefig(out_dir / "rsi_history_thresholds.png", dpi=150, bbox_inches='tight')
plt.close()
print("Exported: rsi_history_thresholds.png")

# =============================================================================
# VISUALIZATION 2.5 - Rainy Day Analysis (Hit/Miss with SPY Drawdown)
# =============================================================================
print("\nGenerating rainy day buy analysis chart...")

# Get your chosen variant (#2) for detailed analysis
your_variant = filtered_results[1]  # Index 1 = Rank #2
variant_cadence = your_variant['cadence']
variant_rsi_threshold = your_variant['rsi_threshold']
variant_rainy_amount = your_variant['rainy_amount']

# Re-simulate to track individual rainy day events
rainy_schedule = weekly_set if variant_cadence == "weekly" else biweekly_set
cash_pool = 0.0
rainy_events = []

for dt in biweekly_set:
    cash_pool += CASH_ACCUMULATION  # Save $30 every payday
    
    if dt in rainy_schedule:
        if dt in prices.index:
            rsi_val = prices.loc[dt, 'RSI']
            spy_price = prices.loc[dt, INDEX_TICKER]
            
            if pd.notna(rsi_val) and rsi_val < variant_rsi_threshold:
                # Rainy day detected
                hit = cash_pool >= variant_rainy_amount
                amount_deployed = variant_rainy_amount if hit else 0
                
                if hit:
                    cash_pool -= variant_rainy_amount
                
                # Determine RSI band
                if rsi_val < 30:
                    band = "Extreme (<30)"
                elif rsi_val < 35:
                    band = "Very Low (30-35)"
                elif rsi_val < 40:
                    band = "Low (35-40)"
                else:
                    band = "Moderate (40-45)"
                
                rainy_events.append({
                    'date': dt,
                    'rsi': rsi_val,
                    'spy_price': spy_price,
                    'hit': hit,
                    'amount': amount_deployed,
                    'band': band,
                    'cash_pool': cash_pool
                })

# Create DataFrame
rainy_df = pd.DataFrame(rainy_events)

# Calculate cumulative extra buying
rainy_df['cumulative_extra'] = rainy_df['amount'].cumsum()

# Get SPY drawdown for rainy dates
rainy_df['spy_drawdown'] = rainy_df['date'].apply(lambda d: spy_drawdown.loc[d] if d in spy_drawdown.index else 0)

# Create figure with 3 subplots
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(18, 14), sharex=True,
                                     gridspec_kw={'height_ratios': [2, 1, 1]})

# Top panel: SPY Price with Hit/Miss markers colored by RSI band
ax1_twin = ax1.twinx()
ax1.plot(prices.index, prices[INDEX_TICKER], color='#1f77b4', linewidth=1.5, label='SPY Price', alpha=0.6)

# Plot rainy day markers
band_colors = {
    "Extreme (<30)": '#8B0000',      # Dark red
    "Very Low (30-35)": '#DC143C',   # Crimson
    "Low (35-40)": '#FF6347',        # Tomato
    "Moderate (40-45)": '#FFA500'    # Orange
}

for band in band_colors.keys():
    band_data = rainy_df[rainy_df['band'] == band]
    hits = band_data[band_data['hit']]
    misses = band_data[~band_data['hit']]
    
    if not hits.empty:
        ax1_twin.scatter(hits['date'], hits['rsi'], c=band_colors[band], 
                        marker='o', s=100, edgecolors='black', linewidths=1.5,
                        label=f'{band} (Hit)', zorder=5, alpha=0.8)
    
    if not misses.empty:
        ax1_twin.scatter(misses['date'], misses['rsi'], c=band_colors[band], 
                        marker='x', s=100, linewidths=2,
                        label=f'{band} (Miss)', zorder=5, alpha=0.8)

ax1.set_ylabel('SPY Price (USD)', fontsize=12, fontweight='bold', color='#1f77b4')
ax1_twin.set_ylabel('RSI Level', fontsize=12, fontweight='bold')
ax1_twin.set_ylim(0, 50)
ax1_twin.axhline(y=variant_rsi_threshold, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label=f'Your Threshold ({variant_rsi_threshold})')
ax1.set_title(f'Rainy Day Buy Opportunities: Variant #2 (Bi-weekly ${int(variant_rainy_amount)} RSI<{variant_rsi_threshold})', 
             fontsize=14, fontweight='bold', pad=15)
ax1.grid(alpha=0.3, linestyle='--')
ax1.set_yscale('log')
ax1.tick_params(axis='y', labelcolor='#1f77b4')

# Combine legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax1_twin.get_legend_handles_labels()
ax1_twin.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=8, ncol=2)

# Middle panel: SPY Drawdown with rainy day markers
ax2.fill_between(prices.index, spy_drawdown, 0, where=(spy_drawdown < 0), 
                 color='#d62728', alpha=0.3, label='Drawdown')
ax2.plot(prices.index, spy_drawdown, color='#d62728', linewidth=1, alpha=0.8)

# Mark rainy day buys on drawdown chart
hits_only = rainy_df[rainy_df['hit']]
ax2.scatter(hits_only['date'], hits_only['spy_drawdown'], c='green', 
           marker='^', s=80, edgecolors='black', linewidths=1,
           label=f'Successful Buy (n={len(hits_only)})', zorder=5)

ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax2.set_ylabel('SPY Drawdown (%)', fontsize=12, fontweight='bold')
ax2.grid(alpha=0.3, linestyle='--')
ax2.legend(loc='lower left', fontsize=10)

# Bottom panel: Cumulative extra buying power deployed
ax3.plot(rainy_df['date'], rainy_df['cumulative_extra'], color='#2ca02c', 
        linewidth=2.5, label='Cumulative Extra Capital Deployed')
ax3.fill_between(rainy_df['date'], 0, rainy_df['cumulative_extra'], 
                 alpha=0.3, color='#2ca02c')

ax3.set_ylabel('Cumulative Extra\nBuying ($CAD)', fontsize=12, fontweight='bold')
ax3.set_xlabel('Date', fontsize=12, fontweight='bold')
ax3.grid(alpha=0.3, linestyle='--')
ax3.legend(loc='upper left', fontsize=10)
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

plt.tight_layout()
plt.savefig(out_dir / "rainy_day_analysis_detailed.png", dpi=150, bbox_inches='tight')
plt.close()
print("Exported: rainy_day_analysis_detailed.png")

# Print rainy day statistics by band
print("\nRainy Day Statistics by RSI Band:")
for band in ["Extreme (<30)", "Very Low (30-35)", "Low (35-40)", "Moderate (40-45)"]:
    band_data = rainy_df[rainy_df['band'] == band]
    if not band_data.empty:
        hits = band_data[band_data['hit']].shape[0]
        total = band_data.shape[0]
        total_deployed = band_data['amount'].sum()
        avg_drawdown = band_data['spy_drawdown'].mean()
        print(f"  {band}: {hits}/{total} hit ({hits/total*100:.1f}%), ${total_deployed:,.0f} deployed, avg DD: {avg_drawdown:.1f}%")

# =============================================================================
# VISUALIZATION 3 - Top 3 Variants vs Baseline DCA
# =============================================================================
print("\nGenerating comparison chart with baseline DCA...")
fig, ax = plt.subplots(figsize=(16, 8))

# Plot baseline first (gray, dashed)
ax.plot(baseline["equity_curve"].index, baseline["equity_curve"]["equity"], 
        label=f"Baseline DCA (No Rainy): {baseline['cagr']*100:.2f}% CAGR", 
        linewidth=2.5, color='gray', linestyle='--', alpha=0.7)

# Plot only your chosen variant #2
your_variant = filtered_results[1]  # Rank #2
eq_df = your_variant["equity_curve"]
label = f"#2 Bi-weekly $150 RSI<45 (YOUR CHOICE): {your_variant['cagr']*100:.2f}% CAGR"
ax.plot(eq_df.index, eq_df["equity"], label=label, linewidth=3, color='#1f77b4')

ax.set_title("Your RSI Cash Strategy vs Simple DCA Baseline", 
             fontsize=14, fontweight='bold', pad=15)
ax.set_ylabel("Portfolio Value (CAD)", fontsize=12, fontweight='bold')
ax.set_xlabel("Date", fontsize=12, fontweight='bold')
ax.grid(alpha=0.3)
ax.legend(loc='upper left', fontsize=11)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.tight_layout()
plt.savefig(out_dir / "strategy_comparison_with_baseline.png", dpi=150)
plt.close()
print("Exported: strategy_comparison_with_baseline.png")

# =============================================================================
# VISUALIZATION 4 - Variant #2 Only (Detailed View)
# =============================================================================
print("\nGenerating variant #2 detailed equity chart...")
fig, ax = plt.subplots(figsize=(16, 8))

# Plot your variant #2 only
your_variant = filtered_results[1]  # Rank #2
eq_df = your_variant["equity_curve"]
ax.plot(eq_df.index, eq_df["equity"], label=f"Bi-weekly $150 RSI<45: {your_variant['cagr']*100:.2f}% CAGR", 
        linewidth=2.5, color='#1f77b4')
ax.fill_between(eq_df.index, 0, eq_df["equity"], alpha=0.2, color='#1f77b4')

ax.set_title("Your Strategy: Bi-weekly $150 with RSI < 45 Rainy Day Buying", 
             fontsize=14, fontweight='bold', pad=15)
ax.set_ylabel("Portfolio Value (CAD)", fontsize=12, fontweight='bold')
ax.set_xlabel("Date", fontsize=12, fontweight='bold')
ax.grid(alpha=0.3)
ax.legend(loc='upper left', fontsize=11)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# Add annotations for major milestones
milestones = [
    (pd.Timestamp('2009-03-09'), 'Financial Crisis Bottom'),
    (pd.Timestamp('2020-03-23'), 'COVID-19 Bottom'),
]
for date, label in milestones:
    if date in eq_df.index:
        value = eq_df.loc[date, 'equity']
        ax.annotate(label, xy=(date, value), xytext=(10, 20), 
                   textcoords='offset points', fontsize=9,
                   arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

plt.tight_layout()
plt.savefig(out_dir / "variant_2_equity_curve.png", dpi=150)
plt.close()
print("Exported: variant_2_equity_curve.png")

# =============================================================================
# HEATMAP - CAGR by Amount and Threshold (bi-weekly only - your chosen cadence)
# =============================================================================
print("\nGenerating bi-weekly parameter heatmap...")

# Only show bi-weekly since that's your chosen cadence
cadence = 'biweekly'
cadence_results = [r for r in results if r['cadence'] == cadence]

# Create pivot table
heatmap_data = []
for r in cadence_results:
    heatmap_data.append({
        'rainy_amount': r['rainy_amount'],
        'rsi_threshold': r['rsi_threshold'],
        'cagr': r['cagr'] * 100,
        'hit_rate': r['hit_rate'] * 100
    })
df_heat = pd.DataFrame(heatmap_data)

# CAGR heatmap
pivot_cagr = df_heat.pivot(index='rainy_amount', columns='rsi_threshold', values='cagr')
pivot_hit = df_heat.pivot(index='rainy_amount', columns='rsi_threshold', values='hit_rate')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# CAGR
im1 = ax1.imshow(pivot_cagr.values, cmap='RdYlGn', aspect='auto')
ax1.set_xticks(range(len(pivot_cagr.columns)))
ax1.set_xticklabels([f"<{int(x)}" for x in pivot_cagr.columns])
ax1.set_yticks(range(len(pivot_cagr.index)))
ax1.set_yticklabels([f"${int(x)}" for x in pivot_cagr.index])
ax1.set_xlabel('RSI Threshold', fontweight='bold')
ax1.set_ylabel('Rainy Amount', fontweight='bold')
ax1.set_title(f'CAGR (%) - {cadence.title()} Cadence', fontweight='bold')

# Annotate values with highlight for your choice (150, 45)
for i in range(len(pivot_cagr.index)):
    for j in range(len(pivot_cagr.columns)):
        is_your_choice = (pivot_cagr.index[i] == 150 and pivot_cagr.columns[j] == 45)
        bbox = dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.8) if is_your_choice else None
        text = ax1.text(j, i, f'{pivot_cagr.values[i, j]:.1f}%',
                       ha="center", va="center", color="black", fontsize=9, fontweight='bold',
                       bbox=bbox)

plt.colorbar(im1, ax=ax1, label='CAGR (%)')

# Hit Rate
im2 = ax2.imshow(pivot_hit.values, cmap='Blues', aspect='auto', vmin=0, vmax=100)
ax2.set_xticks(range(len(pivot_hit.columns)))
ax2.set_xticklabels([f"<{int(x)}" for x in pivot_hit.columns])
ax2.set_yticks(range(len(pivot_hit.index)))
ax2.set_yticklabels([f"${int(x)}" for x in pivot_hit.index])
ax2.set_xlabel('RSI Threshold', fontweight='bold')
ax2.set_ylabel('Rainy Amount', fontweight='bold')
ax2.set_title(f'Hit Rate (%) - {cadence.title()} Cadence', fontweight='bold')

# Annotate values + highlight target zone and your choice
for i in range(len(pivot_hit.index)):
    for j in range(len(pivot_hit.columns)):
        val = pivot_hit.values[i, j]
        is_your_choice = (pivot_hit.index[i] == 150 and pivot_hit.columns[j] == 45)
        color = "white" if 65 <= val <= 85 else "black"
        weight = 'bold' if 65 <= val <= 85 else 'normal'
        bbox = dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.8) if is_your_choice else None
        text = ax2.text(j, i, f'{val:.1f}%',
                       ha="center", va="center", color=color, fontsize=9, fontweight=weight,
                       bbox=bbox)

plt.colorbar(im2, ax=ax2, label='Hit Rate (%)')

plt.tight_layout()
plt.savefig(out_dir / f"rsi_variants_heatmap_{cadence}.png", dpi=150)
plt.close()
print(f"Exported: rsi_variants_heatmap_{cadence}.png")

# =============================================================================
# FINAL REPORT
# =============================================================================
print("\n" + "=" * 80)
print("OPTIMIZATION COMPLETE")
print("=" * 80)

best = filtered_results[0]
print(f"\nBEST VARIANT:")
print(f"  Cadence: {best['cadence']}")
print(f"  Rainy amount: ${best['rainy_amount']:.0f}")
print(f"  RSI threshold: <{best['rsi_threshold']}")
print(f"  CAGR: {best['cagr']*100:.2f}%")
print(f"  Hit rate: {best['hit_rate']*100:.1f}%")
print(f"  Final equity: ${best['end_equity']:,.0f}")
print(f"  Total contributions: ${best['contributions']:,.0f}")
print(f"  Rainy buys: {best['rainy_hits']} / {best['rainy_total']}")

print(f"\nBASELINE DCA COMPARISON:")
print(f"  Baseline CAGR: {baseline['cagr']*100:.2f}%")
print(f"  Baseline equity: ${baseline['end_equity']:,.0f}")
print(f"  Baseline invested: ${baseline['contributions']:,.0f}")
print(f"  CAGR improvement: +{(best['cagr'] - baseline['cagr'])*100:.2f} percentage points")
print(f"  Equity improvement: +${(best['end_equity'] - baseline['end_equity']):,.0f} ({((best['end_equity']/baseline['end_equity'])-1)*100:.1f}% more)")

print(f"\nRAINY PERIOD ANALYSIS (RSI < 45):")
print(f"  Total rainy periods: {len(rainy_periods)}")
if rainy_periods:
    period_lengths = [p['length'] for p in rainy_periods]
    monday_periods = [p['length'] // 5 for p in rainy_periods]  # Approximate weeks
    print(f"  Shortest period: {min(period_lengths)} trading days (~{min(monday_periods)} Mondays)")
    print(f"  Longest period: {max(period_lengths)} trading days (~{max(monday_periods)} Mondays)")
    print(f"  Average period: {np.mean(period_lengths):.1f} trading days (~{np.mean(monday_periods):.1f} Mondays)")

print(f"\nSPY DRAWDOWN ANALYSIS:")
print(f"  Maximum drawdown: {spy_drawdown.min():.2f}%")
print(f"  Date of max DD: {spy_drawdown.idxmin().date()}")

print("\n" + "=" * 80)
