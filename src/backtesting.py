import pandas as pd 
import matplotlib.pyplot as plt

def calculate_var_breaches(strategy_returns,rolling_var):
    loss = - strategy_returns
    
    breaches = loss > rolling_var.shift(1)
    
    return breaches

def backtest_summary(breaches):
    breach_count = breaches.sum()
    breache_rate = breaches.mean()
    return {
        "Breach Count": breach_count,
        "Breach Rate": breache_rate
    }
    
def plot_var_backtest(strategy_returns, rolling_var):
    loss = -strategy_returns

    plt.figure(figsize=(12,6))

    plt.plot(loss, label="Daily Loss")
    plt.plot(rolling_var.shift(1), label="95% Rolling VaR")

    plt.title("VaR Backtesting")
    plt.xlabel("Date")
    plt.ylabel("Loss")

    plt.legend()

    plt.show()
    

def largest_breaches(strategy_returns, rolling_var, n=5):
    loss = -strategy_returns

    breaches = loss[loss > rolling_var.shift(1)]

    return breaches.sort_values(ascending=False).head(n)