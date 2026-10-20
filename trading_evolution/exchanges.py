"""
קריאת מחירי ביטקוין מבורסות אמיתיות דרך ה-API הציבורי שלהן.
רק קריאת מחירים: אין כאן מפתחות, אין חשבון ואין שום קנייה או מכירה אמיתית.
"""

import json
import time
import urllib.request
from datetime import datetime, timezone

HOUR = 3600


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "trading-evolution/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def closed_only(candles):
    """משאיר רק נרות שכבר נסגרו (הנר של השעה הנוכחית עוד זז), מהישן לחדש."""
    now = time.time()
    return sorted((t, p) for t, p in candles if t + HOUR <= now)


def kraken():
    data = get_json("https://api.kraken.com/0/public/OHLC?pair=XBTUSD&interval=60")
    if data.get("error"):
        raise RuntimeError(data["error"])
    rows = next(v for k, v in data["result"].items() if k != "last")
    return closed_only((int(r[0]), float(r[4])) for r in rows)


def binance(start_ms=None):
    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=1000"
    if start_ms is not None:
        url += f"&startTime={start_ms}"
    return closed_only((int(r[0]) // 1000, float(r[4])) for r in get_json(url))


def coinbase():
    rows = get_json("https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=3600")
    return closed_only((int(r[0]), float(r[4])) for r in rows)


SOURCES = {"kraken": kraken, "binance": binance, "coinbase": coinbase}


def latest_hourly():
    """נרות של שעה מהבורסה הראשונה שעונה. מחזיר (שם הבורסה, [(זמן, מחיר), ...])."""
    errors = []
    for name, fetch in SOURCES.items():
        try:
            candles = fetch()
            if candles:
                return name, [(datetime.fromtimestamp(t, timezone.utc).replace(tzinfo=None), p)
                              for t, p in candles]
        except Exception as e:
            errors.append(f"{name}: {e}")
    raise RuntimeError("אף בורסה לא ענתה - " + " | ".join(errors))


def binance_history(days):
    """היסטוריה של נרות שעה מ-Binance, עד כמה שנים אחורה (1000 נרות בכל בקשה)."""
    start = int((time.time() - days * 86400) * 1000)
    out = []
    while True:
        batch = binance(start)
        out += batch
        if len(batch) < 999:
            return out
        start = (batch[-1][0] + HOUR) * 1000
        time.sleep(0.3)   # לא להציף את הבורסה בבקשות
