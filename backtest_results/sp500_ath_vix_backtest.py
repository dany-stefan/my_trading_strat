"""
20-Year Comparison: Always-DCA vs Event-Driven "Save My Ass" Strategy
=====================================================================

WHAT THIS DOES
- Fetches up to 20 years of daily prices for: S&P 500 proxy (SPY), VIX, and VUN.TO (CAD)
- Simulates two strategies over the same period:
  1) Baseline: DCA $150 CAD into VUN every 2 weeks, no conditions
  2) Event-Driven (SMAS): Same baseline DCA, plus:
     - Event sell trigger: Price crosses DOWN below 50-day SMA + RSI < 40 + 7% drop in past week
       (Triple confirmation: technical breakdown + momentum weakness + significant drop)
     - Sell 50% of entire VUN position to cash
     - Buyback trigger: When 20-day SMA crosses BELOW 50-day SMA (bearish cross indicating dip)
     - Execute 16 weekly buybacks over 4 months - ONLY when BOTH conditions met:
       * Price is BELOW 20-day SMA (buying dips)
       * RSI is oversold (30-50 range)
     - Pause buys when price crosses ABOVE 20-day SMA; resume when it drops back below

NOTES
- Signals use the S&P 500 proxy (SPY) for SMA/RSI.
- VUN.TO inception is ~2012, so the effective backtest period is the overlap across SPY,^VIX,VUN.TO.
    We’ll still fetch 20 years, but simulate from the first date where all series have data.

USAGE
Run the script. Results are printed and exported to backtest_results/ as CSVs and charts.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

# ============================================================================
# PARAMETERS (adjust as needed)
# ============================================================================
INDEX_TICKER = "SPY"           # S&P 500 ETF proxy for signals
VUN_TICKER = "VUN.TO"          # Vanguard US Total Market ETF (CAD)
VIX_TICKER = "^VIX"            # CBOE Volatility Index
LOOKBACK_YEARS = 20            # Years of historical data to analyze

# Event detection criteria - Sell signal
RSI_DOWNTREND_THRESHOLD = 40   # RSI below 40 indicates strong downtrend/weakness
DROP_THRESHOLD = 0.07          # 7% drop from recent high confirms downtrend
EVENT_WINDOW_DAYS = 7          # Look back 1 week for drop measurement

# Event sell rules
SELL_FRACTION = 0.50           # Sell 50% of entire position (not just profits)

# Baseline DCA (always runs, both strategies)
DCA_BASE_AMOUNT = 150.00       # $150 CAD every two weeks into VUN
DCA_BASE_FREQ_DAYS = 14        # Bi-weekly cadence (calendar days)

# Event-driven buyback DCA (only for SMAS strategy)
DCA_MONTHS = 4                 # Window length after start trigger (~4 months)
DCA_BUYBACK_FREQ_DAYS = 7      # Weekly buys during buyback period
DCA_PERIODS = 16               # Target number of buys (weekly over ~4 months: 4*4=16 weeks)

# Buyback trigger (multi-condition bottoming signal)
VIX_CALM_THRESHOLD = 20.0      # VIX must be below 20 (fear subsiding)
SMA_CONVERGENCE_PCT = 0.02     # 20-day SMA within 2% of 50-day SMA (bottoming compression)
RSI_OVERSOLD_MIN = 30          # RSI above 30 (not in extreme panic)
RSI_OVERSOLD_MAX = 50          # RSI below 50 (still in oversold/neutral zone)
VIX_DROP_WINDOW_DAYS = 90      # Extended window: 90 days (~3 months) to catch recovery

# Indicator parameters & thresholds (Signals based on SPY)
SMA_SHORT = 20                 # S&P short-term SMA (for pause/resume)
SMA_LONG = 50                  # S&P long-term SMA (defensive filter)
RSI_PERIOD = 14                # RSI period

# ============================================================================
# DATA FETCHING
# ============================================================================
print("="*80)
print("20-YEAR DCA VS EVENT-DRIVEN (SMAS) BACKTEST")
print("="*80)
print(f"\nFetching up to {LOOKBACK_YEARS} years of historical data...")
print(f"  - S&P 500 proxy: {INDEX_TICKER}")
print(f"  - VIX: {VIX_TICKER}")
print(f"  - Trading instrument: {VUN_TICKER}")

def get_data(ticker, period_days):
    """Fetch adjusted close prices from Yahoo Finance"""
    try:
        # Calculate start and end dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        data = yf.download(ticker, start=start_date, end=end_date, interval="1d", progress=False)
        
        if data.empty:
            print(f"Warning: No data retrieved for {ticker}")
            return pd.Series(dtype=float)
        
        # Handle multi-index columns (newer yfinance versions)
        if isinstance(data.columns, pd.MultiIndex):
            # Flatten the multi-index by taking the first level (price type)
            data.columns = data.columns.get_level_values(0)
        
        # Handle both single-column and multi-column dataframes
        if isinstance(data, pd.Series):
            return data
        elif 'Close' in data.columns:
            return data['Close']
        elif 'Adj Close' in data.columns:
            return data['Adj Close']
        else:
            print(f"Warning: No price column found for {ticker}")
            print(f"Available columns: {data.columns.tolist()}")
            return pd.Series(dtype=float)
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return pd.Series(dtype=float)

period_days = 365 * LOOKBACK_YEARS
index_data = get_data(INDEX_TICKER, period_days)
vix_data = get_data(VIX_TICKER, period_days)
vun_data = get_data(VUN_TICKER, period_days)

# Combine and align data
df = pd.DataFrame({
    'index': index_data,
    'vix': vix_data,
    'vun': vun_data
})

# Check if we have any data
if df.empty or df.dropna().empty:
    print("\nERROR: No data could be retrieved. Please check:")
    print("  1. Your internet connection")
    print("  2. That the tickers are correct")
    print("  3. That yfinance service is available")
    exit(1)

df = df.dropna()

df.index = pd.to_datetime(df.index)

print(f"\nData range (overlap across SPY, VIX, VUN): {df.index[0].date()} to {df.index[-1].date()}")
print(f"Total trading days: {len(df)}")

# ============================================================================
# INDICATORS
# ============================================================================
print("\nAdding indicators (SPY: SMA20, SMA50, RSI)...\n")

def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

df['spx_sma20'] = df['index'].rolling(SMA_SHORT).mean()
df['spx_sma50'] = df['index'].rolling(SMA_LONG).mean()
df['spx_rsi'] = compute_rsi(df['index'], RSI_PERIOD)

# Helpers
def next_trading_day_on_or_after(date: pd.Timestamp) -> pd.Timestamp:
    if date in df.index:
        return date
    idx = df.index.get_indexer([date], method='backfill')[0]
    if idx == -1:
        return df.index[-1]
    return df.index[idx]

def schedule_biweekly_dates(start_date: pd.Timestamp, end_date: pd.Timestamp) -> list:
    dates = []
    d = start_date
    while d <= end_date:
        dates.append(next_trading_day_on_or_after(d))
        d = d + pd.Timedelta(days=DCA_BASE_FREQ_DAYS)
    # ensure unique and sorted
    dates = sorted(pd.unique(dates))
    return dates

# ============================================================================
# STRATEGY SIMULATION
# ============================================================================

print("Simulating Baseline DCA and Event-Driven SMAS strategy...\n")

start_date = df.index[0]
end_date = df.index[-1]

# Baseline state
base_cash = 0.0
base_shares = 0.0
base_cost = 0.0

# SMAS state (includes baseline DCA too)
smas_cash = 0.0
smas_shares = 0.0
smas_cost = 0.0

# Event buyback state
active_event = None  # dict or None
event_cash_pool = 0.0
event_started = False
event_start_date = None
event_end_date = None
event_schedule = []  # list of scheduled buy dates
event_schedule_idx = 0
event_remaining_buys = 0
event_paused = False

# Event tracking for CSV export
events_detected = []
event_buybacks = []

# Equity curves
equity_base = []
equity_smas = []

# Baseline DCA schedule
dca_dates = schedule_biweekly_dates(start_date, end_date)
dca_dates_set = set(dca_dates)

# Precompute for event detection efficiency: we'll process day by day
for i, current_date in enumerate(df.index):
    row = df.loc[current_date]
    price_vun = row['vun']
    price_spx = row['index']

    # --------------------------------------------------
    # Baseline DCA buy (every 14 calendar days)
    # --------------------------------------------------
    # This runs EVERY scheduled date for BOTH strategies, regardless of events.
    # The SMAS strategy continues regular DCA before, during, and after events.
    if current_date in dca_dates_set:
        # Baseline
        if price_vun > 0:
            shares = DCA_BASE_AMOUNT / price_vun
            base_shares += shares
            base_cost += DCA_BASE_AMOUNT

            # SMAS also does the same baseline DCA (paycheck every 2 weeks)
            smas_shares += shares
            smas_cost += DCA_BASE_AMOUNT
        # cash does not change for baseline; assume external contributions

    # --------------------------------------------------
    # Event detection and sell (50% of position)
    # SELL SIGNAL: Price crosses DOWN below 50-day SMA + RSI < 40 + 7% drop in past week
    # --------------------------------------------------
    if active_event is None:
        # Check if price just crossed below 50-day SMA TODAY
        prev_date = df.index[i-1] if i > 0 else None
        crossed_below_sma50 = False
        
        if prev_date is not None and not np.isnan(row['spx_sma50']):
            prev = df.loc[prev_date]
            if not np.isnan(prev['spx_sma50']):
                # Price was above or at SMA50 yesterday, now it's below TODAY
                crossed_below_sma50 = (prev['index'] >= prev['spx_sma50']) and (price_spx < row['spx_sma50'])
        
        # If we crossed below SMA50 TODAY, check RSI and drop
        if crossed_below_sma50:
            # Condition 1: RSI below 40 confirms strong downtrend
            rsi_downtrend = (not np.isnan(row['spx_rsi'])) and (row['spx_rsi'] < RSI_DOWNTREND_THRESHOLD)
            
            # Condition 2: 7% drop from past week's high
            lookback_start = current_date - pd.Timedelta(days=EVENT_WINDOW_DAYS)
            window = df.loc[(df.index >= lookback_start) & (df.index <= current_date)]
            significant_drop = False
            
            if not window.empty and len(window) >= 3:
                week_high = window['index'].max()
                if week_high > 0:
                    drop = (week_high - price_spx) / week_high
                    significant_drop = drop >= DROP_THRESHOLD
            
            # Both conditions must be true
            if rsi_downtrend and significant_drop:
                # Trigger event SELL of 50% of position
                if smas_shares > 0:
                    shares_to_sell = smas_shares * SELL_FRACTION
                    proceeds = shares_to_sell * price_vun
                    avg_cost = smas_cost / smas_shares
                    cost_sold = avg_cost * shares_to_sell
                    
                    smas_shares -= shares_to_sell
                    smas_cost -= cost_sold
                    event_cash_pool += proceeds

                    active_event = {
                        'anchor_date': prev_date,
                        'sell_date': current_date,
                        'anchor_price': week_high,
                        'sell_price_spx': price_spx,
                        'sell_price_vun': price_vun,
                        'vix_anchor': prev['vix'] if 'vix' in prev else np.nan,
                        'vix_today': row['vix'],
                        'drop': drop,
                        'vix_rise': 0,  # Not using VIX for sell signal
                        'proceeds': proceeds,
                        'shares_sold': shares_to_sell,
                        'vix_peak': row['vix']
                    }
                    
                    # Log event detection
                    events_detected.append({
                        'event_number': len(events_detected) + 1,
                        'anchor_date': window['index'].idxmax(),
                        'sell_date': current_date,
                        'anchor_spx': week_high,
                        'sell_spx': price_spx,
                        'drop_pct': drop * 100,
                        'vix_anchor': prev['vix'] if 'vix' in prev else np.nan,
                        'vix_today': row['vix'],
                        'vix_rise_pct': 0,  # Not using VIX
                        'spx_sma50': row['spx_sma50'],
                        'spx_rsi': row['spx_rsi'],
                        'vun_price': price_vun,
                        'cash_raised_cad': proceeds,
                        'shares_sold': shares_to_sell,
                        'sell_fraction': SELL_FRACTION
                    })
                    
                    event_started = False
                    event_start_date = None
                    event_end_date = None
                    event_schedule = []
                    event_schedule_idx = 0
                    event_remaining_buys = DCA_PERIODS
                    event_paused = False
                    # else: if no shares, nothing to sell; ignore event

    # --------------------------------------------------
    # Buyback start trigger (V-shaped bottom: VIX calm + SMA convergence + RSI oversold)
    # --------------------------------------------------
    if active_event is not None and not event_started:
        sell_date = active_event['sell_date']
        days_since_sell = (current_date - sell_date).days
        
        # Check if within the extended window after sell (90 days)
        if days_since_sell <= VIX_DROP_WINDOW_DAYS:
            # Detect SMA20 crossing below SMA50 (bearish cross = buy signal)
            sma20 = row['spx_sma20']
            sma50 = row['spx_sma50']
            prev_date = df.index[i-1] if i > 0 else None
            
            sma_cross_below = False
            if prev_date is not None and not np.isnan(sma20) and not np.isnan(sma50):
                prev = df.loc[prev_date]
                prev_sma20 = prev['spx_sma20']
                prev_sma50 = prev['spx_sma50']
                if not np.isnan(prev_sma20) and not np.isnan(prev_sma50):
                    # SMA20 was above or equal to SMA50, now it's below
                    sma_cross_below = (prev_sma20 >= prev_sma50) and (sma20 < sma50)
            
            # Trigger buyback when SMA20 crosses below SMA50
            if sma_cross_below and event_cash_pool > 0.0:
                event_started = True
                event_start_date = current_date
                event_end_date = current_date + pd.Timedelta(days=30*DCA_MONTHS)  # ~4 months
                # Schedule 16 weekly attempts starting today
                event_schedule = [next_trading_day_on_or_after(current_date + pd.Timedelta(days=DCA_BUYBACK_FREQ_DAYS*k)) for k in range(DCA_PERIODS)]
                event_schedule_idx = 0
                event_remaining_buys = DCA_PERIODS
                event_paused = False
        else:
            # Window expired without bottoming signal - close event, keep cash
            active_event = None
            # Cash pool remains for future opportunities

    # --------------------------------------------------
    # Pause / resume logic during buyback window (BUY when BELOW 20-day SMA)
    # --------------------------------------------------
    if active_event is not None and event_started:
        # End window check
        if current_date > event_end_date or event_remaining_buys == 0 or event_schedule_idx >= len(event_schedule):
            # Close event
            active_event = None
            event_started = False
            event_start_date = None
            event_end_date = None
            event_schedule = []
            event_schedule_idx = 0
            event_remaining_buys = 0
            event_paused = False
        else:
            # Detect crosses for pause/resume against SMA20
            # FLIPPED LOGIC: Buy when price BELOW SMA20, pause when ABOVE SMA20
            prev_date = df.index[i-1] if i > 0 else None
            if prev_date is not None:
                prev = df.loc[prev_date]
                # Cross UP (price goes above SMA20) = PAUSE buying (avoid buying rallies)
                cross_up = (price_spx > row['spx_sma20']) and (prev['index'] <= prev['spx_sma20']) if not np.isnan(row['spx_sma20']) and not np.isnan(prev['spx_sma20']) else False
                # Cross DOWN (price goes below SMA20) = RESUME buying (buy dips)
                cross_down = (price_spx < row['spx_sma20']) and (prev['index'] >= prev['spx_sma20']) if not np.isnan(row['spx_sma20']) and not np.isnan(prev['spx_sma20']) else False
                
                if cross_up:
                    event_paused = True  # Pause when price rallies above SMA20
                elif cross_down:
                    event_paused = False  # Resume when price dips below SMA20

            # Execute buy if today is the next scheduled attempt, not paused, and price BELOW SMA20
            if event_schedule_idx < len(event_schedule) and current_date == event_schedule[event_schedule_idx]:
                # Check if price is below SMA20 AND RSI is oversold
                price_below_sma20 = (not np.isnan(row['spx_sma20'])) and (price_spx < row['spx_sma20'])
                rsi_oversold = (not np.isnan(row['spx_rsi'])) and (RSI_OVERSOLD_MIN <= row['spx_rsi'] <= RSI_OVERSOLD_MAX)
                
                if (not event_paused) and price_below_sma20 and rsi_oversold and event_remaining_buys > 0 and event_cash_pool > 0 and price_vun > 0:
                    allocation = event_cash_pool / event_remaining_buys
                    shares = allocation / price_vun
                    smas_shares += shares
                    smas_cost += allocation
                    event_cash_pool -= allocation
                    event_remaining_buys -= 1
                    
                    # Log buyback purchase
                    event_buybacks.append({
                        'event_number': len(events_detected),
                        'buy_number': DCA_PERIODS - event_remaining_buys,
                        'date': current_date,
                        'vun_price': price_vun,
                        'shares_bought': shares,
                        'cash_spent': allocation,
                        'spx_price': price_spx,
                        'spx_sma20': row['spx_sma20'],
                        'spx_rsi': row['spx_rsi'],
                        'paused': False
                    })
                # Move to next scheduled slot regardless of execution
                event_schedule_idx += 1

    # Mark to market equities each day
    equity_base.append({
        'date': current_date,
        'equity': base_shares * price_vun + base_cash
    })
    equity_smas.append({
        'date': current_date,
        'equity': smas_shares * price_vun + smas_cash + event_cash_pool
    })

# Convert equity curves to DataFrame
eq_base_df = pd.DataFrame(equity_base).set_index('date')
eq_smas_df = pd.DataFrame(equity_smas).set_index('date')

# Summary metrics
def compute_metrics(eq: pd.Series):
    start_val = eq.iloc[0]
    end_val = eq.iloc[-1]
    years = (eq.index[-1] - eq.index[0]).days / 365.25
    total_return = (end_val / start_val) - 1 if start_val > 0 else np.nan
    cagr = (end_val / start_val) ** (1/years) - 1 if start_val > 0 and years > 0 else np.nan
    # max drawdown
    roll_max = eq.cummax()
    drawdown = (eq / roll_max) - 1
    max_dd = drawdown.min()
    return {
        'start': eq.index[0].date(),
        'end': eq.index[-1].date(),
        'years': years,
        'start_val': start_val,
        'end_val': end_val,
        'total_return': total_return,
        'cagr': cagr,
        'max_drawdown': float(max_dd)
    }

metrics_base = compute_metrics(eq_base_df['equity'])
metrics_smas = compute_metrics(eq_smas_df['equity'])

# ============================================================================
# EXPORT RESULTS
# ============================================================================

output_dir = Path("backtest_results")
output_dir.mkdir(exist_ok=True)

print(f"\nExporting comparison data to CSV files in '{output_dir}' directory...")

# Export event detection log
if events_detected:
    events_df = pd.DataFrame(events_detected)
    events_df.to_csv(output_dir / 'events_detected.csv', index=False)
    print(f"  ✓ Saved events_detected.csv ({len(events_detected)} events)")

# Export buyback trades log
if event_buybacks:
    buybacks_df = pd.DataFrame(event_buybacks)
    buybacks_df.to_csv(output_dir / 'event_buybacks.csv', index=False)
    print(f"  ✓ Saved event_buybacks.csv ({len(event_buybacks)} buyback purchases)")

# Export equity curves
eq_base_df.to_csv(output_dir / 'equity_baseline_dca.csv')
eq_smas_df.to_csv(output_dir / 'equity_smas_strategy.csv')

summary_comp = pd.DataFrame([
    {'strategy': 'Baseline_DCA', **metrics_base},
    {'strategy': 'SMAS_Event', **metrics_smas}
])
summary_comp.to_csv(output_dir / 'strategy_comparison_summary.csv', index=False)
print("  ✓ Saved equity_baseline_dca.csv, equity_smas_strategy.csv, strategy_comparison_summary.csv")

# ============================================================================
# RESULTS REPORTING
# ============================================================================

print("="*80)
print("STRATEGY COMPARISON SUMMARY")
print("="*80)
print(f"\nPeriod: {metrics_base['start']} → {metrics_base['end']} ({metrics_base['years']:.2f} years)")
print(f"Bi-weekly DCA: ${DCA_BASE_AMOUNT:.2f} CAD every 2 weeks")
print(f"Total contributions (both strategies): ${DCA_BASE_AMOUNT * len(dca_dates):.2f} CAD")

print("\n" + "-"*80)
print("BASELINE DCA (No Event Strategy - Just Hold)")
print("-"*80)
print(f"  Start value: ${metrics_base['start_val']:.2f}")
print(f"  End value:   ${metrics_base['end_val']:.2f}")
print(f"  Total return: {metrics_base['total_return']*100:.2f}%")
print(f"  CAGR: {metrics_base['cagr']*100:.2f}%")
print(f"  Max drawdown: {metrics_base['max_drawdown']*100:.2f}%")

print("\n" + "-"*80)
print("SMAS EVENT-DRIVEN (Sell Profits on Crash, Buyback on Recovery)")
print("-"*80)
print(f"  Start value: ${metrics_smas['start_val']:.2f}")
print(f"  End value:   ${metrics_smas['end_val']:.2f}")
print(f"  Total return: {metrics_smas['total_return']*100:.2f}%")
print(f"  CAGR: {metrics_smas['cagr']*100:.2f}%")
print(f"  Max drawdown: {metrics_smas['max_drawdown']*100:.2f}%")

print("\n" + "="*80)
print("PERFORMANCE DIFFERENCE (SMAS vs Baseline)")
print("="*80)
edge = (metrics_smas['end_val'] - metrics_base['end_val'])
edge_pct = (edge / metrics_base['end_val'] * 100) if metrics_base['end_val'] > 0 else 0
cagr_diff = (metrics_smas['cagr'] - metrics_base['cagr']) * 100
dd_diff = (metrics_smas['max_drawdown'] - metrics_base['max_drawdown']) * 100

print(f"  Terminal value difference: ${edge:+,.2f} CAD ({edge_pct:+.2f}%)")
print(f"  CAGR difference: {cagr_diff:+.2f}% points")
print(f"  Max drawdown difference: {dd_diff:+.2f}% points")

if edge > 0:
    print(f"\n  💰 SMAS strategy MADE ${edge:,.2f} MORE by taking action during crashes!")
elif edge < 0:
    print(f"\n  📉 SMAS strategy LOST ${abs(edge):,.2f} by trying to time the market")
else:
    print(f"\n  ➡️  Both strategies ended with the same value")

print(f"\n  📊 Events detected and acted upon: {len(events_detected)}")
if event_buybacks:
    print(f"  🔄 Total buyback purchases executed: {len(event_buybacks)}")

print(f"\n{'='*80}")
print("END OF BACKTEST")
print(f"{'='*80}\n")

# ============================================================================
# VISUALIZATION - PLOTS
# ============================================================================

print(f"\nGenerating comparison plot in '{output_dir}' directory...")

# Main equity comparison chart
fig, ax = plt.subplots(1, 1, figsize=(14, 6))
ax.plot(eq_base_df.index, eq_base_df['equity'], label='Baseline DCA', color='blue')
ax.plot(eq_smas_df.index, eq_smas_df['equity'], label='SMAS Event-Driven', color='orange')
ax.set_title('Portfolio Equity Curves')
ax.set_ylabel('Value (CAD)')
ax.grid(True, alpha=0.3)
ax.legend(loc='best')
plt.tight_layout()
plt.savefig(output_dir / 'equity_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ Saved equity_comparison.png")

# Individual event charts showing SPY price with SMAs
if events_detected:
    print(f"\nGenerating {len(events_detected)} event detail charts...")
    for ev_dict in events_detected:
        ev_num = ev_dict['event_number']
        sell_date = pd.to_datetime(ev_dict['sell_date'])
        
        # Find buybacks for this event
        event_buybacks_list = [b for b in event_buybacks if b['event_number'] == ev_num]
        
        # Define plot window: 30 days before sell to 90 days after (or last buyback + 30 days)
        plot_start = sell_date - pd.Timedelta(days=30)
        if event_buybacks_list:
            last_buyback_date = pd.to_datetime(event_buybacks_list[-1]['date'])
            plot_end = last_buyback_date + pd.Timedelta(days=30)
        else:
            plot_end = sell_date + pd.Timedelta(days=90)
        
        plot_data = df.loc[plot_start:plot_end].copy()
        
        if plot_data.empty:
            continue
        
        # Create figure with 2 subplots (SPY price + SMAs, RSI)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        fig.suptitle(f'Event #{ev_num}: {sell_date.strftime("%Y-%m-%d")} - SPY Drop {ev_dict["drop_pct"]:.1f}%, VIX Spike {ev_dict["vix_rise_pct"]:.1f}%', 
                     fontsize=14, fontweight='bold')
        
        # Subplot 1: SPY Price and SMAs
        ax1.plot(plot_data.index, plot_data['index'], label='SPY Price', color='black', linewidth=2)
        ax1.plot(plot_data.index, plot_data['spx_sma20'], label='SMA20', color='red', linestyle='--', linewidth=1.5, alpha=0.8)
        ax1.plot(plot_data.index, plot_data['spx_sma50'], label='SMA50', color='blue', linestyle='--', linewidth=1.5, alpha=0.8)
        
        # Mark sell signal
        ax1.scatter(sell_date, ev_dict['sell_spx'], color='red', s=200, marker='v', 
                   zorder=5, label=f'SELL 50% (SPY ${ev_dict["sell_spx"]:.2f})', edgecolors='black', linewidths=2)
        
        # Mark buyback points
        if event_buybacks_list:
            buy_dates = [pd.to_datetime(b['date']) for b in event_buybacks_list]
            buy_prices = [b['spx_price'] for b in event_buybacks_list]
            ax1.scatter(buy_dates, buy_prices, color='green', s=80, marker='o', 
                       zorder=5, label=f'Buybacks ({len(event_buybacks_list)})', edgecolors='black', linewidths=1)
        
        ax1.set_ylabel('SPY Price (USD)', fontsize=11, fontweight='bold')
        ax1.legend(loc='best', fontsize=9)
        ax1.grid(True, alpha=0.3)
        ax1.set_title(f'S&P 500 (SPY) with Moving Averages', fontsize=11)
        
        # Subplot 2: RSI
        ax2.plot(plot_data.index, plot_data['spx_rsi'], label='RSI(14)', color='purple', linewidth=1.5)
        ax2.axhline(70, color='red', linestyle='--', alpha=0.5, label='Overbought (70)')
        ax2.axhline(30, color='green', linestyle='--', alpha=0.5, label='Oversold (30)')
        ax2.axhline(50, color='gray', linestyle=':', alpha=0.5, label='Neutral (50)')
        ax2.axhline(RSI_OVERSOLD_MIN, color='orange', linestyle=':', alpha=0.7,
                   label=f'RSI Range ({RSI_OVERSOLD_MIN}-{RSI_OVERSOLD_MAX})')
        ax2.axhline(RSI_OVERSOLD_MAX, color='orange', linestyle=':', alpha=0.7)        # Mark key dates on RSI chart
        ax2.axvline(sell_date, color='red', linestyle=':', alpha=0.3)
        if event_buybacks_list:
            for buy in event_buybacks_list:
                ax2.axvline(pd.to_datetime(buy['date']), color='green', linestyle=':', alpha=0.2)
        
        ax2.set_ylabel('RSI', fontsize=11, fontweight='bold')
        ax2.set_xlabel('Date', fontsize=11, fontweight='bold')
        ax2.legend(loc='best', fontsize=9)
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 100)
        ax2.set_title(f'Relative Strength Index (RSI)', fontsize=11)
        
        # Format x-axis
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Add info text box
        info_text = f"Sell: ${ev_dict['cash_raised_cad']:.0f} CAD raised\n"
        if event_buybacks_list:
            total_buyback = sum(b['cash_spent'] for b in event_buybacks_list)
            info_text += f"Buyback: ${total_buyback:.0f} CAD spent ({len(event_buybacks_list)} buys)"
        else:
            info_text += "Buyback: No trigger (cash held)"
        ax1.text(0.02, 0.98, info_text, transform=ax1.transAxes, fontsize=9,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig(output_dir / f'event_{ev_num}_detail.png', dpi=150, bbox_inches='tight')
        plt.close()
    
    print(f"  ✓ Saved {len(events_detected)} event detail charts")

print(f"\n{'='*80}")
print(f"All results exported to '{output_dir}' directory")
print(f"{'='*80}\n")
