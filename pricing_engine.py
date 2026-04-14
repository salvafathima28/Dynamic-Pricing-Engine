import torch
import numpy as np
import pandas as pd
from train_rl import DQN
from demand_model import predict_demand
from data_fetcher import fetch_signals_for_product
from config import PRODUCTS, PRICE_STEP

def load_agent():
    model = DQN()
    model.load_state_dict(torch.load("dqn_model.pth", map_location="cpu"))
    model.eval()
    return model

def get_recommended_price(signals: dict, product: dict = None) -> dict:
    if product is None:
        product = PRODUCTS[0]

    agent = load_agent()
    state = torch.FloatTensor([
        product["base_price"],
        signals["comp_avg"],
        signals["hour"],
        signals["day_of_week"],
        signals["weather_boost"],
        signals["trend_score"],
    ])
    with torch.no_grad():
        action = agent(state).argmax().item()

    delta     = {0: -PRICE_STEP, 1: 0, 2: PRICE_STEP}[action]
    rl_price  = float(np.clip(
        product["base_price"] + delta,
        product["min_price"], product["max_price"]))

    fair_price = min(rl_price, signals["comp_avg"] * 1.15)
    fair_price = float(np.clip(
        fair_price, product["min_price"], product["max_price"]))

    demand       = predict_demand(fair_price, signals)
    action_label = {0: "Price down", 1: "Hold", 2: "Price up"}[action]

    return {
        "product_id":          product["id"],
        "product_name":        product["name"],
        "category":            product["category"],
        "recommended_price":   round(fair_price, 2),
        "base_price":          product["base_price"],
        "rl_price":            round(rl_price, 2),
        "rl_action":           action_label,
        "predicted_demand":    round(demand, 1),
        "predicted_revenue":   round(fair_price * demand, 2),
        "comp_avg":            signals["comp_avg"],
        "trend_score":         signals["trend_score"],
        "signals":             signals,
    }

def get_shop_prices() -> list:
    """Get recommended price for every product in the shop."""
    import time
    results = []
    for product in PRODUCTS:
        print(f"  Pricing: {product['name']}")
        signals = fetch_signals_for_product(product)
        result  = get_recommended_price(signals=signals, product=product)
        results.append(result)
        time.sleep(0.5)
    return results

if __name__ == "__main__":
    import json
    result = get_recommended_price(
        signals=__import__('data_fetcher').fetch_all_signals(),
        product=PRODUCTS[0]
    )
    print(json.dumps(result, indent=2))