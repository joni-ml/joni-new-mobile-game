"""
מוריד מחירי ביטקוין אמיתיים לתיקייה data/ בפורמט time,close.

  python3 fetch_data.py            # מחיר יומי 2010 עד היום + מחיר לשעה 2011-2017
  python3 fetch_data.py --recent   # גם מחיר לשעה של השנתיים האחרונות מ-Binance
"""

import argparse
import csv
import io
import os
import urllib.request
from datetime import datetime, timezone

from exchanges import binance_history

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

# מחיר יומי מ-Coin Metrics (נתונים פתוחים לשימוש אישי)
DAILY_URL = "https://raw.githubusercontent.com/coinmetrics/data/master/csv/btc.csv"
# מחיר לשעה מבורסת Bitstamp, 2011-2017 (מתוך ספריית ta בגיטהאב)
HOURLY_URL = "https://raw.githubusercontent.com/bukosabino/ta/master/test/data/datas.csv"


def download(url):
    req = urllib.request.Request(url, headers={"User-Agent": "trading-evolution/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return io.StringIO(r.read().decode())


def write(name, rows):
    path = os.path.join(DATA, name)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time", "close"])
        w.writerows(rows)
    print(f"נשמר {path}: {len(rows)} נרות, {rows[0][0]} עד {rows[-1][0]}")


def iso(ts):
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--recent", action="store_true", help="גם מחירים לשעה מ-Binance")
    p.add_argument("--days", type=int, default=730, help="כמה ימים אחורה להוריד מ-Binance")
    args = p.parse_args()
    os.makedirs(DATA, exist_ok=True)

    write("btc_daily.csv", [(r["time"], r["PriceUSD"]) for r in csv.DictReader(download(DAILY_URL))
                            if r["PriceUSD"]])
    # בקובץ הזה יש שעות שבהן הבורסה לא עבדה, והמחיר בהן הוא 1.7e+308 - מדלגים עליהן
    write("btc_hourly_2011_2017.csv", [(iso(int(float(r["Timestamp"]))), r["Close"])
                                       for r in csv.DictReader(download(HOURLY_URL))
                                       if 0 < float(r["Close"]) < 1e6])
    if args.recent:
        write("btc_hourly_recent.csv", [(iso(t), p) for t, p in binance_history(args.days)])


if __name__ == "__main__":
    main()
