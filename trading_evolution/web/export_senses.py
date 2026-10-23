"""
מייצא את "החושים מהאינטרנט" (internet.py) לאתר: web/senses.json.
לכל יום ולכל מטבע - הסימן של כל חוש (בין -100 ל-100), מיושר כמו בפייתון: רק מספר שכבר פורסם באותו יום.
חוש של כל השוק (למשל מדד הפחד) נשמר פעם אחת ב-"all", וחוש של כל מטבע (למשל כתובות פעילות) ב-"coins".

  python web/export_senses.py      (אחרי fetch_data.py)
"""

import json
import os
import sys

WEB = os.path.dirname(os.path.abspath(__file__))
HERE = os.path.dirname(WEB)
sys.path.insert(0, HERE)

import core  # noqa: E402
import evolution_sim as es  # noqa: E402
import internet  # noqa: E402


def main():
    cfg = core.load_settings(os.path.join(HERE, "settings.toml"))
    times, prices = es.load_data("daily", cfg.assets, 1)
    assets = list(prices)
    ex = internet.extras(assets, times, False)
    q = lambda xs: [None if x is None else round(x * 100) for x in xs]
    out = {"start": times[0].strftime("%Y-%m-%d"), "n": len(times), "names": list(internet.SOURCES),
           "titles": [internet.SOURCES[n]["title"] for n in internet.SOURCES], "all": {}, "coins": {a: {} for a in assets}}
    for name in internet.SOURCES:
        per_coin = any(os.path.exists(internet.path(name, a)) for a in assets)
        for a in assets:
            if name in ex[a]:
                sig = q(ex[a][name][1])
                if per_coin:
                    out["coins"][a][name] = sig
                else:
                    out["all"][name] = sig
    path = os.path.join(WEB, "senses.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"), ensure_ascii=False)
    print(f"{path}: {os.path.getsize(path):,} בתים, חושים: {', '.join(out['names'])}")


if __name__ == "__main__":
    main()
