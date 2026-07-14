<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>שרידות</title>
<style>
  html, body { width:100%; height:100%; }
  * { margin:0; padding:0; box-sizing:border-box; -webkit-tap-highlight-color:transparent; user-select:none; -webkit-user-select:none; }
  body {
    background:#0d0f14; font-family:'Courier New', monospace; overflow:hidden;
    display:flex; justify-content:center; align-items:center;
    height:100vh; height:100dvh; color:#e8e0c8; touch-action:none;
  }
  #wrap { position:relative; width:100vw; height:100vh; height:100dvh; max-width:900px; margin:0 auto; }

  #game { display:block; background:#1a2f1a; width:100%; height:100%; touch-action:none; filter: brightness(1); }

  #hudLeft { position:absolute; top:10px; left:10px; display:flex; flex-direction:column; gap:6px; pointer-events:none; z-index:20; transform-origin: top left; }
  .bars { display:flex; flex-direction:column; gap:4px; background:rgba(15,15,20,0.85); padding:8px 10px; border-radius:8px; border:1px solid #4a4230; box-shadow: 0 4px 8px rgba(0,0,0,0.4); }
  .bar-row { display:flex; align-items:center; gap:5px; width:110px; }
  .bar-label { width:14px; text-align:center; font-size:12px; }
  .bar-bg { flex:1; height:9px; background:#222; border:1px solid #555; border-radius:3px; overflow:hidden; }
  .bar-fill { height:100%; transition:width 0.2s; }
  #health .bar-fill { background:#c94a3d; }
  #hunger .bar-fill { background:#d69a3e; }
  #dayinfo { background:rgba(15,15,20,0.85); padding:5px 10px; border-radius:6px; border:1px solid #4a4230; font-size:11px; white-space:nowrap; width: fit-content; box-shadow: 0 4px 8px rgba(0,0,0,0.4); }

  #minimap { position:absolute; top:95px; left:10px; width:85px; height:85px; background:rgba(10,10,10,0.6); border:1px solid #4a4230; border-radius:8px; pointer-events:none; z-index:20; transform-origin: top left; }

  #actionMenu { position:absolute; top:10px; right:10px; display:flex; gap:8px; pointer-events:auto; z-index:20; transform-origin: top right; }
  .menuBtn { width:42px; height:42px; border-radius:8px; background:rgba(15,15,20,0.85); border:1px solid #d9c98a; display:flex; align-items:center; justify-content:center; font-size:20px; cursor:pointer; box-shadow: 0 4px 8px rgba(0,0,0,0.5); transition: transform 0.1s; }
  .menuBtn:active { transform: scale(0.9); }

  #bagPanel, #settingsPanel, #cheatPanel { position:absolute; top:58px; right:10px; background:rgba(15,15,20,0.95); border:1px solid #d9c98a; border-radius:10px; padding:12px; width:220px; display:none; max-height:65vh; overflow-y:auto; pointer-events:auto; z-index:25; box-shadow: 0 6px 16px rgba(0,0,0,0.6); transform-origin: top right; }
  #bagPanel.open { display:block; }
  #bagPanel h3, #settingsPanel h3, #cheatPanel h3 { font-size:12px; margin:6px 0 6px; color:#d9c98a; border-bottom:1px solid #4a4230; padding-bottom:4px; }

  .settingRow { display:flex; flex-direction:column; gap:2px; margin-bottom:14px; padding:6px 0; position:relative; }
  .settingRow label { font-size:10px; color:#b0a888; }

  .settingRow input[type="range"] { width:100%; height:44px; accent-color:#d9c98a; background:transparent; cursor:pointer; padding:10px 0; -webkit-appearance: none; }
  .settingRow input[type="range"]::-webkit-slider-runnable-track { background: #333; height: 6px; border-radius: 3px; }
  .settingRow input[type="range"]::-webkit-slider-thumb { -webkit-appearance: none; height: 20px; width: 20px; border-radius: 50%; background: #d9c98a; margin-top: -7px; }
  
  .settingRow select, .settingRow input[type="number"], .settingRow input[type="text"] { width:100%; background:#222; color:#fff; border:1px solid #4a4230; padding:6px; border-radius:4px; font-family:inherit; font-size:16px; }
  
  .compact-grid { display:grid; grid-template-columns:1fr 1fr; gap:6px; margin-bottom:10px; }
  .compact-grid .settingRow { margin-bottom: 0; padding: 2px 0; }
  .compact-grid label { font-size: 9px; }
  .compact-grid input[type="number"] { font-size: 13px; padding: 4px; }

  .resRow { display:flex; justify-content:space-between; align-items:center; font-size:11px; padding:4px 2px; border-bottom:1px solid rgba(255,255,255,0.05); }
  .weaponRow { display:flex; gap:6px; flex-wrap:wrap; margin-bottom:6px; }
  .weaponIcon { width:36px; height:36px; border-radius:6px; background:#222; border:2px solid #4a4230; display:flex; align-items:center; justify-content:center; font-size:16px; cursor:pointer; }
  .weaponIcon.active { border-color:#d9c98a; background:#3a3222; }
  .craftItem { display:flex; flex-direction:column; font-size:11px; padding:6px 4px; cursor:pointer; border-radius:5px; margin-bottom:2px; background:rgba(255,255,255,0.03); }

  #msg { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); background:rgba(0,0,0,0.95); padding:25px 35px; border-radius:12px; border:2px solid #c94a3d; text-align:center; display:none; z-index:40; pointer-events:auto; box-shadow: 0 0 20px rgba(201,74,61,0.4); }
  #msg button { margin-top:14px; padding:10px 26px; background:#4a6b3a; border:none; color:#fff; border-radius:6px; cursor:pointer; font-family:inherit; font-size:14px; }

  #toast { position:absolute; top:210px; left:50%; transform:translateX(-50%); background:rgba(0,0,0,0.85); border:1px solid #d9c98a; padding:6px 16px; border-radius:6px; font-size:11px; color:#d9c98a; opacity:0; transition:opacity 0.3s; pointer-events:none; white-space:nowrap; z-index:30; }

  #chestPanel { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); background:rgba(15,15,20,0.95); border:2px solid #7a6a3a; border-radius:10px; padding:14px; width:240px; display:none; z-index:35; pointer-events:auto; max-height:82vh; }
  #chestPanel.open { display:flex; flex-direction:column; }
  #chestList { overflow-y:auto; flex:1; min-height:0; }
  #chestClose { position:absolute; top:6px; left:10px; color:#c94a3d; font-size:20px; cursor:pointer; line-height:1; z-index:2; }
  .chestRow { display:flex; justify-content:space-between; align-items:center; font-size:12px; padding:5px 0; border-bottom:1px solid #3a3226; }
  .chestRow button { background:#3a5a2a; border:none; color:#fff; padding:4px 10px; border-radius:4px; font-size:11px; }

  #touchControls { position:absolute; bottom:0; left:0; right:0; height:48%; display:flex; justify-content:space-between; align-items:flex-end; padding:0 24px 24px; pointer-events:none; z-index:15; }
  #joyZone { width:120px; height:120px; border-radius:50%; background:rgba(255,255,255,0.08); border:2px solid rgba(255,255,255,0.25); position:relative; pointer-events:auto; touch-action:none; }
  #joyStick { width:52px; height:52px; border-radius:50%; background:rgba(217,201,138,0.55); border:2px solid rgba(217,201,138,0.8); position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); pointer-events:none; }

  /* quick-place button that appears next to the joystick while building, so you aim with the left thumb and tap to drop blocks fast */
  #placeBtn { position:absolute; left:26px; bottom:150px; width:62px; height:62px; border-radius:50%; background:rgba(47,122,234,0.8); border:3px solid #fff; display:none; align-items:center; justify-content:center; font-size:26px; color:#fff; pointer-events:auto; box-shadow:0 4px 10px rgba(0,0,0,0.45); z-index:17; touch-action:none; }
  #placeBtn.show { display:flex; }
  #placeBtn:active { transform:scale(0.9); }

  #btnHolder { display:flex; flex-direction:column; gap:12px; align-items:center; pointer-events:auto; }
  #interactBtn { width:56px; height:56px; border-radius:50%; background:rgba(217,201,138,0.45); border:2px solid rgba(217,201,138,0.8); display:flex; align-items:center; justify-content:center; font-size:20px; cursor:pointer; color:#fff; box-shadow: 0 4px 8px rgba(0,0,0,0.3); transition: background 0.2s, transform 0.1s; }
  #interactBtn:active { transform: scale(0.9); }
  #actionBtn { width:80px; height:80px; border-radius:50%; background:rgba(201,74,61,0.5); border:3px solid rgba(201,74,61,0.9); display:flex; align-items:center; justify-content:center; font-size:26px; touch-action:none; color:#fff; box-shadow: 0 4px 10px rgba(0,0,0,0.4); }

  #cheatPanel { border-color:#c94a3d; }
  #cheatPanel h3 { border-bottom-color:#c94a3d; color:#e8a898; }
  .cheatBtnRow { display:flex; gap:6px; margin-bottom:8px; }
  .cheatBtnRow button, .fullBtn { flex:1; padding:7px; background:#3a5a2a; color:#fff; border:none; border-radius:5px; font-size:10px; cursor:pointer; }
  .fullBtn { width:100%; margin-bottom:8px; }
  .toggleRow { display:flex; justify-content:space-between; align-items:center; font-size:11px; margin-bottom:10px; }

  /* ---- World-select start screen ---- */
  #worldSelect { position:absolute; inset:0; background:radial-gradient(circle at 50% 30%, #1a2f1a, #0a0d10 80%); display:flex; flex-direction:column; align-items:center; justify-content:center; z-index:60; pointer-events:auto; padding:20px; overflow-y:auto; }
  #worldSelect h1 { color:#d9c98a; font-size:26px; margin-bottom:6px; text-shadow:0 2px 6px #000; }
  #worldSelect .sub { color:#8a8266; font-size:12px; margin-bottom:20px; }
  .worldCard { width:min(88vw, 340px); background:rgba(20,22,28,0.92); border:2px solid #4a4230; border-radius:12px; padding:14px 16px; margin-bottom:12px; cursor:pointer; transition:transform 0.1s, border-color 0.2s; }
  .worldCard:active { transform:scale(0.97); }
  .worldCard:hover { border-color:#d9c98a; }
  .worldCard .wt { font-size:16px; color:#e8e0c8; margin-bottom:4px; }
  .worldCard .wd { font-size:11px; color:#9a927a; line-height:1.5; }
  .worldCard.locked { border-color:#5a3a3a; }
  #wsCodeWrap { display:flex; gap:6px; width:min(88vw,340px); margin-top:4px; }
  #wsCodeWrap input { flex:1; background:#222; color:#fff; border:1px solid #4a4230; padding:8px; border-radius:6px; font-size:16px; font-family:inherit; }
  #wsCodeWrap button { padding:8px 14px; background:#5a4a2a; color:#fff; border:none; border-radius:6px; cursor:pointer; font-family:inherit; }

  /* ---- Morning bonus / lucky choice modal ---- */
  #bonusModal { position:absolute; inset:0; background:rgba(0,0,0,0.72); display:none; flex-direction:column; align-items:center; justify-content:center; z-index:55; pointer-events:auto; padding:16px; }
  #bonusModal.open { display:flex; }
  #bonusModal .bx { position:relative; background:rgba(18,20,26,0.98); border:2px solid #d9c98a; border-radius:14px; padding:18px 16px 16px; width:min(92vw, 380px); box-shadow:0 8px 30px rgba(0,0,0,0.6); }
  #bonusModal h2 { color:#f5c518; font-size:18px; text-align:center; margin-bottom:2px; }
  #bonusModal .bsub { color:#9a927a; font-size:11px; text-align:center; margin-bottom:14px; }
  .bonusChoice { display:flex; align-items:center; gap:10px; background:rgba(255,255,255,0.04); border:1px solid #4a4230; border-radius:10px; padding:12px; margin-bottom:10px; cursor:pointer; transition:transform 0.1s, border-color 0.2s; }
  .bonusChoice:active { transform:scale(0.98); }
  .bonusChoice:hover { border-color:#f5c518; }
  .bonusChoice .bemoji { font-size:26px; width:34px; text-align:center; }
  .bonusChoice .binfo { flex:1; }
  .bonusChoice .bname { font-size:14px; color:#e8e0c8; }
  .bonusChoice .bval { font-size:12px; color:#73c745; font-weight:bold; }
  #bonusLater { width:100%; padding:10px; background:#3a3226; color:#d9c98a; border:1px dashed #6a5a3a; border-radius:8px; cursor:pointer; font-family:inherit; font-size:12px; margin-top:2px; }
  #bonusX { position:absolute; top:8px; left:12px; color:#c94a3d; font-size:22px; cursor:pointer; line-height:1; }

  /* ---- Stats panel ---- */
  #statsPanel { position:absolute; top:58px; right:10px; background:rgba(15,15,20,0.97); border:1px solid #d9c98a; border-radius:10px; padding:12px; width:230px; display:none; max-height:70vh; overflow-y:auto; pointer-events:auto; z-index:26; box-shadow:0 6px 16px rgba(0,0,0,0.6); }
  #statsPanel h3 { font-size:12px; margin:8px 0 6px; color:#d9c98a; border-bottom:1px solid #4a4230; padding-bottom:4px; }
  #statsPanel .statRow { display:flex; justify-content:space-between; font-size:11px; padding:4px 2px; border-bottom:1px solid rgba(255,255,255,0.05); }
  #statsPanel .statRow b { color:#73c745; }
  .noiseToggleRow { display:flex; justify-content:space-between; align-items:center; font-size:11px; margin-bottom:8px; }
</style>
</head>
<body>
<div id="wrap">
  <canvas id="game"></canvas>

  <div id="hudLeft">
    <div class="bars">
      <div class="bar-row" id="health"><span class="bar-label">❤️</span><div class="bar-bg"><div class="bar-fill" style="width:100%"></div></div></div>
      <div class="bar-row" id="hunger"><span class="bar-label">🍖</span><div class="bar-bg"><div class="bar-fill" style="width:100%"></div></div></div>
    </div>
    <div id="dayinfo">יום <span id="dayNum">1</span> | <span id="timeOfDay">☀️ יום</span></div>
  </div>

  <canvas id="minimap" width="90" height="90"></canvas>

  <div id="actionMenu">
    <div class="menuBtn" onclick="toggleBag()">🎒</div>
    <div class="menuBtn" onclick="toggleStats()">📊</div>
    <div class="menuBtn" onclick="toggleSettings()">⚙️</div>
  </div>

  <div id="bagPanel">
    <h3>⚔️ נשק פעיל</h3>
    <div class="weaponRow" id="weaponRow"></div>
    <h3>📦 חומרים</h3>
    <div id="resList"></div>
    <h3>🛠️ קראפטינג</h3>
    <div id="craftList"></div>
  </div>

  <div id="settingsPanel">
    <h3>⚙️ הגדרות משחק</h3>
    <div class="settingRow"><label>☀️ תאורת מסך (למשחק בשמש):</label><input type="range" min="0.8" max="1.8" step="0.1" value="1.0" oninput="changeAppBrightness(this.value)"></div>
    <div class="settingRow"><label>🕹️ סוג רשת תנועה (Grid Mode):</label><select id="gridMode" onchange="changeGridMode(this.value)"><option value="smooth">🏃 תנועה חופשית (Smooth)</option><option value="quarter">📐 רבע בלוק (1/4 Tile)</option><option value="half">📏 חצי בלוק (1/2 Tile)</option><option value="full">🧱 בלוק מלא (Full Tile)</option></select></div>
    <div class="settingRow"><label>🎨 רמת יופי וגרפיקה (1-6):</label><input type="range" min="1" max="6" step="1" value="1" oninput="changeGraphics(this.value)"></div>
    <div class="settingRow" id="noiseSection" style="display:none; border-top:1px dashed #4a4230; padding-top:8px;">
      <label>🎛️ טקסטורה 6 — רעש (סאונד) לבלוקים:</label>
      <div class="noiseToggleRow"><span>הכל</span><input type="checkbox" id="noiseAll" checked onchange="setAllNoise(this.checked)"></div>
      <div id="noiseList"></div>
    </div>
    <div class="settingRow"><label>📱 גודל כללי לממשק (UI Scale):</label><input type="range" min="1.0" max="2.0" step="0.1" value="1.2" oninput="changeUIScale(this.value)"></div>
    <div class="settingRow"><label>🔎 מרחק מצלמה (Zoom):</label><input type="range" min="0.6" max="2.6" step="0.1" value="1.5" oninput="changeZoom(this.value)"></div>
    <div class="settingRow"><label>🕹️ גודל ג'ויסטיק תנועה:</label><input type="range" min="80" max="260" step="5" value="120" oninput="changeJoySize(this.value)"></div>
    <div class="settingRow"><label>🔴 גודל לחצן תקיפה (⚔️):</label><input type="range" min="65" max="180" step="5" value="80" oninput="changeActionSize(this.value)"></div>
    <button onclick="toggleSettings()" style="width:100%; padding:8px; background:#4a3a2a; color:#fff; border:none; border-radius:6px; margin-top:6px; font-family:inherit; cursor:pointer;">סגור הגדרות</button>

    <div class="settingRow" style="margin-top:10px; border-top:1px dashed #4a4230; padding-top:10px;">
      <label>🔑 קוד מפתח</label>
      <div style="display:flex; gap:6px;"><input type="text" id="cheatCodeInput" inputmode="numeric" style="flex:1;"><button onclick="tryCheatCode()" style="padding:6px 12px; background:#5a3a3a; color:#fff; border:none; border-radius:4px; cursor:pointer;">פתח</button></div>
    </div>
  </div>

  <div id="cheatPanel">
    <h3>🔑 תפריט מפתח (OP Controls)</h3>
    <div class="toggleRow"><span>👾 מפלצות פעילות</span><input type="checkbox" id="cheatEnemiesToggle" checked onchange="cheatToggleEnemies(this.checked)"></div>
    <div class="toggleRow"><span>🛡️ מצב אלוהים (חסין)</span><input type="checkbox" id="cheatGodToggle" onchange="cheatToggleGod(this.checked)"></div>
    <div class="toggleRow"><span>🌙 כל לילה: לאקי בלוק + כל הכוחות</span><input type="checkbox" id="cheatNightlyToggle" onchange="cheatToggleNightly(this.checked)"></div>

    <h4 style="font-size:11px; margin:10px 0 6px; color:#d9c98a;">⏱️ מנוע בלוקים רנדומליים</h4>
    <div class="settingRow"><label>מרווח זמן לחיפוש (בשניות, 0=כבוי):</label><input type="number" value="1" min="0" step="0.1" onchange="opSetTickDelay(this.value)"></div>
    <div class="settingRow"><label>כמות בלוקים לבדיקה בכל פעימה:</label><input type="number" value="1" min="1" max="5000" step="1" onchange="opSetBlocksPerTick(this.value)"></div>

    <h4 style="font-size:11px; margin:10px 0 6px; color:#d9c98a;">🎲 הגדרות מקסימום ואחוזים</h4>
    <div class="compact-grid">
      <div class="settingRow"><label>🌲 סיכוי עץ (%)</label><input type="number" step="0.1" value="5" onchange="opTreeChance=parseFloat(this.value)"></div>
      <div class="settingRow"><label>מקס' עצים בעולם</label><input type="number" value="300" onchange="opMaxTree=parseInt(this.value)"></div>

      <div class="settingRow"><label>🪨 סיכוי אבן (%)</label><input type="number" step="0.1" value="2.5" onchange="opStoneChance=parseFloat(this.value)"></div>
      <div class="settingRow"><label>מקס' אבנים</label><input type="number" value="150" onchange="opMaxStone=parseInt(this.value)"></div>

      <div class="settingRow"><label>⚫ סיכוי פחם (%)</label><input type="number" step="0.1" value="1.3" onchange="opCoalChance=parseFloat(this.value)"></div>
      <div class="settingRow"><label>מקס' פחם</label><input type="number" value="100" onchange="opMaxCoal=parseInt(this.value)"></div>

      <div class="settingRow"><label>🔶 סיכוי ברזל (%)</label><input type="number" step="0.1" value="0.7" onchange="opIronChance=parseFloat(this.value)"></div>
      <div class="settingRow"><label>מקס' ברזל</label><input type="number" value="60" onchange="opMaxIron=parseInt(this.value)"></div>

      <div class="settingRow"><label>🍓 סיכוי שיח/חיטה (%)</label><input type="number" step="0.1" value="1" onchange="opBushChance=parseFloat(this.value)"></div>
      <div class="settingRow"><label>מקס' שיחים</label><input type="number" value="60" onchange="opMaxBush=parseInt(this.value)"></div>
      
      <div class="settingRow"><label>🐇 סיכוי חיה (%)</label><input type="number" step="0.1" value="0.5" onchange="opAnimalChance=parseFloat(this.value)"></div>
      <div class="settingRow"><label>מקס' חיות</label><input type="number" value="25" onchange="opMaxAnimal=parseInt(this.value)"></div>

      <div class="settingRow"><label>🌾 זמן גדילת יבול (שניות)</label><input type="number" value="240" min="5" onchange="opCropGrowSeconds=parseFloat(this.value)"></div>
      <div class="settingRow"><label>💀 סיכוי גולגולת (%)</label><input type="number" step="0.01" value="0.5" onchange="opSkullChance=parseFloat(this.value)"></div>
    </div>

    <div class="settingRow" style="margin-top:10px;"><label>❤️ קביעת חיים (עד מיליון!)</label><div style="display:flex; gap:6px;"><input type="number" id="cheatHpInput" value="100" min="0" style="flex:1;"><button onclick="cheatSetHealth()" style="padding:6px 10px; background:#3a5a2a; color:#fff; border:none; border-radius:4px;">קבע</button></div></div>
    <div class="settingRow"><label>📦 תן חומרים</label><select id="cheatResSelect"><option value="wood">🪵 עץ</option><option value="stone">🪨 אבן</option><option value="coal">⚫ פחם</option><option value="iron">🔶 ברזל</option><option value="iron_ingot">⚪ ברזל מחומם</option><option value="berry">🍓 פרי</option><option value="meat">🍖 בשר</option><option value="torch">🔥 לפיד</option><option value="bones">🦴 עצם</option><option value="wheat">🌾 חיטה</option><option value="seeds">🌱 זרעים</option></select><div style="display:flex; gap:6px; margin-top:6px;"><input type="number" id="cheatResAmount" value="10" min="1" max="999" style="flex:1;"><button onclick="cheatGiveRes()" style="padding:6px 10px; background:#3a5a2a; color:#fff; border:none; border-radius:4px;">תן</button></div></div>

    <div class="settingRow"><label>🌑 עוצמת חושך בלילה: <span id="cheatDarkVal">20%</span></label><input type="range" min="0" max="90" step="5" value="20" oninput="cheatSetDarkness(this.value)"></div>
    <div class="settingRow"><label>🔦 מרחק ראייה עם לפיד: <span id="cheatLightVal">145</span></label><input type="range" min="60" max="400" step="10" value="145" oninput="cheatSetLightRadius(this.value)"></div>
    <div class="settingRow"><label>⏱️ אורך יום/לילה (שניות): <span id="cheatCycleVal">180</span></label><input type="range" min="60" max="600" step="10" value="180" oninput="cheatSetCycleLength(this.value)"></div>
    <div class="settingRow"><label>🧱 קשיחות קיר (מכות עד שבירה): <span id="cheatWallVal">10</span></label><input type="range" min="1" max="300" step="1" value="10" oninput="opWallToughnessHits=parseInt(this.value); document.getElementById('cheatWallVal').textContent=this.value;"></div>
    <div class="cheatBtnRow"><button onclick="cheatSetTimeOfDay('day')">☀️ עשה יום</button><button onclick="cheatSetTimeOfDay('night')">🌙 עשה לילה</button></div>
    <button class="fullBtn" style="background:#4a3a2a;" onclick="toggleCheatPanel()">סגור תפריט מפתח</button>
  </div>

  <div id="toast"></div>

  <div id="chestPanel">
    <span id="chestClose" onclick="closeChest()">✕</span>
    <h3>📦 תיבת אחסון</h3>
    <div id="chestList"></div>
    <button style="width:100%; padding:8px; background:#4a3a2a; color:#fff; border:none; border-radius:6px; margin-top:8px; flex-shrink:0;" onclick="closeChest()">סגור</button>
  </div>

  <div id="touchControls">
    <div id="joyZone"><div id="joyStick"></div></div>
    <div id="placeBtn">📍</div>
    <div id="btnHolder"><div id="interactBtn" onclick="tryInteract()">🖐️</div><div id="actionBtn">⚔️</div></div>
  </div>

  <div id="msg"><h2 id="msgTitle" style="color:#c94a3d; margin-bottom:10px;">מתת!</h2><p id="msgBody">שרדת <span id="survivedDays">0</span> ימים</p><button onclick="restart()">התחל מחדש</button></div>

  <div id="bonusModal">
    <div class="bx">
      <span id="bonusX" onclick="bonusDefer()">✕</span>
      <h2 id="bonusTitle">🌅 בוקר טוב! בחר בונוס</h2>
      <div class="bsub" id="bonusSub">בחר אחד מהשלושה — או קח לאקי בלוק לאחר כך</div>
      <div id="bonusChoices"></div>
      <button id="bonusLater" onclick="bonusDefer()">📦 אחר כך (קבל לאקי בלוק לתיק)</button>
    </div>
  </div>

  <div id="statsPanel">
    <h3>📊 סטטיסטיקות</h3>
    <div id="statsBody"></div>
    <h3>🏆 שדרוגים שבחרת</h3>
    <div id="statsChoices"></div>
    <button style="width:100%; padding:8px; background:#4a3a2a; color:#fff; border:none; border-radius:6px; margin-top:8px;" onclick="toggleStats()">סגור</button>
  </div>

  <div id="worldSelect">
    <h1>🌍 שרידות</h1>
    <div class="sub">בחר עולם כדי להתחיל</div>
    <div class="worldCard" onclick="startWorld('crystal')">
      <div class="wt">💎 עולם הקריסטל</div>
      <div class="wd">המשחק הרגיל. מצא ובנה את הקריסטל לפני היום החמישי כדי לעצור את הלילה הנצחי.</div>
    </div>
    <div class="worldCard" onclick="startWorld('eternal')">
      <div class="wt">🌑 עולם ללא קריסטל</div>
      <div class="wd">אין קריסטל — לילה נצחי מההתחלה. המטרה: לשרוד כמה שיותר זמן. מסוכן מאוד!</div>
    </div>
    <div class="worldCard locked" onclick="askWorldCode()">
      <div class="wt">🔒 עולם ניסיון (דורש קוד)</div>
      <div class="wd">עולם בדיקה עם כל הבלוקים והחומרים מוכנים, כדי לבדוק באגים במהירות. הזן קוד סודי.</div>
    </div>
    <div id="wsCodeWrap" style="display:none;">
      <input type="text" id="wsCodeInput" inputmode="numeric" placeholder="קוד סודי">
      <button onclick="submitWorldCode()">פתח</button>
    </div>
  </div>
</div>

<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
let W, H;
function resizeCanvas(){
  const rect = document.getElementById('wrap').getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  canvas.width = Math.round(rect.width * dpr);
  canvas.height = Math.round(rect.height * dpr);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  W = rect.width;
  H = rect.height;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

const TILE = 32;
const MAPW = 80, MAPH = 60;
let gameZoom = 1.5;
let gfxLevel = 1;
let motionGrid = 'smooth';

const lightCanvas = document.createElement('canvas');
const lightCtx = lightCanvas.getContext('2d');

/* ============ Cheat / dev menu & OP Configs ============ */
const CHEAT_CODE = '1256';
let cheatNoEnemies = false;
let cheatGodMode = false;
let nightDarkness = 0.20;
let torchLightRadius = 145;
const BASE_TORCHLESS_RADIUS = 45;

let CYCLE_LEN = 180;
let DUSK_LEN = 10;
let DAWN_LEN = 10;
let NIGHT_CORE_RATIO = 0.28;

let opTickDelay = 1.0;     
let opBlocksPerTick = 1;   

let opTreeChance = 5, opStoneChance = 2.5, opCoalChance = 1.3, opIronChance = 0.7, opBushChance = 1.0, opAnimalChance = 0.5;
let opMaxTree = 300, opMaxStone = 150, opMaxCoal = 100, opMaxIron = 60, opMaxBush = 60, opMaxAnimal = 25;
let opCropGrowSeconds = 240, opSkullChance = 0.5;
let tickAcc = 0;           
let currentCounts = { tree:0, stone:0, coal:0, iron:0, bush:0, animal:0 };

/* ============ Crystal device / day-5 eternal night ============ */
let crystalPlaced = false, crystalActivated = false, crystalDevicePos = null;
let eternalNightActive = false, forcedDayUntil = 0;
let opWallToughnessHits = 10; // how many ~1s "chew ticks" it takes an enemy to break a plain wall
let crystalBonusDays = 0;
let enemyProjectiles = [];

function clearMobileZoomReset() {
  if (document.activeElement && document.activeElement.tagName === 'INPUT') document.activeElement.blur();
  setTimeout(() => { window.scrollTo(0, 0); }, 50);
}
function tryCheatCode(){
  const val = document.getElementById('cheatCodeInput').value.trim();
  if (val === CHEAT_CODE){
    document.getElementById('cheatCodeInput').value='';
    document.getElementById('settingsPanel').style.display='none';
    document.getElementById('cheatPanel').style.display='block';
    showToast('תפריט מפתח נפתח 🔑');
  } else if (val === '2020'){
    document.getElementById('cheatCodeInput').value='';
    const d = prompt('כמה ימים עד הלילה הנצחי? (נוכחי: '+eternalNightDay+')', String(eternalNightDay));
    const parsed = parseInt(d);
    if (!isNaN(parsed) && parsed >= 1){ eternalNightDay = parsed; showToast('🔑 כמות הימים עודכנה ל-'+parsed); }
  } else { showToast('קוד שגוי'); }
  clearMobileZoomReset();
}
function toggleCheatPanel(){
  const p = document.getElementById('cheatPanel');
  p.style.display = p.style.display === 'block' ? 'none' : 'block';
  clearMobileZoomReset();
}
function opSetTickDelay(val) { opTickDelay = parseFloat(val); if (opTickDelay < 0) opTickDelay = 0; }
function opSetBlocksPerTick(val) { opBlocksPerTick = parseInt(val); if (opBlocksPerTick < 1) opBlocksPerTick = 1; }
function cheatToggleEnemies(checked){ cheatNoEnemies = !checked; if (cheatNoEnemies) enemies = []; showToast(checked ? 'מפלצות הופעלו' : 'מפלצות כובו'); }
function cheatToggleGod(checked){ cheatGodMode = checked; showToast(checked ? 'מצב אלוהים פעיל' : 'מצב אלוהים כבוי'); }
function cheatToggleNightly(checked){ adminNightlyAll = checked; showToast(checked ? '🌙 כל לילה תקבל לאקי בלוק + כל הכוחות' : 'מצב לילה-הכל כבוי'); }
function cheatSetHealth(){ const v = parseFloat(document.getElementById('cheatHpInput').value); if (!isNaN(v)){ player.maxHealth = Math.max(100, v); player.health = v; showToast('חיים נקבעו ל-'+v); } clearMobileZoomReset(); }
function cheatGiveRes(){ const k = document.getElementById('cheatResSelect').value; const amt = parseInt(document.getElementById('cheatResAmount').value) || 0; player.inv[k] = (player.inv[k]||0) + amt; showToast('קיבלת '+amt+' '+(names[k]||k)); renderBag(); clearMobileZoomReset(); }
function cheatSetDarkness(val){ nightDarkness = parseInt(val)/100; document.getElementById('cheatDarkVal').textContent = val+'%'; }
function cheatSetLightRadius(val){ torchLightRadius = parseInt(val); document.getElementById('cheatLightVal').textContent = val; }
function cheatSetCycleLength(val){ CYCLE_LEN = parseInt(val); DUSK_LEN = Math.max(5, CYCLE_LEN*0.08); DAWN_LEN = DUSK_LEN; document.getElementById('cheatCycleVal').textContent = val; showToast('אורך מחזור יום/לילה: '+val+' שניות'); }
function cheatSetTimeOfDay(which){ const nightCore = CYCLE_LEN * NIGHT_CORE_RATIO; const dayLen = CYCLE_LEN - nightCore - DUSK_LEN - DAWN_LEN; if (which==='day'){ time = dayLen*0.5; showToast('הפכת ליום'); } else { time = dayLen + DUSK_LEN + nightCore*0.5; showToast('הפכת ללילה'); } }
function toggleSettings(){ const p = document.getElementById('settingsPanel'); p.style.display = p.style.display === 'block' ? 'none' : 'block'; if(p.style.display === 'block'){ document.getElementById('bagPanel').classList.remove('open'); document.getElementById('cheatPanel').style.display='none'; document.getElementById('statsPanel').style.display='none'; } clearMobileZoomReset(); }
function changeZoom(val) { gameZoom = parseFloat(val); }
function changeGraphics(val) {
  gfxLevel = parseInt(val);
  const ns = document.getElementById('noiseSection');
  if (ns){ ns.style.display = gfxLevel >= 6 ? 'flex' : 'none'; if (gfxLevel >= 6) renderNoiseList(); }
  showToast(gfxLevel>=6 ? 'טקסטורה 6 פעילה — אפשר לכוון רעש לכל בלוק' : ('איכות גרפיקה שונתה לרמה ' + val));
}
const NOISE_LABELS = { wall:'🧱 קיר אפור', bone_wall:'🦴 קיר עצמות', temple:'🏛️ רצפת המקדש', floor_grass:'🌿 רצפת דשא', floor_sand:'🏜️ רצפת מדבר', floor_snow:'❄️ רצפת שלג' };
function renderNoiseList(){
  const list = document.getElementById('noiseList'); if (!list) return;
  list.innerHTML = Object.keys(NOISE_LABELS).map(k=>`<div class="noiseToggleRow"><span>${NOISE_LABELS[k]}</span><input type="checkbox" ${blockNoise[k]?'checked':''} onchange="toggleBlockNoise('${k}', this.checked)"></div>`).join('');
  const all = Object.keys(NOISE_LABELS).every(k=>blockNoise[k]);
  const allBox = document.getElementById('noiseAll'); if (allBox) allBox.checked = all;
}
function toggleBlockNoise(k, on){ blockNoise[k] = on; }
function setAllNoise(on){ for (const k in NOISE_LABELS) blockNoise[k] = on; renderNoiseList(); }
function changeGridMode(val) { motionGrid = val; showToast('רשת תנועה שונתה!'); player.moving = false; }
function changeAppBrightness(val) { document.getElementById('game').style.filter = `brightness(${val})`; }
function changeJoySize(val) { const zone = document.getElementById('joyZone'); zone.style.width = val + 'px'; zone.style.height = val + 'px'; JOY_R = parseInt(val) * 0.4; }
function changeActionSize(val) { const btn = document.getElementById('actionBtn'); btn.style.width = val + 'px'; btn.style.height = val + 'px'; btn.style.fontSize = (parseInt(val) * 0.33) + 'px'; const ibtn = document.getElementById('interactBtn'); ibtn.style.width = (parseInt(val) * 0.7) + 'px'; ibtn.style.height = (parseInt(val) * 0.7) + 'px'; ibtn.style.fontSize = (parseInt(val) * 0.25) + 'px'; }
function changeUIScale(val) { document.getElementById('hudLeft').style.transform = `scale(${val})`; document.getElementById('minimap').style.transform = `scale(${val})`; document.getElementById('actionMenu').style.transform = `scale(${val})`; document.getElementById('bagPanel').style.transform = `scale(${val})`; document.getElementById('settingsPanel').style.transform = `scale(${val})`; document.getElementById('statsPanel').style.transform = `scale(${val})`; }

let actx = null;
function ensureAudio(){ if (!actx){ try{ actx = new (window.AudioContext||window.webkitAudioContext)(); }catch(e){} } }
function beep(freq, dur, type, vol){ if (!actx) return; const o = actx.createOscillator(); const g = actx.createGain(); o.type = type||'square'; o.frequency.value = freq; g.gain.value = vol||0.06; o.connect(g); g.connect(actx.destination); o.start(); g.gain.exponentialRampToValueAtTime(0.0001, actx.currentTime + (dur||0.1)); o.stop(actx.currentTime + (dur||0.1)+0.02); }
function sfxHit(){ beep(180,0.08,'square',0.08); }
function sfxGather(){ beep(320,0.06,'triangle',0.06); }
function sfxHurt(){ beep(90,0.15,'sawtooth',0.09); }
function sfxShoot(){ beep(500,0.05,'square',0.05); }

let keys = {};
window.addEventListener('keydown', e => { keys[e.key.toLowerCase()] = true; ensureAudio(); }); window.addEventListener('keyup', e => { keys[e.key.toLowerCase()] = false; });
let joyActive=false, joyDX=0, joyDY=0, joyTouchId=null; const joyZone = document.getElementById('joyZone'); const joyStick = document.getElementById('joyStick'); let JOY_R = 48;
function joyStart(e){ ensureAudio(); const t = e.changedTouches?e.changedTouches[0]:e; joyTouchId = e.changedTouches?t.identifier:'mouse'; joyActive=true; joyMove(e); }
function joyMove(e){ if(!joyActive) return; let t; if (e.changedTouches){ t = Array.from(e.changedTouches).find(tt=>tt.identifier===joyTouchId); if(!t) return; } else t = e; const rect = joyZone.getBoundingClientRect(); const cx = rect.left+rect.width/2, cy = rect.top+rect.height/2; let dx = t.clientX-cx, dy = t.clientY-cy; const dist = Math.hypot(dx,dy); if (dist > JOY_R){ dx = dx/dist*JOY_R; dy = dy/dist*JOY_R; } joyStick.style.transform = `translate(calc(-50% + ${dx}px), calc(-50% + ${dy}px))`; joyDX = dx/JOY_R; joyDY = dy/JOY_R; }
function joyEnd(){ joyActive=false; joyDX=0; joyDY=0; joyTouchId=null; joyStick.style.transform='translate(-50%,-50%)'; }
joyZone.addEventListener('touchstart', e=>{e.preventDefault(); joyStart(e);}, {passive:false}); joyZone.addEventListener('touchmove', e=>{e.preventDefault(); joyMove(e);}, {passive:false}); joyZone.addEventListener('touchend', e=>{e.preventDefault(); joyEnd();}, {passive:false}); joyZone.addEventListener('touchcancel', e=>{e.preventDefault(); joyEnd();}, {passive:false});
let actionHeld = false; const actionBtn = document.getElementById('actionBtn'); actionBtn.addEventListener('touchstart', e=>{e.preventDefault(); ensureAudio(); actionHeld=true;}, {passive:false}); actionBtn.addEventListener('touchend', e=>{e.preventDefault(); actionHeld=false;}, {passive:false});
// Quick-place button: aim with the joystick (frontPos already follows it) and tap here to drop a block instantly.
const placeBtnEl = document.getElementById('placeBtn');
placeBtnEl.addEventListener('touchstart', e=>{ e.preventDefault(); ensureAudio(); tryInteract(); }, {passive:false});
placeBtnEl.addEventListener('click', e=>{ e.preventDefault(); if (player.placingItem) tryInteract(); });
function toggleBag(){ 
    const p = document.getElementById('bagPanel'); 
    p.classList.toggle('open'); 
    if(p.classList.contains('open')){
        document.getElementById('settingsPanel').style.display = 'none';
        document.getElementById('cheatPanel').style.display='none';
        document.getElementById('statsPanel').style.display='none';
        player.placingItem = null; // ביטול הנחת חפץ כשפותחים תיק שוב
        renderBag(); 
    } 
}

const T = { GRASS:0, TREE:1, ROCK:2, COAL:3, IRONROCK:4, WATER:5, BUSH:6, SAND:7, CACTUS:8, SNOW:9, PINE:10, WALL:11, CAMPFIRE:12, TRUNK:13, CRAFTING_TABLE:14, SAPLING:15, SKULL:16, UPGRADED_TABLE:17, FURNACE:18, WHEAT:19, CROP:20, ALTAR_FLOOR:21, TABLET:22, CRYSTAL_ORE:23, CRYSTAL_DEVICE:24, PLACED_TORCH:25, WALL_THORN:26, BONE_WALL:27, LUCKY:28 };
const BIOME = { FOREST:'forest', SNOW:'snow', DESERT:'desert', PLAINS:'plains' };
function biomeAt(x,y){ const nx = x/MAPW, ny = y/MAPH; if (ny < 0.45 && nx < 0.5) return BIOME.FOREST; if (ny < 0.45 && nx >= 0.5) return BIOME.SNOW; if (ny >= 0.45 && nx < 0.5) return BIOME.DESERT; return BIOME.PLAINS; }

let world;
function tileHP(t){
  if (t===T.TREE||t===T.PINE) return 3; if (t===T.ROCK||t===T.COAL) return 4; if (t===T.IRONROCK) return 6;
  if (t===T.BUSH||t===T.SKULL||t===T.WHEAT) return 1; if (t===T.CACTUS) return 2; if (t===T.WALL) return 15; if (t===T.CAMPFIRE) return 5; 
  if (t===T.TRUNK) return 2; if (t===T.CRAFTING_TABLE) return 4; if (t===T.SAPLING) return 1; if(t===T.UPGRADED_TABLE) return 6; if(t===T.FURNACE) return 8; if(t===T.CROP) return 1;
  if (t===T.TABLET) return 999999; if (t===T.CRYSTAL_ORE) return 10; if (t===T.CRYSTAL_DEVICE) return 40; if (t===T.PLACED_TORCH) return 3; if (t===T.WALL_THORN) return 20; if (t===T.BONE_WALL) return 22; if (t===T.LUCKY) return 2; return 0;
}
function genWorld(){
  world = []; const riverX = Math.floor(MAPW*0.5);
  for(let y=0;y<MAPH;y++){
    world[y] = [];
    for(let x=0;x<MAPW;x++){
      const edge = x<2||y<2||x>MAPW-3||y>MAPH-3; const nearRiver = Math.abs(x - (riverX + Math.sin(y*0.15)*4)) < 1.6;
      const lakeDX = x-(MAPW*0.72), lakeDY = y-(MAPH*0.78); const inLake = Math.sqrt(lakeDX*lakeDX+lakeDY*lakeDY) < 6;
      if (edge || nearRiver || inLake){ world[y][x] = {type:T.WATER, hp:0}; continue; }
      const b = biomeAt(x,y); const n = Math.random(); let tile = T.GRASS;
      if (b===BIOME.FOREST){ if (n<0.14) tile=T.TREE; else if (n<0.18) tile=T.COAL; else if (n<0.21) tile=T.ROCK; else if (n<0.23) tile=T.IRONROCK; else if (n<0.26) tile=T.BUSH; else if (n<0.29) tile=T.WHEAT; }
      else if (b===BIOME.SNOW){ tile = T.SNOW; if (n<0.12) tile=T.PINE; else if (n<0.155) tile=T.IRONROCK; else if (n<0.18) tile=T.ROCK; }
      else if (b===BIOME.DESERT){ tile = T.SAND; if (n<0.005) tile=T.SKULL; else if (n<0.09) tile=T.CACTUS; else if (n<0.13) tile=T.ROCK; else if (n<0.15) tile=T.IRONROCK; }
      else { if (n<0.06) tile=T.TREE; else if (n<0.09) tile=T.ROCK; else if (n<0.12) tile=T.BUSH; else if (n<0.15) tile=T.WHEAT; }
      world[y][x] = { type: tile, hp: tileHP(tile), timer: 0 };
    }
  }

  // Central altar: a 4-tile-radius circle of grey stone floor with a tablet in the exact center.
  const acx = Math.floor(MAPW/2), acy = Math.floor(MAPH/2);
  for (let y=acy-4; y<=acy+4; y++){
    for (let x=acx-4; x<=acx+4; x++){
      if (y<0||y>=MAPH||x<0||x>=MAPW) continue;
      if (Math.hypot(x-acx, y-acy) <= 4.2){ world[y][x] = { type:T.ALTAR_FLOOR, hp:0, timer:0 }; }
    }
  }
  world[acy][acx] = { type:T.TABLET, hp:tileHP(T.TABLET), timer:0 };

  // The one and only crystal ore in the world - somewhere away from the altar.
  let placedCrystalOre = false, tries=0;
  while(!placedCrystalOre && tries<400){
    tries++;
    const rx = 4+Math.floor(Math.random()*(MAPW-8)), ry = 4+Math.floor(Math.random()*(MAPH-8));
    if (Math.hypot(rx-acx, ry-acy) < 10) continue;
    const t = world[ry][rx];
    if (t.type===T.GRASS||t.type===T.SAND||t.type===T.SNOW){
      world[ry][rx] = { type:T.CRYSTAL_ORE, hp:tileHP(T.CRYSTAL_ORE), maxHp:tileHP(T.CRYSTAL_ORE), timer:0 };
      placedCrystalOre = true;
    }
  }
}

function groundColor(b, tileType){ if (tileType===T.WATER) return '#2a5a8a'; if (tileType===T.ALTAR_FLOOR) return '#8a8a8a'; if (b===BIOME.DESERT) return '#d8c27a'; if (b===BIOME.SNOW) return '#e8eef2'; return '#3a7d34'; }
function tileAt(px,py){ const tx=Math.floor(px/TILE), ty=Math.floor(py/TILE); if (ty<0||ty>=MAPH||tx<0||tx>=MAPW) return {type:T.WATER, hp:0}; return world[ty][tx]; }
function isSolid(t){ return [T.TREE, T.ROCK, T.COAL, T.IRONROCK, T.CACTUS, T.PINE, T.WALL, T.WALL_THORN, T.BONE_WALL, T.LUCKY, T.TRUNK, T.CRAFTING_TABLE, T.SAPLING, T.SKULL, T.UPGRADED_TABLE, T.FURNACE, T.TABLET, T.CRYSTAL_ORE, T.CRYSTAL_DEVICE].includes(t.type); }
function isWater(t){ return t.type===T.WATER; }

let enemies, animals, particles, projectiles, placedTorches, chests, cropTiles;
let player, camX, camY, time, dayNum, gameOver, countTimer=0;
let gameMode = 'crystal';      // 'crystal' | 'eternal' | 'test'
let gameStarted = false;       // stays false until a world is picked
let bonusModalOpen = false;    // pauses the world while the morning-bonus modal is up
let eternalNightDay = 5;       // day the eternal night begins (editable via secret code 2020)
let stats = { animalsKilled:0, monstersKilled:0, blocksDestroyed:0, maxBreakDist:2, luckyOpened:0, dailyChoices:[] };
let bonusShownForDay = 0;      // guards against re-triggering the morning bonus in the same day
let luckyQueue = [];           // pending saved choice-sets, attached to lucky blocks in order they're placed
let adminNightlyAll = false;   // admin toggle: every night auto-grant a lucky block + every bonus power
function resetStats(){ stats = { animalsKilled:0, monstersKilled:0, blocksDestroyed:0, maxBreakDist:2, luckyOpened:0, dailyChoices:[] }; }
function initEntities(){ enemies=[]; animals=[]; particles=[]; projectiles=[]; placedTorches=[]; chests=[]; cropTiles=[]; enemyProjectiles=[]; }
function initPlayer(){
  const gx = Math.floor(MAPW/2), gy = Math.floor(MAPH*0.42);
  player = { 
    gridX:gx, gridY:gy, x:gx*TILE+TILE/2, y:gy*TILE+TILE/2, w:18,h:18, moving:false, moveFrom:{x:0,y:0}, moveTo:{x:0,y:0}, moveT:0, moveDuration:0.24, health:100, maxHealth:100, hunger:100, maxHunger:100, speed:2.5, facing:'down', 
    inv:{ wood:0, stone:0, coal:0, iron:0, iron_ingot:0, berry:0, meat:0, torch:0, bones:0, wheat:0, seeds:0, bowl:0, dough:0, bread:0, cooked_meat:0, fruit_salad:0, crystal:0, reinforcement:0,
          item_wall:0, item_wall_thorn:0, item_bone_wall:0, item_campfire:0, item_furnace:0, item_crafting_table:0, item_upgraded_table:0, item_chest:0, item_crystal_device:0, item_lucky:0 },
    equipment:{}, activeWeapon:'sword', attackCd:0, stepSfxCd:0, nearFire:0, walkFrame:0, isWalking:false, hurtSfxCd:0,
    placingItem: null, speedBoostTimer: 0, efficiencyBoostTimer: 0,
    gatherBonus: 0, breakReach: 2, speedBonus: 0   // permanent bonuses from morning choices
  };
}
function initGame(){
  genWorld(); initEntities(); initPlayer(); resetStats();
  time = 0; dayNum = 1; gameOver=false; tickAcc=0; countTimer=0;
  bonusShownForDay = 0; luckyQueue = [];
  // reset run-scoped crystal / eternal-night state (important on restart)
  crystalPlaced=false; crystalActivated=false; crystalDevicePos=null; crystalBonusDays=0;
  eternalNightActive=false; forcedDayUntil=0; enemyProjectiles=[];
  if (gameMode==='eternal'){ eternalNightActive = true; }        // no crystal, night from the start
  else if (gameMode==='test'){ setupTestWorld(); }
  camX = player.x; camY = player.y; updateHUD(); renderBag(); changeUIScale(1.2); updateResourceCounts();
}
// Test/sandbox world: hands you every tool, block and material so glitches can be reproduced fast.
function setupTestWorld(){
  player.equipment = { axe:1, pickaxe:1, sword:1, bow:1, iron_axe:1, iron_pickaxe:1, iron_sword:1, shovel:1 };
  player.activeWeapon = 'iron_sword';
  const give = { wood:200, stone:200, coal:200, iron:200, iron_ingot:200, berry:50, meat:50, torch:50, bones:200, wheat:50, seeds:50, bowl:20, dough:20, bread:20, cooked_meat:20, fruit_salad:20, crystal:5, reinforcement:30, arrowWood:99, arrowIron:99,
    item_wall:50, item_wall_thorn:50, item_bone_wall:50, item_campfire:20, item_furnace:20, item_crafting_table:20, item_upgraded_table:20, item_chest:20, item_crystal_device:5, item_lucky:20 };
  for (const k in give) player.inv[k] = give[k];
  // drop one of each work-station near spawn so every craft menu is reachable immediately
  const gx = player.gridX, gy = player.gridY;
  const samples = [[T.CRAFTING_TABLE,2,0],[T.UPGRADED_TABLE,3,0],[T.FURNACE,4,0],[T.CAMPFIRE,2,2]];
  for (const [tt,ox,oy] of samples){ const cx=gx+ox, cy=gy+oy; if (world[cy] && world[cy][cx] && !isWater(world[cy][cx])){ const hp=tileHP(tt); world[cy][cx]={type:tt,hp,maxHp:hp,timer:0}; } }
}

const RECIPES = [ 
  { id:'crafting_table', name:'🛠️ שולחן עבודה', cost:{wood:2}, type:'building', station:'none' }, 
  { id:'torch', name:'🔥 לפיד בתיק', cost:{wood:1, coal:1}, type:'ammo', give:{torch:1}, station:'none' }, 
  { id:'plant_seeds', name:'🌱 שתול זרעים', cost:{seeds:1}, type:'plant', station:'none' },
  
  { id:'axe', name:'🪓 גרזן אבן', cost:{wood:3}, type:'tool', station:'table' }, 
  { id:'pickaxe', name:'⛏️ מכוש אבן', cost:{wood:2, stone:2}, type:'tool', station:'table' }, 
  { id:'sword', name:'🗡️ חרב אבן', cost:{wood:1, coal:2}, type:'tool', station:'table' }, 
  { id:'bow', name:'🏹 קשת', cost:{wood:3, coal:1}, type:'tool', station:'table' }, 
  { id:'arrowWood', name:'➶ 5 חצי אבן', cost:{wood:1, stone:1}, type:'ammo', give:{arrowWood:5}, station:'table' }, 
  { id:'upgraded_table', name:'⚙️ שולחן משודרג', cost:{wood:4, stone:4, coal:2}, type:'building', station:'table' },
  { id:'campfire', name:'🏕️ מדורה', cost:{wood:4, stone:2}, type:'building', station:'table' }, 
  { id:'chest', name:'📦 תיבת אחסון', cost:{wood:4, stone:2}, type:'chest', station:'table' },
  { id:'wall', name:'🧱 קיר', cost:{stone:3}, type:'building', station:'table' },
  { id:'wall_thorn', name:'🌵 קיר קוצים', cost:{wood:2, stone:1}, type:'building', station:'table' },
  { id:'bone_wall', name:'🦴 קיר עצמות', cost:{bones:4}, type:'building', station:'table' },
  { id:'shovel', name:'🥄 את חפירה', cost:{wood:2, stone:1}, type:'tool', station:'table' },
  
  { id:'furnace', name:'♨️ תנור אבן', cost:{stone:8}, type:'building', station:'upgraded' },
  { id:'crafting_table_dup', name:'🛠️ שולחן עבודה', cost:{wood:2}, type:'building', station:'upgraded' }, 
  { id:'upgraded_table_dup', name:'⚙️ שולחן משודרג', cost:{wood:4, stone:4, coal:2}, type:'building', station:'upgraded' }, 
  { id:'campfire_dup', name:'🏕️ מדורה', cost:{wood:4, stone:2}, type:'building', station:'upgraded' }, 
  { id:'dough', name:'🥟 בצק חיטה', cost:{wheat:1}, type:'ammo', give:{dough:1}, station:'upgraded' },
  { id:'bowl', name:'🥣 קערת עץ', cost:{wood:3}, type:'ammo', give:{bowl:1}, station:'upgraded' },
  { id:'crystal_device', name:'💎 מכשיר הקריסטל', cost:{stone:8, iron:8, crystal:1}, type:'building', station:'upgraded' },
  { id:'reinforcement', name:'⛓️ חיזוק ברזל', cost:{iron_ingot:2}, type:'ammo', give:{reinforcement:1}, station:'upgraded' },
  
  { id:'iron_bucket', name:'🪣 דלי ברזל', cost:{iron_ingot:3}, type:'ammo', give:{torch:1}, station:'furnace' }, 
  { id:'arrowIron', name:'➶ 5 חצי ברזל', cost:{wood:1, iron_ingot:1}, type:'ammo', give:{arrowIron:5}, station:'furnace' }, 
  { id:'iron_axe', name:'🪓 גרזן ברזל', cost:{wood:2, iron_ingot:2}, type:'tool', station:'furnace' }, 
  { id:'iron_pickaxe', name:'⛏️ מכוש ברזל', cost:{wood:2, iron_ingot:3}, type:'tool', station:'furnace' }, 
  { id:'iron_sword', name:'🗡️ חרב ברזל', cost:{wood:1, iron_ingot:2}, type:'tool', station:'furnace' }, 
  { id:'bread', name:'🍞 לחם חם', cost:{dough:1, coal:1}, type:'ammo', give:{bread:1}, station:'furnace' },
  { id:'smelt_iron', name:'⚪ חמם ברזל', cost:{iron:1, coal:1}, type:'ammo', give:{iron_ingot:1}, station:'furnace' },
  
  { id:'cooked_meat', name:'🍖 בשר מעושן', cost:{bowl:1, meat:1}, type:'ammo', give:{cooked_meat:1}, station:'campfire' },
  { id:'fruit_salad', name:'🥗 סלט פירות', cost:{bowl:1, berry:2}, type:'ammo', give:{fruit_salad:1}, station:'campfire' }
];

const names = {wood:'🪵 עץ',stone:'🪨 אבן',coal:'⚫ פחם',iron:'🔶 ברזל',iron_ingot:'⚪ ברזל מחומם',berry:'🍓 פרי',meat:'🍖 בשר',torch:'🔥 לפיד',bones:'🦴 עצם',wheat:'🌾 חיטה',seeds:'🌱 זרעים',bowl:'🥣 קערה',dough:'🥟 בצק',bread:'🍞 לחם',cooked_meat:'🍖 בשר מעושן',fruit_salad:'🥗 סלט פירות',crafting_table:'🛠️ שולחן עבודה',upgraded_table:'⚙️ שולחן משודרג',furnace:'♨️ תנור אבן', chest:'📦 תיבת אחסון', campfire:'🏕️ מדורה', wall:'🧱 קיר', wall_thorn:'🌵 קיר קוצים', bone_wall:'🦴 קיר עצמות', crystal:'💎 קריסטל', reinforcement:'⛓️ חיזוק ברזל',
  item_wall:'🧱 קיר (בתיק)', item_wall_thorn:'🌵 קיר קוצים (בתיק)', item_bone_wall:'🦴 קיר עצמות (בתיק)', item_campfire:'🏕️ מדורה (בתיק)', item_furnace:'♨️ תנור (בתיק)', item_crafting_table:'🛠️ שולחן (בתיק)', item_upgraded_table:'⚙️ שולחן משודרג (בתיק)', item_chest:'📦 תיבה (בתיק)', item_crystal_device:'💎 מכשיר קריסטל (בתיק)', item_lucky:'🟨 לאקי בלוק (בתיק)'};

function canCraft(r){ for(const k in r.cost){ if((player.inv[k]||0) < r.cost[k]) return false; } return true; }

function frontPos(){ 
  let dirX = 0, dirY = 0;
  if (joyActive && (Math.abs(joyDX)>0.1 || Math.abs(joyDY)>0.1)) {
      let mag = Math.hypot(joyDX, joyDY); dirX = joyDX / mag; dirY = joyDY / mag;
  } else {
      if (player.facing.includes('right')) dirX = 1; if (player.facing.includes('left')) dirX = -1;
      if (player.facing.includes('down')) dirY = 1; if (player.facing.includes('up')) dirY = -1;
      if (dirX !== 0 && dirY !== 0) { dirX *= 0.707; dirY *= 0.707; }
      else if (dirX===0 && dirY===0) { dirY=1; }
  }
  return { fx: player.x + dirX * (TILE * 1.5), fy: player.y + dirY * (TILE * 1.5) }; 
}

function getNearbyStations() { 
    const tx = Math.floor(player.x/TILE), ty = Math.floor(player.y/TILE); 
    let res = { table: false, upgraded: false, furnace: false, campfire: false };
    for(let oy = -5; oy <= 5; oy++) { 
        for(let ox = -5; ox <= 5; ox++) { 
            const cx = tx+ox, cy = ty+oy; 
            if (world[cy] && world[cy][cx]) {
                let t = world[cy][cx].type;
                if (t === T.CRAFTING_TABLE) res.table = true;
                if (t === T.UPGRADED_TABLE) { res.upgraded = true; res.table = true; } 
                if (t === T.FURNACE) res.furnace = true;
                if (t === T.CAMPFIRE) res.campfire = true;
            }
        }
    } 
    return res; 
}

const DEFERRED_BUILD_IDS = ['crafting_table','upgraded_table','furnace','campfire','chest','wall','crystal_device'];
function normalizedBuildId(id){ return id.replace('_dup',''); }
function craft(r){ 
  if (!canCraft(r)){ showToast('חסרים משאבים!'); return; } 

  if (r.type==='plant') {
      // seeds are placed straight from your bag; cost is only paid at the moment you actually plant
      player.placingItem = r;
      toggleBag();
      showToast(`נבחר: ${r.name}. השתמש בלחצן הבנייה להצבה.`);
      return;
  }

  if (r.type==='building' || r.type==='chest') {
      for(const k in r.cost) player.inv[k] -= r.cost[k];
      const itemKey = 'item_'+normalizedBuildId(r.id);
      player.inv[itemKey] = (player.inv[itemKey]||0) + 1;
      showToast(`${r.name} נוסף לתיק! לחץ עליו ברשימת החומרים כדי להציב אותו.`);
      renderBag();
      return;
  }

  for(const k in r.cost) player.inv[k] -= r.cost[k];

  if (r.id === 'cooked_meat') {
      player.inv.coal = (player.inv.coal || 0) + 1;
      player.inv.cooked_meat = (player.inv.cooked_meat || 0) + 1;
      showToast('בישלת בשר מעושן! הקערה נשרפה והפכה לפחם ⚫');
  } else {
      if (r.type==='tool'){ 
          player.equipment[r.id]=(player.equipment[r.id]||0)+1; showToast('יצרת '+r.name); 
          if(r.id.includes('sword') || r.id==='bow') player.activeWeapon=r.id; 
      } else if (r.type==='ammo'){ 
          for(const k in r.give) player.inv[k]=(player.inv[k]||0)+r.give[k]; showToast('יצרת '+r.name); 
      }
  }
  renderBag();
}
function placeTorchFromBag(){
  if ((player.inv.torch||0) <= 0) return;
  player.placingItem = { id:'torch_place', name:'🔥 לפיד', cost:{}, type:'torch_place' };
  toggleBag();
  showToast('בחרת לפיד - פנה למקום הרצוי ולחץ 🖐️ כדי להציב');
}
function placeItemFromBag(baseId){
  const itemKey = 'item_'+baseId;
  if ((player.inv[itemKey]||0) <= 0) return;
  const label = names[itemKey] || baseId;
  player.placingItem = { id: baseId, name: label, cost: {}, type: 'place_from_item' };
  toggleBag();
  showToast(`בחרת ${label} - פנה למקום הרצוי ולחץ 🖐️ כדי להציב`);
}
window.selectReinforcement = function(){
  if ((player.inv.reinforcement||0) <= 0) return;
  player.placingItem = { id:'reinforce', name:'⛓️ חיזוק ברזל', cost:{}, type:'reinforce' };
  toggleBag();
  showToast('בחרת חיזוק ברזל - כוון אל מבנה שבנית ולחץ 🖐️ כדי לחזק אותו');
}

window.eatItem = function(k) { 
  if ((player.inv[k]||0) <= 0) return; 
  player.inv[k]--; 
  if (k === 'berry') { player.hunger = Math.min(player.maxHunger, player.hunger + 20); showToast('אכלת תות! 🍓'); } 
  else if (k === 'meat') { player.hunger = Math.min(player.maxHunger, player.hunger + 40); player.health = Math.min(player.maxHealth, player.health + 15); showToast('אכלת בשר! 🍖'); } 
  else if (k === 'bread') { player.hunger = Math.min(player.maxHunger, player.hunger + 80); player.health = Math.min(player.maxHealth, player.health + 35); showToast('אכלת לחם חם! 🍞'); }
  else if (k === 'cooked_meat') { player.hunger = Math.min(player.maxHunger, player.hunger + 90); player.health = Math.min(player.maxHealth, player.health + 50); showToast('אכלת בשר מעושן משובח! 🍖🔥'); }
  else if (k === 'fruit_salad') { 
      player.hunger = Math.min(player.maxHunger, player.hunger + 40); 
      player.health = Math.min(player.maxHealth, player.health + 25); 
      player.speedBoostTimer = 8.0; 
      player.efficiencyBoostTimer = 8.0;
      player.inv.bowl = (player.inv.bowl || 0) + 1;
      showToast('🥗 אכלת סלט פירות! מהירות וחציבה שופרו זמנית!'); 
  }
  sfxGather(); renderBag(); updateHUD(); 
}

window.tryInteract = function() { 
    if (player.placingItem) {
        let r = player.placingItem;
        
        let p = frontPos();
        let tx = Math.floor(p.fx / TILE);
        let ty = Math.floor(p.fy / TILE);
        if (ty < 0 || ty >= MAPH || tx < 0 || tx >= MAPW) { showToast('מחוץ לגבולות המפה!'); return; }
        
        let t = world[ty][tx];
        let ptx = Math.floor(player.x/TILE), pty = Math.floor(player.y/TILE);

        // Iron reinforcement: wrap an EXISTING built object to add a big chunk of durability.
        if (r.type === 'reinforce'){
          if ((player.inv.reinforcement||0) <= 0){ showToast('אין לך חיזוק ברזל בתיק!'); player.placingItem = null; return; }
          if (PLAYER_BUILT_TILES.includes(t.type) || t.type===T.CRYSTAL_DEVICE){
            player.inv.reinforcement -= 1;
            const add = 100; // each iron reinforcement adds ~100 hits of durability
            t.maxHp = (t.maxHp || tileHP(t.type)) + add;
            t.hp = (t.hp || tileHP(t.type)) + add;
            t.reinforced = (t.reinforced || 0) + 1;
            showToast('⛓️ חיזקת את המבנה בברזל! +100 עמידות');
            if ((player.inv.reinforcement||0) <= 0) player.placingItem = null;
            renderBag();
          } else {
            showToast('כוון אל מבנה שבנית כדי לחזק אותו');
          }
          return;
        }

        // Building on water is now allowed (bridges/bases over the lake); only seeds still can't go on water.
        let waterBlocked = isWater(t) && r.type === 'plant';
        if (isSolid(t) || waterBlocked || (tx === ptx && ty === pty)) { showToast('המקום חסום!'); return; }

        if (r.type === 'plant') {
            if (!canCraft(r)) { showToast('חסרים משאבים!'); player.placingItem = null; return; }
            for(const k in r.cost) player.inv[k] -= r.cost[k];
            const newTile = { type:T.CROP, hp:tileHP(T.CROP), timer:0, growAt: performance.now()+opCropGrowSeconds*1000, plantedAt: performance.now() };
            world[ty][tx] = newTile;
            cropTiles.push(newTile);
            showToast('שתלת זרעים! 🌱 יגדל עם הזמן');
            if (!canCraft(r)) player.placingItem = null;   // keep planting while you still have seeds
            renderBag();
            return;
        }

        if (r.type === 'torch_place') {
            if ((player.inv.torch||0) <= 0) { showToast('אין לך לפיד בתיק!'); player.placingItem = null; return; }
            player.inv.torch -= 1;
            world[ty][tx] = { type:T.PLACED_TORCH, hp:tileHP(T.PLACED_TORCH), timer:0 };
            showToast('הצבת לפיד על הרצפה! 🔥');
            if ((player.inv.torch||0) <= 0) player.placingItem = null;   // keep placing while torches remain
            renderBag();
            return;
        }

        if (r.type === 'place_from_item') {
            const itemKey = 'item_'+r.id;
            if ((player.inv[itemKey]||0) <= 0) { showToast('אין לך את זה בתיק!'); player.placingItem = null; return; }

            if (r.id === 'chest') {
                chests.push({x: tx*TILE + TILE/2, y: ty*TILE + TILE/2, items:{}});
                player.inv[itemKey] -= 1;
                showToast('הצבת ' + r.name + ' בהצלחה! 🎉');
                if ((player.inv[itemKey]||0) <= 0) player.placingItem = null;
                renderBag(); return;
            }

            let placedType = T.WALL;
            if (r.id==='wall_thorn') placedType = T.WALL_THORN;
            if (r.id==='bone_wall') placedType = T.BONE_WALL;
            if (r.id==='crafting_table') placedType = T.CRAFTING_TABLE;
            if (r.id==='upgraded_table') placedType = T.UPGRADED_TABLE;
            if (r.id==='furnace') placedType = T.FURNACE;
            if (r.id==='campfire') placedType = T.CAMPFIRE;
            if (r.id==='crystal_device') placedType = T.CRYSTAL_DEVICE;
            if (r.id==='lucky') placedType = T.LUCKY;

            const placedHp = tileHP(placedType);
            world[ty][tx] = { type: placedType, hp: placedHp, maxHp: placedHp, timer: 0 };
            if (placedType===T.LUCKY) { world[ty][tx].luckyChoices = luckyQueue.length ? luckyQueue.shift() : null; }
            player.inv[itemKey] -= 1;

            if (r.id==='crystal_device') {
                crystalPlaced = true; crystalActivated = false;
                crystalDevicePos = { x: tx*TILE+TILE/2, y: ty*TILE+TILE/2, tx, ty };
                showToast('הצבת את מכשיר הקריסטל! גש אליו ולחץ 🖐️ כדי להפעיל אותו 💎');
                player.placingItem = null;   // crystal device is one-off
            } else {
                showToast('הצבת ' + r.name + ' בהצלחה! 🎉');
                if ((player.inv[itemKey]||0) <= 0) player.placingItem = null;   // keep building the same block until you run out
            }
            renderBag();
            return;
        }
        return;
    }

    // Shovel: dig ground that touches water and the water spreads into it — lets you carve your own lakes/canals.
    if (player.equipment && player.equipment.shovel){
        const dp = frontPos(); const dtx = Math.floor(dp.fx/TILE), dty = Math.floor(dp.fy/TILE);
        if (world[dty] && world[dty][dtx]){
            const dg = world[dty][dtx];
            if (dg.type===T.GRASS || dg.type===T.SAND || dg.type===T.SNOW){
                const nearWater = [[0,-1],[0,1],[-1,0],[1,0]].some(([ox,oy])=> world[dty+oy] && world[dty+oy][dtx+ox] && world[dty+oy][dtx+ox].type===T.WATER);
                if (nearWater){
                    world[dty][dtx] = { type:T.WATER, hp:0, timer:0 };
                    stats.blocksDestroyed++; sfxGather(); spawnParticle(dp.fx, dp.fy, '#2a5a8a', 5);
                    showToast('🥄 חפרת תעלה — המים התפשטו!');
                    return;
                }
            }
        }
    }

    // Crystal device activation
    if (crystalPlaced && crystalDevicePos){
        const cd = Math.hypot(player.x - crystalDevicePos.x, player.y - crystalDevicePos.y);
        if (cd < TILE*2.2){
            if (!crystalActivated){
                crystalActivated = true;
                eternalNightActive = false;
                forcedDayUntil = performance.now() + 120000;
                player.maxHealth += 50; player.maxHunger += 50;
                player.health = player.maxHealth; player.hunger = player.maxHunger;
                showToast('💎 הפעלת את הקריסטל! +50 חיים מקס׳, +50 אוכל מקס׳. הלילה הנצחי (אם התחיל) נעצר, ותקבל עוד כוח על כל יום ששרדת איתו פעיל!');
            } else {
                showToast('💎 הקריסטל כבר פעיל ומגן עליך');
            }
            return;
        }
    }

    // Tablet lore
    const ttx = Math.floor(player.x/TILE), tty = Math.floor(player.y/TILE);
    for(let oy=-2; oy<=2; oy++){
        for(let ox=-2; ox<=2; ox++){
            const cx=ttx+ox, cy=tty+oy;
            if (world[cy] && world[cy][cx] && world[cy][cx].type===T.TABLET){
                alert('תבנה קריסטל לפני היום החמישי ותפעיל אותו.\nהוא ייתן לך כוחות על כל יום שאתה מצליח לשרוד.\nואם לא - ביום החמישי יגיע הלילה הנצחי.\n\n(חפש קריסטל נדיר במפה - יש רק אחד כזה בעולם, ובנה אותו לכלי בשולחן המשודרג עם 8 אבן + 8 ברזל)');
                return;
            }
        }
    }

    let found = false; 
    for (const c of chests){ if (Math.hypot(c.x-player.x, c.y-player.y) < TILE*5.5){ openChest(c); found = true; break; } } 
    if (found) return; 
    
    const tx = Math.floor(player.x/TILE), ty = Math.floor(player.y/TILE); 
    for(let oy=-5; oy<=5; oy++) { 
        for(let ox=-5; ox<=5; ox++) { 
            const cx = tx+ox, cy = ty+oy; 
            if (world[cy] && world[cy][cx]) {
                let t = world[cy][cx].type;
                if (t === T.CAMPFIRE || t === T.CRAFTING_TABLE || t === T.UPGRADED_TABLE || t === T.FURNACE) { 
                    if(!document.getElementById('bagPanel').classList.contains('open')) toggleBag(); 
                    let msg = t===T.FURNACE ? '♨️ תנור מופעל' : (t===T.UPGRADED_TABLE ? '⚙️ שולחן משודרג פעיל' : (t===T.CAMPFIRE ? '🏕️ מדורה פעילה' : '🛠️ שולחן עבודה פעיל'));
                    showToast(msg); found = true; break; 
                }
            }
        }
        if (found) break;
    } 
    if (!found) showToast('אין תחנת עבודה או תיבה ברדיוס 5 בלוקים'); 
}

function hasTreeNeighbor(x, y) { let dirs = [[0,-1],[0,1],[-1,0],[1,0],[-1,-1],[1,-1],[-1,1],[1,1]]; for (let d of dirs) { let nx = x + d[0], ny = y + d[1]; if (ny >= 0 && ny < MAPH && nx >= 0 && nx < MAPW) { let t = world[ny][nx].type; if (t === T.TREE || t === T.PINE) return true; } } return false; }
function updateResourceCounts() { currentCounts = { tree:0, stone:0, coal:0, iron:0, bush:0, animal:animals.length }; for(let y=0;y<MAPH;y++){ for(let x=0;x<MAPW;x++){ let t = world[y][x].type; if (t===T.TREE || t===T.PINE || t===T.TRUNK || t===T.SAPLING) currentCounts.tree++; else if (t===T.ROCK) currentCounts.stone++; else if (t===T.COAL) currentCounts.coal++; else if (t===T.IRONROCK) currentCounts.iron++; else if (t===T.BUSH || t===T.WHEAT) currentCounts.bush++; } } }

function runRandomTickEngine() {
  let rx = Math.floor(Math.random() * MAPW); let ry = Math.floor(Math.random() * MAPH); let tile = world[ry][rx];
  if (tile.type === T.GRASS || tile.type === T.SAND || tile.type === T.SNOW) {
    if (hasTreeNeighbor(rx, ry)) {
      let roll = Math.random() * 100;
      if (roll < opStoneChance) { if(currentCounts.stone < opMaxStone) { world[ry][rx] = { type: T.ROCK, hp: tileHP(T.ROCK), timer: 0 }; currentCounts.stone++; } }
      else if (roll < opStoneChance + opCoalChance) { if(currentCounts.coal < opMaxCoal) { world[ry][rx] = { type: T.COAL, hp: tileHP(T.COAL), timer: 0 }; currentCounts.coal++; } }
      else if (roll < opStoneChance + opCoalChance + opIronChance) { if(currentCounts.iron < opMaxIron) { world[ry][rx] = { type: T.IRONROCK, hp: tileHP(T.IRONROCK), timer: 0 }; currentCounts.iron++; } }
      else if (roll < opStoneChance + opCoalChance + opIronChance + opBushChance) { 
          if(currentCounts.bush < opMaxBush) { 
              let finalSpawn = Math.random() < 0.5 ? T.BUSH : T.WHEAT; 
              world[ry][rx] = { type: finalSpawn, hp: tileHP(finalSpawn), timer: 0 }; 
              currentCounts.bush++; 
          } 
      }
    }
    if (Math.random() * 100 < opAnimalChance && currentCounts.animal < opMaxAnimal) { animals.push(makeAnimal(rx*TILE+TILE/2, ry*TILE+TILE/2)); currentCounts.animal++; }
    // saplings sprout on their own from bare grass/snow (not desert sand), independent of nearby trees
    if ((tile.type===T.GRASS || tile.type===T.SNOW) && currentCounts.tree < opMaxTree && Math.random()*100 < 0.12) { world[ry][rx] = { type:T.SAPLING, hp:tileHP(T.SAPLING), timer:0 }; currentCounts.tree++; }
  } else if (tile.type === T.TREE || tile.type === T.PINE || tile.type === T.TRUNK) {
    if (Math.random() * 100 < opTreeChance) {
      if (tile.type === T.TRUNK) { let b = biomeAt(rx, ry); world[ry][rx].type = (b === BIOME.SNOW) ? T.PINE : T.TREE; world[ry][rx].hp = tileHP(world[ry][rx].type); }
      else {
        let dirs = [[0,-1],[0,1],[-1,0],[1,0],[-1,-1],[1,-1],[-1,1],[1,1]]; let d = dirs[Math.floor(Math.random() * dirs.length)]; let nx = rx + d[0], ny = ry + d[1];
        if (ny >= 0 && ny < MAPH && nx >= 0 && nx < MAPW) { let nt = world[ny][nx].type; if (nt === T.GRASS || nt === T.SAND || nt === T.SNOW) { if(currentCounts.tree < opMaxTree) { world[ny][nx] = { type: T.SAPLING, hp: tileHP(T.SAPLING), timer: 0 }; currentCounts.tree++; } } }
      }
    }
  } else if (tile.type === T.SAPLING) { let b = biomeAt(rx, ry); world[ry][rx].type = (b === BIOME.SNOW) ? T.PINE : T.TREE; world[ry][rx].hp = tileHP(world[ry][rx].type); }
}

/* ============ Farming: planted crop growth ============ */
function updateCrops(){
  if (!cropTiles.length) return;
  const now = performance.now();
  for (const c of cropTiles){
    if (c.type !== T.CROP) continue;
    const total = Math.max(1, opCropGrowSeconds*1000);
    const elapsed = total - (c.growAt - now);
    c.stage = elapsed < total*0.34 ? 0 : (elapsed < total*0.67 ? 1 : 2);
    if (now >= c.growAt){ c.type = T.WHEAT; c.hp = tileHP(T.WHEAT); }
  }
  if (cropTiles.length > 300) cropTiles = cropTiles.filter(c=>c.type===T.CROP);
}

function update(dt){
  if (gameOver || !gameStarted || bonusModalOpen) return;
  time += dt; if (time >= CYCLE_LEN){ time = 0; dayNum++; showToast('יום '+dayNum+' מתחיל'); if (dayNum>=eternalNightDay && !crystalActivated){ if(!eternalNightActive){ eternalNightActive = true; showToast('🌑 הלילה הנצחי החל! מפלצות שונות יגיעו וינסו לשבור מה שבנית'); } }
    if (crystalActivated){ crystalBonusDays++; player.maxHealth += 10; player.maxHunger += 10; player.health = Math.min(player.maxHealth, player.health+10); player.hunger = Math.min(player.maxHunger, player.hunger+10); showToast(`💎 כוח הקריסטל גדל! +10 חיים מקס׳, +10 אוכל מקס׳, נזק גבוה יותר (יום ${crystalBonusDays} עם הקריסטל)`); }
    if (adminNightlyAll) grantNightlyAll(); else maybeShowMorningBonus();
  }
  const isNight = getNightFactor() > 0.45;
  
  countTimer += dt; if (countTimer >= 1.0) { countTimer = 0; updateResourceCounts(); }

  if (opTickDelay > 0) {
    tickAcc += dt;
    while (tickAcc >= opTickDelay) {
      tickAcc -= opTickDelay;
      for (let i = 0; i < opBlocksPerTick; i++) runRandomTickEngine();
    }
  }
  updateCrops();

  if (player.hurtSfxCd > 0) player.hurtSfxCd -= dt;
  let dx=0, dy=0; if (keys['w']||keys['arrowup']) dy-=1; if (keys['s']||keys['arrowdown']) dy+=1; if (keys['a']||keys['arrowleft']) dx-=1; if (keys['d']||keys['arrowright']) dx+=1;
  if (joyActive && (Math.abs(joyDX)>0.2||Math.abs(joyDY)>0.2)){ dx=joyDX; dy=joyDY; }
  let isWaterTile = isWater(tileAt(player.x, player.y)); 
  
  let currentSpeed = (player.speed + (player.speedBonus||0)) * (isWaterTile ? 0.5 : 1.0);
  if (player.speedBoostTimer && player.speedBoostTimer > 0) {
      player.speedBoostTimer -= dt;
      currentSpeed *= 1.5;
  }

  if (Math.abs(dx) > 0.1 || Math.abs(dy) > 0.1) {
    player.isWalking = true; player.walkFrame += dt * 10;
    if (Math.abs(dx) > 0.1 && Math.abs(dy) > 0.1) {
        player.facing = (dy > 0 ? 'down' : 'up') + '-' + (dx > 0 ? 'right' : 'left');
    } else if (Math.abs(dx) >= Math.abs(dy)) {
        player.facing = dx > 0 ? 'right' : 'left';
    } else {
        player.facing = dy > 0 ? 'down' : 'up';
    }
  } else { player.isWalking = false; }

  if (motionGrid === 'smooth') {
    if (player.isWalking) { let nextX = player.x + dx * currentSpeed; let nextY = player.y + dy * currentSpeed; if (!isSolid(tileAt(nextX, player.y))) player.x = nextX; if (!isSolid(tileAt(player.x, nextY))) player.y = nextY; }
  } else {
    let stepSize = TILE; if (motionGrid === 'half') stepSize = TILE / 2; if (motionGrid === 'quarter') stepSize = TILE / 4;
    if (!player.moving && player.isWalking) {
      let stepX = 0, stepY = 0; if (Math.abs(dx) >= Math.abs(dy)) stepX = dx > 0 ? stepSize : -stepSize; else stepY = dy > 0 ? stepSize : -stepSize;
      let targetX = player.x + stepX; let targetY = player.y + stepY;
      if (!isSolid(tileAt(targetX, targetY))) { player.moveFrom = { x: player.x, y: player.y }; player.moveTo = { x: targetX, y: targetY }; player.moveT = 0; player.moving = true; player.moveDuration = (stepSize / TILE) * (isWaterTile ? 0.45 : 0.22); }
    }
    if (player.moving) { player.moveT += dt / player.moveDuration; if (player.moveT >= 1) { player.moveT = 1; player.moving = false; player.x = player.moveTo.x; player.y = player.moveTo.y; } else { player.x = player.moveFrom.x + (player.moveTo.x - player.moveFrom.x) * player.moveT; player.y = player.moveFrom.y + (player.moveTo.y - player.moveFrom.y) * player.moveT; } }
  }
  player.x = Math.max(TILE * 2.2, Math.min((MAPW - 2.2) * TILE, player.x)); player.y = Math.max(TILE * 2.2, Math.min((MAPH - 2.2) * TILE, player.y));
  player.gridX = Math.floor(player.x/TILE); player.gridY = Math.floor(player.y/TILE);
  camX = player.x; camY = player.y; player.hunger -= dt*0.32; if (player.hunger<=0){ player.hunger=0; if(!cheatGodMode) player.health -= dt*1.4; }
  if (world[player.gridY] && world[player.gridY][player.gridX]) { let pTile = world[player.gridY][player.gridX]; if(pTile.type === T.CAMPFIRE) { player.health = Math.min(player.maxHealth, player.health+dt*8); } }
  if (player.attackCd>0) player.attackCd -= dt; if (keys[' '] || actionHeld) tryAction();
  const curBiome = biomeAt(Math.floor(player.x/TILE), Math.floor(player.y/TILE));
  const inEternalNight = eternalNightActive && !crystalActivated;
  if (!cheatNoEnemies && (isNight || inEternalNight)){ const cap = (inEternalNight ? 10 : 5) + Math.floor(dayNum/2); if (Math.random() < dt*(inEternalNight?0.28:0.16) && enemies.length < cap) spawnEnemy(curBiome); } else if (!isNight) { enemies = []; if (Math.random() < dt*0.08 && animals.length < 6 && curBiome!==BIOME.SNOW) spawnAnimal(); }
  if (cheatNoEnemies && enemies.length) enemies = [];
  updateEnemies(dt); updateAnimals(dt); updateProjectiles(dt); updateParticles(dt);
  
  const ibtn = document.getElementById('interactBtn');
  const pbtn = document.getElementById('placeBtn');
  if (player.placingItem) {
      let bEmoji = player.placingItem.name.split(' ')[0] || '🧱';
      ibtn.innerHTML = bEmoji;
      ibtn.style.background = "rgba(47, 122, 234, 0.85)";
      pbtn.classList.add('show'); pbtn.textContent = bEmoji;
  } else {
      ibtn.innerHTML = '🖐️';
      ibtn.style.background = "rgba(217, 201, 138, 0.45)";
      pbtn.classList.remove('show');
  }

  if (player.health<=0 && !cheatGodMode) endGame(); updateHUD();
}
function getNightFactor() {
  if (performance.now() < forcedDayUntil) return 0;
  if (eternalNightActive && !crystalActivated) return 1;
  const nightCore = CYCLE_LEN * NIGHT_CORE_RATIO; const dayLen = Math.max(1, CYCLE_LEN - nightCore - DUSK_LEN - DAWN_LEN); const duskStart = dayLen; const duskEnd = dayLen + DUSK_LEN; const nightEnd = duskEnd + nightCore; const dawnEnd = nightEnd + DAWN_LEN; if (time < duskStart) return 0; if (time < duskEnd) return (time - duskStart) / DUSK_LEN; if (time < nightEnd) return 1; if (time < dawnEnd) return 1 - (time - nightEnd) / DAWN_LEN; return 0;
}

function tryAction(){
  if (player.attackCd > 0) return; player.attackCd = player.activeWeapon==='bow' ? 0.45 : 0.25;
  
  let dirX = 0, dirY = 0;
  if (joyActive && (Math.abs(joyDX)>0.1 || Math.abs(joyDY)>0.1)) {
      let mag = Math.hypot(joyDX, joyDY); dirX = joyDX / mag; dirY = joyDY / mag;
  } else {
      if (player.facing.includes('right')) dirX = 1; if (player.facing.includes('left')) dirX = -1;
      if (player.facing.includes('down')) dirY = 1; if (player.facing.includes('up')) dirY = -1;
      if (dirX !== 0 && dirY !== 0) { dirX *= 0.707; dirY *= 0.707; } else if (dirX===0 && dirY===0) { dirY=1; }
  }

  if (player.activeWeapon==='bow'){ 
    const arrowType = player.inv.arrowIron>0 ? 'arrowIron' : (player.inv.arrowWood>0 ? 'arrowWood' : null); 
    if (!arrowType){ showToast('אין חצים!'); return; } player.inv[arrowType]--; renderBag(); 
    projectiles.push({ x:player.x, y:player.y, vx:dirX*7, vy:dirY*7, dmg: (arrowType==='arrowIron'?7:3) + (crystalActivated?crystalBonusDays+2:0), life:1.2 }); sfxShoot(); return; 
  }

  let toolPower = 1 + (player.equipment.axe?1:0) + (player.equipment.iron_axe?2:0) + (player.equipment.pickaxe?1:0) + (player.equipment.iron_pickaxe?2:0) + (player.gatherBonus||0);
  if (player.efficiencyBoostTimer && player.efficiencyBoostTimer > 0) {
      toolPower += 2;
  }

  const breakables = [T.TREE,T.PINE,T.ROCK,T.COAL,T.IRONROCK,T.BUSH,T.CACTUS,T.WALL,T.WALL_THORN,T.BONE_WALL,T.LUCKY,T.CAMPFIRE,T.TRUNK,T.CRAFTING_TABLE,T.UPGRADED_TABLE,T.FURNACE,T.SAPLING,T.SKULL,T.WHEAT,T.CROP,T.CRYSTAL_ORE,T.PLACED_TORCH];
  
  let hitBlock = false;
  // Mining reach (upgradable via morning bonuses)
  for (let d = 0; d <= (player.breakReach||2); d += 0.5) {
      let fx = player.x + dirX * (d * TILE); let fy = player.y + dirY * (d * TILE); let t = tileAt(fx, fy);
      if (breakables.includes(t.type)){
        t.hp -= toolPower; sfxGather(); spawnParticle(fx,fy,'#fff',5);
        if (d > stats.maxBreakDist) stats.maxBreakDist = d;
        if (t.hp<=0){
          stats.blocksDestroyed++;
          const tx=Math.floor(fx/TILE),ty=Math.floor(fy/TILE); let b = biomeAt(tx, ty); let defaultFloor = (b===BIOME.DESERT)?T.SAND:(b===BIOME.SNOW)?T.SNOW:T.GRASS;
          if (t.type===T.TREE||t.type===T.PINE) { player.inv.wood+=1; world[ty][tx] = {type: T.TRUNK, hp: tileHP(T.TRUNK), timer: 0}; showToast('קיבלת עץ, הגזע נשאר! 🪵'); }
          else if (t.type === T.TRUNK) { player.inv.wood+=2; world[ty][tx] = {type:defaultFloor, hp:0, timer:0}; showToast('השמדת את הגזע! קבל 2 עץ 🪓'); }
          else if (t.type === T.SAPLING) { player.inv.wood+=1; world[ty][tx] = {type:defaultFloor, hp:0, timer:0}; showToast('חצבת שתיל תינוק! קיבלת עץ 1 🌱'); }
          else if (t.type === T.CRAFTING_TABLE || t.type === T.UPGRADED_TABLE) { player.inv.wood+=2; world[ty][tx] = {type:defaultFloor, hp:0, timer:0}; showToast('שברת שולחן עבודה! 🛠️'); }
          else if (t.type === T.FURNACE) { player.inv.stone+=4; world[ty][tx] = {type:defaultFloor, hp:0, timer:0}; showToast('שברת את התנור! ♨️'); }
          else if (t.type === T.SKULL) { player.inv.bones+=2; world[ty][tx] = {type:defaultFloor, hp:0, timer:0}; showToast('מצאת עצמות! 💀'); }
          else if (t.type === T.CRYSTAL_ORE) { player.inv.crystal = (player.inv.crystal||0)+1; world[ty][tx] = {type:defaultFloor, hp:0, timer:0}; showToast('💎 מצאת את הקריסטל היחיד בעולם! עכשיו בנה אותו בשולחן המשודרג'); }
          else if (t.type === T.PLACED_TORCH) { player.inv.torch = (player.inv.torch||0)+1; world[ty][tx] = {type:defaultFloor, hp:0, timer:0}; showToast('אספת את הלפיד בחזרה 🔥'); }
          else if (t.type === T.WALL_THORN) { player.inv.wood+=1; world[ty][tx] = {type:defaultFloor, hp:0, timer:0}; showToast('פירקת קיר קוצים'); }
          else if (t.type === T.BONE_WALL) { player.inv.bones+=2; world[ty][tx] = {type:defaultFloor, hp:0, timer:0}; showToast('פירקת קיר עצמות 🦴'); }
          else if (t.type === T.LUCKY) { const savedChoices = t.luckyChoices; world[ty][tx] = {type:defaultFloor, hp:0, timer:0}; openLuckyBlock(savedChoices); }
          else if (t.type === T.CROP) {
              const stage = t.stage||0;
              world[ty][tx] = {type:defaultFloor, hp:0, timer:0};
              if (stage>=2) { showToast('עקרת יבול לא בשל 🌱 (חכה לו לגדול הבא)'); }
              else { player.inv.seeds = (player.inv.seeds||0)+1; showToast('עקרת שתיל צעיר, קיבלת זרע בחזרה 🌱'); }
          }
          else if (t.type === T.WHEAT) {
              player.inv.wheat = (player.inv.wheat || 0) + 1;
              let seedsGained = Math.random() < 0.10 ? 2 : 1; 
              player.inv.seeds = (player.inv.seeds || 0) + seedsGained;
              world[ty][tx] = {type:defaultFloor, hp:0, timer:0};
              showToast(`קצרת חיטה בשלה! 🌾 (+1 חיטה, +${seedsGained} זרעים)`);
          }
          else {
              if (t.type===T.ROCK){ player.inv.stone+=2; if(Math.random()<0.15) player.inv.iron+=1; }
              if (t.type===T.COAL) player.inv.coal+=2; if (t.type===T.IRONROCK) player.inv.iron+=2;
              if (t.type===T.BUSH) player.inv.berry+=1; if (t.type===T.CACTUS) player.inv.wood+=1;
              world[ty][tx] = {type:defaultFloor, hp:0, timer:0};
          } renderBag();
        } hitBlock = true; break; 
      }
  }
  if (hitBlock) return; 

  let meleeDmg = 4 + (player.equipment.iron_sword ? 4 : 0) + (crystalActivated ? crystalBonusDays+2 : 0); 
  for (const e of enemies){ if (Math.hypot(e.x-player.x, e.y-player.y) < TILE*1.5){ e.hp -= meleeDmg; sfxHit(); spawnParticle(e.x,e.y,'#e04a30',5); if(e.hp<=0){ enemies=enemies.filter(x=>x!==e); stats.monstersKilled++; player.inv.bones += e.kind==='wolf'?3:e.kind==='siberian_wolf'?4:e.kind==='brute'?5:1; if(e.eatenLoot){ for(const k in e.eatenLoot) player.inv[k]=(player.inv[k]||0)+e.eatenLoot[k]; if(Object.keys(e.eatenLoot).length) showToast('קיבלת בחזרה חומרים שהמפלצת שברה! 🦴📦'); else showToast(`הרגת מפלצת! 🦴`); } else showToast(`הרגת מפלצת! 🦴`); renderBag(); } return; } }
  for (const a of animals){ if (Math.hypot(a.x-player.x, a.y-player.y) < TILE*1.5){ a.hp -= meleeDmg; sfxHit(); if(a.hp<=0){ animals=animals.filter(x=>x!==a); stats.animalsKilled++; player.inv.meat+=2; player.inv.bones+=1; player.hunger=Math.min(player.maxHunger,player.hunger+15); renderBag(); } return; } }
}

// A position is "lit" if a torch/campfire/furnace is within ~4 tiles -> monsters refuse to spawn there (keeps your lit base safe).
function isNearLight(px, py){
  const tx = Math.floor(px/TILE), ty = Math.floor(py/TILE), R = 4;
  for (let oy=-R; oy<=R; oy++){ for (let ox=-R; ox<=R; ox++){ const cx=tx+ox, cy=ty+oy; if (world[cy] && world[cy][cx]){ const tt = world[cy][cx].type; if (tt===T.PLACED_TORCH || tt===T.CAMPFIRE || tt===T.FURNACE) return true; } } }
  return false;
}
function spawnEnemy(biome){ let angle=Math.random()*Math.PI*2; const dist=340+Math.random()*100; let kind='zombie'; if (biome===BIOME.FOREST) kind='wolf'; else if (biome===BIOME.SNOW) kind='siberian_wolf'; else if (biome===BIOME.DESERT) kind='scorpion';
  const inEternalNight = eternalNightActive && !crystalActivated;
  // Variety grows with days survived: day10+ brings the big brute, day15+ adds wraiths, day20+ adds archers.
  let r = Math.random();
  if (dayNum>=20 && r<0.15) kind='archer';
  else if (dayNum>=15 && r<0.30) kind='wraith';
  else if (dayNum>=10 && r<0.45) kind='brute';
  if (inEternalNight && Math.random()<0.35){ kind = Math.random()<0.5 ? 'wraith' : (dayNum>=10?'brute':kind); }
  const scale = 1 + dayNum*0.15; const baseTable = { wolf:{hp:6,spd:1.2,dmg:9}, siberian_wolf:{hp:8,spd:1.3,dmg:12}, scorpion:{hp:5,spd:0.8,dmg:8}, zombie:{hp:6,spd:0.9,dmg:8}, wraith:{hp:5,spd:1.6,dmg:10}, brute:{hp:16,spd:0.6,dmg:16}, archer:{hp:6,spd:0.7,dmg:6} };
  const base = baseTable[kind];
  let ex, ey, ok=false;
  for (let attempt=0; attempt<10 && !ok; attempt++){
    ex = player.x+Math.cos(angle)*dist; ey = player.y+Math.sin(angle)*dist;
    ex = Math.max(TILE*3, Math.min((MAPW-3)*TILE, ex)); ey = Math.max(TILE*3, Math.min((MAPH-3)*TILE, ey));
    if (!isNearLight(ex, ey)) ok=true; else angle = Math.random()*Math.PI*2;
  }
  if (!ok) return; // every candidate spot was near light -> skip this spawn
  const targetsCrystal = false; // monsters only ever hunt the player, never the crystal
  // late-game, monsters hit both the player and buildings harder over time
  const dmgScale = 1 + Math.max(0, dayNum-5)*0.05;
  enemies.push({ x:ex, y:ey, kind, hp:Math.round(base.hp*scale), maxHp:Math.round(base.hp*scale), speed:base.spd*(1+dayNum*0.02), dmg:base.dmg*(1+dayNum*0.04)*dmgScale, facing:'left', stuck:0, eatenLoot:{}, targetsCrystal, shootCd:0 });
}
// Disguised "spider-rabbit": looks like a rabbit, eyes glow at night, drifts toward you, and reveals as a spider when you get close.
function rollSpider(){
  const inEternalNight = eternalNightActive && !crystalActivated;
  if (inEternalNight) return Math.random() < 0.45;
  if (dayNum >= 15) return Math.random() < 0.22;
  return false;
}
function makeAnimal(x, y){ return { x, y, hp:3, maxHp:3, speed:0.8, wanderT:0, wx:0, wy:0, isSpider: rollSpider() }; }
function spawnAnimal(){ const angle=Math.random()*Math.PI*2, dist=260+Math.random()*100; let ax = player.x+Math.cos(angle)*dist; let ay = player.y+Math.sin(angle)*dist; ax = Math.max(TILE*3, Math.min((MAPW-3)*TILE, ax)); ay = Math.max(TILE*3, Math.min((MAPH-3)*TILE, ay)); animals.push(makeAnimal(ax, ay)); }
// Tiles enemies will chew through to reach the player. Crystal device is intentionally excluded so monsters never destroy it.
const PLAYER_BUILT_TILES = [T.WALL, T.WALL_THORN, T.BONE_WALL, T.FURNACE, T.CRAFTING_TABLE, T.UPGRADED_TABLE, T.CAMPFIRE];
function destroyBuiltTile(bt, bxi, byi, e){
  e.eatenLoot = e.eatenLoot||{};
  if (bt.type===T.WALL) e.eatenLoot.stone=(e.eatenLoot.stone||0)+3;
  else if (bt.type===T.WALL_THORN) e.eatenLoot.wood=(e.eatenLoot.wood||0)+1;
  else if (bt.type===T.FURNACE) e.eatenLoot.stone=(e.eatenLoot.stone||0)+8;
  else if (bt.type===T.CRAFTING_TABLE) e.eatenLoot.wood=(e.eatenLoot.wood||0)+2;
  else if (bt.type===T.UPGRADED_TABLE){ e.eatenLoot.wood=(e.eatenLoot.wood||0)+4; e.eatenLoot.stone=(e.eatenLoot.stone||0)+4; e.eatenLoot.coal=(e.eatenLoot.coal||0)+2; }
  else if (bt.type===T.CAMPFIRE){ e.eatenLoot.wood=(e.eatenLoot.wood||0)+4; e.eatenLoot.stone=(e.eatenLoot.stone||0)+2; }
  else if (bt.type===T.CRYSTAL_DEVICE){ e.eatenLoot.stone=(e.eatenLoot.stone||0)+8; e.eatenLoot.iron=(e.eatenLoot.iron||0)+8; crystalPlaced=false; crystalDevicePos=null; showToast('💔 מפלצת הרסה את מכשיר הקריסטל! מהר תבנה עוד אחד'); }
  const bb=biomeAt(bxi,byi);
  world[byi][bxi] = { type: (bb===BIOME.DESERT?T.SAND:bb===BIOME.SNOW?T.SNOW:T.GRASS), hp:0, timer:0 };
}
function updateEnemies(dt){
  const canBreakBlocks = dayNum >= eternalNightDay || (eternalNightActive && !crystalActivated);
  for (const e of enemies){
    let tx = player.x, ty = player.y;
    if (e.targetsCrystal && crystalPlaced && crystalDevicePos && !crystalActivated){ tx = crystalDevicePos.x; ty = crystalDevicePos.y; }
    let ang = Math.atan2(ty-e.y, tx-e.x); let currentSpeed = e.speed * (isWater(tileAt(e.x, e.y)) ? 0.3 : 1.0);
    e.facing = (tx > e.x) ? 'right' : 'left';

    // Archers stay at range and shoot at the player or at buildings blocking their path
    if (e.kind==='archer'){
      e.shootCd = (e.shootCd||0) - dt;
      const distToTarget = Math.hypot(tx-e.x, ty-e.y);
      if (distToTarget > TILE*4){
        const tryX = e.x + Math.cos(ang)*currentSpeed, tryY = e.y + Math.sin(ang)*currentSpeed;
        if (!isSolid(tileAt(tryX, e.y))) e.x = tryX;
        if (!isSolid(tileAt(e.x, tryY))) e.y = tryY;
      } else if (e.shootCd<=0){
        e.shootCd = 1.8;
        enemyProjectiles.push({ x:e.x, y:e.y, vx:Math.cos(ang)*6, vy:Math.sin(ang)*6, dmg:e.dmg*0.6, life:2.2 });
      }
      e.x = Math.max(TILE*2.2, Math.min((MAPW-2.2)*TILE, e.x)); e.y = Math.max(TILE*2.2, Math.min((MAPH-2.2)*TILE, e.y));
      continue;
    }

    let tryX = e.x + Math.cos(ang) * currentSpeed, tryY = e.y + Math.sin(ang) * currentSpeed;
    if (!isSolid(tileAt(tryX, e.y))) e.x = tryX;
    if (!isSolid(tileAt(e.x, tryY))) e.y = tryY;
    e.x = Math.max(TILE*2.2, Math.min((MAPW-2.2)*TILE, e.x)); e.y = Math.max(TILE*2.2, Math.min((MAPH-2.2)*TILE, e.y));

    // Check directly ahead every frame (independent of whether they slid a bit sideways) so they reliably chew through blocks
    e.stuck = e.stuck||0;
    if (canBreakBlocks){
      const bx = e.x + Math.cos(ang)*TILE*0.75, by = e.y + Math.sin(ang)*TILE*0.75;
      const bt = tileAt(bx,by);
      if (PLAYER_BUILT_TILES.includes(bt.type)){
        e.stuck += dt;
        if (e.stuck > 0.4){
          const toughness = bt.type===T.WALL ? opWallToughnessHits : (bt.type===T.WALL_THORN ? 3 : 8);
          bt.hp -= dt * (tileHP(bt.type)/toughness);
          if (Math.random()<dt*3) spawnParticle(bx,by,'#fff',3);
          if (bt.type===T.WALL_THORN){ e.hp -= dt*6; spawnParticle(e.x,e.y,'#8fae4a',3); } // thorns bite back
          if (bt.hp<=0){
            const bxi=Math.floor(bx/TILE), byi=Math.floor(by/TILE);
            destroyBuiltTile(bt, bxi, byi, e);
            e.stuck = 0;
          }
        }
      } else { e.stuck = 0; }
    } else { e.stuck = 0; }

    // Standing on/near a campfire burns enemies (they can cross it, but it hurts)
    const curTile = tileAt(e.x, e.y);
    if (curTile.type===T.CAMPFIRE){
      e.hp -= dt*9;
      if (Math.random()<dt*4) spawnParticle(e.x, e.y-6, '#ff6a00', 3);
    }

    if (!cheatGodMode && Math.hypot(player.x - e.x, player.y - e.y) < 14) { player.health -= dt * e.dmg; if (player.hurtSfxCd <= 0 || !player.hurtSfxCd) { sfxHurt(); player.hurtSfxCd = 0.5; } }
  }
  enemies = enemies.filter(e=>{
    if (e.hp<=0){ stats.monstersKilled++; if(e.eatenLoot){ for(const k in e.eatenLoot) player.inv[k]=(player.inv[k]||0)+e.eatenLoot[k]; } player.inv.bones+=1; renderBag(); return false; }
    return true;
  });
  for (const p of enemyProjectiles){
    p.x += p.vx*TILE*dt*3; p.y += p.vy*TILE*dt*3; p.life -= dt;
    if (Math.hypot(player.x-p.x, player.y-p.y) < 14){ if(!cheatGodMode) player.health -= p.dmg; p.life=0; sfxHurt(); }
    else {
      const bt = tileAt(p.x,p.y);
      if (PLAYER_BUILT_TILES.includes(bt.type)){ bt.hp -= p.dmg*0.6; p.life=0; if (bt.hp<=0){ const bxi=Math.floor(p.x/TILE), byi=Math.floor(p.y/TILE); destroyBuiltTile(bt, bxi, byi, {eatenLoot:{}}); } }
    }
  }
  enemyProjectiles = enemyProjectiles.filter(p=>p.life>0);
}
function revealSpider(a){
  // turn the disguised rabbit into a fast spider enemy right where it stood
  const scale = 1 + dayNum*0.12;
  enemies.push({ x:a.x, y:a.y, kind:'spider', hp:Math.round(8*scale), maxHp:Math.round(8*scale), speed:1.45*(1+dayNum*0.02), dmg:11*(1+dayNum*0.04), facing:'left', stuck:0, eatenLoot:{}, targetsCrystal:false, shootCd:0 });
  animals = animals.filter(x=>x!==a);
  showToast('🕷️ זה היה עכביש מחופש לארנב! היזהר');
  sfxHurt();
}
function updateAnimals(dt){
  const reveals = [];
  for (const a of animals){
    const d = Math.hypot(player.x-a.x, player.y-a.y);
    if (a.isSpider){
      // spiders creep toward you to bait an approach; reveal on contact range
      if (d < 42){ reveals.push(a); continue; }
      a.wanderT -= dt; if (a.wanderT<=0){ a.wanderT=1+Math.random()*2; const ang=Math.random()*Math.PI*2; a.wx=Math.cos(ang); a.wy=Math.sin(ang); }
      let stepX, stepY;
      if (d < 260){ stepX = (player.x-a.x)/d*a.speed*0.7; stepY = (player.y-a.y)/d*a.speed*0.7; }
      else { stepX = a.wx*a.speed*0.5; stepY = a.wy*a.speed*0.5; }
      let tryX = a.x + stepX, tryY = a.y + stepY;
      if (tryX > TILE*2.2 && tryX < (MAPW-2.2)*TILE && !isSolid(tileAt(tryX, a.y))) a.x = tryX;
      if (tryY > TILE*2.2 && tryY < (MAPH-2.2)*TILE && !isSolid(tileAt(a.x, tryY))) a.y = tryY;
      continue;
    }
    a.wanderT -= dt; if (a.wanderT<=0){ a.wanderT=1+Math.random()*2; const ang=Math.random()*Math.PI*2; a.wx=Math.cos(ang); a.wy=Math.sin(ang); }
    let stepX = 0, stepY = 0; if (d < 100){ stepX = -(player.x-a.x)/d*a.speed*1.5; stepY = -(player.y-a.y)/d*a.speed*1.5; } else { stepX = a.wx*a.speed*0.5; stepY = a.wy*a.speed*0.5; }
    let tryX = a.x + stepX; let tryY = a.y + stepY; if (tryX > TILE*2.2 && tryX < (MAPW-2.2)*TILE && !isSolid(tileAt(tryX, a.y))) a.x = tryX; if (tryY > TILE*2.2 && tryY < (MAPH-2.2)*TILE && !isSolid(tileAt(a.x, tryY))) a.y = tryY;
  }
  for (const a of reveals) revealSpider(a);
}
function updateProjectiles(dt){ for (const p of projectiles){ p.x += p.vx*TILE*dt*4; p.y += p.vy*TILE*dt*4; p.life -= dt; for (const e of enemies){ if (Math.hypot(e.x-p.x,e.y-p.y) < 14){ e.hp -= p.dmg; p.life=0; if(e.hp<=0){ enemies=enemies.filter(x=>x!==e); stats.monstersKilled++; player.inv.bones+=2; if(e.eatenLoot){ for(const k in e.eatenLoot) player.inv[k]=(player.inv[k]||0)+e.eatenLoot[k]; } renderBag(); } } } } projectiles = projectiles.filter(p=>p.life>0); }
function spawnParticle(x,y,color,r){ particles.push({x,y,color,r:r||4,life:0.6,vy:-20}); } function updateParticles(dt){ for(const p of particles){ p.life-=dt; p.y+=p.vy*dt; } particles = particles.filter(p=>p.life>0); }

let openChestRef = null; function openChest(c){ openChestRef = c; document.getElementById('chestPanel').classList.add('open'); renderChest(); } function closeChest(){ document.getElementById('chestPanel').classList.remove('open'); openChestRef=null; } function renderChest(){ const list = document.getElementById('chestList'); list.innerHTML = ''; const keys = ['wood','stone','coal','iron','iron_ingot','berry','meat','bones','wheat','seeds','bowl','dough','bread','cooked_meat','fruit_salad']; keys.forEach(k=>{ if(player.inv[k]!==undefined){ const row = document.createElement('div'); row.className='chestRow'; row.innerHTML = `<span>${names[k]}: תיק ${player.inv[k]||0} | תיבה ${openChestRef.items[k]||0}</span><span><button onclick="chestTransfer('${k}',1)">➡️</button><button onclick="chestTransfer('${k}',-1)">⬅️</button></span>`; list.appendChild(row); } }); } function chestTransfer(k, dir){ if (!openChestRef) return; if (dir>0){ if ((player.inv[k]||0)>0){ player.inv[k]--; openChestRef.items[k]=(openChestRef.items[k]||0)+1; } } else { if ((openChestRef.items[k]||0)>0){ openChestRef.items[k]--; player.inv[k]=(player.inv[k]||0)+1; } } renderChest(); renderBag(); }
function endGame(){ gameOver=true; document.getElementById('msg').style.display='block'; document.getElementById('survivedDays').textContent=dayNum; } function restart(){ document.getElementById('msg').style.display='none'; initGame(); }

/* ============ World selection start screen ============ */
const WORLD_TEST_CODE = '2020';
function startWorld(mode){
  gameMode = mode;
  document.getElementById('worldSelect').style.display = 'none';
  initGame();
  gameStarted = true;
  ensureAudio();
  if (mode==='eternal') showToast('🌑 עולם ללא קריסטל — שרוד כמה שתוכל!');
  else if (mode==='test') showToast('🧪 עולם ניסיון — כל הבלוקים והחומרים אצלך');
}
function askWorldCode(){ document.getElementById('wsCodeWrap').style.display = 'flex'; document.getElementById('wsCodeInput').focus(); }
function submitWorldCode(){
  const val = (document.getElementById('wsCodeInput').value||'').trim();
  if (val !== WORLD_TEST_CODE){ showToast('קוד שגוי'); return; }
  // secret code also unlocks editing how many days pass before the eternal night
  const d = prompt('כמה ימים עד הלילה הנצחי? (ברירת מחדל 5)', String(eternalNightDay));
  const parsed = parseInt(d);
  if (!isNaN(parsed) && parsed >= 1) eternalNightDay = parsed;
  startWorld('test');
}

/* ============ Morning bonus + lucky block system ============ */
function bonusMul(){ return (eternalNightActive && !crystalActivated) ? 2 : 1; }   // eternal night = double reward
function scaledRound(base){
  let v = base * (1 + Math.max(0, dayNum - eternalNightDay) * 0.12) * bonusMul();
  if (Math.random() < 0.05) return 6 + Math.floor(Math.random()*2);   // rare "un-round" 6 or 7
  v = Math.round(v/5)*5; return Math.max(5, v);
}
function mkBonus(emoji, name, value, applyFn){ return { emoji, name, value, valueStr:'+'+value, apply:()=>applyFn(value) }; }
const BONUS_POOL = [
  () => mkBonus('❤️','חיים מקסימליים', scaledRound(30), v=>{ player.maxHealth+=v; player.health=Math.min(player.maxHealth, player.health+v); }),
  () => mkBonus('🍖','אוכל מקסימלי', scaledRound(30), v=>{ player.maxHunger+=v; player.hunger=Math.min(player.maxHunger, player.hunger+v); }),
  () => mkBonus('🧱','קירות לתיק', scaledRound(10), v=>{ player.inv.item_wall=(player.inv.item_wall||0)+v; }),
  () => mkBonus('🌵','קירות קוצים', scaledRound(10), v=>{ player.inv.item_wall_thorn=(player.inv.item_wall_thorn||0)+v; }),
  () => mkBonus('🦴','קירות עצמות', scaledRound(10), v=>{ player.inv.item_bone_wall=(player.inv.item_bone_wall||0)+v; }),
  () => mkBonus('⛓️','חיזוקי ברזל', Math.max(2, Math.round(scaledRound(10)/3)), v=>{ player.inv.reinforcement=(player.inv.reinforcement||0)+v; }),
  () => mkBonus('🔥','לפידים', scaledRound(10), v=>{ player.inv.torch=(player.inv.torch||0)+v; }),
  () => mkBonus('📦','עץ + אבן', scaledRound(30), v=>{ player.inv.wood+=v; player.inv.stone+=v; }),
  () => mkBonus('🍞','בשר לאכילה', scaledRound(10), v=>{ player.inv.meat=(player.inv.meat||0)+v; }),
  () => mkBonus('⛏️','כוח חציבה קבוע', Math.max(1, Math.round(scaledRound(5)/5)), v=>{ player.gatherBonus=(player.gatherBonus||0)+v; }),
  () => mkBonus('📏','מרחק שבירה', 1, v=>{ player.breakReach=Math.min(5, (player.breakReach||2)+v); }),
  () => mkBonus('🏃','מהירות תנועה', 1, v=>{ player.speedBonus=(player.speedBonus||0)+0.3; }),
];
function generateBonusChoices(n){
  const idx = BONUS_POOL.map((_,i)=>i);
  for (let i=idx.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [idx[i],idx[j]]=[idx[j],idx[i]]; }
  return idx.slice(0, n).map(i => BONUS_POOL[i]());
}
let activeBonusChoices = null, bonusFromLucky = false;
function maybeShowMorningBonus(){
  // The bug-testing world keeps the lucky-block / morning bonus OFF so it never interrupts testing
  // (unless the admin "every night" toggle is on, which is handled separately).
  if (gameMode==='test') return;
  const eligible = (gameMode==='eternal' && dayNum>=2) || (dayNum > eternalNightDay);
  if (!eligible || bonusShownForDay >= dayNum) return;
  bonusShownForDay = dayNum;
  openBonusModal(generateBonusChoices(3), false);
}
// Admin convenience: every passing night, hand over a lucky block AND apply every bonus power at once.
function grantNightlyAll(){
  const choices = generateBonusChoices(3);
  luckyQueue.push(choices);
  player.inv.item_lucky = (player.inv.item_lucky||0) + 1;
  BONUS_POOL.forEach(gen => { const c = gen(); c.apply(); stats.dailyChoices.push({ day: dayNum, label: c.emoji + ' ' + c.name + ' ' + c.valueStr }); });
  showToast('🌙 מצב מנהל: קיבלת לאקי בלוק + כל הכוחות ללילה הזה!');
  renderBag(); updateHUD();
}
function openBonusModal(choices, fromLucky){
  activeBonusChoices = choices; bonusFromLucky = !!fromLucky;
  const wrap = document.getElementById('bonusChoices'); wrap.innerHTML='';
  choices.forEach((c, i)=>{
    const d = document.createElement('div'); d.className='bonusChoice';
    d.innerHTML = `<div class="bemoji">${c.emoji}</div><div class="binfo"><div class="bname">${c.name}</div><div class="bval">${c.valueStr}</div></div>`;
    d.onclick = ()=> pickBonus(i);
    wrap.appendChild(d);
  });
  document.getElementById('bonusTitle').textContent = fromLucky ? '🟨 לאקי בלוק' : '🌅 בוקר טוב! בחר בונוס';
  document.getElementById('bonusSub').textContent = fromLucky ? 'בחר אחד — אלו הבחירות ששמרת' : (bonusMul()>1 ? 'לילה נצחי: הבונוסים כפולים! בחר אחד' : 'בחר אחד מהשלושה — או קח לאקי בלוק לאחר כך');
  // from a lucky block you must commit to a pick (no defer/close)
  document.getElementById('bonusLater').style.display = fromLucky ? 'none' : 'block';
  document.getElementById('bonusX').style.display = fromLucky ? 'none' : 'block';
  document.getElementById('bonusModal').classList.add('open');
  bonusModalOpen = true;
}
function pickBonus(i){
  if (!activeBonusChoices || !activeBonusChoices[i]) return;
  const c = activeBonusChoices[i];
  c.apply();
  stats.dailyChoices.push({ day: dayNum, label: c.emoji + ' ' + c.name + ' ' + c.valueStr });
  showToast(`${c.emoji} קיבלת ${c.name} ${c.valueStr}`);
  closeBonusModal(); renderBag(); updateHUD();
}
function bonusDefer(){
  // stash this exact choice-set and hand over a lucky block to open later
  if (activeBonusChoices) luckyQueue.push(activeBonusChoices);
  player.inv.item_lucky = (player.inv.item_lucky||0) + 1;
  showToast('📦 קיבלת לאקי בלוק! הצב אותו ושבור כדי לבחור מאוחר יותר');
  closeBonusModal(); renderBag();
}
function closeBonusModal(){ document.getElementById('bonusModal').classList.remove('open'); bonusModalOpen=false; activeBonusChoices=null; }
// Breaking a placed lucky block re-opens its saved 3 choices (no infinite rerolling for a wanted item).
function openLuckyBlock(savedChoices){
  stats.luckyOpened++;
  const choices = (savedChoices && savedChoices.length) ? savedChoices : generateBonusChoices(3);
  openBonusModal(choices, true);
}

/* ============ Stats panel ============ */
function toggleStats(){
  const p = document.getElementById('statsPanel');
  const show = p.style.display !== 'block';
  p.style.display = show ? 'block' : 'none';
  if (show){ document.getElementById('settingsPanel').style.display='none'; document.getElementById('bagPanel').classList.remove('open'); document.getElementById('cheatPanel').style.display='none'; renderStats(); }
}
function renderStats(){
  const rows = [
    ['👾 מפלצות שהרגת', stats.monstersKilled],
    ['🐇 חיות שהרגת', stats.animalsKilled],
    ['⛏️ בלוקים ששברת', stats.blocksDestroyed],
    ['📏 מרחק שבירה מקסימלי', (player.breakReach||2) + ' בלוקים'],
    ['❤️ חיים מקסימליים', Math.round(player.maxHealth)],
    ['🍖 אוכל מקסימלי', Math.round(player.maxHunger)],
    ['🟨 לאקי בלוקים שפתחת', stats.luckyOpened],
    ['📅 יום נוכחי', dayNum],
  ];
  document.getElementById('statsBody').innerHTML = rows.map(r=>`<div class="statRow"><span>${r[0]}</span><b>${r[1]}</b></div>`).join('');
  const ch = stats.dailyChoices;
  document.getElementById('statsChoices').innerHTML = ch.length ? ch.map(c=>`<div class="statRow"><span>יום ${c.day}</span><b>${c.label}</b></div>`).join('') : '<div class="statRow"><span>עדיין לא בחרת שדרוגים</span></div>';
}

/* ============ Texture-6 visual grain ("סאונד") + damage cracks ============ */
// Per-surface toggle for the grainy noise texture unlocked at graphics level 6.
let blockNoise = { wall:true, temple:true, floor_grass:true, floor_sand:true, floor_snow:true, floor_plains:true, bone_wall:true };
function noiseKeyForTile(type){ if(type===T.WALL) return 'wall'; if(type===T.BONE_WALL) return 'bone_wall'; if(type===T.ALTAR_FLOOR) return 'temple'; return null; }
function blockNoiseOn(type){ if (gfxLevel < 6) return false; const k = noiseKeyForTile(type); return k ? blockNoise[k] : false; }
function floorNoiseOn(b, type){ if (gfxLevel < 6) return false; if (type===T.ALTAR_FLOOR) return blockNoise.temple; if (type===T.GRASS) return blockNoise.floor_grass; if (type===T.SAND) return blockNoise.floor_sand; if (type===T.SNOW) return blockNoise.floor_snow; return false; }
// deterministic hash so grain is stable per pixel-cell (doesn't shimmer each frame)
function hash2(x,y){ let h = (x*73856093) ^ (y*19349663); h = (h ^ (h>>13)) * 1274126177; return ((h>>>0) % 1000)/1000; }
function drawGrain(x, y, w, h, color){
  ctx.save(); ctx.fillStyle = color; ctx.globalAlpha = 0.28;
  const step = 4;
  for (let gy=0; gy<h; gy+=step){ for (let gx=0; gx<w; gx+=step){ if (hash2(Math.floor(x+gx), Math.floor(y+gy)) < 0.32){ ctx.fillRect(x+gx, y+gy, 2, 2); } } }
  ctx.globalAlpha = 1; ctx.restore();
}
function drawCracks(cx, cy, frac){
  if (frac >= 0.98) return;
  const cracks = Math.min(10, Math.round((1-frac)*10));
  const crackLines = [[[-8,-6],[-2,2]],[[8,-4],[2,3]],[[-4,8],[3,-2]],[[6,7],[-1,-1]],[[-9,2],[-3,-1]],[[9,3],[3,1]],[[0,-10],[0,-2]],[[-6,-9],[-2,-4]],[[5,-8],[1,-3]],[[-2,9],[1,4]]];
  ctx.save(); ctx.strokeStyle = frac<=0.10 ? 'rgba(60,10,5,0.95)' : 'rgba(20,20,20,0.7)'; ctx.lineWidth = 1.3;
  for (let i=0; i<cracks && i<crackLines.length; i++){ const l = crackLines[i]; ctx.beginPath(); ctx.moveTo(cx+l[0][0], cy+l[0][1]); ctx.lineTo(cx+l[1][0], cy+l[1][1]); ctx.stroke(); }
  ctx.restore();
}
function drawResourceShape(t, sx, sy, tileObj){
  const cx = sx+TILE/2, cy = sy+TILE/2; ctx.save();
  if (gfxLevel === 5) { ctx.shadowColor = 'rgba(0,0,0,0.4)'; ctx.shadowBlur = 5; ctx.shadowOffsetY = 4; }
  let sway = (gfxLevel >= 4) ? Math.sin(performance.now() * 0.005 + sx * 0.02) * 2.5 : 0;

  if (t===T.TREE){
    ctx.fillStyle='rgba(0,0,0,0.18)'; ctx.beginPath(); ctx.ellipse(cx+1, cy+13, 10, 4, 0,0,Math.PI*2); ctx.fill();
    ctx.fillStyle = '#6b4423'; ctx.fillRect(cx-2.5, cy+1, 5, 13); ctx.translate(sway, 0);
    const leafG = ctx.createRadialGradient(cx-4,cy-14,2,cx,cy-8,15); leafG.addColorStop(0,'#5ea852'); leafG.addColorStop(1,'#1f5225'); ctx.fillStyle = leafG;
    ctx.beginPath(); ctx.arc(cx-7,cy-6,8,0,6.3); ctx.arc(cx+7,cy-6,8,0,6.3); ctx.arc(cx,cy-15,10,0,6.3); ctx.arc(cx,cy-6,11,0,6.3); ctx.fill();
  } else if (t===T.TRUNK) {
    ctx.fillStyle='rgba(0,0,0,0.18)'; ctx.beginPath(); ctx.ellipse(cx+1, cy+13, 8, 3, 0,0,Math.PI*2); ctx.fill();
    ctx.fillStyle = '#6b4423'; ctx.fillRect(cx-3, cy+5, 6, 9); ctx.fillStyle = '#d9a066'; ctx.beginPath(); ctx.ellipse(cx, cy+5, 3, 1.5, 0, 0, Math.PI*2); ctx.fill();
  } else if (t===T.SAPLING) {
    ctx.fillStyle = '#6b4423'; ctx.fillRect(cx-1, cy+6, 2, 6); ctx.fillStyle = '#73c745'; ctx.beginPath(); ctx.arc(cx, cy+4, 4, 0, Math.PI*2); ctx.fill();
  } else if (t===T.CROP) {
    const stage = (tileObj && tileObj.stage) || 0;
    ctx.fillStyle='rgba(0,0,0,0.12)'; ctx.beginPath(); ctx.ellipse(cx+1, cy+10, 6, 2.5, 0,0,6.3); ctx.fill();
    if (stage===0){ ctx.fillStyle='#73c745'; ctx.beginPath(); ctx.arc(cx, cy+4, 3, 0, 6.3); ctx.fill(); }
    else if (stage===1){ ctx.fillStyle='#4a8a2a'; ctx.fillRect(cx-1, cy, 2, 8); ctx.fillStyle='#73c745'; ctx.beginPath(); ctx.arc(cx, cy-1, 3.5, 0, 6.3); ctx.fill(); }
    else { ctx.fillStyle='#e2b13c'; ctx.fillRect(cx-3, sy+12, 1.5, 12); ctx.fillRect(cx, sy+8, 1.5, 16); ctx.fillRect(cx+3, sy+13, 1.5, 11);
      ctx.fillStyle='#f4d06f'; ctx.beginPath(); ctx.arc(cx-2.5, sy+12, 2.4, 0, 6.3); ctx.arc(cx, sy+8, 2.8, 0, 6.3); ctx.arc(cx+3, sy+13, 2, 0, 6.3); ctx.fill(); }
  } else if (t===T.CRAFTING_TABLE) {
    ctx.fillStyle = '#8a5a36'; ctx.fillRect(sx+5, sy+16, 4, 12); ctx.fillRect(sx+TILE-9, sy+16, 4, 12); ctx.fillStyle = '#b5835a'; ctx.fillRect(sx+2, sy+6, TILE-4, 10); ctx.fillStyle = '#7a7a7a'; ctx.fillRect(cx-3, cy-4, 6, 3);
  } else if (t===T.UPGRADED_TABLE) {
    ctx.fillStyle = '#4a2f1c'; ctx.fillRect(sx+4, sy+14, 6, 14); ctx.fillRect(sx+TILE-10, sy+14, 6, 14); 
    ctx.fillStyle = '#8a5a36'; ctx.fillRect(sx+2, sy+6, TILE-4, 10); 
    ctx.fillStyle = '#9e9e9e'; ctx.fillRect(cx-5, cy-4, 10, 4); 
    ctx.fillStyle = '#444'; ctx.fillRect(sx+4, sy+8, 4, 2); ctx.fillRect(sx+TILE-8, sy+8, 4, 2); 
  } else if (t===T.FURNACE) {
    ctx.fillStyle = '#6a6a6a'; ctx.fillRect(sx+4, sy+4, TILE-8, TILE-8);
    ctx.fillStyle = '#444'; ctx.fillRect(sx+6, sy+6, TILE-12, TILE-16); 
    ctx.fillStyle = '#222'; ctx.fillRect(cx-5, cy+4, 10, 6); 
    if (Math.random() > 0.3) { ctx.fillStyle = '#ff6a00'; ctx.fillRect(cx-3, cy+6, 6, 2); } 
  } else if (t===T.WHEAT) {
    ctx.fillStyle = '#e2b13c'; ctx.fillRect(cx-4, sy+10, 2, 14); ctx.fillRect(cx, sy+6, 2, 18); ctx.fillRect(cx+4, sy+12, 2, 12);
    ctx.fillStyle = '#f4d06f'; ctx.beginPath(); ctx.arc(cx-3, sy+10, 3, 0, 6.3); ctx.arc(cx, sy+6, 3.5, 0, 6.3); ctx.arc(cx+3, sy+12, 2.5, 0, 6.3); ctx.fill();
  } else if (t===T.PINE){
    // ground shadow, then trunk UNDER the foliage, then 3 stacked conifer tiers (bottom->top) with snow caps
    ctx.fillStyle='rgba(0,0,0,0.18)'; ctx.beginPath(); ctx.ellipse(cx+1, cy+13, 9, 4, 0,0,Math.PI*2); ctx.fill();
    ctx.fillStyle='#4a3826'; ctx.fillRect(cx-2.5, cy+6, 5, 8);
    ctx.translate(sway, 0);
    const tiers = [ {y:cy+9, w:11, h:11}, {y:cy+2, w:9, h:10}, {y:cy-5, w:7, h:10} ];
    for (const s of tiers){
      ctx.fillStyle = '#1c5233';
      ctx.beginPath(); ctx.moveTo(cx, s.y - s.h); ctx.lineTo(cx - s.w, s.y); ctx.lineTo(cx + s.w, s.y); ctx.closePath(); ctx.fill();
      // snow cap sitting on top of each tier
      ctx.fillStyle = '#eef4f8';
      ctx.beginPath(); ctx.moveTo(cx, s.y - s.h); ctx.lineTo(cx - s.w*0.42, s.y - s.h*0.5); ctx.lineTo(cx + s.w*0.42, s.y - s.h*0.5); ctx.closePath(); ctx.fill();
    }
  } else if (t===T.ROCK || t===T.COAL || t===T.IRONROCK){
    if (gfxLevel === 5) {
      if (t === T.COAL) {
        ctx.fillStyle = '#151515'; ctx.beginPath(); ctx.moveTo(cx-11, cy+8); ctx.lineTo(cx-6, cy-9); ctx.lineTo(cx+6, cy-11); ctx.lineTo(cx+12, cy+4); ctx.lineTo(cx+4, cy+9); ctx.closePath(); ctx.fill();
        ctx.strokeStyle = '#333'; ctx.lineWidth = 1.5; ctx.stroke(); ctx.fillStyle = '#fff'; ctx.fillRect(cx-4, cy-5, 2.5, 2.5);
      } else if (t === T.IRONROCK) {
        let metalGrad = ctx.createRadialGradient(cx-4, cy-4, 1, cx, cy, 12); metalGrad.addColorStop(0, '#ffbe5c'); metalGrad.addColorStop(0.6, '#d98f3a'); metalGrad.addColorStop(1, '#784305');
        ctx.fillStyle = metalGrad; ctx.beginPath(); ctx.moveTo(cx-12, cy+6); ctx.lineTo(cx-3, cy-12); ctx.lineTo(cx+8, cy-8); ctx.lineTo(cx+11, cy+7); ctx.closePath(); ctx.fill();
      } else {
        ctx.fillStyle = '#8f8f8a'; ctx.beginPath(); ctx.moveTo(cx-12, cy+9); ctx.lineTo(cx-9, cy-7); ctx.lineTo(cx, cy-12); ctx.lineTo(cx+9, cy-4); ctx.lineTo(cx+12, cy+9); ctx.closePath(); ctx.fill();
        ctx.fillStyle = '#5c5c57'; ctx.beginPath(); ctx.moveTo(cx, cy-12); ctx.lineTo(cx-2, cy+9); ctx.lineTo(cx+12, cy+9); ctx.lineTo(cx+9, cy-4); ctx.closePath(); ctx.fill();
      }
    } else {
      ctx.fillStyle= t===T.COAL?'#1e1e1e':t===T.IRONROCK?'#d98f3a':'#7a7a75'; ctx.beginPath(); ctx.moveTo(cx-10, cy+6); ctx.lineTo(cx-8, cy-6); ctx.lineTo(cx+4, cy-8); ctx.lineTo(cx+10, cy+6); ctx.closePath(); ctx.fill();
    }
  } else if (t===T.SKULL) {
    ctx.fillStyle='#e8e8e8'; ctx.fillRect(cx-5, cy-4, 10, 8); ctx.fillRect(cx-3, cy+4, 6, 3);
    ctx.fillStyle='#111'; ctx.fillRect(cx-3, cy-1, 2, 2); ctx.fillRect(cx+1, cy-1, 2, 2); ctx.fillRect(cx-1, cy+2, 2, 1);
  } else if (t===T.BUSH){
    ctx.translate(sway, 0); ctx.fillStyle='#295c2e'; ctx.beginPath(); ctx.arc(cx, cy, 8, 0, 6.3); ctx.fill();
    if(gfxLevel >= 2) { ctx.fillStyle='#c94a3d'; ctx.beginPath(); ctx.arc(cx-3, cy-2, 2, 0, 6.3); ctx.arc(cx+3, cy+2, 2, 0, 6.3); ctx.fill(); }
  } else if (t===T.CACTUS){
    if (gfxLevel === 5) { ctx.fillStyle='#1e5c2b'; ctx.fillRect(cx-3, cy-13, 6, 22); ctx.fillRect(cx-9, cy-3, 6, 3); ctx.fillRect(cx-9, cy-8, 3, 6); ctx.fillRect(cx+3, cy-7, 6, 3); ctx.fillRect(cx+6, cy-12, 3, 6); ctx.fillStyle='#fff'; ctx.fillRect(cx-1, cy-9, 1, 1); ctx.fillRect(cx+1, cy+1, 1, 1); } else { ctx.fillStyle='#2f7a3f'; ctx.fillRect(cx-3, cy-13, 6, 22); }
  } else if (t===T.WALL){
    const frac = tileObj ? Math.max(0, tileObj.hp)/((tileObj.maxHp)||tileHP(T.WALL)) : 1;
    // last 10% of durability -> the wall glows red as a warning it's about to give
    let base = '#616161';
    if (frac <= 0.10) base = '#b03a2e'; else if (frac <= 0.35) base = '#8a5a4a';
    ctx.fillStyle=base; ctx.fillRect(sx+2, sy+2, TILE-4, TILE-4);
    if (blockNoiseOn(T.WALL)) drawGrain(sx+2, sy+2, TILE-4, TILE-4, frac<=0.10?'#5a1a12':'#3a3a3a');
    ctx.strokeStyle= frac<=0.10 ? '#6a1a12' : '#3a3a3a'; ctx.strokeRect(sx+2, sy+2, TILE-4, TILE-4);
    drawCracks(cx, cy, frac);
  }
  else if (t===T.WALL_THORN) {
    const frac = tileObj ? Math.max(0, tileObj.hp)/((tileObj.maxHp)||tileHP(T.WALL_THORN)) : 1;
    ctx.fillStyle= frac<=0.10 ? '#5a3a1a' : '#3a5a2a'; ctx.fillRect(sx+3, sy+3, TILE-6, TILE-6); ctx.strokeStyle='#1e3a15'; ctx.strokeRect(sx+3, sy+3, TILE-6, TILE-6);
    ctx.fillStyle='#8fae4a';
    const spikes=[[cx-8,cy-8],[cx+8,cy-8],[cx-8,cy+8],[cx+8,cy+8],[cx,cy]];
    spikes.forEach(([px,py])=>{ ctx.beginPath(); ctx.moveTo(px,py-5); ctx.lineTo(px-3,py+3); ctx.lineTo(px+3,py+3); ctx.closePath(); ctx.fill(); });
    drawCracks(cx, cy, frac);
  }
  else if (t===T.BONE_WALL) {
    const frac = tileObj ? Math.max(0, tileObj.hp)/((tileObj.maxHp)||tileHP(T.BONE_WALL)) : 1;
    ctx.fillStyle= frac<=0.10 ? '#c9857a' : '#e8e0d0'; ctx.fillRect(sx+2, sy+2, TILE-4, TILE-4);
    ctx.strokeStyle='#a89e88'; ctx.strokeRect(sx+2, sy+2, TILE-4, TILE-4);
    // stacked bone segments
    ctx.strokeStyle='#b8ac90'; ctx.lineWidth=2;
    for(let by=-6; by<=6; by+=6){ ctx.beginPath(); ctx.moveTo(cx-9, cy+by); ctx.lineTo(cx+9, cy+by); ctx.stroke(); ctx.fillStyle='#f2ece0'; ctx.beginPath(); ctx.arc(cx-9, cy+by, 2.4, 0, 6.3); ctx.arc(cx+9, cy+by, 2.4, 0, 6.3); ctx.fill(); }
    if (blockNoiseOn(T.BONE_WALL)) drawGrain(sx+2, sy+2, TILE-4, TILE-4, '#c8bfa8');
    drawCracks(cx, cy, frac);
  }
  else if (t===T.LUCKY) {
    // precise-yellow lucky block with black corners and a "?" in the middle
    ctx.fillStyle='#f5c518'; ctx.fillRect(sx+2, sy+2, TILE-4, TILE-4);
    ctx.fillStyle='#111'; const cs=6;
    ctx.fillRect(sx+2, sy+2, cs, cs); ctx.fillRect(sx+TILE-2-cs, sy+2, cs, cs);
    ctx.fillRect(sx+2, sy+TILE-2-cs, cs, cs); ctx.fillRect(sx+TILE-2-cs, sy+TILE-2-cs, cs, cs);
    ctx.fillStyle='#111'; ctx.font='bold 16px "Courier New", monospace'; ctx.textAlign='center'; ctx.textBaseline='middle'; ctx.fillText('?', cx, cy+1);
    ctx.textAlign='start'; ctx.textBaseline='alphabetic';
    if (gfxLevel>=4){ ctx.strokeStyle='rgba(255,255,255,0.5)'; ctx.lineWidth=1; ctx.strokeRect(sx+3, sy+3, TILE-6, TILE-6); }
  }
  else if (t===T.CAMPFIRE){ ctx.fillStyle='#5a3a1e'; ctx.fillRect(sx+6, sy+20, TILE-12, 6); ctx.fillStyle='#ff6a00'; ctx.beginPath(); ctx.arc(cx, cy+4, 8, 0, 6.3); ctx.fill(); }
  else if (t===T.TABLET) {
    ctx.fillStyle='rgba(0,0,0,0.2)'; ctx.beginPath(); ctx.ellipse(cx+1, cy+13, 10, 4, 0,0,6.3); ctx.fill();
    ctx.fillStyle='#6a6a66'; ctx.fillRect(cx-8, cy-13, 16, 24);
    ctx.fillStyle='#8a8a84'; ctx.beginPath(); ctx.moveTo(cx-8,cy-13); ctx.lineTo(cx,cy-18); ctx.lineTo(cx+8,cy-13); ctx.closePath(); ctx.fill();
    ctx.strokeStyle='#4a4a44'; ctx.lineWidth=1;
    for(let i=0;i<4;i++){ ctx.beginPath(); ctx.moveTo(cx-5, cy-8+i*5); ctx.lineTo(cx+5, cy-8+i*5); ctx.stroke(); }
  } else if (t===T.CRYSTAL_ORE) {
    const maxHp = (tileObj&&tileObj.maxHp)||10; const frac = tileObj ? Math.max(0,tileObj.hp)/maxHp : 1;
    ctx.fillStyle='rgba(0,0,0,0.2)'; ctx.beginPath(); ctx.ellipse(cx+1, cy+8, 12, 4, 0,0,6.3); ctx.fill();
    ctx.fillStyle='#5c5c57'; ctx.beginPath(); ctx.moveTo(cx-12,cy+7); ctx.lineTo(cx-8,cy-8); ctx.lineTo(cx,cy-12); ctx.lineTo(cx+9,cy-6); ctx.lineTo(cx+12,cy+7); ctx.closePath(); ctx.fill();
    const crystalG = ctx.createRadialGradient(cx-2,cy-3,1,cx,cy,9);
    crystalG.addColorStop(0,'#c9a0ff'); crystalG.addColorStop(0.6,'#8a4fe0'); crystalG.addColorStop(1,'#4a2090');
    ctx.fillStyle = crystalG;
    ctx.beginPath(); ctx.moveTo(cx,cy-9); ctx.lineTo(cx+5,cy-1); ctx.lineTo(cx,cy+8); ctx.lineTo(cx-5,cy-1); ctx.closePath(); ctx.fill();
    // crack overlay grows as hp drops (visible progress every ~3 min via hp ticking down)
    const cracks = Math.round((1-frac)*10);
    ctx.strokeStyle='rgba(20,10,30,0.8)'; ctx.lineWidth=1;
    const crackLines = [[[-8,-6],[-2,2]],[[8,-4],[2,3]],[[-4,8],[3,-2]],[[6,7],[-1,-1]],[[-9,2],[-3,-1]],[[9,3],[3,1]],[[0,-10],[0,-2]],[[-6,-9],[-2,-4]],[[5,-8],[1,-3]],[[-2,9],[1,4]]];
    for(let i=0;i<cracks && i<crackLines.length;i++){ const l=crackLines[i]; ctx.beginPath(); ctx.moveTo(cx+l[0][0],cy+l[0][1]); ctx.lineTo(cx+l[1][0],cy+l[1][1]); ctx.stroke(); }
  } else if (t===T.CRYSTAL_DEVICE) {
    ctx.fillStyle='rgba(0,0,0,0.25)'; ctx.beginPath(); ctx.ellipse(cx+1, cy+11, 14, 5, 0,0,6.3); ctx.fill();
    ctx.fillStyle='#6a6a66'; ctx.beginPath(); ctx.arc(cx,cy+4,13,0,6.3); ctx.fill();
    if (gfxLevel>=2){
      const decos = [[-10,4],[10,4],[-8,-6],[8,-6],[0,10]];
      decos.forEach(([ox,oy],i)=>{ ctx.fillStyle = i%2===0 ? '#8f8f8a':'#d98f3a'; ctx.beginPath(); ctx.arc(cx+ox,cy+oy+4,2.6,0,6.3); ctx.fill(); });
    }
    const active = crystalActivated;
    const pulse = active ? (0.7+Math.sin(performance.now()*0.004)*0.3) : 0.4;
    const baseColor = eternalNightActive && !active ? '#e04a3d' : '#8a4fe0';
    const glowG = ctx.createRadialGradient(cx,cy-2,1,cx,cy,active?16:8);
    glowG.addColorStop(0, active ? baseColor : '#5a3a80'); glowG.addColorStop(1, 'rgba(0,0,0,0)');
    if (active){ ctx.globalAlpha = pulse; ctx.fillStyle = glowG; ctx.beginPath(); ctx.arc(cx,cy-2,16,0,6.3); ctx.fill(); ctx.globalAlpha = 1; }
    const crystalG = ctx.createRadialGradient(cx-1,cy-4,1,cx,cy-2,9);
    crystalG.addColorStop(0, active ? '#ffffff' : '#c9a0ff'); crystalG.addColorStop(0.6, baseColor); crystalG.addColorStop(1,'#3a1a70');
    ctx.fillStyle = crystalG;
    ctx.beginPath(); ctx.moveTo(cx,cy-11); ctx.lineTo(cx+5,cy-2); ctx.lineTo(cx,cy+7); ctx.lineTo(cx-5,cy-2); ctx.closePath(); ctx.fill();
  } else if (t===T.PLACED_TORCH) {
    ctx.fillStyle='#6a4a2a'; ctx.fillRect(cx-2, cy-2, 4, 16);
    ctx.fillStyle='#ff9a3d'; ctx.beginPath(); ctx.ellipse(cx, cy-10, 6, 9, 0,0,6.3); ctx.fill();
    ctx.fillStyle='#ffd77a'; ctx.beginPath(); ctx.ellipse(cx, cy-9, 3, 5, 0,0,6.3); ctx.fill();
  }
  ctx.restore();
}

function draw(){
  ctx.clearRect(0,0,W,H); ctx.save(); ctx.translate(W/2, H/2); ctx.scale(gameZoom, gameZoom); ctx.translate(-player.x, -player.y);
  const visibleW = W / gameZoom; const visibleH = H / gameZoom;
  const startX=Math.max(0,Math.floor((player.x - visibleW/2)/TILE)), startY=Math.max(0,Math.floor((player.y - visibleH/2)/TILE));
  const endX=Math.min(MAPW,startX+Math.ceil(visibleW/TILE)+2), endY=Math.min(MAPH,startY+Math.ceil(visibleH/TILE)+2);

  for(let y=startY;y<endY;y++) for(let x=startX;x<endX;x++){
    const t = world[y][x]; const sx=x*TILE, sy=y*TILE; const b = biomeAt(x, y);
    ctx.fillStyle = groundColor(b, t.type); ctx.fillRect(sx,sy,TILE,TILE);
    if (floorNoiseOn(b, t.type)){ const gc = t.type===T.ALTAR_FLOOR ? '#565656' : t.type===T.SAND ? '#b89a55' : t.type===T.SNOW ? '#c4cdd6' : '#2a5a24'; drawGrain(sx, sy, TILE, TILE, gc); }
    if (gfxLevel === 5) { if (t.type === T.GRASS) { ctx.fillStyle = '#2e692a'; ctx.fillRect(sx + 5, sy + 6, 2, 4); } else if (t.type === T.SAND) { ctx.fillStyle = '#c7b06b'; ctx.fillRect(sx + 2, sy + 14, 14, 1.5); } }
    if (t.type === T.WATER && gfxLevel >= 4) { ctx.fillStyle = 'rgba(255,255,255,0.08)'; ctx.fillRect(sx + 4 + Math.sin(performance.now() * 0.003 + sx)*2, sy + 10, 8, 1.5); }
    if (t.type!==T.GRASS && t.type!==T.WATER && t.type!==T.SAND && t.type!==T.SNOW && t.type!==T.ALTAR_FLOOR){ drawResourceShape(t.type, sx, sy, t); }
  }

  for (const c of chests){ ctx.fillStyle='#7a5a2a'; ctx.fillRect(c.x-11, c.y-8, 22, 16); }
  for (const p of particles){ ctx.globalAlpha=Math.max(0,p.life/0.6); ctx.fillStyle = p.color; ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 6.3); ctx.fill(); ctx.globalAlpha=1; }
  for (const p of projectiles){ ctx.fillStyle='#fff'; ctx.fillRect(p.x-2, p.y-2, 4, 4); }
  for (const p of enemyProjectiles){ ctx.fillStyle='#8a2f1a'; ctx.fillRect(p.x-2, p.y-2, 4, 4); }
  for (const a of animals){ ctx.save(); ctx.translate(a.x, a.y); let hop = Math.abs(Math.sin(performance.now() * 0.008)) * 3.5; ctx.fillStyle = 'rgba(0,0,0,0.15)'; ctx.beginPath(); ctx.ellipse(0, 6, 6, 2.5, 0, 0, 6.3); ctx.fill(); ctx.fillStyle = '#f5f5f5'; ctx.beginPath(); ctx.arc(0, -2 - hop, 6, 0, 6.3); ctx.fill(); ctx.beginPath(); ctx.arc(4, -6 - hop, 4.5, 0, 6.3); ctx.fill(); ctx.fillRect(1, -14 - hop, 1.8, 6); ctx.fillRect(4, -14 - hop, 1.8, 6); if (gfxLevel === 5) { ctx.fillStyle = '#ffb3b3'; ctx.fillRect(1.5, -12 - hop, 0.8, 4); ctx.fillStyle = '#ffffff'; ctx.beginPath(); ctx.arc(-6, -2 - hop, 2.2, 0, 6.3); ctx.fill(); } ctx.fillStyle = '#ff9999'; ctx.fillRect(6, -6 - hop, 1.5, 1.5); if (a.isSpider && getNightFactor() > 0.4){ ctx.fillStyle='#ff2b2b'; ctx.shadowColor='#ff2b2b'; ctx.shadowBlur=6; ctx.fillRect(2.5, -7 - hop, 1.8, 1.8); ctx.fillRect(5.5, -7 - hop, 1.8, 1.8); ctx.shadowBlur=0; } ctx.restore(); }
  const enemyColor = {zombie:'#3c7a4b', scorpion:'#b5743b', wolf:'#3a3a3a', siberian_wolf:'#d5e2eb'};
  for (const e of enemies){
    ctx.save(); ctx.translate(e.x, e.y); let bob = Math.sin(performance.now() * 0.008 + e.x) * 2.5; let isRight = (e.facing === 'right');
    ctx.fillStyle = 'rgba(0,0,0,0.2)'; ctx.beginPath(); ctx.ellipse(0, 7, 8, 3, 0, 0, 6.3); ctx.fill();
    if (e.kind === 'zombie') { ctx.fillStyle = '#3c7a4b'; ctx.beginPath(); ctx.ellipse(0, -2 + bob, 7, 9, 0, 0, 6.3); ctx.fill(); ctx.fillStyle = '#2c5a35'; ctx.fillRect(isRight ? 3 : -9, -3 + bob, 6, 3.5); ctx.fillStyle = '#ffea00'; if (isRight) { ctx.fillRect(2, -6 + bob, 1.5, 1.5); ctx.fillRect(5, -6 + bob, 1.5, 1.5); } else { ctx.fillRect(-5, -6 + bob, 1.5, 1.5); ctx.fillRect(-2, -6 + bob, 1.5, 1.5); } }
    else if (e.kind === 'wolf' || e.kind === 'siberian_wolf') { ctx.fillStyle = enemyColor[e.kind]; ctx.beginPath(); ctx.ellipse(0, bob, 10, 6, 0, 0, 6.3); ctx.fill(); let hX = isRight ? 7 : -7; ctx.beginPath(); ctx.arc(hX, -3 + bob, 4, 0, 6.3); ctx.fill(); ctx.beginPath(); ctx.moveTo(hX - 1, -6 + bob); ctx.lineTo(hX, -11 + bob); ctx.lineTo(hX + 1, -6 + bob); ctx.fill(); ctx.fillStyle = e.kind === 'wolf' ? '#e74c3c' : '#00d2ff'; ctx.fillRect(isRight ? hX + 1 : hX - 2, -4 + bob, 1.5, 1.5); }
    else if (e.kind === 'scorpion') { ctx.fillStyle = '#b5743b'; ctx.beginPath(); ctx.ellipse(0, 1, 9, 5, 0, 0, 6.3); ctx.fill(); ctx.strokeStyle = '#b5743b'; ctx.lineWidth = 2.5; ctx.beginPath(); if (isRight) { ctx.arc(-5, -4, 6, 0, Math.PI, true); ctx.stroke(); ctx.fillStyle = '#733f15'; ctx.fillRect(-5, -10, 2.5, 2.5); } else { ctx.arc(5, -4, 6, 0, Math.PI, true); ctx.stroke(); ctx.fillStyle = '#733f15'; ctx.fillRect(5, -10, 2.5, 2.5); } }
    else if (e.kind === 'archer') { ctx.fillStyle = '#4a3a6a'; ctx.beginPath(); ctx.ellipse(0, -2+bob, 7, 9, 0, 0, 6.3); ctx.fill(); ctx.strokeStyle='#c9a0ff'; ctx.lineWidth=2; ctx.beginPath(); ctx.arc(isRight?5:-5, -2+bob, 6, -1, 1); ctx.stroke(); ctx.fillStyle='#ffe94a'; ctx.fillRect(-2,-6+bob,1.6,1.6); ctx.fillRect(2,-6+bob,1.6,1.6); }
    else if (e.kind === 'wraith') { ctx.globalAlpha = 0.55; const wg = ctx.createRadialGradient(0,-4+bob,1,0,-2+bob,11); wg.addColorStop(0,'#c9c9ff'); wg.addColorStop(1,'#5a5a9a'); ctx.fillStyle = wg; ctx.beginPath(); ctx.arc(0,-4+bob,8,Math.PI,0); ctx.lineTo(6,6+bob); ctx.lineTo(2,2+bob); ctx.lineTo(0,7+bob); ctx.lineTo(-2,2+bob); ctx.lineTo(-6,6+bob); ctx.closePath(); ctx.fill(); ctx.globalAlpha=1; ctx.fillStyle='#1a1a2a'; ctx.beginPath(); ctx.arc(-2.5,-5+bob,1.3,0,6.3); ctx.arc(2.5,-5+bob,1.3,0,6.3); ctx.fill(); }
    else if (e.kind === 'brute') { ctx.fillStyle = '#5a3a2a'; ctx.beginPath(); ctx.ellipse(0, bob, 13, 12, 0, 0, 6.3); ctx.fill(); ctx.fillStyle='#3a2418'; ctx.fillRect(-10,-8+bob,6,6); ctx.fillRect(4,-8+bob,6,6); ctx.fillStyle='#ffea00'; ctx.fillRect(isRight?4:-9,-3+bob,2,2); ctx.fillRect(isRight?8:-5,-3+bob,2,2); }
    else if (e.kind === 'spider') { ctx.strokeStyle='#1a1a1a'; ctx.lineWidth=2; for(let s=-1;s<=1;s+=2){ for(let li=0; li<3; li++){ ctx.beginPath(); ctx.moveTo(0, bob); ctx.lineTo(s*(9+li*2), bob - 6 + li*6); ctx.stroke(); } } ctx.fillStyle='#2a2a2e'; ctx.beginPath(); ctx.ellipse(0, bob, 7, 6, 0, 0, 6.3); ctx.fill(); ctx.beginPath(); ctx.arc(0, -4+bob, 4, 0, 6.3); ctx.fill(); ctx.fillStyle='#ff3030'; ctx.fillRect(-2.5,-5+bob,1.8,1.8); ctx.fillRect(1,-5+bob,1.8,1.8); }
    ctx.fillStyle='#222'; ctx.fillRect(-14, -18 + bob, 28, 3); ctx.fillStyle='#c94a3d'; ctx.fillRect(-14, -18 + bob, 28*(e.hp/e.maxHp), 3); ctx.restore();
  }

  // GHOST PREVIEW RENDER SYSTEM
  if (player.placingItem) {
      let p = frontPos();
      let tx = Math.floor(p.fx / TILE);
      let ty = Math.floor(p.fy / TILE);
      if (ty >= 0 && ty < MAPH && tx >= 0 && tx < MAPW) {
          let t = world[ty][tx];
          let ptx = Math.floor(player.x/TILE), pty = Math.floor(player.y/TILE);
          let blocked = isSolid(t) || (isWater(t) && player.placingItem.type==='plant') || (tx === ptx && ty === pty);
          ctx.fillStyle = blocked ? "rgba(201, 74, 61, 0.45)" : "rgba(47, 122, 234, 0.4)";
          ctx.fillRect(tx * TILE, ty * TILE, TILE, TILE);
          ctx.strokeStyle = blocked ? "#c94a3d" : "#2f7aea";
          ctx.lineWidth = 2;
          ctx.strokeRect(tx * TILE, ty * TILE, TILE, TILE);
      }
  }

  // DRAW AIMING LINE EXPLICITLY ON PLAYER
  if (gfxLevel >= 3) {
      let dirX = 0, dirY = 0;
      if (joyActive && (Math.abs(joyDX)>0.1 || Math.abs(joyDY)>0.1)) {
          let mag = Math.hypot(joyDX, joyDY); dirX = joyDX / mag; dirY = joyDY / mag;
      } else {
          if (player.facing.includes('right')) dirX = 1; if (player.facing.includes('left')) dirX = -1;
          if (player.facing.includes('down')) dirY = 1; if (player.facing.includes('up')) dirY = -1;
          if (dirX !== 0 && dirY !== 0) { dirX *= 0.707; dirY *= 0.707; } else if (dirX===0 && dirY===0) { dirY=1; }
      }
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)'; ctx.lineWidth = 2; ctx.setLineDash([4, 4]);
      ctx.beginPath(); 
      ctx.moveTo(player.x, player.y); 
      ctx.lineTo(player.x + dirX * (1.8 * TILE), player.y + dirY * (1.8 * TILE)); 
      ctx.stroke(); ctx.setLineDash([]);
      
      ctx.fillStyle = 'rgba(255, 255, 255, 0.6)'; 
      ctx.beginPath(); 
      ctx.arc(player.x + dirX * (1.8 * TILE), player.y + dirY * (1.8 * TILE), 3, 0, 6.3); 
      ctx.fill();
  }

  ctx.save(); ctx.translate(player.x, player.y);

  let pBob = player.isWalking ? Math.sin(player.walkFrame) * 2 : 0; let pFeet = player.isWalking ? Math.sin(player.walkFrame) * 4 : 0;
  ctx.fillStyle = 'rgba(0,0,0,0.2)'; ctx.beginPath(); ctx.ellipse(0, 9, 8, 3, 0, 0, 6.3); ctx.fill();
  
  let df = player.facing;
  if (gfxLevel < 3 && df.includes('-')) df = df.split('-')[1];

  ctx.fillStyle = '#2f5f8a'; ctx.fillRect(-5, -4 + pBob, 10, 10);
  ctx.fillStyle = '#ffd1a9'; ctx.beginPath(); ctx.arc(0, -9 + pBob, 5, 0, 6.3); ctx.fill();

  if (df === 'down') { 
      ctx.fillStyle = '#3a2212'; ctx.fillRect(-4 + pFeet, 6, 3, 3); ctx.fillRect(1 - pFeet, 6, 3, 3); 
      ctx.fillStyle = '#111'; ctx.fillRect(-2, -10 + pBob, 1.5, 1.5); ctx.fillRect(1, -10 + pBob, 1.5, 1.5); 
      ctx.fillStyle = '#5a3a1e'; ctx.beginPath(); ctx.arc(0, -10 + pBob, 5.2, 3.14, 0); ctx.fill(); 
  }
  else if (df === 'up') { 
      ctx.fillStyle = '#3a2212'; ctx.fillRect(-4 + pFeet, 6, 3, 3); ctx.fillRect(1 - pFeet, 6, 3, 3); 
      ctx.fillStyle = '#543b2b'; ctx.fillRect(-4, -2 + pBob, 8, 6);
      ctx.fillStyle = '#5a3a1e'; ctx.beginPath(); ctx.arc(0, -9.5 + pBob, 5.5, 0, 6.3); ctx.fill(); 
  }
  else if (df === 'left') { 
      ctx.fillStyle = '#3a2212'; ctx.fillRect(-3 + pFeet, 6, 3, 3); ctx.fillRect(-1 - pFeet, 6, 3, 3); 
      ctx.fillStyle = '#111'; ctx.fillRect(-3, -10 + pBob, 1.5, 1.5); 
      ctx.fillStyle = '#5a3a1e'; ctx.beginPath(); ctx.arc(-0.5, -10 + pBob, 5.2, 3.14, 0); ctx.fill(); 
  }
  else if (df === 'right') { 
      ctx.fillStyle = '#3a2212'; ctx.fillRect(-2 + pFeet, 6, 3, 3); ctx.fillRect(0 - pFeet, 6, 3, 3); 
      ctx.fillStyle = '#111'; ctx.fillRect(2, -10 + pBob, 1.5, 1.5); 
      ctx.fillStyle = '#5a3a1e'; ctx.beginPath(); ctx.arc(0.5, -10 + pBob, 5.2, 3.14, 0); ctx.fill(); 
  }
  else if (df === 'up-left') {
      ctx.fillStyle = '#3a2212'; ctx.fillRect(-3 + pFeet, 6, 3, 3); ctx.fillRect(1 - pFeet, 6, 3, 3); 
      ctx.fillStyle = '#543b2b'; ctx.fillRect(-2, -2 + pBob, 6, 6); 
      ctx.fillStyle = '#5a3a1e'; ctx.beginPath(); ctx.arc(1, -9.5 + pBob, 5.5, 0, 6.3); ctx.fill(); 
  }
  else if (df === 'up-right') {
      ctx.fillStyle = '#3a2212'; ctx.fillRect(-4 + pFeet, 6, 3, 3); ctx.fillRect(0 - pFeet, 6, 3, 3); 
      ctx.fillStyle = '#543b2b'; ctx.fillRect(-4, -2 + pBob, 6, 6); 
      ctx.fillStyle = '#5a3a1e'; ctx.beginPath(); ctx.arc(-1, -9.5 + pBob, 5.5, 0, 6.3); ctx.fill(); 
  }
  else if (df === 'down-right') {
      ctx.fillStyle = '#3a2212'; ctx.fillRect(-3 + pFeet, 6, 3, 3); ctx.fillRect(1 - pFeet, 6, 3, 3); 
      ctx.fillStyle = '#111'; ctx.fillRect(0, -10 + pBob, 1.5, 1.5); ctx.fillRect(3, -10 + pBob, 1.5, 1.5); 
      ctx.fillStyle = '#5a3a1e'; ctx.beginPath(); ctx.arc(1, -10 + pBob, 5.2, 3.14, 0); ctx.fill(); 
  }
  else if (df === 'down-left') {
      ctx.fillStyle = '#3a2212'; ctx.fillRect(-4 + pFeet, 6, 3, 3); ctx.fillRect(0 - pFeet, 6, 3, 3); 
      ctx.fillStyle = '#111'; ctx.fillRect(-4, -10 + pBob, 1.5, 1.5); ctx.fillRect(-1, -10 + pBob, 1.5, 1.5); 
      ctx.fillStyle = '#5a3a1e'; ctx.beginPath(); ctx.arc(-1, -10 + pBob, 5.2, 3.14, 0); ctx.fill(); 
  }
  ctx.restore();

  if (gfxLevel === 5 && Math.random() < 0.08) { for(let y=startY; y<endY; y++) for(let x=startX; x<endX; x++) { if((world[y][x].type === T.CAMPFIRE || world[y][x].type === T.FURNACE) && Math.random() < 0.2) spawnParticle(x*TILE + 16 + (Math.random()*16-8), y*TILE + 16, '#ffaa00', Math.random()*2+1); } }
  ctx.restore();

  /* Night darkness overlay */
  const nf = getNightFactor();
  if (nf > 0) {
    if (lightCanvas.width !== W || lightCanvas.height !== H) { lightCanvas.width = W; lightCanvas.height = H; }
    lightCtx.fillStyle = `rgba(0, 0, 0, ${nf * nightDarkness})`; lightCtx.fillRect(0, 0, W, H); lightCtx.globalCompositeOperation = 'destination-out';
    let baseRadius = (player.inv.torch && player.inv.torch > 0) ? torchLightRadius : BASE_TORCHLESS_RADIUS; let radius = baseRadius * gameZoom;
    let grad = lightCtx.createRadialGradient(W/2, H/2, 5 * gameZoom, W/2, H/2, radius); grad.addColorStop(0, 'rgba(0,0,0,1)'); grad.addColorStop(1, 'rgba(0,0,0,0)');
    lightCtx.fillStyle = grad; lightCtx.beginPath(); lightCtx.arc(W/2, H/2, radius, 0, 6.3); lightCtx.fill();
    for(let y=startY; y<endY; y++) for(let x=startX; x<endX; x++) {
      if(world[y] && world[y][x] && (world[y][x].type === T.CAMPFIRE || world[y][x].type === T.FURNACE || world[y][x].type === T.PLACED_TORCH)) {
        let lightScale = world[y][x].type === T.PLACED_TORCH ? 0.75 : 1;
        let scrX = (x*TILE + 16 - player.x) * gameZoom + W/2, scrY = (y*TILE + 16 - player.y) * gameZoom + H/2; let fireRadius = 115 * gameZoom * lightScale;
        let fireGrad = lightCtx.createRadialGradient(scrX, scrY, 10 * gameZoom, scrX, scrY, fireRadius); fireGrad.addColorStop(0, 'rgba(0,0,0,1)'); fireGrad.addColorStop(1, 'rgba(0,0,0,0)');
        lightCtx.fillStyle = fireGrad; lightCtx.beginPath(); lightCtx.arc(scrX, scrY, fireRadius, 0, 6.3); lightCtx.fill();
      }
    }
    lightCtx.globalCompositeOperation = 'source-over'; ctx.drawImage(lightCanvas, 0, 0);
  }
  if (gfxLevel === 5) { let vignGrad = ctx.createRadialGradient(W/2, H/2, Math.min(W, H) * 0.4, W/2, H/2, Math.max(W, H) * 0.75); vignGrad.addColorStop(0, 'rgba(0,0,0,0)'); vignGrad.addColorStop(1, 'rgba(0,0,0,0.5)'); ctx.fillStyle = vignGrad; ctx.fillRect(0, 0, W, H); }
  drawMinimap();
}

const mmCanvas = document.getElementById('minimap'); const mmCtx = mmCanvas.getContext('2d');
function drawMinimap(){ mmCtx.clearRect(0,0,90,90); const scale = 90/(28*TILE); const originX = player.x - 14*TILE, originY = player.y - 14*TILE; const sx0 = Math.max(0, Math.floor(originX/TILE)), sy0=Math.max(0, Math.floor(originY/TILE)); const sx1 = Math.min(MAPW, sx0+28), sy1=Math.min(MAPH, sy0+28); for (let y=sy0;y<sy1;y+=1) for (let x=sx0;x<sx1;x+=1){ const b = biomeAt(x,y); mmCtx.fillStyle = groundColor(b,world[y][x].type); mmCtx.fillRect((x*TILE-originX)*scale, (y*TILE-originY)*scale, TILE*scale+1, TILE*scale+1); } mmCtx.fillStyle = '#c94a3d'; mmCtx.beginPath(); mmCtx.arc((player.x-originX)*scale,(player.y-originY)*scale,3,0,7); mmCtx.fill(); }

function updateHUD(){ document.querySelector('#health .bar-fill').style.width = Math.max(0,(player.health/player.maxHealth)*100)+'%'; document.querySelector('#hunger .bar-fill').style.width = Math.max(0,(player.hunger/player.maxHunger)*100)+'%'; document.getElementById('dayNum').textContent = dayNum; const nf = getNightFactor(); let label = '☀️ יום'; if (eternalNightActive && !crystalActivated) label = '🌑 לילה נצחי'; else if (nf>0.66) label = '🌙 לילה'; else if (nf>0.05) label = '🌆 דמדומים'; document.getElementById('timeOfDay').textContent = label; }
function renderBag(){ 
    const wr = document.getElementById('weaponRow'); wr.innerHTML=''; 
    const weapons = [{id:'sword',icon:'🗡️'},{id:'iron_sword',icon:'⚔️'},{id:'bow',icon:'🏹'}];
    weapons.forEach(w=>{ 
        if ((w.id==='bow' && !player.equipment.bow) || (w.id==='iron_sword' && !player.equipment.iron_sword) || (w.id==='sword' && player.equipment.iron_sword)) return; 
        const d = document.createElement('div'); d.className = 'weaponIcon' + (player.activeWeapon===w.id ? ' active':''); d.textContent = w.icon; d.onclick = ()=>{ player.activeWeapon=w.id; renderBag(); }; wr.appendChild(d); 
    }); 
    
    const resList = document.getElementById('resList'); resList.innerHTML=''; 
    Object.keys(names).forEach(k=>{ 
        if(player.inv[k]!==undefined && player.inv[k]>0){
          const row = document.createElement('div'); row.className='resRow'; 
          let eatBtn = ''; if((k==='berry' || k==='meat' || k==='bread' || k==='cooked_meat' || k==='fruit_salad') && (player.inv[k]||0) > 0) eatBtn = `<button onclick="eatItem('${k}')" style="background:#4a6b3a; border:none; color:white; padding:3px 7px; border-radius:4px; font-size:10px; margin-left:6px; cursor:pointer;">אכל</button>`; 
          let placeBtn = '';
          if (k.startsWith('item_')) { const baseId = k.replace('item_',''); placeBtn = `<button onclick="placeItemFromBag('${baseId}')" style="background:#2f7aea; border:none; color:white; padding:3px 7px; border-radius:4px; font-size:10px; margin-left:6px; cursor:pointer;">📍 הצב</button>`; }
          if (k === 'torch') { placeBtn = `<button onclick="placeTorchFromBag()" style="background:#2f7aea; border:none; color:white; padding:3px 7px; border-radius:4px; font-size:10px; margin-left:6px; cursor:pointer;">📍 הצב</button>`; }
          if (k === 'reinforcement') { placeBtn = `<button onclick="selectReinforcement()" style="background:#6a6a8a; border:none; color:white; padding:3px 7px; border-radius:4px; font-size:10px; margin-left:6px; cursor:pointer;">⛓️ חזק</button>`; }
          row.innerHTML = `<span>${names[k]}</span><span>${eatBtn}${placeBtn} ${player.inv[k]||0}</span>`; resList.appendChild(row); 
        }
    }); 
    
    const list = document.getElementById('craftList'); list.innerHTML=''; 
    const stations = getNearbyStations();
    
    const statusDiv = document.createElement('div'); statusDiv.style.fontSize = '11px'; statusDiv.style.color = '#e8a898'; statusDiv.style.marginBottom = '8px'; statusDiv.style.padding = '4px'; statusDiv.style.background = 'rgba(0,0,0,0.2)'; statusDiv.style.borderRadius = '4px'; 
    if (stations.furnace) { statusDiv.textContent = '♨️ תנור פעיל: התכה ואפייה'; statusDiv.style.color = '#ffaa00'; }
    else if (stations.upgraded) { statusDiv.textContent = '⚙️ שולחן משודרג פעיל: ציוד מתקדם ותנורים'; statusDiv.style.color = '#8a5a36'; }
    else if (stations.table) { statusDiv.textContent = '🛠️ שולחן עבודה פעיל: ציוד בסיסי'; statusDiv.style.color = '#73c745'; }
    else { statusDiv.textContent = '🎒 תיק אישי (מתכונים בסיסיים בלבד)'; }
    list.appendChild(statusDiv); 
    
    RECIPES.forEach(r=>{ 
        if (r.station === 'table' && !stations.table) return;
        if (r.station === 'upgraded' && !stations.upgraded) return;
        if (r.station === 'furnace' && !stations.furnace) return;
        if (r.station === 'campfire' && !stations.campfire) return;

        const ok = canCraft(r); 
        const div = document.createElement('div'); div.className = 'craftItem' + (ok ? '' : ' disabled'); if(!ok) div.style.opacity = '0.5'; 
        const reqStr = Object.entries(r.cost).map(([k,v])=>{ const emoji = names[k] ? names[k].split(' ')[0] : ''; return `${v}${emoji}`; }).join(' '); 
        div.innerHTML = `<div style="display:flex; justify-content:space-between; width:100%;"><span>${r.name}</span><span style="color:#b0a888; font-size:10px;">עלות: ${reqStr}</span></div>`; 
        div.onclick = () => craft(r); list.appendChild(div); 
    }); 
}
function showToast(msg){ const t = document.getElementById('toast'); t.textContent = msg; t.style.opacity=1; clearTimeout(t._to); t._to = setTimeout(()=>{ t.style.opacity=0; }, 1500); }

let lastTime = performance.now(); function loop(now){ const dt = Math.min(0.05, (now-lastTime)/1000); lastTime = now; update(dt); draw(); requestAnimationFrame(loop); }
// Build a valid world behind the start screen (gameStarted stays false so it's paused) and wait for the player's choice.
gameMode = 'crystal'; initGame(); gameStarted = false; requestAnimationFrame(loop);
</script>
</body>
</html>
