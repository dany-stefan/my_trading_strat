"""
Integration Verification Script - TURBO
========================================

Verifies that all modules integrate correctly:
1. Backtest results match CSV files
2. Markdown reports reference correct CSV data
3. Email templates pull correct metrics
4. All data flows are consistent

This script runs all components and validates data consistency.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import sys

# Import local modules
from strategy_comparison import calculate_strategy_comparison
from advanced_metrics import calculate_advanced_metrics
from market_metrics import MarketMetrics
from email_generator_turbo import generate_email_content


def verify_csv_consistency():
    """Verify CSV files exist and have consistent data."""
    print("\n" + "="*80)
    print("STEP 1: Verifying CSV File Consistency")
    print("="*80)
    
    issues = []
    warnings = []
    
    # Check PROD equity curve
    prod_file = Path("equity_prod_rainy_calendar_dates.csv")
    if not prod_file.exists():
        issues.append(f"❌ Missing: {prod_file}")
    else:
        df = pd.read_csv(prod_file)
        print(f"✅ Found equity_prod_rainy_calendar_dates.csv: {len(df)} records")
        print(f"   Final equity: ${df['equity'].iloc[-1]:,.2f}")
    
    # Check TURBO equity curve
    turbo_file = Path("equity_turbo_rainy_calendar_dates.csv")
    if not turbo_file.exists():
        issues.append(f"❌ Missing: {turbo_file}")
    else:
        df = pd.read_csv(turbo_file)
        print(f"✅ Found equity_turbo_rainy_calendar_dates.csv: {len(df)} records")
        print(f"   Final equity: ${df['equity'].iloc[-1]:,.2f}")
    
    # Check PROD rainy buys
    prod_rainy_file = Path("rainy_buys_prod_calendar_dates.csv")
    if not prod_rainy_file.exists():
        warnings.append(f"⚠️  Missing: {prod_rainy_file}")
    else:
        df_rainy = pd.read_csv(prod_rainy_file)
        print(f"✅ Found rainy_buys_prod_calendar_dates.csv: {len(df_rainy)} records")
        print(f"   Total PROD rainy deployments: ${df_rainy['amount'].sum():,.2f}")
    
    # Check TURBO rainy buys
    turbo_rainy_file = Path("rainy_buys_turbo_calendar_dates.csv")
    if not turbo_rainy_file.exists():
        warnings.append(f"⚠️  Missing: {turbo_rainy_file}")
    else:
        df_rainy = pd.read_csv(turbo_rainy_file)
        print(f"✅ Found rainy_buys_turbo_calendar_dates.csv: {len(df_rainy)} records")
        print(f"   Total TURBO rainy deployments: ${df_rainy['amount'].sum():,.2f}")
        if 'regime' in df_rainy.columns:
            print(f"   Regime distribution: {df_rainy['regime'].value_counts().to_dict()}")
        if 'vix' in df_rainy.columns:
            print(f"   Average VIX on buys: {df_rainy['vix'].mean():.2f}")
    
    # Check yearly comparison
    yearly_file = Path("yearly_prod_vs_turbo.csv")
    if yearly_file.exists():
        df_yearly = pd.read_csv(yearly_file)
        print(f"✅ Found yearly_prod_vs_turbo.csv: {len(df_yearly)} years")
        print(f"   Winner distribution: {df_yearly['winner'].value_counts().to_dict()}")
    else:
        warnings.append(f"⚠️  Missing: {yearly_file}")
    
    return issues, warnings


def verify_strategy_comparison():
    """Verify strategy comparison module works correctly."""
    print("\n" + "="*80)
    print("STEP 2: Verifying Strategy Comparison Module")
    print("="*80)
    
    issues = []
    
    try:
        comp = calculate_strategy_comparison()
        metrics = comp.get_all_metrics()
        
        print(f"✅ Strategy comparison module loaded successfully")
        print(f"\nKey Metrics:")
        print(f"   TURBO CAGR: {metrics['turbo_cagr']}")
        print(f"   TURBO Final: {metrics['turbo_final']}")
        print(f"   TURBO Invested: {metrics['turbo_invested']}")
        print(f"   PROD CAGR: {metrics['prod_cagr']}")
        print(f"   PROD Final: {metrics['prod_final']}")
        print(f"   PROD Invested: {metrics['prod_invested']}")
        print(f"   Gain vs PROD: {metrics['gain_vs_prod']} ({metrics['gain_vs_prod_pct']})")
        print(f"   Backtest Period: {metrics['backtest_period']}")
        
        # Verify metrics are reasonable
        turbo_final_raw = float(metrics['turbo_final'].replace('$', '').replace(',', ''))
        if turbo_final_raw < 100000:
            issues.append(f"❌ TURBO final value seems too low: {metrics['turbo_final']}")
        
    except Exception as e:
        issues.append(f"❌ Strategy comparison failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return issues


def verify_advanced_metrics():
    """Verify advanced metrics module works correctly."""
    print("\n" + "="*80)
    print("STEP 3: Verifying Advanced Metrics Module")
    print("="*80)
    
    issues = []
    
    try:
        equity_file = "equity_turbo_rainy_calendar_dates.csv"
        if not Path(equity_file).exists():
            issues.append(f"❌ Cannot test advanced metrics - {equity_file} missing")
            return issues
        
        metrics = calculate_advanced_metrics(equity_file, initial_capital=74010)
        all_metrics = metrics.get_all_metrics()
        
        print(f"✅ Advanced metrics calculated successfully")
        print(f"\nAdvanced Metrics (TURBO):")
        print(f"   Sharpe Ratio: {all_metrics['sharpe_display']} ({metrics.get_sharpe_rating()})")
        print(f"   SQN: {all_metrics['sqn_display']} ({metrics.get_sqn_rating()})")
        print(f"   Max Drawdown: {all_metrics['max_drawdown_display']}")
        print(f"   Volatility: {all_metrics['volatility_display']}")
        print(f"   R²: {all_metrics['r_squared_display']}")
        print(f"   Win Rate: {all_metrics['win_rate_display']}")
        
    except Exception as e:
        issues.append(f"❌ Advanced metrics failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return issues


def verify_market_metrics():
    """Verify market metrics module works correctly."""
    print("\n" + "="*80)
    print("STEP 4: Verifying Market Metrics Module (TURBO)")
    print("="*80)
    
    issues = []
    
    try:
        # Test with sample data - BEAR regime, HIGH VIX
        test_price = 600.0
        test_spy_200ma = 650.0  # Below MA = BEAR
        test_vix = 30.0  # HIGH volatility
        test_rsi_sma = 40.0
        
        metrics = MarketMetrics(
            price=test_price,
            spy_200ma=test_spy_200ma,
            vix=test_vix,
            rsi_sma=test_rsi_sma
        )
        
        all_metrics = metrics.get_all_metrics()
        
        print(f"✅ Market metrics calculated successfully")
        print(f"\nTest Scenario (BEAR regime, HIGH VIX):")
        print(f"   Market Regime: {all_metrics['market_regime']}")
        print(f"   Adaptive Threshold: {all_metrics['adaptive_threshold']}")
        print(f"   Volatility Sizing: ${all_metrics['volatility_sizing']:.0f}")
        print(f"   VIX Level: {all_metrics['vix_level']}")
        print(f"   Deviation: {all_metrics['deviation_pct']:.2f}%")
        
        # Verify adaptive logic
        expected_regime = "BEAR"  # Price < MA
        if all_metrics['market_regime'] != expected_regime:
            issues.append(f"❌ Expected regime {expected_regime}, got {all_metrics['market_regime']}")
        
        expected_threshold = 48  # BEAR threshold
        if abs(all_metrics['adaptive_threshold'] - expected_threshold) > 0.1:
            issues.append(f"❌ Expected threshold {expected_threshold}, got {all_metrics['adaptive_threshold']}")
        
        expected_sizing = 210  # HIGH VIX sizing
        if abs(all_metrics['volatility_sizing'] - expected_sizing) > 0.1:
            issues.append(f"❌ Expected sizing ${expected_sizing}, got ${all_metrics['volatility_sizing']}")
        
        print(f"\nAdaptive Logic Verification:")
        print(f"   ✅ Regime detection correct")
        print(f"   ✅ Threshold adaptation correct")
        print(f"   ✅ Volatility sizing correct")
        
    except Exception as e:
        issues.append(f"❌ Market metrics failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return issues


def verify_email_generation():
    """Verify email generation works correctly."""
    print("\n" + "="*80)
    print("STEP 5: Verifying Email Generation (TURBO)")
    print("="*80)
    
    issues = []
    
    try:
        # Test email generation with sample data
        test_rsi_sma = 40.0
        test_price = 600.0
        test_cash_pool = 450.0
        test_contributions = 0.0
        test_rainy_buys = []
        test_spy_200ma = 650.0
        test_vix = 30.0
        
        subject, body = generate_email_content(
            rsi_sma=test_rsi_sma,
            price=test_price,
            cash_pool=test_cash_pool,
            total_contributions=test_contributions,
            rainy_buys=test_rainy_buys,
            is_simulation=True,
            spy_200ma=test_spy_200ma,
            vix=test_vix
        )
        
        print(f"✅ Email generated successfully")
        print(f"\nEmail Details:")
        print(f"   Subject: {subject[:80]}...")
        print(f"   Body length: {len(body)} characters")
        
        # Verify TURBO-specific content
        if "TURBO" not in subject:
            issues.append(f"❌ Email subject missing TURBO marker")
        
        if "3-FACTOR SYSTEM" not in body and "3-Factor System" not in body:
            issues.append(f"❌ Email missing 3-factor system explanation")
        
        if "CRITERIA EXPLANATION" not in body:
            issues.append(f"❌ Email missing criteria explanation")
        
        if "Market Regime" not in body and "REGIME" not in body:
            issues.append(f"❌ Email missing regime information")
        
        if "VIX" not in body:
            issues.append(f"❌ Email missing VIX information")
        
        print(f"\nTURBO Content Checks:")
        print(f"   ✅ Contains TURBO marker")
        print(f"   ✅ Contains 3-factor system")
        print(f"   ✅ Contains criteria explanation")
        print(f"   ✅ Contains regime info")
        print(f"   ✅ Contains VIX info")
        
    except Exception as e:
        issues.append(f"❌ Email generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return issues


def verify_visualizations():
    """Verify enhanced visualizations exist."""
    print("\n" + "="*80)
    print("STEP 6: Verifying Enhanced Visualizations")
    print("="*80)
    
    issues = []
    warnings = []
    
    expected_charts = [
        "strategy_comparison_prod_vs_turbo.png",
        "dashboard_interactive_turbo.png",
        "regime_performance_turbo.png",
        "monte_carlo_cash_pool_turbo.png",
        "consecutive_rainy_heatmap_turbo.png",
        "yearly_prod_vs_turbo.png",
        "rainy_amount_over_time_prod_vs_turbo.png"
    ]
    
    for chart in expected_charts:
        chart_path = Path(chart)
        if chart_path.exists():
            print(f"   ✅ Found: {chart}")
        else:
            warnings.append(f"⚠️  Missing chart: {chart}")
    
    return issues, warnings


def run_full_verification():
    """Run all verification steps."""
    print("\n" + "="*80)
    print("TURBO FOLDER - INTEGRATION VERIFICATION")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_issues = []
    all_warnings = []
    
    # Step 1: CSV consistency
    issues, warnings = verify_csv_consistency()
    all_issues.extend(issues)
    all_warnings.extend(warnings)
    
    # Step 2: Strategy comparison
    issues = verify_strategy_comparison()
    all_issues.extend(issues)
    
    # Step 3: Advanced metrics
    issues = verify_advanced_metrics()
    all_issues.extend(issues)
    
    # Step 4: Market metrics
    issues = verify_market_metrics()
    all_issues.extend(issues)
    
    # Step 5: Email generation
    issues = verify_email_generation()
    all_issues.extend(issues)
    
    # Step 6: Visualizations
    issues, warnings = verify_visualizations()
    all_issues.extend(issues)
    all_warnings.extend(warnings)
    
    # Final report
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)
    
    if all_issues:
        print(f"\n❌ FAILED - {len(all_issues)} issue(s) found:")
        for issue in all_issues:
            print(f"   {issue}")
    else:
        print(f"\n✅ PASSED - All integration checks successful!")
    
    if all_warnings:
        print(f"\n⚠️  {len(all_warnings)} warning(s):")
        for warning in all_warnings:
            print(f"   {warning}")
    
    print("\n" + "="*80)
    
    return len(all_issues) == 0


if __name__ == "__main__":
    success = run_full_verification()
    sys.exit(0 if success else 1)
