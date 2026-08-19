/* ============================================================================
   RLS · שכבת הרשת
   ============================================================================

   העולם הוא רשת תאים. תא מחזיק *חומר אחד* — כלומר קבוצת אטומים — טמפרטורה,
   ומצב צבירה. אין "חול", "מים", "קרח" ו"אדים" כארבעה דברים שונים: יש SiO₂
   ויש H₂O, והשאר נגזר.

   שלושה דברים מבדילים את הקובץ הזה מהמנוע של המשחק הישן:

   1. תנועה נקבעת לפי צפיפות, לא לפי סוג. לא כתוב בשום מקום "שמן צף על מים"
      — זה יוצא מזה שהצפיפות שלו נמוכה יותר. כל חומר שייוולד תוך כדי משחק
      יידע לצוף או לשקוע נכון מהרגע הראשון.

   2. מצב הצבירה נגזר מנקודות ההיתוך והרתיחה האמיתיות, דרך שער של חום כמוס.
      לכן מים רותחים נעצרים על 100 מעלות במקום להתאדות בהבזק.

   3. תגובות נקראות ממנוע הכימיה, כולל היחסים. 2H₂ + O₂ → 2H₂O באמת דורש
      שלושה תאים ומייצר שניים. תא אחד נעלם — וזה נכון, כי נפח לא נשמר.
      מה שכן נשמר, תמיד, זה האטומים.

   ה"צורה" (form) היא השכבה הנוספת: אותו חומר בדיוק יכול להיות גרגרי או
   מלוכד. SiO₂ גרגרי הוא חול, SiO₂ מלוכד הוא זכוכית. אף אחד לא כתב חוק
   שהופך חול לזכוכית — כשחול נמס ומתקרר הוא פשוט מתמצק כגוש. זה מה שקורה
   בתנור אמיתי.
   ============================================================================ */
import { reaction, subById, sub_ } from './chem.js';
import { SOLID, LIQUID, GAS, stateOf, density, heatCap,
         conductivity, latentFus, latentVap, color } from './matter.js';

export const EMPTY = 65535;                  // ריק = ואקום, לא "אוויר"
export const BULK = 0, GRAIN = 1;            // צורה: גוש מלוכד / גרגרים
export const ABS_ZERO = -273.15;
export const MAX_TEMP = 60000;
/* טמפרטורה חסומה — הגדרה אחת, במקום אחד. היו כאן שלושה עותקים של אותה
   בדיקה, ואחד מהם לא היה ניתן להגעה בכלל: קלקלנו אותו בכוונה ואף בדיקה לא
   הרגישה, כי עותק אחר תפס במקומו. שלושה עותקים של חוק אחד זה שלושה מקומות
   שאפשר לשכוח לתקן. */
export const clampT = t => t < ABS_ZERO ? ABS_ZERO : t > MAX_TEMP ? MAX_TEMP : t;

/* כמה מהאנרגיה של תגובה נשארת כחום בתאים. השאר יוצא כאור וקרינה — ולכן
   להבה אמיתית מגיעה ל-2000 ולא ל-4000 מעלות. */
const HEAT_YIELD = 0.60;
const D8 = [[-1,-1],[0,-1],[1,-1],[-1,0],[1,0],[-1,1],[0,1],[1,1]];

export class World {
  constructor(w, h, ambient = 20, seed = 12345) {
    this.w = w; this.h = h; this.n = w * h;
    this.ambient = ambient;
    this.sub   = new Uint16Array(this.n).fill(EMPTY);   // איזה חומר
    this.temp  = new Float32Array(this.n).fill(ambient);
    this.phase = new Uint8Array(this.n);                // מוצק/נוזל/גז
    this.form  = new Uint8Array(this.n);                // גוש/גרגר
    this.prog  = new Float32Array(this.n);              // התקדמות בשינוי מצב
    this.sup   = new Uint8Array(this.n);                // נתמך על ידי הקרקע
    this.done  = new Uint8Array(this.n);                // כבר זז השנייה הזו
    this.dT    = new Float32Array(this.n);
    this.stack = new Int32Array(this.n);
    this.tick  = 0;
    this.s     = seed >>> 0 || 1;
    /* קצב איבוד החום לסביבה. אפס = תיבה אטומה לגמרי, שימושי כשרוצים למדוד
       אנרגיה בלי שהקרינה תבלבל את המספרים. */
    this.radiate = 0.004;
    this.reactions = 0;                                 // מונה לצורכי בדיקה
  }

