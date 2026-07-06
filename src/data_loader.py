import pandas as pd
import yfinance as yf 

def download_adjusted_close_prices(tickers, start_date, end_date):
    data = yf.download(
        tickers = tickers,
        start = start_date,
        end = end_date,
        progress = False
    )
    prices = data["Close"]
    
    return prices

def calculate_daily_returns(prices):
    returns = prices.pct_change().dropna()
    return returns

def save_prices_to_csv(prices, filename):
    prices.to_csv(filename)

def load_prices_from_csv(filename):
    prices = pd.read_csv(
        filename,
        index_col = 0,
        parse_dates=True
    )
    return prices