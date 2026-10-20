"""
אימון ובדיקה של בוטי המסחר על מחירי עבר (כסף מזויף).

  python3 evolution_sim.py                                   # מחירים מדומים
  python3 evolution_sim.py --data data/btc_daily.csv --from 2018-01-01
  python3 evolution_sim.py --data data/btc_daily.csv --from 2016-01-01 --split 2022-01-01

עם --split: הבוטים מתאמנים על התקופה שלפני התאריך, האסטרטגיות הכי טובות נשמרות
ב-brains.json, ואז בודקים אותן על התקופה שאחרי - מחירים שהן לא ראו אף פעם.
זאת הבדיקה האמיתית: להצליח בעבר זה קל, השאלה היא אם זה עובד גם על העתיד.
"""

import argparse
import os
from datetime import datetime

from core import (MAX_WINDOW, World, load_brains, load_prices, run_history,
                  save_brains, synthetic_prices)


def cut_range(times, prices, start=None, end=None):
    """מחזיר רק את התקופה המבוקשת, ועוד MAX_WINDOW נרות לפניה לחישוב אינדיקטורים."""
    lo = next((i for i, t in enumerate(times) if start is None or t >= start), len(times))
    hi = next((i for i, t in enumerate(times) if end is not None and t >= end), len(times))
    warm = max(0, lo - MAX_WINDOW)
    return times[warm:hi], prices[warm:hi], lo - warm


def simulate(times, prices, warmup, args, seeds=(), log=None):
    world = World(args.cut, args.seed, seeds)
    world.populate(args.bots)
    run_history(times, prices, world, warmup, log)
    return world


def summary(title, world, times, prices, warmup):
    price = prices[-1]
    inside = sum(b.value(price) for b in world.bots)
    net = world.owner_profit + inside - world.invested
    hold = (price / prices[warmup] - 1) * 100
    print(f"\n=== {title} ({times[warmup]:%d/%m/%Y} - {times[-1]:%d/%m/%Y}, {world.day} ימים) ===")
    print(f"ביטקוין עשה {hold:+.0f}% | השקעת {world.invested:.2f} ש\"ח | לקחת {world.owner_profit:.2f} | "
          f"נשאר בבוטים {inside:.2f}")
    print(f"רווח/הפסד נקי: {net:+.2f} ש\"ח ({net / world.invested * 100:+.0f}%) | "
          f"מתו {world.deaths}, שוכפלו {world.clones}, חיים {len(world.bots)}, "
          f"דור ממוצע {sum(b.generation for b in world.bots) / max(len(world.bots), 1):.1f}")
    return net


def show_best(world, k=3):
    print("האסטרטגיות הכי מצליחות:")
    for b in world.best(k):
        print(f"  בוט #{b.id} (דור {b.generation}): {b.genome.describe()}")


def main():
    p = argparse.ArgumentParser(description="אימון ובדיקה של בוטי מסחר על מחירי עבר")
    p.add_argument("--data", help="קובץ מחירים (time,close). בלי זה - מחירים מדומים")
    p.add_argument("--from", dest="start", help="תאריך התחלה, למשל 2018-01-01")
    p.add_argument("--to", dest="end", help="תאריך סיום")
    p.add_argument("--split", help="מתאמנים לפני התאריך הזה, נבחנים אחריו")
    p.add_argument("--rounds", type=int, default=3, help="כמה פעמים לעבור על תקופת האימון")
    p.add_argument("--brains", default="brains.json", help="איפה לשמור/לטעון אסטרטגיות מאומנות")
    p.add_argument("--use-brains", action="store_true", help="להתחיל מהאסטרטגיות השמורות")
    p.add_argument("--days", type=int, default=60, help="אורך הסימולציה במחירים מדומים")
    p.add_argument("--bots", type=int, default=10)
    p.add_argument("--cut", type=float, default=0.01, help="כמה הבעלים לוקח כל יום (0.01 = 1%%)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--verbose", action="store_true", help="להראות כל מוות ושכפול")
    args = p.parse_args()

    times, prices = load_prices(args.data) if args.data else synthetic_prices(args.days, args.seed)
    date = lambda s: datetime.fromisoformat(s) if s else None
    log = print if args.verbose else None

    if not args.split:
        seeds = load_brains(args.brains) if args.use_brains else ()
        t, pr, warm = cut_range(times, prices, date(args.start), date(args.end))
        world = simulate(t, pr, warm, args, seeds, log)
        summary("תוצאות", world, t, pr, warm)
        show_best(world)
        return

    # שלב 1: אימון. כל סבב מתחיל מהאסטרטגיות הכי טובות של הסבב הקודם.
    t, pr, warm = cut_range(times, prices, date(args.start), date(args.split))
    seeds = ()
    for r in range(1, args.rounds + 1):
        world = simulate(t, pr, warm, args, seeds, log)
        summary(f"אימון, סבב {r}", world, t, pr, warm)
        seeds = [b.genome for b in world.best(args.bots)]
    save_brains(args.brains, seeds)
    show_best(world)
    print(f"\nנשמרו {len(seeds)} אסטרטגיות ב-{os.path.abspath(args.brains)}")

    # שלב 2: מבחן על תקופה שהבוטים לא ראו. משווים לבוטים אקראיים שלא התאמנו.
    t, pr, warm = cut_range(times, prices, date(args.split), date(args.end))
    trained = summary("מבחן: בוטים מאומנים", simulate(t, pr, warm, args, seeds, log), t, pr, warm)
    fresh = summary("מבחן: בוטים אקראיים (בלי אימון)", simulate(t, pr, warm, args), t, pr, warm)
    verdict = "האימון עזר" if trained > fresh else "האימון לא עזר"
    print(f"\n{verdict}: מאומנים {trained:+.2f} ש\"ח מול אקראיים {fresh:+.2f} ש\"ח")


if __name__ == "__main__":
    main()
