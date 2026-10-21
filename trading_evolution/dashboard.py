"""
יוצר דף HTML עם חלון לכל בוט, גרף של הכסף שלך וגרף של המטבעות.
פותחים אותו בדפדפן (לחיצה כפולה על הקובץ). עובד גם בלי אינטרנט.
במסחר החי הדף מתרענן לבד כל חצי דקה.
"""

import html
import json
import os
from datetime import datetime

from core import (CLEAR, NET_SIGNALS, PATTERN_AHEAD, PATTERN_LEN, PATTERN_MIN, SCHOOL, SIGNALS, Bot, Genome,
                  brain_fit, brain_importance, brain_think, clamp, fmt_price, human)

MAX_COINS = 7   # כמה מטבעות אפשר להראות בגרף המטבעות (יש 7 צבעים שקל להבדיל ביניהם)


def net_series(world):
    """רווח/הפסד נקי אחרי כל נר: מה שלקחת + מה שנשאר בבוטים - מה שהשקעת."""
    return [round(s["collected"] + s["inside"] - s["invested"], 2) for s in world.history]


def hold_series(world):
    """מה היה קורה אם כל שקל שהשקעת בבוטים היה נקנה במטבעות, שווה בשווה, ונשאר שם."""
    units, last, prev, out = {}, {}, 0.0, []
    for s in world.history:
        last.update(s["prices"])
        new = s["invested"] - prev
        prev = s["invested"]
        for a, p in s["prices"].items():
            units[a] = units.get(a, 0.0) + new / len(s["prices"]) / p
        out.append(round(sum(u * last[a] for a, u in units.items()) - s["invested"], 2))
    return out


def coin_series(world):
    """פי כמה כל מטבע עלה או ירד מאז תחילת התקופה (1 = בלי שינוי, 2 = הוכפל)."""
    assets = list(dict.fromkeys(a for s in world.history for a in s["prices"]))[:MAX_COINS]
    out = []
    for a in assets:
        base, values = None, []
        for s in world.history:
            p = s["prices"].get(a)
            base = base or p
            values.append(round(p / base, 5) if p else None)
        out.append({"name": a, "values": values})
    return out


NAMES = {"trend": "מגמה", "dip": "ירידה חדה (RSI)", "momentum": "תנופה", "stretch": "מרחק מהממוצע",
         "macd": "MACD", "bollinger": "רצועות בולינגר", "channel": "ערוץ 20 נרות",
         "breakout": "פריצה של 55 נרות (שיטת הצבים)", "calm": "כמה השוק סוער", "pattern": "זיכרון דפוסים",
         "fear_greed": "פחד וחמדנות בקריפטו 🌐", "stocks": "הבורסה האמריקאית (S&P 500) 🌐",
         "vix": "מדד הפחד של וול סטריט (VIX) 🌐", "attention": "התעניינות בביטקוין (ויקיפדיה) 🌐",
         "activity": "פעילות ברשת של המטבע 🌐", "valuation": "כמה המטבע יקר (MVRV) 🌐",
         "stablecoins": "סטייבלקוינים: כסף שנכנס לקריפטו 🌐"}


def mood(v):
    return ("פחד קיצוני" if v < 25 else "פחד" if v < 45 else "ניטרלי" if v <= 55 else
            "חמדנות" if v <= 75 else "חמדנות קיצונית")


def net_text(name, r, asset):
    """מה הבוט רואה מהאינטרנט (המספר מאתמול, כי של היום עוד לא פורסם)."""
    v, z = r.get(name + "_raw"), r.get(name)
    if v is None:
        return "אין נתון עדכני מהאתר, אז החוש הזה לא משפיע עכשיו"
    if z is None:
        return "עוד אין מספיק היסטוריה כדי לדעת אם זה הרבה או מעט"
    usual = "גבוה מהרגיל" if z > 0.25 else "נמוך מהרגיל" if z < -0.25 else "בערך כרגיל"
    return {
        "fear_greed": f"המדד עומד על {v:.0f} מתוך 100: {mood(v)} (alternative.me)",
        "stocks": f"S&P 500 = {v:,.0f}; בחודש האחרון הבורסה " +
                  ("עלתה יותר מהרגיל" if z > 0.25 else "נפלה יותר מהרגיל" if z < -0.25 else "זזה כרגיל"),
        "vix": f"VIX = {v:.1f}, {usual} לעומת השנה האחרונה (מעל 30 = פחד גדול בכלכלה)",
        "attention": f"{v:,.0f} כניסות ביום לערך Bitcoin; בחודש האחרון " +
                     ("ההתעניינות עלתה יותר מהרגיל" if z > 0.25 else "ההתעניינות ירדה יותר מהרגיל" if z < -0.25
                      else "ההתעניינות כרגיל"),
        "activity": f"{v:,.0f} כתובות פעילות ביום ברשת של {asset}; בחודש האחרון " +
                    ("הרשת גדלה יותר מהרגיל" if z > 0.25 else "הרשת התכווצה יותר מהרגיל" if z < -0.25 else "בערך כרגיל"),
        "valuation": f"MVRV = {v:.2f} ({usual} לשנה האחרונה; מתחת ל-1 = זול מאוד, מעל 3 = יקר מאוד)",
        "stablecoins": f"יש {v / 1e9:,.1f} מיליארד דולר בסטייבלקוינים (USDT, USDC ועוד); בחודש האחרון " +
                       ("נכנס כסף חדש מהר יותר מהרגיל" if z > 0.25 else "נכנס פחות כסף מהרגיל (או שיצא כסף)"
                        if z < -0.25 else "נכנס כסף בקצב הרגיל"),
    }[name]


def channel_text(x, n):
    if x > 1:
        return f"המחיר פרץ מעל השיא של {n} הנרות האחרונים"
    if x < 0:
        return f"המחיר נפל מתחת לשפל של {n} הנרות האחרונים"
    return f"המחיר נמצא {x:.0%} מהדרך בין השפל לשיא של {n} הנרות האחרונים"


def pattern_text(r):
    if r["pattern"] is None:
        return "עוד אין מספיק נרות כדי לזהות דפוס"
    code, marks = r["pattern"], []
    for _ in range(PATTERN_LEN):
        code, d = divmod(code, 3)
        marks.append("▲▬▼"[2 - d])
    shape = " ".join(reversed(marks))
    text = f"{PATTERN_LEN} הנרות האחרונים: {shape} (▲ עלייה, ▼ ירידה, ▬ כמעט בלי שינוי). "
    if r["seen"] < PATTERN_MIN:
        return text + f"ראה את הדפוס הזה רק {r['seen']} פעמים, אז עוד לא סומך עליו"
    return (text + f"ראה אותו {r['seen']} פעמים, ואחריו המחיר {'עלה' if r['ahead'] >= 0 else 'ירד'} "
            f"בממוצע ב-{abs(r['ahead']):.1%} ב-{PATTERN_AHEAD} הנרות הבאים")


