"""
יוצר דף HTML עם גרפים של הכסף שלך ושל מחיר הביטקוין.
פותחים אותו בדפדפן (לחיצה כפולה על הקובץ). עובד גם בלי אינטרנט.
"""

import html
import json


def net_series(world):
    """רווח/הפסד נקי בכל יום: מה שלקחת + מה שנשאר בבוטים - מה שהשקעת."""
    return [round(s["collected"] + s["inside"] - s["invested"], 2) for s in world.history]


def hold_series(world):
    """מה היה קורה אם כל שקל שהשקעת בבוטים היה הולך ישר לקניית ביטקוין."""
    btc = prev = 0.0
    out = []
    for s in world.history:
        btc += (s["invested"] - prev) / s["price"]
        prev = s["invested"]
        out.append(round(btc * s["price"] - s["invested"], 2))
    return out


def write_chart(path, title, runs):
    """runs: רשימה של (שם, עולם). הראשון הוא הראשי, ממנו לוקחים את המספרים למעלה."""
    main = runs[0][1]
    h = main.history
    if not h:
        return
    series = [{"name": runs[0][0], "values": net_series(main)},
              {"name": "רק לקנות ביטקוין באותו כסף", "values": hold_series(main)}]
    series += [{"name": name, "values": net_series(w)} for name, w in runs[1:]]
    last = h[-1]
    net = series[0]["values"][-1]
    data = {
        "dates": [s["date"][:10] for s in h],
        "price": [round(s["price"], 2) for s in h],
        "series": series,
        "tiles": [
            ["רווח/הפסד נקי", f"{net:+,.2f} ₪"],
            ["השקעת", f"{last['invested']:,.2f} ₪"],
            ["לקחת מהבוטים", f"{last['collected']:,.2f} ₪"],
            ["נשאר בבוטים", f"{last['inside']:,.2f} ₪"],
            ["ביטקוין בתקופה", f"{(last['price'] / h[0]['price'] - 1) * 100:+,.0f}%"],
            ["בוטים חיים / מתו", f"{last['alive']} / {main.deaths}"],
        ],
    }
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = TEMPLATE.replace("__TITLE__", html.escape(title)).replace("__DATA__", payload)
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)


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
  --grid: #e1e0d9; --axis: #c3c2b7; --ring: rgba(11,11,11,0.10);
  --s1: #2a78d6; --s2: #eb6834; --s3: #1baf7a;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --page: #0d0d0d; --surface: #1a1a19; --ink: #f0efec; --ink2: #c3c2b7; --muted: #898781;
    --grid: #2c2c2a; --axis: #383835; --ring: rgba(255,255,255,0.10);
    --s1: #3987e5; --s2: #d95926; --s3: #199e70;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --page: #0d0d0d; --surface: #1a1a19; --ink: #f0efec; --ink2: #c3c2b7; --muted: #898781;
  --grid: #2c2c2a; --axis: #383835; --ring: rgba(255,255,255,0.10);
  --s1: #3987e5; --s2: #d95926; --s3: #199e70;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--page); color: var(--ink);
       font: 15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width: 960px; margin: 0 auto; padding: 24px 16px 48px; }
h1 { font-size: 22px; margin: 0 0 16px; }
h2 { font-size: 16px; margin: 0 0 2px; }
.sub { color: var(--ink2); margin: 0 0 12px; font-size: 14px; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 20px; }
.tile, .card { background: var(--surface); border-radius: 12px; box-shadow: 0 0 0 1px var(--ring); }
.tile { padding: 12px 14px; }
.tile .label { color: var(--ink2); font-size: 13px; }
.tile .value { font-size: 20px; font-weight: 600; direction: ltr; text-align: right; white-space: nowrap; }
.tile.hero .value { font-size: 28px; line-height: 1.2; }
.card { padding: 16px; margin-bottom: 20px; position: relative; }
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
details { margin-top: 8px; }
summary { cursor: pointer; color: var(--ink2); font-size: 14px; }
table { border-collapse: collapse; width: 100%; font-size: 13px; margin-top: 8px; font-variant-numeric: tabular-nums; }
th, td { padding: 4px 8px; text-align: right; border-bottom: 1px solid var(--grid); }
td.num { direction: ltr; text-align: left; }
.note { color: var(--muted); font-size: 13px; }
</style>
</head>
<body>
<main>
  <h1>__TITLE__</h1>
  <div class="tiles" id="tiles"></div>

  <section class="card">
    <h2>הכסף שלך לאורך הזמן</h2>
    <p class="sub">רווח או הפסד נקי בשקלים: מה שלקחת, ועוד מה שנשאר בבוטים, פחות מה שהשקעת</p>
    <div class="legend" id="legend1"></div>
    <div class="plot" id="money"></div>
  </section>

  <section class="card">
    <h2>מחיר הביטקוין (בדולרים)</h2>
    <p class="sub" id="priceSub"></p>
    <div class="plot" id="price"></div>
  </section>

  <details class="card">
    <summary>כל המספרים בטבלה</summary>
    <table id="table"></table>
  </details>
  <p class="note">הכסף בסימולציה מזויף. העבר לא מבטיח כלום לגבי העתיד.</p>
