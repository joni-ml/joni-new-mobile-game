"""
הלב של המערכת: הגדרות, נתוני שוק, אינדיקטורים, הבוטים והאבולוציה.

את הקובץ הזה לא מריצים ישירות. משתמשים בו:
  evolution_sim.py - אימון ובדיקה על מחירי עבר
  live.py          - מסחר חי על נייר עם מחירים אמיתיים מהבורסה
"""

import copy
import csv
import json
import math
import random
from collections import deque

import internet
from dataclasses import asdict, dataclass, field, fields, replace
from datetime import datetime, timedelta

FEE = 0.0015            # כל קנייה/מכירה עולה 0.15%: עמלה של 0.1% + "החלקה" (המחיר זז קצת עד שהעסקה מתבצעת)
DEATH_LINE = 0.05       # מתחת לזה הבוט "מת"
MAX_WINDOW = 200        # הממוצע הנע הכי ארוך שבוט יכול להשתמש בו
IMMIGRANT_RATE = 0.1    # חלק מהשכפולים מקבלים אסטרטגיה חדשה לגמרי, כדי להמשיך לחפש רעיונות
MIX_RATE = 0.25         # חלק מהשכפולים לוקחים גם תכונות מבוט טוב אחר
DROP_PENALTY = 0.5      # judge = "steady": כמה מענישים בוט על כל נפילה בדרך (0.5 = נפילה של 10% עולה 5%)
MAX_SHARE = 1.0         # גיוון: איזה חלק מהבוטים לכל היותר יכול להיות באותו מטבע (1 = בלי הגבלה)
SWITCH_RATE = 0.1       # הסיכוי ששכפול יעבור לסחור במטבע אחר
BASKET_RATE = 0.3       # הסיכוי שבוט חדש (או שכפול שעובר מטבע) יסחור בסל של 2-3 מטבעות במקום במטבע אחד
CHART_POINTS = 2000     # כמה נקודות לשמור לגרף של הבעלים
BOT_POINTS = 300        # כמה נקודות לשמור לגרף של כל בוט
EVENTS = 30             # כמה אירועים אחרונים לזכור (מוות, שכפול, מבחן)
PATTERN_LEN = 5         # כמה נרות אחרונים יוצרים "דפוס"
PATTERN_AHEAD = 5       # כמה נרות קדימה בודקים מה קרה אחרי כל דפוס
PATTERN_MIN = 5         # כמה פעמים צריך לראות דפוס בעבר כדי לסמוך עליו
SHORTS = False          # האם מותר לבוטים להמר נגד (מכירה בחסר) כשהם בורחים מסכנה
TOP_UP = True           # במצב "להחזיק": להשקיע גם כסף שנשאר בצד בזמן שמחזיקים
CLEAR = 0.1             # במצב "להחזיק": כמה הציון צריך לעלות מעל קו הסכנה כדי לקנות שוב
TEACH = 0.0             # הכי טוב מלמד את השאר: כמה מהמוח והנוסחה שלהם זז לכיוון שלו בכל מבחן
STUDY = False           # החכמים (הרבע העליון) לומדים שוב על העבר הקרוב אחרי כל מבחן
HIDDEN = 8              # כמה "תאי עצב" יש במוח של כל בוט
SCHOOL = 365            # כמה נרות מהעבר בוט חדש לומד ("בית ספר") לפני שהוא מתחיל לסחור
ACC_POINTS = 60         # כמה נקודות לשמור לגרף "כמה המוח צודק לאורך הזמן"


# ---------- הגדרות ----------

@dataclass
class Settings:
    assets: list = field(default_factory=lambda: ["BTC", "ETH", "XRP", "DOGE", "LTC", "ADA", "LINK"])
    start_bots: int = 10
    max_bots: int = 20
    start_money: float = 5.0
    pay_every: str = "1d"
    pay_percent: float = 0.1
    select_every: str = "7d"
    kill_percent: float = 50.0
    losers_money: str = "me"
    candle: str = "1h"
    signals: list = field(default_factory=lambda: list(SIGNALS))
    refill: bool = True
    goal: str = "hold"
    judge: str = "beat_hold"
    baskets: bool = False
    patience: str = "3d"
    brain: str = "learning"


def load_settings(path):
    try:
        import tomllib
    except ImportError:
        raise SystemExit("צריך Python 3.11 ומעלה. אפשר להוריד מ-python.org")
    try:
        with open(path, "rb") as f:
            raw = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise SystemExit(f"יש טעות בכתיבה של {path}: {e}")
    unknown = set(raw) - {f.name for f in fields(Settings)}
    if unknown:
        raise SystemExit(f"הגדרה לא מוכרת ב-{path}: {', '.join(sorted(unknown))}")
    s = Settings(**raw)
    s.assets = list(dict.fromkeys(a.upper() for a in s.assets))
    s.max_bots = max(1, s.max_bots)
    s.start_bots = max(1, min(s.start_bots, s.max_bots))
    s.pay_percent = min(max(s.pay_percent, 0.0), 100.0)
    s.kill_percent = min(max(s.kill_percent, 0.0), 95.0)
    for t in (s.pay_every, s.select_every, s.patience):
        minutes(t)                      # בודק שהזמנים כתובים נכון
    if minutes(s.candle) not in (1, 5, 15, 60):
        raise SystemExit(f"candle יכול להיות רק 1m, 5m, 15m או 1h (כתוב {s.candle!r})")
    if not s.assets:
        raise SystemExit("צריך לפחות מטבע אחד ב-assets")
    bad = [x for x in s.signals if x not in SIGNALS]
    if bad or not s.signals:
        raise SystemExit(f"שיטה לא מוכרת ב-signals: {', '.join(bad) or 'הרשימה ריקה'}. "
                         f"אפשר: {', '.join(SIGNALS)}")
    if s.brain not in ("learning", "simple"):
        raise SystemExit(f"brain יכול להיות רק \"learning\" או \"simple\" (כתוב {s.brain!r})")
    if s.judge not in ("beat_hold", "steady", "money"):
        raise SystemExit(f"judge יכול להיות רק \"beat_hold\", \"steady\" או \"money\" (כתוב {s.judge!r})")
    if s.goal not in ("hold", "trade"):
        raise SystemExit(f"goal יכול להיות רק \"hold\" או \"trade\" (כתוב {s.goal!r})")
    if not isinstance(s.baskets, bool):
        raise SystemExit(f"baskets יכול להיות רק true או false (כתוב {s.baskets!r})")
    if not isinstance(s.refill, bool):
        raise SystemExit(f"refill יכול להיות רק true או false (כתוב {s.refill!r})")
    if s.losers_money not in ("me", "winners"):
        raise SystemExit(f"losers_money יכול להיות רק \"me\" או \"winners\" (כתוב {s.losers_money!r})")
    return s


def minutes(text):
    """'30m' / '6h' / '7d' / '2w' -> מספר דקות."""
    units = {"m": 1, "h": 60, "d": 1440, "w": 10080}
    t = str(text).strip().lower()
    try:
        return max(1, round(float(t[:-1]) * units[t[-1]]))
    except (KeyError, ValueError, IndexError):
        raise SystemExit(f"זמן לא מובן: {text!r} (כותבים למשל 30m, 6h, 7d)")


def every(text, candle_minutes):
    """כל כמה נרות קורה משהו שצריך לקרות כל text."""
    return max(1, round(minutes(text) / candle_minutes))


def human(mins):
    if mins < 60:
        return f"{mins:.0f} דקות"
    if mins < 1440:
        return f"{mins / 60:.0f} שעות" if mins >= 120 else "שעה"
    return f"{mins / 1440:.0f} ימים" if mins >= 2880 else "יום"


# ---------- נתוני שוק ----------

def load_prices(path):
    """קורא קובץ CSV עם עמודות time,close. מחזיר (זמנים, מחירים)."""
    times, prices = [], []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            times.append(datetime.fromisoformat(row["time"]))
            prices.append(float(row["close"]))
    return times, prices


