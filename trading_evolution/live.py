"""
מסחר חי על נייר: מחירים אמיתיים מהבורסה בזמן אמת, אבל כסף מזויף.
ההגדרות נמצאות ב-settings.toml, ואפשר לשנות אותן בזמן שהתוכנה רצה.
כל המצב נשמר ב-live_state.json, אז אפשר לכבות את המחשב ולהמשיך מאותה נקודה.

  python live.py            # רץ ברציפות (Ctrl+C כדי לעצור)
  python live.py --once     # בדיקה אחת ויציאה (טוב לתזמון אוטומטי)
  python live.py --status   # רק להראות מה המצב, בלי להתחבר לבורסה
  python live.py --reset    # להתחיל מחדש

את הבוטים רואים בדף live_dashboard.html: חלון לכל בוט, והוא מתרענן לבד.
אם קיים brains.json (מהאימון ב-evolution_sim.py), הבוטים הראשונים יתחילו ממנו.
"""

import argparse
import json
import os
import time
from dataclasses import replace
from datetime import datetime, timedelta

from core import Market, World, load_brains, load_settings, members, minutes
from dashboard import write_dashboard
from exchanges import latest
import internet as net
from phone import announce, serve

HERE = os.path.dirname(os.path.abspath(__file__))
HISTORY = 720   # כמה נרות אחרונים לזכור בשביל האינדיקטורים וזיכרון הדפוסים (כמה שהבורסה נותנת)
TITLE = "בוטי מסחר: מסחר חי על נייר"


def load_state(path, cfg):
    with open(path) as f:
        s = json.load(f)
    s["times"] = [datetime.fromisoformat(t) for t in s["times"]]
    s["world"] = World.from_dict(s["world"], cfg)
    return s


def save_state(path, s):
    out = {**s, "times": [t.isoformat() for t in s["times"]], "world": s["world"].to_dict()}
    with open(path + ".tmp", "w") as f:
        json.dump(out, f)
    os.replace(path + ".tmp", path)   # שמירה בטוחה גם אם המחשב נכבה באמצע


def new_state(cfg, brains):
    seeds = load_brains(brains, minutes(cfg.candle)) if os.path.exists(brains) else ()
    world = World(cfg, minutes(cfg.candle), seeds=seeds)
    world.populate()
    origin = f"מ-{len(seeds)} אסטרטגיות מאומנות" if seeds else "עם אסטרטגיות אקראיות"
    print(f"נוצרו {len(world.bots)} בוטים {origin}.")
    return {"candle": minutes(cfg.candle), "times": [], "prices": {}, "world": world}


def fetch(assets, mins, must_have):
    """מביא מחירים לכל מטבע. מטבע שלא עובד ואף בוט לא מחזיק בו - מדלגים עליו בינתיים."""
    got = {}
    for asset in assets:
        try:
            got[asset] = dict(latest(asset, mins)[1])
        except Exception as e:
            if asset in must_have:
                raise
            print(f"מדלג בינתיים על {asset}: {e}")
    return got


def fill(candles, times):
    """עמודת מחירים של מטבע לפי רשימת זמנים. זמן חסר מקבל את המחיר הקודם."""
    last = candles[min(candles)]
    return [last := candles.get(t, last) for t in times]


def tick(s, cfg):
    """מביא נרות חדשים מהבורסה ונותן לבוטים לסחור על כל נר שעוד לא ראו."""
    world = s["world"]
    mins = minutes(cfg.candle)
    if s["candle"] != mins:            # אורך הנר השתנה בהגדרות: לומדים היסטוריה מחדש
        s.update(candle=mins, times=[], prices={})
        for b in world.bots:           # ניחושים על נרות באורך הישן כבר לא יתבררו
            b.forget()
    world.candle = mins
    held = {a for b in world.bots for a in members(b.genome.asset)}
    got = fetch(list(dict.fromkeys(cfg.assets + sorted(held))), mins, held)
    world.cfg = replace(cfg, assets=[a for a in cfg.assets if a in got] or sorted(held))

    if not s["times"]:                 # פעם ראשונה: רק לומדים את ההיסטוריה, בלי לסחור
        common = sorted(set.intersection(*(set(c) for c in got.values())))[-HISTORY:]
        s["times"] = common
        s["prices"] = {a: [c[t] for t in common] for a, c in got.items()}
        print(f"קיבלתי {len(common)} נרות של היסטוריה ל-{len(got)} מטבעות. מתחילים לסחור.")
        ex = net.extras(list(s["prices"]), common, mins < 1440)
        world.step({a: Market(col, ex[a]) for a, col in s["prices"].items()}, len(common) - 1, common[-1])
        return
    s["prices"] = {a: col for a, col in s["prices"].items() if a in got}
    for a, c in got.items():           # מטבע חדש שנוסף להגדרות
        if a not in s["prices"]:
            s["prices"][a] = fill(c, s["times"])
    upto = min(max(c) for c in got.values())   # לא רצים לפני המטבע הכי איטי
    new = sorted({t for c in got.values() for t in c if s["times"][-1] < t <= upto})
    if not new:
        return
    if new[0] - s["times"][-1] > timedelta(minutes=mins):   # הפסקה ארוכה (המחשב היה כבוי): יש נרות שלא נראו
        for b in world.bots:
            b.forget()
    times, cols = s["times"] + new, {}
    for a, col in s["prices"].items():
        last, cols[a] = col[-1], list(col)
        for t in new:
            last = got[a].get(t, last)
            cols[a].append(last)
    ex = net.extras(list(cols), times, mins < 1440)   # החושים מהאינטרנט, פעם אחת לכל הנרות החדשים
    for k in range(len(s["times"]), len(times)):      # כל נר חדש בתורו, עם HISTORY הנרות שלפניו
        lo = max(0, k + 1 - HISTORY)
        markets = {a: Market(col[lo:k + 1], {n: (raw[lo:k + 1], sig[lo:k + 1]) for n, (raw, sig) in ex[a].items()})
                   for a, col in cols.items()}
        world.step(markets, k - lo, times[k])
    s["times"] = times[-HISTORY:]
    s["prices"] = {a: col[-HISTORY:] for a, col in cols.items()}