def hold_rules(b, score):
    """מצב "להחזיק": מחזיקים כמה שיותר, ובורחים רק כשיש סימני סכנה."""
    g, clear = b.genome, b.genome.sell_at + CLEAR
    if b.units > 0:
        drop = b.price / b.peak - 1 if b.peak else 0.0
        status = (f"מחזיק {g.asset} (קנה ב-{fmt_price(b.entry)}, עכשיו {fmt_price(b.price)}). "
                  f"ממשיך להחזיק כל עוד אין סכנה")
        rules = [[f"בורח אם הציון יורד מתחת לקו הסכנה {g.sell_at:+.2f}", f"עכשיו {score:+.2f}"],
                 [f"בורח אם המחיר יורד {g.stop_loss:.0%} מהשיא מאז שקנה ({fmt_price(b.peak)})",
                  f"עכשיו {drop:+.1%}"],
                 ["לא מוכר בגלל רווח - המטרה היא להחזיק כמה שיותר זמן", ""]]
    else:
        status = (f"ברח מסכנה. מחכה עוד {b.wait} נרות לפני שיקנה שוב" if b.wait else
                  f"במזומן. יקנה ברגע שאין סימני סכנה (ציון מעל {clear:+.2f})" if b.cash > 0.01 else
                  "אין לו מספיק מזומן כדי לקנות")
        rules = [[f"קונה {g.asset} כשאין סימני סכנה: הציון מעל {clear:+.2f}, ב-{g.bet:.0%} מהמזומן שלו",
                  f"עכשיו {score:+.2f}"],
                 [f"אחרי שבורח, מחכה {g.cooldown} נרות לפני שקונה שוב", ""],
                 [f"אחרי שקנה: מחזיק, ובורח רק אם הציון יורד מתחת ל-{g.sell_at:+.2f} "
                  f"או שהמחיר יורד {g.stop_loss:.0%} מהשיא", ""]]
    return status, rules, [round(clear, 3), "חוזר לקנות מעל " + f"{clear:+.2f}", "סכנה: בורח מתחת " + f"{g.sell_at:+.2f}"]


def mind_rows(b, allowed):
    """במוח הלומד: כמה כל סימן משנה את הניחוש עכשיו (בודקים מה המוח היה מנחש בלי הסימן הזה),
    וכמה הסימן חשוב למוח באופן כללי (1 = הכי חשוב מבין הסימנים המותרים)."""
    brain_fit(b.mind, len(SIGNALS))
    x = Bot.inputs(b.readings, allowed)
    full = brain_think(b.mind, x)[0]
    imp = brain_importance(b.mind, [e[0] for e in b.memory] or [x])
    top = max((imp[j] for j, n in enumerate(SIGNALS) if n in allowed), default=0.0) or 1.0
    out = {}
    for j, name in enumerate(SIGNALS):
        if name in allowed:
            without = brain_think(b.mind, x[:j] + [0.0] + x[j + 1:])[0]
            out[name] = (round(imp[j] / top, 2), full - without)
    return out


def accuracy(b):
    return round(100 * sum(b.hits) / len(b.hits)) if len(b.hits) >= 30 else None


def brain(b, allowed, goal="trade", learning=False, candle=1440):
    """מה הבוט חישב בנר האחרון, כדי להבין למה הוא קונה, מוכר או מחכה."""
    g, r = b.genome, b.readings
    if not isinstance(r, dict) or not r:
        return None
    sees = {
        "trend": f"הממוצע של {g.fast} הנרות האחרונים {'גבוה' if r['trend'] >= 0 else 'נמוך'} "
                 f"ב-{abs(r['trend']):.1%} מהממוצע של {g.slow} נרות",
        "dip": f"RSI = {r['rsi']:.0f} (מתחת ל-30: ירד הרבה לאחרונה, מעל 70: עלה הרבה)",
        "momentum": f"המחיר {'עלה' if r['mom'] >= 0 else 'ירד'} ב-{abs(r['mom']):.1%} ב-{g.mom} הנרות האחרונים",
        "stretch": f"המחיר {'גבוה' if r['stretch'] >= 0 else 'נמוך'} ב-{abs(r['stretch']):.1%} "
                   f"מהממוצע של {g.slow} נרות",
        "macd": "קו ה-MACD (12/26/9) " + ("מעל קו האות שלו: התנופה מתחזקת" if r["macd"] >= 0
                                          else "מתחת לקו האות שלו: התנופה נחלשת"),
        "bollinger": f"המחיר {abs(r['z']):.1f} סטיות תקן {'מעל ' if r['z'] >= 0 else 'מתחת ל'}ממוצע {g.slow} הנרות",
        "channel": channel_text(r["ch20"], 20),
        "breakout": channel_text(r["ch55"], 55),
        "calm": f"השוק זז עכשיו פי {r['vol']:.1f} ממה שהוא זז בדרך כלל",
        "pattern": pattern_text(r),
        **{n: net_text(n, r, g.asset) for n in NET_SIGNALS},
    }
    learning = learning and b.mind is not None and b.feel is not None
    parts = g.parts(Genome.signals(r), allowed)
    if learning:   # כל סימן דוחף את הציון דרך הנוסחה ודרך המוח, לפי כמה שהבוט מקשיב לכל אחד
        mr, ear = mind_rows(b, allowed), g.listen
        rows = [{"name": NAMES[s], "sees": sees[s], "weight": round(w, 2), "imp": mr[s][0],
                 "part": round(clamp((1 - ear) * p + ear * mr[s][1]), 3)}
                for s, w, p in zip(SIGNALS, g.weights, parts) if s in allowed]
    else:
        rows = [{"name": NAMES[s], "sees": sees[s], "weight": round(w, 2), "part": round(p, 3)}
                for s, w, p in zip(SIGNALS, g.weights, parts) if s in allowed]
    score = b.score
    mind = {"learning": True, "lessons": b.lessons, "acc": accuracy(b), "acc_n": len(b.hits),
            "accuracy": b.accuracy, "horizon": g.horizon, "listen": round(g.listen, 2),
            "formula": round(sum(parts), 3), "guess": round(b.guess, 3), "feel": round(b.feel, 3),
            "school": human(SCHOOL * candle)} if learning else {"learning": False}
    if goal == "hold":
        status, rules, (buy, buy_label, sell_label) = hold_rules(b, score)
        return {"rows": rows, "score": round(score, 3), "buy": buy, "sell": round(g.sell_at, 3),
                "buy_label": buy_label, "sell_label": sell_label, **mind,
                "status": status, "rules": rules, "last": b.last, "scores": b.scores}
    if b.units > 0:
        change = b.price / b.entry - 1
        status = f"מחזיק {g.asset} שקנה ב-{fmt_price(b.entry)}. עכשיו {fmt_price(b.price)} ({change:+.1%})"
        rules = [[f"מוכר אם הציון יורד מתחת לסף {g.sell_at:+.2f}", f"עכשיו {score:+.2f}"],
                 [f"מוכר אם המחיר ירד {g.stop_loss:.0%} מהקנייה (סטופ-לוס)", f"עכשיו {change:+.1%}"],
                 [f"מוכר אם המחיר עלה {g.take_profit:.0%} מהקנייה (לוקח רווח)", f"עכשיו {change:+.1%}"]]
    else:
        status = (f"במזומן. מחכה שהציון יעלה מעל הסף {g.buy_at:+.2f}" if b.cash > 0.01
                  else "אין לו מספיק מזומן כדי לקנות")
        rules = [[f"קונה {g.asset} אם הציון עולה מעל הסף {g.buy_at:+.2f}, ב-{g.bet:.0%} מהמזומן שלו",
                  f"עכשיו {score:+.2f}"],
                 [f"אחרי שקנה: מוכר אם הציון יורד מתחת לסף {g.sell_at:+.2f}, "
                  f"אם המחיר ירד {g.stop_loss:.0%} או אם עלה {g.take_profit:.0%}", ""]]
    return {"rows": rows, "score": round(score, 3), "buy": round(g.buy_at, 3), "sell": round(g.sell_at, 3),
            "buy_label": f"קונה מעל {g.buy_at:+.2f}", "sell_label": f"מוכר מתחת {g.sell_at:+.2f}", **mind,
            "status": status, "rules": rules, "last": b.last, "scores": b.scores}


