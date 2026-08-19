/* בדיקות לשכבת הרשת של RLS.
   הרצה:  node rls/test-world.mjs

   השאלה שכל בדיקה כאן שואלת: האם ההתנהגות באמת *נגזרת* מהנתונים הפיזיקליים,
   או שמישהו כתב אותה ביד? לכן כמעט כל בדיקה כאן היא על דבר שאיש לא תכנת:
   שהשמן יצוף, שהקרח יימס, שהחול יהפוך לזכוכית. */
import { World, EMPTY, BULK, GRAIN } from './game/world.js';
import { SOLID, LIQUID, GAS, stateOf, density, STATE_NAME } from './game/matter.js';
import { sub_, subById } from './game/chem.js';

let pass = 0, fail = 0;
const ok = (name, cond, detail) => {
  if (cond) { pass++; console.log('  ✔ ' + name + (detail ? '   ' + detail : '')); }
  else { fail++; console.log('  ✘ ' + name + (detail ? '   ' + detail : '')); }
};
const idOf = k => sub_(k).id;
/* ציור העולם כטקסט — כדי שכשבדיקה נכשלת אפשר יהיה לראות למה */
function draw(w, mark) {
  const ch = { }; let out = '';
  for (let y = 0; y < w.h; y++) {
    let row = '';
    for (let x = 0; x < w.w; x++) {
      const i = w.idx(x, y), s = w.at(i);
      if (!s) { row += '.'; continue; }
      let c = s.key[0];
      if (w.phase[i] === GAS) c = c.toLowerCase();
      if (w.phase[i] === LIQUID) c = '~';
      row += c;
    }
    out += '    ' + row + '\n';
  }
  return out;
}
const topOf = (w, key) => { const id = idOf(key);
  for (let y = 0; y < w.h; y++) for (let x = 0; x < w.w; x++) if (w.sub[w.idx(x, y)] === id) return y;
  return -1; };
const bottomOf = (w, key) => { const id = idOf(key);
  for (let y = w.h - 1; y >= 0; y--) for (let x = 0; x < w.w; x++) if (w.sub[w.idx(x, y)] === id) return y;
  return -1; };
const avgY = (w, key) => { const id = idOf(key); let s = 0, n = 0;
  for (let y = 0; y < w.h; y++) for (let x = 0; x < w.w; x++) if (w.sub[w.idx(x, y)] === id) { s += y; n++; }
  return n ? s / n : -1; };

/* ========================================================================= */
console.log('\n=== 1. כובד וערימות ===');
{
  const w = new World(11, 12);
  for (let x = 3; x <= 7; x++) w.set(x, 0, 'SiO2', 20, GRAIN);
  w.run(40);
  ok('חול נופל עד הקרקע', bottomOf(w, 'SiO2') === 11,
     'הגרגר התחתון בשורה ' + bottomOf(w, 'SiO2') + ' מתוך 11');
  ok('החול נשאר — לא נעלם בדרך', w.count('SiO2') === 5, w.count('SiO2') + ' תאים מתוך 5');
}
{
  /* שופכים חול מנקודה אחת. אם גרגר רק נופל ישר, ייווצר מגדל ברוחב 1.
     אם הוא גם מחליק הצידה — נוצרת ערימה משופעת, כמו בשעון חול אמיתי. */
  const w = new World(21, 16);
  for (let k = 0; k < 60; k++) { w.set(10, 0, 'SiO2', 20, GRAIN); w.run(4); }
  w.run(60);
  let width = 0, height = 0;
  for (let x = 0; x < 21; x++) { let n = 0;
    for (let y = 0; y < 16; y++) if (w.sub[w.idx(x, y)] !== EMPTY) n++;
    if (n) width++; height = Math.max(height, n); }
  ok('חול שנשפך מנקודה אחת בונה ערימה, לא מגדל', width > 5 && height > 1,
     'רוחב הערימה ' + width + ' · גובה ' + height + '\n' + draw(w));
}

