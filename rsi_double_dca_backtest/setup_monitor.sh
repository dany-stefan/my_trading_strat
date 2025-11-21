#!/bin/bash
# Setup script for RSI Strategy Monitor using macOS launchd

echo "RSI Strategy Monitor - Setup Script"
echo "===================================="
echo ""

PLIST_FILE="$HOME/Library/LaunchAgents/com.user.rsi_strategy_monitor.plist"
SOURCE_PLIST="/Users/danystefan/Documents/workspace/my_trading_strat/rsi_double_dca_backtest/com.user.rsi_strategy_monitor.plist"

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$HOME/Library/LaunchAgents"

# Copy the plist file
echo "1. Copying launch agent configuration..."
cp "$SOURCE_PLIST" "$PLIST_FILE"
echo "   ✅ Copied to: $PLIST_FILE"
echo ""

# Load the launch agent
echo "2. Loading launch agent..."
launchctl load "$PLIST_FILE"
echo "   ✅ Launch agent loaded"
echo ""

# Check status
echo "3. Checking status..."
launchctl list | grep com.user.rsi_strategy_monitor
echo ""

echo "✅ SETUP COMPLETE!"
echo ""
echo "Your script will now run daily at 10:00 AM"
echo "Even if your Mac was sleeping, it will run when it wakes up"
echo ""
echo "Useful commands:"
echo "  • Check status:  launchctl list | grep com.user.rsi_strategy_monitor"
echo "  • View logs:     tail -f /Users/danystefan/Documents/workspace/my_trading_strat/rsi_double_dca_backtest/monitor.log"
echo "  • Unload (stop): launchctl unload $PLIST_FILE"
echo "  • Reload:        launchctl unload $PLIST_FILE && launchctl load $PLIST_FILE"
echo ""
echo "Next scheduled run: Tomorrow at 10:00 AM (or next time your Mac is on at 10 AM)"