def bot_cards(world):
    prices = world.history[-1]["prices"]
    cards = []
    for rank, b in enumerate(world.ranked(prices), 1):
        p = prices[b.genome.asset]
        cards.append({
            "rank": rank, "id": b.id, "asset": b.genome.asset, "gen": b.generation,
            "value": round(b.value(p), 2), "change": round(b.period_return(p) * 100, 1),
            "paid": round(b.paid, 2), "holding": b.units > 0, "trades": b.trades,
            "age": human((world.tick - b.born) * world.candle),
            "desc": b.genome.describe(world.cfg.signals, world.cfg.goal, world.cfg.brain == "learning"),
            "acc": accuracy(b) if world.cfg.brain == "learning" else None,
            "invested": round(100 * b.held / b.seen) if b.seen else 0,
            "clone": b.genome.clone_rule(world.cfg.start_money),
            "brain": brain(b, world.cfg.signals, world.cfg.goal, world.cfg.brain == "learning", world.candle),
            "spark": b.values,
        })
    return cards


def write_dashboard(path, title, runs, cfg, live=False):
    """runs: רשימה של (שם, עולם). הראשון הוא הראשי: ממנו המספרים והחלונות של הבוטים."""
    data = build(title, runs, cfg, live)
    if data:
        write_page(path, title, data)


def write_replay(path, title, frames):
    """דף שמנגן את הבוטים כמו סרטון. frames: רשימה של מה ש-build החזיר, מהישן לחדש.
    הקווים בגרפים נשמרים פעם אחת (מהתמונה האחרונה), וכל תמונה שומרת רק כמה נקודות מהם להראות."""
    full = {k: frames[-1][k] for k in ("times", "money", "coins")}
    keep = ("title", "rules", "tiles", "bots", "events", "updated")
    write_page(path, title, {**frames[-1], "refresh": 0},
               {"full": full, "frames": [{**{k: f[k] for k in keep}, "n": len(f["times"])} for f in frames]})


def write_page(path, title, data, replay=None):
    dump = lambda x: json.dumps(x, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    page = (TEMPLATE.replace("__TITLE__", html.escape(title)).replace("__DATA__", dump(data))
            .replace("__REPLAY__", dump(replay)))
    with open(path + ".tmp", "w", encoding="utf-8") as f:
        f.write(page)
    os.replace(path + ".tmp", path)   # כדי שהדפדפן לא יקרא חצי קובץ באמצע כתיבה


def build(title, runs, cfg, live=False):
    """כל מה שהדף צריך כדי להראות את המצב עכשיו (או None אם עוד אין כלום)."""
    world = runs[0][1]
    h = world.history
    if not h:
        return None
    last = h[-1]
    pay, select = world.every(cfg.pay_every) * world.candle, world.every(cfg.select_every) * world.candle
    money = [{"name": runs[0][0], "values": net_series(world), "color": "--s1"},
             {"name": "רק לקנות את המטבעות ולחכות", "values": hold_series(world), "color": "--hold"}]
    money += [{"name": name, "values": net_series(w), "color": "--s7"} for name, w in runs[1:]]
    tiles = [
        ["רווח/הפסד נקי", f"{money[0]['values'][-1]:+,.2f} ₪"],
        ["לקחת מהבוטים", f"{last['collected']:,.2f} ₪"],
        ["השקעת", f"{last['invested']:,.2f} ₪"],
        ["נשאר בבוטים", f"{last['inside']:,.2f} ₪"],
        ["בוטים עכשיו / מקסימום", f"{last['alive']} / {cfg.max_bots}"],
        ["מתו / שוכפלו", f"{world.deaths} / {world.clones}"],
        ["בחרו לא להשתכפל", f"{world.declined}"],
        ["נולדו במקומות ריקים", f"{world.refilled}"],
    ]
    if live:
        tiles += [["התשלום הבא בעוד", human(world.next_in(cfg.pay_every))],
                  ["המבחן הבא בעוד", human(world.next_in(cfg.select_every))]]
    return {
        "title": title,
        "refresh": 30 if live else 0,
        "updated": datetime.now().strftime("%H:%M:%S"),
        "rules": ("המטרה: להחזיק כמה שיותר זמן, ולברוח רק כשרואים סכנה · " if cfg.goal == "hold" else "") +
                 f"כל {human(pay)} כל בוט משלם לך {cfg.pay_percent:g}% מהכסף שלו · "
                 f"כל {human(select)} יש מבחן: {cfg.kill_percent:g}% הכי פחות טובים מתים, "
                 f"והטובים בוחרים אם להשתכפל · עד {cfg.max_bots} בוטים",
        "times": [s["time"] for s in h],
        "money": money,
        "coins": coin_series(world),
        "tiles": tiles,
        "bots": bot_cards(world),
        "events": world.events[::-1][:12],
    }


TEMPLATE = r"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
:root {
  color-scheme: light;
  --page: #f9f9f7; --surface: #fcfcfb; --ink: #0b0b0b; --ink2: #52514e; --muted: #898781;
  --grid: #e1e0d9; --axis: #c3c2b7; --ring: rgba(11,11,11,0.10); --up: #006300; --down: #d03b3b;
  --hold: #898781;
  --s1: #2a78d6; --s2: #eb6834; --s3: #1baf7a; --s4: #eda100; --s5: #e87ba4; --s6: #008300; --s7: #6250d6; --s8: #e34948;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --page: #0d0d0d; --surface: #1a1a19; --ink: #f0efec; --ink2: #c3c2b7; --muted: #898781;
    --grid: #2c2c2a; --axis: #383835; --ring: rgba(255,255,255,0.10); --up: #0ca30c; --down: #d03b3b;
    --s1: #3987e5; --s2: #d95926; --s3: #199e70; --s4: #c98500; --s5: #d55181; --s6: #008300; --s7: #9085e9; --s8: #e66767;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --page: #0d0d0d; --surface: #1a1a19; --ink: #f0efec; --ink2: #c3c2b7; --muted: #898781;
  --grid: #2c2c2a; --axis: #383835; --ring: rgba(255,255,255,0.10); --up: #0ca30c; --down: #d03b3b;
  --s1: #3987e5; --s2: #d95926; --s3: #199e70; --s4: #c98500; --s5: #d55181; --s6: #008300; --s7: #9085e9; --s8: #e66767;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--page); color: var(--ink);
       font: 15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width: 1100px; margin: 0 auto; padding: 24px 16px 48px; }
h1 { font-size: 22px; margin: 0 0 4px; }
h2 { font-size: 16px; margin: 0 0 2px; }
.rules { color: var(--ink2); font-size: 14px; margin: 0 0 16px; }
.sub { color: var(--ink2); margin: 0 0 12px; font-size: 14px; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 20px; }
.tile, .card, .bot { background: var(--surface); border-radius: 12px; box-shadow: 0 0 0 1px var(--ring); }
.tile { padding: 12px 14px; }
.tile .label { color: var(--ink2); font-size: 13px; }
.tile .value { font-size: 20px; font-weight: 600; white-space: nowrap; }
.tile.hero .value { font-size: 28px; line-height: 1.2; }
.ltr { direction: ltr; unicode-bidi: isolate; }
.card { padding: 16px; margin-bottom: 20px; position: relative; }
.grid2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 0 20px; }
@media (max-width: 480px) { .grid2 { grid-template-columns: 1fr; } }
.legend { display: flex; flex-wrap: wrap; gap: 6px 18px; margin: 4px 0 8px; font-size: 13px; color: var(--ink2); }
.legend span::before { content: ""; display: inline-block; width: 16px; height: 2px; border-radius: 1px;
                       background: var(--c); vertical-align: middle; margin-left: 6px; }
