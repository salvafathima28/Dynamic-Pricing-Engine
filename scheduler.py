import schedule
import time
import sqlite3
import json
import traceback
from datetime import datetime
from market_fetcher import fetch_signals_for_product
from config import PRODUCTS

CACHE_DB = "pricing_cache.db"

def init_cache():
    con = sqlite3.connect(CACHE_DB)
    con.execute("""CREATE TABLE IF NOT EXISTS cache (
        product_id  TEXT PRIMARY KEY,
        data        TEXT,
        updated_at  TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS price_history (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id  TEXT,
        your_price  REAL,
        market_min  REAL,
        market_avg  REAL,
        suggested   REAL,
        action      TEXT,
        urgency     TEXT,
        sellers     INTEGER,
        recorded_at TEXT)""")
    con.commit()
    con.close()

def price_all_products():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking market prices for {len(PRODUCTS)} products...")
    con     = sqlite3.connect(CACHE_DB)
    success = 0
    alerts  = []

    for p in PRODUCTS:
        try:
            signals = fetch_signals_for_product(p)

            con.execute(
                "INSERT OR REPLACE INTO cache VALUES (?,?,?)",
                (p["id"], json.dumps({**signals, "product": p}),
                 datetime.now().isoformat()))

            con.execute(
                """INSERT INTO price_history
                   (product_id,your_price,market_min,market_avg,
                    suggested,action,urgency,sellers,recorded_at)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (p["id"], p["base_price"],
                 signals["comp_min"], signals["comp_avg"],
                 signals["suggested_price"], signals["action"],
                 signals["urgency"], signals["sellers_found"],
                 datetime.now().isoformat()))

            con.commit()

            if signals["urgency"] in ("high","medium"):
                alerts.append(
                    f"{p['name']}: {signals['action']} "
                    f"(gap ₹{abs(signals['comp_delta']):,})")

            status = "⚠" if signals["urgency"]=="high" else "✓"
            print(f"  {status}  {p['name'][:35]:35s}"
                  f"  Your:₹{p['base_price']:>8,.0f}"
                  f"  Market:₹{signals['comp_avg']:>8,.0f}"
                  f"  → {signals['action']}")

            success += 1
            time.sleep(2)

        except Exception:
            print(f"  ERR {p['name']}")
            traceback.print_exc()

    con.close()
    if alerts:
        print(f"\n  ALERTS ({len(alerts)}):")
        for a in alerts:
            print(f"    · {a}")
    print(f"\nDone. {success}/{len(PRODUCTS)} products updated.\n")

def get_cached_prices() -> list:
    con  = sqlite3.connect(CACHE_DB)
    rows = con.execute(
        "SELECT data FROM cache ORDER BY updated_at DESC").fetchall()
    con.close()
    results = []
    for r in rows:
        d = json.loads(r[0])
        results.append(d)
    return results

def get_price_history(product_id: str, days: int = 7) -> list:
    con  = sqlite3.connect(CACHE_DB)
    rows = con.execute(
        """SELECT your_price,market_min,market_avg,
                  suggested,action,urgency,sellers,recorded_at
           FROM price_history
           WHERE product_id=?
             AND recorded_at >= datetime('now',?)
           ORDER BY recorded_at ASC""",
        (product_id, f"-{days} days")).fetchall()
    con.close()
    return [{"your_price":r[0],"market_min":r[1],"market_avg":r[2],
             "suggested":r[3],"action":r[4],"urgency":r[5],
             "sellers":r[6],"recorded_at":r[7]} for r in rows]

init_cache()

if __name__ == "__main__":
    price_all_products()
    schedule.every(30).minutes.do(price_all_products)
    print("Scheduler running every 30 min. Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(10)