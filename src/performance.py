import pandas as pd 

def calculate_total_return(strategy_returns):
    total_return = (1+strategy_returns).prod()-1
    return total_return

def calculate_annualized_return(strategy_returns):
    total_return = calculate_total_return(strategy_returns)
    annualized_return = (1 + total_return) ** (252 / len(strategy_returns)) - 1
    return annualized_return

def calculate_annualized_volatility(strategy_returns):
    annualized_volatility = strategy_returns.std()*(252**0.5)
    return annualized_volatility

def calculate_sharpe_ratio(strategy_returns):
    sharpe_ratio = strategy_returns.mean()/strategy_returns.std()*(252**0.5)
    return sharpe_ratio

def calculate_maximum_drawdown(strategy_returns):
    cumulative = (1+strategy_returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = cumulative/running_max - 1
    maximum_drawdown = drawdown.min()
    return maximum_drawdown

def calculate_win_ratio(strategy_returns):
    win_days = (strategy_returns>0).sum()
    win_ratio = win_days / len(strategy_returns)
    return win_ratio

def calculate_performance_metrics(strategy_returns):
    return {
        "Total Return": calculate_total_return(strategy_returns),
        "Annualized Return": calculate_annualized_return(strategy_returns),
        "Annualized Volatility": calculate_annualized_volatility(strategy_returns),
        "Sharpe Ratio": calculate_sharpe_ratio(strategy_returns),
        "Maximum Drawdown": calculate_maximum_drawdown(strategy_returns),
        "Win Ratio": calculate_win_ratio(strategy_returns),
    }
    