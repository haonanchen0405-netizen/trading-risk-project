import numpy as np
import pandas as pd
from statistics import NormalDist
import matplotlib.pyplot as plt
import yfinance as yf


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
    
    plt.title("252-day Rolling Historical VaR")
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




def stress_scenarios():
    scenarios = {
        "Equity Selloff": {
            "equity": -0.08,
            "bond": 0.02,
            "gold": 0.03,
        },

        "Rates Shock": {
            "equity": -0.02,
            "bond": -0.08,
            "gold": 0.01,
        },

        "Crisis Risk-Off": {
            "equity": -0.10,
            "bond": 0.05,
            "gold": 0.06,
        },

        "Inflation Shock": {
            "equity": -0.04,
            "bond": -0.06,
            "gold": 0.04,
        }
    }

    return scenarios

def get_asset_class(ticker):

    info = yf.Ticker(ticker).info

    category = str(info.get("category", "")).lower()
    name = str(info.get("longName", "")).lower()

    text = category + " " + name

    if "government" in text or "treasury" in text or "bond" in text:
        return "bond"

    elif "gold" in text or "commodity" in text:
        return "gold"

    else:
        return "equity"

def run_stress_test(weights, tickers, scenarios):

    asset_classes = {
        ticker: get_asset_class(ticker)
        for ticker in tickers
    }

    results = {}

    for scenario_name, shocks in scenarios.items():

        portfolio_return = 0

        for ticker in tickers:

            shock = shocks[asset_classes[ticker]]

            portfolio_return += weights[ticker] * shock

        results[scenario_name] = portfolio_return

    return pd.Series(results, name="Portfolio Return")