</main>

<script>
const DATA = __DATA__;
const COLORS = ["--s1", "--s2", "--s3"];

function css(name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }
function el(tag, attrs, parent) {
  const ns = ["svg","path","line","circle","text","rect","g"].includes(tag) ? "http://www.w3.org/2000/svg" : null;
  const e = ns ? document.createElementNS(ns, tag) : document.createElement(tag);
  for (const k in attrs || {}) e.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(e);
  return e;
}
function money(v) {
  const a = Math.abs(v), s = v > 0 ? "+" : v < 0 ? "−" : "";
  return s + (a >= 1000 ? Math.round(a).toLocaleString("en-US") : a.toFixed(2)) + " ₪";
}
function compact(v) {
  const a = Math.abs(v), s = v < 0 ? "−" : "";
  if (a >= 1e6) return s + +(a / 1e6).toFixed(1) + "M";
  if (a >= 1e3) return s + +(a / 1e3).toFixed(1) + "K";
  return s + +a.toFixed(a < 10 ? 1 : 0);
}
function usd(v) { return "$" + Math.round(v).toLocaleString("en-US"); }
function fmtDate(d) { const [y, m, dd] = d.split("-"); return dd + "/" + m + "/" + y; }

function niceTicks(lo, hi, n) {
  const raw = (hi - lo) / n, mag = Math.pow(10, Math.floor(Math.log10(raw || 1)));
  const step = [1, 2, 5, 10].map(x => x * mag).find(x => x >= raw);
  const out = [];
  for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) out.push(+v.toFixed(10));
  return out;
}
function logTicks(lo, hi) {
  const out = [];
  for (let k = Math.floor(Math.log10(lo)); k <= Math.ceil(Math.log10(hi)); k++)
    for (const m of [1, 2, 5]) { const v = m * Math.pow(10, k); if (v >= lo && v <= hi) out.push(v); }
  return out.length > 7 ? out.filter(v => String(v)[0] === "1") : out;
}

function lineChart(box, series, opts) {
  box.textContent = "";
  const W = box.clientWidth, H = W < 500 ? 220 : 280;
  const m = { l: 52, r: opts.endLabels ? 64 : 16, t: 10, b: 26 };
  const n = DATA.dates.length;
  const all = series.flatMap(s => s.values);
  let lo = Math.min(...all), hi = Math.max(...all);
  if (opts.zero) { lo = Math.min(lo, 0); hi = Math.max(hi, 0); }
  if (lo === hi) { lo -= 1; hi += 1; }
  const log = opts.log && hi / lo > 20;
  const f = log ? Math.log10 : v => v;
  let ticks = log ? logTicks(lo, hi) : niceTicks(lo, hi, 4);
  if (!log) { lo = Math.min(lo, ticks[0]); hi = Math.max(hi, ticks[ticks.length - 1]); }
  const x = i => m.l + (n === 1 ? 0 : i / (n - 1)) * (W - m.l - m.r);
  const y = v => m.t + (1 - (f(v) - f(lo)) / (f(hi) - f(lo))) * (H - m.t - m.b);

  const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, height: H, tabindex: 0, role: "img",
                          "aria-label": opts.label }, box);
  for (const t of ticks) {
    el("line", { x1: m.l, x2: W - m.r, y1: y(t), y2: y(t), stroke: t === 0 && opts.zero ? css("--axis") : css("--grid"),
                 "stroke-width": 1, "shape-rendering": "crispEdges" }, svg);
    const lab = el("text", { x: m.l - 8, y: y(t) + 4, "text-anchor": "end", "font-size": 11, fill: css("--muted") }, svg);
    lab.textContent = opts.tick(t);
  }
  // תוויות בציר הזמן: תחילת כל שנה בתקופות ארוכות, אחרת תאריכים במרווחים קבועים
  const years = new Set(DATA.dates.map(d => d.slice(0, 4))).size > 2;
  const step = Math.max(1, Math.round(n / (W < 500 ? 3 : 6)));
  let lastX = -Infinity;
  for (let i = 0; i < n; i++) {
    const d = DATA.dates[i];
    const due = years ? i > 0 && d.slice(0, 4) !== DATA.dates[i - 1].slice(0, 4) : i % step === 0;
    if (!due || x(i) - lastX < 40 || x(i) > W - m.r - 12) continue;
    lastX = x(i);
    el("text", { x: x(i), y: H - 6, "text-anchor": "middle", "font-size": 11, fill: css("--muted") }, svg)
      .textContent = years ? d.slice(0, 4) : fmtDate(d).slice(0, 5);
  }
  series.forEach(s => {
    const d = s.values.map((v, i) => (i ? "L" : "M") + x(i).toFixed(1) + "," + y(v).toFixed(1)).join("");
    el("path", { d, fill: "none", stroke: css(s.color), "stroke-width": 2, "stroke-linejoin": "round",
                 "stroke-linecap": "round" }, svg);
  });
  // נקודה וערך בסוף כל קו (אם הערכים לא עולים אחד על השני)
  const ends = series.map(s => ({ s, v: s.values[n - 1] })).sort((a, b) => y(a.v) - y(b.v));
  const roomy = ends.every((e, i) => i === 0 || y(e.v) - y(ends[i - 1].v) >= 14);
  for (const e of ends) {
    el("circle", { cx: x(n - 1), cy: y(e.v), r: 4, fill: css(e.s.color), stroke: css("--surface"), "stroke-width": 2 }, svg);
    if (opts.endLabels && roomy) {
      const t = el("text", { x: x(n - 1) + 8, y: y(e.v) + 4, "font-size": 12, fill: css("--ink2") }, svg);
      t.textContent = opts.fmt(e.v);
    }
  }

  // שכבת ריחוף: קו אנכי + חלונית עם כל הערכים באותו יום
  const cross = el("line", { y1: m.t, y2: H - m.b, stroke: css("--axis"), "stroke-width": 1, visibility: "hidden" }, svg);
  const dots = series.map(s => el("circle", { r: 4, fill: css(s.color), stroke: css("--surface"), "stroke-width": 2,
                                              visibility: "hidden" }, svg));
  const tip = el("div", { class: "tip" }, box);
  const hit = el("rect", { x: m.l, y: 0, width: W - m.l - m.r, height: H, fill: "transparent" }, svg);
  let cur = n - 1;
  function show(i) {
    cur = Math.max(0, Math.min(n - 1, i));
    cross.setAttribute("x1", x(cur)); cross.setAttribute("x2", x(cur)); cross.setAttribute("visibility", "visible");
    series.forEach((s, k) => { dots[k].setAttribute("cx", x(cur)); dots[k].setAttribute("cy", y(s.values[cur]));
                               dots[k].setAttribute("visibility", "visible"); });
    tip.textContent = "";
    el("div", { class: "date" }, tip).textContent = fmtDate(DATA.dates[cur]);
    series.map(s => s).sort((a, b) => b.values[cur] - a.values[cur]).forEach(s => {
      const row = el("div", { class: "row" }, tip);
      el("span", { class: "key", style: `background:${css(s.color)}` }, row);
      el("b", {}, row).textContent = opts.fmt(s.values[cur]);
      if (series.length > 1) el("span", { class: "name" }, row).textContent = s.name;
    });
    tip.style.display = "block";
    const tw = tip.offsetWidth, px = x(cur);
    tip.style.left = (px + 12 + tw > W ? px - 12 - tw : px + 12) + "px";
    tip.style.top = "8px";
  }
  function hide() { cross.setAttribute("visibility", "hidden"); dots.forEach(d => d.setAttribute("visibility", "hidden"));
                    tip.style.display = "none"; }
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