.plot { direction: ltr; position: relative; }
.plot svg { display: block; width: 100%; overflow: visible; }
.plot svg:focus-visible { outline: 2px solid var(--s1); outline-offset: 4px; border-radius: 4px; }
.tip { position: absolute; pointer-events: none; background: var(--surface); color: var(--ink);
       box-shadow: 0 0 0 1px var(--ring), 0 4px 12px rgba(0,0,0,.12); border-radius: 8px;
       padding: 8px 10px; font-size: 13px; white-space: nowrap; display: none; direction: rtl; z-index: 2; }
.tip .date { color: var(--ink2); margin-bottom: 4px; }
.tip .row { display: flex; align-items: center; gap: 8px; }
.tip .row b { direction: ltr; }
.tip .key { width: 12px; height: 2px; border-radius: 1px; }
.tip .name { color: var(--ink2); }

.bots { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 12px; margin-bottom: 20px; }
.bot { padding: 12px 14px; display: flex; flex-direction: column; gap: 4px; }
.bot .head { display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: var(--ink2); }
.bot .head b { color: var(--ink); font-size: 15px; }
.chip { display: inline-flex; align-items: center; gap: 6px; font-size: 13px; color: var(--ink); font-weight: 600; }
.chip::before { content: ""; width: 8px; height: 8px; border-radius: 50%; background: var(--c); }
.bot .money { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 0 8px; }
.bot .money .v { font-size: 22px; font-weight: 600; white-space: nowrap; }
.change { font-size: 13px; font-weight: 600; white-space: nowrap; }
.change.up { color: var(--up); } .change.down { color: var(--down); }
.bot svg { width: 100%; height: 40px; display: block; direction: ltr; }
.bot .meta { font-size: 12px; color: var(--ink2); }
.bot .desc { font-size: 12px; color: var(--muted); }
.brain { margin-top: 6px; border-top: 1px solid var(--grid); padding-top: 6px; font-size: 13px; }
.brain summary { cursor: pointer; font-weight: 600; }
.brain .status { margin: 8px 0 0; font-weight: 600; }
.brain .lbl { color: var(--ink2); font-size: 12px; font-weight: 600; margin: 12px 0 2px; }
.brain .desc { margin: 2px 0; }
.bot svg.score { height: auto; aspect-ratio: 220 / 90; }
.sig { margin: 8px 0; }
.sigtop { display: flex; justify-content: space-between; gap: 8px; }
.sigtop.total { border-top: 1px solid var(--grid); padding-top: 6px; margin-top: 6px; }
.bar { position: relative; height: 6px; background: var(--grid); border-radius: 3px; direction: ltr; margin-top: 4px; }
.bar::after { content: ""; position: absolute; left: 50%; top: -2px; bottom: -2px; width: 1px; background: var(--axis); }
.bar i { position: absolute; top: 0; bottom: 0; border-radius: 3px; }
.rules { margin: 0; padding: 0 16px 0 0; }
.rules li { margin: 4px 0; }
.rules .now { color: var(--ink2); margin-right: 6px; white-space: nowrap; }
.events { list-style: none; margin: 0; padding: 0; font-size: 14px; }
.events li { padding: 6px 0; border-bottom: 1px solid var(--grid); display: flex; gap: 12px; }
.events li:last-child { border-bottom: 0; }
.events time { color: var(--muted); white-space: nowrap; font-variant-numeric: tabular-nums; }
.note { color: var(--muted); font-size: 13px; }
.player { position: sticky; top: 0; z-index: 5; display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
          background: var(--surface); box-shadow: 0 0 0 1px var(--ring); border-radius: 12px; padding: 8px 12px; margin-bottom: 16px; }
.player button, .player select { font: inherit; color: var(--ink); background: var(--page); border: 1px solid var(--axis);
                                 border-radius: 8px; padding: 4px 10px; cursor: pointer; }
