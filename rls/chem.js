/* ============================================================================
   RLS — Real Life Simulator · מנוע הכימיה
   ============================================================================

   העיקרון: אין "חומרים" מקודדים. יש *אטומים*, ויש חוק אחד שמחליט מה קורה
   כשהם נפגשים. כל השאר נגזר מזה.

   למה זה שונה מהמשחק הקודם:
     קודם — לכל זוג חומרים היה חוק ידני משלו. 60 פונקציות. כל חומר חדש דרש
             לכתוב עוד N חוקים, וכל חוק שנשכח היה באג (מים שלא עברו מחול
             לאדמה היה בדיוק זה — אף אחד לא כתב את החוק ההוא).
     עכשיו — תא מחזיק *אילו אטומים יש בו*. חוק אחד בודק אם סידור מחדש של
             האטומים משחרר אנרגיה. אם כן — זה קורה. זה הכל.

   התכונה החשובה ביותר: **שימור חומר לפי בנייה, לא לפי זהירות.**
   החיפוש שוקל רק חלוקות שמשמרות בדיוק את אותם אטומים, ולכן אי אפשר
   ליצור או למחוק חומר גם אם נכתוב באג. במשחק הישן זה היה מקור לחצי מהבאגים.

   ============================================================================ */

/* ---------------------------------------------------------------------------
   1) יסודות — נתונים אמיתיים
   Z = מספר אטומי · m = מסה אטומית · en = אלקטרושליליות (פאולינג)
   ve = אלקטרונים בקליפה החיצונית · col = צבע לתצוגה
   --------------------------------------------------------------------------- */
export const EL = {
  H : {Z:1,  m:1.008,  en:2.20, ve:1, name:'מימן',      col:[235,240,248]},
  He: {Z:2,  m:4.003,  en:0,    ve:2, name:'הליום',     col:[190,235,230]},
  C : {Z:6,  m:12.011, en:2.55, ve:4, name:'פחמן',      col:[ 58, 58, 66]},
  N : {Z:7,  m:14.007, en:3.04, ve:5, name:'חנקן',      col:[ 90,110,225]},
  O : {Z:8,  m:15.999, en:3.44, ve:6, name:'חמצן',      col:[225, 80, 80]},
  Na: {Z:11, m:22.990, en:0.93, ve:1, name:'נתרן',      col:[175,100,210]},
  Mg: {Z:12, m:24.305, en:1.31, ve:2, name:'מגנזיום',   col:[105,195,145]},
  Al: {Z:13, m:26.982, en:1.61, ve:3, name:'אלומיניום', col:[185,188,196]},
  Si: {Z:14, m:28.085, en:1.90, ve:4, name:'צורן',      col:[130,140,150]},
  P : {Z:15, m:30.974, en:2.19, ve:5, name:'זרחן',      col:[232,138, 42]},
  S : {Z:16, m:32.06,  en:2.58, ve:6, name:'גופרית',    col:[232,210, 58]},
  Cl: {Z:17, m:35.45,  en:3.16, ve:7, name:'כלור',      col:[ 90,200, 95]},
  K : {Z:19, m:39.098, en:0.82, ve:1, name:'אשלגן',     col:[143, 64,212]},
  Ca: {Z:20, m:40.078, en:1.00, ve:2, name:'סידן',      col:[ 78,180, 98]},
  Fe: {Z:26, m:55.845, en:1.83, ve:2, name:'ברזל',      col:[188,132, 90]},
  Cu: {Z:29, m:63.546, en:1.90, ve:2, name:'נחושת',     col:[200,128, 77]},
  Zn: {Z:30, m:65.38,  en:1.65, ve:2, name:'אבץ',       col:[168,176,184]},
  Sn: {Z:50, m:118.71, en:1.96, ve:4, name:'בדיל',      col:[154,160,168]},
  Au: {Z:79, m:196.97, en:2.54, ve:1, name:'זהב',       col:[245,197, 24]},
  Hg: {Z:80, m:200.59, en:2.00, ve:2, name:'כספית',     col:[166,168,176]},
};

