#!/bin/bash

# Send trading strategy reports via macOS Mail
# Usage: ./send_reports_via_email.sh [recipient_email]

WORKSPACE_DIR="/Users/danystefan/Documents/workspace/my_trading_strat"
FILE_LIST="$WORKSPACE_DIR/to_share_via_email_reports.txt"

# Email configuration
RECIPIENT="${1:-danystefan@icloud.com}"  # Default to your iCloud if no argument
SUBJECT="Trading Strategy Performance Reports - $(date '+%B %d, %Y')"
BODY="Hi,

Attached are the comprehensive trading strategy performance reports including:

• PROD Strategy Analysis
• TURBO v2.0 Strategy Analysis  
• Strategy Performance Summary
• RSI Verification Results
• Rainy Contribution Analysis
• Summary Analysis
• Hit/Miss Charts Documentation
• Comprehensive Performance Report

These reports cover the complete backtest analysis (2003-2025) for the RSI-based DCA rainy day strategy.

Best regards,
Trading Strategy Automation"

# Check if file list exists
if [ ! -f "$FILE_LIST" ]; then
    echo "Error: File list not found at $FILE_LIST"
    exit 1
fi

# Build attachment paths
ATTACHMENTS=""
echo "=== Gathering report files ==="
while IFS= read -r file; do
    # Skip empty lines and comments
    [[ -z "$file" || "$file" =~ ^# ]] && continue
    
    # Build full path
    FULL_PATH="$WORKSPACE_DIR/$file"
    
    # Check if file exists
    if [ -f "$FULL_PATH" ]; then
        echo "✓ Found: $file"
        ATTACHMENTS="$ATTACHMENTS -a \"$FULL_PATH\""
    else
        echo "✗ Missing: $file"
    fi
done < "$FILE_LIST"

echo ""
echo "=== Creating email with attachments ==="

# Create AppleScript to send email via Mail.app
osascript <<EOF
tell application "Mail"
    set newMessage to make new outgoing message with properties {subject:"$SUBJECT", content:"$BODY", visible:true}
    tell newMessage
        make new to recipient at end of to recipients with properties {address:"$RECIPIENT"}
        
        -- Add attachments
$(while IFS= read -r file; do
    [[ -z "$file" || "$file" =~ ^# ]] && continue
    FULL_PATH="$WORKSPACE_DIR/$file"
    if [ -f "$FULL_PATH" ]; then
        echo "        make new attachment with properties {file name:POSIX file \"$FULL_PATH\"} at after the last paragraph"
    fi
done < "$FILE_LIST")
    end tell
    
    activate
end tell
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Email draft created successfully in Mail.app"
    echo "📧 Recipient: $RECIPIENT"
    echo "📎 Attachments: $(wc -l < "$FILE_LIST" | xargs) files"
    echo ""
    echo "Please review the email in Mail.app and click Send when ready."
else
    echo ""
    echo "❌ Error creating email draft"
    exit 1
fi
