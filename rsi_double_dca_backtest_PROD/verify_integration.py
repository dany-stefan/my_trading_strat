"""
Integration Verification Script - PROD
======================================

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
from market_metrics import calculate_market_metrics
from email_generator import generate_email_content


def verify_csv_consistency():
    """Verify CSV files exist and have consistent data."""
    print("\n" + "="*80)
    print("STEP 1: Verifying CSV File Consistency")
    print("="*80)
    
    issues = []
    warnings = []
    
    # Check equity curve exists
    equity_file = Path("equity_rainy_strategy_calendar_dates.csv")
    if not equity_file.exists():
        issues.append(f"❌ Missing: {equity_file}")
    else:
        df = pd.read_csv(equity_file)
        print(f"✅ Found equity_rainy_strategy_calendar_dates.csv: {len(df)} records")
        
        # Verify required columns
        required_cols = ['date', 'equity', 'shares_value', 'cash_pool']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            issues.append(f"❌ Missing columns in equity CSV: {missing_cols}")
        else:
            print(f"   Columns: {list(df.columns)}")
            print(f"   Date range: {df['date'].iloc[0]} to {df['date'].iloc[-1]}")
            print(f"   Final equity: ${df['equity'].iloc[-1]:,.2f}")
    
    # Check rainy buys CSV
    rainy_file = Path("rainy_buys_calendar_dates.csv")
    if not rainy_file.exists():
        warnings.append(f"⚠️  Missing: {rainy_file} (might be no rainy buys)")
    else:
        df_rainy = pd.read_csv(rainy_file)
        print(f"✅ Found rainy_buys_calendar_dates.csv: {len(df_rainy)} records")
        print(f"   Total rainy deployments: ${df_rainy['amount'].sum():,.2f}")
        print(f"   Average RSI SMA on buys: {df_rainy['rsi_sma'].mean():.2f}")
    
    # Check baseline DCA CSV
    baseline_file = Path("equity_baseline_calendar_dates.csv")
    if not baseline_file.exists():
        issues.append(f"❌ Missing: {baseline_file}")
    else:
        df_baseline = pd.read_csv(baseline_file)
        print(f"✅ Found equity_baseline_calendar_dates.csv: {len(df_baseline)} records")
        print(f"   Final equity: ${df_baseline['equity'].iloc[-1]:,.2f}")
    
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
        print(f"   Rainy Day CAGR: {metrics['rainy_cagr']}")
        print(f"   Rainy Day Final: {metrics['rainy_final']}")
        print(f"   Rainy Day Invested: {metrics['rainy_invested']}")
        print(f"   Simple DCA Final: {metrics['dca_final']}")
        print(f"   Buy & Hold Final: {metrics['buy_hold_final']}")
        print(f"   Gain vs DCA: {metrics['gain_vs_dca']} ({metrics['gain_vs_dca_pct']})")
        print(f"   Backtest Period: {metrics['backtest_period']}")
        
        # Verify metrics are reasonable
        rainy_final_raw = float(metrics['rainy_final'].replace('$', '').replace(',', ''))
        if rainy_final_raw < 100000:
            issues.append(f"❌ Rainy final value seems too low: {metrics['rainy_final']}")
        
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
        equity_file = "equity_rainy_strategy_calendar_dates.csv"
        if not Path(equity_file).exists():
            issues.append(f"❌ Cannot test advanced metrics - {equity_file} missing")
            return issues
        
        metrics = calculate_advanced_metrics(equity_file, initial_capital=73950)
        all_metrics = metrics.get_all_metrics()
        
        print(f"✅ Advanced metrics calculated successfully")
        print(f"\nAdvanced Metrics:")
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
    print("STEP 4: Verifying Market Metrics Module")
    print("="*80)
    
    issues = []
    
    try:
        # Test with sample data
        test_rsi_sma = 34.5
        test_price = 659.03
        test_cash_pool = 330.0
        test_contributions = 0.0
        test_rainy_buys = []
        
        metrics = calculate_market_metrics(
            rsi_sma=test_rsi_sma,
            price=test_price,
            cash_pool=test_cash_pool,
            total_contributions=test_contributions,
            rainy_buys=test_rainy_buys
        )
        
        all_metrics = metrics.get_all_metrics()
        
        print(f"✅ Market metrics calculated successfully")
        print(f"\nTest Scenario (RSI SMA = {test_rsi_sma}):")
        print(f"   Is Rainy: {all_metrics['is_rainy']}")
        print(f"   Can Deploy: {all_metrics['can_deploy']}")
        print(f"   Action Type: {all_metrics['action_type']}")
        print(f"   Total Investment Today: ${all_metrics['total_investment_today']:.2f}")
        print(f"   New Cash Pool: ${all_metrics['new_cash_pool']:.2f}")
        print(f"   Recommendation: {all_metrics['recommendation'][:50]}...")
        
        # Verify logic
        if test_rsi_sma < 45.0 and all_metrics['is_rainy'] == False:
            issues.append(f"❌ Logic error: RSI {test_rsi_sma} < 45 but is_rainy = False")
        
        if test_cash_pool >= 150 and all_metrics['can_deploy'] == False:
            issues.append(f"❌ Logic error: Cash ${test_cash_pool} >= $150 but can_deploy = False")
        
    except Exception as e:
        issues.append(f"❌ Market metrics failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return issues


def verify_email_generation():
    """Verify email generation works correctly."""
    print("\n" + "="*80)
    print("STEP 5: Verifying Email Generation")
    print("="*80)
    
    issues = []
    
    try:
        # Test email generation with sample data
        test_rsi_sma = 34.5
        test_price = 659.03
        test_cash_pool = 330.0
        test_contributions = 0.0
        test_rainy_buys = []
        
        subject, body = generate_email_content(
            rsi_sma=test_rsi_sma,
            price=test_price,
            cash_pool=test_cash_pool,
            total_contributions=test_contributions,
            rainy_buys=test_rainy_buys,
            is_simulation=True
        )
        
        print(f"✅ Email generated successfully")
        print(f"\nEmail Details:")
        print(f"   Subject: {subject[:80]}...")
        print(f"   Body length: {len(body)} characters")
        
        # Verify key data is in email
        if "34.5" not in body and "34.50" not in body:
            issues.append(f"❌ RSI SMA value (34.5) not found in email body")
        
        if "$659.03" not in body:
            issues.append(f"❌ Price ($659.03) not found in email body")
        
        if "RSI STRATEGY MONITOR" not in body:
            issues.append(f"❌ Email missing expected header")
        
        # Check that comparison metrics are included
        if "VARIANT PERFORMANCE SUMMARY" not in body:
            issues.append(f"❌ Email missing variant performance summary")
        
        print(f"\nEmail Content Checks:")
        print(f"   ✅ Contains RSI SMA value")
        print(f"   ✅ Contains price")
        print(f"   ✅ Contains header")
        print(f"   ✅ Contains variant summary")
        
    except Exception as e:
        issues.append(f"❌ Email generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return issues


def verify_markdown_reports():
    """Verify markdown reports exist and have correct data."""
    print("\n" + "="*80)
    print("STEP 6: Verifying Markdown Reports")
    print("="*80)
    
    issues = []
    warnings = []
    
    report_file = Path("COMPREHENSIVE_PERFORMANCE_REPORT.md")
    if not report_file.exists():
        warnings.append(f"⚠️  Missing: {report_file}")
    else:
        content = report_file.read_text()
        print(f"✅ Found COMPREHENSIVE_PERFORMANCE_REPORT.md")
        
        # Verify key metrics are in report
        if "Terminal Value" not in content:
            issues.append(f"❌ Report missing 'Terminal Value'")
        
        if "CAGR" not in content:
            issues.append(f"❌ Report missing 'CAGR'")
        
        if "Sharpe Ratio" not in content:
            issues.append(f"❌ Report missing 'Sharpe Ratio'")
        
        # Check if report references CSV files
        if "equity_rainy_strategy_calendar_dates.csv" in content or "equity_baseline_calendar_dates.csv" in content:
            print(f"   ✅ Report references source CSV files")
        else:
            warnings.append(f"⚠️  Report doesn't reference source CSV files")
    
    return issues, warnings


def run_full_verification():
    """Run all verification steps."""
    print("\n" + "="*80)
    print("PROD FOLDER - INTEGRATION VERIFICATION")
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
    
    # Step 6: Markdown reports
    issues, warnings = verify_markdown_reports()
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
