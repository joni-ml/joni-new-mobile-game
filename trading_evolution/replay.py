"""
הקלטה: הבוטים סוחרים יום אחרי יום על מחירי עבר אמיתיים, עם כל השיטות והחושים מהאינטרנט,
והדף replay.html מנגן את זה כמו סרטון (כפתור נגן/עצור, פס זמן ומהירות). עובד גם בטלפון.
ההגדרות נלקחות מ-settings.toml, בדיוק כמו במסחר החי.

  python replay.py                                   # השנה האחרונה שיש לה מחירים
  python replay.py --from 2024-01-01 --to 2025-01-01
  python replay.py --every 7                         # תמונה כל 7 ימים (קובץ קטן יותר)
"""

import argparse
import os
from datetime import datetime, timedelta

import internet as net
from core import Market, World, candle_minutes, load_settings
from dashboard import build, write_replay
from evolution_sim import cut_range, load_data

HERE = os.path.dirname(os.path.abspath(__file__))
SPARK = 120   # כמה נקודות אחרונות לשמור בגרפים הקטנים של כל בוט (כדי שהקובץ לא יהיה ענק)


def shrink(frame):
    for b in frame["bots"]:
        b["spark"] = b["spark"][-SPARK:]
        if b["brain"]:
            b["brain"]["scores"] = b["brain"]["scores"][-SPARK:]
    return frame


def main():
    p = argparse.ArgumentParser(description="הקלטה של הבוטים בפעולה")
    p.add_argument("--settings", default=os.path.join(HERE, "settings.toml"))
    p.add_argument("--data", default="daily", choices=["daily", "hourly", "old"])
    p.add_argument("--from", dest="start", help="מתי להתחיל (ברירת מחדל: שנה לפני המחיר האחרון)")
    p.add_argument("--to", dest="end")
    p.add_argument("--every", type=int, default=4, help="כל כמה נרות לצלם תמונה")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--out", default="replay.html")
    args = p.parse_args()

    cfg = load_settings(args.settings)
    times, prices = load_data(args.data, cfg.assets, args.seed)
    cfg.assets = list(prices)
    start = datetime.fromisoformat(args.start) if args.start else times[-1] - timedelta(days=365)
    t, pr, warm = cut_range(times, prices, start, datetime.fromisoformat(args.end) if args.end else None)
    minutes = candle_minutes(t)
    extras = net.extras(cfg.assets, t, minutes < 1440)
    markets = {a: Market(col, extras.get(a)) for a, col in pr.items()}
    world = World(cfg, minutes, args.seed)
    world.populate()

    frames = []
    for i in range(warm, len(t)):
        world.step(markets, i, t[i])
        if (i - warm) % args.every == 0 or i == len(t) - 1:
            frames.append(shrink(build(f"הבוטים בפעולה · {t[i]:%d/%m/%Y}", [("הבוטים", world)], world.cfg, live=True)))
    write_replay(args.out, "הבוטים בפעולה", frames)
    last = world.history[-1]
    print(f"{len(frames)} תמונות, {t[warm]:%d/%m/%Y} עד {t[-1]:%d/%m/%Y} | "
          f"נשאר בבוטים {last['inside']:.2f} מתוך {last['invested']:.2f} ש\"ח שהושקעו, ולקחת {last['collected']:.2f}")
    print(f"ההקלטה: {os.path.abspath(args.out)} (לפתוח בדפדפן; בטלפון: python phone.py {args.out})")


if __name__ == "__main__":
    main()
