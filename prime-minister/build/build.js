/*
 * Builds the self-contained copies of the game from the live one.
 *
 * prime-minister/index.html is the game as it is served, and it loads two
 * files beside it. Those get inlined here so the whole game — including
 * multiplayer — travels as a single file:
 *
 *   ../standalone.html   a complete page: open it, or send it to someone
 *   ../artifact.html     the same, minus the document scaffolding that the
 *                        artifact host supplies itself
 *
 * The build fails loudly if a single line of the original prototype is ever
 * missing from the result, so the game it was grown from stays intact.
 */
const fs = require('fs');
const path = require('path');

const HERE = __dirname;
const DIR = path.join(HERE, '..');
const ORIGINAL = process.argv[2] || '/root/.claude/uploads/380178b8-d7cf-5df9-a01c-8260baf0f2e4/50a55cbb-prototype2.html';

const live = fs.readFileSync(path.join(DIR, 'index.html'), 'utf8');
const original = fs.readFileSync(ORIGINAL, 'utf8');

/* ---- 1. inline what the served page loads from beside it ---- */
const EXTERNALS = [
  ['<script src="vendor/peerjs.min.js"></script>', 'vendor/peerjs.min.js'],
  ['<script src="mp-room.js"></script>', 'mp-room.js'],
];
let single = live;
for (const [tag, file] of EXTERNALS) {
  if (!single.includes(tag)) throw new Error('missing script tag for ' + file);
  const body = fs.readFileSync(path.join(DIR, file), 'utf8');
  // a literal </script> inside the source would close this block early
  if (/<\/script/i.test(body)) throw new Error(file + ' contains a closing script tag');
  single = single.replace(tag, '<script>\n/* inlined from ' + file + ' */\n' + body + '\n</script>');
}

/* ---- 2. the artifact host owns the document scaffolding ---- */
const SCAFFOLD = new Set([
  '<!DOCTYPE html>', '<html lang="he" dir="rtl">', '<head>',
  '<meta charset="UTF-8">', '</head>', '<body>', '</body>', '</html>',
]);
const RTL = `<script>
  // The original document carried dir="rtl" on its root element; the
  // artifact host owns that element now, so the direction is set here.
  document.documentElement.setAttribute('dir', 'rtl');
  document.documentElement.setAttribute('lang', 'he');
</script>
`;
const artifact = RTL + single.split('\n').filter(l => !SCAFFOLD.has(l.trim())).join('\n');

/* ---- 3. nothing of the original game may go missing ---- */
function check(name, out, allowScaffoldLoss) {
  const wanted = original.split('\n').filter(l => !(allowScaffoldLoss && SCAFFOLD.has(l.trim())));
  const got = out.split('\n');
  let i = 0; const missing = [];
  for (const line of wanted) {
    const at = got.indexOf(line, i);
    if (at === -1) { missing.push(line.slice(0, 70)); if (missing.length > 3) break; }
    else i = at + 1;
  }
  if (missing.length) { console.error('❌ ' + name + ' lost original lines:', missing); process.exit(1); }
  return wanted.length;
}

fs.writeFileSync(path.join(DIR, 'standalone.html'), single);
fs.writeFileSync(path.join(DIR, 'artifact.html'), artifact);

const kept = check('standalone.html', single, false);
check('artifact.html', artifact, true);

const kb = t => (Buffer.byteLength(t) / 1024).toFixed(0) + ' KB';
console.log('✅ standalone.html — complete page, ' + kb(single));
console.log('✅ artifact.html   — same, host supplies the scaffolding, ' + kb(artifact));
console.log('   original game lines kept : ' + kept + '/' + original.split('\n').length);
console.log('   external files inlined   : ' + EXTERNALS.map(e => e[1]).join(', '));
console.log('   no leftover script srcs  : ' + !/<script src=/.test(single));
