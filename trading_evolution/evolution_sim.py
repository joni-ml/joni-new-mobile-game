"""
אימון ובדיקה של בוטי המסחר על מחירי עבר (כסף מזויף).
ההגדרות (מטבעות, תשלומים, מבחנים, מספר בוטים) נמצאות ב-settings.toml.

  python evolution_sim.py                                   # מחיר יומי, כל התקופה
  python evolution_sim.py --from 2021-01-01                 # רק מ-2021
  python evolution_sim.py --from 2018-01-01 --split 2022-01-01
  python evolution_sim.py --data hourly                     # מחיר לשעה (fetch_data.py --recent)
  python evolution_sim.py --data fake                       # מחירים מדומים

עם --split: הבוטים מתאמנים על התקופה שלפני התאריך, האסטרטגיות הכי טובות נשמרות
ב-brains.json, ואז בודקים אותן על התקופה שאחרי - מחירים שהן לא ראו אף פעם.
זאת הבדיקה האמיתית: להצליח בעבר זה קל, השאלה היא אם זה עובד גם על העתיד.
"""

import argparse
import os
from collections import Counter
from datetime import datetime

from core import (MAX_WINDOW, World, align, candle_minutes, load_brains, load_prices,
                  load_settings, run_history, save_brains, synthetic_prices)
from dashboard import write_dashboard

HERE = os.path.dirname(os.path.abspath(__file__))


def load_data(kind, assets, seed):
    """מחזיר (זמנים, {מטבע: מחירים}) לכל המטבעות שיש להם קובץ מחירים."""
    if kind == "fake":
        return synthetic_prices(60, assets, seed)
    folder = os.path.join(HERE, "data", kind)
    found = {a: load_prices(os.path.join(folder, f"{a}.csv")) for a in assets
             if os.path.exists(os.path.join(folder, f"{a}.csv"))}
    missing = [a for a in assets if a not in found]
    if not found:
        how = {"daily": "", "hourly": " --recent", "old": " --old"}[kind]
        raise SystemExit(f"אין קבצי מחירים ב-{folder}. קודם מריצים: python fetch_data.py{how}")
    if missing:
        print(f"אין מחירים של {', '.join(missing)} - הבוטים יסחרו רק ב-{', '.join(found)}")
    times, prices = align(found)
    first = {a: ts[0] for a, (ts, _) in found.items()}
    late = max(first, key=first.get)
    print(f"יש מחירים לכל המטבעות מ-{times[0]:%d/%m/%Y} (המטבע הכי חדש: {late})")
    return times, prices


def cut_range(times, prices, start=None, end=None):
    """מחזיר את התקופה המבוקשת, ועוד כל מה שלפניה בשביל האינדיקטורים. הבוטים סוחרים רק מ-start."""
    lo = next((i for i, t in enumerate(times) if start is None or t >= start), len(times))
    hi = next((i for i, t in enumerate(times) if end is not None and t >= end), len(times))
    lo = max(lo, min(MAX_WINDOW, hi - 1))   # בלי מספיק היסטוריה לפני, מתחילים קצת יותר מאוחר
    warm = 0   # כל מה שקרה לפני - בשביל האינדיקטורים וזיכרון הדפוסים (הבוטים לא סוחרים בזה)
    return times[warm:hi], {a: p[warm:hi] for a, p in prices.items()}, lo - warm


def simulate(times, prices, warmup, cfg, args, seeds=()):
    world = World(cfg, candle_minutes(times), args.seed, seeds)
    world.out = print if args.verbose else None
    world.verbose = args.verbose
    world.populate()
    run_history(times, prices, world, warmup)
    return world


def summary(title, world, times, prices, warmup):
    last = world.history[-1]
    net = last["collected"] + last["inside"] - last["invested"]
    print(f"\n=== {title} ({times[warmup]:%d/%m/%Y} - {times[-1]:%d/%m/%Y}) ===")
    coins = " ".join(f"{a} {(p[-1] / p[warmup] - 1) * 100:+.0f}%" for a, p in prices.items())
    print(f"המטבעות: {coins}")
    print(f"השקעת {last['invested']:.2f} ש\"ח | לקחת {last['collected']:.2f} | נשאר בבוטים {last['inside']:.2f}")
    print(f"רווח/הפסד נקי: {net:+.2f} ש\"ח ({net / last['invested'] * 100:+.0f}%) | "
          f"מבחנים {world.selections}, מתו {world.deaths}, שוכפלו {world.clones}, "
          f"בחרו לא להשתכפל {world.declined}, נולדו במקומות ריקים {world.refilled}, חיים {len(world.bots)}")
    picks = Counter(b.genome.asset for b in world.bots)
    print("במה הבוטים בחרו לסחור: " + ", ".join(f"{a} ({n})" for a, n in picks.most_common()))
    return net


