"""
פקודה אחת שעושה הכול, ובסוף יוצר קובץ results.zip לשלוח בחזרה:

  python run_all.py              # הכול (לוקח זמן - אפשר לעזוב את המחשב)
  python run_all.py --quick      # בלי הבדיקה הארוכה על כמה שנים
  python run_all.py --rounds 20  # יותר סבבי אימון

מה זה עושה:
  1. מוריד מחירים (יומי, ולשעה מהשנתיים האחרונות) ואת הגלאים מהאינטרנט
  2. מאמן את הבוטים על כל מה שהיה עד לפני שנה, ובודק אותם על השנה האחרונה (שהם לא ראו)
  3. מקליט אותם בפעולה על השנה האחרונה (replay.html)
  4. אם יש מחירים לשעה: אותו דבר על מחירים לשעה (חצי שנה אחרונה למבחן)
  5. בדיקה הוגנת על כמה שנים (evaluate.py)
  6. אורז הכול ל-results.zip
"""

import argparse
import csv
import os
import subprocess
import sys
import zipfile
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results")


def run(title, args, log=None):
    """מריץ שלב אחד. אם הוא נכשל - ממשיכים לשלב הבא, והשגיאה נשמרת ביומן."""
    print(f"\n=== {title} ===", flush=True)
    cmd = [sys.executable, *args]
    if log:
        with open(os.path.join(OUT, log), "w", encoding="utf-8") as f:
            code = subprocess.call(cmd, cwd=HERE, stdout=f, stderr=subprocess.STDOUT)
        print(f"   נשמר ב-results/{log}" + ("" if code == 0 else f" (הסתיים עם שגיאה {code})"))
    else:
        code = subprocess.call(cmd, cwd=HERE)
    return code == 0


def last_date(kind):
    path = os.path.join(HERE, "data", kind, "BTC.csv")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        rows = list(csv.reader(f))
    return datetime.fromisoformat(rows[-1][0][:19])


def main():
    p = argparse.ArgumentParser(description="מוריד, מאמן, בודק ומקליט - הכול בפקודה אחת")
    p.add_argument("--rounds", type=int, default=10, help="כמה סבבי אימון")
    p.add_argument("--quick", action="store_true", help="בלי הבדיקה הארוכה על כמה שנים")
    p.add_argument("--no-hourly", action="store_true", help="בלי מחירים לשעה")
    args = p.parse_args()
    os.makedirs(OUT, exist_ok=True)

    run("1. מוריד מחירים וגלאים מהאינטרנט", ["fetch_data.py"] + ([] if args.no_hourly else ["--recent"]),
        "fetch_log.txt")
    end = last_date("daily")
    if not end:
        raise SystemExit("לא הצלחתי להוריד מחירים. אפשר לראות למה ב-results/fetch_log.txt")
    split = (end - timedelta(days=365)).strftime("%Y-%m-%d")
    print(f"   יש מחירים עד {end:%d/%m/%Y}. מתאמנים עד {split}, ונבחנים על השנה שאחרי.")

    run("2. אימון ומבחן על השנה האחרונה", ["evolution_sim.py", "--from", "2018-01-01", "--split", split,
                                           "--rounds", str(args.rounds), "--brains", "results/brains.json",
                                           "--chart", "results/dashboard.html"], "train_log.txt")
    run("3. הקלטה של הבוטים המאומנים בפעולה", ["replay.py", "--from", split, "--brains", "results/brains.json",
                                              "--out", "results/replay.html"], "replay_log.txt")
    hour_end = last_date("hourly")
    if hour_end and not args.no_hourly:
        hsplit = (hour_end - timedelta(days=180)).strftime("%Y-%m-%d")
        run("4. אימון ומבחן על מחירים לשעה", ["evolution_sim.py", "--data", "hourly", "--split", hsplit,
                                              "--rounds", "3", "--brains", "results/brains_hourly.json",
                                              "--chart", "results/dashboard_hourly.html"], "train_log_hourly.txt")
    if not args.quick:
        run("5. בדיקה הוגנת על כמה שנים (הכי ארוך)", ["evaluate.py", "--seeds", "2", "--rounds", "4"],
            "evaluate_log.txt")

    zip_path = os.path.join(HERE, "results.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for name in sorted(os.listdir(OUT)):
            z.write(os.path.join(OUT, name), name)
    print(f"\nסיימתי! את הקובץ הזה שולחים בחזרה: {zip_path}")
    print("ואת הבוטים בפעולה רואים ב-results/replay.html (לפתוח בדפדפן).")


if __name__ == "__main__":
    main()
