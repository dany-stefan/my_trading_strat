#!/usr/bin/env python3
"""
Batch Execution Script - PROD
==============================

Runs all PROD backtest scripts, report generators, and verification in optimized order.
Groups operations to minimize redundant computations.

Execution Order:
1. Core backtest (generates CSV files)
2. Variant comparisons (uses CSV files)
3. Visualization generators (uses CSV files)
4. Report generators (uses CSV files)
5. Integration verification (validates everything)

Usage:
    python run_all_batch.py
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime


def run_script(script_name, description):
    """Run a Python script and report status."""
    print(f"\n{'='*80}")
    print(f"Running: {description}")
    print(f"Script: {script_name}")
    print(f"{'='*80}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        if result.returncode != 0:
            print(f"\n❌ FAILED with exit code {result.returncode}")
            if result.stderr:
                print(f"Error output:\n{result.stderr}")
            return False
        else:
            print(f"\n✅ SUCCESS")
            return True
            
    except subprocess.TimeoutExpired:
        print(f"\n❌ TIMEOUT - Script took longer than 5 minutes")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False


def main():
    """Run all scripts in optimized batch order."""
    print("\n" + "="*80)
    print("PROD FOLDER - BATCH EXECUTION")
    print("="*80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Working Directory: {Path.cwd()}")
    
    results = {}
    
    # =========================================================================
    # PHASE 1: Core Backtest (Generates all CSV files)
    # =========================================================================
    print("\n" + "="*80)
    print("PHASE 1: CORE BACKTEST")
    print("="*80)
    
    success = run_script(
        "rsi_calendar_date_backtest.py",
        "Calendar Date Backtest (3rd & 17th) - Generates equity CSVs"
    )
    results["Core Backtest"] = success
    
    if not success:
        print("\n❌ Core backtest failed - cannot continue")
        return False
    
    # =========================================================================
    # PHASE 2: Variant Comparisons (Uses CSV files from Phase 1)
    # =========================================================================
    print("\n" + "="*80)
    print("PHASE 2: VARIANT COMPARISONS")
    print("="*80)
    
    if Path("rsi_variants_backtest.py").exists():
        success = run_script(
            "rsi_variants_backtest.py",
            "Strategy Variant Comparisons"
        )
        results["Variant Comparisons"] = success
    else:
        print("⚠️  rsi_variants_backtest.py not found - skipping")
        results["Variant Comparisons"] = None
    
    if Path("strategy_comparison.py").exists():
        success = run_script(
            "strategy_comparison.py",
            "Strategy Comparison Module Test"
        )
        results["Strategy Comparison Test"] = success
    else:
        print("⚠️  strategy_comparison.py not runnable as main - skipping")
        results["Strategy Comparison Test"] = None
    
    # =========================================================================
    # PHASE 3: Visualization Generation (Uses CSV files from Phase 1)
    # =========================================================================
    print("\n" + "="*80)
    print("PHASE 3: VISUALIZATIONS")
    print("="*80)
    
    viz_scripts = [
        ("generate_cash_pool_visualization.py", "Cash Pool Visualization"),
        ("generate_rsi_timeline_chart.py", "RSI Timeline Chart"),
        ("generate_hit_miss_charts.py", "Hit/Miss Charts"),
    ]
    
    for script, desc in viz_scripts:
        if Path(script).exists():
            success = run_script(script, desc)
            results[desc] = success
        else:
            print(f"⚠️  {script} not found - skipping")
            results[desc] = None
    
    # =========================================================================
    # PHASE 4: Report Generation (Uses CSV files and metrics)
    # =========================================================================
    print("\n" + "="*80)
    print("PHASE 4: REPORT GENERATION")
    print("="*80)
    
    if Path("generate_performance_report.py").exists():
        success = run_script(
            "generate_performance_report.py",
            "Comprehensive Performance Report"
        )
        results["Performance Report"] = success
    else:
        print("⚠️  generate_performance_report.py not found - skipping")
        results["Performance Report"] = None
    
    # =========================================================================
    # PHASE 5: UPDATE METRICS REFERENCE
    # =========================================================================
    print("\n" + "="*80)
    print("PHASE 5: UPDATE METRICS REFERENCE")
    print("="*80)
    
    if Path("update_metrics_reference.py").exists():
        success = run_script(
            "update_metrics_reference.py",
            "Update METRICS_REFERENCE.json with Latest Data"
        )
        results["Metrics Reference Update"] = success
    else:
        print("⚠️  update_metrics_reference.py not found - skipping")
        results["Metrics Reference Update"] = None
    
    # =========================================================================
    # PHASE 6: RSI VERIFICATION UPDATE
    # =========================================================================
    print("\n" + "="*80)
    print("PHASE 6: RSI VERIFICATION UPDATE")
    print("="*80)
    
    # =========================================================================
    # PHASE 6: RSI VERIFICATION UPDATE
    # =========================================================================
    print("\n" + "="*80)
    print("PHASE 6: RSI VERIFICATION UPDATE")
    print("="*80)
    
    if Path("update_rsi_verification.py").exists():
        success = run_script(
            "update_rsi_verification.py",
            "Update RSI Verification List with Missing Dates"
        )
        results["RSI Verification Update"] = success
    else:
        print("⚠️  update_rsi_verification.py not found - skipping")
        results["RSI Verification Update"] = None
    
    # =========================================================================
    # PHASE 7: INTEGRATION VERIFICATION (Validates all outputs)
    # =========================================================================
    print("\n" + "="*80)
    print("PHASE 7: INTEGRATION VERIFICATION")
    print("="*80)
    
    success = run_script(
        "verify_integration.py",
        "Integration Verification - Data Flow Check"
    )
    results["Integration Verification"] = success
    
    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================
    print("\n" + "="*80)
    print("BATCH EXECUTION SUMMARY")
    print("="*80)
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\nResults:")
    for task, status in results.items():
        if status is True:
            print(f"   ✅ {task}")
        elif status is False:
            print(f"   ❌ {task}")
        else:
            print(f"   ⚠️  {task} (skipped)")
    
    # Count results
    passed = sum(1 for s in results.values() if s is True)
    failed = sum(1 for s in results.values() if s is False)
    skipped = sum(1 for s in results.values() if s is None)
    
    print(f"\nSummary: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed > 0:
        print("\n❌ BATCH EXECUTION FAILED")
        return False
    else:
        print("\n✅ BATCH EXECUTION SUCCESSFUL")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
