/*
 * Builds the single-file Artifact edition:
 *   original prototype  +  multiplayer UI  +  multiplayer logic
 *
 * The artifact host wraps the file in its own <!doctype>/<head>/<body>
 * skeleton, so the document scaffolding is dropped and the page's RTL
 * direction is applied to the real <html> element at runtime instead.
 * Everything else of the original is copied through byte-for-byte, and
 * the build fails loudly if any of it is removed or altered.
 */
const fs = require('fs');
const path = require('path');

const STANDALONE = process.argv.includes('--standalone');
const args = process.argv.slice(2).filter(a => !a.startsWith('--'));
const ORIGINAL = args[0] || '/root/.claude/uploads/380178b8-d7cf-5df9-a01c-8260baf0f2e4/50a55cbb-prototype2.html';
const OUT = path.join(__dirname, '..', STANDALONE ? 'standalone.html' : 'artifact.html');

const original = fs.readFileSync(ORIGINAL, 'utf8');
const ui = fs.readFileSync(path.join(__dirname, 'artifact-ui.html'), 'utf8');
const mp = fs.readFileSync(path.join(__dirname, 'artifact-mp.js'), 'utf8');

// the host supplies these; carrying our own would nest a document inside a document
const SCAFFOLD = new Set([
  '<!DOCTYPE html>', '<html lang="he" dir="rtl">', '<head>',
  '<meta charset="UTF-8">', '</head>', '<body>', '</body>', '</html>',
]);

// standalone keeps the whole document (it is opened directly, not framed)
const body = STANDALONE
  ? original
  : original.split('\n').filter(l => !SCAFFOLD.has(l.trim())).join('\n');

// the original set RTL on <html>; that element now belongs to the host
const RTL = `<script>
  // The original document carried dir="rtl" on its root element; the
  // artifact host owns that element now, so the direction is set here.
  document.documentElement.setAttribute('dir', 'rtl');
  document.documentElement.setAttribute('lang', 'he');
</script>
`;

const scriptTag = '<script>\n/* ---------- COUNTRIES ---------- */';
if (!body.includes(scriptTag)) throw new Error('anchor: game script');
let out = (STANDALONE ? '' : RTL) + body.replace(scriptTag, ui + '\n' + scriptTag);

if (STANDALONE) {
  const tail = '</script>\n</body>\n</html>';
  if (!out.includes(tail)) throw new Error('anchor: closing tags');
  out = out.replace(tail, '</script>\n\n<script>\n' + mp + '</script>\n</body>\n</html>');
} else {
  if (!out.trimEnd().endsWith('</script>')) throw new Error('anchor: trailing script');
  out = out.trimEnd() + '\n\n<script>\n' + mp + '</script>\n';
}

fs.writeFileSync(OUT, out);

// prove every non-scaffold line of the original survived, in order
const wanted = STANDALONE ? original.split('\n') : original.split('\n').filter(l => !SCAFFOLD.has(l.trim()));
const got = out.split('\n');
let i = 0; const missing = [];
for (const line of wanted) {
  const at = got.indexOf(line, i);
  if (at === -1) { missing.push(line.slice(0, 70)); if (missing.length > 3) break; }
  else i = at + 1;
}
if (missing.length) { console.error('❌ original lines missing/altered:', missing); process.exit(1); }

console.log('✅ built ' + OUT);
console.log('   original game lines kept : ' + wanted.length + ' / ' + original.split('\n').length +
            ' (dropped only ' + (original.split('\n').length - wanted.length) + ' scaffold tags)');
console.log('   built lines              : ' + got.length);
console.log('   size                     : ' + (Buffer.byteLength(out) / 1024).toFixed(0) + ' KB');
if (!STANDALONE) console.log('   no nested document       : ' + !/<\/?(html|head|body)\b/i.test(out));
else console.log('   charset / rtl kept       : ' + (/<meta charset="UTF-8">/.test(out) && /<html lang="he" dir="rtl">/.test(out)));
