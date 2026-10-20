"""
סימולטור "אבולוציה של בוטי מסחר" - מסחר על נייר בלבד (בלי כסף אמיתי).

הרעיון:
  * כל בוט מתחיל עם 5 ש"ח וירטואליים ואסטרטגיה אקראית משלו ("גנום").
  * הבוט סוחר בביטקוין (מחירים מדומים או מקובץ CSV אמיתי), כולל עמלות.
  * בסוף כל יום הבעלים לוקח אחוז מהיתרה של כל בוט ("מס יומי").
  * בוט שיורד מתחת למינימום - מת, ובמקומו נולד בוט חדש עם אסטרטגיה אקראית.
  * בוט שאחרי שבוע עדיין שווה יותר ממה שהתחיל - משוכפל: חצי מהכסף שלו
    עובר לצאצא עם אסטרטגיה דומה (עם מוטציה קטנה).

הרצה:
  python3 evolution_sim.py                   # מחירים מדומים
  python3 evolution_sim.py --csv btc.csv     # מחירים אמיתיים (עמודה close)
  python3 evolution_sim.py --days 90 --seed 7
"""

import argparse
import csv
import math
import random
from dataclasses import dataclass, field

START_MONEY = 5.0          # ש"ח לכל בוט חדש
STEPS_PER_DAY = 24         # נר אחד לשעה
FEE = 0.001                # 0.1% עמלה לכל קנייה/מכירה (בבורסה אמיתית לרוב יותר)
DEATH_LINE = 0.05          # מתחת לזה הבוט "מת"
MAX_BOTS = 64              # תקרה על גודל האוכלוסייה


# ---------- נתוני שוק ----------

def synthetic_prices(days, seed):
    """מחירי ביטקוין מדומים: הליכה אקראית עם תנודתיות דומה לביטקוין."""
    rng = random.Random(seed)
    price, prices = 250_000.0, []
    hourly_vol = 0.03 / math.sqrt(24)  # ~3% תנודתיות יומית
    regime = 0.0
    for _ in range(days * STEPS_PER_DAY):
        if rng.random() < 0.01:                     # מדי פעם השוק משנה "מצב רוח"
            regime = rng.gauss(0, 0.0002)
        price *= math.exp(regime + rng.gauss(0, hourly_vol))
        prices.append(price)
    return prices


def csv_prices(path):
    """קורא מחירי סגירה מקובץ CSV עם עמודה בשם close (נרות של שעה)."""
    with open(path, newline="") as f:
        return [float(row["close"]) for row in csv.DictReader(f)]


# ---------- הבוט ----------

@dataclass
class Genome:
    fast: int          # ממוצע נע קצר
    slow: int          # ממוצע נע ארוך
    rsi_buy: float     # קנה כשה-RSI נמוך מזה
    rsi_sell: float    # מכור כשה-RSI גבוה מזה
    stop_loss: float   # מכור אם ההפסד מהקנייה גדול מזה
    bet: float         # איזה חלק מהמזומן להשקיע בכל קנייה

    @staticmethod
    def random(rng):
        fast = rng.randint(3, 30)
        return Genome(fast, fast + rng.randint(5, 100), rng.uniform(15, 50),
                      rng.uniform(50, 85), rng.uniform(0.01, 0.15), rng.uniform(0.2, 1.0))

    def mutate(self, rng):
        def jitter(v, lo, hi, scale):
            return min(hi, max(lo, v + rng.gauss(0, scale)))
        fast = int(jitter(self.fast, 2, 50, 3))
        return Genome(fast, max(fast + 3, int(jitter(self.slow, 5, 200, 8))),
                      jitter(self.rsi_buy, 5, 50, 4), jitter(self.rsi_sell, 50, 95, 4),
                      jitter(self.stop_loss, 0.005, 0.3, 0.02), jitter(self.bet, 0.1, 1.0, 0.1))


@dataclass
class Bot:
    id: int
    genome: Genome
    born_day: int
    cash: float = START_MONEY
    btc: float = 0.0
    entry: float = 0.0
    week_start_value: float = START_MONEY
    trades: int = 0
    parent: int | None = None

    def value(self, price):
        return self.cash + self.btc * price

    def step(self, prices, i):
        g = self.genome
        if i < g.slow + 1:
            return
        price = prices[i]
        fast_ma = sum(prices[i - g.fast:i]) / g.fast
        slow_ma = sum(prices[i - g.slow:i]) / g.slow
        r = rsi(prices, i)

        if self.btc > 0:
            hit_stop = price < self.entry * (1 - g.stop_loss)
            if hit_stop or (fast_ma < slow_ma and r > g.rsi_sell):
                self.cash += self.btc * price * (1 - FEE)
                self.btc = 0.0
                self.trades += 1
        elif fast_ma > slow_ma and r < g.rsi_buy and self.cash > 0.01:
            spend = self.cash * g.bet
            self.btc = spend * (1 - FEE) / price
            self.cash -= spend
            self.entry = price
            self.trades += 1