def align(series):
    """מיישר כמה מטבעות לאותם זמנים: {מטבע: (זמנים, מחירים)} -> (זמנים, {מטבע: מחירים}).
    מתחילים מהרגע שיש מחיר לכולם, ושעה חסרה מקבלת את המחיר הקודם."""
    start = max(ts[0] for ts, _ in series.values())
    times = sorted({t for ts, _ in series.values() for t in ts if t >= start})
    out = {}
    for asset, (ts, ps) in series.items():
        known = dict(zip(ts, ps))
        last = next(p for t, p in zip(reversed(ts), reversed(ps)) if t <= start)
        out[asset] = [last := known.get(t, last) for t in times]
    return times, out


def synthetic_prices(days, assets, seed):
    """מחירים מדומים (נר לשעה) לכל מטבע, למקרה שאין קבצי מחירים אמיתיים."""
    rng = random.Random(seed)
    start = datetime(2025, 1, 1)
    times = [start + timedelta(hours=h) for h in range(days * 24)]
    prices = {}
    for asset in assets:
        price, regime, col = rng.uniform(1, 1000), 0.0, []
        for _ in times:
            if rng.random() < 0.01:             # מדי פעם השוק משנה "מצב רוח"
                regime = rng.gauss(0, 0.0002)
            price *= math.exp(regime + rng.gauss(0, 0.04 / math.sqrt(24)))
            col.append(price)
        prices[asset] = col
    return times, prices


