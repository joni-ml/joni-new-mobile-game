"""
הלב של המערכת: נתוני שוק, אינדיקטורים, הבוטים והאבולוציה.

את הקובץ הזה לא מריצים ישירות. משתמשים בו:
  evolution_sim.py - אימון ובדיקה על מחירי עבר
  live.py          - מסחר חי על נייר עם מחירים אמיתיים מהבורסה
"""

import csv
import json
import math
import random
from dataclasses import asdict, dataclass, fields
from datetime import datetime, timedelta

START_MONEY = 5.0       # ש"ח לכל בוט חדש
FEE = 0.001             # 0.1% עמלה לכל קנייה/מכירה
DEATH_LINE = 0.05       # מתחת לזה הבוט "מת"
MAX_BOTS = 64           # תקרה על גודל האוכלוסייה
MAX_WINDOW = 200        # הממוצע הנע הכי ארוך שבוט יכול להשתמש בו
IMMIGRANT_RATE = 0.15   # כמה מהתינוקות נולדים עם אסטרטגיה אקראית לגמרי, כדי להמשיך לחפש רעיונות חדשים


# ---------- נתוני שוק ----------

def load_prices(path):
    """קורא קובץ CSV עם עמודות time,close. מחזיר (זמנים, מחירים)."""
    times, prices = [], []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            times.append(datetime.fromisoformat(row["time"]))
            prices.append(float(row["close"]))
    return times, prices


def synthetic_prices(days, seed):
    """מחירי ביטקוין מדומים (נר לשעה), למקרה שאין קובץ מחירים אמיתי."""
    rng = random.Random(seed)
    price, regime = 250_000.0, 0.0
    start = datetime(2025, 1, 1)
    times, prices = [], []
    for h in range(days * 24):
        if rng.random() < 0.01:                 # מדי פעם השוק משנה "מצב רוח"
            regime = rng.gauss(0, 0.0002)
        price *= math.exp(regime + rng.gauss(0, 0.03 / math.sqrt(24)))
        times.append(start + timedelta(hours=h))
        prices.append(price)
    return times, prices


