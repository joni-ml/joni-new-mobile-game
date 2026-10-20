"""
הלב של המערכת: הגדרות, נתוני שוק, אינדיקטורים, הבוטים והאבולוציה.

את הקובץ הזה לא מריצים ישירות. משתמשים בו:
  evolution_sim.py - אימון ובדיקה על מחירי עבר
  live.py          - מסחר חי על נייר עם מחירים אמיתיים מהבורסה
"""

import csv
import json
import math
import random
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime, timedelta

FEE = 0.001             # 0.1% עמלה לכל קנייה/מכירה
DEATH_LINE = 0.05       # מתחת לזה הבוט "מת"
MAX_WINDOW = 200        # הממוצע הנע הכי ארוך שבוט יכול להשתמש בו
IMMIGRANT_RATE = 0.1    # חלק מהשכפולים מקבלים אסטרטגיה חדשה לגמרי, כדי להמשיך לחפש רעיונות
MIX_RATE = 0.25         # חלק מהשכפולים לוקחים גם תכונות מבוט טוב אחר
SWITCH_RATE = 0.1       # הסיכוי ששכפול יעבור לסחור במטבע אחר
CHART_POINTS = 2000     # כמה נקודות לשמור לגרף של הבעלים
BOT_POINTS = 300        # כמה נקודות לשמור לגרף של כל בוט
EVENTS = 30             # כמה אירועים אחרונים לזכור (מוות, שכפול, מבחן)


# ---------- הגדרות ----------

@dataclass
class Settings:
    assets: list = field(default_factory=lambda: ["BTC", "ETH", "XRP", "DOGE", "LTC", "ADA", "LINK"])
    start_bots: int = 10
    max_bots: int = 20
    start_money: float = 5.0
    pay_every: str = "1d"
    pay_percent: float = 1.0
    select_every: str = "7d"
    kill_percent: float = 50.0
    losers_money: str = "me"
    candle: str = "1h"


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
    for t in (s.pay_every, s.select_every):
        minutes(t)                      # בודק שהזמנים כתובים נכון
    if minutes(s.candle) not in (1, 5, 15, 60):
        raise SystemExit(f"candle יכול להיות רק 1m, 5m, 15m או 1h (כתוב {s.candle!r})")
    if not s.assets:
        raise SystemExit("צריך לפחות מטבע אחד ב-assets")
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


class Market:
    """מחירים של מטבע אחד + אינדיקטורים שמחושבים פעם אחת מראש, כדי שהכול ירוץ מהר."""

    def __init__(self, prices):
        self.p = prices
        self.cum = [0.0]
        for x in prices:
            self.cum.append(self.cum[-1] + x)
        self.rsi = rsi_series(prices)

    def ma(self, i, n):
        """ממוצע של n המחירים האחרונים, עד נר i כולל."""
        return (self.cum[i + 1] - self.cum[i + 1 - n]) / n


# ---------- האסטרטגיה ("הגנום") ----------

