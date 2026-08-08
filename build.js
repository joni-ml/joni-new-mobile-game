#!/usr/bin/env node
/* בונה גרסה "מוגנת" של המשחק להפצה: ממזער ומערפל את הקוד (בלי הערות, בלי שמות
   ברורים למשתנים מקומיים) כדי שיהיה קשה מאוד להעתיק. הקוד המקורי הנקי נשאר ב-index.html;
   הפלט המוגן נכתב ל-dist/ (זו הגרסה שמתארחת ומוגשת לשחקנים).
   שמות גלובליים לא משתנים — כי הקוד בונה מחרוזות HTML עם onclick="פונקציה()". */
const fs = require('fs');
const path = require('path');
const { minify } = require('terser');

const SRC = path.join(__dirname, 'index.html');
const OUT_DIR = path.join(__dirname, 'dist');

function minifyCSS(css){
  return css
    .replace(/\/\*[\s\S]*?\*\//g, '')      // הסרת הערות CSS
    .replace(/\s+/g, ' ')                    // כיווץ רווחים
    .replace(/\s*([{}:;,>])\s*/g, '$1')      // רווחים סביב סימנים
    .replace(/;}/g, '}')
    .trim();
}

(async () => {
  let html = fs.readFileSync(SRC, 'utf8');

  // --- מזעור ה-JS (הלב של המשחק) ---
  const sOpen = html.indexOf('<script>');
  const sClose = html.indexOf('</script>', sOpen);
  if (sOpen === -1 || sClose === -1) throw new Error('לא נמצא בלוק <script> יחיד');
  const js = html.slice(sOpen + '<script>'.length, sClose);
  const res = await minify(js, {
    compress: { drop_console: false, passes: 2 },
    mangle: { toplevel: false },            // לא נוגעים בשמות גלובליים (onclick במחרוזות)
    format: { comments: false }
  });
  if (res.error) throw res.error;
  html = html.slice(0, sOpen) + '<script>' + res.code + '</script>' + html.slice(sClose + '</script>'.length);

  // --- מזעור ה-CSS ---
  html = html.replace(/<style>([\s\S]*?)<\/style>/, (_, css) => '<style>' + minifyCSS(css) + '</style>');

  // --- הסרת הערות HTML (מחוץ לסקריפט/סגנון) וכיווץ שורות ריקות ---
  // מסירים רק הערות <!-- --> שאינן DOCTYPE
  html = html.replace(/<!--(?!\[if)[\s\S]*?-->/g, '');
  html = html.replace(/\n\s*\n+/g, '\n').trim();

  // --- כתיבה ל-dist/ + העתקת נכסים ---
  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(path.join(OUT_DIR, 'index.html'), html);
  for (const f of ['manifest.webmanifest', 'icon.png']) {
    if (fs.existsSync(path.join(__dirname, f))) fs.copyFileSync(path.join(__dirname, f), path.join(OUT_DIR, f));
  }

  const before = fs.statSync(SRC).size, after = Buffer.byteLength(html);
  console.log(`✓ נבנה dist/index.html — ${(before/1024).toFixed(0)}KB → ${(after/1024).toFixed(0)}KB (${Math.round((1-after/before)*100)}% קטן יותר)`);
})().catch(e => { console.error('שגיאת בנייה:', e); process.exit(1); });
