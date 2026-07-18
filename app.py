import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from src import data_loader
from src import strategy
from src import portfolio
from src import performance
from src import risk
from src import backtesting


PROJECT_DIR = Path(__file__).resolve().parent
BENCHMARK_TICKERS = ["SPY", "QQQ", "TLT", "GLD"]
BENCHMARK_DATA_FILE = PROJECT_DIR / "data" / "prices.csv"
ECONOMIC_EVENTS_FILE = PROJECT_DIR / "data" / "major_economic_events.csv"


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

tickers = list(
    dict.fromkeys(
        ticker.strip().upper()
        for ticker in tickers_input.split(",")
        if ticker.strip()
    )
)

start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2018-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2024-12-31"))

lookback = st.sidebar.number_input("Momentum Lookback", value=60, min_value=20, max_value=252)

confidence_interval = st.sidebar.number_input("Confidence Interval",value = 0.95, min_value = 0.01, max_value = 0.99)


# =====================
# Run Analysis
# =====================

if not tickers:
    st.error("Enter at least one ticker.")
    st.stop()

period_start = pd.Timestamp(start_date)
period_end = pd.Timestamp(end_date)

benchmark_prices_all = data_loader.load_prices_from_csv(
    BENCHMARK_DATA_FILE
).sort_index()
benchmark_prices_all = benchmark_prices_all.reindex(columns=BENCHMARK_TICKERS)

local_tickers = [
    ticker for ticker in tickers
    if ticker in BENCHMARK_TICKERS
]
on_demand_tickers = [
    ticker for ticker in tickers
    if ticker not in BENCHMARK_TICKERS
]

price_frames = []

if local_tickers:
    local_prices = benchmark_prices_all.loc[
        (benchmark_prices_all.index >= period_start)
        & (benchmark_prices_all.index < period_end),
        local_tickers,
    ]
    price_frames.append(local_prices)

if on_demand_tickers:
    on_demand_prices = data_loader.download_adjusted_close_prices(
        on_demand_tickers,
        start_date,
        end_date,
    )
    if isinstance(on_demand_prices, pd.Series):
        on_demand_prices = on_demand_prices.to_frame(
            name=on_demand_tickers[0]
        )
    price_frames.append(on_demand_prices)

prices = (
    pd.concat(price_frames, axis=1, join="inner")
    .sort_index()
    .reindex(columns=tickers)
    .dropna()
)

if len(prices) <= lookback:
    st.error(
        "Not enough overlapping price history for the selected tickers and "
        "momentum lookback."
    )
    st.stop()

returns = prices.pct_change().dropna()

benchmark_prices = benchmark_prices_all.loc[
    (benchmark_prices_all.index >= period_start)
    & (benchmark_prices_all.index < period_end)
].dropna()
benchmark_returns = portfolio.calculate_benchmark_returns(
    benchmark_prices.pct_change().dropna()
)

signals = strategy.generate_signal(prices, lookback)
position = strategy.generate_position(signals)
target_weights = portfolio.calculate_equal_weights(position)
strategy_returns, weights = portfolio.calculate_drifted_weights_and_returns(
    target_weights,
    returns,
    rebalance_frequency="W-FRI",
)

rolling_var = risk.calculate_rolling_var(
    strategy_returns,
    confidence_interval=confidence_interval,
)

breaches = backtesting.calculate_var_breaches(strategy_returns, rolling_var)
breach_summary = backtesting.backtest_summary(breaches)
largest_breaches = backtesting.largest_breaches(strategy_returns, rolling_var)
economic_events = pd.read_csv(
    ECONOMIC_EVENTS_FILE,
    parse_dates=["event_date"],
)
annotated_breaches = backtesting.annotate_breaches_with_events(
    largest_breaches,
    rolling_var,
    economic_events,
    window_days=30,
)

current_weights = weights.iloc[-1]
scenarios = risk.stress_scenarios()

