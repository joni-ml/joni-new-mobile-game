#!/usr/bin/env node
const fs = require('fs');
const { minify } = require('terser');

(async () => {
  let html = fs.readFileSync('./index.html', 'utf8');

  // Extract and minify JS
  const sOpen = html.indexOf('<script>');
  const sClose = html.indexOf('</script>', sOpen);
  const js = html.slice(sOpen + '<script>'.length, sClose);
  const res = await minify(js, {
    compress: { drop_console: false, passes: 2 },
    mangle: { toplevel: false },
    format: { comments: false }
  });
  if (res.error) throw res.error;
  html = html.slice(0, sOpen) + '<script>' + res.code + '</script>' + html.slice(sClose + '</script>'.length);

  // Minify CSS
  html = html.replace(/<style>([\s\S]*?)<\/style>/, (_, css) =>
    '<style>' + css.replace(/\/\*[\s\S]*?\*\//g, '').replace(/\s+/g, ' ').replace(/\s*([{}:;,>])\s*/g, '$1').replace(/;}/g, '}').trim() + '</style>'
  );

  // Remove HTML comments
  html = html.replace(/<!--(?!\[if)[\s\S]*?-->/g, '');
  html = html.replace(/\n\s*\n+/g, '\n').trim();

  fs.writeFileSync('./index.html', html);
  const before = fs.statSync('./index-backup.html').size;
  const after = Buffer.byteLength(html);
  console.log(`✓ מינימיזציה: ${(before/1024).toFixed(0)}KB → ${(after/1024).toFixed(0)}KB (${Math.round((1-after/before)*100)}% קטן יותר)`);
})().catch(e => { console.error('Error:', e); process.exit(1); });
