#!/bin/bash

# Send trading strategy reports via macOS Mail (as ZIP)
# Usage: ./to_share_send_reports_via_email.sh [recipient_email]

WORKSPACE_DIR="/Users/danystefan/Documents/workspace/my_trading_strat"
FILE_LIST="$WORKSPACE_DIR/to_share_via_email_reports.txt"

# ZIP file with timestamp in workspace root
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
ZIP_NAME="trading_strategy_reports_${TIMESTAMP}.zip"
ZIP_PATH="$WORKSPACE_DIR/$ZIP_NAME"

# Email configuration
RECIPIENT="${1:-stefan_dany@icloud.com}"
SUBJECT="Trading Strategy Performance Reports - $(date '+%B %d, %Y')"
BODY="Hi,

Attached is a comprehensive trading strategy performance report package (ZIP file) including:

📊 REPORTS:
• PROD Strategy Analysis
• TURBO v2.0 Strategy Analysis  
• Strategy Performance Summary
• RSI Verification Results
• Rainy Contribution Analysis
• Summary Analysis
• Hit/Miss Charts Documentation
• Comprehensive Performance Report

📈 VISUALIZATIONS (8 PNG charts):
• Strategy comparison charts
• Cash pool analysis
• RSI timeline and hit/miss patterns
• Rainy period analytics
• SPY price with rainy deployments

�� DATA & METRICS:
• Rainy analytics JSON
• Metrics reference

These reports cover the complete backtest analysis (2003-2025) for the RSI-based DCA rainy day strategy.

Best regards,
Trading Strategy Automation"

# Check if file list exists
if [ ! -f "$FILE_LIST" ]; then
    echo "❌ Error: File list not found at $FILE_LIST"
    exit 1
fi

# Update RSI Verification List before creating ZIP
echo "=== Updating RSI Verification List ==="
cd "$WORKSPACE_DIR/rsi_double_dca_backtest_PROD"
python3 update_rsi_verification.py
if [ $? -eq 0 ]; then
    echo "✅ RSI Verification List updated"
else
    echo "⚠️  Warning: Failed to update RSI Verification List"
fi
cd "$WORKSPACE_DIR"
echo ""

# Clean up old ZIP files in workspace root
echo "🧹 Cleaning up old ZIP files..."
OLD_ZIPS=$(ls "$WORKSPACE_DIR"/trading_strategy_reports_*.zip 2>/dev/null | wc -l)
if [ "$OLD_ZIPS" -gt 0 ]; then
    rm "$WORKSPACE_DIR"/trading_strategy_reports_*.zip
    echo "   Removed $OLD_ZIPS old ZIP file(s)"
else
    echo "   No old ZIP files found"
fi
echo ""

# Create ZIP file
echo "📦 Creating ZIP archive: $ZIP_NAME"
FILE_COUNT=0
while IFS= read -r file; do
    [[ -z "$file" || "$file" =~ ^# ]] && continue
    FULL_PATH="$WORKSPACE_DIR/$file"
    if [ -f "$FULL_PATH" ]; then
        echo "  ✅ Added: $file"
        ((FILE_COUNT++))
    else
        echo "  ⚠️  Missing: $file"
    fi
done < "$FILE_LIST"

# Create the ZIP using the file list
cd "$WORKSPACE_DIR"
zip -q "$ZIP_PATH" -@ < "$FILE_LIST"

if [ ! -f "$ZIP_PATH" ]; then
    echo "❌ Error creating ZIP file"
    exit 1
fi

ZIP_SIZE=$(du -h "$ZIP_PATH" | cut -f1)
echo ""
echo "✅ Created: $ZIP_NAME ($ZIP_SIZE, $FILE_COUNT files)"
echo ""
echo "=== Creating email with ZIP attachment ==="

# Create AppleScript to send email via Mail.app
osascript <<EOF
tell application "Mail"
    set newMessage to make new outgoing message with properties {subject:"$SUBJECT", content:"$BODY", visible:true}
    tell newMessage
        make new to recipient at end of to recipients with properties {address:"$RECIPIENT"}
        make new attachment with properties {file name:POSIX file "$ZIP_PATH"} at after the last paragraph
    end tell
    activate
end tell
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Email draft created successfully in Mail.app"
    echo "📧 Recipient: $RECIPIENT"
    echo "📎 Attachment: $ZIP_NAME ($ZIP_SIZE)"
    echo "📦 Contains: $FILE_COUNT files (9 markdown + 8 PNG charts + 1 HTML + 1 JSON)"
    echo ""
    echo "Please review the email in Mail.app and click Send when ready."
    echo ""
    echo "Note: ZIP file saved at: $ZIP_PATH"
else
    echo ""
    echo "❌ Error creating email draft"
    exit 1
fi
