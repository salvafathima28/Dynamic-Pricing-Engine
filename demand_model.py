import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
from config import *

def generate_realistic_data(n=8000):
    np.random.seed(42)
    price        = np.random.uniform(MIN_PRICE, MAX_PRICE, n)
    comp_avg     = np.random.uniform(MIN_PRICE * 0.85, MAX_PRICE * 1.1, n)
    hour         = np.random.randint(0, 24, n)
    day          = np.random.randint(0, 7, n)
    weather_boost = np.random.uniform(0, 0.5, n)
    trend_score  = np.random.uniform(0.2, 1.0, n)

    # Realistic demand formula incorporating all signals
    demand = (
        300
        - 0.18 * price                        # price elasticity
        + 0.08 * comp_avg                     # competitor pricing effect
        + 60  * trend_score                   # search demand signal
        + 40  * weather_boost                 # weather-driven online shopping
        + 25  * (day >= 5).astype(float)      # weekend boost
        + 30  * ((hour >= 19) & (hour <= 22)).astype(float)  # evening peak
        + np.random.normal(0, 15, n)          # noise
    ).clip(0, 800).astype(int)

    return pd.DataFrame({
        "price":         price,
        "comp_avg":      comp_avg,
        "hour":          hour,
        "day_of_week":   day,
        "weather_boost": weather_boost,
        "trend_score":   trend_score,
        "demand":        demand,
    })

FEATURES = ["price", "comp_avg", "hour", "day_of_week",
            "weather_boost", "trend_score"]

def train():
    df = generate_realistic_data()
    X  = df[FEATURES]
    y  = df["demand"]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

    model = XGBRegressor(n_estimators=300, learning_rate=0.05,
                         max_depth=6, subsample=0.8, random_state=42)
    model.fit(X_tr, y_tr,
              eval_set=[(X_te, y_te)],
              verbose=False)

    preds = model.predict(X_te)
    print(f"MAE : {mean_absolute_error(y_te, preds):.1f} units")
    print(f"R²  : {r2_score(y_te, preds):.4f}")

    joblib.dump(model, "demand_model.pkl")
    print("Saved → demand_model.pkl")
    return model

def predict_demand(price, signals: dict):
    model = joblib.load("demand_model.pkl")
    X = pd.DataFrame([{
        "price":         price,
        "comp_avg":      signals["comp_avg"],
        "hour":          signals["hour"],
        "day_of_week":   signals["day_of_week"],
        "weather_boost": signals["weather_boost"],
        "trend_score":   signals["trend_score"],
    }])
    return max(0, float(model.predict(X)[0]))

if __name__ == "__main__":
    train()