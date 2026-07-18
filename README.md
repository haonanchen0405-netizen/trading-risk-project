# Trading Strategy and Market Risk Dashboard

A Python-based quantitative finance project that backtests a momentum strategy,
compares it with a static multi-asset benchmark, measures market risk, and
presents the results in an interactive Streamlit dashboard.

## Project overview

The project covers the complete workflow from market data to portfolio risk:

- Load local historical prices for SPY, QQQ, TLT, and GLD.
- Download other user-selected tickers from Yahoo Finance on demand.
- Generate a 60-day momentum signal without lookahead bias.
- Rebalance the strategy weekly and allow portfolio weights to drift between
  rebalances.
- Compare the strategy with a static stock, bond, and gold benchmark.
- Calculate return, volatility, Sharpe ratio, drawdown, VaR, and Expected
  Shortfall.
- Backtest rolling VaR forecasts and identify the largest breaches.
- Match large breaches to a curated list of major economic events.
- Estimate portfolio performance under hypothetical stress scenarios.

## Strategy methodology

### Momentum signal

For each asset, the default signal is based on its trailing 60-trading-day
return:

    momentum = price / price.shift(60) - 1

An asset is active when momentum is positive. Active assets receive equal
target weights; otherwise that allocation remains in cash.

The signal is shifted by one trading day before it is converted into a
position:

    position = signal.shift(1)

This ensures that today's return is never calculated using information that
only becomes available at today's close.

### Weekly rebalancing and intra-week drift

The portfolio rebalances before the return on the first trading day of each
week. Weeks are defined with the Pandas frequency W-FRI, meaning that each
weekly period ends on Friday. If Monday is a market holiday, the first
available trading day becomes the rebalance day.

Between rebalances, holdings are not reset to their target weights. Each
asset's beginning-of-day weight changes with its previous daily return:

    portfolio_return = sum(weight_i * asset_return_i)

    next_weight_i = (
        weight_i * (1 + asset_return_i)
        / (1 + portfolio_return)
    )

The strategy therefore produces daily P&L while trading only once per week.
Cash is implicit, earns 0%, and equals one minus the risky-asset weights.

## Static benchmark

The benchmark uses a fixed strategic allocation:

| Asset | Weight |
|---|---:|
| SPY | 16.7% |
| QQQ | 16.7% |
| TLT | 33.3% |
| GLD | 33.3% |

Local benchmark prices are stored in data/prices.csv. The file contains daily
observations from January 2015 through December 2025. Strategy and benchmark
returns are aligned to their common trading dates before metrics are
calculated.

## Performance and market risk

The dashboard reports:

- Total and annualized return
- Annualized volatility
- Sharpe ratio
- Maximum drawdown
- Win rate
- Historical and parametric VaR
- Historical Expected Shortfall
- 252-day rolling historical VaR

At a 95% confidence level, historical VaR is the loss corresponding to the
fifth percentile of daily returns. Expected Shortfall is the average loss
among observations beyond that VaR threshold.

### VaR backtesting

The backtest compares today's realized loss with the VaR forecast calculated
using information available one trading day earlier:

    breach = realized_loss > rolling_var.shift(1)

The dashboard plots realized losses, previous-day VaR forecasts, and breach
markers. It also reports the breach count, breach rate, and the five largest
breaches.

### Economic-event annotations

The file data/major_economic_events.csv contains ten curated events from 2015
to 2025 with descriptions and official source links. Each large VaR breach is
matched to the closest event within plus or minus 30 calendar days.

The annotation is labelled **Possible Related Event**. Date proximity does not
establish that an event caused a portfolio loss, and unmatched breaches remain
explicitly unclassified.

## Stress testing

The project includes four hypothetical scenarios:

- Equity selloff
- Interest-rate shock
- Crisis risk-off
- Inflation shock

Stress functions are implemented in src/risk.py. Asset classes for
user-selected tickers are identified through Yahoo Finance metadata before
scenario shocks are applied to current portfolio weights.

## Project structure

    trading-risk-project/
    |-- app.py
    |-- risk_project.ipynb
    |-- README.md
    |-- data/
    |   |-- prices.csv
    |   |-- major_economic_events.csv
    |-- src/
        |-- data_loader.py
        |-- strategy.py
        |-- portfolio.py
        |-- performance.py
        |-- risk.py
        |-- backtesting.py

## Installation

Python 3.10 or newer is recommended.

    python3 -m pip install pandas numpy matplotlib yfinance streamlit jupyter

## Run the dashboard

From Terminal:

    cd /Users/haonanchen/Desktop/project
    python3 -m streamlit run app.py

Then open the local URL shown by Streamlit, normally:

    http://localhost:8501

Press Control+C in Terminal to stop the server.

## Use the research notebook

Start Jupyter from the project directory:

    cd /Users/haonanchen/Desktop/project
    python3 -m jupyter notebook risk_project.ipynb

Run the notebook cells in order so that the weekly strategy returns, risk
measures, stress results, and benchmark comparison use the same inputs.

## Dashboard sections

- **Inputs:** tickers, date range, momentum lookback, and VaR confidence level
- **Performance:** cumulative return and performance metrics
- **Benchmark Comparison:** strategy-versus-benchmark chart and metrics
- **Drawdown:** drawdown history
- **Risk:** VaR, Expected Shortfall, and rolling VaR
- **VaR Backtesting:** breaches, chart, and economic-event annotations
- **Stress Testing:** hypothetical scenario results

## Important limitations

- Historical results do not guarantee future performance.
- Transaction costs, bid-ask spreads, taxes, and market impact are excluded.
- Cash earns a 0% return.
- The strategy is long-only and uses a single momentum rule.
- VaR is not a worst-case loss estimate.
- Historical VaR assumes the selected sample is informative about future risk.
- The static benchmark does not represent every investor's appropriate
  allocation.
- Economic-event matching is based on date proximity, not causal inference.
- On-demand prices and asset metadata depend on Yahoo Finance availability.
