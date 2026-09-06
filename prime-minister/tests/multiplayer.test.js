/*
 * Multiplayer: offers, shared quarters and war between players
 *
 * Drives the real game in a real browser. Start the server first:
 *   npm start            # serves the game on :8080
 *   npx peer --port 9000 --host 127.0.0.1   # matchmaker, multiplayer suite only
 * then:  npm test
 */
const { chromium }=require('playwright');
const EXE = process.env.CHROME_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const B = process.env.GAME_URL || (process.env.GAME_URL || 'http://localhost:8080');
const w=ms=>new Promise(r=>setTimeout(r,ms));
let fails=0; const ok=(c,m)=>{console.log((c?'✅':'❌')+' '+m); if(!c)fails++;};
const noise=t=>/Failed to load resource|ERR_CONNECTION|fonts\.g|favicon/i.test(t);
const CFG=`window.MP_PEER_CONFIG={host:'localhost',port:9000,path:'/',secure:false};`;

(async()=>{
  const br=await chromium.launch({executablePath:EXE,args:['--no-sandbox']});
  async function open(name){
    const ctx=await br.newContext({viewport:{width:900,height:1000}});
    await ctx.addInitScript(CFG);
    const pg=await ctx.newPage();
    const errs=[]; pg.on('console',m=>{if(m.type()==='error'&&!noise(m.text()))errs.push(m.text());});
    pg.on('pageerror',e=>errs.push('PAGEERROR: '+e.message));
    await pg.goto(B); await w(400);
    await pg.click('button:has-text("משחק מרובה")'); await w(250);
    await pg.fill('#mpName',name);
    return {pg,errs,name};
  }
  const A=await open('אבי');
  await A.pg.click('button:has-text("צור שרת")');
  await A.pg.waitForFunction(()=>/^\d{2}$/.test((document.getElementById('mpCodeBig')||{}).textContent||''),{timeout:20000});
  const code=(await A.pg.locator('#mpCodeBig').textContent()).trim();
  const G=await open('דנה');
  await G.pg.fill('#mpRoom',code); await G.pg.click('#mpConnectBtn');
  await G.pg.waitForFunction(()=>document.querySelectorAll('.mp-player').length>=2,{timeout:25000});
  await A.pg.click('#mpStartBtn'); await w(900);
  await A.pg.click('.country-card:has-text("ישראל") >> nth=0'); await w(900);
  await G.pg.click('.country-card:has-text("קנדה") >> nth=0'); await w(1200);
  ok(await A.pg.isVisible('#gameRoot') && await G.pg.isVisible('#gameRoot'),'both players are in the game (room '+code+')');

  /* ---------- 1. an offer is a question, not something done to you ---------- */
  const openWorld=async p=>{ await p.evaluate(()=>openWorldView()); await w(700); };
  const shutWorld=async p=>{ await p.evaluate(()=>closeWorldView()); await w(400); };
  await openWorld(A.pg);
  const gTreasuryBefore = await G.pg.evaluate(()=>state.treasury);
  await A.pg.locator('#worldGrid .world-card:has-text("קנדה") button:has-text("סחר")').first().click();
  await w(1200);
  ok(await G.pg.locator('#mpAsk.open').count()===1,'the friend gets a decision panel, not a silent effect');
  const askTitle=await G.pg.locator('#mpAskTitle').textContent();
  ok(/סחר/.test(askTitle),'panel says what is on offer: "'+askTitle.trim()+'"');
  /* The quarter clock drifts the treasury by a couple of units a second, so
     equality is the wrong test; what matters is that the offer's 350 has not
     landed while it is still only an offer. */
  const gDrift = Math.abs(await G.pg.evaluate(()=>state.treasury) - gTreasuryBefore);
  ok(gDrift < 100,'nothing was applied while the offer was pending (moved '+gDrift.toFixed(1)+', payout is 350)');
  await G.pg.screenshot({path:'tests/shots/1-offer.png'});
  await G.pg.click('.mp-ask-btn:has-text("לחתום")'); await w(1200);
  ok(await G.pg.evaluate(()=>state.treasury) > gTreasuryBefore,'accepting pays the friend');
  const aLog=await A.pg.locator('#log').textContent();
  ok(/דנה/.test(aLog)&&/סחר/.test(aLog),'the sender is told the offer was accepted');

  /* ---------- 2. sanctions can be answered in kind ---------- */
  await openWorld(A.pg);
  const aT=await A.pg.evaluate(()=>state.treasury);
  await A.pg.locator('#worldGrid .world-card:has-text("קנדה") button:has-text("סנקציות")').first().click();
  await w(1200);
  const opts=await G.pg.locator('.mp-ask-btn').count();
  ok(opts===3,'sanctions offer the target three real answers (got '+opts+')');
  await G.pg.screenshot({path:'tests/shots/2-sanction.png'});
  await G.pg.click('.mp-ask-btn:has-text("סנקציות נגד")'); await w(1200);
  ok(await A.pg.evaluate(()=>state.treasury) < aT,'answering in kind costs the sender too');

  /* ---------- 3. the quarter is shared ---------- */
  await shutWorld(A.pg);
  const turnOf=p=>p.evaluate(()=>state.turn);
  const t0=await turnOf(A.pg);
  ok(t0===await turnOf(G.pg),'both players start the same quarter ('+t0+')');
  await A.pg.click('#eventCard button.choice >> nth=0'); await w(900);
  ok(await A.pg.evaluate(()=>document.body.classList.contains('mp-waiting')),'after committing, A is held until the others commit');
  const waitTxt=await A.pg.locator('#mpWaitNames').textContent();
  ok(/דנה/.test(waitTxt),'A is told who it waits for: "'+waitTxt.trim()+'"');
  await A.pg.screenshot({path:'tests/shots/3-waiting.png'});
  ok(!(await G.pg.evaluate(()=>document.body.classList.contains('mp-waiting'))),'B is not held — B has not played yet');
  await G.pg.click('#eventCard button.choice >> nth=0'); await w(1200);
  ok(!(await A.pg.evaluate(()=>document.body.classList.contains('mp-waiting'))),'A is released once B commits');
  const tA=await turnOf(A.pg), tG=await turnOf(G.pg);
  ok(tA===tG && tA===t0+1,'both moved to the same next quarter ('+tA+' / '+tG+')');

  /* ---------- 4. war ends someone's game ---------- */
  await A.pg.evaluate(()=>{ state.militaryReadiness=100; state.stability=95; state.approval=90; });
  await G.pg.evaluate(()=>{ state.militaryReadiness=1; state.stability=5; state.approval=5; });
  await openWorld(A.pg);
  const warBtn=A.pg.locator('#worldGrid .world-card:has-text("קנדה") button:has-text("הכרז מלחמה")').first();
  ok(await warBtn.count()===1,'a war button appears on a country a real player runs');
  await warBtn.click(); await w(600);
  await A.pg.click('.mp-ask-btn:has-text("להכריז מלחמה")'); await w(1200);
  ok(await G.pg.locator('#mpAsk.open').count()===1,'the defender must answer the declaration');
  await G.pg.screenshot({path:'tests/shots/4-war.png'});
  await G.pg.click('.mp-ask-btn:has-text("להתבצר")'); await w(1600);
  const gOver=await G.pg.locator('#mainArea').textContent();
  ok(/סוף הכהונה/.test(gOver),'the loser gets the end-of-term screen — their game is over');
  const aLog2=await A.pg.locator('#log').textContent();
  ok(/ניצחת במלחמה/.test(aLog2),'the winner is told they won');
  await G.pg.screenshot({path:'tests/shots/5-defeated.png'});

  /* ---------- 5. the survivor is not stuck waiting for a dead player ---------- */
  await shutWorld(A.pg);
  const tBefore=await turnOf(A.pg);
  await A.pg.click('#eventCard button.choice >> nth=0'); await w(1400);
  ok(await turnOf(A.pg)===tBefore+1,'the winner keeps playing alone, not blocked by the eliminated player');

  const errs=A.errs.concat(G.errs);
  ok(errs.length===0,'no JS errors ('+(errs.slice(0,3).join(' | ')||'none')+')');
  console.log('\n'+(fails===0?'ALL MULTIPLAYER FEATURE TESTS PASSED':fails+' FAILED'));
  await br.close(); process.exit(fails?1:0);
})().catch(e=>{console.error('ERR',e);process.exit(2)});
