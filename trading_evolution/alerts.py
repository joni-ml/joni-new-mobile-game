"""
התראות לטלפון (טלגרם) ודוח תקופתי על הבוטים.

איך מחברים את טלגרם (פעם אחת):
  1. בטלגרם מחפשים @BotFather, שולחים לו /newbot ועונים על השאלות. בסוף הוא נותן "טוקן" (מחרוזת ארוכה).
  2. שולחים הודעה כלשהי לבוט החדש שלכם (כדי שיהיה לו מותר לכתוב לכם).
  3. פותחים בדפדפן: https://api.telegram.org/bot<הטוקן>/getUpdates ומעתיקים את המספר שאחרי "chat":{"id":
  4. כותבים את שניהם ב-settings.toml: telegram_token = "..." ו-telegram_chat = "..."
הטוקן הוא כמו סיסמה: לא לשתף את settings.toml אחרי שכתבתם אותו.
"""

import os
import urllib.parse
import urllib.request
from datetime import datetime

from dashboard import hold_series

HERE = os.path.dirname(os.path.abspath(__file__))


def send(cfg, text):
    """שולח הודעה לטלגרם. בלי טוקן - לא עושה כלום. אם זה לא עובד, רק מדפיס (המסחר ממשיך)."""
    if not (cfg.telegram_token and cfg.telegram_chat):
        return False
    url = f"https://api.telegram.org/bot{cfg.telegram_token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": cfg.telegram_chat, "text": text[:4000]}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=15) as r:
            return r.status == 200
    except Exception as e:
        print(f"לא הצלחתי לשלוח התראה לטלגרם: {e}")
        return False


def news(world, seen):
    """מה חדש מאז הפעם הקודמת: קניות ומכירות של בוטים, ואירועים חשובים (מבחן, עצירה).
    seen נשמר במצב של המסחר החי, כדי לא לשלוח את אותו דבר פעמיים."""
    out = []
    trades = seen.setdefault("trades", {})
    for b in world.bots:
        if b.last and trades.get(str(b.id)) != b.last[0]:
            trades[str(b.id)] = b.last[0]
            out.append(f"בוט #{b.id}: {b.last[1]}")
    alive = {str(b.id) for b in world.bots}
    seen["trades"] = {k: v for k, v in trades.items() if k in alive}
    last = seen.get("event")
    fresh = world.events if last is None or last not in world.events else world.events[world.events.index(last) + 1:]
    if world.events:
        seen["event"] = world.events[-1]
    out += [text for _, text in fresh if text.startswith(("מבחן", "עצירה", "כל הבוטים מתו"))]
    return out


def report(world, cfg, since):
    """דוח קצר: איך הולך, מול "לקנות ולחכות", מי מת ומי שוכפל מאז הדוח הקודם, ומה הבוט הכי טוב עושה.
    since: המספרים מהדוח הקודם (נשמרים במצב של המסחר החי)."""
    if not world.history:
        return "עוד לא התחלנו לסחור."
    last = world.history[-1]
    net = last["collected"] + last["inside"] - last["invested"]
    hold = hold_series(world)[-1]
    lines = [f"דוח הבוטים - {datetime.now():%d/%m/%Y %H:%M}",
             f"השקעת {last['invested']:.2f} ש\"ח, נשאר בבוטים {last['inside']:.2f}, לקחת {last['collected']:.2f}",
             f"רווח/הפסד נקי: {net:+.2f} ש\"ח | אם היית קונה את כל המטבעות ומחכה: {hold:+.2f} ש\"ח",
             ("הבוטים מנצחים את \"לקנות ולחכות\"" if net > hold else "\"לקנות ולחכות\" מנצח כרגע") +
             f" (הפרש {net - hold:+.2f} ש\"ח)",
             f"מאז הדוח הקודם: מתו {world.deaths - since.get('deaths', 0)}, "
             f"שוכפלו {world.clones - since.get('clones', 0)}, חיים {len(world.bots)}"]
    checked, right, ups = world.brain_record()
    if checked >= 100:
        lines.append(f"המוחות צדקו ב-{100 * right / checked:.0f}% מהניחושים (לומר תמיד אותו דבר: {100 * ups / checked:.0f}%)")
    if world.bots:
        prices = last["prices"]
        best = world.ranked(prices)[0]
        lines.append(f"הבוט המוביל: #{best.id} ({best.genome.asset}, דור {best.generation}) - "
                     f"{best.genome.describe(world.cfg.signals, world.cfg.goal, world.cfg.brain == 'learning')}")
    if world.stopped:
        lines.append("⏸ המשחק עצור (stop_all). כדי להמשיך: python live.py --resume")
    since.update(deaths=world.deaths, clones=world.clones)
    return "\n".join(lines)


def save_report(text):
    """שומר את הדוח בתיקייה reports, וגם מחזיר איפה."""
    folder = os.path.join(HERE, "reports")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"report_{datetime.now():%Y-%m-%d_%H%M}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    return path
