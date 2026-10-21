"""
בדיקה הוגנת על כמה תקופות: האם הבוטים באמת טובים יותר מ"לקנות ולחכות", או שהיה להם מזל בתקופה אחת?

לכל שנת מבחן: הבוטים מתאמנים על כל מה שהיה לפניה, ואז סוחרים שנה שלמה שהם לא ראו.
כל זה כמה פעמים (עם מזל אחר), ומשווים למה שהיה קורה אם אותו כסף היה נקנה במטבעות ונשאר שם.
ההגדרות נלקחות מ-settings.toml, אז אפשר לשנות הגדרה ולבדוק אם זה באמת עוזר.

  python evaluate.py                          # 6 שנות מבחן, 3 פעמים כל אחת
  python evaluate.py --seeds 5 --rounds 3     # יותר בדיקות (לוקח יותר זמן)
  python evaluate.py --years 2022 2024
"""

import argparse
import os
from datetime import datetime

from core import Bot, load_settings
from dashboard import hold_series
from evolution_sim import cut_range, load_data, simulate

HERE = os.path.dirname(os.path.abspath(__file__))


def run(times, prices, cfg, year, seed, rounds):
    """מתאמן עד תחילת השנה, נבחן על השנה. מחזיר (רווח הבוטים, רווח של לקנות ולחכות) בשקלים."""
    class Args:
        verbose = False
    Args.seed = seed
    start, split, end = datetime(2018, 1, 1), datetime(year, 1, 1), datetime(year + 1, 1, 1)
    t, pr, warm = cut_range(times, prices, start, split)
    best = []
    for _ in range(rounds):   # המוחות לא עוברים בין סבבי אימון, רק מהאחרון אל המבחן (כמו ב-evolution_sim)
        world = simulate(t, pr, warm, cfg, Args, [Bot(0, b.genome, 0) for b in best])
        best = world.best(cfg.max_bots)
    t, pr, warm = cut_range(times, prices, split, end)
    world = simulate(t, pr, warm, cfg, Args, best)
    last = world.history[-1]
    return last["collected"] + last["inside"] - last["invested"], hold_series(world)[-1], last["invested"]


def main():
    p = argparse.ArgumentParser(description="בדיקה של הבוטים על כמה תקופות")
    p.add_argument("--settings", default=os.path.join(HERE, "settings.toml"))
    p.add_argument("--years", type=int, nargs="+", default=[2020, 2021, 2022, 2023, 2024, 2025])
    p.add_argument("--seeds", type=int, default=3, help="כמה פעמים לבדוק כל שנה (עם מזל אחר)")
    p.add_argument("--rounds", type=int, default=2, help="כמה סבבי אימון לפני כל מבחן")
    args = p.parse_args()

    cfg = load_settings(args.settings)
    times, prices = load_data("daily", cfg.assets, 1)
    cfg.assets = list(prices)
    years = [y for y in args.years if datetime(y, 1, 1) > times[0] and datetime(y, 1, 1) < times[-1]]
    print(f"\nשנה  | הבוטים (ממוצע) | לקנות ולחכות | מי ניצח (מתוך {args.seeds})")
    wins = total = 0
    edge = 0.0
    for year in years:
        rows = [run(times, prices, cfg, year, seed, args.rounds) for seed in range(1, args.seeds + 1)]
        bots = sum(r[0] for r in rows) / len(rows)
        hold = sum(r[1] for r in rows) / len(rows)
        beat = sum(r[0] > r[1] for r in rows)
        wins, total = wins + beat, total + len(rows)
        edge += sum((r[0] - r[1]) / r[2] for r in rows)
        print(f"{year} | {bots:+10.2f} ש\"ח | {hold:+10.2f} ש\"ח | הבוטים ניצחו {beat}/{len(rows)}", flush=True)
    if total:
        print(f"\nבסך הכול הבוטים ניצחו את \"לקנות ולחכות\" ב-{wins} מתוך {total} בדיקות, "
              f"ובממוצע ב-{100 * edge / total:+.1f}% מהכסף שהושקע.")
        print("אם זה בערך חצי מהבדיקות - ההבדל הוא כנראה מזל. שינוי שווה לשמור רק אם הוא מנצח ברוב התקופות.")


if __name__ == "__main__":
    main()
