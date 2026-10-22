"""
מעבדה: בודק הרבה צירופים של הגדרות על כל שנה מ-2020, ויוצר דף lab.html עם מחוונים.
מזיזים מחוון ורואים מיד כמה הבוטים היו מרוויחים בכל שנה, מול "לקנות ולחכות".

  python lab.py               # 27 צירופים (לוקח זמן; התוצאות נשמרות, אז אפשר לעצור ולהמשיך)
  python lab.py --workers 4   # כמה בדיקות במקביל (לפי כמה ליבות יש למחשב)

הבדיקות קצרות (פעם אחת לכל שנה), אז יש בהן הרבה מזל. צירוף ששווה לנסות הוא כזה שטוב ברוב השנים,
לא רק באחת. ואחרי שבוחרים - כדאי לבדוק אותו עם evaluate.py.
"""

import argparse
import itertools
import json
import os
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "lab_results.json")
GRID = {"select_every": ["14d", "30d", "60d"], "kill_percent": [15, 25, 35], "patience": ["1d", "3d", "5d"]}
NAMES = {"select_every": "כל כמה זמן יש מבחן", "kill_percent": "כמה אחוזים מתים במבחן",
         "patience": "כמה זמן מחכים לפני שבורחים מסכנה"}
YEARS = [2020, 2021, 2022, 2023, 2024, 2025]


def check(job):
    """צירוף אחד: על כל שנה - מתאמנים על מה שהיה לפניה ונבחנים עליה."""
    key, conf, settings = job
    from core import load_settings
    from evaluate import run
    from evolution_sim import load_data
    cfg = load_settings(settings)
    times, prices = load_data("daily", cfg.assets, 1)
    cfg.assets = list(prices)
    for k, v in conf.items():
        setattr(cfg, k, v)
    out = {}
    for y in YEARS:
        if datetime(y, 1, 1) < times[-1]:
            bots, hold, invested = run(times, prices, cfg, y, 1, 2)
            out[str(y)] = [round(bots, 2), round(hold, 2), round(invested, 2)]
    return key, out


def main():
    p = argparse.ArgumentParser(description="מעבדה: הרבה הגדרות, דף עם מחוונים")
    p.add_argument("--settings", default=os.path.join(HERE, "settings.toml"))
    p.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    p.add_argument("--out", default=os.path.join(HERE, "lab.html"))
    args = p.parse_args()
    done = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    jobs = []
    for values in itertools.product(*GRID.values()):
        conf = dict(zip(GRID, values))
        key = "|".join(str(v) for v in values)
        if key not in done:
            jobs.append((key, conf, args.settings))
    print(f"{len(done)} צירופים כבר נבדקו, נשארו {len(jobs)}")
    with ProcessPoolExecutor(args.workers) as pool:
        for n, (key, out) in enumerate(pool.map(check, jobs), 1):
            done[key] = out
            with open(CACHE, "w") as f:
                json.dump(done, f)
            print(f"  {n}/{len(jobs)}: {key}", flush=True)
            write_page(args.out, done)
    write_page(args.out, done)
    print(f"הדף: {os.path.abspath(args.out)} (לפתוח בדפדפן)")


def write_page(path, done):
    data = {"grid": GRID, "names": NAMES, "results": done}
    with open(path, "w", encoding="utf-8") as f:
        f.write(PAGE.replace("__DATA__", json.dumps(data, ensure_ascii=False)))