# כל בוט מסתכל על 4 סימנים, ומחליט כמה משקל לתת לכל אחד (משקל שלילי = ההפך).
SIGNALS = ("trend", "dip", "momentum", "stretch")
SIGNAL_WORDS = {
    "trend": ("עוקב אחרי המגמה", "הולך נגד המגמה"),
    "dip": ("קונה אחרי ירידות", "קונה כשהשוק חם"),
    "momentum": ("רודף אחרי עליות", "קונה אחרי נפילות"),
    "stretch": ("קונה כשהמחיר מעל הממוצע", "קונה כשהמחיר מתחת לממוצע"),
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

    @staticmethod
    def random(rng, assets):
        fast = rng.randint(2, 30)
        return Genome(rng.choice(assets), fast, fast + rng.randint(5, 120), rng.randint(2, 60),
                      [rng.uniform(-1, 1) for _ in SIGNALS],
                      rng.uniform(0.05, 0.6), rng.uniform(-0.6, 0.0),
                      rng.uniform(0.02, 0.25), rng.uniform(0.03, 0.5), rng.uniform(0.2, 1.0)).fix()

    def fix(self):
        self.fast = int(clamp(self.fast, 2, 50))
        self.slow = int(clamp(self.slow, self.fast + 3, MAX_WINDOW))
        self.mom = int(clamp(self.mom, 2, 100))
        self.sell_at = min(self.sell_at, self.buy_at - 0.05)
        return self

    def mutate(self, rng, assets, strength=1.0):
        """עותק עם שינויים קטנים - כך אסטרטגיות מתפתחות לאט לאט."""
        def j(v, lo, hi, s):
            return clamp(v + rng.gauss(0, s * strength), lo, hi)
        asset = self.asset
        if asset not in assets or rng.random() < SWITCH_RATE:
            asset = rng.choice(assets)
        return Genome(asset, round(j(self.fast, 2, 50, 3)), round(j(self.slow, 5, MAX_WINDOW, 10)),
                      round(j(self.mom, 2, 100, 5)), [j(w, -1, 1, 0.2) for w in self.weights],
                      j(self.buy_at, -0.2, 0.9, 0.08), j(self.sell_at, -0.9, 0.2, 0.08),
                      j(self.stop_loss, 0.005, 0.4, 0.03), j(self.take_profit, 0.01, 1.0, 0.05),
                      j(self.bet, 0.1, 1.0, 0.1)).fix()

    @staticmethod
    def crossover(a, b, rng):
        """ילד של שני הורים: כל תכונה נלקחת מאחד מהם."""
        def pick(x, y):
            return x if rng.random() < 0.5 else y
        genes = {f.name: pick(getattr(a, f.name), getattr(b, f.name)) for f in fields(Genome)}
        genes["weights"] = [pick(x, y) for x, y in zip(a.weights, b.weights)]
        return Genome(**genes).fix()

    def score(self, m, i):
        """ציון בין -1 ל-1: כמה הבוט "רוצה" להחזיק את המטבע עכשיו."""
        p, slow = m.p[i], m.ma(i, self.slow)
        signals = (clamp((m.ma(i, self.fast) / slow - 1) * 20),
                   (50 - m.rsi[i]) / 50,
                   clamp((p / m.p[i - self.mom] - 1) * 10),
                   clamp((p / slow - 1) * 10))
        total = sum(abs(w) for w in self.weights) or 1.0
        return sum(w * s for w, s in zip(self.weights, signals)) / total

    def describe(self):
        top = sorted(zip(SIGNALS, self.weights), key=lambda sw: -abs(sw[1]))[:2]
        style = " + ".join(SIGNAL_WORDS[s][0 if w > 0 else 1] for s, w in top)
        return (f"{style}; משקיע {self.bet:.0%} מהמזומן, "
                f"סטופ-לוס {self.stop_loss:.0%}, לוקח רווח ב-{self.take_profit:.0%}")


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
    prev_value: float = 0.0
    log_growth: float = 0.0     # כמה הבוט גדל מהמסחר שלו (בלי תשלומים ושכפולים)
    paid: float = 0.0           # כמה הוא שילם לבעלים עד עכשיו
    trades: int = 0
    values: list = field(default_factory=list)

    def value(self, price):
        return self.cash + self.units * price

    def period_return(self, price):
        return self.value(price) / self.period_start - 1 if self.period_start > 0 else -1.0

    def fitness(self, tick):
        """צמיחה ממוצעת לנר. לבוט צעיר אין עדיין מספיק היסטוריה, אז הציון שלו קרוב ל-0."""
        return self.log_growth / max(tick - self.born, 30)

    def step(self, m, i):
        g = self.genome
        if i < max(g.slow, g.mom):
            return
        price = m.p[i]
        if self.units > 0:
            change = price / self.entry - 1
            if change < -g.stop_loss or change > g.take_profit or g.score(m, i) < g.sell_at:
                self.cash += self.units * price * (1 - FEE)
                self.units = 0.0
                self.trades += 1
        elif self.cash > 0.01 and g.score(m, i) > g.buy_at:
            spend = self.cash * g.bet
            self.units = spend * (1 - FEE) / price
            self.cash -= spend
            self.entry = price
            self.trades += 1

    def take(self, amount, price):
        """מוציא כסף מהבוט: קודם מהמזומן, ואם אין מספיק מוכר קצת מהמטבעות."""
        from_cash = min(self.cash, amount)
        self.cash -= from_cash
        units = min(self.units, (amount - from_cash) / (price * (1 - FEE)))
        self.units -= units
        return from_cash + units * price * (1 - FEE)


def thin(points, limit):
    """כשיש יותר מדי נקודות לגרף, משאירים כל נקודה שנייה (ותמיד את האחרונה)."""
    return points[:-1:2] + points[-1:] if len(points) > limit else points


# ---------- האבולוציה ----------

class World:
    def __init__(self, cfg, minutes_per_candle, seed=None, seeds=()):
        self.cfg = cfg
        self.candle = minutes_per_candle
        self.rng = random.Random(seed)
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
        self.selections = 0
        self.history = []             # תמונת מצב אחרי כל נר, בשביל הגרפים
        self.events = []              # מה קרה לאחרונה

    def note(self, text, important=False):
        self.events = (self.events + [[self.now, text]])[-EVENTS:]
        if self.out and (important or self.verbose):
            self.out(text)

    def populate(self):
        assets = self.cfg.assets
        for k in range(self.cfg.start_bots):
            if self.seeds:
                g = self.seeds[k % len(self.seeds)]
                if k >= len(self.seeds) or g.asset not in assets:
                    g = g.mutate(self.rng, assets, 0.5)
            else:
                g = Genome.random(self.rng, assets)
            self.spawn(g)

    def spawn(self, genome, money=None, generation=0):
        if money is None:
            money = self.cfg.start_money
            self.invested += money      # בוט חדש מאפס = הבעלים משקיע עוד כסף
        bot = Bot(self.next_id, genome, self.tick, generation, cash=money, period_start=money, prev_value=money)
        self.next_id += 1
        self.bots.append(bot)
        return bot

    def every(self, text):
        return every(text, self.candle)

    def step(self, markets, i, when):
        """נר אחד: הבוטים סוחרים, ואם הגיע הזמן - משלמים לבעלים ועוברים מבחן."""
        self.now = when.isoformat(timespec="minutes")
        prices = {a: m.p[i] for a, m in markets.items()}
        for bot in self.bots:
            bot.step(markets[bot.genome.asset], i)
        self.tick += 1
        for bot in self.bots:
            v = bot.value(prices[bot.genome.asset])
            bot.log_growth += math.log(max(v, 1e-9) / max(bot.prev_value, 1e-9))

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
            v = bot.value(prices[bot.genome.asset])
            inside += v
            bot.prev_value = v
            bot.values = thin(bot.values + [round(v, 4)], BOT_POINTS)
        self.history = thin(self.history + [{
            "time": self.now, "prices": prices, "alive": len(self.bots), "inside": round(inside, 4),
            "collected": round(self.owner_profit, 4), "invested": round(self.invested, 4)}], CHART_POINTS)

    def pay(self, prices):
        share = self.cfg.pay_percent / 100
        for bot in self.bots:
            p = prices[bot.genome.asset]
            got = bot.take(bot.value(p) * share, p)
            bot.paid += got
            self.owner_profit += got

    def bury_broke(self, prices):
        for bot in list(self.bots):
            p = prices[bot.genome.asset]
            if bot.value(p) < DEATH_LINE:
                self.bots.remove(bot)
                self.deaths += 1
                self.owner_profit += bot.take(bot.value(p), p)
                self.note(f"בוט #{bot.id} ({bot.genome.asset}) נשאר בלי כסף ומת")

    def select(self, prices):
        """המבחן: הפחות טובים מתים, והכסף שלהם הולך לבעלים (או לטובים, לפי ההגדרות).
        כל אחד מהטובים משתכפל ומתחלק בכסף שלו עם השכפול."""
        price = lambda b: prices[b.genome.asset]
        ranked = sorted(self.bots, key=lambda b: b.period_return(price(b)), reverse=True)
        keep = len(ranked) - int(len(ranked) * self.cfg.kill_percent / 100)
        keep = max(1, min(keep, self.cfg.max_bots))
        self.selections += 1
        to_me = self.cfg.losers_money == "me"
        loot = 0.0
        for bot in ranked[keep:]:
            change = bot.period_return(price(bot))
            got = bot.take(bot.value(price(bot)), price(bot))
            loot += got
            self.deaths += 1
            self.note(f"בוט #{bot.id} ({bot.genome.asset}, {change:+.0%}) נכשל במבחן ומת. "
                      f"{got:.2f} ש\"ח עברו {'אליך' if to_me else 'לטובים'}")
        self.bots = ranked[:keep]
        if to_me:
            self.owner_profit += loot
        else:
            for bot in self.bots:
                bot.cash += loot / len(self.bots)
        born = 0
        for parent in ranked[:keep]:
            if len(self.bots) >= self.cfg.max_bots:
                break
            p = price(parent)
            if parent.value(p) < 2 * DEATH_LINE:
                continue
            money = parent.take(parent.value(p) / 2, p)
            child = self.spawn(self.child_genome(parent), money, parent.generation + 1)
            self.clones += 1
            born += 1
            self.note(f"בוט #{parent.id} שוכפל לבוט #{child.id} ({child.genome.asset})")
        for bot in self.bots:
            bot.period_start = bot.value(price(bot))
        self.note(f"מבחן {self.selections}: {len(ranked) - keep} בוטים מתו "
                  f"({loot:.2f} ש\"ח עברו {'אליך' if to_me else 'לטובים'}), "
                  f"{born} שוכפלו. עכשיו יש {len(self.bots)} בוטים", True)

    def child_genome(self, parent):
        r, assets = self.rng.random(), self.cfg.assets
        if r < IMMIGRANT_RATE:
            return Genome.random(self.rng, assets)
        g = parent.genome
        others = [b for b in self.bots if b is not parent]
        if r < IMMIGRANT_RATE + MIX_RATE and others:
            g = Genome.crossover(g, self.rng.choice(others).genome, self.rng)
        return g.mutate(self.rng, assets, 0.5)

    def ranked(self, prices):
        """הבוטים לפי מי שהכי מצליח מאז המבחן האחרון."""
        return sorted(self.bots, key=lambda b: b.period_return(prices[b.genome.asset]), reverse=True)

    def best(self, k):
        return sorted(self.bots, key=lambda b: b.fitness(self.tick), reverse=True)[:k]

    def next_in(self, text):
        """בעוד כמה דקות יקרה האירוע הבא שקורה כל text."""
        n = self.every(text)
        return (n - self.tick % n) * self.candle

    # --- שמירה וטעינה (בשביל המסחר החי, שרץ לאורך ימים) ---

    def to_dict(self):
        skip = ("rng", "seeds", "cfg", "out", "verbose", "bots")
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
        return w


def run_history(times, prices, world, start=0):
    """מריץ את העולם על מחירי עבר. prices: {מטבע: [מחירים]}.
    נרות לפני start משמשים רק לחישוב אינדיקטורים."""
    markets = {a: Market(p) for a, p in prices.items()}
    for i in range(start, len(times)):
        world.step(markets, i, times[i])


def save_brains(path, genomes):
    with open(path, "w") as f:
        json.dump([asdict(g) for g in genomes], f, indent=1)


def load_brains(path):
    with open(path) as f:
        return [Genome(**{"asset": "BTC", **g}) for g in json.load(f)]