def show_best(world, k=3):
    print("האסטרטגיות הכי מצליחות:")
    for b in world.best(k):
        print(f"  בוט #{b.id} ({b.genome.asset}, דור {b.generation}): {b.genome.describe(world.cfg.signals)}")
        print(f"      {b.genome.clone_rule(world.cfg.start_money)}")


def main():
    p = argparse.ArgumentParser(description="אימון ובדיקה של בוטי מסחר על מחירי עבר")
    p.add_argument("--settings", default=os.path.join(HERE, "settings.toml"))
    p.add_argument("--data", default="daily", choices=["daily", "hourly", "old", "fake"],
                   help="איזה מחירים: יומי, לשעה (שנתיים אחרונות), ביטקוין לשעה 2011-2017, או מדומים")
    p.add_argument("--from", dest="start", help="תאריך התחלה, למשל 2018-01-01")
    p.add_argument("--to", dest="end", help="תאריך סיום")
    p.add_argument("--split", help="מתאמנים לפני התאריך הזה, נבחנים אחריו")
    p.add_argument("--rounds", type=int, default=3, help="כמה פעמים לעבור על תקופת האימון")
    p.add_argument("--brains", default="brains.json", help="איפה לשמור/לטעון אסטרטגיות מאומנות")
    p.add_argument("--use-brains", action="store_true", help="להתחיל מהאסטרטגיות השמורות")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--verbose", action="store_true", help="להראות כל מוות ושכפול")
    p.add_argument("--chart", default="dashboard.html", help="איפה לשמור את דף הגרפים")
    args = p.parse_args()

    cfg = load_settings(args.settings)
    times, prices = load_data(args.data, cfg.assets, args.seed)
    cfg.assets = list(prices)
    date = lambda s: datetime.fromisoformat(s) if s else None

    if not args.split:
        seeds = load_brains(args.brains) if args.use_brains else ()
        t, pr, warm = cut_range(times, prices, date(args.start), date(args.end))
        world = simulate(t, pr, warm, cfg, args, seeds)
        summary("תוצאות", world, t, pr, warm)
        show_best(world)
        save(args.chart, "בוטי מסחר: תוצאות", [("הבוטים", world)], cfg)
        return

    # שלב 1: אימון. כל סבב מתחיל מהאסטרטגיות הכי טובות של הסבב הקודם.
    t, pr, warm = cut_range(times, prices, date(args.start), date(args.split))
    seeds = ()
    for r in range(1, args.rounds + 1):
        world = simulate(t, pr, warm, cfg, args, seeds)
        summary(f"אימון, סבב {r}", world, t, pr, warm)
        seeds = [b.genome for b in world.best(cfg.max_bots)]
    save_brains(args.brains, seeds)
    show_best(world)
    print(f"\nנשמרו {len(seeds)} אסטרטגיות ב-{os.path.abspath(args.brains)}")

    # שלב 2: מבחן על תקופה שהבוטים לא ראו. משווים לבוטים אקראיים שלא התאמנו.
    t, pr, warm = cut_range(times, prices, date(args.split), date(args.end))
    trained_world = simulate(t, pr, warm, cfg, args, seeds)
    fresh_world = simulate(t, pr, warm, cfg, args)
    trained = summary("מבחן: בוטים מאומנים", trained_world, t, pr, warm)
    fresh = summary("מבחן: בוטים אקראיים (בלי אימון)", fresh_world, t, pr, warm)
    verdict = "האימון עזר" if trained > fresh else "האימון לא עזר"
    print(f"\n{verdict}: מאומנים {trained:+.2f} ש\"ח מול אקראיים {fresh:+.2f} ש\"ח")
    save(args.chart, "בוטי מסחר: מבחן על תקופה שהבוטים לא ראו",
         [("בוטים מאומנים", trained_world), ("בוטים בלי אימון", fresh_world)], cfg)


def save(path, title, runs, cfg):
    write_dashboard(path, title, runs, cfg)
    print(f"\nהדף עם הגרפים והחלונות של הבוטים: {os.path.abspath(path)} (לפתוח בדפדפן)")


if __name__ == "__main__":
    main()