.player input[type=range] { flex: 1; min-width: 120px; direction: ltr; }
.player .when { font-weight: 600; font-variant-numeric: tabular-nums; }
</style>
</head>
<body>
<main>
  <div class="player" id="player" hidden>
    <button id="play" type="button" aria-label="נגן או עצור">⏸ עצור</button>
    <span class="when" id="when"></span>
    <input type="range" id="frame" min="0" value="0" aria-label="איזה יום להראות">
    <select id="speed" aria-label="מהירות"><option value="1">רגיל</option><option value="2">מהר</option><option value="4">מהר מאוד</option></select>
  </div>
  <h1 id="title">__TITLE__</h1>
  <p class="rules" id="rules"></p>
  <div class="tiles" id="tiles"></div>

  <div class="grid2">
    <section class="card">
      <h2>הכסף שלך לאורך הזמן</h2>
      <p class="sub">רווח או הפסד נקי בשקלים: מה שלקחת, ועוד מה שנשאר בבוטים, פחות מה שהשקעת</p>
      <div class="legend" id="moneyLegend"></div>
      <div class="plot" id="money"></div>
    </section>
    <section class="card">
      <h2>המטבעות</h2>
      <p class="sub" id="coinSub">כמה כל מטבע עלה או ירד מאז ההתחלה</p>
      <div class="legend" id="coinLegend"></div>
      <div class="plot" id="coins"></div>
    </section>
  </div>

  <h2>הבוטים</h2>
  <p class="sub">חלון לכל בוט, לפי הסדר: מי שהכי מצליח מאז המבחן האחרון נמצא ראשון</p>
  <div class="bots" id="bots"></div>

  <section class="card">
    <h2>מה קרה לאחרונה</h2>
    <ul class="events" id="events"></ul>
  </section>
  <p class="note" id="updated"></p>
</main>

<script>
let DATA = __DATA__;
const REPLAY = __REPLAY__;   // בדף של הקלטה: כל התמונות, אחת אחרי השנייה
const COIN_COLORS = ["--s2", "--s3", "--s4", "--s5", "--s6", "--s7", "--s8"];
let coinColor = {}, T = [], SPAN = 0, DAILY = true;
function prepare() {
  coinColor = {};
  DATA.coins.forEach((c, i) => { c.color = COIN_COLORS[i]; coinColor[c.name] = c.color; });
  T = DATA.times.map(s => new Date(s + "Z"));
  SPAN = (T[T.length - 1] - T[0]) / 864e5;   // ימים
  DAILY = T.every(t => t.getUTCHours() === 0 && t.getUTCMinutes() === 0);
}

function css(name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }
function el(tag, attrs, parent) {
  const svgTags = ["svg", "path", "line", "circle", "text", "rect"];
  const e = svgTags.includes(tag) ? document.createElementNS("http://www.w3.org/2000/svg", tag) : document.createElement(tag);
  for (const k in attrs || {}) e.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(e);
  return e;
}
const pad = n => String(n).padStart(2, "0");
function fmtTime(t, full) {
  const d = `${pad(t.getDate())}/${pad(t.getMonth() + 1)}`;
  if (DAILY) return full ? `${d}/${t.getFullYear()}` : d;
  return `${full ? d + " " : ""}${pad(t.getHours())}:${pad(t.getMinutes())}`;
}
function money(v) {
  const a = Math.abs(v), s = v > 0 ? "+" : v < 0 ? "−" : "";
  return s + (a >= 1000 ? Math.round(a).toLocaleString("en-US") : a.toFixed(2)) + " ₪";
}
function pct(v) {
  const a = Math.abs(v);
  return a < 0.05 ? "0%" : (v > 0 ? "+" : "−") + a.toFixed(a < 10 ? 1 : 0) + "%";
}
function compact(v) {
  const a = Math.abs(v), s = v < 0 ? "−" : "";
  if (a >= 1e6) return s + +(a / 1e6).toFixed(1) + "M";
  if (a >= 1e3) return s + +(a / 1e3).toFixed(1) + "K";
  return s + +a.toFixed(a < 10 ? 1 : 0);
}
function logTicks(lo, hi) {
  const out = [];
  for (let k = Math.floor(Math.log10(lo)); k <= Math.ceil(Math.log10(hi)); k++)
    for (const m of [1, 2, 5]) { const v = +(m * Math.pow(10, k)).toPrecision(3); if (v >= lo && v <= hi) out.push(v); }
  return out.length > 7 ? out.filter(v => String(v).replace(/^0\.0*/, "")[0] === "1") : out;
}
const ratio = v => v >= 2 ? "×" + compact(v) : pct((v - 1) * 100);
function niceTicks(lo, hi, n) {
  const raw = (hi - lo) / n, mag = Math.pow(10, Math.floor(Math.log10(raw || 1)));
  const step = [1, 2, 5, 10].map(x => x * mag).find(x => x >= raw);
  const out = [];
  for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) out.push(+v.toFixed(10));
  return out;
}

