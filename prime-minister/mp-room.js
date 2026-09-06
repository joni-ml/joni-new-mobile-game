/*
 * חדר המשחק — ספר החוקים של המולטיפלייר.
 * The game room: the multiplayer rulebook.
 *
 * Runs inside the host's own browser for a direct device-to-device game,
 * and inside server.js when a Node server is used, so both paths obey the
 * same rules. It is deliberately pure: no DOM, no network. It is handed a
 * deliver(playerId, message) callback and only decides *who is told what*,
 * which keeps every rule here testable in Node.
 *
 * It is the authority on three things a single client cannot decide alone:
 *   - the shared quarter, so nobody plays ahead of anyone else
 *   - whether an offer was accepted, refused or answered in kind
 *   - who wins a war (and is therefore still in the game)
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.MPRoom = factory();
})(typeof self !== 'undefined' ? self : this, function () {

  /* Strength a country brings to a war. Readiness carries it; a country in
     turmoil or hated at home fights worse than its army suggests. */
  function warStrength(summary) {
    const s = summary || {};
    const num = (v, d) => (typeof v === 'number' && isFinite(v) ? v : d);
    return num(s.militaryReadiness, 50) * 1.0
         + num(s.stability, 50) * 0.4
         + num(s.approval, 50) * 0.2;
  }

  /* How a country votes on a resolution. Not a dice roll: it reads the
     target the way a foreign ministry would, and the bar for authorising a
     nuclear strike is set so high that only a country already on the edge of
     war can clear it — which is why the answer is almost always "no". */
  function botBallot(kind, voter, target) {
    const n = (v, d) => (typeof v === 'number' && isFinite(v) ? v : d);
    const tension = n(target.borderTension, 50);
    const approval = n(target.approval, 50);
    const stability = n(target.stability, 55);
    const treasury = n(target.treasury, 10000);
    const voterStab = n(voter.stability, 55);
    const reasons = [];
    let score;

    if (kind === 'nuclear') {
      // Extreme tension alone is not enough: a country must be both on the
      // brink of war and already isolated at home before anyone says yes.
      score = (tension - 88) * 0.10 - 1.35;
      if (tension > 88) reasons.push('המתיחות בגבולות ' + Math.round(tension) + '% מצדיקה צעד קיצוני');
      else reasons.push('אין הצדקה לנשק גרעיני נגד מדינה שאינה על סף מלחמה');
      if (approval < 25) { score += 0.30; reasons.push('המשטר שם מבודד גם בבית'); }
    } else {
      score = (tension - 55) * 0.05;
      if (tension > 55) reasons.push('התנהגות תוקפנית בגבולות (' + Math.round(tension) + '%)');
      else reasons.push('המדינה אינה מאיימת על אף אחד כרגע');
      if (approval < 35) { score += 0.50; reasons.push('משטר מבודד ולא פופולרי'); }
      score += (voterStab > 60 ? 0.30 : -0.30);
      if (voterStab <= 60) reasons.push('מדינות לא יציבות נמנעות מעימות');
      if (treasury > 40000) { score -= 0.80; reasons.push('שותפת סחר עשירה מדי לריב איתה'); }
      else if (treasury > 25000) { score -= 0.30; reasons.push('קשרי מסחר משמעותיים מרסנים'); }
      if (stability < 30) { score += 0.20; reasons.push('חוסר יציבות שם מדאיג את האזור'); }
    }
    return { vote: score > 0 ? 'for' : 'against', score: score, reasons: reasons };
  }

  function createRoom(code, deliver, opts) {
    const rnd = (opts && opts.random) || Math.random;
    const players = new Map(); // id -> {id,name,country,lastSummary,alive}
    const proposals = new Map(); // id -> {from,to,kind}
    const wars = new Map();      // id -> {attacker,defender,stage,posture}
    const votes = new Map();     // id -> an open UN resolution
    const nukeAuth = new Map();  // playerId -> {country, untilTurn}
    let hostId = null;
    let started = false;
    let nextId = 1;
    let seq = 1;
    let turn = 1;
    let submitted = new Set();

    function snapshot() {
      const out = {};
      for (const p of players.values()) {
        out[p.id] = { id: p.id, name: p.name, country: p.country, alive: p.alive !== false };
      }
      return out;
    }
    function broadcast(msg) { for (const p of players.values()) deliver(p.id, msg); }
    function broadcastRoom() {
      broadcast({ t: 'room', players: snapshot(), host: hostId, started: started, turn: turn });
    }

    /* Who the shared quarter waits for: in the game, still alive. */
    function activePlayers() {
      return [...players.values()].filter(p => p.country && p.alive !== false);
    }
    function pushTurnState() {
      const waiting = activePlayers().filter(p => !submitted.has(p.id)).map(p => p.name);
      broadcast({ t: 'turnState', turn: turn, waiting: waiting });
    }
    /* Advance the moment the last player still in the game has committed. */
    function maybeAdvanceTurn() {
      const active = activePlayers();
      if (!active.length) return;
      if (!active.every(p => submitted.has(p.id))) { pushTurnState(); return; }
      turn += 1;
      submitted = new Set();
      broadcast({ t: 'turnAdvance', turn: turn });
      pushTurnState();
    }

    function eliminate(p, reason) {
      p.alive = false;
      submitted.delete(p.id);
      deliver(p.id, { t: 'eliminated', reason: reason });
    }

    return {
      code: code,
      players: players,
      get hostId() { return hostId; },
      get started() { return started; },
      get turn() { return turn; },
      get size() { return players.size; },

      /* A participant arrives: the host themself, or a friend's device.
         "bind" is called with the new id BEFORE anything is delivered, so the
         caller can register where this player's messages go — otherwise the
         very first message (welcome) has nowhere to arrive. */
      add(name, isHost, bind) {
        const id = nextId++;
        players.set(id, {
          id: id, name: String(name || 'שחקן').slice(0, 24),
          country: null, lastSummary: null, alive: true,
        });
        if (isHost || hostId === null) hostId = id;
        if (typeof bind === 'function') bind(id);

        deliver(id, { t: 'welcome', playerId: id });
        deliver(id, { t: isHost ? 'created' : 'joined', room: code });
        for (const other of players.values()) {
          if (other.id !== id && other.lastSummary) deliver(id, { t: 'world', summary: other.lastSummary });
        }
        if (started) { deliver(id, { t: 'start' }); deliver(id, { t: 'turnAdvance', turn: turn }); }
        broadcastRoom();
        return id;
      },

      /* Someone left. If it was the host, the crown passes to whoever remains. */
      remove(id) {
        if (!players.has(id)) return;
        players.delete(id);
        submitted.delete(id);
        if (players.size === 0) { hostId = null; return; }
        if (hostId === id) hostId = players.keys().next().value;
        broadcastRoom();
        maybeAdvanceTurn(); // nobody should wait on a player who left
      },

      handle(id, m) {
        const me = players.get(id);
        if (!me || !m) return;

        /* ---------- lobby ---------- */
        if (m.t === 'start') {
          if (id !== hostId) return;
          started = true;
          broadcast({ t: 'start' });
          broadcastRoom();
          pushTurnState();
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
          pushTurnState();
          return;
        }

        if (m.t === 'state') {
          me.lastSummary = m.summary || null;
          if (me.lastSummary) {
            if (me.lastSummary.alive === false && me.alive !== false) {
              me.alive = false;
              submitted.delete(id);
              broadcastRoom();
              maybeAdvanceTurn();
            }
            for (const other of players.values()) {
              if (other.id !== id) deliver(other.id, { t: 'world', summary: me.lastSummary });
            }
          }
          return;
        }

        /* ---------- the shared quarter ---------- */
        if (m.t === 'turnDone') {
          if (Number(m.turn) !== turn) return;   // a stale or repeated report
          if (me.alive === false || !me.country) return;
          submitted.add(id);
          maybeAdvanceTurn();
          return;
        }

        /* ---------- offers that the other player answers ---------- */
        if (m.t === 'propose') {
          const target = players.get(Number(m.target));
          if (!target || target.alive === false || target.id === id) return;
          const pid = 'p' + (seq++);
          proposals.set(pid, { from: id, to: target.id, kind: m.kind });
          deliver(target.id, {
            t: 'proposal', id: pid, kind: m.kind,
            fromName: me.name, fromCountry: me.country,
          });
          deliver(id, { t: 'proposalSent', id: pid, kind: m.kind, toName: target.name });
          return;
        }

        if (m.t === 'respond') {
          const pr = proposals.get(String(m.id));
          if (!pr || pr.to !== id) return;
          proposals.delete(String(m.id));
          const from = players.get(pr.from);
          const payload = {
            t: 'resolution', id: String(m.id), kind: pr.kind, choice: String(m.choice || ''),
            fromName: from ? from.name : 'שחקן', fromCountry: from ? from.country : null,
            toName: me.name, toCountry: me.country,
          };
          deliver(id, Object.assign({ side: 'target' }, payload));
          if (from) deliver(from.id, Object.assign({ side: 'sender' }, payload));
          return;
        }

        /* ---------- the United Nations ----------
           Bot countries are counted by the proposer's own client, which is
           the only side that holds the whole world's numbers; every human
           in the game answers for themselves. The room tallies both and
           announces one result, so everyone applies the same outcome. */
        if (m.t === 'unPropose') {
          if (me.alive === false || !me.country) return;
          const kind = m.kind === 'nuclear' ? 'nuclear' : 'sanctions';
          const targetCountry = String(m.targetCountry || '');
          if (!targetCountry || targetCountry === me.country) return;

          const vid = 'u' + (seq++);
          const voters = activePlayers().filter(p => p.id !== id);
          const v = {
            kind: kind, targetCountry: targetCountry, from: id,
            botFor: Math.max(0, Number(m.botFor) || 0),
            botAgainst: Math.max(0, Number(m.botAgainst) || 0),
            reason: String(m.reason || ''),
            pending: new Set(voters.map(p => p.id)),
            ballots: [],
          };
          votes.set(vid, v);
          deliver(id, { t: 'unProposed', id: vid, kind: kind, targetCountry: targetCountry, voters: voters.length });
          for (const p of voters) {
            deliver(p.id, {
              t: 'unVote', id: vid, kind: kind, targetCountry: targetCountry,
              fromName: me.name, fromCountry: me.country,
              isTarget: p.country === targetCountry,
            });
          }
          if (!voters.length) this._closeVote(vid);
          return;
        }

        if (m.t === 'unBallot') {
          const v = votes.get(String(m.id));
          if (!v || !v.pending.has(id)) return;
          v.pending.delete(id);
          v.ballots.push({ name: me.name, country: me.country, vote: m.vote === 'for' ? 'for' : 'against' });
          if (!v.pending.size) this._closeVote(String(m.id));
          return;
        }

        if (m.t === 'nukeLaunch') {
          const auth = nukeAuth.get(id);
          const targetCountry = String(m.targetCountry || '');
          if (!auth || auth.country !== targetCountry) {
            deliver(id, { t: 'error', msg: 'אין אישור של האו"ם לתקיפה הזו' });
            return;
          }
          nukeAuth.delete(id);
          const victim = [...players.values()].find(p => p.country === targetCountry && p.alive !== false);
          const news = {
            t: 'nukeUsed', byName: me.name, byCountry: me.country,
            targetCountry: targetCountry, victimId: victim ? victim.id : null,
          };
          broadcast(news);
          if (victim) { eliminate(victim, 'nuke'); broadcastRoom(); maybeAdvanceTurn(); }
          return;
        }

        /* ---------- war ---------- */
        if (m.t === 'declareWar') {
          const target = players.get(Number(m.target));
          if (!target || target.alive === false || target.id === id) return;
          const wid = 'w' + (seq++);
          wars.set(wid, { attacker: id, defender: target.id, stage: 'declared' });
          deliver(target.id, {
            t: 'warDeclared', id: wid,
            fromName: me.name, fromCountry: me.country,
          });
          deliver(id, { t: 'warSent', id: wid, toName: target.name, toCountry: target.country });
          return;
        }

        if (m.t === 'warDefend') {
          const war = wars.get(String(m.id));
          if (!war || war.defender !== id || war.stage !== 'declared') return;
          const posture = String(m.posture || 'defend');
          const attacker = players.get(war.attacker);
          if (!attacker) { wars.delete(String(m.id)); return; }

          // asking for a ceasefire hands the decision back to the attacker
          if (posture === 'ceasefire') {
            war.stage = 'ceasefire';
            deliver(attacker.id, {
              t: 'ceasefireAsked', id: String(m.id),
              fromName: me.name, fromCountry: me.country,
            });
            return;
          }
          war.posture = posture;
          this._resolveWar(String(m.id));
          return;
        }

        if (m.t === 'ceasefireAnswer') {
          const war = wars.get(String(m.id));
          if (!war || war.attacker !== id || war.stage !== 'ceasefire') return;
          const defender = players.get(war.defender);
          if (String(m.choice) === 'accept') {
            wars.delete(String(m.id));
            const me2 = players.get(id);
            const msg = {
              t: 'warEnded', id: String(m.id), outcome: 'ceasefire',
              attackerName: me2 ? me2.name : 'שחקן', attackerCountry: me2 ? me2.country : null,
              defenderName: defender ? defender.name : 'שחקן', defenderCountry: defender ? defender.country : null,
            };
            deliver(id, Object.assign({ side: 'attacker' }, msg));
            if (defender) deliver(defender.id, Object.assign({ side: 'defender' }, msg));
            return;
          }
          // refused: the hesitation costs the defender when the fighting starts
          war.stage = 'declared';
          war.posture = 'hesitated';
          this._resolveWar(String(m.id));
          return;
        }
      },

      /* Count a resolution and tell the whole room the same answer. */
      _closeVote(vid) {
        const v = votes.get(vid);
        if (!v) return;
        votes.delete(vid);
        const proposer = players.get(v.from);
        const humanFor = v.ballots.filter(b => b.vote === 'for').length;
        const humanAgainst = v.ballots.filter(b => b.vote === 'against').length;
        const forCount = v.botFor + humanFor + 1;            // the proposer votes for it
        const againstCount = v.botAgainst + humanAgainst;
        const passed = forCount > againstCount;

        if (passed && v.kind === 'nuclear' && proposer) {
          nukeAuth.set(proposer.id, { country: v.targetCountry, untilTurn: turn + 3 });
        }
        broadcast({
          t: 'unResult', id: vid, kind: v.kind, targetCountry: v.targetCountry,
          passed: passed, forCount: forCount, againstCount: againstCount,
          fromId: v.from, fromName: proposer ? proposer.name : 'שחקן',
          fromCountry: proposer ? proposer.country : null,
          ballots: v.ballots, reason: v.reason,
        });
      },

      /* Decide a war and tell both sides. The loser is out of the game. */
      _resolveWar(wid) {
        const war = wars.get(wid);
        if (!war) return;
        wars.delete(wid);
        const attacker = players.get(war.attacker);
        const defender = players.get(war.defender);
        if (!attacker || !defender) return;

        let a = warStrength(attacker.lastSummary);
        let d = warStrength(defender.lastSummary);
        if (war.posture === 'defend') d *= 1.3;        // dug in
        else if (war.posture === 'counter') { d *= 1.1; a *= 0.9; }  // trades risk for reach
        else if (war.posture === 'hesitated') d *= 0.8; // asked for peace, then had to fight
        a *= 0.75 + rnd() * 0.5;
        d *= 0.75 + rnd() * 0.5;

        const attackerWon = a >= d;
        const winner = attackerWon ? attacker : defender;
        const loser = attackerWon ? defender : attacker;

        const msg = {
          t: 'warResult', id: wid,
          winnerId: winner.id, winnerName: winner.name, winnerCountry: winner.country,
          loserId: loser.id, loserName: loser.name, loserCountry: loser.country,
          posture: war.posture || 'defend',
        };
        deliver(attacker.id, Object.assign({ side: attackerWon ? 'winner' : 'loser' }, msg));
        deliver(defender.id, Object.assign({ side: attackerWon ? 'loser' : 'winner' }, msg));
        // note the order: t must be applied last, or msg.t overwrites it
        broadcast(Object.assign({}, msg, { t: 'warNews' }));

        eliminate(loser, 'war');
        broadcastRoom();
        maybeAdvanceTurn();
      },
    };
  }

  return { createRoom: createRoom, warStrength: warStrength, botBallot: botBallot };
});
