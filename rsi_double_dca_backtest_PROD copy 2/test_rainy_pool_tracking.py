"""
Test rainy pool tracking in production email mode
"""
from email_generator import generate_email_content

# Simulate production email with some rainy buy history
rainy_buys_sample = [
    {'date': '2025-03-03', 'rsi_sma': 42.5, 'price': 520.0, 'amount': 150.0, 'cash_before': 330.0, 'cash_after': 180.0},
    {'date': '2025-04-17', 'rsi_sma': 43.8, 'price': 535.0, 'amount': 150.0, 'cash_before': 390.0, 'cash_after': 240.0},
    {'date': '2025-11-03', 'rsi_sma': 44.2, 'price': 620.0, 'amount': 150.0, 'cash_before': 360.0, 'cash_after': 210.0},
]

# Current market conditions
rsi_sma = 42.5
rsi_14 = 48.2
price = 668.73  # Current SPY price
cash_pool = 330.0
total_contributions = 1800.0

print("=" * 80)
print("TESTING RAINY POOL TRACKING - PRODUCTION EMAIL MODE")
print("=" * 80)

# Test with is_simulation=False (production mode)
subject, body = generate_email_content(
    rsi_sma=rsi_sma,
    price=price,
    cash_pool=cash_pool,
    total_contributions=total_contributions,
    rainy_buys=rainy_buys_sample,
    is_simulation=False,  # Production mode
    rsi_14=rsi_14
)

print("\nEMAIL SUBJECT:")
print(subject)

print("\n" + "=" * 80)
print("EMAIL BODY (searching for rainy pool section):")
print("=" * 80)

# Extract just the rainy pool section
lines = body.split('\n')
in_rainy_section = False
rainy_section_lines = []

for line in lines:
    if 'RAINY POOL PERFORMANCE' in line:
        in_rainy_section = True
    if in_rainy_section:
        rainy_section_lines.append(line)
        if line.strip().startswith('*This tracks ONLY'):
            break

if rainy_section_lines:
    print("\n✅ RAINY POOL SECTION FOUND:")
    print('\n'.join(rainy_section_lines))
    
    # Calculate expected values
    total_invested = sum(buy['amount'] for buy in rainy_buys_sample)
    total_shares = sum(buy['amount'] / buy['price'] for buy in rainy_buys_sample)
    current_value = total_shares * price
    profit = current_value - total_invested
    roi = (profit / total_invested) * 100 if total_invested > 0 else 0
    
    print("\n" + "=" * 80)
    print("VERIFICATION:")
    print("=" * 80)
    print(f"Expected Total Invested: ${total_invested:,.2f}")
    print(f"Expected Shares: {total_shares:.4f}")
    print(f"Expected Current Value: ${current_value:,.2f}")
    print(f"Expected Profit: ${profit:,.2f}")
    print(f"Expected ROI: {roi:.2f}%")
    print(f"Expected Buys Count: {len(rainy_buys_sample)}")
else:
    print("\n❌ RAINY POOL SECTION NOT FOUND!")

print("\n" + "=" * 80)
print("TEST WITH is_simulation=True (should NOT show rainy pool):")
print("=" * 80)

subject_test, body_test = generate_email_content(
    rsi_sma=rsi_sma,
    price=price,
    cash_pool=cash_pool,
    total_contributions=total_contributions,
    rainy_buys=rainy_buys_sample,
    is_simulation=True,  # Test mode
    rsi_14=rsi_14
)

if 'RAINY POOL PERFORMANCE' in body_test:
    print("❌ ERROR: Rainy pool section appears in test email!")
else:
    print("✅ CORRECT: Rainy pool section hidden in test mode")

print("\n" + "=" * 80)