PAGE = r"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>מעבדת הבוטים</title>
<style>
:root { --bg: #f6f7f9; --surface: #fff; --ink: #1c2330; --muted: #5f6b7a; --ring: #dfe3e8; --up: #1a7f4b; --down: #c0392b; --s1: #2f6fdf; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #11151b; --surface: #1a2029; --ink: #e8ecf1; --muted: #9aa5b3; --ring: #2c3440; --up: #4cc38a; --down: #ff7b6b; --s1: #6ea0ff; } }
:root[data-theme="dark"] { --bg: #11151b; --surface: #1a2029; --ink: #e8ecf1; --muted: #9aa5b3; --ring: #2c3440; --up: #4cc38a; --down: #ff7b6b; --s1: #6ea0ff; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 16px/1.5 system-ui, -apple-system, "Segoe UI", Arial, sans-serif; }
main { max-width: 760px; margin: 0 auto; padding: 16px; }
.card { background: var(--surface); border-radius: 12px; box-shadow: 0 0 0 1px var(--ring); padding: 16px; margin-bottom: 16px; }
label { display: block; margin: 12px 0 4px; font-weight: 600; }
input[type=range] { width: 100%; accent-color: var(--s1); }
.val { color: var(--s1); font-weight: 700; }
table { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }
th, td { padding: 8px 6px; border-bottom: 1px solid var(--ring); text-align: start; }
.up { color: var(--up); } .down { color: var(--down); }
.big { font-size: 22px; font-weight: 700; }
.muted { color: var(--muted); font-size: 14px; }
.ltr { direction: ltr; unicode-bidi: isolate; display: inline-block; }
</style>
</head>
<body>
<main>
  <h1>מעבדת הבוטים</h1>
  <p class="muted">מזיזים מחוון ורואים כמה הבוטים היו מרוויחים בכל שנה (₪50 בהתחלה, מתאמנים על מה שהיה לפני השנה ונבחנים עליה),
     מול מה שהיה קורה אם אותו כסף היה נקנה בכל המטבעות ונשאר שם. כל בדיקה כאן היא פעם אחת לכל שנה, אז יש בה הרבה מזל.</p>
  <div class="card" id="controls"></div>
  <div class="card"><div class="big" id="summary"></div><p class="muted" id="sub"></p>
    <table><thead><tr><th>שנה</th><th>הבוטים</th><th>לקנות ולחכות</th><th>מי ניצח</th></tr></thead><tbody id="rows"></tbody></table>
  </div>
</main>
<script>
const D = __DATA__;
const keys = Object.keys(D.grid), pick = {};
const box = document.getElementById("controls");
for (const k of keys) {
  const vals = D.grid[k];
  pick[k] = Math.floor(vals.length / 2);
  const lab = document.createElement("label");
  const span = document.createElement("span"); span.className = "val";
  lab.append(D.names[k] + ": ", span);
  const r = Object.assign(document.createElement("input"), { type: "range", min: 0, max: vals.length - 1, step: 1, value: pick[k] });
  r.setAttribute("aria-label", D.names[k]);
  r.oninput = () => { pick[k] = +r.value; show(); };
  box.append(lab, r);
  pick[k + "_span"] = span;
}
const money = v => (v >= 0 ? "+" : "−") + Math.abs(v).toFixed(2) + " ₪";
function show() {
  const values = keys.map(k => D.grid[k][pick[k]]);
  keys.forEach((k, i) => pick[k + "_span"].textContent = values[i] + (k === "kill_percent" ? "%" : ""));
  const res = D.results[values.join("|")];
  const rows = document.getElementById("rows"); rows.textContent = "";
  if (!res) { document.getElementById("summary").textContent = "הצירוף הזה עוד לא נבדק"; document.getElementById("sub").textContent = "מריצים python lab.py ומחכים"; return; }
  let wins = 0, sb = 0, sh = 0;
  for (const [y, [b, h]] of Object.entries(res)) {
    const tr = rows.insertRow();
    const win = b > h; wins += win; sb += b; sh += h;
    tr.insertCell().textContent = y;
    for (const v of [b, h]) { const c = tr.insertCell(); const s = document.createElement("span"); s.className = "ltr " + (v >= 0 ? "up" : "down"); s.textContent = money(v); c.append(s); }
    tr.insertCell().textContent = win ? "הבוטים" : "לקנות ולחכות";
  }
  const n = Object.keys(res).length;
  document.getElementById("summary").textContent = `הבוטים ניצחו ב-${wins} מתוך ${n} שנים`;
  document.getElementById("sub").textContent = `בסך הכול: הבוטים ${money(sb)} · לקנות ולחכות ${money(sh)}`;
}
show();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
