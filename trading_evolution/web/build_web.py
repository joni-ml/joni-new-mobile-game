"""
בונה את אתר האימון: web/bot-trainer.html - דף אחד שמאמנים בו את הבוטים ישר בדפדפן.
לוקח את המחירים מ-data/daily (אחרי fetch_data.py) ומכניס אותם לתוך הדף, אז הדף עובד גם בלי אינטרנט.

  python web/build_web.py
"""

import json
import os
import sys

WEB = os.path.dirname(os.path.abspath(__file__))
HERE = os.path.dirname(WEB)
sys.path.insert(0, HERE)

import core  # noqa: E402
import evolution_sim as es  # noqa: E402


def main():
    cfg = core.load_settings(os.path.join(HERE, "settings.toml"))
    times, prices = es.load_data("daily", cfg.assets, 1)
    assert all((b - a).days == 1 for a, b in zip(times, times[1:])), "יש ימים חסרים במחירים"
    data = {"start": times[0].strftime("%Y-%m-%d"), "n": len(times),
            "coins": {a: [float(f"{x:.5g}") for x in p] for a, p in prices.items()}}
    page = open(os.path.join(WEB, "template.html"), encoding="utf-8").read()
    out = os.path.join(WEB, "bot-trainer.html")
    pre = open(os.path.join(WEB, "pretrained.json"), encoding="utf-8").read().strip()   # הבוטים ש-Claude אימן
    with open(out, "w", encoding="utf-8") as f:
        f.write(page.replace("__PRICES__", json.dumps(data, separators=(",", ":"))).replace("__PRETRAINED__", pre))
    print(f"הדף: {out} ({len(prices)} מטבעות, {times[0]:%d/%m/%Y} עד {times[-1]:%d/%m/%Y}) - לפתוח בדפדפן")


if __name__ == "__main__":
    main()