def candle_minutes(times):
    """כמה דקות יש בכל נר (לפי ההפרש הנפוץ בין זמנים)."""
    gaps = sorted((b - a).total_seconds() / 60 for a, b in zip(times, times[1:]))
    return max(1, round(gaps[len(gaps) // 2])) if gaps else 60


def rsi_series(prices, n=14):
    """RSI: בין 0 ל-100. נמוך = המחיר ירד הרבה לאחרונה, גבוה = עלה הרבה."""
    out = [50.0] * len(prices)
    gain = loss = 0.0
    for i in range(1, len(prices)):
        d = prices[i] - prices[i - 1]
        if i <= n:
            gain += max(d, 0) / n
            loss += max(-d, 0) / n
        else:
            gain = (gain * (n - 1) + max(d, 0)) / n
            loss = (loss * (n - 1) + max(-d, 0)) / n
        if i >= n:
            out[i] = 100.0 if loss == 0 else 100 - 100 / (1 + gain / loss)
    return out


def ema_series(xs, n):
    """ממוצע נע "מעריכי": נותן יותר משקל למחירים האחרונים."""
    k, e, out = 2 / (n + 1), xs[0], []
    for x in xs:
        e += k * (x - e)
        out.append(e)
    return out


def rolling_extremes(xs, n):
    """המחיר הכי גבוה והכי נמוך ב-n הנרות שלפני כל נר (בלי הנר עצמו)."""
    hi, lo = [xs[0]] * len(xs), [xs[0]] * len(xs)
    qh, ql = deque(), deque()
    for i in range(1, len(xs)):
        j = i - 1
        while qh and xs[qh[-1]] <= xs[j]:
            qh.pop()
        while ql and xs[ql[-1]] >= xs[j]:
            ql.pop()
        qh.append(j)
        ql.append(j)
        while qh[0] < i - n:
            qh.popleft()
        while ql[0] < i - n:
            ql.popleft()
        hi[i], lo[i] = xs[qh[0]], xs[ql[0]]
    return hi, lo


def rolling_std(xs, n):
    """כמה הערכים "קופצים" (סטיית תקן) ב-n האחרונים."""
    s1 = s2 = 0.0
    out = []
    for i, x in enumerate(xs):
        s1 += x
        s2 += x * x
        if i >= n:
            s1 -= xs[i - n]
            s2 -= xs[i - n] ** 2
        k = min(i + 1, n)
        out.append(math.sqrt(max(s2 / k - (s1 / k) ** 2, 0.0)))
    return out


def pattern_memory(prices, rets, vol):
    """זיכרון דפוסים: מה קרה בעבר אחרי שהמחיר זז באותה צורה.
    כל נר מסומן כעלייה, ירידה או "בערך אותו דבר" (לפי כמה המחיר זז בדרך כלל),
    ו-PATTERN_LEN הנרות האחרונים יוצרים דפוס, למשל עלייה-עלייה-ירידה-אותו דבר-עלייה.
    לכל נר מחזירים (הדפוס, כמה פעמים ראינו אותו קודם, כמה המחיר זז בממוצע ב-PATTERN_AHEAD הנרות שאחריו).
    משתמשים רק במה שכבר קרה עד אותו נר - בלי להציץ לעתיד."""
    n = len(prices)
    codes = [None] * n
    for i in range(PATTERN_LEN, n):
        half, code = vol[i] / 2, 0
        for r in rets[i - PATTERN_LEN + 1:i + 1]:
            code = code * 3 + (2 if r > half else 0 if r < -half else 1)
        codes[i] = code
    seen, out = {}, [(None, 0, 0.0)] * n
    for i in range(n):
        j = i - PATTERN_AHEAD
        if j >= 0 and codes[j] is not None:     # עכשיו כבר ידוע מה קרה אחרי הדפוס שנגמר בנר j
            total, count = seen.get(codes[j], (0.0, 0))
            seen[codes[j]] = (total + prices[i] / prices[j] - 1, count + 1)
        if codes[i] is not None:
            total, count = seen.get(codes[i], (0.0, 0))
            out[i] = (codes[i], count, total / count if count else 0.0)
    return out


class Market:
    """מחירים של מטבע אחד + אינדיקטורים שמחושבים פעם אחת מראש, כדי שהכול ירוץ מהר."""

    def __init__(self, prices, extras=None):
        self.p = prices
        self.extras = extras or {}   # חושים מהאינטרנט: {שם: (המספרים, הסימנים)}, מיושרים לנרות
        self.cum, self.cum2 = [0.0], [0.0]
        for x in prices:
            self.cum.append(self.cum[-1] + x)
            self.cum2.append(self.cum2[-1] + x * x)
        self.rsi = rsi_series(prices)
        self.macd = [a - b for a, b in zip(ema_series(prices, 12), ema_series(prices, 26))]
        self.macd_signal = ema_series(self.macd, 9)
        self.hi20, self.lo20 = rolling_extremes(prices, 20)
        self.hi55, self.lo55 = rolling_extremes(prices, 55)
        rets = [0.0] + [b / a - 1 for a, b in zip(prices, prices[1:])]
        self.vol14, self.vol50, self.vol100 = (rolling_std(rets, n) for n in (14, 50, 100))
        self.pattern = pattern_memory(prices, rets, self.vol50)

    def ma(self, i, n):
        """ממוצע של n המחירים האחרונים, עד נר i כולל."""
        return (self.cum[i + 1] - self.cum[i + 1 - n]) / n

    def std(self, i, n):
        """כמה המחיר קופץ סביב הממוצע של n הנרות האחרונים (סטיית תקן)."""
        mean = self.ma(i, n)
        return math.sqrt(max((self.cum2[i + 1] - self.cum2[i + 1 - n]) / n - mean * mean, 0.0))


# ---------- האסטרטגיה ("הגנום") ----------

# כל בוט מסתכל על כמה סימנים (שיטות מסחר מוכרות), ומחליט כמה משקל לתת לכל אחד (משקל שלילי = ההפך).
NET_SIGNALS = tuple(internet.SOURCES)                        # חושים מהאינטרנט (גלאי סכנה)
SIGNALS = ("trend", "dip", "momentum", "stretch",          # 4 השיטות הראשונות
           "macd", "bollinger", "channel", "breakout",     # שיטות מוכרות מהאינטרנט
           "calm", "pattern") + NET_SIGNALS                # מצב רוח השוק + זיכרון דפוסים + חושים מהאינטרנט
SIGNAL_WORDS = {
    "trend": ("עוקב אחרי המגמה", "הולך נגד המגמה"),
    "dip": ("קונה אחרי ירידות", "קונה כשהשוק חם"),
    "momentum": ("רודף אחרי עליות", "קונה אחרי נפילות"),
    "stretch": ("קונה כשהמחיר מעל הממוצע", "קונה כשהמחיר מתחת לממוצע"),
    "macd": ("קונה כש-MACD מתחזק", "קונה כש-MACD נחלש"),
    "bollinger": ("קונה בחלק העליון של רצועות בולינגר", "קונה בחלק התחתון של רצועות בולינגר"),
    "channel": ("קונה ליד השיא של 20 נרות", "קונה ליד השפל של 20 נרות"),
    "breakout": ("קונה בפריצה של שיא 55 נרות", "קונה ליד השפל של 55 נרות"),
    "calm": ("קונה כשהשוק רגוע", "קונה כשהשוק סוער"),
    "pattern": ("סומך על דפוסים מהעבר", "הולך נגד הדפוסים מהעבר"),
    "fear_greed": ("קונה כשיש חמדנות בקריפטו", "קונה כשיש פחד בקריפטו"),
    "stocks": ("קונה כשהבורסה האמריקאית עולה", "קונה כשהבורסה האמריקאית נופלת"),
    "vix": ("קונה כשוול סטריט מפחדת", "בורח כשוול סטריט מפחדת"),
    "attention": ("קונה כשיותר אנשים מתעניינים בביטקוין", "קונה כשפחות אנשים מתעניינים"),
    "activity": ("קונה כשהרשת של המטבע גדלה", "קונה כשהרשת של המטבע מתכווצת"),
    "valuation": ("קונה כשהמטבע יקר", "קונה כשהמטבע זול"),
    "stablecoins": ("קונה כשנכנס הרבה כסף חדש לקריפטו", "קונה כשנכנס מעט כסף לקריפטו"),
}


def clamp(x, lo=-1.0, hi=1.0):
    return min(hi, max(lo, x))


@dataclass
class Genome:
    asset: str           # באיזה מטבע הבוט סוחר
    fast: int            # ממוצע נע קצר (בנרות)
    slow: int            # ממוצע נע ארוך
    mom: int             # כמה נרות אחורה בודקים "תנופה"
    weights: list        # משקל לכל סימן, בין -1 ל-1
    buy_at: float        # קונה כשהציון גבוה מזה
    sell_at: float       # מוכר כשהציון נמוך מזה
    stop_loss: float     # מוכר אם ההפסד מהקנייה גדול מזה
    take_profit: float   # מוכר אם הרווח מהקנייה גדול מזה
    bet: float           # איזה חלק מהמזומן להשקיע בכל קנייה
    # ההחלטה אם להשתכפל אחרי שעבר מבחן. גם היא עוברת בתורשה ומשתנה לאט לאט:
    clone_min_return: float = 0.0   # משתכפל רק אם הרוויח לפחות כך מאז המבחן הקודם (0.05 = 5%)
    clone_min_money: float = 0.2    # ורק אם לכל חצי יישאר לפחות כך (כחלק מכסף ההתחלה)
    cooldown: int = 5               # במצב "להחזיק": כמה נרות לחכות אחרי בריחה לפני שקונים שוב
    # המוח הלומד (גם אלה עוברים בתורשה ומשתנים):
    lr: float = 0.03                # קצב למידה: כמה המוח משנה את עצמו אחרי כל טעות
    horizon: int = 7                # כמה נרות קדימה המוח מנסה לנחש
    listen: float = 0.5             # כמה הבוט מקשיב למוח: 0 = רק לנוסחה שירש, 1 = רק למוח
    keep: float = 0.0               # ביטוח (במצב "להחזיק"): איזה חלק מהמטבעות נשאר גם כשבורחים מסכנה
    short: float = 0.0              # הימור נגד (במצב "להחזיק"): כשבורח מסכנה, מוכר בחסר חלק כזה מהכסף (0 = לא)

    def __post_init__(self):
        # בוט מגרסה ישנה (עם פחות שיטות) מקבל משקל 0 לשיטות החדשות, אז הוא ממשיך להתנהג כמו קודם
        self.weights = list(self.weights) + [0.0] * (len(SIGNALS) - len(self.weights))

    @staticmethod
    def random(rng, assets, goal="trade", baskets=False):
        fast = rng.randint(2, 30)
        hold = goal == "hold"   # מחזיקים לטווח ארוך: בורחים רק מסכנה אמיתית, לא מכל ירידה קטנה
        return Genome(pick_asset(rng, assets, baskets), fast, fast + rng.randint(5, 120), rng.randint(2, 60),
                      [rng.uniform(-1, 1) for _ in SIGNALS],
                      rng.uniform(0.05, 0.6), rng.uniform(-0.7, -0.2) if hold else rng.uniform(-0.6, 0.0),
                      rng.uniform(0.1, 0.4) if hold else rng.uniform(0.02, 0.25),
                      rng.uniform(0.03, 0.5), rng.uniform(0.5, 1.0) if hold else rng.uniform(0.2, 1.0),
                      rng.uniform(-0.2, 0.2), rng.uniform(0.0, 0.6), rng.randint(1, 20),
                      math.exp(rng.uniform(math.log(0.005), math.log(0.1))), rng.randint(3, 20), rng.uniform(0, 1),
                      rng.uniform(0, 0.5) if hold else 0.0,
                      rng.uniform(0, 0.5) if hold and SHORTS and rng.random() < 0.5 else 0.0).fix()

    def fix(self):
        self.fast = int(clamp(self.fast, 2, 50))
        self.slow = int(clamp(self.slow, self.fast + 3, MAX_WINDOW))
        self.mom = int(clamp(self.mom, 2, 100))
        self.sell_at = min(self.sell_at, self.buy_at - 0.05)
        self.clone_min_return = clamp(self.clone_min_return, -0.5, 0.5)
        self.clone_min_money = clamp(self.clone_min_money, 0.0, 2.0)
        self.cooldown = int(clamp(self.cooldown, 0, 60))
        self.lr = clamp(self.lr, 0.001, 0.3)
        self.horizon = int(clamp(self.horizon, 2, 30))
        self.listen = clamp(self.listen, 0.0, 1.0)
        self.keep = clamp(self.keep, 0.0, 0.6)
        self.short = clamp(self.short, 0.0, 0.6) if SHORTS else 0.0
        return self

    def mutate(self, rng, assets, strength=1.0, baskets=False):
        """עותק עם שינויים קטנים - כך אסטרטגיות מתפתחות לאט לאט."""
        def j(v, lo, hi, s):
            return clamp(v + rng.gauss(0, s * strength), lo, hi)
        asset = self.asset
        if not tradable(asset, assets) or rng.random() < SWITCH_RATE:
            asset = pick_asset(rng, assets, baskets)
        return Genome(asset, round(j(self.fast, 2, 50, 3)), round(j(self.slow, 5, MAX_WINDOW, 10)),
                      round(j(self.mom, 2, 100, 5)), [j(w, -1, 1, 0.2) for w in self.weights],
                      j(self.buy_at, -0.2, 0.9, 0.08), j(self.sell_at, -0.9, 0.2, 0.08),
                      j(self.stop_loss, 0.005, 0.4, 0.03), j(self.take_profit, 0.01, 1.0, 0.05),
                      j(self.bet, 0.1, 1.0, 0.1),
                      j(self.clone_min_return, -0.5, 0.5, 0.03), j(self.clone_min_money, 0.0, 2.0, 0.1),
                      round(j(self.cooldown, 0, 60, 2)),
                      self.lr * math.exp(rng.gauss(0, 0.3 * strength)), round(j(self.horizon, 2, 30, 2)), j(self.listen, 0, 1, 0.1),
                      j(self.keep, 0, 0.6, 0.05), j(self.short, 0, 0.6, 0.05) if self.short else 0.0).fix()

    @staticmethod
    def crossover(a, b, rng):
        """ילד של שני הורים: כל תכונה נלקחת מאחד מהם."""
        def pick(x, y):
            return x if rng.random() < 0.5 else y
        genes = {f.name: pick(getattr(a, f.name), getattr(b, f.name)) for f in fields(Genome)}
        genes["weights"] = [pick(x, y) for x, y in zip(a.weights, b.weights)]
        return Genome(**genes).fix()

    def readings(self, m, i):
        """מה הבוט מודד עכשיו, במספרים שאדם מבין."""
        p, slow = m.p[i], m.ma(i, self.slow)
        code, seen, ahead = m.pattern[i]
        channel = lambda lo, hi: (p - lo) / (hi - lo) if hi > lo else 0.5
        return {
            "trend": m.ma(i, self.fast) / slow - 1,           # כמה הממוצע הקצר מעל הממוצע הארוך
            "rsi": m.rsi[i],                                   # מתחת ל-30 = ירד הרבה, מעל 70 = עלה הרבה
            "mom": p / m.p[i - self.mom] - 1,                  # כמה המחיר השתנה ב-mom הנרות האחרונים
            "stretch": p / slow - 1,                           # כמה המחיר מעל הממוצע הארוך
            "macd": (m.macd[i] - m.macd_signal[i]) / p,        # MACD מעל קו האות = התנופה מתחזקת
            "z": (p - slow) / (m.std(i, self.slow) or 1e-9),   # כמה סטיות תקן מעל הממוצע (בולינגר)
            "ch20": channel(m.lo20[i], m.hi20[i]),             # 0 = בשפל של 20 נרות, 1 = בשיא, מעל 1 = פריצה
            "ch55": channel(m.lo55[i], m.hi55[i]),             # אותו דבר ל-55 נרות (שיטת הצבים)
            "vol": m.vol14[i] / (m.vol100[i] or 1e-9),         # פי כמה השוק זז עכשיו לעומת הרגיל
            "pattern": code, "seen": seen, "ahead": ahead,     # הדפוס, כמה פעמים נראה, מה קרה אחריו
            "ahead_z": ahead / ((m.vol50[i] or 1e-9) * PATTERN_AHEAD ** 0.5),
            # חושים מהאינטרנט: הסימן (בין -1 ל-1) והמספר עצמו. None = אין נתון עדכני
            **{n: m.extras[n][1][i] if n in m.extras else None for n in NET_SIGNALS},
            **{n + "_raw": m.extras[n][0][i] if n in m.extras else None for n in NET_SIGNALS},
        }

    @staticmethod
    def signals(r):
        """הופך כל מדידה לסימן בין -1 ל-1 (1 = "תקנה!", -1 = "תמכור!")."""
        return [clamp(r["trend"] * 20), (50 - r["rsi"]) / 50, clamp(r["mom"] * 10), clamp(r["stretch"] * 10),
                clamp(r["macd"] * 200), clamp(r["z"] / 2), clamp(r["ch20"] * 2 - 1), clamp(r["ch55"] * 2 - 1),
                clamp(1 - r["vol"]), clamp(r["ahead_z"] * 3) if r["seen"] >= PATTERN_MIN else 0.0] + \
               [r.get(n) or 0.0 for n in NET_SIGNALS]   # אין נתון = אין דעה

    def parts(self, sig, allowed=SIGNALS):
        """כמה כל סימן תורם לציון: הסימן כפול המשקל שהבוט נותן לו. הציון הוא הסכום, בין -1 ל-1.
        שיטות שלא מופיעות ב-allowed (ההגדרה signals) לא נחשבות."""
        w = [x if name in allowed else 0.0 for name, x in zip(SIGNALS, self.weights)]
        total = sum(abs(x) for x in w) or 1.0
        return [x * y / total for x, y in zip(w, sig)]

    def describe(self, allowed=SIGNALS, goal="trade", learning=False):
        top = sorted(((s, w) for s, w in zip(SIGNALS, self.weights) if s in allowed), key=lambda sw: -abs(sw[1]))[:2]
        style = " + ".join(SIGNAL_WORDS[s][0 if w > 0 else 1] for s, w in top)
        if learning:
            style = (f"מקשיב {self.listen:.0%} למוח הלומד (מנחש {self.horizon} נרות קדימה) "
                     f"ו-{1 - self.listen:.0%} לנוסחה ({style})")
        if goal == "hold":
            return (f"מחזיק לטווח ארוך; {'' if learning else 'מקשיב בעיקר ל: '}{style}; "
                    f"משקיע {self.bet:.0%} מהמזומן, "
                    f"בורח אם המחיר יורד {self.stop_loss:.0%} מהשיא" +
                    (f", ומשאיר {self.keep:.0%} מושקע גם כשבורח (ביטוח)" if self.keep >= 0.01 else ""))
        return (f"{style}; משקיע {self.bet:.0%} מהמזומן, "
                f"סטופ-לוס {self.stop_loss:.0%}, לוקח רווח ב-{self.take_profit:.0%}")

    def wants_clone(self, change, value, start_money):
        """האם הבוט בוחר להשתכפל. מחזיר (כן/לא, למה)."""
        need = self.clone_min_money * start_money
        if change < self.clone_min_return:
            return False, f"הרוויח {change:+.0%} ורוצה לפחות {self.clone_min_return:+.0%}"
        if value / 2 < max(need, DEATH_LINE):
            return False, f"יש לו {value:.2f} ש\"ח ורוצה שלכל חצי יישאר לפחות {need:.2f}"
        return True, ""

    def clone_rule(self, start_money):
        return (f"משתכפל רק אם הרוויח לפחות {self.clone_min_return:+.0%} מאז המבחן, "
                f"ושלכל חצי יישארו לפחות {self.clone_min_money * start_money:.2f} ש\"ח")


# ---------- המוח הלומד ----------
# רשת עצבית קטנה: הסימנים נכנסים, עוברים דרך HIDDEN "תאי עצב", ויוצא ניחוש אחד בין -1 ל-1:
# לאן המחיר ילך ב-horizon הנרות הבאים (1 = יעלה הרבה יותר מהרגיל, -1 = ירד הרבה).
# אחרי שעוברים horizon נרות, הבוט רואה מה באמת קרה ומתקן את המשקלים קצת - ככה הוא לומד מטעויות.

def brain_new(rng, n_in):
    s = 1 / math.sqrt(n_in)
    return {"w1": [[rng.gauss(0, s) for _ in range(n_in)] for _ in range(HIDDEN)], "b1": [0.0] * HIDDEN,
            "w2": [rng.gauss(0, 1 / math.sqrt(HIDDEN)) for _ in range(HIDDEN)], "b2": 0.0}


def brain_fit(b, n_in):
    """מוח שנולד כשהיו פחות סימנים מקבל חיבורים חדשים (באפס) לסימנים שנוספו."""
    for row in b["w1"]:
        row.extend([0.0] * (n_in - len(row)))


def brain_think(b, x):
    """הניחוש של המוח (בין -1 ל-1), ומה כל תא עצב הרגיש."""
    h = [math.tanh(sum(w * xi for w, xi in zip(row, x)) + bias) for row, bias in zip(b["w1"], b["b1"])]
    return math.tanh(sum(w * hk for w, hk in zip(b["w2"], h)) + b["b2"]), h


def brain_learn(b, x, target, lr):
    """צעד למידה אחד: משווים את הניחוש למה שקרה באמת, ומזיזים כל משקל קצת לכיוון שהיה מקטין את הטעות."""
    y, h = brain_think(b, x)
    dy = (y - target) * (1 - y * y)
    for k, hk in enumerate(h):
        dh = dy * b["w2"][k] * (1 - hk * hk)
        b["w2"][k] -= lr * dy * hk
        row = b["w1"][k]
        for j, xj in enumerate(x):
            row[j] -= lr * dh * xj
        b["b1"][k] -= lr * dh
    b["b2"] -= lr * dy
    return y


def brain_copy(b, rng, noise=0.02):
    """המוח של ההורה עובר לילד, עם שינוי קטן."""
    c = copy.deepcopy(b)
    for row in c["w1"]:
        for j in range(len(row)):
            row[j] += rng.gauss(0, noise)
    c["w2"] = [w + rng.gauss(0, noise) for w in c["w2"]]
    return c


def brain_importance(b, xs):
    """כמה כל סימן משפיע על המוח באופן כללי: עוצמת החיבורים שלו כפול כמה הסימן באמת זז (xs = קלטים אחרונים).
    סימן שתמיד 0 (אסור בהגדרות או שאין לו נתונים) לא משפיע בכלל, גם אם נשארו לו משקלים אקראיים מהלידה."""
    n = len(b["w1"][0])
    act = [sum(abs(x[j]) for x in xs) / len(xs) if xs else 0.0 for j in range(n)]
    return [act[j] * sum(abs(b["w2"][k] * b["w1"][k][j]) for k in range(len(b["w2"]))) for j in range(n)]


# ---------- הבוט ----------

@dataclass
class Bot:
    id: int
    genome: Genome
    born: int                   # באיזה נר הבוט נולד
    generation: int = 0
    cash: float = 0.0
    units: float = 0.0          # כמה מטבעות הוא מחזיק
    entry: float = 0.0
    period_start: float = 0.0   # כמה כסף היה לו בתחילת תקופת המבחן הנוכחית
    period_price: float = 0.0   # מחיר המטבע (או הסל) בתחילת תקופת המבחן
    period_top: float = 0.0     # השיא של הצמיחה מהמסחר מאז המבחן (בשביל לדעת כמה הוא נפל בדרך)
    period_drop: float = 0.0    # הנפילה הכי גדולה מהשיא מאז המבחן
    prev_value: float = 0.0
    log_growth: float = 0.0     # כמה הבוט גדל מהמסחר שלו (בלי תשלומים ושכפולים)
    paid: float = 0.0           # כמה הוא שילם לבעלים עד עכשיו
    trades: int = 0
    values: list = field(default_factory=list)
    price: float = 0.0          # המחיר בנר האחרון
    readings: dict = field(default_factory=dict)   # מה הוא מדד בנר האחרון
    score: float = None         # הציון שיצא לו בנר האחרון
    scores: list = field(default_factory=list)     # הציונים לאורך הזמן, בשביל הגרף
    last: list = field(default_factory=list)       # [מתי, מה הוא עשה ולמה]
    peak: float = 0.0           # המחיר הכי גבוה מאז שקנה (בשביל לזהות נפילה)
    wait: int = 0               # כמה נרות עוד לחכות אחרי בריחה
    held: int = 0               # בכמה נרות הוא החזיק מטבע
    seen: int = 0               # כמה נרות הוא חי
    danger: int = 0             # כמה נרות ברצף הציון מתחת לקו הסכנה
    study: bool = False         # הוא מהחכמים: בנר הבא הוא לומד שוב על העבר הקרוב
    out: bool = False           # ברח מסכנה (אולי עם חלק קטן שנשאר מושקע - הביטוח), ומחכה לחזור
    mind: dict = None           # המוח הלומד (None = עוד לא למד כלום)
    memory: list = field(default_factory=list)     # [סימנים, מחיר, תנודתיות, ניחוש] של הנרות האחרונים, ללמוד מהם כשיתברר מה קרה
    lessons: int = 0            # מכמה דוגמאות המוח למד
    hits: list = field(default_factory=list)       # האם צדק בכל אחד מ-100 הניחושים האחרונים (1/0)
    accuracy: list = field(default_factory=list)   # כמה הוא צדק לאורך הזמן (בשביל הגרף)
    guess: float = None         # הניחוש האחרון של המוח
    feel: float = None          # ממוצע הניחושים האחרונים (כדי לא לקפוץ מכל רעש) - זה מה שהבוט משתמש בו
    checked: int = 0            # כמה ניחושים של המוח נבדקו בחיים של הבוט הזה (בלי מה שעבר בירושה)
    right: int = 0              # בכמה מהם המוח צדק
    ups: int = 0                # בכמה מהם המחיר באמת עלה (כדי להשוות ל"תמיד לנחש שיעלה")

    def value(self, price):
        return self.cash + self.units * price

    def period_return(self, price):
        return self.value(price) / self.period_start - 1 if self.period_start > 0 else -1.0

    def edge(self, price, market=None):
        """כמה הבוט הרוויח מאז המבחן, פחות כמה היה מרוויח מ"לקנות ולחכות": בכל המטבעות שווה בשווה
        (market = כמה הם עלו או ירדו מאז המבחן), או במטבע שלו אם market לא ידוע.
        חיובי = הוא היה חכם יותר. (מול כל המטבעות, אי אפשר "לרמות" ע"י בחירת מטבע שלא זז ולשבת במזומן.)"""
        if market is None:
            market = price / self.period_price - 1 if self.period_price > 0 else 0.0
        return self.period_return(price) - market

    def fitness(self, tick):
        """צמיחה ממוצעת לנר. לבוט צעיר אין עדיין מספיק היסטוריה, אז הציון שלו קרוב ל-0."""
        return self.log_growth / max(tick - self.born, 30)

    def step(self, m, i, allowed=SIGNALS, goal="trade", learning=False, rng=None, patience=1):
        """מחשב ומחליט אם לקנות או למכור. מחזיר משפט שמסביר מה עשה ולמה (או None)."""
        g = self.genome
        if i < max(g.slow, g.mom):
            return None
        price = self.price = m.p[i]
        self.period_price = self.period_price or price   # בוט חדש: המחיר שממנו משווים ל"לקנות ולחכות"
        self.readings = g.readings(m, i)
        formula = sum(g.parts(Genome.signals(self.readings), allowed))
        if learning:
            danger = goal == "hold"   # במצב "להחזיק" המוח מחפש סכנה, לא מנחש כיוון
            if self.mind is None:
                self.go_to_school(m, i, allowed, rng or random.Random(self.id), danger)
            if self.study:
                self.restudy(m, i, allowed, danger)
            feel = self.observe(self.inputs(self.readings, allowed), price, m.vol50[i], danger)
            self.score = (1 - g.listen) * formula + g.listen * feel
        else:
            self.forget()       # בלי מוח אין ניחושים שמחכים לתוצאה
            self.score = formula
        self.seen += 1
        self.held += self.units > 0
        self.wait = max(0, self.wait - 1)
        if goal == "hold":
            return self.hold_step(price, patience)
        if self.units > 0:
            change = price / self.entry - 1
            why = (f"הפסיד {-change:.0%} מהקנייה (הסטופ-לוס שלו {g.stop_loss:.0%})" if change < -g.stop_loss else
                   f"הרוויח {change:.0%} מהקנייה (לוקח רווח ב-{g.take_profit:.0%})" if change > g.take_profit else
                   f"הציון {self.score:+.2f} ירד מתחת לסף {g.sell_at:+.2f}" if self.score < g.sell_at else None)
            if why:
                self.sell(price)
                return f"מכר {g.asset} ב-{fmt_price(price)} כי {why}"
        elif self.cash > 0.01 and self.score > g.buy_at:
            self.buy(price)
            return f"קנה {g.asset} ב-{fmt_price(price)} כי הציון {self.score:+.2f} עלה מעל הסף {g.buy_at:+.2f}"
        return None

    @staticmethod
    def inputs(readings, allowed):
        """מה נכנס למוח: כל הסימנים (שיטה שאסורה בהגדרות = 0)."""
        return [s if n in allowed else 0.0 for n, s in zip(SIGNALS, Genome.signals(readings))]

    def observe(self, x, price, vol, danger=False):
        """נר אחד מבחינת המוח: קודם לומד מהדוגמה שהתוצאה שלה התבררה עכשיו (לפני horizon נרות),
        ואז מנחש מה יקרה מעכשיו. הניחוש נשמר, כדי לבדוק אותו ביושר כשהתוצאה תגיע.
        danger: המוח מנחש אם תהיה נפילה גדולה בקרוב (במקום לאן המחיר ילך)."""
        brain_fit(self.mind, len(x))
        for e in self.memory:                  # המחיר הכי נמוך מאז כל ניחוש (בשביל "האם הייתה נפילה")
            if len(e) > 4:
                e[4] = min(e[4], price)
        while len(self.memory) >= self.genome.horizon:
            e = self.memory.pop(0)
            self.lesson(*e[:4], price, danger, e[4] if len(e) > 4 else None)
        self.guess = brain_think(self.mind, x)[0]
        self.memory.append([x, price, vol, self.guess, price])
        a = 2 / (self.genome.horizon + 1)
        self.feel = self.guess if self.feel is None else self.feel + a * (self.guess - self.feel)
        return self.feel

    def forget(self):
        """שוכח ניחושים שעוד מחכים לתוצאה (למשל כשאורך הנר השתנה, או אחרי הפסקה ארוכה),
        כדי לא ללמוד מהם תוצאה של זמן אחר מזה שהם ניחשו."""
        self.memory.clear()
        self.feel = None

    def lesson(self, x, p0, vol, guess, p_now, danger=False, low=None):
        """לומד מדוגמה אחת שהתוצאה שלה כבר ידועה: מה היו הסימנים, ומה קרה ב-horizon הנרות שאחריהם.
        "צדק" נמדד לפי הניחוש שנעשה אז, לפני שידע את התוצאה.
        רגיל: לאן המחיר הלך (1 = עלה הרבה יותר מהרגיל, -1 = ירד הרבה).
        סכנה: כמה עמוק המחיר נפל בדרך (1 = לא נפל בכלל, 0 = נפל כמו ירידה רגילה, -1 = נפל פי 2 מזה)."""
        scale = max(vol, 1e-6) * math.sqrt(self.genome.horizon)
        if danger:
            move = math.log(min(low or p_now, p_now) / p0) / scale + 1
            target = clamp(move)
        else:
            move = math.log(p_now / p0) / scale
            target = clamp(move / 2)
        brain_learn(self.mind, x, target, self.genome.lr)
        hit = int((guess > 0) == (move > 0))
        self.lessons += 1
        self.checked, self.right, self.ups = self.checked + 1, self.right + hit, self.ups + (move > 0)
        self.hits = (self.hits + [hit])[-100:]
        if self.lessons % 10 == 0 and len(self.hits) >= 30:
            self.accuracy = thin(self.accuracy + [round(sum(self.hits) / len(self.hits), 3)], ACC_POINTS)

    def restudy(self, m, i, allowed, danger):
        """שיעור נוסף לחכמים: עובר שוב על SCHOOL הנרות האחרונים שהתוצאה שלהם כבר ידועה, ולומד מהם עוד פעם."""
        self.study = False
        g, h = self.genome, self.genome.horizon
        for t in range(max(g.slow, g.mom, i - SCHOOL), i - h):
            x = self.inputs(g.readings(m, t), allowed)
            scale = max(m.vol50[t], 1e-6) * math.sqrt(h)
            if danger:
                target = clamp(math.log(min(m.p[t:t + h + 1]) / m.p[t]) / scale + 1)
            else:
                target = clamp(math.log(m.p[t + h] / m.p[t]) / scale / 2)
            brain_learn(self.mind, x, target, g.lr)

    def go_to_school(self, m, i, allowed, rng, danger=False):
        """בוט חדש בלי מוח: נולד עם מוח אקראי ועובר על SCHOOL הנרות האחרונים בדיוק כמו בזמן אמת -
        נר אחרי נר, מנחש ולומד רק ממה שכבר קרה באותו רגע."""
        g = self.genome
        self.mind = brain_new(rng, len(SIGNALS))
        for t in range(max(g.slow, g.mom, i - SCHOOL), i):
            self.observe(self.inputs(g.readings(m, t), allowed), m.p[t], m.vol50[t], danger)

    def hold_step(self, price, patience=1):
        """המטרה: להחזיק כמה שיותר זמן, ולברוח רק כשרואים סכנה (ואז לחזור כשהיא עוברת).
        patience: כמה נרות ברצף הציון צריך להישאר מתחת לקו הסכנה לפני שבורחים (כדי לא לברוח מכל רעש)."""
        g = self.genome
        self.danger = self.danger + 1 if self.score < g.sell_at else 0
        self.out = self.out and self.units != 0     # מי שמכר הכול כבר לא "בחוץ עם ביטוח", פשוט במזומן
        if self.units > 0 and not self.out:
            self.peak = max(self.peak, price)
            drop = price / self.peak - 1
            why = (f"הציון {self.score:+.2f} נשאר מתחת לקו הסכנה {g.sell_at:+.2f} "
                   f"{self.danger} נרות ברצף" if self.danger >= patience else
                   f"המחיר ירד {-drop:.0%} מהשיא מאז שקנה (בורח בירידה של {g.stop_loss:.0%})"
                   if drop < -g.stop_loss else None)
            if why:
                self.sell(price, 1 - g.keep)
                if g.short:   # הימור נגד: מרוויח אם המחיר ימשיך לרדת, מפסיד אם יעלה (עד שיחזור לקנות)
                    self.short_sell(price, g.short * self.value(price))
                self.out, self.wait = self.units != 0, g.cooldown
                kept = f" (השאיר {g.keep:.0%} מושקע - ביטוח למקרה שהמחיר יחזור לעלות מהר)" if self.out else ""
                return f"זיהה סכנה ומכר {g.asset} ב-{fmt_price(price)} כי {why}{kept}"
        if self.cash > 0.01 and not self.wait and self.score > g.sell_at + CLEAR:
            if self.units > 0 and not self.out:   # כבר מחזיק: משקיע גם כסף שנשאר בצד, אם הוא לא זניח
                if TOP_UP and self.cash > 0.05 * self.value(price):
                    self.buy(price)
                return None
            self.buy(price)
            self.out, self.peak = False, price
            return (f"קנה {g.asset} ב-{fmt_price(price)} כי אין סימני סכנה "
                    f"(הציון {self.score:+.2f} מעל {g.sell_at + CLEAR:+.2f})")
        return None

    def buy(self, price):
        spend = self.cash * self.genome.bet
        if self.units == 0:
            self.entry = self.peak = price
        self.units += spend * (1 - FEE) / price
        self.cash -= spend
        self.trades += 1

    def sell(self, price, part=1.0):
        """מוכר את כל המטבעות, או רק חלק מהם (part)."""
        sold = self.units if part >= 1 else self.units * part
        self.cash += sold * price * (1 - FEE)
        self.units -= sold
        if part >= 1:
            self.units = 0.0
        self.trades += 1

    def short_sell(self, price, amount):
        """מכירה בחסר: "שואל" מטבעות ומוכר אותם עכשיו. כשיקנה בחזרה בזול יותר - הרווח שלו."""
        q = amount / price
        self.cash += q * price * (1 - FEE)
        self.units -= q
        self.trades += 1

    def take(self, amount, price):
        """מוציא כסף מהבוט: קודם מהמזומן, ואם אין מספיק מוכר קצת מהמטבעות."""
        from_cash = min(self.cash, amount)
        self.cash -= from_cash
        units = min(max(self.units, 0.0), (amount - from_cash) / (price * (1 - FEE)))
        self.units -= units
        return from_cash + units * price * (1 - FEE)


def members(asset):
    """המטבעות שבוט סוחר בהם: "BTC" -> ["BTC"], סל "BTC+ETH" -> ["BTC", "ETH"]."""
    return asset.split("+")


def tradable(asset, assets):
    return all(a in assets for a in members(asset))


def pick_asset(rng, assets, baskets=False):
    """מטבע אחד, או (לפעמים) סל של כמה מטבעות - עד כל המטבעות ביחד.
    ככה נפילה של מטבע אחד לא הורגת את כל הכסף, ובשנות שיא הבוט לא מפספס את המטבע שהתפוצץ."""
    if baskets and len(assets) > 1 and rng.random() < BASKET_RATE:
        return "+".join(sorted(rng.sample(list(assets), rng.randint(2, len(assets)))))
    return rng.choice(assets)


def price_of(prices, asset):
    """המחיר של מטבע, או של סל: הממוצע הגאומטרי של המטבעות בסל (כל מטבע משפיע באותה מידה על השינוי)."""
    if asset in prices:
        return prices[asset]
    ps = [prices[a] for a in members(asset)]
    return math.exp(sum(math.log(p) for p in ps) / len(ps))


def fmt_price(p):
    return f"${p:,.0f}" if p >= 100 else f"${p:,.2f}" if p >= 1 else f"${p:.4f}"


def thin(points, limit):
    """כשיש יותר מדי נקודות לגרף, משאירים כל נקודה שנייה (ותמיד את האחרונה)."""
    return points[:-1:2] + points[-1:] if len(points) > limit else points


# ---------- האבולוציה ----------

class World:
    def __init__(self, cfg, minutes_per_candle, seed=None, seeds=()):
        self.cfg = cfg
        self.candle = minutes_per_candle
        self.rng = random.Random(seed)
        self._baskets = {}            # שווקים של סלי מטבעות (לא נשמר, נבנה מחדש)
        self.seeds = list(seeds)      # אסטרטגיות מאומנות שאפשר להתחיל מהן
        self.out = None               # לאן להדפיס אירועים חשובים (למשל print)
        self.verbose = False          # להדפיס גם כל מוות ושכפול
        self.bots = []
        self.next_id = 1
        self.tick = 0
        self.now = ""
        self.owner_profit = 0.0
        self.invested = 0.0
        self.deaths = 0
        self.clones = 0
        self.declined = 0             # כמה פעמים בוטים בחרו לא להשתכפל
        self.refilled = 0             # כמה בוטים חדשים נולדו כדי למלא מקומות ריקים
        self.selections = 0
        self.market_start = None      # מחיר "כל המטבעות שווה בשווה" בתחילת תקופת המבחן
        self.past_brains = [0, 0, 0]  # ניחושים שנבדקו / צדקו / המחיר עלה - של בוטים שכבר מתו
        self.history = []             # תמונת מצב אחרי כל נר, בשביל הגרפים
        self.events = []              # מה קרה לאחרונה

    def note(self, text, important=False):
        self.events = (self.events + [[self.now, text]])[-EVENTS:]
        if self.out and (important or self.verbose):
            self.out(text)

    def populate(self):
        assets = self.cfg.assets
        for k in range(self.cfg.start_bots):
            teacher = None
            if self.seeds:
                teacher = self.seeds[k % len(self.seeds)]
                g = teacher.genome
                if k >= len(self.seeds) or not tradable(g.asset, assets):
                    g = g.mutate(self.rng, assets, 0.5, self.cfg.baskets)
            else:
                g = Genome.random(self.rng, assets, self.cfg.goal, self.cfg.baskets)
            self.spawn(g, parent=teacher)

    def spawn(self, genome, money=None, generation=0, parent=None):
        """בוט חדש. אם יש parent עם מוח, המוח עובר לילד (עם שינוי קטן) יחד עם כל מה שלמד עד עכשיו;
        בלי זה הבוט ילך ל"בית ספר"."""
        if money is None:
            money = self.cfg.start_money
            self.invested += money      # בוט חדש מאפס = הבעלים משקיע עוד כסף
        bot = Bot(self.next_id, genome, self.tick, generation, cash=money, period_start=money, prev_value=money)
        if parent is not None and parent.mind:
            bot.mind = brain_copy(parent.mind, self.rng)
            bot.lessons, bot.hits, bot.accuracy = parent.lessons, list(parent.hits), list(parent.accuracy)
        self.next_id += 1
        self.bots.append(bot)
        return bot

    def every(self, text):
        return every(text, self.candle)

    def market(self, markets, asset):
        """השוק של מטבע, או של סל מטבעות (נבנה פעם אחת מהמטבעות שבו ונשמר)."""
        if asset in markets:
            return markets[asset]
        parts = [markets[a] for a in members(asset)]
        key = (asset, tuple(id(m) for m in parts))
        if key not in self._baskets:
            if len(self._baskets) > 50:
                self._baskets.clear()
            index = [price_of(dict(zip(members(asset), ps)), asset) for ps in zip(*(m.p for m in parts))]
            self._baskets[key] = Market(index, parts[0].extras)   # החושים לפי המטבע הראשון בסל
        return self._baskets[key]

    def step(self, markets, i, when):
        """נר אחד: הבוטים סוחרים, ואם הגיע הזמן - משלמים לבעלים ועוברים מבחן."""
        self.now = when.isoformat(timespec="minutes")
        prices = {a: m.p[i] for a, m in markets.items()}
        self.market_start = self.market_start or self.market_price(prices)
        for bot in self.bots:
            did = bot.step(self.market(markets, bot.genome.asset), i, self.cfg.signals, self.cfg.goal,
                           self.cfg.brain == "learning", self.rng, self.every(self.cfg.patience))
            if did:
                bot.last = [self.now, did]
        self.tick += 1
        for bot in self.bots:
            v = bot.value(price_of(prices, bot.genome.asset))
            bot.log_growth += math.log(max(v, 1e-9) / max(bot.prev_value, 1e-9))
            bot.period_top = max(bot.period_top, bot.log_growth)
            bot.period_drop = max(bot.period_drop, bot.period_top - bot.log_growth)

        if self.tick % self.every(self.cfg.pay_every) == 0:
            self.pay(prices)
        self.bury_broke(prices)
        if self.tick % self.every(self.cfg.select_every) == 0:
            self.select(prices)
        if not self.bots:
            self.populate()
            self.note(f"כל הבוטים מתו. נוצרו {len(self.bots)} בוטים חדשים", True)

        inside = 0.0
        for bot in self.bots:
            v = bot.value(price_of(prices, bot.genome.asset))
            inside += v
            bot.prev_value = v
            bot.values = thin(bot.values + [round(v, 4)], BOT_POINTS)
            bot.scores = thin(bot.scores + [None if bot.score is None else round(bot.score, 3)], BOT_POINTS)
        self.history = thin(self.history + [{
            "time": self.now, "prices": prices, "alive": len(self.bots), "inside": round(inside, 4),
            "collected": round(self.owner_profit, 4), "invested": round(self.invested, 4)}], CHART_POINTS)

    def pay(self, prices):
        share = self.cfg.pay_percent / 100
        for bot in self.bots:
            p = price_of(prices, bot.genome.asset)
            got = bot.take(bot.value(p) * share, p)
            bot.paid += got
            self.owner_profit += got

    def bury_broke(self, prices):
        for bot in list(self.bots):
            p = price_of(prices, bot.genome.asset)
            if bot.value(p) < DEATH_LINE:
                self.bots.remove(bot)
                self.retire(bot)
                self.deaths += 1
                self.owner_profit += bot.take(bot.value(p), p)
                self.note(f"בוט #{bot.id} ({bot.genome.asset}) נשאר בלי כסף ומת")

    def select(self, prices):
        """המבחן: הפחות טובים מתים, והכסף שלהם הולך לבעלים (או לטובים, לפי ההגדרות).
        כל אחד מהטובים מחליט לפי הגנים שלו אם להשתכפל. מי שמשתכפל מתחלק בכסף שלו עם השכפול."""
        price = lambda b: price_of(prices, b.genome.asset)
        change = {b.id: b.period_return(price(b)) for b in self.bots}
        ranked = self.ranked(prices)
        keep = len(ranked) - int(len(ranked) * self.cfg.kill_percent / 100)
        keep = max(1, min(keep, self.cfg.max_bots))
        self.selections += 1
        to_me = self.cfg.losers_money == "me"
        loot = 0.0
        for bot in ranked[keep:]:
            self.retire(bot)
            got = bot.take(bot.value(price(bot)), price(bot))
            loot += got
            self.deaths += 1
            self.note(f"בוט #{bot.id} ({bot.genome.asset}, {change[bot.id]:+.0%}, "
                      f"מול לקנות ולחכות {bot.edge(price(bot), self.market_return(prices)):+.0%}) נכשל במבחן ומת. "
                      f"{got:.2f} ש\"ח עברו {'אליך' if to_me else 'לטובים'}")
        self.bots = ranked[:keep]
        self.teach(ranked[:keep])
        if to_me:
            self.owner_profit += loot
        else:
            for bot in self.bots:
                bot.cash += loot / len(self.bots)
        born = declined = 0
        for parent in ranked[:keep]:
            if len(self.bots) >= self.cfg.max_bots:
                break
            p = price(parent)
            yes, why = parent.genome.wants_clone(change[parent.id], parent.value(p), self.cfg.start_money)
            if not yes:
                declined += 1
                self.note(f"בוט #{parent.id} בחר לא להשתכפל: {why}")
                continue
            money = parent.take(parent.value(p) / 2, p)
            genome, inherit = self.child_genome(parent)
            child = self.spawn(genome, money, parent.generation + 1, parent if inherit else None)
            self.clones += 1
            born += 1
            self.note(f"בוט #{parent.id} שוכפל לבוט #{child.id} ({child.genome.asset})")
        self.declined += declined
        added = self.refill() if self.cfg.refill else 0
        for bot in self.bots:
            bot.period_start, bot.period_price = bot.value(price(bot)), price(bot)
            bot.period_top, bot.period_drop = bot.log_growth, 0.0
        self.market_start = self.market_price(prices)    # תקופה חדשה: משווים מעכשיו
        extra = f", {added} חדשים נולדו במקומות הריקים (שמת עוד {added * self.cfg.start_money:g} ש\"ח)" if added else ""
        self.note(f"מבחן {self.selections}: {len(ranked) - keep} בוטים מתו "
                  f"({loot:.2f} ש\"ח עברו {'אליך' if to_me else 'לטובים'}), "
                  f"{born} שוכפלו, {declined} בחרו לא להשתכפל{extra}. עכשיו יש {len(self.bots)} בוטים", True)

    def refill(self):
        """ממלא מקומות ריקים עד start_bots: בוטים חדשים מהאסטרטגיות של הבוטים הכי טובים
        (עם שינוי קטן), והבעלים משלם על כל אחד start_money כמו בהתחלה."""
        target = min(self.cfg.start_bots, self.cfg.max_bots)
        parents = self.best(len(self.bots))
        added = 0
        while parents and len(self.bots) < target:
            parent = parents[added % len(parents)]
            genome, inherit = self.child_genome(parent)
            child = self.spawn(genome, generation=parent.generation + 1, parent=parent if inherit else None)
            added += 1
            self.note(f"בוט #{child.id} ({child.genome.asset}) נולד במקום ריק, מהאסטרטגיה של בוט #{parent.id}")
        self.refilled += added
        return added

    def teach(self, survivors):
        """הכי חכמים מלמדים: הבוט הכי טוב מעביר חלק מהידע שלו (המוח והנוסחה) לשאר השורדים,
        והחכמים (הרבע העליון) לומדים שוב על העבר הקרוב כדי להשתפר עוד."""
        if len(survivors) < 2:
            return
        best = survivors[0]
        for b in survivors[1:] if TEACH else ():
            b.genome.weights = [(1 - TEACH) * w + TEACH * t for w, t in zip(b.genome.weights, best.genome.weights)]
            if b.mind and best.mind and len(b.mind["w2"]) == len(best.mind["w2"]):
                for key in ("w1",):
                    b.mind[key] = [[(1 - TEACH) * w + TEACH * t for w, t in zip(r, tr)]
                                   for r, tr in zip(b.mind[key], best.mind[key])]
                b.mind["w2"] = [(1 - TEACH) * w + TEACH * t for w, t in zip(b.mind["w2"], best.mind["w2"])]
        for b in survivors[:max(1, len(survivors) // 4)] if STUDY else ():
            b.study = True

    def retire(self, bot):
        """בוט שמת: שומרים כמה ניחושים המוח שלו עשה, כדי שהדיוק של המוחות ייספר ביושר (לא רק אצל מי ששרד)."""
        for k, v in enumerate((bot.checked, bot.right, bot.ups)):
            self.past_brains[k] += v

    def brain_record(self):
        """(כמה ניחושים נבדקו, בכמה המוח צדק, בכמה המחיר עלה) - של כל הבוטים אי פעם."""
        return tuple(p + sum(getattr(b, f) for b in self.bots)
                     for p, f in zip(self.past_brains, ("checked", "right", "ups")))

    def child_genome(self, parent):
        """הגנום של ילד, והאם הוא מקבל גם את המוח של ההורה (רעיון חדש לגמרי מתחיל עם מוח חדש)."""
        r, assets = self.rng.random(), self.cfg.assets
        if r < IMMIGRANT_RATE:
            return Genome.random(self.rng, assets, self.cfg.goal, self.cfg.baskets), False
        g = parent.genome
        others = [b for b in self.bots if b is not parent]
        if r < IMMIGRANT_RATE + MIX_RATE and others:
            g = Genome.crossover(g, self.rng.choice(others).genome, self.rng)
        return self.spread(g.mutate(self.rng, assets, 0.5, self.cfg.baskets)), True

    def spread(self, g):
        """גיוון: אם כבר יותר מדי בוטים במטבע של הילד, הוא עובר למטבע שיש בו פחות בוטים.
        ככה לא כולם יושבים באותו מטבע, ואם מטבע אחר מתפוצץ - יש מי שמחזיק אותו."""
        if MAX_SHARE >= 1 or not self.bots:
            return g
        count = {}
        for b in self.bots:
            count[b.genome.asset] = count.get(b.genome.asset, 0) + 1
        if count.get(g.asset, 0) < MAX_SHARE * len(self.bots):
            return g
        least = min(self.cfg.assets, key=lambda a: (count.get(a, 0), self.rng.random()))
        return replace(g, asset=least)

    def market_price(self, prices):
        """המחיר של "כל המטבעות שווה בשווה" (ממוצע גאומטרי)."""
        return price_of(prices, "+".join(a for a in self.cfg.assets if a in prices) or "+".join(prices))

    def market_return(self, prices):
        """כמה "לקנות ולחכות" בכל המטבעות (שווה בשווה) עלה או ירד מאז המבחן האחרון."""
        now = self.market_price(prices)
        return now / (self.market_start or now) - 1

    def ranked(self, prices):
        """הבוטים לפי מי שהכי מצליח מאז המבחן האחרון: כמה הם ניצחו את "לקנות ולחכות" במטבע שלהם
        (judge = "beat_hold"), או כמה כסף הרוויחו (judge = "money")."""
        market = self.market_return(prices)
        def score(b):
            p = price_of(prices, b.genome.asset)
            if self.cfg.judge == "steady":   # ניצח את "לקנות ולחכות", ובלי ליפול הרבה בדרך
                return b.edge(p, market) - DROP_PENALTY * b.period_drop
            return b.edge(p, market) if self.cfg.judge == "beat_hold" else b.period_return(p)
        return sorted(self.bots, key=score, reverse=True)

    def best(self, k):
        return sorted(self.bots, key=lambda b: b.fitness(self.tick), reverse=True)[:k]

    def next_in(self, text):
        """בעוד כמה דקות יקרה האירוע הבא שקורה כל text."""
        n = self.every(text)
        return (n - self.tick % n) * self.candle

    # --- שמירה וטעינה (בשביל המסחר החי, שרץ לאורך ימים) ---

    def to_dict(self):
        skip = ("rng", "seeds", "cfg", "out", "verbose", "bots", "_baskets")
        d = {k: v for k, v in vars(self).items() if k not in skip}
        d["bots"] = [asdict(b) for b in self.bots]
        return d

    @staticmethod
    def from_dict(d, cfg):
        w = World(cfg, d["candle"])
        for k, v in d.items():
            if k != "bots":
                setattr(w, k, v)
        w.bots = [Bot(**{**b, "genome": Genome(**b["genome"])}) for b in d["bots"]]
        for b in w.bots:
            if b.mind:
                brain_fit(b.mind, len(SIGNALS))   # נוספו סימנים מאז שנשמר
        return w


def run_history(times, prices, world, start=0, extras=None):
    """מריץ את העולם על מחירי עבר. prices: {מטבע: [מחירים]}, extras: חושים מהאינטרנט (internet.extras).
    נרות לפני start משמשים רק לחישוב אינדיקטורים."""
    extras = extras or {}
    markets = {a: Market(p, extras.get(a)) for a, p in prices.items()}
    for i in range(start, len(times)):
        world.step(markets, i, times[i])


def save_brains(path, bots, candle):
    """שומר את הבוטים הכי טובים: האסטרטגיה (גנום), וגם המוח עם כל מה שלמד ואורך הנר שעליו למד."""
    with open(path, "w") as f:
        json.dump([{**asdict(b.genome), "mind": b.mind, "lessons": b.lessons, "candle": candle} for b in bots], f)


def load_brains(path, candle=None):
    """הבוטים השמורים, בתור "מורים" לבוטים החדשים. מוח שלמד על נרות באורך אחר לא עובר
    (מה שקורה ב-7 ימים לא דומה למה שקורה ב-7 שעות) - הבוט החדש ילך ל"בית ספר" במקום."""
    with open(path) as f:
        rows = json.load(f)
    out = []
    for g in rows:
        mind, lessons, made = g.pop("mind", None), g.pop("lessons", 0), g.pop("candle", None)
        if mind and candle is not None and made != candle:
            mind, lessons = None, 0
        if mind:
            brain_fit(mind, len(SIGNALS))
        out.append(Bot(0, Genome(**{"asset": "BTC", **g}), 0, mind=mind, lessons=lessons))
    return out
