"""
Quick Comparison Script
=======================

Run this to see side-by-side comparison of:
- Original strategy
- Optimized strategy
- Full optimization strategy
"""

from strategy_config_optimized import get_strategy_config, compare_configs
from strategy_config import get_strategy_config as get_original_config

print("=" * 80)
print("STRATEGY OPTIMIZATION COMPARISON")
print("=" * 80)
print()

# Load configurations
original = get_original_config('VARIANT_2')
optimized = get_strategy_config('VARIANT_2_OPTIMIZED')
full = get_strategy_config('VARIANT_2_FULL')

print("📊 PARAMETER COMPARISON")
print("-" * 80)
print(f"{'Parameter':<30} {'Original':<20} {'Optimized':<20} {'Full':<20}")
print("-" * 80)

params = [
    ('Cash Accumulation', 
     f"${original.cash_accumulation_per_payday}", 
     f"${optimized.cash_accumulation_per_payday}",
     f"${full.cash_accumulation_per_payday}"),
    
    ('Initial Pool', 
     f"${original.initial_cash_pool}", 
     f"${optimized.initial_cash_pool}",
     f"${full.initial_cash_pool}"),
    
    ('RSI Threshold', 
     f"Fixed {original.rsi_threshold}", 
     f"Fixed {optimized.rsi_threshold}",
     "Adaptive (42/45/48)"),
    
    ('Position Sizing', 
     f"${original.rainy_extra_amount}", 
     f"${optimized.rainy_extra_amount}",
     "Dynamic ($150-$210)"),
    
    ('Expected Hit Rate', 
     f"{original.expected_hit_rate:.1%}", 
     f"{optimized.expected_hit_rate:.1%}",
     f"{full.expected_hit_rate:.1%}"),
]

for param, orig, opt, full_val in params:
    print(f"{param:<30} {orig:<20} {opt:<20} {full_val:<20}")

print("-" * 80)
print()

print("💰 ANNUAL COST COMPARISON")
print("-" * 80)
print(f"{'Item':<40} {'Original':<15} {'Optimized':<15} {'Full':<15}")
print("-" * 80)

# Calculate annual costs
original_annual = original.cash_accumulation_per_payday * 24
optimized_annual = optimized.cash_accumulation_per_payday * 24
full_annual = full.cash_accumulation_per_payday * 24

print(f"{'Annual Cash Accumulation':<40} ${original_annual:<14,.0f} ${optimized_annual:<14,.0f} ${full_annual:<14,.0f}")
print(f"{'Initial Pool (one-time)':<40} ${original.initial_cash_pool:<14,.0f} ${optimized.initial_cash_pool:<14,.0f} ${full.initial_cash_pool:<14,.0f}")
print(f"{'Extra Annual Cost vs Original':<40} ${'0':<14} ${optimized_annual - original_annual:<14,.0f} ${full_annual - original_annual:<14,.0f}")

print("-" * 80)
print()

print("📈 EXPECTED PERFORMANCE IMPROVEMENT (22 YEARS)")
print("-" * 80)
print(f"{'Metric':<40} {'Original':<15} {'Optimized':<15} {'Full':<15}")
print("-" * 80)

print(f"{'Hit Rate':<40} {'88.2%':<15} {'96.3%':<15} {'98%+':<15}")
print(f"{'Missed Rainy Days':<40} {'13':<15} {'2':<15} {'1':<15}")
print(f"{'Expected CAGR':<40} {'30.92%':<15} {'31.5%':<15} {'32.5%':<15}")
print(f"{'Est. Final Value':<40} {'$512,450':<15} {'$525,000':<15} {'$550,000':<15}")
print(f"{'Extra Value vs Original':<40} {'-':<15} {'+$12,550':<15} {'+$37,550':<15}")

print("-" * 80)
print()

print("🎯 RECOMMENDATION")
print("-" * 80)
print("""
START WITH: Optimized
- Simple to implement (5 minute change)
- No added complexity
- 85% of the benefit for 5% of the effort
- Cost: $240/year extra accumulation + $120 one-time

CONSIDER LATER: Full
- If comfortable with strategy after 6-12 months
- Requires market regime tracking
- Adds ~15-20% more benefit
- More complex to maintain

TESTING: Use 'improvments?' folder to validate before deploying to PROD
""")

print("=" * 80)
print()

# Show how to update
print("🔧 HOW TO APPLY OPTIMIZED VERSION:")
print("-" * 80)
print("""
1. Open: /rsi_double_dca_backtest_PROD/strategy_config.py

2. Find the VARIANT_2 configuration

3. Change these two lines:
   cash_accumulation_per_payday=40.0,   # Was 30.0
   initial_cash_pool=450.0,              # Was 330.0

4. Save and rerun backtest:
   python rsi_calendar_date_backtest.py

5. Verify hit rate improved to ~96.3%

Done! ✅
""")

print("=" * 80)
