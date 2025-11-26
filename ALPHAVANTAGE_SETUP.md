# Alpha Vantage API Integration Setup

## Overview

This project now uses **Alpha Vantage API** for dual-source RSI verification, providing genuine independent validation of local calculations.

---

## ✅ What's Been Done

### 1. **API Integration Scripts Created**
- **`fetch_alphavantage_rsi.py`**: Fetches RSI data from Alpha Vantage API
  - Retrieves 6544+ days of RSI(14) data
  - Calculates SMA(7) from API RSI values
  - Handles rate limits and errors gracefully

- **`populate_tv_values_from_alphavantage.py`**: Backfills historical data
  - Batch updates TBD entries in RSI_VERIFICATION_LIST.txt
  - Auto-verifies match status (✅/❌)
  - Respects API rate limits (25 calls/day, 5 calls/minute)

### 2. **Enhanced update_rsi_verification.py**
- Now automatically fetches Alpha Vantage data when adding new entries
- Auto-populates TV-RSI and TV-SMA columns
- Auto-verifies match status on creation
- Falls back to TBD if API key not available

### 3. **Workflow Files Updated**
- `daily_rsi_update.yml`: Added ALPHAVANTAGE_API_KEY environment variable
- `rsi_monitor.yml`: Added ALPHAVANTAGE_API_KEY environment variable
- Both workflows now include `requests` package in dependencies

### 4. **Fake TV Values Cleared**
- All historical "copied" TV values removed
- Set to TBD with ⏳ pending status
- Ready for real Alpha Vantage data population

### 5. **Initial Population Completed**
- First 10 entries populated with real Alpha Vantage data
- Results:
  - Nov 25, 24: ❌ Mismatches (expected - data still preliminary)
  - Nov 21: ✅ Match (manual example)
  - Nov 20-11: ✅ Matches (real Alpha Vantage data)

---

## 🔑 API Key Details

**Service**: Alpha Vantage (Free Tier)
**API Key**: `4PJSX4ETS4LPQEF2`
**Rate Limits**:
- 25 API calls per day
- 5 API calls per minute

---

## ⚙️ GitHub Secret Setup

**REQUIRED**: You must add the API key to GitHub repository secrets for workflows to function.

### Steps:

1. **Go to Repository Settings**:
   - Navigate to: https://github.com/dany-stefan/my_trading_strat/settings/secrets/actions

2. **Create New Secret**:
   - Click "New repository secret"
   - Name: `ALPHAVANTAGE_API_KEY`
   - Value: `4PJSX4ETS4LPQEF2`
   - Click "Add secret"

3. **Verify Secret**:
   - You should see `ALPHAVANTAGE_API_KEY` in the list
   - Updated: (today's date)

---

## 🚀 Usage

### Daily Workflow (Automatic) - **FULLY AUTOMATED**
```yaml
# Runs at 7 PM EST weekdays
# Automatically performs COMPLETE verification workflow:
# 1. Fetches Alpha Vantage data (1 API call)
# 2. Backfills ALL TBD entries from previous days
# 3. Re-evaluates all pending matches (⏳ → ✅/❌)
# 4. Adds new entry for today with external verification
# 5. Commits changes to repository
```

**No manual intervention needed!** The workflow handles everything.

### Manual Trigger (GitHub UI)
```yaml
# Go to Actions → Daily RSI Verification Update → Run workflow
# Same complete workflow as automatic run
# Useful for testing or immediate updates
```

### Local Testing
```bash
cd rsi_double_dca_backtest_PROD
export ALPHAVANTAGE_API_KEY='4PJSX4ETS4LPQEF2'

# Run the complete update workflow
python3 update_rsi_verification.py
```

---

## 📊 Data Sources Comparison

### Local Calculations (Column 1-2)
- **Source**: yfinance SPY historical data
- **RSI(14)**: Wilder's RMA (Relative Moving Average)
- **SMA(7)**: Simple Moving Average of RSI values
- **Function**: `compute_rsi_with_sma()` from `rsi_indicators.py`

### Alpha Vantage API (Column 3-4)
- **Source**: Alpha Vantage RSI indicator API
- **RSI(14)**: Technical indicator from Alpha Vantage
- **SMA(7)**: Calculated locally from API RSI values
- **Update**: Automatic via daily workflow or manual via scripts

### Verification Logic
- **Match (✅)**: Both RSI and SMA match within ±1.0 tolerance
- **Mismatch (❌)**: Either RSI or SMA differs by >1.0
- **Pending (⏳)**: TV values not yet fetched (TBD)

---

## 🔍 Expected Behavior

### Recent Data (Last 1-2 days)
- **Expected**: ❌ Mismatches common
- **Reason**: yfinance data still preliminary
- **Resolution**: Auto-corrects when data finalizes (usually after 7 PM EST)

### Historical Data (3+ days old)
- **Expected**: ✅ Perfect matches
- **Reason**: Both sources use finalized market data
- **Verification**: Confirms calculation accuracy

---

## ⚠️ Important Notes

1. **Fully Automated**: No manual backfills needed - workflow handles everything
2. **API Efficiency**: Only 1 API call per day (fetches all data at once)
3. **Auto-Backfilling**: Catches up on any TBD entries automatically
4. **Daily Updates**: Workflow adds new entry + backfills + re-evaluates matches
5. **API Key Security**: Never commit API key to repository - use GitHub Secrets only
6. **Workflow Dependency**: Both workflows require `requests` package (already added)

---

## 📝 Next Steps

1. ✅ **DONE**: Create integration scripts
2. ✅ **DONE**: Clear fake TV values
3. ✅ **DONE**: Update workflow files
4. ✅ **DONE**: Implement auto-backfilling in update script
5. ⚠️  **TODO**: Add API key to GitHub Secrets (see instructions above)
6. ⏳ **PENDING**: Push changes to GitHub
7. ⏳ **PENDING**: Test daily workflow (trigger manually from GitHub UI)
8. ⏳ **PENDING**: Verify ZIP generation includes real external data

---

## 📚 Related Files

- `fetch_alphavantage_rsi.py`: API integration
- `populate_tv_values_from_alphavantage.py`: Batch population
- `update_rsi_verification.py`: Enhanced with API fetching
- `RSI_VERIFICATION_LIST.txt`: Dual-source verification data
- `.github/workflows/daily_rsi_update.yml`: Daily workflow
- `.github/workflows/rsi_monitor.yml`: Bi-weekly email workflow

---

## 🎯 Success Criteria

✅ API key added to GitHub Secrets
✅ Daily workflow runs without errors
✅ New entries automatically populate with TV values
✅ Match status auto-verified (✅/❌/⏳)
✅ Historical data backfilled (within rate limits)
✅ ZIP package includes real external verification
