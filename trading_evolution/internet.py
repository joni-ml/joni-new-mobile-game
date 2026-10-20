"""
"חושים מהאינטרנט": נתונים מאתרים שהבוטים יכולים ללמוד מהם, בנוסף למחירים.
אלה בעיקר גלאי סכנה: פחד בשוק, פחד בבורסה האמריקאית, כמה אנשים מתעניינים, כמה הרשת בשימוש.

כל מקור הופך ל"סימן" בין -1 ל-1 שאומר: האם המספר הזה גבוה או נמוך במיוחד ביחס לשנה האחרונה?
הבוטים נותנים לכל סימן משקל, בדיוק כמו לשיטות המחיר, והאבולוציה מגלה במה כדאי להאמין.

הכלל הכי חשוב: בוט משתמש רק במספר שכבר פורסם ברגע שהוא מחליט.
לכן לכל מקור יש "lag" - כמה ימים אחורה צריך להסתכל כדי שהמספר כבר היה ידוע.

  python fetch_data.py      # מוריד גם את ההיסטוריה של כל החושים (מגיטהאב)
  live.py מעדכן אותם לבד פעם בכמה שעות מהאתרים עצמם.
"""

import bisect
import csv
import io
import json
import math
import os
import urllib.request
from datetime import date, datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
FOLDER = os.path.join(HERE, "data", "internet")
WINDOW = 365        # משווים כל מספר לשנה שלפניו
MIN_HISTORY = 60    # כמה ימים של היסטוריה צריך לפני שסומכים על ההשוואה
STALE_DAYS = 7      # מספר ישן יותר מזה לא משתמשים בו (בסופי שבוע הבורסה סגורה, אז קצת פער זה בסדר)
GH = "https://raw.githubusercontent.com/"
CM_API = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"


# ---------- הורדה ----------

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (trading-evolution)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode()


def csv_rows(text, date_col, value_col, parse_date=date.fromisoformat):
    rows = []
    for r in csv.DictReader(io.StringIO(text)):
        try:
            rows.append((parse_date(r[date_col].strip()[:10]), float(r[value_col])))
        except (ValueError, KeyError, TypeError):
            continue   # שורה ריקה או חסרה
    return rows


def utc_day(seconds):
    return datetime.fromtimestamp(seconds, timezone.utc).date()


_cm_cache = {}


def coinmetrics_csv(coin):
    """הקובץ היומי של Coin Metrics בגיטהאב (נשמר בזיכרון כדי לא להוריד פעמיים)."""
    if coin not in _cm_cache:
        _cm_cache[coin] = get(GH + f"coinmetrics/data/master/csv/{coin.lower()}.csv")
    return _cm_cache[coin]


def coinmetrics_history(metric, assets):
    return {a: csv_rows(coinmetrics_csv(a), "time", metric) for a in assets}


def coinmetrics_live(metric, assets, days):
    """ה-API החינמי של Coin Metrics (בלי מפתח), בשביל הימים האחרונים."""
    start = (date.today() - timedelta(days=days)).isoformat()
    out = {}
    for a in assets:
        data = json.loads(get(f"{CM_API}?assets={a.lower()}&metrics={metric}&frequency=1d"
                              f"&start_time={start}&page_size=1000"))["data"]
        out[a] = [(date.fromisoformat(x["time"][:10]), float(x[metric])) for x in data if x.get(metric)]
    return out


def fear_greed_live(assets, days):
    data = json.loads(get(f"https://api.alternative.me/fng/?limit={days}&format=json"))["data"]
    return {"ALL": [(utc_day(int(x["timestamp"])), float(x["value"])) for x in data]}


def fred(series):
    """סדרה יומית מ-FRED (אתר הנתונים של הבנק המרכזי האמריקאי), בלי מפתח. ימים בלי מסחר מגיעים ריקים."""
    text = get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}")
    date_col = "observation_date" if text.startswith("observation_date") else "DATE"
    return {"ALL": csv_rows(text, date_col, series)}


def vix_live(assets, days):
    text = get("https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv")
    return {"ALL": csv_rows(text, "DATE", "CLOSE", lambda s: datetime.strptime(s, "%m/%d/%Y").date())}


def wiki_live(assets, days):
    start, end = date.today() - timedelta(days=days), date.today()
    data = json.loads(get("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/"
                          f"all-access/all-agents/Bitcoin/daily/{start:%Y%m%d}00/{end:%Y%m%d}00"))
    return {"ALL": [(datetime.strptime(x["timestamp"][:8], "%Y%m%d").date(), float(x["views"])) for x in data["items"]]}


