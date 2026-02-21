import os
import yfinance as yf
import pandas as pd
from datetime import datetime
from pathlib import Path


def fetch_sp500_data(start=None, end=None, interval='1mo', save_to_file=True):
    """Download S&P 500 stock prices using start/end dates and an interval.

    Dates default to environment variables `START_DATE` and `END_DATE` if set,
    otherwise fall back to reasonable defaults.
    """
    # Resolve project root (assumes this file is in <project>/src)
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / 'data'

    # Read dates from environment if not provided
    start = start or os.environ.get('START_DATE', '2015-01-01')
    end = end or os.environ.get('END_DATE', datetime.now().strftime('%Y-%m-%d'))

    # Path to ticker symbols CSV
    tickers_path = data_dir / 'sp500_symbols.csv'
    print(f"Reading S&P 500 ticker symbols from: {tickers_path}")

    if not tickers_path.exists():
        raise FileNotFoundError(
            f"Ticker symbols file not found at {tickers_path}.\n"
            "Make sure `sp500_symbols.csv` exists in the project's `data/` folder."
        )

    tickers_df = pd.read_csv(tickers_path)
    tickers = tickers_df['Symbol'].to_list()

    print(f"Found {len(tickers)} tickers. Downloading data from {start} to {end} (interval={interval})...")

    # Download data from Yahoo Finance using start/end and interval
    data = yf.download(tickers, start=start, end=end, interval=interval, threads=True)

    # Determine number of unique stocks fetched
    unique_stocks = len(data.columns.get_level_values(1).unique()) if hasattr(data.columns, 'levels') else len(data.columns)
    print(f"Successfully downloaded data for {unique_stocks} stocks.")

    # Save to CSV with start/end date into project data folder
    if save_to_file:
        data_dir.mkdir(parents=True, exist_ok=True)
        today = datetime.now().strftime('%Y-%m-%d')
        filename = data_dir / f'sp500_historical_data_{start}_to_{end}_{today}.csv'
        data.to_csv(filename)
        print(f"Data saved to {filename}")

    return data


if __name__ == "__main__":
    data = fetch_sp500_data()
    print(f"\nData shape: {data.shape}")
    print(f"Date range: {data.index[0]} to {data.index[-1]}")