stress_result = risk.run_stress_test(
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
    "Annual Return": performance.calculate_annualized_return(strategy_returns),
    "Annual Volatility": performance.calculate_annualized_volatility(strategy_returns),
    "Sharpe Ratio": performance.calculate_sharpe_ratio(strategy_returns),
    "Max Drawdown": performance.calculate_maximum_drawdown(strategy_returns),
    "Win Rate": performance.calculate_win_ratio(strategy_returns)
}

st.dataframe(pd.DataFrame(metrics, index=["Value"]).T)


st.subheader("Benchmark Comparison")

comparison_returns = pd.concat(
    [
        strategy_returns.rename("Momentum Strategy"),
        benchmark_returns.rename("Static Benchmark"),
    ],
    axis=1,
    join="inner",
).dropna()

if comparison_returns.empty:
    st.info(
        "The selected strategy period does not overlap the local benchmark "
        "history."
    )
else:
    strategy_comparison_returns = comparison_returns["Momentum Strategy"]
    benchmark_comparison_returns = comparison_returns["Static Benchmark"]

    comparison_figure = portfolio.plot_strategy_vs_benchmark(
        strategy_comparison_returns,
        benchmark_comparison_returns,
    )
    st.pyplot(comparison_figure)

    strategy_metrics = performance.calculate_performance_metrics(
        strategy_comparison_returns
    )
    benchmark_metrics = performance.calculate_performance_metrics(
        benchmark_comparison_returns
    )
    comparison = portfolio.create_performance_comparison(
        strategy_metrics,
        benchmark_metrics,
    )

    comparison_display = comparison.T
    comparison_format = {
        "Total Return": "{:.2%}",
        "Annualized Return": "{:.2%}",
        "Annualized Volatility": "{:.2%}",
        "Sharpe Ratio": "{:.3f}",
        "Maximum Drawdown": "{:.2%}",
        "Win Ratio": "{:.2%}",
    }

    st.caption(
        "Static benchmark allocation: SPY 16.7%, QQQ 16.7%, "
        "TLT 33.3%, GLD 33.3%. "
        f"Comparison period: {comparison_returns.index.min():%Y-%m-%d} to "
        f"{comparison_returns.index.max():%Y-%m-%d}."
    )
    st.dataframe(
        comparison_display.style.format(comparison_format),
        use_container_width=True,
    )



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

realized_loss = -strategy_returns
var_forecast = rolling_var.shift(1)
valid_breaches = breaches & var_forecast.notna()

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(
    realized_loss.index,
    realized_loss,
    label="Daily Realized Loss",
    color="steelblue",
    linewidth=1,
    alpha=0.75,
)
ax.plot(
    var_forecast.index,
    var_forecast,
    label=f"Previous-Day {confidence_interval:.0%} VaR Forecast",
    color="darkorange",
    linewidth=1.5,
)
ax.scatter(
    realized_loss.index[valid_breaches],
    realized_loss[valid_breaches],
    label="VaR Breach",
    color="crimson",
    marker="o",
    s=24,
    zorder=3,
)
ax.axhline(0, color="black", linewidth=0.7, alpha=0.5)
ax.set_title("VaR Backtest: Realized Loss vs Previous-Day Forecast")
ax.set_xlabel("Date")
ax.set_ylabel("Daily Loss")
ax.legend()
ax.grid(True, alpha=0.3)
fig.tight_layout()
st.pyplot(fig)

st.subheader("Largest VaR Breaches")
st.caption(
    "Each breach is matched to the closest curated major economic event "
    "within ±30 calendar days. Proximity does not establish causation."
)
st.dataframe(
    annotated_breaches.style.format(
        {
            "Realized Loss": "{:.2%}",
            "VaR Forecast": "{:.2%}",
        },
        na_rep="—",
    ),
    column_config={
        "Source": st.column_config.LinkColumn(
            "Source",
            display_text="Official source",
        ),
    },
    use_container_width=True,
)


# =====================
# Stress Testing
# =====================

st.header("Stress Testing")

st.dataframe(stress_result)
