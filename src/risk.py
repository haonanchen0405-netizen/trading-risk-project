import numpy as np
import pandas as pd
from statistics import NormalDist
import matplotlib.pyplot as plt

def calculate_historical_var(strategy_returns, confidence_interval=0.95):
    percentile = (1 - confidence_interval) * 100
    historical_var = -np.percentile(strategy_returns.dropna(), percentile)
    return historical_var

def calculate_expected_shortfall(strategy_returns, confidence_interval=0.95):
    percentile = (1 - confidence_interval) * 100
    q = np.percentile(strategy_returns.dropna(), percentile)
    es = -strategy_returns[strategy_returns <= q].mean()
    return es

def calculate_parametric_var(strategy_returns, confidence_interval=0.95):
    r = strategy_returns.dropna()
    mu = r.mean()
    sigma = r.std()
    z = NormalDist().inv_cdf(1 - confidence_interval)
    parametric_var = -(mu + sigma * z)
    return parametric_var

def calculate_rolling_var(strategy_returns,window=252,confidence_interval = 0.95):
    percentile = 1 - confidence_interval
    rolling_var = -strategy_returns.rolling(window).quantile(percentile)
    return rolling_var

def plot_rolling_var(rolling_var):
    plt.figure(figsize=(12,6))
    plt.plot(rolling_var, label = "Rolling Historical Var")
    
    plt.title("252-day Rolling Historical Var")
    plt.xlabel("Date")
    plt.ylabel("Var")
    plt.legend
    
    plt.tight_layout
    plt.show()
    
def apply_risk_control(
        strategy_returns,
        rolling_var,
        threshold=0.02,
        reduction=0.5):

    risk_multiplier = np.where(
        rolling_var.shift(1) > threshold,
        reduction,
        1.0
    )

    controlled_returns = (
        strategy_returns *
        pd.Series(risk_multiplier, index=strategy_returns.index)
    )

    return controlled_returns