/* ---------------------------------------------------------------------------
   2) הרכב — "חומר" הוא רק אוסף אטומים
   מיוצג כאובייקט {H:2, O:1}. המפתח הקנוני "H2O" משמש לחיפוש מהיר.
   --------------------------------------------------------------------------- */
export function key(comp){
  return Object.keys(comp).sort().filter(e=>comp[e]>0)
    .map(e => e + (comp[e]>1 ? comp[e] : '')).join('');
}
export function parse(k){                    // "H2O" -> {H:2,O:1}
  const c={}; const re=/([A-Z][a-z]?)(\d*)/g; let m;
  while((m=re.exec(k))!==null){ if(!m[1]) continue; c[m[1]]=(c[m[1]]||0)+(m[2]?+m[2]:1); }
  return c;
}
export const add = (a,b) => { const o={...a}; for(const e in b) o[e]=(o[e]||0)+b[e]; return o; };
export function sub(a,b){                    // a-b, או null אם b לא נכנס בתוך a
  const o={...a};
  for(const e in b){ if((o[e]||0) < b[e]) return null; o[e]-=b[e]; if(!o[e]) delete o[e]; }
  return o;
}
export const empty = c => Object.keys(c).length===0;
export const atoms = c => Object.values(c).reduce((a,b)=>a+b,0);
export const molarMass = c => Object.keys(c).reduce((s,e)=>s+(EL[e]?EL[e].m*c[e]:0),0);

/* ---------------------------------------------------------------------------
   3) חומרים מוכרים — נתונים אמיתיים
   dHf = אנתלפיית היווצרות בתנאי תקן, kJ/mol. זה המספר שמחליט הכל:
         ככל שהוא נמוך יותר, החומר יציב יותר ו"רוצה" להתקיים.
   melt/boil במעלות צלזיוס. state = מצב הצבירה בטמפ' החדר.
   כל מה שלא נמצא כאן עדיין יכול להיווצר — התכונות שלו ייגזרו (ראה derive).
   --------------------------------------------------------------------------- */