# ---------- המקורות ----------
# kind: איך הופכים את המספר לסימן (ראה normalize). lag: כמה ימים אחורה כדי שהמספר כבר היה ידוע.
# "ALL" = מספר אחד לכל השוק. אחרת - מספר נפרד לכל מטבע.
SOURCES = {
    "fear_greed": dict(
        title="מדד הפחד והחמדנות של הקריפטו", kind="index", lag=1,
        history=lambda assets: {"ALL": csv_rows(get(GH + "j0shcd/risk-metric/main/data/fear_greed_index.csv"),
                                                "Date", "fear_greed_index")},
        live=fear_greed_live),
    # הבורסה האמריקאית (S&P 500): מחירי סגירה אמיתיים, שלא משתנים אחר כך.
    # (מדד הפחד והחמדנות של CNN נפסל: ההיסטוריה שלו נכתבת מחדש בדיעבד, אז בוט היה לומד ממספרים שאף אחד לא ראה בזמן אמת.)
    "stocks": dict(
        title="הבורסה האמריקאית (S&P 500)", kind="change", lag=1,
        history=lambda assets: fred("SP500"),
        mirror=lambda assets: {"ALL": csv_rows(get(GH + "LEEYOUNGJIN-GIT/fred-macro-review/main/data/macro/obs/SP500.csv"),
                                               "date", "value")},
        live=lambda assets, days: fred("SP500")),
    "vix": dict(
        title="מדד הפחד של וול סטריט (VIX)", kind="level", lag=1,
        history=lambda assets: {"ALL": csv_rows(get(GH + "datasets/finance-vix/main/data/vix-daily.csv"),
                                                "DATE", "CLOSE")},
        mirror=lambda assets: fred("VIXCLS"),
        live=vix_live),
    "attention": dict(
        title="כמה אנשים קוראים על ביטקוין בוויקיפדיה", kind="change", lag=1,
        history=lambda assets: {"ALL": csv_rows(get(GH + "j0shcd/risk-metric/main/data/wikipedia_pageviews_btc.csv"),
                                                "Date", "wikipedia_pageviews")},
        live=wiki_live),
    "activity": dict(
        title="כתובות פעילות ברשת של המטבע", kind="change", lag=1,
        history=lambda assets: coinmetrics_history("AdrActCnt", assets),
        live=lambda assets, days: coinmetrics_live("AdrActCnt", assets, days)),
    "valuation": dict(
        title="כמה המטבע יקר (MVRV)", kind="level", lag=1,
        history=lambda assets: coinmetrics_history("CapMVRVCur", assets),
        live=lambda assets, days: coinmetrics_live("CapMVRVCur", assets, days)),
}


# ---------- שמירה וטעינה ----------

def path(signal, coin):
    return os.path.join(FOLDER, signal, f"{coin}.csv")


def save(signal, coin, rows):
    """rows: [(date, value), ...] -> data/internet/<signal>/<coin>.csv"""
    os.makedirs(os.path.dirname(path(signal, coin)), exist_ok=True)
    with open(path(signal, coin) + ".tmp", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "value"])
        w.writerows((d.isoformat(), v) for d, v in sorted(dict(rows).items()))
    os.replace(path(signal, coin) + ".tmp", path(signal, coin))


def load(signal, coin):
    """מחזיר [(date, value), ...] מהישן לחדש, או רשימה ריקה אם אין קובץ."""
    p = path(signal, coin)
    if not os.path.exists(p):
        return []
    with open(p, newline="") as f:
        return [(date.fromisoformat(r["date"]), float(r["value"])) for r in csv.DictReader(f) if r["value"]]


def first_working(*fetchers):
    """מנסה כמה מקורות לפי הסדר, ומחזיר את הראשון שעובד ומחזיר נתונים."""
    errors = []
    for fetch in fetchers:
        try:
            data = fetch()
            if any(data.values()):
                return data
            errors.append("אין נתונים")
        except Exception as e:
            errors.append(str(e))
    raise RuntimeError(" | ".join(errors))


def download_history(assets):
    """מוריד את כל ההיסטוריה של כל החושים ושומר ב-data/internet (אם האתר הראשי לא עונה - מגיבוי בגיטהאב)."""
    for name, src in SOURCES.items():
        try:
            data = first_working(lambda: src["history"](assets), lambda: src.get("mirror", src["history"])(assets))
            for coin, rows in data.items():
                if rows:
                    save(name, coin, rows)
                    print(f"  {src['title']} ({coin}): {len(rows)} ימים, {rows[0][0]} עד {rows[-1][0]}")
        except Exception as e:
            print(f"  {src['title']}: לא הצלחתי להוריד ({e})")


def update_live(assets, days=40):
    """מעדכן את הימים האחרונים מהאתרים עצמם (ואם אתר לא עונה - מהגיבויים).
    מחזיר רשימה של מקורות שלא הצליחו."""
    failed = []
    for name, src in SOURCES.items():
        try:
            data = first_working(lambda: src["live"](assets, days), lambda: src["history"](assets),
                                 lambda: src.get("mirror", src["history"])(assets))
            for coin, rows in data.items():
                if rows:
                    save(name, coin, load(name, coin) + rows)   # החדשים דורסים את הישנים באותו תאריך
        except Exception:
            failed.append(src["title"])
    return failed


# ---------- מספר -> סימן ----------

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


def extras(assets, times, intraday):
    """לכל מטבע: {שם החוש: (המספרים עצמם, הסימנים)}, מיושרים לזמנים של הנרות.
    חוש שאין לו קובץ למטבע מסוים משתמש במספר של כל השוק ("ALL"), ואם גם זה אין - פשוט לא קיים."""
    out, done = {a: {} for a in assets}, {}
    for name, src in SOURCES.items():
        for a in assets:
            coin = a if os.path.exists(path(name, a)) else "ALL"
            if (name, coin) not in done:      # מספר של כל השוק מחשבים פעם אחת לכל המטבעות
                rows = load(name, coin)
                sig = normalize(rows, src["kind"])
                done[name, coin] = (align(rows, times, src["lag"], intraday),
                                    align(sig, times, src["lag"], intraday)) if rows else None
            if done[name, coin]:
                out[a][name] = done[name, coin]
    return out
