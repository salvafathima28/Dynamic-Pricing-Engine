
import pandas as pd
import os

SERP_API_KEY = "c36b5bfc6d781626680556cbd0d0e5ad06a87e9fd2fbe3865c5717791590db52"   # free at serpapi.com

CITY_LAT  = 30.9010
CITY_LON  = 75.8573

FAIRNESS_LAMBDA = 0.3
PRICE_STEP      = 500.0    # bigger step for real electronics prices

_csv_path = os.path.join(os.path.dirname(__file__), "products.csv")
_df       = pd.read_csv(_csv_path)

# Rename your_price → base_price so rest of code works
if "your_price" in _df.columns:
    _df = _df.rename(columns={"your_price": "base_price"})

PRODUCTS  = _df.to_dict("records")
MIN_PRICE = min(p["min_price"]  for p in PRODUCTS)
MAX_PRICE = max(p["max_price"]  for p in PRODUCTS)
BASE_PRICE = PRODUCTS[0]["base_price"]