export const KNOWN = {
  // יסודות במצבם הטבעי — לפי הגדרה dHf=0
  'H2'   :{name:'מימן',          dHf:0,     melt:-259, boil:-253, col:[235,240,248], st:'gas'},
  'O2'   :{name:'חמצן',          dHf:0,     melt:-219, boil:-183, col:[225, 80, 80], st:'gas'},
  'N2'   :{name:'חנקן',          dHf:0,     melt:-210, boil:-196, col:[ 90,110,225], st:'gas'},
  'Cl2'  :{name:'כלור',          dHf:0,     melt:-101, boil: -34, col:[150,215,110], st:'gas'},
  'C'    :{name:'פחמן',          dHf:0,     melt:3550, boil:4027, col:[ 58, 58, 66], st:'solid'},
  'S'    :{name:'גופרית',        dHf:0,     melt: 115, boil: 445, col:[232,210, 58], st:'solid'},
  'Fe'   :{name:'ברזל',          dHf:0,     melt:1538, boil:2861, col:[188,132, 90], st:'solid'},
  'Cu'   :{name:'נחושת',         dHf:0,     melt:1085, boil:2562, col:[200,128, 77], st:'solid'},
  'Zn'   :{name:'אבץ',           dHf:0,     melt: 420, boil: 907, col:[168,176,184], st:'solid'},
  'Al'   :{name:'אלומיניום',     dHf:0,     melt: 660, boil:2470, col:[185,188,196], st:'solid'},
  'Na'   :{name:'נתרן',          dHf:0,     melt:  98, boil: 883, col:[175,100,210], st:'solid'},
  'K'    :{name:'אשלגן',         dHf:0,     melt:  63, boil: 759, col:[143, 64,212], st:'solid'},
  'Ca'   :{name:'סידן',          dHf:0,     melt: 842, boil:1484, col:[ 78,180, 98], st:'solid'},
  'Mg'   :{name:'מגנזיום',       dHf:0,     melt: 650, boil:1090, col:[105,195,145], st:'solid'},
  'Si'   :{name:'צורן',          dHf:0,     melt:1414, boil:3265, col:[130,140,150], st:'solid'},
  'Sn'   :{name:'בדיל',          dHf:0,     melt: 232, boil:2602, col:[154,160,168], st:'solid'},
  'Au'   :{name:'זהב',           dHf:0,     melt:1064, boil:2856, col:[245,197, 24], st:'solid'},
  'Hg'   :{name:'כספית',         dHf:0,     melt: -39, boil: 357, col:[166,168,176], st:'liquid'},
  'P4'   :{name:'זרחן לבן',      dHf:0,     melt:  44, boil: 280, col:[232,138, 42], st:'solid'},

  // תרכובות — dHf אמיתי
  'H2O'  :{name:'מים',           dHf:-286,  melt:   0, boil: 100, col:[ 60,120,220], st:'liquid'},
  'CO2'  :{name:'פחמן דו-חמצני', dHf:-394,  melt: -57, boil: -78, col:[200,205,215], st:'gas'},
  'CO'   :{name:'פחמן חד-חמצני', dHf:-111,  melt:-205, boil:-192, col:[190,195,205], st:'gas'},
  'CH4'  :{name:'מתאן',          dHf: -75,  melt:-182, boil:-162, col:[210,225,235], st:'gas'},
  'NH3'  :{name:'אמוניה',        dHf: -46,  melt: -78, boil: -33, col:[170,210,235], st:'gas'},
  'NaCl' :{name:'מלח בישול',     dHf:-411,  melt: 801, boil:1465, col:[240,240,245], st:'solid'},
  'KCl'  :{name:'אשלגן כלורי',   dHf:-437,  melt: 770, boil:1420, col:[238,232,245], st:'solid'},
  'HCl'  :{name:'מימן כלורי',    dHf: -92,  melt:-114, boil: -85, col:[205,235,200], st:'gas'},
  'SO2'  :{name:'גופרית דו-חמצנית',dHf:-297,melt: -72, boil: -10, col:[225,215,120], st:'gas'},
  'SO3'  :{name:'גופרית תלת-חמצנית',dHf:-396,melt: 17, boil:  45, col:[230,220,140], st:'gas'},
  'H2S'  :{name:'מימן גופרתי',   dHf: -21,  melt: -82, boil: -60, col:[220,215,150], st:'gas'},
  'NO'   :{name:'תחמוצת חנקן',   dHf:  90,  melt:-164, boil:-152, col:[160,170,215], st:'gas'},
  'NO2'  :{name:'דו-תחמוצת חנקן',dHf:  33,  melt: -11, boil:  21, col:[200,120, 60], st:'gas'},
  'Fe2O3':{name:'חלודה',         dHf:-824,  melt:1565, boil:2861, col:[150, 70, 40], st:'solid'},
  'FeS'  :{name:'גופרת ברזל',    dHf:-100,  melt:1194, boil:2861, col:[120, 95, 70], st:'solid'},
  'CuO'  :{name:'תחמוצת נחושת',  dHf:-157,  melt:1326, boil:2000, col:[ 60, 55, 60], st:'solid'},
  'ZnO'  :{name:'תחמוצת אבץ',    dHf:-348,  melt:1974, boil:2360, col:[235,235,230], st:'solid'},
  'Al2O3':{name:'תחמוצת אלומיניום',dHf:-1676,melt:2072,boil:2977, col:[225,225,232], st:'solid'},
  'MgO'  :{name:'מגנזיה',        dHf:-601,  melt:2852, boil:3600, col:[240,240,238], st:'solid'},
  'CaO'  :{name:'סיד חי',        dHf:-635,  melt:2613, boil:2850, col:[238,235,225], st:'solid'},
  'SiO2' :{name:'צורן דו-חמצני', dHf:-911,  melt:1670, boil:2950, col:[224,196,120], st:'solid'},
  'NaOH' :{name:'סודה קאוסטית',  dHf:-425,  melt: 318, boil:1388, col:[235,225,240], st:'solid'},
  'CaCO3':{name:'אבן גיר',       dHf:-1207, melt: 825, boil: 825, col:[228,222,205], st:'solid'},
  'H2O2' :{name:'מי חמצן',       dHf:-188,  melt:  -1, boil: 150, col:[190,225,240], st:'liquid'},
  'NaH'  :{name:'נתרן הידריד',   dHf: -56,  melt: 638, boil: 638, col:[200,170,220], st:'solid'},
};

