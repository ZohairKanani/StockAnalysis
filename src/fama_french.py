import os
import pandas as pd
import statsmodels.api as sm
from pathlib import Path

from data_fetch import fetch_sp500_data


def get_date_range():
    start = os.environ.get('START_DATE', '2015-01-01')
    end = os.environ.get('END_DATE', pd.Timestamp.now().strftime('%Y-%m-%d'))
    return start, end


def load_fama_french_factors():
    """
    Load Fama-French 3 factors from CSV file in the data folder.
    
    Returns a DataFrame with PeriodIndex('M') and columns: Mkt-RF, SMB, HML, RF.
    """
    project_root = Path(__file__).resolve().parent.parent
    ff_path = project_root / 'data' / 'ff_monthly.csv'
    
    if not ff_path.exists():
        raise FileNotFoundError(
            f"Fama-French CSV not found at {ff_path}.\n"
            "Make sure `ff_monthly.csv` exists in the project's `data/` folder."
        )
    
    # Read CSV: first column is date in YYYYMM format
    ff = pd.read_csv(ff_path, index_col=0)
    
    # Convert YYYYMM index to datetime, then to PeriodIndex('M')
    ff.index = pd.to_datetime(ff.index.astype(str), format='%Y%m')
    ff.index = ff.index.to_period('M')
    
    # Convert from percentage to decimal (if needed - check your CSV)
    # The standard FF data is in percentages, so divide by 100
    ff = ff / 100.0
    
    return ff


def calculate_umd(stocks_df, x_percent=0.3):
    """
    Calculate the UMD (momentum) factor from a multi-column stocks DataFrame.

    Assumes `stocks_df` is a yfinance-style multi-index DataFrame where the
    first level contains OHLCV fields and the second level contains tickers.

    Returns a DataFrame with PeriodIndex('M') and a column named 'UMD'.
    """
    # Monthly closes and returns
    monthly_closes = stocks_df['Close'].resample('ME').last()
    monthly_returns = monthly_closes.pct_change()

    # Momentum score: using 12-1 logic (Price at T-1 / Price at T-12) - 1
    mom_score = (monthly_closes.shift(1) / monthly_closes.shift(12)) - 1

    # Rank across columns for each row
    ranks = mom_score.rank(axis=1, pct=True)

    # Winners/losers masks
    winners_mask = (ranks >= (1 - x_percent))
    losers_mask = (ranks <= x_percent)

    # Mean returns for winners and losers
    win_returns = monthly_returns.where(winners_mask).mean(axis=1)
    lose_returns = monthly_returns.where(losers_mask).mean(axis=1)

    umd_series = win_returns - lose_returns
    umd_df = umd_series.to_frame(name='UMD').dropna()
    umd_df.index = umd_df.index.to_period('M')

    return umd_df


def run_fama_french_regression(stocks_df, x_percent=0.3):
    """Compute UMD, merge with Fama-French factors and run 4-factor regression.

    Returns the fitted statsmodels OLS result.
    """
    # Compute UMD
    umd = calculate_umd(stocks_df, x_percent=x_percent)

    # Load FF factors from CSV
    ff = load_fama_french_factors()

    # Merge on PeriodIndex
    df = pd.merge(umd, ff, left_index=True, right_index=True, how='inner')

    # Calculate Excess Returns: UMD is already a factor (not excess), but for regression
    # we will regress UMD on the 3 FF factors plus an intercept (i.e., test if UMD
    # is explained by the FF factors). If you want to regress stock excess returns
    # on the factors, call this function differently.

    Y = df['UMD']
    X = df[['Mkt-RF', 'SMB', 'HML']]
    X = sm.add_constant(X)

    model = sm.OLS(Y, X).fit()

    return model


if __name__ == '__main__':
    # Example runner: fetch monthly data, compute umd and run regression
    start, end = get_date_range()
    print(f"Using date range: {start} to {end}")

    stocks = fetch_sp500_data(start=start, end=end, interval='1mo', save_to_file=False)
    model = run_fama_french_regression(stocks)
    print(model.summary())
