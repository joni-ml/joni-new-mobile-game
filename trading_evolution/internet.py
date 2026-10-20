"""
"חושים מהאינטרנט": נתונים מאתרים שהבוטים יכולים ללמוד מהם, בנוסף למחירים.

כל מקור הופך ל"סימן" בין -1 ל-1 שאומר: האם המספר הזה גבוה או נמוך במיוחד ביחס לשנה האחרונה?
הבוטים נותנים לכל סימן משקל, בדיוק כמו לשיטות המחיר, והאבולוציה מגלה במה כדאי להאמין.

הכלל הכי חשוב: בוט משתמש רק במספר שכבר פורסם ברגע שהוא מחליט.
לכן לכל מקור יש "lag" - כמה ימים אחורה צריך להסתכל כדי שהמספר כבר היה ידוע.
"""

import bisect
import csv
import math
import os
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
FOLDER = os.path.join(HERE, "data", "internet")
WINDOW = 365        # משווים כל מספר לשנה שלפניו
MIN_HISTORY = 60    # כמה ימים של היסטוריה צריך לפני שסומכים על ההשוואה
STALE_DAYS = 7      # מספר ישן יותר מזה לא משתמשים בו


def path(signal, coin):
    return os.path.join(FOLDER, signal, f"{coin}.csv")


def save(signal, coin, rows):
    """rows: [(date, value), ...] -> data/internet/<signal>/<coin>.csv"""
    os.makedirs(os.path.dirname(path(signal, coin)), exist_ok=True)
    with open(path(signal, coin), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "value"])
        w.writerows((d.isoformat(), v) for d, v in sorted(rows))


def load(signal, coin):
    """מחזיר [(date, value), ...] מהישן לחדש, או רשימה ריקה אם אין קובץ."""
    p = path(signal, coin)
    if not os.path.exists(p):
        return []
    with open(p, newline="") as f:
        return [(date.fromisoformat(r["date"]), float(r["value"])) for r in csv.DictReader(f) if r["value"]]


def normalize(rows, kind):
    """הופך סדרה יומית לסימן בין -1 ל-1, רק לפי מה שהיה ידוע עד אותו יום.
    kind:
      "level"  - האם המספר עצמו גבוה או נמוך ביחס לשנה האחרונה
      "change" - האם המספר עלה או ירד בחודש האחרון יותר מהרגיל
      "index"  - מספר שכבר בין 0 ל-100 (למשל מדד הפחד והחמדנות): 0 = -1, 50 = 0, 100 = 1"""
    if kind == "index":
        return [(d, max(-1.0, min(1.0, (v - 50) / 50))) for d, v in rows]
    xs = [v for _, v in rows]
    if kind == "change":
        xs = [math.log(v / xs[i - 30]) if i >= 30 and v > 0 and xs[i - 30] > 0 else None for i, v in enumerate(xs)]
    out, s1, s2, window = [], 0.0, 0.0, []
    for (d, _), x in zip(rows, xs):
        if x is None:
            out.append((d, None))
            continue
        z = None
        if len(window) >= MIN_HISTORY:
            mean = s1 / len(window)
            std = math.sqrt(max(s2 / len(window) - mean * mean, 1e-18))
            z = max(-1.0, min(1.0, (x - mean) / std / 2))
        out.append((d, z))
        window.append(x)
        s1, s2 = s1 + x, s2 + x * x
        if len(window) > WINDOW:
            old = window.pop(0)
            s1, s2 = s1 - old, s2 - old * old
    return out


def align(rows, times, lag, intraday):
    """מתאים סדרה יומית לרשימת זמנים של נרות. לכל נר לוקחים את הערך האחרון שכבר היה ידוע:
    של היום שלפני lag ימים. בנרות של פחות מיום תמיד מסתכלים לפחות יום אחורה,
    כי ערך של יום שלם ידוע רק כשהיום נגמר."""
    lag = max(lag, 1) if intraday else lag
    days = [d for d, _ in rows]
    out = []
    for t in times:
        target = t.date() - timedelta(days=lag)
        k = bisect.bisect_right(days, target) - 1
        ok = k >= 0 and (target - days[k]).days <= STALE_DAYS and rows[k][1] is not None
        out.append(rows[k][1] if ok else None)
    return out