def rsi(prices, i, n=14):
    gains = losses = 0.0
    for k in range(i - n, i):
        d = prices[k + 1] - prices[k]
        gains += max(d, 0)
        losses += max(-d, 0)
    return 100.0 if losses == 0 else 100 - 100 / (1 + gains / losses)


# ---------- האבולוציה ----------

@dataclass
class World:
    rng: random.Random
    daily_cut: float
    bots: list = field(default_factory=list)
    next_id: int = 1
    owner_profit: float = 0.0
    invested: float = 0.0
    deaths: int = 0
    clones: int = 0

    def spawn(self, day, genome=None, money=None, parent=None):
        bot = Bot(self.next_id, genome or Genome.random(self.rng), day, parent=parent)
        if money is None:
            self.invested += START_MONEY    # בוט חדש = הבעלים משקיע עוד 5 ש"ח
        else:
            bot.cash = bot.week_start_value = money
        self.next_id += 1
        self.bots.append(bot)
        return bot

    def end_of_day(self, day, price, log):
        for bot in list(self.bots):
            cut = bot.cash * self.daily_cut          # לוקחים רק ממזומן פנוי
            bot.cash -= cut
            self.owner_profit += cut
            if bot.value(price) < DEATH_LINE:
                self.bots.remove(bot)
                self.deaths += 1
                self.owner_profit += bot.value(price)   # מה שנשאר חוזר לבעלים
                log(f"  יום {day}: בוט #{bot.id} מת. נולד בוט חדש במקומו.")
                self.spawn(day)

        if day % 7 == 0:
            for bot in list(self.bots):
                v = bot.value(price)
                if v > bot.week_start_value and len(self.bots) < MAX_BOTS and bot.cash > v / 2:
                    half = v / 2
                    bot.cash -= half
                    child = self.spawn(day, bot.genome.mutate(self.rng), half, bot.id)
                    self.clones += 1
                    log(f"  יום {day}: בוט #{bot.id} הצליח ({bot.week_start_value:.2f} -> {v:.2f}) "
                        f"ושוכפל לבוט #{child.id}")
                bot.week_start_value = bot.value(price)


def run(prices, n_bots, daily_cut, seed, verbose=True):
    log = print if verbose else (lambda *_: None)
    world = World(random.Random(seed), daily_cut)
    for _ in range(n_bots):
        world.spawn(0)

    days = len(prices) // STEPS_PER_DAY
    for day in range(1, days + 1):
        for i in range((day - 1) * STEPS_PER_DAY, day * STEPS_PER_DAY):
            for bot in world.bots:
                bot.step(prices, i)
        world.end_of_day(day, prices[day * STEPS_PER_DAY - 1], log)

    price = prices[days * STEPS_PER_DAY - 1]
    still_in_bots = sum(b.value(price) for b in world.bots)
    net = world.owner_profit + still_in_bots - world.invested
    hold = (price / prices[0] - 1) * 100

    print("\n========== סיכום ==========")
    print(f"ימים: {days} | ביטקוין: {prices[0]:,.0f} -> {price:,.0f} ({hold:+.1f}%)")
    print(f"השקעת בסך הכל:        {world.invested:8.2f} ש\"ח")
    print(f"לקחת מהבוטים:          {world.owner_profit:8.2f} ש\"ח")
    print(f"עדיין בתוך הבוטים:     {still_in_bots:8.2f} ש\"ח")
    print(f"רווח/הפסד נקי:         {net:+8.2f} ש\"ח ({net / world.invested * 100:+.1f}%)")
    print(f"מקרי מוות: {world.deaths} | שכפולים: {world.clones} | בוטים חיים: {len(world.bots)}")
    best = sorted(world.bots, key=lambda b: b.value(price), reverse=True)[:3]
    for b in best:
        print(f"  בוט #{b.id} (נולד ביום {b.born_day}): {b.value(price):.2f} ש\"ח, "
              f"{b.trades} עסקאות, {b.genome}")
    return net


def main():
    p = argparse.ArgumentParser(description="סימולטור אבולוציה של בוטי מסחר (על נייר)")
    p.add_argument("--days", type=int, default=60)
    p.add_argument("--bots", type=int, default=10)
    p.add_argument("--cut", type=float, default=0.01, help="אחוז שהבעלים לוקח כל יום (0.01 = 1%%)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--csv", help="קובץ מחירים אמיתי עם עמודה close")
    p.add_argument("--quiet", action="store_true")
    a = p.parse_args()

    prices = csv_prices(a.csv) if a.csv else synthetic_prices(a.days, a.seed)
    run(prices, a.bots, a.cut, a.seed, verbose=not a.quiet)


if __name__ == "__main__":
    main()
