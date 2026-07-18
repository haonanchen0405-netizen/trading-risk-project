import pandas as pd 
import matplotlib.pyplot as plt


def _align_weights_and_returns(weights, returns):
    """Align portfolio weights and asset returns to a common data set."""
    common_index = weights.index.intersection(returns.index)
    common_columns = returns.columns.intersection(weights.columns, sort=False)

    if common_index.empty:
        raise ValueError("weights and returns do not have overlapping dates")
    if common_columns.empty:
        raise ValueError("weights and returns do not have overlapping assets")

    aligned_weights = weights.loc[common_index, common_columns].fillna(0.0)
    aligned_returns = returns.loc[common_index, common_columns]

    if aligned_returns.isna().any().any():
        raise ValueError("returns contain missing values after alignment")

    return aligned_weights.astype(float), aligned_returns.astype(float)


def calculate_equal_weights(position):
    active_count = position.sum(axis = 1)
    raw_weights = position.div(active_count,axis=0)
    weights = raw_weights.fillna(0.0)
    return weights
    

def calculate_strategy_returns(weights, returns):
    weights, returns = _align_weights_and_returns(weights, returns)
    strategy_returns = (weights * returns).sum(axis=1)
    strategy_returns.name = "Momentum Strategy"
    return strategy_returns


def calculate_drifted_weights_and_returns(
    target_weights,
    returns,
    rebalance_frequency="W-FRI",
):
    """Calculate P&L while weights drift between scheduled rebalances.

    The portfolio rebalances before the return on the first trading day in
    each calendar week. The target weight for that date must already be based
    on information available before the date (for example, a one-day-shifted
    signal). On all other days, each asset's weight drifts with its return.

    Cash is implicit, earns 0%, and equals one minus the risky-asset weights.

    Returns
    -------
    strategy_returns : pd.Series
        Daily portfolio return, including intra-week P&L.
    drifted_weights : pd.DataFrame
        Beginning-of-day weights used to calculate each day's P&L.
    """
    target_weights, returns = _align_weights_and_returns(
        target_weights,
        returns,
    )

    if not isinstance(returns.index, pd.DatetimeIndex):
        raise TypeError("weekly rebalancing requires a DatetimeIndex")

    weekly_period = returns.index.to_period(rebalance_frequency)
    rebalance_day = ~weekly_period.duplicated()

    drifted_weights = pd.DataFrame(
        index=returns.index,
        columns=returns.columns,
        dtype=float,
    )
    strategy_returns = pd.Series(
        index=returns.index,
        dtype=float,
        name="Momentum Strategy",
    )

    current_weights = None

    for row_number, date in enumerate(returns.index):
        if current_weights is None or rebalance_day[row_number]:
            current_weights = target_weights.loc[date].copy()

        drifted_weights.loc[date] = current_weights
        asset_returns = returns.loc[date]
        daily_portfolio_return = float((current_weights * asset_returns).sum())
        strategy_returns.loc[date] = daily_portfolio_return

        portfolio_growth = 1.0 + daily_portfolio_return
        if portfolio_growth <= 0:
            raise ValueError(
                f"portfolio value is non-positive after the return on {date}"
            )

        current_weights = (
            current_weights * (1.0 + asset_returns) / portfolio_growth
        )

    return strategy_returns, drifted_weights

def calculate_benchmark_returns(returns):
    """
    Calculate the daily returns of the benchmark portfolio.

    Benchmark Allocation:
        - SPY : 16.7%
        - QQQ : 16.7%
        - TLT : 33.3%
        - GLD : 33.3%
    """

    weights = {
        "SPY": 1 / 6,
        "QQQ": 1 / 6,
        "TLT": 1 / 3,
        "GLD": 1 / 3,
    }

    benchmark_returns = sum(
        returns[ticker] * weight
        for ticker, weight in weights.items()
    )

    benchmark_returns.name = "Benchmark"

    return benchmark_returns

def plot_strategy_vs_benchmark(strategy_returns, benchmark_returns):
    """
    Plot cumulative returns of the strategy and benchmark.
    """

    comparison_returns = pd.concat(
        [
            strategy_returns.rename("Momentum Strategy"),
            benchmark_returns.rename("Static Benchmark"),
        ],
        axis=1,
        join="inner",
    ).dropna()
    cumulative = (1 + comparison_returns).cumprod()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        cumulative.index,
        cumulative["Momentum Strategy"],
        label="Momentum Strategy",
    )
    ax.plot(
        cumulative.index,
        cumulative["Static Benchmark"],
        label="Static Benchmark",
    )

    ax.set_title("Momentum Strategy vs Static Benchmark")
    ax.set_xlabel("Date")
    ax.set_ylabel("Growth of $1")
    ax.legend()
    ax.grid(True)
    fig.tight_layout()

    return fig

def create_performance_comparison(strategy_metrics, benchmark_metrics):
    """
    Create a performance comparison table between the strategy
    and the static benchmark.

    Parameters
    ----------
    strategy_metrics : dict
        Performance metrics of the momentum strategy.

    benchmark_metrics : dict
        Performance metrics of the static benchmark.

    Returns
    -------
    pd.DataFrame
        Performance comparison table.
    """

    comparison = pd.DataFrame(
        {
            "Momentum Strategy": strategy_metrics,
            "Static Benchmark": benchmark_metrics
        }
    )

    return comparison
