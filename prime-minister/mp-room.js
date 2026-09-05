/*
 * חדר המשחק שרץ בתוך הטלפון של המארח.
 * The game room that runs inside the host's own device.
 *
 * This is the same rulebook as server.js, but it lives in the host's
 * browser instead of on a machine somewhere. It is deliberately pure:
 * it never touches the DOM and never touches the network. It is handed a
 * deliver(playerId, message) callback and only decides *who gets what*,
 * which keeps it testable in Node and identical in behaviour to the
 * WebSocket server.
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.MPRoom = factory();
})(typeof self !== 'undefined' ? self : this, function () {

  function createRoom(code, deliver) {
    const players = new Map(); // id -> {id, name, country, lastSummary}
    let hostId = null;
    let started = false;
    let nextId = 1;

    function snapshot() {
      const out = {};
      for (const p of players.values()) out[p.id] = { id: p.id, name: p.name, country: p.country };
      return out;
    }
    function broadcast(msg) { for (const p of players.values()) deliver(p.id, msg); }
    function broadcastRoom() { broadcast({ t: 'room', players: snapshot(), host: hostId, started: started }); }

    return {
      code: code,
      players: players,
      get hostId() { return hostId; },
      get started() { return started; },
      get size() { return players.size; },

      /* A participant arrives: the host themself, or a friend's phone.
         "bind" is called with the new id BEFORE anything is delivered, so the
         caller can register where this player's messages should be routed —
         otherwise the very first message (welcome) has nowhere to go. */
      add(name, isHost, bind) {
        const id = nextId++;
        players.set(id, { id: id, name: String(name || 'שחקן').slice(0, 24), country: null, lastSummary: null });
        if (isHost || hostId === null) hostId = id;
        if (typeof bind === 'function') bind(id);

        deliver(id, { t: 'welcome', playerId: id });
        deliver(id, { t: isHost ? 'created' : 'joined', room: code });
        // catch the newcomer up on everyone who is already playing
        for (const other of players.values()) {
          if (other.id !== id && other.lastSummary) deliver(id, { t: 'world', summary: other.lastSummary });
        }
        if (started) deliver(id, { t: 'start' });
        broadcastRoom();
        return id;
      },

      /* Someone left. If it was the host, the crown passes to whoever remains. */
      remove(id) {
        if (!players.has(id)) return;
        players.delete(id);
        if (players.size === 0) { hostId = null; return; }
        if (hostId === id) hostId = players.keys().next().value;
        broadcastRoom();
      },

      handle(id, m) {
        const me = players.get(id);
        if (!me || !m) return;

        if (m.t === 'start') {
          if (id !== hostId) return;            // only the host decides when to begin
          started = true;
          broadcast({ t: 'start' });
          broadcastRoom();
          return;
        }

        if (m.t === 'claim') {
          const wanted = String(m.country || '');
          for (const other of players.values()) {
            if (other.id !== id && other.country === wanted) {
              deliver(id, { t: 'error', msg: 'המדינה כבר נתפסה' });
              broadcastRoom();
              return;
            }
          }
          me.country = wanted;
          broadcastRoom();
          return;
        }

        if (m.t === 'state') {
          me.lastSummary = m.summary || null;
          if (me.lastSummary) {
            for (const other of players.values()) {
              if (other.id !== id) deliver(other.id, { t: 'world', summary: me.lastSummary });
            }
          }
          return;
        }

        if (m.t === 'diplo') {
          const target = players.get(Number(m.target));
          if (target) {
            deliver(target.id, { t: 'diplo', type: m.type, fromName: me.name, fromCountry: me.country });
          }
          return;
        }
      },
    };
  }

  return { createRoom: createRoom };
});
