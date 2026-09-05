/* =========================================================
   MULTIPLAYER (Artifact edition)
   Same screens as the self-hosted build, but the shared room lives in
   the artifact's own shared store instead of a server or a direct link.
   Nothing above this block was modified.
   ========================================================= */
const MP = {
  active:false, started:false, playerId:null, hostId:null,
  name:'', room:null,
  players:{}, humanCountries:{}, humanState:{},
  worldOpen:false, _toastT:null,
  db:null, _unsub:[], _lastPlayers:{}, _sawStart:false, _roomGone:false,

  $(id){ return document.getElementById(id); },

  /* the shared store arrives asynchronously, and may never arrive */
  dbReady(){
    if(MP._dbPromise) return MP._dbPromise;
    MP._dbPromise = (window.claude && typeof window.claude.use==='function')
      ? window.claude.use('db').catch(()=>null)
      : Promise.resolve(null);
    return MP._dbPromise;
  },

  showFormError(msg, kind){
    const el=MP.$('mpFormError');
    if(el){ el.textContent=msg; el.className='mp-formerror'+(kind?' '+kind:''); el.style.display='block'; }
  },
  clearFormError(){ const el=MP.$('mpFormError'); if(el){ el.style.display='none'; el.textContent=''; } },
  setStatus(msg,kind){ const el=MP.$('mpStatus'); if(el){ el.textContent=msg; el.className='mp-status '+(kind||''); } },
  toast(msg,kind){
    let t=MP.$('mpToast');
    if(!t){ t=document.createElement('div'); t.id='mpToast';
      t.style.cssText='position:fixed;bottom:20px;left:50%;transform:translateX(-50%);z-index:3000;background:#1b2029;border:1px solid #b8934b;color:#e9e5da;padding:10px 16px;border-radius:10px;font-family:Assistant,sans-serif;font-size:13px;box-shadow:0 6px 16px rgba(0,0,0,.5);max-width:90%;text-align:center;';
      document.body.appendChild(t); }
    t.textContent=msg; t.style.display='block';
    t.style.borderColor = kind==='bad'?'#b4483f':(kind==='good'?'#4c8c7b':'#b8934b');
    clearTimeout(MP._toastT); MP._toastT=setTimeout(()=>{t.style.display='none';},3500);
  },

  /* ---------- screens ---------- */
  chooseSingle(){ MP.active=false; MP.$('mpModeOverlay').classList.remove('open'); },
  chooseMulti(){
    MP.$('mpModeOverlay').classList.remove('open');
    MP.tutorialClose();
    MP.showForm(); MP.clearFormError();
    MP.$('mpSetupOverlay').classList.add('open');
    MP.dbReady().then(db=>{
      if(!db) MP.showFormError('משחק עם אנשים עובד רק כשפותחים את המשחק מהקישור המשותף. משחק יחיד עובד כאן רגיל.','warn');
    });
  },
  backToMode(){ MP.$('mpSetupOverlay').classList.remove('open'); MP.$('mpModeOverlay').classList.add('open'); },
  tutorialClose(){ const t=MP.$('tutorialOverlay'); if(t) t.classList.remove('open'); },
  showForm(){ MP.$('mpLobby').style.display='none'; MP.$('mpCodeBox').style.display='none'; MP.$('mpConnectForm').style.display='block'; },
  enterLobby(msg){
    MP.clearFormError();
    MP.$('mpConnectForm').style.display='none';
    MP.$('mpLobby').style.display='block';
    MP.$('mpCodeBox').style.display='none';
    MP.setStatus(msg,'wait');
  },
  onCodeInput(el){ el.value=el.value.replace(/\D/g,'').slice(0,2); },

  newId(){ return 'p'+Math.random().toString(36).slice(2,10)+Date.now().toString(36).slice(-4); },
  randomCode(){ return String(10+Math.floor(Math.random()*90)); },

  /* ---------- create / join ---------- */
  async createGame(){
    const db=await MP.dbReady();
    if(!db){ MP.showFormError('משחק עם אנשים לא זמין כאן. פתחו את המשחק מהקישור המשותף.','warn'); return; }
    MP.name=(MP.$('mpName').value||'').trim()||'שחקן';
    MP.enterLobby('פותח חדר…');
    let code=null;
    for(let i=0;i<25;i++){
      const c=MP.randomCode();
      try{
        const snap=await db.doc('rooms/'+c).get();
        if(!snap.exists){ code=c; break; }
      }catch(e){ MP.showForm(); MP.showFormError('לא הצלחנו לפתוח חדר. נסו שוב.'); return; }
    }
    if(!code){ MP.showForm(); MP.showFormError('כל המספרים תפוסים כרגע. נסו שוב בעוד רגע.'); return; }

    MP.db=db; MP.playerId=MP.newId(); MP.room=code; MP.hostId=MP.playerId;
    try{
      await db.doc('rooms/'+code).set({ host:MP.playerId, started:false, createdAt:Date.now() });
      await db.doc('rooms/'+code+'/players/'+MP.playerId).set(MP.myDoc());
    }catch(e){ MP.showForm(); MP.showFormError('לא הצלחנו לפתוח חדר. נסו שוב.'); return; }

    MP.active=true;
    MP.onMessage({t:'welcome', playerId:MP.playerId});
    MP.onMessage({t:'created', room:code});
    MP.subscribe();
  },

  async joinGame(){
    const code=(MP.$('mpRoom').value||'').trim();
    if(!/^\d{1,2}$/.test(code)){ MP.toast('הקלידו את מספר החדר של החבר (שתי ספרות)','bad'); return; }
    const db=await MP.dbReady();
    if(!db){ MP.showFormError('משחק עם אנשים לא זמין כאן. פתחו את המשחק מהקישור המשותף.','warn'); return; }
    MP.name=(MP.$('mpName').value||'').trim()||'שחקן';
    MP.enterLobby('מחפש את חדר '+code+'…');
    let snap;
    try{ snap=await db.doc('rooms/'+code).get(); }
    catch(e){ MP.showForm(); MP.showFormError('שגיאת חיבור. נסו שוב.'); return; }
    if(!snap.exists){
      MP.showForm();
      MP.showFormError('לא נמצא חדר עם המספר '+code+'. ודאו שהחבר פתח חדר ושהמספר נכון.');
      return;
    }
    const info=snap.data()||{};
    MP.db=db; MP.playerId=MP.newId(); MP.room=code; MP.hostId=info.host||null;
    try{ await db.doc('rooms/'+code+'/players/'+MP.playerId).set(MP.myDoc()); }
    catch(e){ MP.showForm(); MP.showFormError('לא הצלחנו להצטרף. נסו שוב.'); return; }

    MP.active=true;
    MP.onMessage({t:'welcome', playerId:MP.playerId});
    MP.onMessage({t:'joined', room:code});
    MP.subscribe();
  },

  myDoc(){
    return { id:MP.playerId, name:MP.name, country:MP.myCountry||null, summary:MP.lastSummary||null, ts:Date.now() };
  },

  /* ---------- live subscriptions ---------- */
  subscribe(){
    const db=MP.db, code=MP.room;
    MP._unsub.push(db.doc('rooms/'+code).onSnapshot(snap=>{
      if(!snap.exists){
        if(MP._roomGone) return;
        MP._roomGone=true;
        if(MP.playerId!==MP.hostId){
          MP.toast('המארח סגר את החדר','bad');
          const p=MP.$('mpPill'); if(p) p.style.borderColor='#b4483f';
        }
        return;
      }
      const d=snap.data()||{};
      MP.hostId=d.host||MP.hostId;
      MP.renderLobby();
      if(d.started && !MP._sawStart){ MP._sawStart=true; MP.onMessage({t:'start'}); }
    }, ()=>{}));

    MP._unsub.push(db.collection('rooms/'+code+'/players').onSnapshot(snap=>{
      const players={};
      snap.docs.forEach(doc=>{
        const d=doc.data()||{};
        players[d.id||doc.id]={ id:d.id||doc.id, name:d.name||'שחקן', country:d.country||null };
        // feed everyone else's live country into the world view
        if((d.id||doc.id)!==MP.playerId && d.summary){ MP.applyWorldUpdate(d.summary); }
      });
      MP.players=players;
      MP._lastPlayers=players;
      MP.humanCountries={};
      Object.values(players).forEach(p=>{ if(p.country) MP.humanCountries[p.country]=p.id; });
      Object.keys(MP.humanState).forEach(c=>{ if(!MP.humanCountries[c]) delete MP.humanState[c]; });
      MP.renderLobby(); MP.decorateGrid(); MP.updatePill();
    }, ()=>{}));

    MP._unsub.push(db.collection('rooms/'+code+'/events').where('to','==',MP.playerId).onSnapshot(snap=>{
      snap.docChanges().forEach(ch=>{
        if(ch.type!=='added') return;
        const d=ch.doc.data()||{};
        MP.receiveDiplo({ type:d.type, fromName:d.fromName, fromCountry:d.fromCountry });
        db.doc('rooms/'+MP.room+'/events/'+ch.doc.id).delete().catch(()=>{});
      });
    }, ()=>{}));

    window.addEventListener('beforeunload', MP.cleanup);
  },

  cleanup(){
    if(!MP.db || !MP.room || !MP.playerId) return;
    try{
      MP.db.doc('rooms/'+MP.room+'/players/'+MP.playerId).delete();
      if(MP.playerId===MP.hostId) MP.db.doc('rooms/'+MP.room).delete();
    }catch(_){}
  },
  leave(){
    MP.cleanup();
    MP._unsub.forEach(u=>{ try{ u(); }catch(_){} }); MP._unsub=[];
    MP.active=false; MP.started=false; MP._sawStart=false; MP._roomGone=false;
    MP.db=null; MP.room=null; MP.playerId=null; MP.myCountry=null;
    MP.showForm();
    MP.$('mpSetupOverlay').classList.remove('open');
    MP.$('mpModeOverlay').classList.add('open');
    const p=MP.$('mpPill'); if(p) p.classList.remove('open');
  },

  /* ---------- outgoing ---------- */
  send(obj){
    if(!MP.active || !MP.db || !MP.room) return;
    const db=MP.db, code=MP.room;
    if(obj.t==='start'){
      if(MP.playerId!==MP.hostId) return;
      db.doc('rooms/'+code).update({started:true}).catch(()=>{});
      return;
    }
    if(obj.t==='claim'){
      const owner=MP.humanCountries[obj.country];
      if(owner && owner!==MP.playerId){ MP.onMessage({t:'error', msg:'המדינה כבר נתפסה'}); return; }
      MP.myCountry=obj.country;
      db.doc('rooms/'+code+'/players/'+MP.playerId).update({country:obj.country, ts:Date.now()}).catch(()=>{});
      return;
    }
    if(obj.t==='state'){
      MP.lastSummary=obj.summary;
      db.doc('rooms/'+code+'/players/'+MP.playerId).update({summary:obj.summary, ts:Date.now()}).catch(()=>{});
      return;
    }
    if(obj.t==='diplo'){
      db.collection('rooms/'+code+'/events').add({
        to:obj.target, type:obj.type, fromName:MP.name, fromCountry:MP.myCountry||null, ts:Date.now()
      }).catch(()=>{});
      return;
    }
  },

  /* ---------- incoming ---------- */
  onMessage(m){
    switch(m.t){
      case 'welcome': MP.playerId=m.playerId; break;
      case 'created':
      case 'joined':
        MP.room=m.room;
        MP.$('mpCodeBig').textContent=m.room;
        MP.$('mpCodeBox').style.display='block';
        MP.setStatus(m.t==='created' ? 'החדר נפתח! מסרו את המספר לחברים.' : 'הצטרפת לחדר מספר '+m.room+'!', 'ok');
        MP.updatePill();
        break;
      case 'start': MP.goPickCountry(); break;
      case 'error': MP.toast(m.msg||'שגיאה','bad'); break;
    }
  },

  renderLobby(){
    const list=MP.$('mpPlayerList');
    const players=Object.values(MP.players);
    if(list){
      list.innerHTML = players.length ? players.map(p=>{
        const me=p.id===MP.playerId, host=p.id===MP.hostId;
        const c=p.country ? p.country : '— טרם בחר/ה מדינה —';
        return '<div class="mp-player'+(me?' me':'')+'"><span class="who">'+(host?'👑 ':'')+p.name+(me?' (אתה)':'')+'</span><span class="cc">'+c+'</span></div>';
      }).join('') : '<div class="mp-hint">אין עדיין שחקנים.</div>';
    }
    const isHost = MP.playerId!=null && MP.playerId===MP.hostId;
    const btn=MP.$('mpStartBtn'), hint=MP.$('mpLobbyHint');
    if(btn) btn.style.display = isHost ? 'inline-block' : 'none';
    if(hint){
      hint.className='mp-hint';
      if(isHost){
        hint.textContent = players.length<2
          ? 'ממתינים שחברים יצטרפו. אפשר גם להתחיל כבר עכשיו.'
          : players.length+' שחקנים בחדר — כשכולם כאן לחצו "התחל משחק".';
      } else {
        hint.textContent='ממתינים שהמארח יתחיל את המשחק';
        hint.className='mp-hint mp-waitdots';
      }
    }
  },
  startGame(){ MP.send({t:'start'}); },
  updatePill(){
    const pill=MP.$('mpPill'); if(!pill) return;
    pill.textContent='🌍 חדר '+(MP.room||'')+' · '+Object.keys(MP.players).length+' שחקנים';
  },
  decorateGrid(){
    if(!MP.active) return;
    document.querySelectorAll('#countryGrid .country-card').forEach(card=>{
      const nameEl=card.querySelector('.cname'); if(!nameEl) return;
      const name=nameEl.textContent.trim();
      let claim=card.querySelector('.mp-claim');
      if(!claim){ claim=document.createElement('div'); claim.className='mp-claim'; card.appendChild(claim); }
      const owner=MP.humanCountries[name];
      if(owner && owner!==MP.playerId){
        const p=MP.players[owner];
        card.classList.add('mp-taken');
        claim.textContent='נתפס ע"י '+(p?p.name:'שחקן');
      } else {
        card.classList.remove('mp-taken');
        claim.textContent = owner===MP.playerId ? 'המדינה שלך' : 'פנוי';
      }
    });
  },
  goPickCountry(){
    MP.tutorialClose();
    MP.$('mpSetupOverlay').classList.remove('open');
    MP.decorateGrid();
    MP.toast('המשחק התחיל! בחר/י מדינה פנויה','good');
  },
  onGameStart(){
    MP.started=true; MP.tutorialClose();
    const pill=MP.$('mpPill'); if(pill) pill.classList.add('open');
    MP.updatePill(); MP.restoreHumans(); MP.pushState();
  },

  /* ---------- world sync ---------- */
  pushState(){
    if(!MP.active || !state) return;
    const s=state;
    MP.send({ t:'state', summary:{
      country:s.country.name, flag:s.country.flag,
      approval:s.approval, stability:s.stability, borderTension:s.borderTension,
      treasury:s.treasury, debtToGdp:s.debtToGdp, turn:s.turn,
      name:MP.name, alive:!checkGameOver()
    }});
  },
  applyWorldUpdate(sum){
    if(!sum || !sum.country || sum.country===MP.myCountry) return;
    const snap={
      approval:sum.approval, stability:sum.stability, borderTension:sum.borderTension,
      treasury:sum.treasury, debtToGdp:sum.debtToGdp,
      headline:'👤 '+(sum.name||'שחקן')+' · רבעון '+(sum.turn||1)+(sum.alive===false?' (הודח)':''),
    };
    MP.humanState[sum.country]=snap;
    if(MP.started && typeof worldState!=='undefined' && worldState[sum.country]){
      const w=worldState[sum.country];
      w.prevBorderTension=w.borderTension;
      Object.assign(w,snap);
    }
    if(MP.worldOpen && typeof openWorldView==='function'){ try{ openWorldView(); }catch(_){} }
  },
  restoreHumans(){
    if(typeof worldState==='undefined') return;
    Object.keys(MP.humanState).forEach(c=>{
      if(c===MP.myCountry) return;
      if(worldState[c]) Object.assign(worldState[c], MP.humanState[c]);
    });
  },
  receiveDiplo(m){
    if(!state) return;
    const from=m.fromName||'שחקן', fromCountry=m.fromCountry;
    const rel = fromCountry!=null ? (state.relations[fromCountry]||0) : 0;
    let msg='';
    switch(m.type){
      case 'trade':
        state.treasury=clamp(state.treasury+350,-20000,100000);
        state.approval=clamp(state.approval+2,0,100);
        if(fromCountry!=null) state.relations[fromCountry]=clamp(rel+15,-100,100);
        msg='🤝 '+from+' חתם/ה איתך על הסכם סחר (+קופה, +יחסים)'; break;
      case 'aid':
        state.treasury=clamp(state.treasury+500,-20000,100000);
        state.stability=clamp(state.stability+8,0,100);
        state.approval=clamp(state.approval+4,0,100);
        if(fromCountry!=null) state.relations[fromCountry]=clamp(rel+20,-100,100);
        msg='📦 '+from+' שלח/ה לך סיוע הומניטרי (+קופה, +יציבות)'; break;
      case 'sanction':
        state.treasury=clamp(state.treasury-800,-20000,100000);
        state.approval=clamp(state.approval-6,0,100);
        if(fromCountry===state.neighborName) state.borderTension=clamp(state.borderTension+6,0,100);
        if(fromCountry!=null) state.relations[fromCountry]=clamp(rel-25,-100,100);
        msg='⛔ '+from+' הטיל/ה עליך סנקציות! (-קופה, -אישור)'; break;
      case 'spy':
        state.approval=clamp(state.approval-1,0,100);
        msg='🕵️ זוהתה פעילות ריגול של '+from+' נגד מדינתך'; break;
      default: return;
    }
    if(typeof addLog==='function') addLog('<b>יחסי חוץ:</b> '+msg);
    MP.toast(msg, m.type==='sanction'?'bad':(m.type==='spy'?'':'good'));
    if(typeof render==='function' && !checkGameOver()) render();
    MP.pushState();
  },
};
window.MP = MP;