function render() {
  const series = DATA.series.map((s, i) => ({ ...s, color: COLORS[i] }));
  // הביטקוין תמיד כתום - גם בגרף הכסף וגם בגרף המחיר
  const price = [{ name: "מחיר", values: DATA.price, color: "--s2" }];
  legend(document.getElementById("legend1"), series);
  lineChart(document.getElementById("money"), series,
            { zero: true, endLabels: true, fmt: money, tick: v => compact(v) + " ₪", label: "הכסף שלך לאורך הזמן" });
  const lo = Math.min(...DATA.price), hi = Math.max(...DATA.price);
  document.getElementById("priceSub").textContent = hi / lo > 20
    ? "סולם לוגריתמי: כל קו בגובה אחר הוא פי כמה מהקודם, כדי שגם המחירים הנמוכים של ההתחלה ייראו"
    : "מחיר הסגירה בסוף כל יום";
  lineChart(document.getElementById("price"), price,
            { log: true, fmt: usd, tick: v => "$" + compact(v), label: "מחיר הביטקוין" });
}

function tiles() {
  const box = document.getElementById("tiles");
  DATA.tiles.forEach(([label, value], i) => {
    const t = el("div", { class: "tile" + (i === 0 ? " hero" : "") }, box);
    el("div", { class: "label" }, t).textContent = label;
    el("div", { class: "value" }, t).textContent = value;
  });
}

function table() {
  const t = document.getElementById("table"), n = DATA.dates.length;
  const head = el("tr", {}, t);
  ["תאריך", "מחיר ביטקוין", ...DATA.series.map(s => s.name)].forEach(h => el("th", {}, head).textContent = h);
  const step = Math.max(1, Math.ceil(n / 40));
  for (let i = 0; i < n; i += step) row(i);
  if ((n - 1) % step) row(n - 1);
  function row(i) {
    const r = el("tr", {}, t);
    el("td", {}, r).textContent = fmtDate(DATA.dates[i]);
    el("td", { class: "num" }, r).textContent = usd(DATA.price[i]);
    DATA.series.forEach(s => el("td", { class: "num" }, r).textContent = money(s.values[i]));
  }
}

tiles(); table(); render();
let timer;
addEventListener("resize", () => { clearTimeout(timer); timer = setTimeout(render, 100); });
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", render);
new MutationObserver(render).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
</script>
</body>
</html>
"""
