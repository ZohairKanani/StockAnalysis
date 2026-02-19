import yfinance as yf
import pandas as pd
from datetime import datetime
from pathlib import Path


def fetch_sp500_data(period='1y', interval='1d', save_to_file=True):
    """Downloads S&P 500 stock prices from Yahoo Finance.

    This function resolves the project root relative to this file so it works
    regardless of the current working directory when the script is executed.
    """
    # Resolve project root (assumes this file is in <project>/src)
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / 'data'

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

    print(f"Found {len(tickers)} tickers. Downloading data for period: {period}...")

    # Download data from Yahoo Finance
    data = yf.download(tickers, period=period, interval=interval, threads=True)

    unique_stocks = len(data.columns.get_level_values(1).unique()) if hasattr(data.columns, 'levels') else len(data.columns)
    print(f"Successfully downloaded data for {unique_stocks} stocks.")

    # Save to CSV with today's date into project data folder
    if save_to_file:
        data_dir.mkdir(parents=True, exist_ok=True)
        today = datetime.now().strftime('%Y-%m-%d')
        filename = data_dir / f'sp500_historical_data_{today}.csv'
        data.to_csv(filename)
        print(f"Data saved to {filename}")

    return data


if __name__ == "__main__":
    data = fetch_sp500_data()
    print(f"\nData shape: {data.shape}")
    print(f"Date range: {data.index[0]} to {data.index[-1]}")