function lineChart(box, series, opts) {
  box.textContent = "";
  const W = box.clientWidth, H = W < 500 ? 220 : 260, n = T.length;
  const m = { l: 52, r: opts.endLabels ? 64 : 16, t: 10, b: 26 };
  const base = opts.base || 0;   // הקו המודגש: 0 שקלים, או "בלי שינוי" במטבעות
  const all = series.flatMap(s => s.values).filter(v => v !== null);
  let lo = Math.min(base, ...all), hi = Math.max(base, ...all);
  if (lo === hi) { lo -= 1; hi += 1; }
  const log = opts.log && lo > 0 && hi / lo > 20;
  const f = log ? Math.log10 : v => v;
  const ticks = log ? logTicks(lo, hi) : niceTicks(lo, hi, 4);
  if (!log) { lo = Math.min(lo, ticks[0]); hi = Math.max(hi, ticks[ticks.length - 1]); }
  const x = i => m.l + (n === 1 ? 0 : i / (n - 1)) * (W - m.l - m.r);
  const y = v => m.t + (1 - (f(v) - f(lo)) / (f(hi) - f(lo))) * (H - m.t - m.b);
  const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, height: H, tabindex: 0, role: "img", "aria-label": opts.label }, box);
  for (const t of ticks) {
    el("line", { x1: m.l, x2: W - m.r, y1: y(t), y2: y(t), stroke: css(t === base ? "--axis" : "--grid"),
                 "stroke-width": 1, "shape-rendering": "crispEdges" }, svg);
    el("text", { x: m.l - 8, y: y(t) + 4, "text-anchor": "end", "font-size": 11, fill: css("--muted") }, svg)
      .textContent = opts.tick(t);
  }
  // ציר הזמן: תחילת כל שנה בתקופות ארוכות, אחרת תאריכים או שעות במרווחים קבועים
  const step = Math.max(1, Math.round(n / (W < 500 ? 3 : 5)));
  let lastX = -Infinity;
  for (let i = 0; i < n; i++) {
    const due = SPAN > 730 ? i > 0 && T[i].getFullYear() !== T[i - 1].getFullYear() : i % step === 0;
    if (!due || x(i) - lastX < 44 || x(i) > W - m.r - 14) continue;
    lastX = x(i);
    el("text", { x: x(i), y: H - 6, "text-anchor": "middle", "font-size": 11, fill: css("--muted") }, svg)
      .textContent = SPAN > 730 ? T[i].getFullYear() : fmtTime(T[i], false);
  }
  for (const s of series) {
    let d = "", pen = false;
    s.values.forEach((v, i) => {
      if (v === null) { pen = false; return; }
      d += (pen ? "L" : "M") + x(i).toFixed(1) + "," + y(v).toFixed(1);
      pen = true;
    });
    el("path", { d, fill: "none", stroke: css(s.color), "stroke-width": 2, "stroke-linejoin": "round",
                 "stroke-linecap": "round" }, svg);
  }
  // נקודה בסוף כל קו, וערך לידה אם הערכים לא עולים אחד על השני
  const ends = series.filter(s => s.values[n - 1] !== null).map(s => ({ s, v: s.values[n - 1] }))
                     .sort((a, b) => y(a.v) - y(b.v));
  const roomy = ends.every((e, i) => i === 0 || y(e.v) - y(ends[i - 1].v) >= 14);
  for (const e of ends) {
    el("circle", { cx: x(n - 1), cy: y(e.v), r: 4, fill: css(e.s.color), stroke: css("--surface"), "stroke-width": 2 }, svg);
    if (opts.endLabels && roomy)
      el("text", { x: x(n - 1) + 8, y: y(e.v) + 4, "font-size": 12, fill: css("--ink2") }, svg).textContent = opts.fmt(e.v);
  }
  // שכבת ריחוף: קו אנכי + חלונית עם כל הערכים באותו רגע
  const cross = el("line", { y1: m.t, y2: H - m.b, stroke: css("--axis"), "stroke-width": 1, visibility: "hidden" }, svg);
  const dots = series.map(s => el("circle", { r: 4, fill: css(s.color), stroke: css("--surface"), "stroke-width": 2,
                                              visibility: "hidden" }, svg));
  const tip = el("div", { class: "tip" }, box);
  const hit = el("rect", { x: m.l, y: 0, width: Math.max(1, W - m.l - m.r), height: H, fill: "transparent" }, svg);
  let cur = n - 1;
  function show(i) {
    cur = Math.max(0, Math.min(n - 1, i));
    cross.setAttribute("x1", x(cur)); cross.setAttribute("x2", x(cur)); cross.setAttribute("visibility", "visible");
    tip.textContent = "";
    el("div", { class: "date" }, tip).textContent = fmtTime(T[cur], true);
    series.forEach((s, k) => {
      const v = s.values[cur];
      dots[k].setAttribute("visibility", v === null ? "hidden" : "visible");
      if (v !== null) { dots[k].setAttribute("cx", x(cur)); dots[k].setAttribute("cy", y(v)); }
    });
    series.filter(s => s.values[cur] !== null).sort((a, b) => b.values[cur] - a.values[cur]).forEach(s => {
      const row = el("div", { class: "row" }, tip);
      el("span", { class: "key", style: `background:${css(s.color)}` }, row);
      el("b", {}, row).textContent = opts.fmt(s.values[cur]);
      el("span", { class: "name" }, row).textContent = s.name;
    });
    tip.style.display = "block";
    const tw = tip.offsetWidth, px = x(cur);
    tip.style.left = Math.max(0, px + 12 + tw > W ? px - 12 - tw : px + 12) + "px";
    tip.style.top = "8px";
  }
  function hide() {
    cross.setAttribute("visibility", "hidden");
    dots.forEach(d => d.setAttribute("visibility", "hidden"));
    tip.style.display = "none";
  }
  hit.addEventListener("pointermove", ev => {
    const r = svg.getBoundingClientRect(), px = (ev.clientX - r.left) * W / r.width;
    show(Math.round((px - m.l) / (W - m.l - m.r) * (n - 1)));
  });
  hit.addEventListener("pointerleave", hide);
  svg.addEventListener("focus", () => show(cur));
  svg.addEventListener("blur", hide);
  svg.addEventListener("keydown", ev => {
    if (ev.key === "ArrowRight") show(cur + 1); else if (ev.key === "ArrowLeft") show(cur - 1); else return;
    ev.preventDefault();
  });
}

function legend(box, series) {
  box.textContent = "";
  for (const s of series) el("span", { style: `--c:var(${s.color})` }, box).textContent = s.name;
}

function sparkline(svg, values, color) {
  const W = 200, H = 40, n = values.length;
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  svg.setAttribute("preserveAspectRatio", "none");
  if (n < 2) return;
  const lo = Math.min(...values), hi = Math.max(...values), span = hi - lo || 1;
  const d = values.map((v, i) => (i ? "L" : "M") + (i / (n - 1) * W).toFixed(1) + "," +
                                 (H - 3 - (v - lo) / span * (H - 6)).toFixed(1)).join("");
  el("path", { d, fill: "none", stroke: css(color), "stroke-width": 2, "vector-effect": "non-scaling-stroke",
               "stroke-linejoin": "round" }, svg);
}

