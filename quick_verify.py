import yfinance as yf
import pandas as pd

spy = yf.download("SPY", start="2025-01-01", end="2025-11-22", progress=False)
print("Index type:", type(spy.index))
print("First few index values:")
print(spy.index[:5])
print("\nColumn names:")
print(spy.columns)
print("\nSample row:")
print(spy.head(1))