def status(s, cfg, chart):
    world = s["world"]
    if not world.history:
        print("עוד לא התחלנו לסחור.")
        return
    last = world.history[-1]
    net = last["collected"] + last["inside"] - last["invested"]
    print(f"עודכן לאחרונה: {last['time']} | {len(world.bots)} בוטים | נשאר בבוטים {last['inside']:.2f} ש\"ח")
    print(f"השקעת {last['invested']:.2f} | לקחת {last['collected']:.2f} | נקי {net:+.2f} ש\"ח | "
          f"מבחנים {world.selections}, מתו {world.deaths}, שוכפלו {world.clones}, "
          f"בחרו לא להשתכפל {world.declined}, נולדו במקומות ריקים {world.refilled}")
    write_dashboard(chart, TITLE, [("הבוטים", world)], cfg, live=True)
    print(f"הדף עם הבוטים: {os.path.abspath(chart)}")


def main():
    p = argparse.ArgumentParser(description="מסחר חי על נייר עם מחירים אמיתיים")
    p.add_argument("--settings", default=os.path.join(HERE, "settings.toml"))
    p.add_argument("--state", default="live_state.json")
    p.add_argument("--brains", default="brains.json")
    p.add_argument("--chart", default="live_dashboard.html", help="הדף עם החלונות של הבוטים")
    p.add_argument("--once", action="store_true")
    p.add_argument("--status", action="store_true")
    p.add_argument("--reset", action="store_true")
    p.add_argument("--verbose", action="store_true", help="להראות כל מוות ושכפול")
    p.add_argument("--phone", action="store_true", help="לפתוח את הדף גם בטלפון (באותו Wi-Fi)")
    p.add_argument("--port", type=int, default=8000, help="הפורט של הדף בשביל הטלפון")
    args = p.parse_args()

    cfg = load_settings(args.settings)
    if args.reset and os.path.exists(args.state):
        os.remove(args.state)
    s = load_state(args.state, cfg) if os.path.exists(args.state) else new_state(cfg, args.brains)
    if args.status:
        return status(s, cfg, args.chart)

    print(f"הדף עם הבוטים: {os.path.abspath(args.chart)} (לפתוח בדפדפן, הוא מתרענן לבד)")
    if args.phone:
        announce(serve(args.chart, args.port))
    while True:
        try:                                     # קוראים מחדש כל פעם, כדי ששינויים ייכנסו לתוקף
            cfg = load_settings(args.settings)
        except SystemExit as e:
            print(f"{e} - ממשיך עם ההגדרות הקודמות")
        world = s["world"]
        world.out, world.verbose = print, args.verbose
        if time.time() - s.get("net_updated", 0) > 6 * 3600:   # החושים מהאינטרנט: פעם ב-6 שעות
            held = sorted({a for b in world.bots for a in members(b.genome.asset)})  # גם מטבעות שבוטים מחזיקים
            failed = net.update_live(list(dict.fromkeys(cfg.assets + held)))
            s["net_updated"] = time.time()
            save_state(args.state, s)                        # כדי לא להוריד שוב אם הבורסה לא עונה
            if failed:
                print("לא הצלחתי לעדכן עכשיו: " + ", ".join(failed) + ". ממשיך עם הנתונים שיש.")
        try:
            tick(s, cfg)
            save_state(args.state, s)
            write_dashboard(args.chart, TITLE, [("הבוטים", world)], world.cfg, live=True)
        except (OSError, RuntimeError, ValueError) as e:
            print(f"בעיה בחיבור לבורסה, אנסה שוב עוד מעט: {e}")
        if args.once:
            return
        time.sleep(min(10, minutes(cfg.candle)) * 60)


if __name__ == "__main__":
    main()
