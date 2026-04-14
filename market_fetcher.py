import requests
import datetime
import time
from config import SERP_API_KEY, CITY_LAT, CITY_LON

def fetch_weather_score():
    url = (f"https://api.open-meteo.com/v1/forecast"
           f"?latitude={CITY_LAT}&longitude={CITY_LON}"
           f"&current=temperature_2m,precipitation,weathercode"
           f"&timezone=Asia/Kolkata")
    try:
        r       = requests.get(url, timeout=5).json()
        current = r["current"]
        temp    = current["temperature_2m"]
        rain    = current["precipitation"]
        code    = current["weathercode"]
        boost   = 0.0
        if rain > 2:            boost += 0.2
        if code in range(61,82):boost += 0.15
        if temp > 38 or temp<10:boost += 0.1
        return round(min(boost,0.5),3), temp, rain
    except:
        return 0.1, 28.0, 0.0

def fetch_market_prices(product: dict) -> dict:
    """
    Searches Google Shopping for the exact product model.
    Returns min, avg, max price and list of sellers found.
    """
    try:
        url    = "https://serpapi.com/search"
        params = {
            "engine":  "google_shopping",
            "q":       product["keyword"],
            "api_key": SERP_API_KEY,
            "gl":      "in",
            "hl":      "en",
            "num":     10
        }
        r       = requests.get(url, params=params, timeout=10).json()
        results = r.get("shopping_results", [])

        prices  = []
        sellers = []
        for item in results:
            p = item.get("price","")
            if isinstance(p, str):
                p = p.replace("₹","").replace(",","").strip()
                try:
                    val = float(p)
                    # Sanity check — ignore prices wildly outside range
                    if product["min_price"]*0.5 <= val <= product["max_price"]*2:
                        prices.append(val)
                        sellers.append(item.get("source","Unknown"))
                except:
                    pass
            elif isinstance(p,(int,float)):
                prices.append(float(p))
                sellers.append(item.get("source","Unknown"))

        if not prices:
            base = product["base_price"]
            return {
                "market_min":   base,
                "market_avg":   base,
                "market_max":   base,
                "sellers_found": 0,
                "sellers":      [],
                "data_source":  "fallback"
            }

        return {
            "market_min":    round(min(prices), 0),
            "market_avg":    round(sum(prices)/len(prices), 0),
            "market_max":    round(max(prices), 0),
            "sellers_found": len(prices),
            "sellers":       sellers[:5],
            "data_source":   "live"
        }
    except Exception as e:
        print(f"  Market fetch error for {product['name']}: {e}")
        base = product["base_price"]
        return {
            "market_min":    base,
            "market_avg":    base,
            "market_max":    base,
            "sellers_found": 0,
            "sellers":       [],
            "data_source":   "error"
        }

def compute_suggestion(product: dict, market: dict) -> dict:
    """
    Core logic: given your price and market prices,
    what should you do?
    """
    your_price  = product["base_price"]
    market_avg  = market["market_avg"]
    market_min  = market["market_min"]

    gap         = your_price - market_avg   # positive = you're expensive
    gap_pct     = gap / market_avg * 100

    if gap_pct > 5:
        action   = "Lower price"
        # Suggest just below market avg to be competitive
        suggested = max(market_min * 1.01, market_avg * 0.985)
        suggested = round(suggested / 50) * 50   # round to nearest 50
        urgency   = "high" if gap_pct > 10 else "medium"
    elif gap_pct < -8:
        action    = "Raise price"
        # You're leaving money on table — go up but stay below avg
        suggested = min(market_avg * 0.97, product["max_price"])
        suggested = round(suggested / 50) * 50
        urgency   = "low"
    else:
        action    = "Hold"
        suggested = your_price
        urgency   = "none"

    # Never go below min or above max
    suggested = max(product["min_price"],
                min(product["max_price"], suggested))

    saving_opportunity = suggested - your_price  # negative = you'll lose revenue
    return {
        "action":             action,
        "suggested_price":    int(suggested),
        "gap_vs_market":      int(gap),
        "gap_pct":            round(gap_pct, 1),
        "urgency":            urgency,
        "revenue_impact":     int(suggested - your_price),
    }

def fetch_signals_for_product(product: dict) -> dict:
    """Full signal fetch for one product — used by scheduler."""
    now = datetime.datetime.now()
    weather_boost, temp, rain = fetch_weather_score()
    market  = fetch_market_prices(product)
    suggest = compute_suggestion(product, market)

    # Simple trend score from time of day
    hour = now.hour
    day  = now.weekday()
    if 19 <= hour <= 22:   trend = 0.75
    elif 10 <= hour <= 13: trend = 0.60
    elif 0 <= hour <= 6:   trend = 0.30
    else:                  trend = 0.45
    if day >= 5: trend = min(1.0, trend + 0.15)

    return {
        "product_id":     product["id"],
        "timestamp":      now.isoformat(),
        "hour":           now.hour,
        "day_of_week":    now.weekday(),
        "is_weekend":     int(now.weekday() >= 5),
        "weather_boost":  weather_boost,
        "temperature":    temp,
        "rainfall":       rain,
        "trend_score":    trend,
        "comp_min":       market["market_min"],
        "comp_avg":       market["market_avg"],
        "comp_max":       market["market_max"],
        "comp_delta":     int(product["base_price"] - market["market_avg"]),
        "sellers_found":  market["sellers_found"],
        "sellers":        market["sellers"],
        "data_source":    market["data_source"],
        "action":         suggest["action"],
        "suggested_price":suggest["suggested_price"],
        "gap_pct":        suggest["gap_pct"],
        "urgency":        suggest["urgency"],
        "revenue_impact": suggest["revenue_impact"],
    }

# Keep backward compatibility
def fetch_all_signals():
    from config import PRODUCTS
    return fetch_signals_for_product(PRODUCTS[0])