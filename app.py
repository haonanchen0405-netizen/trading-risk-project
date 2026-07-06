import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from src import data_loader
from src import strategy
from src import portfolio
from src import performance
from src import risk
from src import backtesting
from src import stress


st.set_page_config(
    page_title="Trading Strategy and Market Risk Dashboard",
    layout="wide"
)

st.title("Trading Strategy and Market Risk Dashboard")


# =====================
# Sidebar Inputs
# =====================

st.sidebar.header("Inputs")

tickers_input = st.sidebar.text_input(
    "Tickers",
    value="SPY,QQQ,TLT,GLD"
)

tickers = [t.strip().upper() for t in tickers_input.split(",")]

start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2018-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2024-12-31"))

lookback = st.sidebar.number_input("Momentum Lookback", value=60, min_value=20, max_value=252)

confidence_interval = st.sidebar.number_input("Confidence Interval",value = 0.95, min_value = 0.01, max_value = 0.99)


# =====================
# Run Analysis
# =====================

prices = data_loader.download_adjusted_close_prices(
    tickers,
    start_date,
    end_date
)

returns = prices.pct_change().dropna()

signals = strategy.generate_signal(prices, lookback)
weights = portfolio.calculate_equal_weights(signals)
strategy_returns = portfolio.calculate_strategy_returns(weights, returns)

rolling_var = risk.calculate_rolling_var(strategy_returns)

breaches = backtesting.calculate_var_breaches(strategy_returns, rolling_var)
breach_summary = backtesting.backtest_summary(breaches)
largest_breaches = backtesting.largest_breaches(strategy_returns, rolling_var)

current_weights = weights.iloc[-1]
scenarios = stress.stress_scenarios()

stress_result = stress.run_stress_test(
    current_weights,
    tickers,
    scenarios
)


# =====================
# Performance
# =====================

st.header("Performance")

cumulative_returns = (1 + strategy_returns).cumprod()

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(cumulative_returns)
ax.set_title("Cumulative Strategy Return")
ax.set_xlabel("Date")
ax.set_ylabel("Growth of $1")
st.pyplot(fig)

total_return = performance.calculate_total_return(strategy_returns)



metrics = {
    "Total Return": performance.calculate_total_return(strategy_returns),
    "Annual Return": performance.calculate_annualized_return(total_return,strategy_returns),
    "Annual Volatility": performance.calculate_annualized_volatility(strategy_returns),
    "Sharpe Ratio": performance.calculate_sharpe_ratio(strategy_returns),
    "Max Drawdown": performance.calculate_maximum_drawdown(strategy_returns),
    "Win Rate": performance.calculate_win_ratio(strategy_returns)
}

st.dataframe(pd.DataFrame(metrics, index=["Value"]).T)



# =====================
# Drawdown
# =====================

st.header("Drawdown")

running_max = cumulative_returns.cummax()
drawdown = cumulative_returns / running_max - 1

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(drawdown)
ax.set_title("Strategy Drawdown")
ax.set_xlabel("Date")
ax.set_ylabel("Drawdown")
st.pyplot(fig)


# =====================
# Risk
# =====================

st.header("Risk")

col1, col2 = st.columns(2)

with col1:
    historical_var = risk.calculate_historical_var(strategy_returns,confidence_interval)
    st.metric(
    f"Historical {confidence_interval:.0%} VaR",
    f"{historical_var:.2%}"
)

with col2:
    expected_shortfall = risk.calculate_expected_shortfall(strategy_returns,confidence_interval)
    st.metric("Expected Shortfall", f"{expected_shortfall:.2%}")

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(rolling_var)
ax.set_title("252-Day Rolling Historical VaR")
ax.set_xlabel("Date")
ax.set_ylabel("VaR")
st.pyplot(fig)


# =====================
# VaR Backtesting
# =====================

st.header("VaR Backtesting")

st.write(breach_summary)

st.subheader("Largest VaR Breaches")
st.dataframe(largest_breaches)


# =====================
# Stress Testing
# =====================

st.header("Stress Testing")

st.dataframe(stress_result)
