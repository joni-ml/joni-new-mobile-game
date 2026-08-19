/* ============================================================================
   בדיקה של הבדיקות
   ============================================================================
   הרצה:  node rls/test-mutations.mjs

   השאלה: הבדיקות עוברות — אבל האם הן באמת בודקות משהו?
   קל מאוד לכתוב בדיקה שעוברת גם כשהקוד שבור. הדרך היחידה לדעת היא לשבור
   את הקוד בכוונה ולראות אם מישהו צועק.

   כל שורה כאן מקלקלת חוק אחד במנוע, מריצה את כל הבדיקות, ומחזירה את הקוד
   למקומו. אם קלקול עובר בשקט — יש חוק שאף בדיקה לא שומרת עליו.

   ככה נמחקה כאן פונקציה שלמה (rise), וככה התגלה שהגנת האפס המוחלט הייתה
   משוכפלת שלוש פעמים ואחד העותקים לא היה ניתן להגעה בכלל.
   ============================================================================ */
import { readFileSync, writeFileSync } from 'fs';
import { execSync } from 'child_process';

const W = 'rls/game/world.js', M = 'rls/game/matter.js', C = 'rls/game/chem.js';
const src = { [W]: readFileSync(W, 'utf8'), [M]: readFileSync(M, 'utf8'), [C]: readFileSync(C, 'utf8') };

const MUTATIONS = [
  ['שום דבר לא זז',              W, 'doMotion() {', 'doMotion() { if(1) return;'],
  ['אין תמיכה — הכל נתמך',       W, 'computeSupport() {', 'computeSupport() { this.sup.fill(1); if(1) return;'],
  ['אין חום כמוס',               W, 'if (Math.abs(this.prog[i]) < need) continue;', ''],
  ['אנרגיה תקועה לא מוחזרת',     W, 'this.temp[i] = clampT(this.temp[i] + this.prog[i] / c);', ''],
  ['אין אפס מוחלט',              W, 'export const clampT = t => t < ABS_ZERO ? ABS_ZERO : t > MAX_TEMP ? MAX_TEMP : t;',
                                    'export const clampT = t => t;'],
  ['כל החומרים באותה צפיפות',    M, 'export function density(s, T, ph) {', 'export function density(s, T, ph) { if(1) return 1;'],
  ['מתכת מוליכה כמו אבן',        M, 'if (isMetal(s)) return 0.60;', ''],
  ['אין תגובות',                 W, 'doReactions() {', 'doReactions() { if(1) return;'],
  ['אין מוליכות חום',            W, 'doConduction() {', 'doConduction() { if(1) return;'],
  ['תוצרים דורסים תאים תפוסים',  W, 'if (slots.length < nOut) return false;', ''],
  ['תגובה בלי לבדוק כמות',       W, 'if (na < r.nA || nb < r.nB) return false;', ''],
  ['נוזל שהתמצק נשאר גרגרי',     W, 'if (target === SOLID) this.form[i] = BULK;', ''],
  ['גרגר לא נופל בכלל',          W, 'if (this.sink(i, x, y, x, y + 1)) return true;', ''],
  ['גרגר לא מחליק הצידה',        W, 'return this.sink(i, x, y, x + d, y + 1) || this.sink(i, x, y, x - d, y + 1);', 'return false;'],
  ['נוזל לא מתפשט הצידה',        W, 'return this.side(i, x, y, true);', 'return false;'],
  ['גז לא מתפשט לריק',           W, 'if (!this.done[j] && this.sub[j] === EMPTY) { this.move(i, j); return true; }', ''],
  ['ציפה מבוטלת לגזים',          W, 'if (this.sink(i, x, y, x, y + 1, false)) return true;', ''],
  ['שימור אטומים בכימיה מבוטל',  C, 'if(rest===null) break;', 'if(rest===null) rest={};'],
];

let caught = 0, missed = [];
console.log('\n=== מקלקלים את המנוע בכוונה, ורואים מי תופס ===\n');
for (const [name, file, from, to] of MUTATIONS) {
  const orig = src[file];
  if (!orig.includes(from)) { console.log('  ?? הקוד השתנה, הקלקול לא רלוונטי: ' + name); continue; }
  writeFileSync(file, orig.replace(from, to));
  let out = '';
  try { out = execSync('node rls/test-world.mjs 2>&1', { encoding: 'utf8' }); }
  catch (e) { out = (e.stdout || '') + (e.message || ''); }
  for (const f in src) writeFileSync(f, src[f]);          // תמיד מחזירים

  const failed = (out.match(/✘/g) || []).length;
  const crashed = !failed && /Error/.test(out);
  const who = out.split('\n').filter(l => l.includes('✘')).map(l => l.replace(/^\s*✘\s*/, '').split('   ')[0]);
  if (failed || crashed) { caught++;
    console.log('  ✔ ' + name.padEnd(26) + ' → ' + (crashed ? 'המנוע קרס' : failed + ' בדיקות תפסו  [' + who.slice(0, 2).join(' | ') + ']'));
  } else { missed.push(name);
    console.log('  ✘ ' + name.padEnd(26) + ' → אף בדיקה לא תפסה!'); }
}
console.log('\n' + (missed.length ? '❌ ' : '✅ ') + caught + ' מתוך ' + MUTATIONS.length + ' קלקולים נתפסו' +
            (missed.length ? '\n   לא נשמרים על ידי אף בדיקה: ' + missed.join(', ') : '') + '\n');
process.exit(missed.length ? 1 : 0);
