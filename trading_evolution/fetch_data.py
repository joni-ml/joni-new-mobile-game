"""
מוריד מחירים אמיתיים של המטבעות שב-settings.toml לתיקייה data/ (פורמט time,close).

  python fetch_data.py            # מחיר יומי של כל מטבע, מההתחלה עד היום
  python fetch_data.py --recent   # גם מחיר לשעה של השנתיים האחרונות (מ-Binance)
  python fetch_data.py --old      # מחיר ביטקוין לשעה 2011-2017
"""

import argparse
import csv
import io
import os
import urllib.request
from datetime import datetime, timezone

from core import load_settings
from exchanges import binance_history
import internet as net

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

# מחיר יומי מ-Coin Metrics (נתונים פתוחים לשימוש אישי)
DAILY_URL = "https://raw.githubusercontent.com/coinmetrics/data/master/csv/{}.csv"
# מחיר ביטקוין לשעה מבורסת Bitstamp, 2011-2017 (מתוך ספריית ta בגיטהאב)
OLD_HOURLY_URL = "https://raw.githubusercontent.com/bukosabino/ta/master/test/data/datas.csv"


def download(url):
    req = urllib.request.Request(url, headers={"User-Agent": "trading-evolution/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return io.StringIO(r.read().decode())


def write(folder, asset, rows):
    os.makedirs(os.path.join(DATA, folder), exist_ok=True)
    path = os.path.join(DATA, folder, f"{asset}.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time", "close"])
        w.writerows(rows)
    print(f"  {asset}: {len(rows)} נרות, {rows[0][0][:10]} עד {rows[-1][0][:10]}")


def iso(ts):
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--settings", default=os.path.join(HERE, "settings.toml"))
    p.add_argument("--recent", action="store_true", help="גם מחירים לשעה מ-Binance")
    p.add_argument("--days", type=int, default=730, help="כמה ימים אחורה להוריד מ-Binance")
    p.add_argument("--old", action="store_true", help="מחיר ביטקוין לשעה 2011-2017")
    args = p.parse_args()
    assets = load_settings(args.settings).assets

    print("מחיר יומי (data/daily):")
    for asset in assets:
        try:
            rows = [(r["time"], r["PriceUSD"]) for r in csv.DictReader(download(DAILY_URL.format(asset.lower())))
                    if r.get("PriceUSD")]
            if not rows:
                raise ValueError("אין שם מחירים")
            write("daily", asset, rows)
        except Exception as e:
            print(f"  {asset}: לא נמצא מחיר יומי ({e})")

    print("חושים מהאינטרנט (data/internet):")
    net.download_history(assets)

    if args.recent:
        print("מחיר לשעה, שנתיים אחרונות (data/hourly):")
        for asset in assets:
            try:
                write("hourly", asset, [(iso(t), p) for t, p in binance_history(asset, args.days)])
            except Exception as e:
                print(f"  {asset}: לא הצלחתי להוריד ({e})")

    if args.old:
        print("מחיר ביטקוין לשעה 2011-2017 (data/old):")
        # בקובץ הזה יש שעות שבהן הבורסה לא עבדה, והמחיר בהן הוא 1.7e+308 - מדלגים עליהן
        write("old", "BTC", [(iso(int(float(r["Timestamp"]))), r["Close"])
                             for r in csv.DictReader(download(OLD_HOURLY_URL))
                             if 0 < float(r["Close"]) < 1e6])


if __name__ == "__main__":
    main()
