"""
יוצר דף HTML עם חלון לכל בוט, גרף של הכסף שלך וגרף של המטבעות.
פותחים אותו בדפדפן (לחיצה כפולה על הקובץ). עובד גם בלי אינטרנט.
במסחר החי הדף מתרענן לבד כל חצי דקה.
"""

import html
import json
import os
from datetime import datetime

from core import human

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


def bot_cards(world):
    prices = world.history[-1]["prices"]
    cards = []
    for rank, b in enumerate(world.ranked(prices), 1):
        p = prices[b.genome.asset]
        cards.append({
            "rank": rank, "id": b.id, "asset": b.genome.asset, "gen": b.generation,
            "value": round(b.value(p), 2), "change": round(b.period_return(p) * 100, 1),
            "paid": round(b.paid, 2), "holding": b.units > 0, "trades": b.trades,
            "age": human((world.tick - b.born) * world.candle), "desc": b.genome.describe(),
            "clone": b.genome.clone_rule(world.cfg.start_money),
            "spark": b.values,
        })
    return cards


def write_dashboard(path, title, runs, cfg, live=False):
    """runs: רשימה של (שם, עולם). הראשון הוא הראשי: ממנו המספרים והחלונות של הבוטים."""
    world = runs[0][1]
    h = world.history
    if not h:
        return
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
    ]
    if live:
        tiles += [["התשלום הבא בעוד", human(world.next_in(cfg.pay_every))],
                  ["המבחן הבא בעוד", human(world.next_in(cfg.select_every))]]
    data = {
        "refresh": 30 if live else 0,
        "updated": datetime.now().strftime("%H:%M:%S"),
        "rules": f"כל {human(pay)} כל בוט משלם לך {cfg.pay_percent:g}% מהכסף שלו · "
                 f"כל {human(select)} יש מבחן: {cfg.kill_percent:g}% הכי פחות טובים מתים, "
                 f"והטובים בוחרים אם להשתכפל · עד {cfg.max_bots} בוטים",
        "times": [s["time"] for s in h],
        "money": money,
        "coins": coin_series(world),
        "tiles": tiles,
        "bots": bot_cards(world),
        "events": world.events[::-1][:12],
    }
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = TEMPLATE.replace("__TITLE__", html.escape(title)).replace("__DATA__", payload)
    with open(path + ".tmp", "w", encoding="utf-8") as f:
        f.write(page)
    os.replace(path + ".tmp", path)   # כדי שהדפדפן לא יקרא חצי קובץ באמצע כתיבה


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
.events { list-style: none; margin: 0; padding: 0; font-size: 14px; }
.events li { padding: 6px 0; border-bottom: 1px solid var(--grid); display: flex; gap: 12px; }
.events li:last-child { border-bottom: 0; }
.events time { color: var(--muted); white-space: nowrap; font-variant-numeric: tabular-nums; }
.note { color: var(--muted); font-size: 13px; }
</style>
</head>
<body>
<main>
  <h1>__TITLE__</h1>
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
const DATA = __DATA__;
const COIN_COLORS = ["--s2", "--s3", "--s4", "--s5", "--s6", "--s7", "--s8"];
const coinColor = {};
DATA.coins.forEach((c, i) => { c.color = COIN_COLORS[i]; coinColor[c.name] = c.color; });
const T = DATA.times.map(s => new Date(s + "Z"));
const SPAN = (T[T.length - 1] - T[0]) / 864e5;   // ימים
const DAILY = T.every(t => t.getUTCHours() === 0 && t.getUTCMinutes() === 0);

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
      `${b.holding ? "מחזיק " + b.asset : "במזומן"} · דור ${b.gen} · חי ${b.age} · שילם לך ${b.paid.toFixed(2)} ₪`;
    el("div", { class: "desc" }, card).textContent = b.desc;
    el("div", { class: "desc" }, card).textContent = b.clone;
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

document.getElementById("rules").textContent = DATA.rules;
DATA.tiles.forEach(([label, value], i) => {
  const t = el("div", { class: "tile" + (i === 0 ? " hero" : "") }, document.getElementById("tiles"));
  el("div", { class: "label" }, t).textContent = label;
  el("div", { class: "value ltr" }, t).textContent = value;
});
const events = document.getElementById("events");
if (!DATA.events.length) el("li", {}, events).textContent = "עוד לא קרה כלום";
for (const [when, text] of DATA.events) {
  const li = el("li", {}, events);
  el("time", {}, li).textContent = when ? fmtTime(new Date(when + "Z"), true) : "";
  el("span", {}, li).textContent = text;
}
document.getElementById("updated").textContent =
  `עודכן ב-${DATA.updated}` + (DATA.refresh ? " · הדף מתרענן לבד" : "") + " · הכסף מזויף, והעבר לא מבטיח כלום לגבי העתיד.";
render();

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
