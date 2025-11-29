#!/usr/bin/env python3
"""
Update METRICS_REFERENCE.json with complete backtest results
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path

def calculate_cagr(start_value, end_value, years):
    """Calculate Compound Annual Growth Rate"""
    if start_value == 0 or years == 0:
        return 0.0
    return (((end_value / start_value) ** (1 / years)) - 1) * 100

def main():
    print("="*80)
    print("UPDATING METRICS_REFERENCE.JSON")
    print("="*80)
    
    # Read CSV files
    print("\nReading CSV files...")
    equity_rainy = pd.read_csv('equity_rainy_strategy_calendar_dates.csv')
    equity_baseline = pd.read_csv('equity_baseline_calendar_dates.csv')
    rainy_buys = pd.read_csv('rainy_buys_calendar_dates.csv')
    
    # Calculate date range
    start_date = equity_rainy['date'].iloc[0]
    end_date = equity_rainy['date'].iloc[-1]
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)
    years = round((end_dt - start_dt).days / 365.25, 1)
    
    # Rainy strategy metrics
    final_equity_rainy = round(equity_rainy['equity'].iloc[-1], 2)
    final_cash_pool = round(equity_rainy['cash_pool'].iloc[-1], 2)
    
    # Calculate total invested for rainy strategy
    # Assume $150 base every 2 weeks for 22.1 years = 575 paydays
    # Plus rainy buys
    total_rainy_deployed = rainy_buys['amount'].sum()
    num_execution_days = len(equity_rainy)
    base_dca_investment = 150 * len(rainy_buys) + 150 * (num_execution_days - len(rainy_buys)) - total_rainy_deployed
    # Recalculate: we need the actual payday count
    # From backtest: 491 execution days total
    execution_days = 491
    base_dca_investment = 150 * execution_days  # Base $150 on each execution day
    total_invested_rainy = base_dca_investment + total_rainy_deployed
    
    profit_rainy = final_equity_rainy - total_invested_rainy
    profit_pct_rainy = round((profit_rainy / total_invested_rainy) * 100, 1)
    
    # Baseline DCA metrics
    final_equity_baseline = round(equity_baseline['equity'].iloc[-1], 2)
    total_invested_baseline = 150 * execution_days  # Same $150 per execution day
    
    # Calculate CAGRs
    # Backtest CAGR: growth from initial equity to final equity
    initial_equity = 150  # First investment
    cagr_backtest_rainy = round(calculate_cagr(initial_equity, final_equity_rainy, years), 2)
    cagr_backtest_baseline = round(calculate_cagr(initial_equity, final_equity_baseline, years), 2)
    
    # ROI CAGR: annualized return on total contributions
    cagr_roi_rainy = round(calculate_cagr(total_invested_rainy, final_equity_rainy, years), 2)
    cagr_roi_baseline = round(calculate_cagr(total_invested_baseline, final_equity_baseline, years), 2)
    
    # Rainy buy statistics
    num_rainy_buys = len(rainy_buys)
    avg_rsi_sma = round(rainy_buys['rsi_sma'].mean(), 2)
    
    # From backtest output: 85 total opportunities, 83 successful
    total_opportunities = 85
    missed_opportunities = total_opportunities - num_rainy_buys
    hit_rate = round((num_rainy_buys / total_opportunities) * 100, 1)
    frequency = round((total_opportunities / execution_days) * 100, 1)
    
    # Calculate rainy portion value (need current SPY price and shares)
    # This requires simulating the shares from rainy buys
    rainy_shares = sum(row['amount'] / row['price'] for _, row in rainy_buys.iterrows())
    current_spy_price = 659.03  # From backtest end date
    rainy_portion_value = round(rainy_shares * current_spy_price, 0)
    rainy_roi_pct = round(((rainy_portion_value - total_rainy_deployed) / total_rainy_deployed) * 100, 1)
    rainy_cagr = round(calculate_cagr(total_rainy_deployed, rainy_portion_value, years), 2)
    
    # Performance comparison
    outperformance_dollars = round(final_equity_rainy - final_equity_baseline, 2)
    outperformance_pct = round((outperformance_dollars / final_equity_baseline) * 100, 1)
    return_on_rainy_pct = round(((outperformance_dollars / total_rainy_deployed) - 1) * 100, 1)
    return_multiplier = round(outperformance_dollars / total_rainy_deployed, 2)
    
    # Build metrics dictionary
    metrics = {
        "generation_date": datetime.now().strftime("%Y-%m-%d"),
        "generation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "backtest_period": {
            "start_date": start_date,
            "end_date": end_date,
            "years": years
        },
        "rainy_day_strategy": {
            "final_equity": final_equity_rainy,
            "final_cash_pool": final_cash_pool,
            "total_invested": int(total_invested_rainy),
            "base_dca_investment": int(base_dca_investment),
            "rainy_investment": int(total_rainy_deployed),
            "profit": round(profit_rainy, 2),
            "profit_percent": profit_pct_rainy,
            "cagr_backtest": cagr_backtest_rainy,
            "cagr_roi": cagr_roi_rainy,
            "max_drawdown_percent": 27.25,
            "volatility_percent": 19.92
        },
        "simple_dca_baseline": {
            "final_equity": final_equity_baseline,
            "total_invested": int(total_invested_baseline),
            "cagr_backtest": cagr_backtest_baseline,
            "cagr_roi": cagr_roi_baseline,
            "max_drawdown_percent": 27.55
        },
        "rainy_day_statistics": {
            "total_opportunities": total_opportunities,
            "successful_deployments": num_rainy_buys,
            "missed_opportunities": missed_opportunities,
            "hit_rate_percent": hit_rate,
            "frequency_percent": frequency,
            "average_rsi_sma": avg_rsi_sma,
            "total_deployed": int(total_rainy_deployed),
            "rainy_portion_value": int(rainy_portion_value),
            "rainy_roi_percent": rainy_roi_pct,
            "rainy_cagr_percent": rainy_cagr
        },
        "performance_comparison": {
            "outperformance_vs_dca_dollars": outperformance_dollars,
            "outperformance_vs_dca_percent": outperformance_pct,
            "extra_capital_deployed": int(total_rainy_deployed),
            "return_on_rainy_capital_percent": return_on_rainy_pct,
            "return_on_rainy_capital_multiplier": return_multiplier
        },
        "market_comparison": {
            "market_cagr_percent": 8.0,
            "rainy_cagr_percent": rainy_cagr,
            "beats_market_by_percent": round(rainy_cagr - 8.0, 2),
            "extra_wealth_vs_market": int(rainy_portion_value - (total_rainy_deployed * (1.08 ** years)))
        },
        "advanced_metrics": {
            "sharpe_ratio": 1.26,
            "sharpe_rating": "Good",
            "sqn": 6.84,
            "sqn_rating": "Excellent",
            "r_squared": 0.846,
            "win_rate_percent": 54.9
        },
        "strategy_parameters": {
            "base_dca_amount": 150,
            "rainy_amount": 150,
            "cash_accumulation_per_payday": 30,
            "rsi_threshold": 45.0,
            "payday_schedule": "1st and 15th of each month",
            "execution_schedule": "3rd and 17th of each month"
        }
    }
    
    # Write to file in root directory
    output_path = Path('..') / 'METRICS_REFERENCE.json'
    with open(output_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"\n✅ Updated: {output_path.absolute()}")
    
    # Print summary
    print("\n" + "="*80)
    print("METRICS SUMMARY")
    print("="*80)
    print(f"Period: {start_date} to {end_date} ({years} years)")
    print(f"\nRainy Strategy:")
    print(f"  Final Equity: ${final_equity_rainy:,.2f}")
    print(f"  Total Invested: ${total_invested_rainy:,.0f}")
    print(f"  CAGR (ROI): {cagr_roi_rainy}%")
    print(f"\nBaseline DCA:")
    print(f"  Final Equity: ${final_equity_baseline:,.2f}")
    print(f"  CAGR (ROI): {cagr_roi_baseline}%")
    print(f"\nRainy Day Stats:")
    print(f"  Successful Deployments: {num_rainy_buys}")
    print(f"  Hit Rate: {hit_rate}%")
    print(f"  Total Deployed: ${total_rainy_deployed:,.0f}")
    print(f"  Rainy ROI: {rainy_roi_pct}%")
    print(f"\nOutperformance:")
    print(f"  vs DCA: ${outperformance_dollars:,.2f} (+{outperformance_pct}%)")
    print(f"  Return on Rainy Capital: {return_on_rainy_pct}%")
    print("="*80)

if __name__ == "__main__":
    main()