console.log('\n=== 2. תמיכה — מה מרחף ומה נופל ===');
{
  const w = new World(9, 10);
  for (let x = 0; x < 9; x++) w.set(x, 9, 'Fe', 20, BULK);      // רצפה
  w.set(4, 8, 'Fe', 20, BULK); w.set(4, 7, 'Fe', 20, BULK);      // עמוד מחובר
  w.run(30);
  ok('עמוד מחובר לקרקע לא נופל', w.sub[w.idx(4, 7)] === idOf('Fe'), 'העמוד עומד');
}
{
  const w = new World(9, 10);
  for (let x = 0; x < 9; x++) w.set(x, 9, 'Fe', 20, BULK);
  w.set(4, 3, 'Fe', 20, BULK); w.set(5, 3, 'Fe', 20, BULK);      // שני גושים באוויר
  w.run(30);
  ok('שני גושים באוויר לא מחזיקים זה את זה', w.sub[w.idx(4, 3)] === EMPTY,
     'הבאג מהמשחק הישן — נפלו כמו שצריך');
}

console.log('\n=== 3. מצבי צבירה — אין קרח, מים ואדים בנפרד ===');
{
  const w = new World(5, 5, -30);
  w.set(2, 2, 'H2O', -30);
  ok('מים במינוס הם קרח', w.phase[w.idx(2, 2)] === SOLID, 'מצב: ' + STATE_NAME[w.phase[w.idx(2, 2)]]);
}
{
  const w = new World(5, 5, 30);
  w.set(2, 2, 'H2O', 200);
  ok('מים ב-200 מעלות הם אדים', w.phase[w.idx(2, 2)] === GAS, 'מצב: ' + STATE_NAME[w.phase[w.idx(2, 2)]]);
}
{
  const w = new World(7, 7, 400);                 // חדר לוהט
  for (let x = 0; x < 7; x++) w.set(x, 6, 'Fe', 400, BULK);
  w.set(3, 5, 'H2O', -40);                        // קוביית קרח
  const before = w.phase[w.idx(3, 5)];
  w.run(150);
  let melted = false, tempSeen = 0;
  for (let i = 0; i < w.n; i++) if (w.sub[i] === idOf('H2O')) { if (w.phase[i] !== SOLID) melted = true; tempSeen = w.temp[i]; }
  ok('קרח בחדר לוהט נמס', before === SOLID && melted, 'הגיע ל-' + tempSeen.toFixed(0) + '°');
}
{
  // חום כמוס: כוס מים על אש לא הופכת לענן בפריים אחד
  const w = new World(6, 8, 20);
  for (let x = 0; x < 6; x++) w.set(x, 7, 'Fe', 1200, BULK);
  for (let x = 1; x <= 4; x++) w.set(x, 6, 'H2O', 20);
  w.run(6);
  let stillLiquid = 0;
  for (let i = 0; i < w.n; i++) if (w.sub[i] === idOf('H2O') && w.phase[i] === LIQUID) stillLiquid++;
  ok('מים על אש לא מתאדים בבת אחת — חום כמוס עוצר אותם', stillLiquid > 0,
     stillLiquid + ' תאי מים עדיין נוזליים אחרי 6 צעדים');
  /* הלהבה דולקת — מחזיקים את הברזל חם, כמו גז פתוח מתחת לסיר */
  for (let k = 0; k < 400; k++) { for (let x = 0; x < 6; x++) w.temp[w.idx(x, 7)] = 1200; w.step(); }
  let gas = 0;
  for (let i = 0; i < w.n; i++) if (w.sub[i] === idOf('H2O') && w.phase[i] === GAS) gas++;
  ok('אבל בסוף הם כן רותחים', gas > 0, gas + ' תאי אדים');
}

