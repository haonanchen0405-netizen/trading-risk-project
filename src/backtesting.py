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


def annotate_breaches_with_events(
    breach_losses,
    rolling_var,
    events,
    window_days=30,
):
    """Add the closest major economic event to each VaR breach.

    Event matches are based only on calendar proximity. A match means that the
    breach occurred within window_days before or after an event anchor date;
    it does not establish that the event caused the breach.
    """
    required_columns = {
        "event_date",
        "event_name",
        "category",
        "summary",
        "source_url",
    }
    missing_columns = required_columns.difference(events.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"events data is missing required columns: {missing}")
    if window_days < 0:
        raise ValueError("window_days must be non-negative")

    event_data = events.copy()
    event_data["event_date"] = pd.to_datetime(
        event_data["event_date"],
        errors="coerce",
    )
    event_data = event_data.dropna(subset=["event_date"])

    var_forecast = rolling_var.shift(1)
    annotated_rows = []

    for breach_date, realized_loss in breach_losses.items():
        breach_date = pd.Timestamp(breach_date)
        row = {
            "Breach Date": breach_date,
            "Realized Loss": float(realized_loss),
            "VaR Forecast": var_forecast.get(breach_date, float("nan")),
            "Possible Related Event": "No major event matched",
            "Event Date": pd.NaT,
            "Days From Event": pd.NA,
            "Category": pd.NA,
            "Event Summary": pd.NA,
            "Source": pd.NA,
        }

        if not event_data.empty:
            days_from_event = (
                breach_date - event_data["event_date"]
            ).dt.days
            nearby_events = event_data.loc[
                days_from_event.abs() <= window_days
            ].copy()

            if not nearby_events.empty:
                nearby_events["days_from_event"] = days_from_event.loc[
                    nearby_events.index
                ]
                closest_index = (
                    nearby_events["days_from_event"].abs().idxmin()
                )
                closest_event = nearby_events.loc[closest_index]

                row.update(
                    {
                        "Possible Related Event": closest_event["event_name"],
                        "Event Date": closest_event["event_date"],
                        "Days From Event": int(
                            closest_event["days_from_event"]
                        ),
                        "Category": closest_event["category"],
                        "Event Summary": closest_event["summary"],
                        "Source": closest_event["source_url"],
                    }
                )

        annotated_rows.append(row)

    columns = [
        "Breach Date",
        "Realized Loss",
        "VaR Forecast",
        "Possible Related Event",
        "Event Date",
        "Days From Event",
        "Category",
        "Event Summary",
        "Source",
    ]
    result = pd.DataFrame(annotated_rows, columns=columns)

    if not result.empty:
        result["Days From Event"] = result["Days From Event"].astype(
            "Int64"
        )
        result = result.set_index("Breach Date")

    return result
