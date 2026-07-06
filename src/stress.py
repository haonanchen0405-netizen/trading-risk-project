import pandas as pd
import yfinance as yf



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
