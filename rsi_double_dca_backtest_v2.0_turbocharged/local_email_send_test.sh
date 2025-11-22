#!/bin/bash
# Local test script for TURBO v2.0 HTML email with FORCE_EMAIL mode
# This sends a test email with enhanced visualizations and TURBO branding
cd /Users/danystefan/Documents/workspace/my_trading_strat/rsi_double_dca_backtest_v2.0_turbocharged
FORCE_EMAIL=true /Users/danystefan/Documents/workspace/my_trading_strat/.venv/bin/python monitor_strategy.py