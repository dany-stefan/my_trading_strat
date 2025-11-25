# Rainy Pool ROI Tracking - Deployment Checklist

## Feature Summary

Starting December 3, 2025, production emails will track cumulative rainy day contributions and their real-time ROI.

## Pre-Deployment Status

### ✅ Completed
- [x] Added rainy pool ROI calculation to `email_generator.py`
- [x] Conditional display logic (production only, not test emails)
- [x] Integration with existing `strategy_tracking.json` structure
- [x] HTML email formatting support via `email_formatter.py`
- [x] Testing with sample rainy buy data
- [x] Documentation created (`README_RAINY_POOL_TRACKING.md`)

### ✅ Verified
- [x] Calculations accurate (tested with 2-3 sample buys)
- [x] Production mode shows rainy pool section
- [x] Test mode hides rainy pool section
- [x] HTML rendering works correctly
- [x] Plain text formatting intact

## December 3, 2025 Deployment

### What Happens

**First Email (Dec 3, 2025)**:
- Monitor_strategy.py runs at 17:00 UTC (GitHub Actions)
- Checks RSI SMA(7) for rainy day condition
- If rainy: Executes buy and records to `strategy_tracking.json`
- Generates email with rainy pool tracking section

**Expected Email Content**:

**Scenario 1: Not Rainy Day (RSI SMA ≥ 45)**
- Rainy pool section shows: $0 invested, $0 value, 0% ROI, 0 buys
- (Won't appear because `rainy_buys[]` is empty)

**Scenario 2: First Rainy Day (RSI SMA < 45)**
```
💧 RAINY POOL PERFORMANCE TRACKER
| Metric | Value |
|---|---|
| Total Rainy Contributions | $150.00 CAD |
| Average Rainy Buy Price | $XXX.XX USD |
| Current SPY Price | $XXX.XX USD |
| Current Rainy Pool Value | $150.00 CAD |
| Rainy Pool Profit | $0.00 CAD |
| Rainy Pool ROI | 0.00% |
| Rainy Buys Deployed | 1 |
```

### Files Involved

**Modified Files**:
1. `email_generator.py` (lines 1-50): Added rainy pool calculation logic
2. `README_RAINY_POOL_TRACKING.md`: Feature documentation

**Unchanged Files** (already compatible):
- `monitor_strategy.py`: Records rainy buys with price data
- `strategy_tracking.json`: Stores rainy buy history
- `email_formatter.py`: Converts markdown to HTML
- `.github/workflows/*.yml`: GitHub Actions workflows

## Post-Deployment Monitoring

### First Week (Dec 3-10, 2025)

**Check #1: December 3**
- [ ] Email received at expected time
- [ ] Rainy pool section appears (if rainy day)
- [ ] ROI calculation correct (0% on first buy)

**Check #2: December 17**
- [ ] Email received
- [ ] Rainy pool shows cumulative data (if Dec 3 was rainy)
- [ ] ROI updates based on current SPY price

### First Month (Dec 2025 - Jan 2026)

Track emails on: Dec 3, Dec 17, Jan 1 (→ Jan 2), Jan 15 (→ Jan 17)

**Validate**:
- [ ] Cumulative rainy contributions accurate
- [ ] ROI calculations match manual verification
- [ ] HTML formatting renders correctly
- [ ] No errors in GitHub Actions logs

## Rollback Plan

If issues arise, revert `email_generator.py` to previous version:

```bash
cd rsi_double_dca_backtest_PROD
git log --oneline email_generator.py  # Find previous commit
git checkout <commit-hash> email_generator.py
git commit -m "Rollback rainy pool tracking"
git push
```

**Impact**: Emails will still send, just without rainy pool tracking section.

## Testing Commands

### Test Production Email (with rainy buys)
```bash
cd rsi_double_dca_backtest_PROD
python3 test_rainy_pool_tracking.py
```

Expected: ✅ Rainy pool section visible in production mode

### Test Simulation Email (without rainy buys)
```bash
cd rsi_double_dca_backtest_PROD
python3 simulate_payday_email.py
```

Expected: ❌ Rainy pool section hidden in test mode

## Data Verification

### Manual ROI Calculation

To verify email calculations, use this formula:

```python
# From strategy_tracking.json
rainy_buys = [
    {'date': '2025-03-03', 'price': 520.0, 'amount': 150.0},
    # ... more buys
]

total_invested = sum(buy['amount'] for buy in rainy_buys)
total_shares = sum(buy['amount'] / buy['price'] for buy in rainy_buys)

# Get current SPY price (e.g., from Yahoo Finance)
current_price = 668.73

current_value = total_shares * current_price
profit = current_value - total_invested
roi = (profit / total_invested) * 100

print(f"Total Invested: ${total_invested:,.2f}")
print(f"Current Value: ${current_value:,.2f}")
print(f"ROI: {roi:.2f}%")
```

## Key Metrics to Monitor

### Health Indicators

**✅ Healthy**:
- ROI calculations match manual verification
- Emails send on schedule (3rd/17th)
- `strategy_tracking.json` updates correctly
- No GitHub Actions failures

**⚠️ Warning**:
- ROI calculation off by >1%
- Missing rainy buy records
- Email delays >2 hours

**🚨 Critical**:
- Emails not sending
- `strategy_tracking.json` corruption
- GitHub Actions workflow errors
- Incorrect rainy buy execution

## Support Resources

- **Feature Documentation**: `README_RAINY_POOL_TRACKING.md`
- **Email Generator Code**: `email_generator.py` (lines 1-160)
- **Test Script**: `test_rainy_pool_tracking.py`
- **Tracking Data**: `strategy_tracking.json`

## Timeline

- **Nov 24, 2025**: Feature implemented and tested
- **Dec 3, 2025**: First deployment (production email)
- **Dec 17, 2025**: Second email (cumulative tracking test)
- **Jan 2, 2026**: Third email (verify multi-period tracking)

## Success Criteria

Feature is successful if:

1. ✅ Production emails show rainy pool tracking
2. ✅ Test emails hide rainy pool tracking
3. ✅ ROI calculations accurate within 0.01%
4. ✅ No email delivery failures
5. ✅ No GitHub Actions errors
6. ✅ `strategy_tracking.json` maintains data integrity

---

**Deployed By**: GitHub Copilot Agent  
**Deployment Date**: November 24, 2025  
**First Production Run**: December 3, 2025 at 17:00 UTC
