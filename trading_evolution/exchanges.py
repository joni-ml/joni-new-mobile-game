"""
קריאת מחירים של מטבעות מבורסות אמיתיות דרך ה-API הציבורי שלהן.
רק קריאת מחירים: אין כאן מפתחות, אין חשבון ואין שום קנייה או מכירה אמיתית.
"""

import json
import time
import urllib.request
from datetime import datetime, timezone

# אורכי נר שכל הבורסות תומכות בהם: דקות -> השם אצל Binance
CANDLES = {1: "1m", 5: "5m", 15: "15m", 60: "1h"}


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "trading-evolution/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def closed_only(candles, seconds):
    """משאיר רק נרות שכבר נסגרו (הנר הנוכחי עוד זז), מהישן לחדש."""
    now = time.time()
    return sorted((t, p) for t, p in candles if t + seconds <= now)


def kraken(asset, mins):
    pair = {"BTC": "XBT", "DOGE": "XDG"}.get(asset, asset) + "USD"
    data = get_json(f"https://api.kraken.com/0/public/OHLC?pair={pair}&interval={mins}")
    if data.get("error"):
        raise RuntimeError(data["error"])
    rows = next(v for k, v in data["result"].items() if k != "last")
    return closed_only(((int(r[0]), float(r[4])) for r in rows), mins * 60)


def binance(asset, mins, start_ms=None):
    url = f"https://api.binance.com/api/v3/klines?symbol={asset}USDT&interval={CANDLES[mins]}&limit=1000"
    if start_ms is not None:
        url += f"&startTime={start_ms}"
    return closed_only(((int(r[0]) // 1000, float(r[4])) for r in get_json(url)), mins * 60)


def coinbase(asset, mins):
    rows = get_json(f"https://api.exchange.coinbase.com/products/{asset}-USD/candles?granularity={mins * 60}")
    return closed_only(((int(r[0]), float(r[4])) for r in rows), mins * 60)


SOURCES = {"kraken": kraken, "binance": binance, "coinbase": coinbase}


def latest(asset, mins):
    """נרות אחרונים של מטבע מהבורסה הראשונה שעונה. מחזיר (שם הבורסה, [(זמן, מחיר), ...])."""
    if mins not in CANDLES:
        raise SystemExit(f"אורך נר לא נתמך: {mins} דקות. אפשר: 1m, 5m, 15m, 1h")
    errors = []
    for name, fetch in SOURCES.items():
        try:
            candles = fetch(asset, mins)
            if candles:
                return name, [(datetime.fromtimestamp(t, timezone.utc).replace(tzinfo=None), p)
                              for t, p in candles]
        except Exception as e:
            errors.append(f"{name}: {e}")
    raise RuntimeError(f"אף בורסה לא נתנה מחיר של {asset} - " + " | ".join(errors))


def binance_history(asset, days, mins=60):
    """היסטוריה של נרות מ-Binance, עד כמה שנים אחורה (1000 נרות בכל בקשה)."""
    start = int((time.time() - days * 86400) * 1000)
    out = []
    while True:
        batch = binance(asset, mins, start)
        out += batch
        if len(batch) < 999:
            return out
        start = (batch[-1][0] + mins * 60) * 1000
        time.sleep(0.3)   # לא להציף את הבורסה בבקשות