/* ---------------------------------------------------------------------------
   4) גזירת תכונות — לחומר שאיש לא רשם
   זה מה שמאפשר לתרכובות *חדשות* להופיע בלי שנכתוב להן שורה.
   הערכות גסות, ומסומנות ככאלה: derived=true.
   --------------------------------------------------------------------------- */
export function derive(comp){
  const els = Object.keys(comp);
  const mm  = molarMass(comp);
  // ככל שהפרש האלקטרושליליות גדול יותר הקשר יוני וחזק יותר → נקודת היתוך גבוהה
  let mx=0, mn=9;
  for(const e of els){ const en=EL[e]?EL[e].en:2; if(en>mx)mx=en; if(en<mn)mn=en; }
  const ionic = Math.max(0, mx-mn);
  const melt  = Math.round(-100 + ionic*420 + Math.min(mm,200)*1.6);
  const boil  = Math.round(melt + 180 + ionic*260);
  // צבע = ממוצע משוקלל של צבעי היסודות
  const col=[0,0,0]; let n=0;
  for(const e of els){ const c=EL[e]?EL[e].col:[128,128,128];
    for(let k=0;k<3;k++) col[k]+=c[k]*comp[e]; n+=comp[e]; }
  return { name:key(comp), dHf:estimateDHf(comp), melt, boil,
           col: col.map(v=>Math.round(v/Math.max(1,n))),
           st: melt>25 ? 'solid' : boil>25 ? 'liquid' : 'gas',
           derived:true };
}
/* הערכת יציבות לתרכובת לא מוכרת. הפרש אלקטרושליליות גדול = קשר חזק = יציב.
   שמרני בכוונה: תרכובת מנוחשת לא תנצח תרכובת אמיתית שנמדדה במעבדה. */
function estimateDHf(comp){
  const els=Object.keys(comp); if(els.length<2) return 0;
  let mx=0, mn=9;
  for(const e of els){ const en=EL[e]?EL[e].en:2; if(en>mx)mx=en; if(en<mn)mn=en; }
  // מתכות אצילות לא מתחמצנות. זהב חשוף לחמצן כבר אלפי שנים ועדיין נוצץ —
  // בלי החוק הזה המנוע המציא "AuO" והחליט שהוא יציב.
  const noble = els.some(e => e==='Au' || e==='Hg');
  if(noble) return +40;                      // חיובי = לא יציב, לא ייווצר מעצמו
  // שמרני בכוונה: ניחוש לא אמור לנצח מדידה אמיתית מהמעבדה.
  return -Math.round((mx-mn) * 22 * atoms(comp) * 0.5);
}

/* ---------------------------------------------------------------------------
   5) רישום החומרים — כל חומר מקבל מזהה מספרי לשימוש ברשת
   --------------------------------------------------------------------------- */
const byKey = new Map(), list = [];
export function sub_(k){                        // מחזיר (ויוצר אם צריך) חומר
  if(byKey.has(k)) return byKey.get(k);
  const comp = parse(k);
  const info = KNOWN[k] ? {...KNOWN[k]} : derive(comp);
  const rec = { id:list.length, key:k, comp, ...info };
  list.push(rec); byKey.set(k,rec);
  return rec;
}
export const subById = id => list[id];
export const allSubs = () => list.slice();
/* הרשימה הקבועה שנטענה מהטבלה. חשוב: list גדל תוך כדי ריצה (כל שארית
   סבירה נרשמת), ולכן סריקה של כל הצמדים חייבת לרוץ על *הבסיס* ולא על
   הרשימה המתפתחת — אחרת היא גדלה בזמן שסורקים אותה. */
