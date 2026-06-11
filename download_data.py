import os
from sec_edgar_downloader import Downloader

dl = Downloader("name-of-project", "email")

# The tickers we want to analyze
tickers = ["AAPL", "NVDA"]

print("Starting downloads from SEC Edgar database...")
for ticker in tickers:
    print(f"Downloading latest 10-K for {ticker}...")
    # This downloads the most recent ('limit=1') annual report ('10-K')
    dl.get("10-K", ticker, limit=1)

print("\nDownloads complete! Check the 'sec-edgar-filings' folder.")
