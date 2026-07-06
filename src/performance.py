import pandas as pd 

def calculate_total_return(strategy_returns):
    total_return = (1+strategy_returns).prod()-1
    return total_return

def calculate_annualized_return(total_return,strategy_returns):
    annualized_return = (1+total_return)**(252/len(strategy_returns))-1
    return annualized_return

def calculate_annualized_volatility(strategy_returns):
    annualized_volatility = strategy_returns.std()*(252**0.5)
    return annualized_volatility

def calculate_sharpe_ratio(strategy_returns):
    sharpe_ratio = strategy_returns.mean()/strategy_returns.std()*(252**0.5)
    return sharpe_ratio

def calculate_maximum_drawdown(strategy_returns):
    running_max = strategy_returns.cummax()
    cumulative = (1+strategy_returns).cumprod()
    drawdown = cumulative/running_max - 1
    maximum_drawdown = drawdown.min()
    return maximum_drawdown

def calculate_win_ratio(strategy_returns):
    win_days = (strategy_returns>0).sum()
    win_ratio = win_days / len(strategy_returns)
    return win_ratio
    