let BASE=null;
export const baseSubs = () => (BASE || (BASE = list.slice()));
for(const k in KNOWN) sub_(k);                  // לטעון מראש את המוכרים

/* ---------------------------------------------------------------------------
   6) החוק היחיד
   ---------------------------------------------------------------------------
   בטבע, מה שמחליט אם תגובה קורית זה אנרגיה: אם לתוצרים אנרגיה נמוכה יותר
   מלמקור, התגובה משחררת אנרגיה ו"רוצה" לקרות. הטמפרטורה נותנת את הדחיפה
   הראשונית (אנרגיית שפעול).

   החיפוש שוקל אך ורק חלוקות ששומרות *בדיוק* את אותם אטומים — ולכן שימור
   החומר מובטח מהמבנה, לא מזהירות בכתיבה.
   --------------------------------------------------------------------------- */
export const R = {
  minRelease: 60,      // כמה kJ/mol צריך להשתחרר כדי שנטרח בכלל
  actScale:   0.40,    // ככל שהתגובה משחררת יותר, קל יותר להצית אותה
  actBase:    520,     // מחסום הפתיחה הבסיסי במעלות
};

/* יסודות שבטבע לא קיימים כאטום בודד — הם תמיד זוגות. אטום חמצן בודד הוא
   לא "חומר", הוא רדיקל חופשי, ואסור שהמנוע ישאיר אותו כתוצר. */
const DIATOMIC = new Set(['H','O','N','Cl']);
function plausible(comp){
  const els=Object.keys(comp);
  if(els.length===0) return false;
  if(els.length===1){                       // יסוד טהור
    const e=els[0];
    if(DIATOMIC.has(e)) return comp[e]===2;    // בדיוק זוג: O2 כן, O לא, O4 לא קיים
    return comp[e]===1;                        // מוצק טהור — יחידה אחת
  }
  if(KNOWN[key(comp)]) return true;         // נמדד במעבדה — תמיד תקף
  if(els.length>3) return false;
  for(const e of els) if(comp[e]>6) return false;
  /* תרכובת שהמנוע *ניחש* חייבת להסתדר לפי ערכיות. בלי החוק הזה נרשמו
     19,000 חומרים כמו HN3 ו-H2N שאינם קיימים, וזה גם ניפח את הזיכרון. */
  if(els.length===2){
    const [a,b]=els, A=EL[a], B=EL[b];
    if(!A||!B) return false;
    // מי נותן אלקטרונים ומי לוקח — לפי אלקטרושליליות
    const [give,take] = A.en<B.en ? [a,b] : [b,a];
    const gv = EL[give].ve <= 4 ? EL[give].ve : 8-EL[give].ve;   // כמה נותן
    const tk = 8 - EL[take].ve;                                   // כמה צריך
    if(gv<=0 || tk<=0) return false;
    return comp[give]*gv === comp[take]*tk;    // חייב להתאזן בדיוק
  }
  return false;                              // שלישיות רק אם הן מוכרות
}
/* רשימת המועמדים נבנית *פעם אחת*. קודם היא נבנתה תוך כדי החיפוש, וכל שארית
   יצרה חומר חדש שהפך בעצמו למועמד — מה שגרם לרשימה לגדול בלי סוף והתקיעה
   את המנוע. עכשיו הרשימה קבועה, ולכן החיפוש חסום וצפוי. */
let POOL=null;
function pool(){
  if(POOL) return POOL;
  POOL = list.filter(s=>plausible(s.comp));
  return POOL;
}
const gcd=(a,b)=>b?gcd(b,a%b):a;
/* מצמצם נוסחה ליחס הפשוט ביותר: H4O2 → H2O פי 2. ככה מזהים שהשארית היא
   בעצם כמה עותקים של חומר אמיתי, ולא איזו מפלצת כמו "H4O2". */
