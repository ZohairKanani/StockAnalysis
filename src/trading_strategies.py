import os
import pandas as pd
from data_fetch import fetch_sp500_data


def momentum_strategy(stocks_df, lookback=12, lag=1, num_stocks=10):
    """
    Implements a momentum trading strategy based on close-to-close returns.
    
    The strategy:
    1. Calculates momentum score using price change over a lookback period
    2. Ranks all stocks by their momentum score
    3. Goes LONG on top N stocks (highest momentum)
    4. Goes SHORT on bottom N stocks (lowest momentum)
    
    Parameters:
    -----------
    stocks_df : pandas.DataFrame
        Multi-level DataFrame with stock price data
    lookback : int
        Number of months to look back for momentum calculation (default: 12)
    lag : int
        Number of months to hold out/lag (default: 1)
    num_stocks : int
        Number of stocks to go long and short (default: 10)
    
    Returns:
    --------
    tuple
        (long_positions, short_positions) - lists of stock symbols
    """
    
    # Extract close prices from multi-level DataFrame
    closes = stocks_df.xs('Close', level=0, axis=1)
    
    # Calculate momentum score
    delayed_price = closes.shift(lag)
    starting_price = closes.shift(lag + lookback)
    mom_score = (delayed_price / starting_price) - 1
    
    # Rank stocks by momentum score (percentile rank)
    all_daily_ranks = mom_score.rank(axis=1, pct=True)
    
    # Get current (most recent) rankings
    current_ranks = all_daily_ranks.iloc[-1].sort_values(ascending=False)
    
    # Select top and bottom stocks
    long_positions = current_ranks.head(num_stocks).index.to_list()
    short_positions = current_ranks.tail(num_stocks).index.to_list()
    
    # Display results
    print("\n" + "="*60)
    print("MOMENTUM STRATEGY RESULTS")
    print("="*60)
    print(f"Lookback Period: {lookback} months")
    print(f"Lag Period: {lag} months")
    print(f"Number of Positions: {num_stocks}")
    print("\n")
    
    print("LONG POSITIONS (Top Momentum):")
    for i, stock in enumerate(long_positions, 1):
        rank_pct = current_ranks[stock] * 100
        print(f"  {i}. {stock:6s} - Momentum Rank: {rank_pct:.1f}%")
    
    print("\nSHORT POSITIONS (Bottom Momentum):")
    for i, stock in enumerate(short_positions, 1):
        rank_pct = current_ranks[stock] * 100
        print(f"  {i}. {stock:6s} - Momentum Rank: {rank_pct:.1f}%")
    
    print("="*60)
    
    return long_positions, short_positions


def main():
    """
    Main function to run the trading strategy selector.
    """
    print("\n" + "="*60)
    print("STOCK TRADING STRATEGIES")
    print("="*60)
    print("\nAvailable Strategies:")
    print("1. Momentum Strategy")
    print("\nEnter 'q' to quit")
    print("="*60)
    
    choice = input("\nSelect a strategy (1): ").strip()
    
    if choice.lower() == 'q':
        print("Exiting...")
        return
    
    # Fetch data (use monthly data and START_DATE/END_DATE env vars)
    print("\nFetching S&P 500 monthly data...")
    start = os.environ.get('START_DATE')
    end = os.environ.get('END_DATE')
    data = fetch_sp500_data(start=start, end=end, interval='1mo', save_to_file=False)
    
    if choice == '1':
        # Get parameters from user
        print("\n--- Momentum Strategy Parameters ---")
        
        lookback_input = input("Enter lookback period in days (default: 126): ").strip()
        lookback = int(lookback_input) if lookback_input else 126
        
        lag_input = input("Enter lag period in days (default: 21): ").strip()
        lag = int(lag_input) if lag_input else 21
        
        num_stocks_input = input("Enter number of stocks for long/short positions (default: 10): ").strip()
        num_stocks = int(num_stocks_input) if num_stocks_input else 10
        
        # Run momentum strategy
        momentum_strategy(data, lookback=lookback, lag=lag, num_stocks=num_stocks)
    
    else:
        print("Invalid choice. Please select a valid strategy number.")


if __name__ == "__main__":
    main()