/* ---------- wrap the original functions (single player untouched) ---------- */
(function(){
  const _selectCountry = window.selectCountry;
  window.selectCountry = function(name){
    if(MP.active){
      const owner=MP.humanCountries[name];
      if(owner && owner!==MP.playerId){ MP.toast('המדינה כבר נתפסה — בחר/י אחרת','bad'); return; }
      MP.myCountry=name;
      MP.send({t:'claim', country:name});
    }
    _selectCountry(name);
    if(MP.active){ MP.onGameStart(); }
  };
  const _makeChoice = window.makeChoice;
  window.makeChoice = function(i){
    _makeChoice(i);
    if(MP.active){ MP.restoreHumans(); MP.pushState(); if(MP.worldOpen){ try{ openWorldView(); }catch(_){} } }
  };
  const _worldAction = window.worldAction;
  window.worldAction = function(name, type){
    _worldAction(name, type);
    if(MP.active){
      const owner=MP.humanCountries[name];
      if(owner && owner!==MP.playerId){ MP.send({t:'diplo', target:owner, type:type}); }
      MP.pushState();
    }
  };
  const _sendSpy = window.sendSpy;
  window.sendSpy = function(name){
    _sendSpy(name);
    if(MP.active){
      const owner=MP.humanCountries[name];
      if(owner && owner!==MP.playerId){ MP.send({t:'diplo', target:owner, type:'spy'}); }
      MP.pushState();
    }
  };
  const _filterCountries = window.filterCountries;
  window.filterCountries = function(){ _filterCountries(); if(MP.active) MP.decorateGrid(); };
  const _openWorldView = window.openWorldView;
  window.openWorldView = function(){ _openWorldView(); MP.worldOpen=true; };
  const _closeWorldView = window.closeWorldView;
  window.closeWorldView = function(){ _closeWorldView(); MP.worldOpen=false; };
})();

/* ---------- saving a campaign ----------
   The game's own "שמור" button builds a download link, which the artifact
   viewer never grants. Route it through the platform's save instead when
   that is available, and fall back to the original everywhere else.
   The original exportSave is not modified. */
(function(){
  const _exportSave = window.exportSave;
  window.exportSave = async function(){
    let downloads=null;
    try{
      downloads = (window.claude && typeof window.claude.use==='function')
        ? await window.claude.use('downloads') : null;
    }catch(_){}
    if(!downloads) return _exportSave();

    try{
      const payload={ state, worldState, savedAt:new Date().toISOString() };
      await downloads.save({
        filename: 'pm-save-'+state.country.name+'-turn'+state.turn+'.json',
        data: JSON.stringify(payload,null,2),
      });
      if(typeof addLog==='function') addLog('<b>שמירה:</b> קובץ הכהונה יוצא בהצלחה.');
      if(typeof render==='function') render();
    }catch(e){
      const code=e && e.code;
      if(code==='declined') MP.toast('השמירה בוטלה','bad');
      else if(code==='rate_limited') MP.toast('נסו לשמור שוב בעוד רגע','bad');
      else MP.toast('השמירה לא זמינה כאן','bad');
    }
  };
})();