function reduce(comp){
  const v=Object.values(comp); let g=v[0];
  for(const x of v) g=gcd(g,x);
  if(g<2) return {unit:comp, n:1};
  const u={}; for(const e in comp) u[e]=comp[e]/g;
  return {unit:u, n:g};
}
const mul=(comp,k)=>{ const o={}; for(const e in comp) o[e]=comp[e]*k; return o; };

/* חיפוש התגובה.
   כאן נמצא הלב: תגובות אמיתיות כמעט אף פעם אינן ביחס 1:1. שריפת מימן היא
   2H₂ + O₂ → 2H₂O, תרמיט הוא Fe₂O₃ + 2Al, מלח הוא 2Na + Cl₂. מודל של
   "תא אחד + תא אחד" פשוט לא מסוגל לבטא את זה, ולכן כל התגובות המפורסמות
   נכשלו. עכשיו החיפוש בודק גם *כמויות*: כמה תאים מכל צד, וכמה תאים תוצר.
   שכבת הרשת תחליט אחר כך אם באמת יש מספיק תאים שכנים. */
function search(A, B, T){
  let best=null, bestGain=0;
  for(const [nA,nB] of [[1,1],[2,1],[1,2],[3,1],[1,3],[2,3],[3,2]]){
    const total = add(mul(A.comp,nA), mul(B.comp,nB));
    const before = A.dHf*nA + B.dHf*nB;
    for(const P of pool()){
      for(let k=1;k<=4;k++){
        const taken = mul(P.comp,k);
        const rest = sub(total, taken);
        if(rest===null) break;                       // כבר לא נכנס, אין טעם להמשיך
        let Q=null, m=0;
        if(!empty(rest)){
          const r=reduce(rest);
          if(!plausible(r.unit)) continue;
          Q=sub_(key(r.unit)); m=r.n;
        }
        // אותה תוצאה כמו ההתחלה — לא תגובה
        if(!Q && P.id===A.id) continue;
        if(Q && ((P.id===A.id&&Q.id===B.id)||(P.id===B.id&&Q.id===A.id))) continue;
        const after = P.dHf*k + (Q?Q.dHf*m:0);
        const gain = before - after;
        if(gain < R.minRelease) continue;
        const need = Math.max(0, R.actBase - gain*R.actScale);
        if(T < need) continue;
        // מנרמלים לפי מספר האטומים, אחרת תגובה גדולה תמיד "מנצחת" סתם בגלל גודלה
        const score = gain / atoms(total);
        if(score > bestGain){
          bestGain = score;
          best = {nA, nB, p:P.id, pk:k, q:Q?Q.id:null, qk:m, gain:Math.round(gain), need:Math.round(need)};
        }
      }
    }
  }
  return best;
}

const memo = new Map();                       // ← זה מה שהופך את זה למהיר
export function reaction(aId, bId, T){
  // מחשבים פעם אחת לכל צירוף וטווח־טמפ', ואז זו רק קריאה מהמפה.
  const band = T<0 ? 0 : T<100 ? 1 : T<400 ? 2 : T<900 ? 3 : T<1600 ? 4 : 5;
  const mk = aId+','+bId+','+band;
  if(memo.has(mk)) return memo.get(mk);
  const r = search(list[aId], list[bId], T);
  memo.set(mk, r);
  return r;
}
export const memoSize = () => memo.size;
export const clearMemo = () => memo.clear();

/* בדיקת שפיות שאפשר להריץ מכל מקום: האם התגובה שמרה על האטומים? */
/* שימור חומר — עכשיו כולל את הכמויות. זו הבדיקה שמוודאת שהחוק לא יכול
   להמציא או למחוק אטומים, לא משנה איזה באג נכתוב מעליו. */
export function conserves(aId,bId,r){
  const t1 = add(mul(list[aId].comp, r.nA), mul(list[bId].comp, r.nB));
  let t2 = mul(list[r.p].comp, r.pk);
  if(r.q!=null) t2 = add(t2, mul(list[r.q].comp, r.qk));
  return key(t1)===key(t2);
}
