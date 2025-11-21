#!/bin/bash
# Local test script for HTML email with FORCE_EMAIL mode
cd /Users/danystefan/Documents/workspace/my_trading_strat
FORCE_EMAIL=true /Users/danystefan/Documents/workspace/my_trading_strat/.venv/bin/python rsi_double_dca_backtest/monitor_strategy.py