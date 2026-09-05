/*
 * משרד ראש הממשלה — שרת מולטיפלייר
 * Prime Minister game — multiplayer server.
 *
 * A single Node process that does two things:
 *   1. Serves the game (index.html) over HTTP.
 *   2. Runs a WebSocket hub that connects players into shared "rooms",
 *      relays each player's country state to the others, and forwards
 *      diplomatic actions (trade / aid / sanction / spy) between players.
 *
 * Run it with:   npm install   &&   npm start
 * Then open      http://localhost:8080      in the browser.
 *
 * No database, no config — state lives in memory for as long as the
 * server is running. Perfect for a game night with friends.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { WebSocketServer } = require('ws');

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

/* ---------------- multiplayer hub ---------------- */
const wss = new WebSocketServer({ server });
const rooms = new Map(); // roomCode -> { players: Map<id, player> }
let nextId = 1;

/* Room codes are short 2-digit numbers (10-99) so they are easy to read
   out loud to a friend. Only a couple of games run at a time, so 90 codes
   is far more than enough; a code is recycled as soon as its room empties. */
function allocCode() {
  const free = [];
  for (let n = 10; n <= 99; n++) if (!rooms.has(String(n))) free.push(String(n));
  if (!free.length) return null;
  return free[Math.floor(Math.random() * free.length)];
}

function roomSnapshot(room) {
  const players = {};
  for (const p of room.players.values()) {
    players[p.id] = { id: p.id, name: p.name, country: p.country };
  }
  return players;
}

function send(ws, obj) {
  if (ws.readyState === ws.OPEN) ws.send(JSON.stringify(obj));
}

function broadcastRoom(room) {
  const msg = { t: 'room', players: roomSnapshot(room) };
  for (const p of room.players.values()) send(p.ws, msg);
}

wss.on('connection', (ws) => {
  const player = { id: nextId++, name: 'שחקן', country: null, room: null, lastSummary: null, ws };

  send(ws, { t: 'welcome', playerId: player.id });

  ws.on('message', (raw) => {
    let m;
    try { m = JSON.parse(raw.toString()); } catch (_) { return; }

    // "create" opens a brand-new game and hands back its 2-digit code;
    // "join" enters an existing game by that code.
    if (m.t === 'create' || m.t === 'join') {
      player.name = String(m.name || 'שחקן').slice(0, 24);
      let code, room;

      if (m.t === 'create') {
        code = allocCode();
        if (!code) { send(ws, { t: 'error', code: 'full', msg: 'אין כרגע מקום למשחק חדש' }); return; }
        room = { players: new Map() };
        rooms.set(code, room);
      } else {
        code = String(m.room || '').trim();
        room = rooms.get(code);
        if (!room) { send(ws, { t: 'error', code: 'noroom', msg: 'לא נמצא משחק עם המספר הזה' }); return; }
      }

      player.room = code;
      room.players.set(player.id, player);
      send(ws, { t: m.t === 'create' ? 'created' : 'joined', room: code });
      // hand the newcomer every country snapshot already in the room
      for (const other of room.players.values()) {
        if (other.id !== player.id && other.lastSummary) {
          send(ws, { t: 'world', summary: other.lastSummary });
        }
      }
      broadcastRoom(room);
      return;
    }

    const room = player.room ? rooms.get(player.room) : null;
    if (!room) return;

    if (m.t === 'claim') {
      const wanted = String(m.country || '');
      // reject if another player in the room already holds this country
      for (const other of room.players.values()) {
        if (other.id !== player.id && other.country === wanted) {
          send(ws, { t: 'error', msg: 'המדינה כבר נתפסה' });
          broadcastRoom(room);
          return;
        }
      }
      player.country = wanted;
      broadcastRoom(room);
      return;
    }

    if (m.t === 'state') {
      player.lastSummary = m.summary || null;
      if (player.lastSummary) {
        for (const other of room.players.values()) {
          if (other.id !== player.id) send(other.ws, { t: 'world', summary: player.lastSummary });
        }
      }
      return;
    }

    if (m.t === 'diplo') {
      const target = room.players.get(Number(m.target));
      if (target) {
        send(target.ws, {
          t: 'diplo', type: m.type,
          fromName: player.name, fromCountry: player.country,
        });
      }
      return;
    }
  });

  ws.on('close', () => {
    const room = player.room ? rooms.get(player.room) : null;
    if (room) {
      room.players.delete(player.id);
      if (room.players.size === 0) rooms.delete(player.room);
      else broadcastRoom(room);
    }
  });
});

server.listen(PORT, () => {
  console.log(`\n🌍  משרד ראש הממשלה — השרת פועל`);
  console.log(`    שחק/י כאן:            http://localhost:${PORT}`);
  console.log(`    לשחק עם חברים ברשת:   http://<כתובת-ה-IP-שלך>:${PORT}\n`);
});
