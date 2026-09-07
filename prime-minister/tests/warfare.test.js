/*
 * Single player: the quarter clock, army command and war with the world
 *
 * Drives the real game in a real browser. Start the server first:
 *   npm start            # serves the game on :8080
 *   npx peer --port 9000 --host 127.0.0.1   # matchmaker, multiplayer suite only
 * then:  npm test
 */
const { chromium } = require('playwright');
const EXE = process.env.CHROME_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const w = ms => new Promise(r=>setTimeout(r,ms));
let fails=0; const ok=(c,m)=>{console.log((c?'✅':'❌')+' '+m); if(!c)fails++;};

(async () => {
  const br = await chromium.launch({ executablePath:EXE, args:['--no-sandbox'] });
  const ctx = await br.newContext({ viewport:{width:1100,height:1500}, deviceScaleFactor:2 });
  const pg = await ctx.newPage();
  const errs=[];
  pg.on('console',m=>{ if(m.type()==='error' && !/fonts\.g|favicon|Failed to load resource/i.test(m.text())) errs.push(m.text()); });
  pg.on('pageerror',e=>errs.push('PAGEERROR: '+e.message));

  await pg.goto((process.env.GAME_URL || 'http://localhost:8080')); await w(400);
  await pg.click('button:has-text("משחק יחיד")'); await w(300);
  await pg.evaluate(()=>{try{closeTutorial()}catch(e){}}); await w(150);
  await pg.click('.country-card >> nth=0'); await w(900);
  await pg.evaluate(()=>{try{closeTutorial()}catch(e){}}); await w(300);

  /* ---------- 1. the quarter clock ---------- */
  ok(await pg.isVisible('#turnClock'), 'a quarter clock is on screen');
  const t1 = await pg.textContent('#turnClockTime');
  ok(/^[45]:\d\d$/.test(t1.trim()), 'it starts near five minutes ("'+t1.trim()+'")');
  const money1 = await pg.evaluate(()=>state.treasury);
  await w(3200);
  const t2 = await pg.textContent('#turnClockTime');
  ok(t2.trim() !== t1.trim(), 'it is counting down ("'+t1.trim()+'" → "'+t2.trim()+'")');
  const money2 = await pg.evaluate(()=>state.treasury);
  ok(money1 !== money2, 'the treasury moves while the clock runs — metrics are live');

  /* the drift must not be charged twice at the end of the quarter */
  const drift = await pg.evaluate(()=>state.driftApplied.treasury);
  ok(Math.abs(drift) > 0, 'the drift is booked to a ledger ('+drift.toFixed(1)+')');
  await pg.click('#eventCard button.choice >> nth=0'); await w(600);
  ok(await pg.evaluate(()=>state.driftApplied.treasury) === 0, 'the ledger is settled and reset on the next quarter');

  /* ---------- 2. the army ---------- */
  await pg.evaluate(()=>openArmyView()); await w(500);
  ok(await pg.isVisible('#armyOverlay'), 'army command opens');
  const nActions = await pg.locator('.army-btn').count();
  ok(nActions === 7, 'it offers every lever (got '+nActions+')');
  await pg.screenshot({ path:'tests/shots/4-army.png' });
  const before = await pg.evaluate(()=>({ r: state.militaryReadiness, t: state.treasury }));
  await pg.click('.army-btn:has-text("גיוס מילואים")'); await w(500);
  const after = await pg.evaluate(()=>({ r: state.militaryReadiness, t: state.treasury }));
  ok(after.r > before.r && after.t < before.t, 'recruiting raises readiness and costs money');
  await pg.evaluate(()=>{ state.treasury = 100; openArmyView(); }); await w(300);
  ok(await pg.locator('.army-btn:disabled').count() > 0, 'what you cannot afford is disabled, not silently ignored');
  await pg.evaluate(()=>closeArmyView()); await w(300);

  /* ---------- 3. war against a computer-run country ---------- */
  await pg.evaluate(()=>{ state.treasury = 20000; openWorldView(); }); await w(700);
  const warBtns = await pg.locator('#worldGrid .wact-war').count();
  ok(warBtns > 20, 'every country can be attacked, not only the ones people run ('+warBtns+')');
  const target = await pg.evaluate(()=>Object.keys(worldState)[0]);
  await pg.evaluate(t=>{ state.militaryReadiness=100; state.stability=95; state.approval=90;
    state.bombInventory={conventional:9,chemical:3,nuclear:3};
    worldState[t].militaryReadiness=1; worldState[t].stability=3; worldState[t].approval=3;
    declareWarOnCountry(t); }, target);
  /* No war is ever a certainty — the odds are clamped to 95% either way — so
     the roll is pinned here rather than left to fail one run in twenty. */
  await pg.evaluate(()=>{ window.__realRandom = Math.random; Math.random = () => 0; });
  await w(600);
  ok(await pg.locator('#mpAsk.open').count()===1, 'declaring war asks first, with the odds on the table');
  const odds = await pg.textContent('#mpAskFrom');
  ok(/\d+%/.test(odds), 'the dialog quotes a win chance ("'+odds.trim()+'")');
  await pg.screenshot({ path:'tests/shots/5-war.png' });
  await pg.click('.mp-ask-btn:has-text("לצאת למתקפה")'); await w(1400);
  await pg.evaluate(()=>{ Math.random = window.__realRandom; });
  const conquered = await pg.evaluate(t=>({ c: worldState[t].conquered, list: state.conquests, over: !!state.defeatMessage }), target);
  ok(conquered.c === true && conquered.list.length === 1, 'an overwhelming attack conquers the country');
  await pg.screenshot({ path:'tests/shots/6-conquest.png' });

  /* the world does not shrug at an invasion */
  const rels = await pg.evaluate(()=>Object.values(state.relations).filter(v=>v<0).length);
  ok(rels > 5, 'the rest of the world turns on you after an invasion ('+rels+' soured)');

  /* ---------- 4. losing a war ends the term ---------- */
  await pg.evaluate(()=>{ const t=Object.keys(worldState).find(n=>!worldState[n].conquered);
    state.militaryReadiness=1; state.stability=2; state.approval=2; state.bombInventory={conventional:0,chemical:0,nuclear:0};
    worldState[t].militaryReadiness=100; worldState[t].stability=99; worldState[t].approval=99;
    const real = Math.random; Math.random = () => 0.999;   // pin the roll to a loss
    resolveWarWithBot(t);
    Math.random = real; });
  await w(900);
  ok(await pg.evaluate(()=>!!state.defeatMessage), 'losing a war you started ends the term');
  const overTxt = await pg.textContent('#mainArea');
  ok(/סוף הכהונה/.test(overTxt), 'the end-of-term screen is shown');

  /* ---------- 5. the world attacks you back, driven by relations ---------- */
  await pg.reload(); await w(400);
  await pg.click('button:has-text("משחק יחיד")'); await w(300);
  await pg.evaluate(()=>{try{closeTutorial()}catch(e){}}); await w(150);
  await pg.click('.country-card >> nth=0'); await w(900);
  await pg.evaluate(()=>{try{closeTutorial()}catch(e){}}); await w(300);

  const friendly = await pg.evaluate(()=>{
    state.turn = 9; state.lastAttackedTurn = 0;
    Object.keys(worldState).forEach(n=>{ state.relations[n] = 60; });
    let hits=0; for(let i=0;i<400;i++) if(botAggressionCheck()) hits++;
    return hits;
  });
  ok(friendly === 0, 'countries on good terms never attack you (0 of 400 rolls)');

  const hostile = await pg.evaluate(()=>{
    state.turn = 9; state.lastAttackedTurn = 0;
    state.militaryReadiness = 5; state.stability = 10; state.approval = 10;
    state.bombInventory = { conventional:0, chemical:0, nuclear:0 };
    Object.keys(worldState).forEach(n=>{ state.relations[n] = -100; worldState[n].militaryReadiness = 95; });
    let hits=0; for(let i=0;i<400;i++) if(botAggressionCheck()) hits++;
    return hits;
  });
  ok(hostile > 300, 'a hated, weak country gets invaded ('+hostile+' of 400 rolls)');

  const allied = await pg.evaluate(()=>{
    state.allies = Object.keys(worldState);
    let hits=0; for(let i=0;i<300;i++) if(botAggressionCheck()) hits++;
    return hits;
  });
  ok(allied === 0, 'an ally never turns on you, however bad the relations');

  await pg.evaluate(()=>{ state.allies=[]; const t=Object.keys(worldState)[0]; botDeclaresWar(t); });
  await w(700);
  ok(await pg.locator('#mpAsk.open').count()===1, 'you get to answer an invasion, not just read about it');
  const defOpts = await pg.locator('.mp-ask-btn').count();
  ok(defOpts === 3, 'three real answers: dig in, counter-attack, or sue for peace ('+defOpts+')');
  await pg.screenshot({ path:'tests/shots/7-invaded.png' });
  await pg.click('.mp-ask-btn:has-text("הפסקת אש")'); await w(800);
  ok(await pg.evaluate(()=>!state.defeatMessage), 'a ceasefire ends it without anyone being deposed');

  console.log(errs.length ? '\nJS ERRORS:\n'+errs.join('\n') : '\nno js errors');
  console.log(fails ? '\n'+fails+' FAILED' : '\nALL NEW-SYSTEM TESTS PASSED');
  await br.close();
  process.exit(fails||errs.length ? 1 : 0);
})();