def rsi_series(prices, n=14):
    """RSI: בין 0 ל-100. נמוך = השוק ירד הרבה לאחרונה, גבוה = עלה הרבה."""
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
    """מחירים + אינדיקטורים שמחושבים פעם אחת מראש, כדי שהסימולציה תרוץ מהר."""

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
    def random(rng):
        fast = rng.randint(2, 30)
        return Genome(fast, fast + rng.randint(5, 120), rng.randint(2, 60),
                      [rng.uniform(-1, 1) for _ in SIGNALS],
                      rng.uniform(0.05, 0.6), rng.uniform(-0.6, 0.0),
                      rng.uniform(0.02, 0.25), rng.uniform(0.03, 0.5), rng.uniform(0.2, 1.0)).fix()

    def fix(self):
        self.fast = int(clamp(self.fast, 2, 50))
        self.slow = int(clamp(self.slow, self.fast + 3, MAX_WINDOW))
        self.mom = int(clamp(self.mom, 2, 100))
        self.sell_at = min(self.sell_at, self.buy_at - 0.05)
        return self

    def mutate(self, rng, strength=1.0):
        """עותק עם שינויים קטנים - כך אסטרטגיות מתפתחות לאט לאט."""
        def j(v, lo, hi, s):
            return clamp(v + rng.gauss(0, s * strength), lo, hi)
        return Genome(round(j(self.fast, 2, 50, 3)), round(j(self.slow, 5, MAX_WINDOW, 10)),
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
        """ציון בין -1 ל-1: כמה הבוט "רוצה" להחזיק ביטקוין עכשיו."""
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
    born_day: int
    generation: int = 0
    cash: float = START_MONEY
    btc: float = 0.0
    entry: float = 0.0
    day_start_value: float = START_MONEY
    week_start_value: float = START_MONEY
    log_growth: float = 0.0     # כמה הבוט גדל מהמסחר שלו (בלי המס היומי והשכפולים)
    trades: int = 0

    def value(self, price):
        return self.cash + self.btc * price

    def fitness(self, day):
        """צמיחה ממוצעת ליום. לבוט צעיר אין עדיין מספיק היסטוריה, אז הציון שלו קרוב ל-0."""
        return self.log_growth / max(day - self.born_day, 14)

    def step(self, m, i):
        g = self.genome
        if i < max(g.slow, g.mom):
            return
        price = m.p[i]
        if self.btc > 0:
            change = price / self.entry - 1
            if change < -g.stop_loss or change > g.take_profit or g.score(m, i) < g.sell_at:
                self.cash += self.btc * price * (1 - FEE)
                self.btc = 0.0
                self.trades += 1
        elif self.cash > 0.01 and g.score(m, i) > g.buy_at:
            spend = self.cash * g.bet
            self.btc = spend * (1 - FEE) / price
            self.cash -= spend
            self.entry = price
            self.trades += 1

    def take(self, amount, price):
        """מוציא כסף מהבוט: קודם מהמזומן, ואם אין מספיק מוכר קצת ביטקוין."""
        from_cash = min(self.cash, amount)
        self.cash -= from_cash
        btc = min(self.btc, (amount - from_cash) / (price * (1 - FEE)))
        self.btc -= btc
        return from_cash + btc * price * (1 - FEE)


# ---------- האבולוציה ----------

class World:
    def __init__(self, daily_cut, seed=None, seeds=()):
        self.rng = random.Random(seed)
        self.daily_cut = daily_cut
        self.seeds = list(seeds)      # אסטרטגיות מאומנות שאפשר להתחיל מהן
        self.bots = []
        self.next_id = 1
        self.day = 0
        self.owner_profit = 0.0
        self.invested = 0.0
        self.deaths = 0
        self.clones = 0

    def populate(self, n):
        for k in range(n):
            if self.seeds:
                seed = self.seeds[k % len(self.seeds)]
                self.spawn(seed if k < len(self.seeds) else seed.mutate(self.rng, 0.5))
            else:
                self.spawn(Genome.random(self.rng))

    def spawn(self, genome, money=None, generation=0):
        bot = Bot(self.next_id, genome, self.day, generation)
        if money is None:
            self.invested += START_MONEY    # בוט חדש = הבעלים משקיע עוד 5 ש"ח
        else:
            bot.cash = bot.day_start_value = bot.week_start_value = money
        self.next_id += 1
        self.bots.append(bot)
        return bot

    def pick_parent(self, candidates):
        """טורניר: בוחרים 3 בוטים אקראיים, והטוב מביניהם הוא ההורה."""
        return max(self.rng.sample(candidates, min(3, len(candidates))),
                   key=lambda b: b.fitness(self.day))

    def newborn(self):
        """בוט חדש במקום בוט שמת: לרוב ילד של המצליחים, לפעמים רעיון חדש לגמרי."""
        adults = [b for b in self.bots if self.day - b.born_day >= 7] or self.bots
        if len(adults) >= 2 and self.rng.random() > IMMIGRANT_RATE:
            mom, dad = self.pick_parent(adults), self.pick_parent(adults)
            child = Genome.crossover(mom.genome, dad.genome, self.rng).mutate(self.rng, 0.5)
            return self.spawn(child, generation=max(mom.generation, dad.generation) + 1)
        return self.spawn(Genome.random(self.rng))

    def end_of_day(self, price, log=None):
        log = log or (lambda *_: None)
        self.day += 1
        for bot in list(self.bots):
            v = bot.value(price)
            bot.log_growth += math.log(max(v, 1e-9) / max(bot.day_start_value, 1e-9))
            self.owner_profit += bot.take(v * self.daily_cut, price)
            if bot.value(price) < DEATH_LINE:
                self.bots.remove(bot)
                self.deaths += 1
                self.owner_profit += bot.take(bot.value(price), price)  # מה שנשאר חוזר לבעלים
                child = self.newborn()
                log(f"יום {self.day}: בוט #{bot.id} מת. נולד בוט #{child.id} (דור {child.generation})")
            bot.day_start_value = bot.value(price)

        if self.day % 7 == 0:
            for bot in list(self.bots):
                v = bot.value(price)
                if v > bot.week_start_value and len(self.bots) < MAX_BOTS:
                    money = bot.take(v / 2, price)
                    child = self.spawn(bot.genome.mutate(self.rng, 0.5), money, bot.generation + 1)
                    self.clones += 1
                    log(f"יום {self.day}: בוט #{bot.id} הצליח ({bot.week_start_value:.2f} -> {v:.2f}) "
                        f"ושוכפל לבוט #{child.id}")
                bot.week_start_value = bot.day_start_value = bot.value(price)

    def best(self, k):
        return sorted(self.bots, key=lambda b: b.fitness(self.day), reverse=True)[:k]

    # --- שמירה וטעינה (בשביל המסחר החי, שרץ לאורך ימים) ---

    def to_dict(self):
        d = {k: v for k, v in vars(self).items() if k not in ("rng", "bots", "seeds")}
        d["bots"] = [asdict(b) for b in self.bots]
        return d

    @staticmethod
    def from_dict(d):
        w = World(d["daily_cut"])
        for k, v in d.items():
            if k != "bots":
                setattr(w, k, v)
        w.bots = [Bot(**{**b, "genome": Genome(**b["genome"])}) for b in d["bots"]]
        return w


def run_history(times, prices, world, start=0, log=None):
    """מריץ את העולם על מחירי עבר. נרות לפני start משמשים רק לחישוב אינדיקטורים."""
    m = Market(prices)
    for i in range(start, len(prices)):
        for bot in world.bots:
            bot.step(m, i)
        if i + 1 == len(prices) or times[i + 1].date() != times[i].date():
            world.end_of_day(prices[i], log)


def save_brains(path, genomes):
    with open(path, "w") as f:
        json.dump([asdict(g) for g in genomes], f, indent=1)


def load_brains(path):
    with open(path) as f:
        return [Genome(**g) for g in json.load(f)]
