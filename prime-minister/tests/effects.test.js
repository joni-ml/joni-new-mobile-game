/*
 * Effects control and the national address.
 *
 * Start the server first (npm start), then: node tests/effects.test.js
 */
const { chromium } = require('playwright');
const EXE = process.env.CHROME_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const URL = process.env.GAME_URL || 'http://localhost:8080';
const w = ms => new Promise(r=>setTimeout(r,ms));
let fails=0; const ok=(c,m)=>{console.log((c?'✅':'❌')+' '+m); if(!c)fails++;};

(async () => {
  const br = await chromium.launch({ executablePath:EXE, args:['--no-sandbox'] });
  const ctx = await br.newContext({ viewport:{width:1000,height:900}, deviceScaleFactor:2 });
  const pg = await ctx.newPage();
  const errs=[];
  pg.on('console',m=>{ if(m.type()==='error' && !/fonts\.g|favicon|Failed to load resource/i.test(m.text())) errs.push(m.text()); });
  pg.on('pageerror',e=>errs.push('PAGEERROR: '+e.message));

  const start = async () => {
    await pg.click('button:has-text("משחק יחיד")'); await w(300);
    await pg.evaluate(()=>{try{closeTutorial()}catch(e){}}); await w(150);
    await pg.click('.country-card:has-text("ישראל") >> nth=0'); await w(900);
    await pg.evaluate(()=>{try{closeTutorial()}catch(e){}}); await w(400);
  };
  await pg.goto(URL); await w(400); await start();

  /* ---------- effects control ---------- */
  await pg.evaluate(()=>openFxView()); await w(400);
  ok(await pg.isVisible('#fxOverlay'), 'the effects panel opens');
  ok(await pg.locator('.fx-preset').count() === 3, 'three presets: cinematic, standard, performance');
  ok(await pg.locator('.fx-toggle').count() === 7, 'and a switch for each individual effect');
  await pg.screenshot({ path:'tests/shots/9-effects.png' });

  await pg.click('.fx-preset:has-text("חסכוני")'); await w(400);
  const perf = await pg.evaluate(()=>({ ...FX }));
  ok(perf.reflections === false && perf.weather === false && perf.grain === false,
     'performance mode really turns the expensive passes off');
  ok(await pg.locator('.fx-preset.on:has-text("חסכוני")').count() === 1, 'the chosen preset is marked');

  /* the scene must still be drawable with everything off */
  const drewBare = await pg.evaluate(()=>{
    try { drawPixelScene(document.getElementById('pixelCanvas'), state.country, state, 40); return true; }
    catch(e){ return 'THREW: ' + e.message; }
  });
  ok(drewBare === true, 'the scene still renders with every effect switched off');

  await pg.click('.fx-toggle:has-text("השתקפות במים")'); await w(350);
  const custom = await pg.evaluate(()=>({ ...FX }));
  ok(custom.reflections === true && custom.preset === 'custom',
     'touching one switch turns it on and drops out of the preset');

  /* the choice has to survive a reload or it is not a setting */
  await pg.reload(); await w(500);
  const restored = await pg.evaluate(()=>({ ...FX }));
  ok(restored.reflections === true && restored.weather === false,
     'the effect settings are remembered on the device');
  await pg.evaluate(()=>setFxPreset('cinematic')); await w(300);
  await start();

  /* ---------- the national address ---------- */
  ok(await pg.evaluate(()=>addressAvailable()), 'the address is available at the start of a term');
  await pg.evaluate(()=>openAddress()); await w(500);
  ok(await pg.locator('#mpAsk.open').count() === 1, 'it asks before going live');
  const odds = await pg.textContent('#mpAskFrom');
  ok(/\d+%/.test(odds), 'and quotes the chance it lands ("'+odds.trim()+'")');

  /* charisma is the lever the player can actually pull */
  const scaling = await pg.evaluate(()=>{
    const out = [];
    for(const lvl of [1,5]){ state.skills.rhetoric = lvl; out.push(addressOdds()); }
    return out;
  });
  ok(scaling[1] > scaling[0] + 0.3,
     'charisma moves the odds a great deal ('+(scaling[0]*100).toFixed(0)+'% → '+(scaling[1]*100).toFixed(0)+'%)');

  const before = await pg.evaluate(()=>state.approval);
  await pg.evaluate(()=>{ state.skills.rhetoric = 5; state.stability = 90; state.approval = 70; deliverAddress(); });
  await w(500);
  const after = await pg.evaluate(()=>({ a: state.approval, cinema, cls: document.getElementById('pixelFrame').className }));
  ok(after.a > 70, 'a speech that lands lifts the country ('+after.a.toFixed(0)+'%)');
  ok(after.cinema > 0, 'the broadcast plays out on the monitor');
  ok(/cinema/.test(after.cls), 'and the monitor goes cinematic while it runs');
  await pg.screenshot({ path:'tests/shots/10-address.png' });

  ok(!(await pg.evaluate(()=>addressAvailable())), 'you cannot speak twice in the same year');
  await pg.evaluate(()=>{ state.turn += 4; }); await w(100);
  ok(await pg.evaluate(()=>addressAvailable()), 'a year later the country will listen again');

  /* a failed address costs — it is a gamble, not a free button */
  const dropped = await pg.evaluate(()=>{
    state.approval = 60; state.skills.rhetoric = 1; state.stability = 10;
    state.lastAddressTurn = -99;
    const odds = addressOdds();
    const before = state.approval;
    let worst = before;
    for(let i=0;i<200;i++){ state.approval = 60; state.lastAddressTurn = -99; deliverAddress();
      worst = Math.min(worst, state.approval); }
    return { odds, worst };
  });
  ok(dropped.worst < 60, 'a speech that misses costs approval (worst seen '+dropped.worst.toFixed(0)+'%)');
  ok(dropped.odds < 0.55, 'and a weak speaker in an unstable country is unlikely to land it ('+(dropped.odds*100).toFixed(0)+'%)');

  console.log(errs.length ? '\nJS ERRORS:\n'+errs.join('\n') : '\nno js errors');
  console.log(fails ? '\n'+fails+' FAILED' : '\nALL EFFECTS TESTS PASSED');
  await br.close();
  process.exit(fails||errs.length ? 1 : 0);
})();