  /* מספרים אקראיים עם זרע — כדי שבדיקה שנכשלה תיכשל שוב באותה צורה */
  rnd() { let x = this.s; x ^= x << 13; x ^= x >>> 17; x ^= x << 5; this.s = x >>> 0; return this.s / 4294967296; }
  rndInt(k) { return Math.floor(this.rnd() * k) % k; }

  idx(x, y) { return y * this.w + x; }
  inside(x, y) { return x >= 0 && y >= 0 && x < this.w && y < this.h; }
  at(i) { return this.sub[i] === EMPTY ? null : subById(this.sub[i]); }

  /* ---------- כתיבה לעולם ---------- */
  set(x, y, keyOrNull, T, form) {
    if (!this.inside(x, y)) return;
    const i = this.idx(x, y);
    if (keyOrNull === null) { this.clear(i); return; }
    const s = sub_(keyOrNull);
    this.sub[i] = s.id;
    this.temp[i] = T === undefined ? this.ambient : clampT(T);
    this.phase[i] = stateOf(s, this.temp[i]);
    this.form[i] = form === undefined ? (this.phase[i] === SOLID ? GRAIN : BULK) : form;
    this.prog[i] = 0;
  }
  clear(i) { this.sub[i] = EMPTY; this.temp[i] = this.ambient; this.prog[i] = 0; this.form[i] = 0; this.phase[i] = 0; }
  fill(x0, y0, x1, y1, key, T, form) {
    for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) this.set(x, y, key, T, form);
  }
  count(key) {
    const id = sub_(key).id; let n = 0;
    for (let i = 0; i < this.n; i++) if (this.sub[i] === id) n++;
    return n;
  }

  /* ---------- תכונות של תא ---------- */
  den(i) { const s = this.at(i); return s ? density(s, this.temp[i], this.phase[i]) : 0; }
  cap(i) { const s = this.at(i); return s ? heatCap(s) : 0.02; }
  cond(i) { const s = this.at(i); return s ? conductivity(s, this.temp[i], this.phase[i]) : 0; }
  color(i) { const s = this.at(i); return s ? color(s, this.temp[i], this.phase[i]) : null; }

  /* ---------- ספירת אטומים בכל העולם ----------
     הבדיקה החשובה ביותר במשחק. אם המספר הזה משתנה בלי שנגענו בעולם — יש באג
     שמוחק או ממציא חומר. במשחק הישן זה קרה שוב ושוב.                      */
  /* סך האנרגיה התרמית בעולם — כולל מה שנצבר לשינוי מצב שעוד לא הושלם.
     משמש לבדיקה שחום לא נעלם בשקט. */
  energy() {
    let e = 0;
    for (let i = 0; i < this.n; i++) {
      const s = this.at(i); if (!s) continue;
      e += heatCap(s) * this.temp[i] + this.prog[i];
    }
    return e;
  }

  census() {
    const c = {};
    for (let i = 0; i < this.n; i++) {
      const s = this.at(i); if (!s) continue;
      for (const e in s.comp) c[e] = (c[e] || 0) + s.comp[e];
    }
    return c;
  }

  /* ======================================================================
     צעד זמן
     ====================================================================== */
  step() {
    this.tick++;
    this.doReactions();
    this.doPhases();
    this.doConduction();
    this.computeSupport();
    this.doMotion();
  }
  run(n) { for (let k = 0; k < n; k++) this.step(); }

  /* ----------------------------------------------------------------------
     1) תגובות — החוק היחיד, מופעל על שכנים
     ----------------------------------------------------------------------
     המנוע אומר "2 תאים של A עם תא של B נותנים 2 תאים של C". כאן בודקים אם
     באמת יש מספיק תאים כאלה בסביבה הקרובה, ואם יש מקום לתוצרים. אם אין —
     שום דבר לא קורה. זה גם מה שייתן בהמשך לחץ: תגובה שמייצרת יותר תאים
     ממה שצרכה זקוקה למקום פנוי.                                          */
  doReactions() {
    const { w, h } = this;
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      if (this.rnd() > 0.30) continue;         // לא כל תא בכל צעד — מרכך ומאיץ
      this.tryReact(x, y);
    }
  }
  tryReact(x, y) {
    const i = this.idx(x, y);
    const a = this.sub[i]; if (a === EMPTY) return false;
    const d = D8[this.rndInt(8)];
    const tx = x + d[0], ty = y + d[1];
    if (!this.inside(tx, ty)) return false;
    const j = this.idx(tx, ty);
    const b = this.sub[j]; if (b === EMPTY) return false;

    const T = (this.temp[i] + this.temp[j]) / 2;
    const r = reaction(a, b, T);
    if (!r) return false;

    /* אוספים את התאים הדרושים מתוך ריבוע 3×3 סביב i */
    const box = [];
    for (let yy = y - 1; yy <= y + 1; yy++) for (let xx = x - 1; xx <= x + 1; xx++)
      if (this.inside(xx, yy)) box.push(this.idx(xx, yy));

    const used = [];
    if (a === b) {
      for (const k of box) if (this.sub[k] === a && used.length < r.nA + r.nB) used.push(k);
      if (used.length < r.nA + r.nB) return false;
    } else {
      let na = 0, nb = 0;
      for (const k of box) if (this.sub[k] === a && na < r.nA) { used.push(k); na++; }
      for (const k of box) if (this.sub[k] === b && nb < r.nB) { used.push(k); nb++; }
      if (na < r.nA || nb < r.nB) return false;
    }

    /* מקום לתוצרים: קודם התאים שהתפנו, ואם צריך עוד — תאים ריקים בסביבה */
    const nOut = r.pk + r.qk;
    const slots = used.slice();
    if (nOut > slots.length) {
      for (const k of box) {
        if (slots.length >= nOut) break;
        if (this.sub[k] === EMPTY && !slots.includes(k)) slots.push(k);
      }
      if (slots.length < nOut) return false;   // אין מקום — התגובה לא קורית
    }

    /* אנרגיה: כל האנרגיה שהשתחררה מתחלקת על התוצרים לפי קיבול החום שלהם */
    const P = subById(r.p), Q = r.q != null ? subById(r.q) : null;
    let capTot = heatCap(P) * r.pk + (Q ? heatCap(Q) * r.qk : 0);
    const dT = Math.min(4000, (r.gain * HEAT_YIELD) / Math.max(0.01, capTot));
    const newT = clampT(T + dT);

    for (let k = 0; k < r.pk; k++) this.place(slots[k], P, newT);
    for (let k = 0; k < r.qk; k++) this.place(slots[r.pk + k], Q, newT);
    for (let k = nOut; k < slots.length; k++) this.clear(slots[k]);   // נפח קטן

    this.reactions++;
    return true;
  }
  /* תוצר מוצק נולד כאבקה — ככה זה נראה כשחומר מתגבש מתגובה, לא כלבנה שלמה */
  place(i, s, T) {
    this.sub[i] = s.id;
    this.temp[i] = T;
    this.phase[i] = stateOf(s, T);
    this.form[i] = this.phase[i] === SOLID ? GRAIN : BULK;
    this.prog[i] = 0;
  }

  /* ----------------------------------------------------------------------
     2) שינויי מצב — עם חום כמוס
     ----------------------------------------------------------------------
     כשתא מגיע לנקודת ההיתוך או הרתיחה הוא *נעצר* שם, וכל האנרגיה הנוספת
     נכנסת למונה prog. רק כשהמונה מגיע לחום הכמוס המצב באמת משתנה. בלי זה
     כוס מים הייתה הופכת לענן בפריים אחד.                                 */
  doPhases() {
    for (let i = 0; i < this.n; i++) {
      const s = this.at(i); if (!s) continue;
      let T = this.temp[i];
      T = this.temp[i] = clampT(T);
      const c = heatCap(s), ph = this.phase[i];

      /* איזה מעבר ממתין, לאיזה כיוון, ובאיזה מחיר */
      let dir = 0, edge = 0, need = 0, target = 0;
      /* גדול-או-שווה בכוונה: תא שכבר נעצר על נקודת המעבר חייב *להישאר* שם
         ולשמור על מה שצבר. עם "גדול" לבד הוא היה משחרר הכל בחזרה בצעד הבא
         ומקפץ בין 100 ל-130 בלי סוף. */
      if      (ph === SOLID  && T >= s.melt) { dir = +1; edge = s.melt; need = latentFus(s); target = LIQUID; }
      else if (ph === LIQUID && T <= s.melt) { dir = -1; edge = s.melt; need = latentFus(s); target = SOLID;  }
      else if (ph === LIQUID && T >= s.boil) { dir = +1; edge = s.boil; need = latentVap(s); target = GAS;    }
      else if (ph === GAS    && T <= s.boil) { dir = -1; edge = s.boil; need = latentVap(s); target = LIQUID; }

      if (dir === 0) { this.release(i, c); continue; }
      if (this.prog[i] * dir < 0) this.release(i, c);   // הכיוון התחלף — מחזירים קודם

      /* התא נעצר על נקודת המעבר, וכל האנרגיה שמעבר לה נצברת במונה */
      this.temp[i] = edge;
      this.prog[i] += dir * Math.abs(T - edge) * c;
      if (Math.abs(this.prog[i]) < need) continue;

      const left = Math.abs(this.prog[i]) - need;
      this.prog[i] = 0;
      this.phase[i] = target;
      this.temp[i] = clampT(edge + dir * (left / c));
      /* נוזל שהתמצק מתלכד לגוש. ככה חול מותך שהתקרר הופך לזכוכית, בלי שאף
         אחד כתב חוק כזה. */
      if (target === SOLID) this.form[i] = BULK;
    }
  }
  /* אנרגיה שנצברה למעבר שלא הושלם חייבת לחזור לטמפרטורה. אם פשוט מאפסים
     את המונה, החום הזה נמחק מהעולם — בדיוק סוג הדליפה השקטה שאי אפשר
     לראות במסך אבל היא משנה כל תוצאה. */
  release(i, c) {
    if (!this.prog[i]) return;
    this.temp[i] = clampT(this.temp[i] + this.prog[i] / c);
    this.prog[i] = 0;
  }

  /* ----------------------------------------------------------------------
     3) מוליכות חום
     ----------------------------------------------------------------------
     כל זוג שכנים מתקרב לטמפרטורת שיווי המשקל המשותפת שלהם. החישוב לפי
     אנרגיה ולא לפי טמפרטורה, ולכן חום לא נוצר ולא נעלם — תא קטן שמתחמם
     חייב לקרר מישהו אחר בדיוק באותה אנרגיה.                              */
  doConduction() {
    const { w, h, temp, dT } = this;
    dT.fill(0);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const i = this.idx(x, y);
      if (this.sub[i] === EMPTY) continue;
      for (let k = 0; k < 2; k++) {
        const nx = x + (k === 0 ? 1 : 0), ny = y + (k === 0 ? 0 : 1);
        if (!this.inside(nx, ny)) continue;
        const j = this.idx(nx, ny);
        if (this.sub[j] === EMPTY) continue;
        const ci = this.cap(i), cj = this.cap(j);
        const eq = (ci * temp[i] + cj * temp[j]) / (ci + cj);
        const k2 = Math.min(this.cond(i), this.cond(j)) * 0.25;
        dT[i] += (eq - temp[i]) * k2;
        dT[j] += (eq - temp[j]) * k2;
      }
    }
    /* קרינה: כל דבר חם מאבד אנרגיה לסביבה. בלי זה אש נדלקת ולא נכבית לעולם. */
    for (let i = 0; i < this.n; i++) {
      if (this.sub[i] === EMPTY) continue;
      let t = temp[i] + dT[i];
      t -= (t - this.ambient) * this.radiate;
      temp[i] = clampT(t);
    }
  }

  /* ----------------------------------------------------------------------
     4) תמיכה — למה קיר לא נופל
     ----------------------------------------------------------------------
     גוש מוצק נשאר במקומו רק אם יש שרשרת מוצקים ממנו עד לקרקע. זה בדיוק
     הבאג שהיה במשחק הישן: שם נבדק רק "יש שכן?", ולכן שני בלוקים באוויר
     החזיקו זה את זה וריחפו.                                              */
  computeSupport() {
    const { w, h, sup, stack } = this;
    sup.fill(0);
    let top = 0;
    for (let x = 0; x < w; x++) {
      const i = this.idx(x, h - 1);
      if (this.sub[i] !== EMPTY && this.phase[i] === SOLID) { sup[i] = 1; stack[top++] = i; }
    }
    while (top > 0) {
      const i = stack[--top];
      const x = i % w, y = (i / w) | 0;
      for (let k = 0; k < 4; k++) {
        const nx = x + (k === 0 ? -1 : k === 1 ? 1 : 0), ny = y + (k === 2 ? -1 : k === 3 ? 1 : 0);
        if (!this.inside(nx, ny)) continue;
        const j = this.idx(nx, ny);
        if (sup[j] || this.sub[j] === EMPTY || this.phase[j] !== SOLID) continue;
        sup[j] = 1; stack[top++] = j;
      }
    }
  }

  /* ----------------------------------------------------------------------
     5) תנועה
     ----------------------------------------------------------------------
     אין כאן "חול נופל" או "מים זורמים". יש מצב צבירה וצפיפות, ומזה נובע
     הכל: מה שכבד שוקע, מה שקל עולה, נוזל מתפשט, גז ממלא כל חלל.          */
  doMotion() {
    const { w, h } = this;
    this.done.fill(0);
    const rtl = (this.tick & 1) === 1;         // לסירוגין, אחרת הכל נוטה לצד אחד
    for (let y = h - 1; y >= 0; y--) {
      for (let c = 0; c < w; c++) {
        const x = rtl ? w - 1 - c : c;
        const i = this.idx(x, y);
        if (this.sub[i] === EMPTY || this.done[i]) continue;
        this.moveCell(i, x, y);
      }
    }
  }
  moveCell(i, x, y) {
    const ph = this.phase[i];
    if (ph === SOLID) {
      if (this.form[i] === BULK) {
        if (this.sup[i]) return false;         // מחובר לקרקע — לא זז
        return this.sink(i, x, y, x, y + 1);   // גוש חופשי נופל ישר
      }
      if (this.sink(i, x, y, x, y + 1)) return true;
      const d = this.rnd() < 0.5 ? 1 : -1;     // גרגר מחליק ויוצר ערימה
      return this.sink(i, x, y, x + d, y + 1) || this.sink(i, x, y, x - d, y + 1);
    }
    if (ph === LIQUID) return this.liquidStep(i, x, y);
    return this.gasStep(i, x, y);
  }

  /* מעבר לתא יעד: לתוך ריק תמיד; החלפה עם נוזל/גז רק אם היא מסדרת את
     הצפיפות — כבד למטה, קל למעלה. הסייג הזה הוא מה שמונע ריצוד אינסופי. */
  sink(i, x, y, tx, ty, allowEmpty = true) {
    if (!this.inside(tx, ty)) return false;
    const j = this.idx(tx, ty);
    if (this.done[j]) return false;
    if (this.sub[j] === EMPTY) { if (!allowEmpty) return false; this.move(i, j); return true; }
    if (this.phase[j] === SOLID) return false;
    if (this.den(j) < this.den(i) * 0.995) { this.swap(i, j); return true; }
    return false;
  }
  /* אין כאן פונקציית "עלייה", בכוונה.
     ציפה היא סימטרית: אם הקל עולה, זה בדיוק אותו דבר כמו שהכבד שמעליו יורד.
     היה כאן קוד נפרד לעלייה, ובבדיקה התברר שאפשר למחוק אותו בלי ששום בדיקה
     תרגיש — כי sink כבר עושה את העבודה משני הכיוונים. פחות קוד, פחות מקום
     לבאג להתחבא בו.
     בנוסף: ציפה דורשת חומר להדוף. בלון לא עולה בוואקום. לכן גז לא "עולה"
     לתוך ריק — הוא רק מתפשט לכל הכיוונים. */
  side(i, x, y, allowSwap) {
    const d = this.rnd() < 0.5 ? 1 : -1;
    for (const dx of [d, -d]) {
      if (!this.inside(x + dx, y)) continue;
      const j = this.idx(x + dx, y);
      if (this.done[j]) continue;
      if (this.sub[j] === EMPTY) { this.move(i, j); return true; }
      if (allowSwap && this.phase[j] === GAS && this.phase[i] === LIQUID) { this.swap(i, j); return true; }
    }
    return false;
  }
  liquidStep(i, x, y) {
    if (this.sink(i, x, y, x, y + 1)) return true;
    const d = this.rnd() < 0.5 ? 1 : -1;
    if (this.sink(i, x, y, x + d, y + 1)) return true;
    if (this.sink(i, x, y, x - d, y + 1)) return true;
    return this.side(i, x, y, true);           // מתפשט עד שהמפלס מתיישר
  }
  gasStep(i, x, y) {
    /* ציפה — רק מול חומר אחר, לא לתוך ריק */
    if (this.rnd() < 0.65) {
      if (this.sink(i, x, y, x, y + 1, false)) return true;      // כבד מהסביבה — שוקע
    }
    /* התפשטות: גז ממלא כל חלל פנוי, לכל כיוון. אין כאן העדפה למעלה —
       בוואקום אין למה לצוף, ולכן גז פשוט מתפזר. */
    const d = D8[this.rndInt(8)];
    if (this.inside(x + d[0], y + d[1])) {
      const j = this.idx(x + d[0], y + d[1]);
      if (!this.done[j] && this.sub[j] === EMPTY) { this.move(i, j); return true; }
    }
    /* דיפוזיה: שני גזים שכנים מתערבבים גם בלי הפרש צפיפות */
    const s = this.rnd() < 0.5 ? 1 : -1;
    for (const dx of [s, -s]) {
      if (!this.inside(x + dx, y)) continue;
      const j = this.idx(x + dx, y);
      if (this.done[j]) continue;
      if (this.phase[j] === GAS && this.sub[j] !== this.sub[i] && this.rnd() < 0.25) { this.swap(i, j); return true; }
    }
    return false;
  }

  move(i, j) {
    this.sub[j] = this.sub[i]; this.temp[j] = this.temp[i];
    this.phase[j] = this.phase[i]; this.form[j] = this.form[i]; this.prog[j] = this.prog[i];
    this.clear(i);
    this.done[j] = 1;
  }
  swap(i, j) {
    const a = this.sub[i], b = this.temp[i], c = this.phase[i], d = this.form[i], e = this.prog[i];
    this.sub[i] = this.sub[j]; this.temp[i] = this.temp[j]; this.phase[i] = this.phase[j];
    this.form[i] = this.form[j]; this.prog[i] = this.prog[j];
    this.sub[j] = a; this.temp[j] = b; this.phase[j] = c; this.form[j] = d; this.prog[j] = e;
    this.done[i] = 1; this.done[j] = 1;
  }
}
