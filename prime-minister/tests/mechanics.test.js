/*
 * Causality: the cabinet's advice, the ledger of what moved, and the queue
 * of consequences already in flight.
 *
 * Start the server first (npm start), then: node tests/mechanics.test.js
 */
const { chromium } = require('playwright');
const EXE = process.env.CHROME_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const URL = process.env.GAME_URL || 'http://localhost:8080';
const w = ms => new Promise(r=>setTimeout(r,ms));
let fails=0; const ok=(c,m)=>{console.log((c?'✅':'❌')+' '+m); if(!c)fails++;};

(async () => {
  const br = await chromium.launch({ executablePath:EXE, args:['--no-sandbox'] });
  const ctx = await br.newContext({ viewport:{width:1100,height:1600}, deviceScaleFactor:2 });
  const pg = await ctx.newPage();
  const errs=[];
  pg.on('console',m=>{ if(m.type()==='error' && !/fonts\.g|favicon|Failed to load resource/i.test(m.text())) errs.push(m.text()); });
  pg.on('pageerror',e=>errs.push('PAGEERROR: '+e.message));

  await pg.goto(URL); await w(400);
  await pg.click('button:has-text("משחק יחיד")'); await w(300);
  await pg.evaluate(()=>{try{closeTutorial()}catch(e){}}); await w(150);
  await pg.click('.country-card >> nth=0'); await w(900);
  await pg.evaluate(()=>{try{closeTutorial()}catch(e){}}); await w(400);

  /* ---------- the cabinet takes a position before you decide ---------- */
  const advice = await pg.evaluate(()=>state.currentAdvice);
  ok(Array.isArray(advice) && advice.length === 3, 'all three ministers take a position on the dilemma');
  ok(advice.every(a => Number.isInteger(a.choice) && a.choice >= 0), 'each one backs a specific option');
  ok(await pg.locator('#eventCard .backer').count() === 3, 'their names sit on the option they back');

  /* the position is read from their agenda, not rolled blind */
  const agendaDriven = await pg.evaluate(()=>{
    const ev = { id:'t', choices:[
      { title:'A', desc:'', tags:['austerity'], impact:{approval:0,stability:0,treasury:0,tension:0} },
      { title:'B', desc:'', tags:['spending'],  impact:{approval:0,stability:0,treasury:0,tension:0} } ]};
    state.ministers = [{ name:'שרת האוצר', loyalty:70, likes:['austerity'], dislikes:['spending'] }];
    let backedA = 0;
    for(let t=1;t<=40;t++){ state.turn = t; if(cabinetAdvice(ev)[0].choice === 0) backedA++; }
    return backedA;
  });
  ok(agendaDriven >= 38, 'a minister backs their own agenda, not a coin flip ('+agendaDriven+'/40)');

  /* ---------- backing them buys loyalty, overruling them spends it ---------- */
  const loyalty = await pg.evaluate(()=>{
    state.ministers = [{ name:'שר א', loyalty:50, likes:[], dislikes:[] },
                       { name:'שר ב', loyalty:50, likes:[], dislikes:[] }];
    state.currentAdvice = [{ name:'שר א', choice:0 }, { name:'שר ב', choice:1 }];
    applyAdviceLoyalty(0);
    return state.ministers.map(m=>m.loyalty);
  });
  ok(loyalty[0] > 50 && loyalty[1] < 50, 'the minister you sided with gains, the one you overruled loses');

  /* ---------- the ledger explains the quarter ---------- */
  await pg.reload(); await w(400);
  await pg.click('button:has-text("משחק יחיד")'); await w(300);
  await pg.evaluate(()=>{try{closeTutorial()}catch(e){}}); await w(150);
  await pg.click('.country-card >> nth=0'); await w(900);
  await pg.evaluate(()=>{try{closeTutorial()}catch(e){}}); await w(400);

  const before = await pg.evaluate(()=>({ a: state.approval, t: state.treasury }));
  await pg.click('#eventCard button.choice >> nth=0'); await w(900);
  const ledger = await pg.evaluate(()=>state.ledger);
  ok(ledger.length >= 2, 'the quarter is booked stage by stage ('+ledger.length+' entries)');
  ok(ledger.some(e=>/ההחלטה/.test(e.label)), 'the decision itself is one of them');
  ok(ledger.some(e=>/תקציב/.test(e.label)), 'so is the budget baseline');
  ok(await pg.locator('#ledgerBody .ledger-row').count() >= 2, 'and it is on screen, not just in memory');

  /* every point of change must be attributable — that is the whole promise */
  const after = await pg.evaluate(()=>({ a: state.approval, t: state.treasury }));
  const sum = k => ledger.reduce((n,e)=>n + (e.d[k]||0), 0);
  const approvalGap = Math.abs((after.a - before.a) - sum('approval'));
  const treasuryGap = Math.abs((after.t - before.t) - sum('treasury'));
  ok(approvalGap < 1.5, 'the approval the ledger explains matches the approval that moved (off by '+approvalGap.toFixed(2)+')');
  ok(treasuryGap < 1.5, 'and the same for the treasury (off by '+treasuryGap.toFixed(2)+')');

  /* ---------- consequences in flight are visible ---------- */
  await pg.evaluate(()=>{
    state.delayed = [
      { dueTurn: state.turn + 1, label:'המחאה שהוזנחה גלשה למהומות', effect:()=>{} },
      { dueTurn: state.turn + 3, label:'משבר אשראי בגלל האזהרה שהתעלמת ממנה', effect:()=>{} } ];
    render();
  });
  await w(400);
  ok(await pg.locator('#pendingBody .pending-row').count() === 2, 'what is already coming is on the board');
  ok(await pg.locator('#pendingBody .pending-row.soon').count() === 1, 'the imminent one is marked as imminent');
  const firstWhen = await pg.textContent('#pendingBody .pending-row >> nth=0');
  ok(/הבא/.test(firstWhen), 'the nearest consequence is listed first ("'+firstWhen.trim().split('\n')[0]+'")');
  await pg.screenshot({ path:'tests/shots/8-causality.png' });

  /* ---------- the sky moves with the clock, not only with the quarter ---------- */
  const drift = await pg.evaluate(()=>{
    const a = dayFraction(state);
    turnSecondsLeft = Math.max(0, turnSecondsLeft - 120);
    const b = dayFraction(state);
    return b - a;
  });
  ok(drift > 0.05, 'the light advances while the quarter clock runs (+'+drift.toFixed(3)+' of a day)');

  console.log(errs.length ? '\nJS ERRORS:\n'+errs.join('\n') : '\nno js errors');
  console.log(fails ? '\n'+fails+' FAILED' : '\nALL CAUSALITY TESTS PASSED');
  await br.close();
  process.exit(fails||errs.length ? 1 : 0);
})();
