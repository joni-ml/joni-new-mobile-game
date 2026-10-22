#!/usr/bin/env node
/* בונה את index.html (הגרסה המוגנת שמעתיקים ומפיצים) מתוך src/game.html (הקוד הקריא).
   שמות גלובליים נשמרים — הקוד בונה מחרוזות HTML עם onclick="פונקציה()".
   הרצה:  node minify.js                                                          */
const fs = require('fs');
const path = require('path');
const { minify } = require('terser');

const SRC = path.join(__dirname, 'src', 'game.html');
const OUT = path.join(__dirname, 'index.html');

(async () => {
  let html = fs.readFileSync(SRC, 'utf8');

  const sOpen = html.indexOf('<script>');
  const sClose = html.indexOf('</script>', sOpen);
  if (sOpen === -1 || sClose === -1) throw new Error('לא נמצא בלוק <script>');
  const res = await minify(html.slice(sOpen + 8, sClose), {
    compress: { drop_console: false, passes: 2 },
    mangle: { toplevel: false },
    format: { comments: false }
  });
  if (res.error) throw res.error;
  html = html.slice(0, sOpen) + '<script>' + res.code + '</script>' + html.slice(sClose + 9);

  html = html.replace(/<style>([\s\S]*?)<\/style>/, (_, css) => '<style>' + css
    .replace(/\/\*[\s\S]*?\*\//g, '').replace(/\s+/g, ' ')
    .replace(/\s*([{}:;,>])\s*/g, '$1').replace(/;}/g, '}').trim() + '</style>');

  html = html.replace(/<!--(?!\[if)[\s\S]*?-->/g, '').replace(/\n\s*\n+/g, '\n').trim();

  fs.writeFileSync(OUT, html);
  const before = fs.statSync(SRC).size, after = Buffer.byteLength(html);
  console.log(`✓ index.html — ${(before/1024).toFixed(0)}KB → ${(after/1024).toFixed(0)}KB (${Math.round((1-after/before)*100)}% קטן יותר)`);
})().catch(e => { console.error('שגיאת בנייה:', e); process.exit(1); });
