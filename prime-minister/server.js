/*
 * משרד ראש הממשלה — שרת מולטיפלייר (אופציונלי)
 * Prime Minister game — optional multiplayer server.
 *
 * The game normally connects players device-to-device and needs no server
 * at all; this exists for anyone who would rather run a central one. It
 * does two things:
 *   1. Serves the game over HTTP.
 *   2. Carries messages between players.
 *
 * It deliberately holds no game rules of its own: every room is an
 * MPRoom from mp-room.js, the same rulebook the browser host runs, so
 * both ways of playing behave identically and are covered by the same
 * tests.
 *
 * Run it with:   npm install   &&   npm start
 * Then open      http://localhost:8080
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { WebSocketServer } = require('ws');
const MPRoom = require('./mp-room.js');

const PORT = process.env.PORT || 8080;
const ROOT = __dirname;

/* ---------------- static file server ---------------- */
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
};

const server = http.createServer((req, res) => {
  let urlPath = decodeURIComponent((req.url || '/').split('?')[0]);
  if (urlPath === '/') urlPath = '/index.html';

  // resolve safely inside ROOT (no path traversal)
  const filePath = path.normalize(path.join(ROOT, urlPath));
  if (!filePath.startsWith(ROOT)) { res.writeHead(403); res.end('forbidden'); return; }

  fs.readFile(filePath, (err, data) => {
    if (err) { res.writeHead(404); res.end('not found'); return; }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(filePath)] || 'application/octet-stream' });
    res.end(data);
  });
});

/* ---------------- rooms ---------------- */
const wss = new WebSocketServer({ server });
const rooms = new Map(); // code -> { room, sockets: Map<playerId, ws> }

/* Room codes are short 2-digit numbers (10-99) so they are easy to read out
   loud. A code is recycled as soon as its room empties. */
function allocCode() {
  const free = [];
  for (let n = 10; n <= 99; n++) if (!rooms.has(String(n))) free.push(String(n));
  if (!free.length) return null;
  return free[Math.floor(Math.random() * free.length)];
}

function send(ws, obj) {
  if (ws && ws.readyState === ws.OPEN) ws.send(JSON.stringify(obj));
}

function openRoom(code) {
  const sockets = new Map();
  const room = MPRoom.createRoom(code, (pid, msg) => send(sockets.get(pid), msg));
  const entry = { room, sockets };
  rooms.set(code, entry);
  return entry;
}

wss.on('connection', (ws) => {
  let entry = null;   // the room this socket belongs to
  let pid = null;     // this socket's player id inside that room

  ws.on('message', (raw) => {
    let m;
    try { m = JSON.parse(raw.toString()); } catch (_) { return; }

    if (m.t === 'create' || m.t === 'join') {
      if (entry) return;                       // already seated
      let code;
      if (m.t === 'create') {
        code = allocCode();
        if (!code) { send(ws, { t: 'error', code: 'full', msg: 'אין כרגע מקום למשחק חדש' }); return; }
        entry = openRoom(code);
      } else {
        code = String(m.room || '').trim();
        entry = rooms.get(code) || null;
        if (!entry) { send(ws, { t: 'error', code: 'noroom', msg: 'לא נמצא משחק עם המספר הזה' }); return; }
      }
      // bind the socket before anything is delivered, or 'welcome' has nowhere to go
      entry.room.add(m.name, m.t === 'create', (id) => { pid = id; entry.sockets.set(id, ws); });
      return;
    }

    if (!entry || pid == null) return;
    entry.room.handle(pid, m);                 // every other rule lives in mp-room.js
  });

  ws.on('close', () => {
    if (!entry || pid == null) return;
    entry.sockets.delete(pid);
    entry.room.remove(pid);
    if (entry.room.size === 0) rooms.delete(entry.room.code);
  });
});

server.listen(PORT, () => {
  console.log(`\n🌍  משרד ראש הממשלה — השרת פועל`);
  console.log(`    שחק/י כאן:            http://localhost:${PORT}`);
  console.log(`    לשחק עם חברים ברשת:   http://<כתובת-ה-IP-שלך>:${PORT}\n`);
});