{
  /* מדידה ישירה של השער: תא מים בודד שמישהו מחזיק על 120 מעלות. בלי חום
     כמוס הוא הופך לאדים בצעד אחד. עם חום כמוס הוא צריך לספוג 33 kJ קודם. */
  const w = new World(1, 1, 20);                  // תא בודד, שלא יברח למטה
  w.set(0, 0, 'H2O', 20);
  let steps = 0;
  while (w.phase[0] !== GAS && steps < 500) { w.temp[0] = 120; w.step(); steps++; }
  ok('רתיחה לוקחת זמן — היא סופגת אנרגיה, לא רק מגיעה למספר', steps > 5 && steps < 500,
     'נדרשו ' + steps + ' צעדים על 120 מעלות (בלי חום כמוס: צעד אחד)');
}
{
  /* מה שנכנס למעבר שלא הושלם חייב לחזור. מכבים את הקרינה כדי שהמספר יהיה נקי. */
  const w = new World(1, 1, 20); w.radiate = 0;
  w.set(0, 0, 'H2O', 20);
  w.temp[0] = 130; w.step();                      // נעצר על 100 ואוגר את העודף
  const stored = w.prog[0];
  w.temp[0] = 50;  w.step();                      // הפסקנו לחמם, והוא ירד מתחת לרתיחה
  ok('חום שנכנס לרתיחה שלא הושלמה חוזר, לא נמחק', w.temp[0] > 70,
     'נאגרו ' + stored.toFixed(2) + ' kJ · חזר ל-' + w.temp[0].toFixed(0) + '° במקום 50°');
}

console.log('\n=== 4. צפיפות — מה צף ומה שוקע ===');
{
  const w = new World(6, 12, 20);
  for (let x = 0; x < 6; x++) w.set(x, 11, 'Fe', 20, BULK);
  for (let y = 4; y <= 9; y++) for (let x = 0; x < 6; x++) w.set(x, y, 'H2O', 20);
  w.set(3, 4, 'Hg', 20);                              // כספית — כבדה פי 13
  w.run(120);
  const y = (() => { for (let i = 0; i < w.n; i++) if (w.sub[i] === idOf('Hg')) return (i / w.w) | 0; return -1; })();
  ok('כספית שוקעת דרך מים', y >= 9, 'הגיעה לשורה ' + y + ' מתוך 10 האפשריות');
}
{
  const w = new World(9, 12, 20);
  for (let x = 0; x < 9; x++) w.set(x, 11, 'Fe', 20, BULK);
  for (let y = 0; y <= 10; y++) for (let x = 0; x < 9; x++) w.set(x, y, 'N2', 20);   // אוויר
  for (let x = 3; x <= 5; x++) w.set(x, 5, 'CO2', 20);
  w.run(150);
  const co2 = avgY(w, 'CO2');
  ok('CO₂ כבד מהאוויר ושוקע', co2 > 5, 'גובה ממוצע ' + co2.toFixed(1) + ' (התחיל ב-5, גדול יותר = נמוך יותר)');
}
{
  const w = new World(9, 12, 20);
  for (let x = 0; x < 9; x++) w.set(x, 11, 'Fe', 20, BULK);
  for (let y = 0; y <= 10; y++) for (let x = 0; x < 9; x++) w.set(x, y, 'N2', 20);
  for (let x = 3; x <= 5; x++) w.set(x, 6, 'H2', 20);
  w.run(150);
  const h2 = avgY(w, 'H2');
  ok('מימן קל מהאוויר ועולה', h2 < 6, 'גובה ממוצע ' + h2.toFixed(1) + ' (התחיל ב-6)');
}