let openBots = new Set();
try { openBots = new Set(JSON.parse(sessionStorage.getItem("openBots") || "[]")); } catch (e) {}
function saveOpen() { try { sessionStorage.setItem("openBots", JSON.stringify([...openBots])); } catch (e) {} }
const signed = v => Math.abs(v) < 0.005 ? "0.00" : (v > 0 ? "+" : "−") + Math.abs(v).toFixed(2);
// מספר עם סימן (+5%, -0.26) בתוך משפט בעברית: מבודדים אותו, אחרת הסימן קופץ לצד השני של המספר
const bidi = t => t.replace(/(^|[\s(])([+\-−]\d+(?:[.,]\d+)*%?)/g, "$1\u2066$2\u2069");

// גרף הציון של בוט: מעל הקו העליון הוא קונה, מתחת לקו התחתון הוא מוכר
function scoreChart(svg, x, color) {
  const W = 220, H = 90, vals = x.scores, n = vals.length;
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  const seen = vals.filter(v => v !== null).concat([x.buy, x.sell, x.score]);
  const lo = Math.max(-1, Math.min(...seen) - 0.1), hi = Math.min(1, Math.max(...seen) + 0.1);
  const y = v => 10 + (1 - (v - lo) / (hi - lo)) * (H - 20);
  if (lo < 0 && hi > 0) el("line", { x1: 0, x2: W, y1: y(0), y2: y(0), stroke: css("--grid"), "stroke-width": 1 }, svg);
  const lines = [[x.buy, "--up", x.buy_label, -3], [x.sell, "--down", x.sell_label, 10]];
  for (const [v, c] of lines)
    el("line", { x1: 0, x2: W, y1: y(v), y2: y(v), stroke: css(c), "stroke-width": 1 }, svg);
  let d = "", pen = false;
  vals.forEach((v, i) => {
    if (v === null) { pen = false; return; }
    d += (pen ? "L" : "M") + (n < 2 ? 0 : i / (n - 1) * W).toFixed(1) + "," + y(v).toFixed(1);
    pen = true;
  });
  el("path", { d, fill: "none", stroke: css(color), "stroke-width": 1.5, "stroke-linejoin": "round" }, svg);
  el("circle", { cx: W, cy: y(x.score), r: 3, fill: css(color), stroke: css("--surface"), "stroke-width": 1.5 }, svg);
  // התוויות אחרונות, עם רקע בהיר מסביב, כדי שהקו של הציון לא יסתיר אותן
  for (const [v, , label, dy] of lines)
    el("text", { x: 4, y: y(v) + dy, "font-size": 8, fill: css("--ink2"), stroke: css("--surface"),
                 "stroke-width": 3, "paint-order": "stroke", direction: "rtl", "text-anchor": "end" }, svg)
      .textContent = bidi(label);
}

// גרף "כמה המוח צודק לאורך הזמן", עם קו של 50% (כמו להטיל מטבע)
function accChart(svg, values, color) {
  const W = 220, H = 64, n = values.length;
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  const lo = Math.min(0.4, ...values) - 0.02, hi = Math.max(0.6, ...values) + 0.02;
  const y = v => 6 + (1 - (v - lo) / (hi - lo)) * (H - 12);
  el("line", { x1: 0, x2: W, y1: y(0.5), y2: y(0.5), stroke: css("--axis"), "stroke-width": 1 }, svg);
  if (n > 1) el("path", { d: values.map((v, i) => (i ? "L" : "M") + (i / (n - 1) * W).toFixed(1) + "," + y(v).toFixed(1)).join(""),
                          fill: "none", stroke: css(color), "stroke-width": 1.5, "stroke-linejoin": "round" }, svg);
  el("text", { x: 4, y: y(0.5) - 3, "font-size": 8, fill: css("--ink2"), stroke: css("--surface"), "stroke-width": 3,
               "paint-order": "stroke", direction: "rtl", "text-anchor": "end" }, svg).textContent = "50% = כמו להטיל מטבע";
}

function brainPanel(card, b, color) {
  const d = el("details", { class: "brain" }, card);
  d.open = openBots.has(b.id);
  d.addEventListener("toggle", () => { d.open ? openBots.add(b.id) : openBots.delete(b.id); saveOpen(); });
  el("summary", {}, d).textContent = "איך הוא מחליט אם לקנות או למכור";
  const x = b.brain;
  if (!x) { el("p", { class: "desc" }, d).textContent = "עוד לא חישב כלום. מחכה לנר הבא."; return; }
  el("p", { class: "status" }, d).textContent = bidi(x.status);
  if (x.learning) {
    const ear = Math.round(x.listen * 100);
    el("div", { class: "lbl" }, d).textContent = "מה המוח למד";
    el("p", { class: "desc" }, d).textContent = "המוח עובר בירושה מהורה לילד (עם שינוי קטן), וכל דור ממשיך ללמוד ממה שקורה. " +
      `עד עכשיו המוח הזה למד מ-${x.lessons.toLocaleString("en-US")} דוגמאות. ` +
      `(מוח חדש לגמרי מתחיל ב"בית ספר" על ${x.school} שלפני שהבוט נולד.) ` +
      (x.acc === null ? "עוד אין מספיק ניחושים כדי לדעת כמה הוא צודק." :
       `ב-${x.acc_n} הניחושים האחרונים הוא צדק בכיוון ב-${x.acc}% מהפעמים (50% = כמו להטיל מטבע).`);
    if (x.accuracy.length > 1) {
      el("div", { class: "lbl" }, d).textContent = "כמה הוא צודק לאורך הזמן";
      accChart(el("svg", { class: "score", role: "img", "aria-label": "כמה המוח צודק לאורך הזמן" }, d), x.accuracy, color);
    }
    el("div", { class: "lbl" }, d).textContent = "כמה הוא מקשיב למוח";
    el("p", { class: "desc" }, d).textContent = `מקשיב ${ear}% למוח ו-${100 - ear}% לנוסחה הקבועה שירש. ` +
      "גם זה עובר בירושה ומשתנה: אם להקשיב למוח עוזר להרוויח, הצאצאים מקשיבים לו יותר, ואם לא - פחות.";
  }
  el("div", { class: "lbl" }, d).textContent = "הציון שלו לאורך הזמן";
  scoreChart(el("svg", { class: "score", role: "img", "aria-label": "הציון לאורך הזמן" }, d), x, color);
  el("div", { class: "lbl" }, d).textContent = "איך יצא הציון עכשיו";
  el("p", { class: "desc" }, d).textContent = x.learning
    ? "הציון מחבר שני קולות: הנוסחה הקבועה (כל סימן כפול המשקל שהבוט ירש), והמוח - רשת עצבית קטנה שמקבלת את כל " +
      `${x.rows.length} הסימנים, מנחשת לאן המחיר ילך ב-${x.horizon} הנרות הבאים, ולומדת מכל טעות. ` +
      "ליד כל סימן: כמה הוא דוחף את הציון עכשיו (כחול = לקנות, אדום = למכור), המשקל שלו בנוסחה, וכמה הוא חשוב למוח."
    : `הבוט בודק ${x.rows.length} סימנים. כל סימן נותן מספר בין 1- ל-1, כפול המשקל שהבוט נותן לו (משקל שלילי = הוא עושה ההפך). ` +
      "הסכום הוא הציון. כחול = דוחף לקנות, אדום = דוחף למכור.";
  for (const r of x.rows) {
    const row = el("div", { class: "sig" }, d);
    const top = el("div", { class: "sigtop" }, row);
    el("b", {}, top).textContent = r.name;
    el("span", { class: "ltr" }, top).textContent = signed(r.part);
    el("div", { class: "desc" }, row).textContent = bidi(x.learning
      ? `${r.sees} · משקל בנוסחה ${signed(r.weight)} · חשיבות במוח ${Math.round(r.imp * 100)}%`
      : `${r.sees} · משקל ${signed(r.weight)}`);
    const fill = el("i", {}, el("div", { class: "bar" }, row));
    fill.style.left = (r.part >= 0 ? 50 : 50 + r.part * 50) + "%";
    fill.style.width = Math.abs(r.part) * 50 + "%";
    fill.style.background = `var(${r.part >= 0 ? "--s1" : "--s8"})`;
  }
  if (x.learning) {   // החשבון: נוסחה × כמה שמקשיבים לה + מוח × כמה שמקשיבים לו
    const ear = Math.round(x.listen * 100);
    for (const [name, v, w] of [["הנוסחה הקבועה", x.formula, 100 - ear],
                                ["המוח (ממוצע הניחושים האחרונים)", x.feel, ear]]) {
      const line = el("div", { class: "sigtop" }, d);
      el("span", {}, line).textContent = `${name} × ${w}%`;
      el("span", { class: "ltr" }, line).textContent = signed(v);
    }
    el("div", { class: "desc" }, d).textContent = bidi(`הניחוש של המוח בנר הזה: ${signed(x.guess)}. ` +
      "הבוט משתמש בממוצע של הניחושים האחרונים, כדי לא לקפוץ מכל רעש קטן.");
  }
  const tot = el("div", { class: "sigtop total" }, d);
  el("b", {}, tot).textContent = "ציון כולל";
  el("b", { class: "ltr" }, tot).textContent = signed(x.score);
  el("div", { class: "lbl" }, d).textContent = "הכללים שלו";
  const ul = el("ul", { class: "rules" }, d);
  for (const [rule, now] of x.rules) {
    const li = el("li", {}, ul);
    el("span", {}, li).textContent = bidi(rule);
    if (now) el("span", { class: "now" }, li).textContent = bidi(`(${now})`);
  }
  el("div", { class: "lbl" }, d).textContent = "מה הוא עשה לאחרונה";
  el("p", { class: "desc" }, d).textContent = x.last.length
    ? bidi(`${x.last[1]} (${fmtTime(new Date(x.last[0] + "Z"), true)})`) : "עוד לא קנה ולא מכר";
}

function bots() {
  const box = document.getElementById("bots");
  box.textContent = "";
  for (const b of DATA.bots) {
    const color = coinColor[b.asset] || "--s1";
    const card = el("article", { class: "bot" }, box);
    const head = el("div", { class: "head" }, card);
    const who = el("span", {}, head);
    who.textContent = `מקום ${b.rank} · `;
    el("b", {}, who).textContent = `בוט #${b.id}`;
    el("span", { class: "chip", style: `--c:var(${color})` }, head).textContent = b.asset;
    const row = el("div", { class: "money" }, card);
    el("span", { class: "v ltr" }, row).textContent = b.value.toFixed(2) + " ₪";
    const ch = el("span", { class: "change " + (b.change >= 0 ? "up" : "down") }, row);
    ch.textContent = (b.change >= 0 ? "▲ " : "▼ ") + pct(b.change) + " מאז המבחן";
    sparkline(el("svg", { "aria-hidden": "true" }, card), b.spark, color);
    el("div", { class: "meta" }, card).textContent =
      `${b.holding ? "מחזיק " + b.asset : "במזומן"} · מושקע ${b.invested}% מהזמן · ` +
      (b.acc === null || b.acc === undefined ? "" : `המוח צודק ${b.acc}% · `) + `דור ${b.gen} · חי ${b.age} · ` +
      `שילם לך ${b.paid.toFixed(2)} ₪`;
    el("div", { class: "desc" }, card).textContent = b.desc;
    el("div", { class: "desc" }, card).textContent = bidi(b.clone);
    brainPanel(card, b, color);
  }
}

function render() {
  legend(document.getElementById("moneyLegend"), DATA.money);
  lineChart(document.getElementById("money"), DATA.money,
            { endLabels: true, fmt: money, tick: v => compact(v) + " ₪", label: "הכסף שלך לאורך הזמן" });
  legend(document.getElementById("coinLegend"), DATA.coins);
  const vals = DATA.coins.flatMap(c => c.values).filter(v => v !== null);
  const big = Math.max(...vals) / Math.min(...vals) > 20;
  document.getElementById("coinSub").textContent = big
    ? "כמה כל מטבע עלה או ירד מאז ההתחלה. ×10 = המחיר גדל פי 10. כל קו בגרף הוא פי כמה מהקו שמתחתיו, כדי שכל המטבעות ייראו"
    : "כמה כל מטבע עלה או ירד מאז ההתחלה, באחוזים";
  lineChart(document.getElementById("coins"), DATA.coins,
            { base: 1, log: true, fmt: v => pct((v - 1) * 100), tick: ratio, label: "כמה כל מטבע עלה או ירד" });
  bots();
}

function renderAll() {
  prepare();
  document.getElementById("title").textContent = DATA.title;
  document.getElementById("rules").textContent = DATA.rules;
  const tiles = document.getElementById("tiles");
  tiles.textContent = "";
  DATA.tiles.forEach(([label, value], i) => {
    const t = el("div", { class: "tile" + (i === 0 ? " hero" : "") }, tiles);
    el("div", { class: "label" }, t).textContent = label;
    el("div", { class: "value ltr" }, t).textContent = value;
  });
  const events = document.getElementById("events");
  events.textContent = "";
  if (!DATA.events.length) el("li", {}, events).textContent = "עוד לא קרה כלום";
  for (const [when, text] of DATA.events) {
    const li = el("li", {}, events);
    el("time", {}, li).textContent = when ? fmtTime(new Date(when + "Z"), true) : "";
    el("span", {}, li).textContent = bidi(text);
  }
  document.getElementById("updated").textContent = (REPLAY ? "הקלטה" : `עודכן ב-${DATA.updated}`) +
    (DATA.refresh ? " · הדף מתרענן לבד" : "") + " · הכסף מזויף, והעבר לא מבטיח כלום לגבי העתיד.";
  render();
}

// נגן ההקלטה: מחליף תמונה כל פעם, כמו סרטון
let showFrame = () => {};
if (REPLAY) {
  const frames = REPLAY.frames, last = frames.length - 1;
  const slider = document.getElementById("frame"), btn = document.getElementById("play");
  let k = 0, playing = true, speed = 1;
  document.getElementById("player").hidden = false;
  slider.max = last;
  showFrame = i => {
    k = Math.max(0, Math.min(last, i));
    const f = frames[k], full = REPLAY.full, cut = s => ({ ...s, values: s.values.slice(0, f.n) });
    DATA = { ...DATA, ...f, times: full.times.slice(0, f.n), money: full.money.map(cut), coins: full.coins.map(cut) };
    slider.value = k;
    document.getElementById("when").textContent = `${k + 1} / ${frames.length}`;
    renderAll();
  };
  const label = () => { btn.textContent = playing ? "⏸ עצור" : "▶ נגן"; };
  btn.addEventListener("click", () => { if (!playing && k === last) showFrame(0); playing = !playing; label(); });
  slider.addEventListener("input", () => { playing = false; label(); showFrame(+slider.value); });
  document.getElementById("speed").addEventListener("change", e => { speed = +e.target.value; });
  (function play() {
    if (playing && k < last) showFrame(k + 1);
    else if (playing) { playing = false; label(); }
    setTimeout(play, 900 / speed);
  })();
  showFrame(0);
} else {
  renderAll();
}

let timer;
addEventListener("resize", () => { clearTimeout(timer); timer = setTimeout(render, 100); });
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", render);
new MutationObserver(render).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
if (DATA.refresh) {
  try { const y = sessionStorage.getItem("scrollY"); if (y) scrollTo(0, +y); } catch (e) {}
  setTimeout(() => {
    try { sessionStorage.setItem("scrollY", String(scrollY)); } catch (e) {}
    location.reload();
  }, DATA.refresh * 1000);
}
</script>
</body>
</html>
"""
