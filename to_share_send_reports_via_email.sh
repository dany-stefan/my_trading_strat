#!/bin/bash

# Send trading strategy reports via macOS Mail (as ZIP)
# Usage: ./to_share_send_reports_via_email.sh [recipient_email]

WORKSPACE_DIR="/Users/danystefan/Documents/workspace/my_trading_strat"
FILE_LIST="$WORKSPACE_DIR/to_share_via_email_reports.txt"
ZIP_NAME="Trading_Strategy_Reports_$(date '+%Y-%m-%d').zip"
ZIP_PATH="$WORKSPACE_DIR/$ZIP_NAME"

# Email configuration
RECIPIENT="${1:-stefan_dany@icloud.com}"  # Default to your iCloud if no argument
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

📈 VISUALIZATIONS (15 charts):
• Strategy comparison charts
• Cash pool analysis
• RSI timeline and hit/miss patterns
• Rainy period analytics
• SPY price with rainy deployments
• Cumulative value growth

These reports cover the complete backtest analysis (2003-2025) for the RSI-based DCA rainy day strategy.

Best regards,
Trading Strategy Automation"

# Check if file list exists
if [ ! -f "$FILE_LIST" ]; then
    echo "Error: File list not found at $FILE_LIST"
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

# Remove old ZIP if exists
[ -f "$ZIP_PATH" ] && rm "$ZIP_PATH"

# Create temporary directory for organized ZIP structure
TEMP_DIR=$(mktemp -d)
REPORTS_DIR="$TEMP_DIR/Trading_Strategy_Reports"
mkdir -p "$REPORTS_DIR"

echo "=== Gathering report files ==="
FILE_COUNT=0
while IFS= read -r file; do
    # Skip empty lines and comments
    [[ -z "$file" || "$file" =~ ^# ]] && continue
    
    # Build full path
    FULL_PATH="$WORKSPACE_DIR/$file"
    
    # Check if file exists
    if [ -f "$FULL_PATH" ]; then
        echo "✓ Found: $file"
        # Copy file to temp directory, preserving directory structure
        DEST_PATH="$REPORTS_DIR/$file"
        mkdir -p "$(dirname "$DEST_PATH")"
        cp "$FULL_PATH" "$DEST_PATH"
        ((FILE_COUNT++))
    else
        echo "✗ Missing: $file"
    fi
done < "$FILE_LIST"

echo ""
echo "=== Creating ZIP archive ==="
cd "$TEMP_DIR"
zip -r "$ZIP_PATH" "Trading_Strategy_Reports" -q

# Clean up temp directory
rm -rf "$TEMP_DIR"

if [ ! -f "$ZIP_PATH" ]; then
    echo "❌ Error creating ZIP file"
    exit 1
fi

ZIP_SIZE=$(du -h "$ZIP_PATH" | cut -f1)
echo "✅ Created ZIP: $ZIP_NAME ($ZIP_SIZE)"
echo "📦 Contains: $FILE_COUNT files"
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
    echo "📦 Contains: $FILE_COUNT files (8 markdown + 15 PNG charts)"
    echo ""
    echo "Please review the email in Mail.app and click Send when ready."
    echo ""
    echo "Note: ZIP file saved at: $ZIP_PATH"
else
    echo ""
    echo "❌ Error creating email draft"
    exit 1
fi