console.log('\n=== 5. חום ===');
{
  /* שני מוטות זהים, אותה טמפרטורה בקצה. השאלה כמה רחוק החום מגיע. */
  const w = new World(20, 3, 20);
  for (let x = 0; x < 20; x++) { w.set(x, 1, 'Fe', 20, BULK); w.set(x, 2, 'SiO2', 20, BULK); }
  for (let k = 0; k < 60; k++) { w.temp[w.idx(0, 1)] = 1000; w.temp[w.idx(0, 2)] = 1000; w.step(); }
  const fe = w.temp[w.idx(4, 1)], si = w.temp[w.idx(4, 2)];
  ok('מתכת מוליכה חום מהר יותר מאבן', fe > si + 5,
     'ברזל ' + fe.toFixed(0) + '° · צורן דו-חמצני ' + si.toFixed(0) + '°');
}
{
  const w = new World(9, 12, 20);
  for (let y = 0; y <= 11; y++) for (let x = 0; x < 9; x++) w.set(x, y, 'N2', 20);
  for (let x = 3; x <= 5; x++) w.temp[w.idx(x, 10)] = 600;      // כיס אוויר חם למטה
  w.run(60);
  let hotY = 0, tot = 0;
  for (let i = 0; i < w.n; i++) if (w.temp[i] > 120) { hotY += (i / w.w) | 0; tot++; }
  ok('אוויר חם עולה מעצמו — קונבקציה', tot > 0 && hotY / tot < 9,
     'מרכז החום בשורה ' + (tot ? (hotY / tot).toFixed(1) : '—') + ' (התחיל ב-10)');
}
{
  /* כותבים ישירות למערך הטמפרטורות, כדי לעקוף את הבדיקה שב-set ולבחון את
     ההגנה שבתוך הסימולציה עצמה. במשחק הישן חנקן נוזלי ירד מתחת לאפס המוחלט
     בדיוק ככה. */
  const w = new World(5, 5, -260); w.radiate = 0;
  w.set(2, 4, 'Fe', -260, BULK);
  w.temp[w.idx(2, 4)] = -9999;
  w.step();
  ok('אי אפשר לרדת מתחת לאפס המוחלט', w.temp[w.idx(2, 4)] >= -273.16,
     w.temp[w.idx(2, 4)].toFixed(2) + '° (הגבול -273.15)');
}
{
  /* בלון לא עולה בחלל. בלי אוויר שידחוף — אין ציפה. */
  const w = new World(7, 12, 20);
  for (let x = 0; x < 7; x++) w.set(x, 11, 'Fe', 20, BULK);
  for (let x = 2; x <= 4; x++) w.set(x, 9, 'H2', 20);   // מימן, הגז הקל ביותר, בוואקום
  const before = w.count('H2');
  w.run(80);
  const hi = topOf(w, 'H2'), lo = bottomOf(w, 'H2');
  ok('גז בוואקום מתפזר במקום לצוף',
     w.count('H2') === before && hi < 9 && hi > 0 && lo > hi,
     'זז מהשורה 9 והתפרש על השורות ' + hi + '–' + lo + ' — לא קפא במקום ולא נדבק לתקרה');
}
{
  /* צוואר של שעון חול: פיר ברוחב תא אחד. כאן אין אלכסונים, ולכן נפילה ישרה
     היא הדרך היחידה למטה. */
  const w = new World(5, 12, 20);
  for (let y = 0; y <= 10; y++) { w.set(1, y, 'Fe', 20, BULK); w.set(3, y, 'Fe', 20, BULK); }
  for (let x = 0; x < 5; x++) w.set(x, 11, 'Fe', 20, BULK);
  w.set(2, 0, 'SiO2', 20, GRAIN);
  w.run(40);
  ok('גרגר יורד גם בפיר צר שאין בו אלכסונים', w.sub[w.idx(2, 10)] === idOf('SiO2'),
     'הגיע לשורה ' + bottomOf(w, 'SiO2') + ' מתוך 10');
}
{
  /* מים נשפכים בצד אחד של אמבט. הם חייבים להתיישר — זו התכונה שמגדירה נוזל. */
  const w = new World(12, 8, 20);
  for (let y = 0; y < 8; y++) { w.set(0, y, 'Fe', 20, BULK); w.set(11, y, 'Fe', 20, BULK); }
  for (let x = 0; x < 12; x++) w.set(x, 7, 'Fe', 20, BULK);
  for (let x = 1; x <= 4; x++) for (let y = 2; y <= 6; y++) w.set(x, y, 'H2O', 20);
  w.run(300);
  const col = [];
  for (let x = 1; x <= 10; x++) { let n = 0;
    for (let y = 0; y < 7; y++) if (w.sub[w.idx(x, y)] === idOf('H2O')) n++; col.push(n); }
  const lo = Math.min(...col), hi = Math.max(...col);
  ok('מים מתיישרים לאורך כל האמבט', lo >= 1 && hi - lo <= 1,
     'גובה לפי עמודה: ' + col.join(',') + '\n' + draw(w));
}

