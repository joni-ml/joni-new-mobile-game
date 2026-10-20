"""
מסחר חי על נייר: מחירי ביטקוין אמיתיים מהבורסה בזמן אמת, אבל כסף מזויף.
הבוטים ממשיכים להתפתח כל יום, וכל המצב נשמר בקובץ live_state.json -
אפשר לכבות את המחשב ולהמשיך מחר מאותה נקודה.

  python3 live.py            # רץ ברציפות (Ctrl+C כדי לעצור)
  python3 live.py --once     # בדיקה אחת ויציאה (טוב לתזמון אוטומטי)
  python3 live.py --status   # רק להראות מה המצב, בלי להתחבר לבורסה
  python3 live.py --reset    # להתחיל מחדש

אם קיים brains.json (מהאימון ב-evolution_sim.py), הבוטים הראשונים יתחילו ממנו.
"""

import argparse
import json
import os
import time
from datetime import datetime

from core import MAX_WINDOW, Market, World, load_brains
from exchanges import latest_hourly

HISTORY = MAX_WINDOW + 60   # כמה נרות אחרונים לזכור בשביל האינדיקטורים


def load_state(path):
    with open(path) as f:
        s = json.load(f)
    s["history"] = [(datetime.fromisoformat(t), p) for t, p in s["history"]]
    s["world"] = World.from_dict(s["world"])
    return s


def save_state(path, s):
    out = {**s, "history": [(t.isoformat(), p) for t, p in s["history"]], "world": s["world"].to_dict()}
    with open(path + ".tmp", "w") as f:
        json.dump(out, f)
    os.replace(path + ".tmp", path)   # שמירה בטוחה גם אם המחשב נכבה באמצע


def new_state(args):
    seeds = load_brains(args.brains) if os.path.exists(args.brains) else ()
    world = World(args.cut, seeds=seeds)
    world.populate(args.bots)
    origin = f"מ-{len(seeds)} אסטרטגיות מאומנות" if seeds else "עם אסטרטגיות אקראיות"
    print(f"נוצרו {args.bots} בוטים {origin}.")
    return {"history": [], "world": world}


def tick(s, log):
    """מביא נרות חדשים מהבורסה ונותן לבוטים לסחור על כל נר שעוד לא ראו."""
    source, candles = latest_hourly()
    world, hist = s["world"], s["history"]
    if not hist:                       # פעם ראשונה: רק לומדים את ההיסטוריה, בלי לסחור
        hist.extend(candles[-HISTORY:])
        print(f"התחברתי ל-{source}. קיבלתי {len(hist)} שעות של היסטוריה. מתחילים לסחור.")
        return
    for t, price in candles:
        if t <= hist[-1][0]:
            continue
        if t.date() != hist[-1][0].date():
            world.end_of_day(hist[-1][1], log)
            report(world, hist[-1][1])
        hist.append((t, price))
        del hist[:-HISTORY]
        m = Market([p for _, p in hist])
        for bot in world.bots:
            bot.step(m, len(hist) - 1)


def report(world, price):
    inside = sum(b.value(price) for b in world.bots)
    net = world.owner_profit + inside - world.invested
    print(f"יום {world.day}: {len(world.bots)} בוטים | בתוך הבוטים {inside:.2f} ש\"ח | "
          f"לקחת עד עכשיו {world.owner_profit:.2f} | נקי {net:+.2f} ש\"ח")


def status(s):
    world, hist = s["world"], s["history"]
    if not hist:
        print("עוד לא התחלנו לסחור.")
        return
    print(f"מחיר אחרון: {hist[-1][1]:,.0f}$ ({hist[-1][0]:%d/%m %H:00})")
    report(world, hist[-1][1])
    print(f"השקעת {world.invested:.2f} ש\"ח | מתו {world.deaths} | שוכפלו {world.clones}")
    for b in world.best(3):
        print(f"  בוט #{b.id} (דור {b.generation}): {b.value(hist[-1][1]):.2f} ש\"ח - {b.genome.describe()}")


def main():
    p = argparse.ArgumentParser(description="מסחר חי על נייר עם מחירים אמיתיים")
    p.add_argument("--state", default="live_state.json")
    p.add_argument("--brains", default="brains.json")
    p.add_argument("--bots", type=int, default=10)
    p.add_argument("--cut", type=float, default=0.01, help="כמה הבעלים לוקח כל יום (0.01 = 1%%)")
    p.add_argument("--every", type=int, default=10, help="כל כמה דקות לבדוק מחיר")
    p.add_argument("--once", action="store_true")
    p.add_argument("--status", action="store_true")
    p.add_argument("--reset", action="store_true")
    p.add_argument("--verbose", action="store_true", help="להראות כל מוות ושכפול")
    args = p.parse_args()

    if args.reset and os.path.exists(args.state):
        os.remove(args.state)
    s = load_state(args.state) if os.path.exists(args.state) else new_state(args)
    if args.status:
        return status(s)

    log = print if args.verbose else None
    while True:
        try:
            tick(s, log)
            save_state(args.state, s)
        except Exception as e:
            print(f"שגיאה בחיבור לבורסה, אנסה שוב אחר כך: {e}")
        if args.once:
            return
        time.sleep(args.every * 60)


if __name__ == "__main__":
    main()
