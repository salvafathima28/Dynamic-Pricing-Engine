import pandas as pd
import os
from datetime import datetime
import sqlite3

CSV_PATH = os.path.join(os.path.dirname(__file__), "products.csv")
LOG_DB   = "pricing_cache.db"

def load_products() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)
    if "your_price" in df.columns and "base_price" not in df.columns:
        df = df.rename(columns={"your_price": "base_price"})
    if "cost_price" not in df.columns:
        df["cost_price"] = 0
    return df

def save_price(product_id: str, new_price: float, old_price: float) -> bool:
    """Update your_price in CSV and log the change."""
    try:
        df = pd.read_csv(CSV_PATH)
        price_col = "your_price" if "your_price" in df.columns else "base_price"
        mask = df["id"] == product_id
        if not mask.any():
            return False

        df.loc[mask, price_col] = int(new_price)
        df.to_csv(CSV_PATH, index=False)

        # Log change to database
        _log_price_change(product_id, old_price, new_price)
        return True
    except Exception as e:
        print(f"Error saving price: {e}")
        return False

def _log_price_change(product_id: str, old_price: float, new_price: float):
    con = sqlite3.connect(LOG_DB)
    con.execute("""CREATE TABLE IF NOT EXISTS price_changes (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id  TEXT,
        old_price   REAL,
        new_price   REAL,
        change_amt  REAL,
        changed_at  TEXT
    )""")
    con.execute(
        "INSERT INTO price_changes VALUES (NULL,?,?,?,?,?)",
        (product_id, old_price, new_price,
         new_price - old_price,
         datetime.now().isoformat()))
    con.commit()
    con.close()

def get_price_changes(days: int = 30) -> list:
    """Return full log of manual price changes."""
    try:
        con  = sqlite3.connect(LOG_DB)
        rows = con.execute(
            """SELECT product_id, old_price, new_price,
                      change_amt, changed_at
               FROM price_changes
               WHERE changed_at >= datetime('now', ?)
               ORDER BY changed_at DESC""",
            (f"-{days} days",)).fetchall()
        con.close()
        return [{"product_id": r[0], "old_price": int(r[1]),
                 "new_price":  int(r[2]), "change_amt": int(r[3]),
                 "changed_at": r[4]} for r in rows]
    except:
        return []

def compute_margin(your_price: float, cost_price: float) -> dict:
    """Calculate profit margin metrics."""
    if cost_price <= 0:
        return {"profit": 0, "margin_pct": 0, "margin_label": "No cost set"}

    profit     = your_price - cost_price
    margin_pct = (profit / your_price) * 100

    if margin_pct >= 20:
        label = "Healthy"
        color = "green"
    elif margin_pct >= 10:
        label = "Moderate"
        color = "amber"
    elif margin_pct >= 0:
        label = "Thin"
        color = "red"
    else:
        label = "Loss!"
        color = "red"

    return {
        "profit":      int(profit),
        "margin_pct":  round(margin_pct, 1),
        "margin_label": label,
        "margin_color": color,
    }