console.log('\n=== 6. תגובות בתוך הרשת ===');
{
  const w = new World(12, 12, 20);
  for (let x = 0; x < 12; x++) w.set(x, 11, 'Al2O3', 20, BULK);
  // מערבבים מימן וחמצן, ומדליקים ניצוץ באמצע
  for (let y = 4; y <= 8; y++) for (let x = 1; x < 11; x++) w.set(x, y, (x + y) % 3 === 0 ? 'O2' : 'H2', 20);
  for (let y = 5; y <= 7; y++) for (let x = 5; x <= 7; x++) w.temp[w.idx(x, y)] = 900;
  w.run(60);
  const water = w.count('H2O');
  let hottest = 0; for (let i = 0; i < w.n; i++) hottest = Math.max(hottest, w.temp[i]);
  ok('מימן וחמצן נדלקים ומייצרים מים', water > 0,
     'נוצרו ' + water + ' תאי מים · השיא ' + hottest.toFixed(0) + '°');
  ok('הלהבה מגיעה לטמפרטורה של שריפה אמיתית', hottest > 800 && hottest < 6000,
     hottest.toFixed(0) + '° (להבת מימן אמיתית: 2000–3000)');
}
{
  const w = new World(12, 12, 20);
  for (let x = 0; x < 12; x++) w.set(x, 11, 'Al2O3', 20, BULK);
  for (let y = 6; y <= 9; y++) for (let x = 1; x < 11; x++) w.set(x, y, (x + y) % 2 ? 'Fe2O3' : 'Al', 900, GRAIN);
  w.run(80);
  ok('תרמיט ברשת: חלודה + אלומיניום → ברזל', w.count('Fe') > 0,
     'נוצרו ' + w.count('Fe') + ' תאי ברזל');
}
{
  const w = new World(10, 10, 20);
  for (let y = 0; y < 9; y++) for (let x = 0; x < 10; x++) w.set(x, y, 'H2O', 20);
  for (let x = 0; x < 10; x++) w.set(x, 9, 'Au', 20, BULK);
  const before = w.count('H2O');
  w.run(100);
  ok('מים ליד זהב לא עושים כלום', w.count('H2O') === before && w.count('Au') === 10,
     before + ' תאי מים, 10 תאי זהב — בלי שינוי');
}

console.log('\n=== 7. זכוכית — התנהגות שאיש לא תכנת ===');
{
  /* חול הוא SiO₂ גרגרי. זכוכית היא אותו SiO₂ בדיוק, רק מלוכד. אין חוק
     "חול → זכוכית": יש נוזל שמתקרר ומתמצק, וזה כל הסיפור. */
  const w = new World(5, 5, 20);
  w.set(2, 4, 'SiO2', 20, GRAIN);
  ok('חול מתחיל כגרגרים', w.form[w.idx(2, 4)] === GRAIN);
  w.temp[w.idx(2, 4)] = 2000;                    // תנור: מעל 1670
  for (let k = 0; k < 400 && w.phase[w.idx(2, 4)] !== LIQUID; k++) { w.step(); w.temp[w.idx(2, 4)] = Math.max(w.temp[w.idx(2, 4)], 2000); }
  const wasLiquid = w.phase[w.idx(2, 4)] === LIQUID;
  w.temp[w.idx(2, 4)] = 20;
  for (let k = 0; k < 900 && w.phase[w.idx(2, 4)] !== SOLID; k++) { w.step(); w.temp[w.idx(2, 4)] = Math.min(w.temp[w.idx(2, 4)], 20); }
  ok('חול שנמס והתקרר חוזר כגוש — כלומר זכוכית',
     wasLiquid && w.phase[w.idx(2, 4)] === SOLID && w.form[w.idx(2, 4)] === BULK,
     wasLiquid ? 'נמס ואז התמצק כגוש' : 'לא הצליח להימס');
}

