import numpy as np
import datetime
import pandas as pd
from demand_model import predict_demand

def forecast_24h(product: dict, base_signals: dict) -> list:
    forecast = []
    now      = datetime.datetime.now()

    for hour_offset in range(24):
        future_dt   = now + datetime.timedelta(hours=hour_offset)
        future_hour = future_dt.hour
        future_day  = future_dt.weekday()

        signals = base_signals.copy()
        signals["hour"]        = future_hour
        signals["day_of_week"] = future_day
        signals["is_weekend"]  = int(future_day >= 5)

        # Adjust trend score by time of day
        base_trend = base_signals["trend_score"]
        if 19 <= future_hour <= 22:
            signals["trend_score"] = min(1.0, base_trend + 0.30)
        elif 12 <= future_hour <= 14:
            signals["trend_score"] = min(1.0, base_trend + 0.15)
        elif 0 <= future_hour <= 6:
            signals["trend_score"] = max(0.1, base_trend - 0.20)
        else:
            signals["trend_score"] = base_trend

        # Weekend bump
        if future_day >= 5:
            signals["trend_score"] = min(1.0, signals["trend_score"] + 0.10)

        demand  = predict_demand(product["base_price"], signals)
        revenue = product["base_price"] * demand

        is_peak    = 19 <= future_hour <= 22
        is_morning = 12 <= future_hour <= 14
        is_low     = 0  <= future_hour <= 6

        forecast.append({
            "hour":        future_hour,
            "label":       future_dt.strftime("%H:%M"),
            "date_label":  future_dt.strftime("%a %H:%M"),
            "demand":      round(demand, 1),
            "revenue":     round(revenue, 2),
            "trend_score": round(signals["trend_score"], 2),
            "is_peak":     is_peak,
            "is_morning":  is_morning,
            "is_low":      is_low,
        })

    return forecast


def get_best_pricing_window(forecast: list) -> dict:
    """Find the best and worst hours for demand in the 24h forecast."""
    df = pd.DataFrame(forecast)

    if df.empty:
        return {
            "best_hour":     "N/A",
            "best_demand":   0,
            "lowest_hour":   "N/A",
            "lowest_demand": 0,
        }

    peak_row = df.loc[df["demand"].idxmax()]
    low_row  = df.loc[df["demand"].idxmin()]

    return {
        "best_hour":     peak_row["label"],
        "best_demand":   peak_row["demand"],
        "lowest_hour":   low_row["label"],
        "lowest_demand": low_row["demand"],
    }