console.log('\n=== 8. שימור חומר — הבדיקה שהכי חשובה ===');
{
  /* עולם כאוטי: הכל מעורבב, חם, נופל ומגיב. אחרי 300 צעדים חייבים להיות
     בדיוק אותם אטומים. במשחק הישן זו הייתה הבדיקה שנכשלה שוב ושוב. */
  const w = new World(24, 24, 20, 777);
  const keys = ['H2', 'O2', 'C', 'Fe', 'Fe2O3', 'Al', 'H2O', 'CH4', 'Na', 'Cl2', 'S', 'Mg', 'CO2', 'SiO2'];
  for (let y = 0; y < 24; y++) for (let x = 0; x < 24; x++)
    if ((x * 7 + y * 13) % 5 !== 0) w.set(x, y, keys[(x * 3 + y * 5) % keys.length], 20 + ((x * y) % 30) * 60);
  const before = w.census();
  w.run(300);
  const after = w.census();
  const els = new Set([...Object.keys(before), ...Object.keys(after)]);
  let bad = [];
  for (const e of els) if ((before[e] || 0) !== (after[e] || 0))
    bad.push(e + ': ' + (before[e] || 0) + '→' + (after[e] || 0));
  const total = Object.values(before).reduce((a, b) => a + b, 0);
  ok('אחרי 300 צעדים בעולם כאוטי — אותם אטומים בדיוק', bad.length === 0,
     total + ' אטומים · ' + w.reactions + ' תגובות התרחשו' + (bad.length ? ' · הפרות: ' + bad.join(', ') : ''));
  ok('העולם באמת עשה משהו (הבדיקה למעלה לא עברה כי כלום לא קרה)', w.reactions > 20,
     w.reactions + ' תגובות');
}
{
  // אותה בדיקה בקור מוחלט, שם כמעט אין תגובות — רק תנועה
  const w = new World(20, 20, -200, 999);
  const keys = ['H2O', 'Fe', 'SiO2', 'Hg', 'N2', 'CO2', 'Au'];
  for (let y = 0; y < 20; y++) for (let x = 0; x < 20; x++)
    if ((x + y) % 3) w.set(x, y, keys[(x + y * 3) % keys.length], -200);
  const before = w.census();
  w.run(200);
  const after = w.census();
  let bad = 0;
  for (const e of new Set([...Object.keys(before), ...Object.keys(after)]))
    if ((before[e] || 0) !== (after[e] || 0)) bad++;
  ok('גם תנועה טהורה בלי תגובות לא מאבדת חומר', bad === 0,
     Object.values(before).reduce((a, b) => a + b, 0) + ' אטומים');
}

console.log('\n=== 9. גבולות העולם ===');
{
  const w = new World(6, 6, 20);
  for (let x = 0; x < 6; x++) { w.set(x, 0, 'H2O', 20); w.set(x, 5, 'H2', 20); }
  for (let y = 0; y < 6; y++) { w.set(0, y, 'CO2', 20); w.set(5, y, 'He', 20); }
  const before = w.census();
  w.run(200);
  const after = w.census();
  let bad = 0;
  for (const e of new Set([...Object.keys(before), ...Object.keys(after)]))
    if ((before[e] || 0) !== (after[e] || 0)) bad++;
  ok('שום דבר לא בורח מקצוות המפה', bad === 0);
}

console.log('\n=== 10. מהירות ===');
{
  const w = new World(160, 120, 20, 42);
  const keys = ['H2', 'O2', 'C', 'Fe', 'H2O', 'SiO2', 'N2'];
  for (let y = 0; y < 120; y++) for (let x = 0; x < 160; x++)
    if ((x + y) % 4) w.set(x, y, keys[(x + y * 3) % keys.length], 20 + ((x * y) % 20) * 40);
  w.run(3);                                       // חימום המטמון
  const t0 = Date.now();
  w.run(30);
  const ms = (Date.now() - t0) / 30;
  ok('רשת 160×120 רצה בקצב שמתאים לטלפון', ms < 33,
     ms.toFixed(1) + 'ms לצעד  (' + (1000 / ms).toFixed(0) + ' צעדים בשנייה)');
}

console.log('\n' + (fail ? '❌ ' + fail + ' נכשלו, ' : '✅ ') + pass + ' עברו\n');
process.exit(fail ? 1 : 0);
