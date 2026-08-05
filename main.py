<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<title>שרידות</title>
<!-- Installable as a home-screen app (full-screen, no browser bars) once served from a real URL -->
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="שרידות">
<meta name="theme-color" content="#0a0d10">
<link rel="apple-touch-icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Crect width='180' height='180' fill='%233a7d34'/%3E%3Ctext x='90' y='128' font-size='120' text-anchor='middle'%3E%F0%9F%8C%8D%3C/text%3E%3C/svg%3E">
<link rel="manifest" href="data:application/json,%7B%22name%22%3A%22%D7%A9%D7%A8%D7%99%D7%93%D7%95%D7%AA%22%2C%22short_name%22%3A%22%D7%A9%D7%A8%D7%99%D7%93%D7%95%D7%AA%22%2C%22display%22%3A%22fullscreen%22%2C%22orientation%22%3A%22portrait%22%2C%22background_color%22%3A%22%230a0d10%22%2C%22theme_color%22%3A%22%230a0d10%22%2C%22start_url%22%3A%22.%22%7D">
<!-- PeerJS: enables short-code co-op over the internet/hotspot. Loaded async; game works fine without it (single-player). -->
<script async src="https://unpkg.com/peerjs@1.5.4/dist/peerjs.min.js"></script>
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
  #skinRow { display:flex; align-items:center; gap:7px; margin-bottom:16px; flex-wrap:wrap; justify-content:center; }
  .skinSwatch { width:26px; height:26px; border-radius:50%; border:2px solid rgba(255,255,255,0.25); cursor:pointer; transition:transform 0.1s; }
  .skinSwatch.sel { border-color:#fff; transform:scale(1.2); }
  .dayPick { padding:8px 10px; background:#5a2a2a; color:#fff; border:1px solid #c94a3d; border-radius:6px; font-family:inherit; font-size:12px; cursor:pointer; }
  .dayPick:active { transform:scale(0.92); background:#7a3030; }
  .worldCard { width:min(88vw, 340px); background:rgba(20,22,28,0.92); border:2px solid #4a4230; border-radius:12px; padding:14px 16px; margin-bottom:12px; cursor:pointer; transition:transform 0.1s, border-color 0.2s; }
  .worldCard:active { transform:scale(0.97); }
  .worldCard:hover { border-color:#d9c98a; }
  .worldCard .wt { font-size:16px; color:#e8e0c8; margin-bottom:4px; }
  .worldCard .wd { font-size:11px; color:#9a927a; line-height:1.5; }
  .worldCard.locked { border-color:#5a3a3a; }
  #wsCodeWrap { display:flex; gap:6px; width:min(88vw,340px); margin-top:4px; }
  #wsCodeWrap input { flex:1; background:#222; color:#fff; border:1px solid #4a4230; padding:8px; border-radius:6px; font-size:16px; font-family:inherit; }
  #wsCodeWrap button { padding:8px 14px; background:#5a4a2a; color:#fff; border:none; border-radius:6px; cursor:pointer; font-family:inherit; }
  .sharedTypeCard { width:min(88vw,340px); }
  .sharedTypeCard.sel { border-color:#73c745; box-shadow:0 0 0 2px rgba(115,199,69,0.3); }
  .sharedBtn { flex:1; padding:12px 4px; background:#2f5a8a; color:#fff; border:none; border-radius:8px; font-family:inherit; font-size:12px; cursor:pointer; }
  .sharedBack { margin-top:12px; padding:8px 18px; background:#3a3226; color:#d9c98a; border:1px solid #6a5a3a; border-radius:8px; font-family:inherit; cursor:pointer; }
  .saveRow { display:flex; align-items:center; gap:6px; background:rgba(20,22,28,0.9); border:1px solid #4a4230; border-radius:8px; padding:8px 10px; margin-bottom:6px; font-size:12px; }
  .saveRow .sName { flex:1; color:#e8e0c8; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .saveRow button { padding:6px 10px; border:none; border-radius:5px; font-family:inherit; font-size:11px; cursor:pointer; }
  .saveRow .loadB { background:#3a5a2a; color:#fff; } .saveRow .delB { background:#5a3a3a; color:#fff; }

  /* ---- Net (P2P) connection panel ---- */
  #netPanel { position:absolute; inset:0; background:rgba(0,0,0,0.82); display:none; flex-direction:column; align-items:center; justify-content:center; z-index:70; pointer-events:auto; padding:16px; }
  #netPanel.open { display:flex; }
  #netPanel .bx { position:relative; background:rgba(18,20,26,0.98); border:2px solid #2f7aea; border-radius:14px; padding:18px 16px; width:min(94vw, 400px); max-height:88vh; overflow-y:auto; }
  #netPanel h2 { color:#4a9aff; font-size:18px; text-align:center; margin-bottom:2px; }
  #netPanel .bsub { color:#9a927a; font-size:11px; text-align:center; margin-bottom:12px; }
  #netPanel .netLbl { display:block; font-size:11px; color:#b0a888; margin:10px 0 4px; }
  #netPanel textarea { width:100%; background:#111; color:#8fe08f; border:1px solid #4a4230; border-radius:6px; padding:8px; font-family:monospace; font-size:10px; resize:vertical; word-break:break-all; }
  #netHostCode { font-size:44px; font-weight:bold; text-align:center; color:#4a9aff; letter-spacing:8px; padding:14px; background:#0d1018; border-radius:10px; user-select:text; -webkit-user-select:text; width:100%; box-sizing:border-box; border:none; font-family:inherit; }
  #netJoinCode { width:100%; font-size:30px; text-align:center; letter-spacing:6px; background:#111; color:#8fe08f; border:1px solid #4a4230; border-radius:8px; padding:12px; user-select:text; -webkit-user-select:text; }
  #netPanel .netBtn { width:100%; padding:9px; margin-top:6px; background:#2f5a8a; color:#fff; border:none; border-radius:6px; font-family:inherit; font-size:12px; cursor:pointer; }
  #netX { position:absolute; top:8px; left:12px; color:#c94a3d; font-size:22px; cursor:pointer; line-height:1; }
  /* remote players are drawn on the game canvas; name tags reuse toast styling */

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
  #connBanner { position:absolute; top:8px; left:50%; transform:translateX(-50%); background:rgba(180,60,40,0.92); color:#fff; padding:6px 16px; border-radius:8px; font-size:12px; z-index:45; display:none; pointer-events:none; box-shadow:0 4px 10px rgba(0,0,0,0.4); }
  #connBanner.show { display:block; }
  #bossBanner { position:absolute; top:80px; left:50%; transform:translateX(-50%); background:rgba(150,20,20,0.95); color:#fff; padding:10px 22px; border-radius:10px; font-size:16px; font-weight:bold; z-index:46; display:none; pointer-events:none; box-shadow:0 0 24px rgba(200,40,40,0.7); text-align:center; }
  #bossBanner.show { display:block; animation:bossPulse 0.8s infinite alternate; }
  @keyframes bossPulse { from{ transform:translateX(-50%) scale(1);} to{ transform:translateX(-50%) scale(1.06);} }
  #bossHp { position:absolute; top:8px; left:50%; transform:translateX(-50%); width:min(70vw,320px); display:none; z-index:44; pointer-events:none; text-align:center; }
  #bossHp.show { display:block; }
  #bossHpLabel { color:#ffcaca; font-size:11px; margin-bottom:2px; text-shadow:0 1px 2px #000; }
  #bossHpBar { height:12px; background:#2a1010; border:1px solid #6a2020; border-radius:6px; overflow:hidden; }
  #bossHpFill { height:100%; width:100%; background:linear-gradient(90deg,#c94a3d,#ff7a5a); transition:width 0.2s; }
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
    <div id="dayinfo">יום <span id="dayNum">1</span> | <span id="timeOfDay">☀️ יום</span> <span id="safeIndicator" style="display:none; color:#8fe08f;">🏡</span></div>
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
    <h3>🛠️ כלים</h3>
    <div class="weaponRow" id="toolRow"></div>
    <h3>📦 חומרים</h3>
    <div id="resList"></div>
    <h3>🛠️ קראפטינג</h3>
    <div id="craftList"></div>
  </div>

  <div id="settingsPanel">
    <h3>⚙️ הגדרות משחק</h3>
    <div class="settingRow"><label>☀️ תאורת מסך (למשחק בשמש):</label><input type="range" min="0.8" max="1.8" step="0.1" value="1.0" oninput="changeAppBrightness(this.value)"></div>
    <div class="settingRow"><label>🕹️ סוג רשת תנועה:</label><select id="gridMode" onchange="changeGridMode(this.value)"><option value="smooth">🏃 תנועה חופשית</option><option value="quarter">📐 רבע בלוק</option><option value="half">📏 חצי בלוק</option><option value="full">🧱 בלוק מלא</option></select></div>
    <div class="settingRow"><label>🎨 רמת יופי וגרפיקה (1-6):</label><input type="range" min="1" max="6" step="1" value="1" oninput="changeGraphics(this.value)"></div>
    <div class="settingRow"><label>🕶️ מבט:</label><button onclick="toggleView3D()" style="width:100%; padding:9px; background:#2a4a6a; color:#fff; border:1px solid #4a9aff; border-radius:6px; font-family:inherit; font-size:12px; cursor:pointer;">החלף בין תלת־מימד (גוף ראשון) למבט מלמעלה</button></div>
    <div class="settingRow" id="noiseSection" style="display:none; border-top:1px dashed #4a4230; padding-top:8px;">
      <label>🎛️ טקסטורה 6 — רעש (סאונד) לבלוקים:</label>
      <div class="noiseToggleRow"><span>הכל</span><input type="checkbox" id="noiseAll" checked onchange="setAllNoise(this.checked)"></div>
      <div id="noiseList"></div>
    </div>
    <div class="settingRow"><label>📱 גודל כללי לממשק:</label><input type="range" min="1.0" max="2.0" step="0.1" value="1.2" oninput="changeUIScale(this.value)"></div>
    <div class="settingRow"><label>🔎 מרחק מצלמה:</label><input type="range" min="0.6" max="2.6" step="0.1" value="1.5" oninput="changeZoom(this.value)"></div>
    <div class="settingRow"><label>🕹️ גודל ג'ויסטיק תנועה:</label><input type="range" min="80" max="260" step="5" value="120" oninput="changeJoySize(this.value)"></div>
    <div class="settingRow"><label>🔴 גודל לחצן תקיפה (⚔️):</label><input type="range" min="65" max="180" step="5" value="80" oninput="changeActionSize(this.value)"></div>
    <div class="settingRow" style="flex-direction:row; justify-content:space-between; align-items:center;"><label>🏷️ הצג שמות של שחקנים אחרים</label><input type="checkbox" checked onchange="showPlayerNames=this.checked"></div>
    <div style="display:flex; gap:6px; margin-top:6px;">
      <button onclick="saveWorld()" style="flex:1; padding:8px; background:#3a5a2a; color:#fff; border:none; border-radius:6px; font-family:inherit; cursor:pointer;">💾 שמור עולם</button>
      <button onclick="showWorldSelect()" style="flex:1; padding:8px; background:#5a4a2a; color:#fff; border:none; border-radius:6px; font-family:inherit; cursor:pointer;">🏠 תפריט ראשי</button>
    </div>
    <button onclick="toggleSettings()" style="width:100%; padding:8px; background:#4a3a2a; color:#fff; border:none; border-radius:6px; margin-top:6px; font-family:inherit; cursor:pointer;">סגור הגדרות</button>

    <div class="settingRow" style="margin-top:10px; border-top:1px dashed #4a4230; padding-top:10px;">
      <label>🔑 קוד מפתח</label>
      <div style="display:flex; gap:6px;"><input type="text" id="cheatCodeInput" inputmode="numeric" style="flex:1;"><button onclick="tryCheatCode()" style="padding:6px 12px; background:#5a3a3a; color:#fff; border:none; border-radius:4px; cursor:pointer;">פתח</button></div>
    </div>
  </div>

  <div id="cheatPanel">
    <h3>🔑 תפריט מפתח</h3>
    <div class="toggleRow"><span>👾 מפלצות פעילות</span><input type="checkbox" id="cheatEnemiesToggle" checked onchange="cheatToggleEnemies(this.checked)"></div>
    <div class="toggleRow"><span>🛡️ מצב אלוהים (חסין)</span><input type="checkbox" id="cheatGodToggle" onchange="cheatToggleGod(this.checked)"></div>
    <div class="toggleRow"><span>🌙 כל לילה: לאקי בלוק + כל הכוחות</span><input type="checkbox" id="cheatNightlyToggle" onchange="cheatToggleNightly(this.checked)"></div>
    <div class="toggleRow"><span>🤝 אפשר צ׳יטים לאורחים (במשחק משותף)</span><input type="checkbox" id="cheatGuestToggle" onchange="cheatToggleGuestCheats(this.checked)"></div>

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
  <div id="connBanner">🔄 החיבור נפל — מתחבר מחדש...</div>
  <div id="bossBanner"></div>
  <div id="bossHp"><div id="bossHpLabel">👑 בוס</div><div id="bossHpBar"><div id="bossHpFill"></div></div></div>

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

  <div id="msg"><h2 id="msgTitle" style="color:#c94a3d; margin-bottom:10px;">מתת!</h2><p id="msgBody">שרדת <span id="survivedDays">0</span> ימים</p><button onclick="restart()">התחל מחדש</button><button onclick="showWorldSelect()" style="background:#5a4a2a; margin-right:8px;">🏠 תפריט ראשי</button></div>

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
    <div style="margin:0 0 10px; display:flex; align-items:center; justify-content:center; gap:8px;">
      <span style="font-size:12px; color:#9a927a;">🙂 השם שלך:</span>
      <input id="playerNameInput" maxlength="14" placeholder="הקלד שם" oninput="setPlayerName(this.value)" style="width:150px; padding:7px 9px; border-radius:7px; border:1px solid #4a4230; background:#0d1018; color:#fff; font-family:inherit; font-size:14px; text-align:center;">
    </div>
    <div id="skinRow">
      <span style="font-size:11px; color:#9a927a; margin-left:6px;">👕 צבע:</span>
      <div class="skinSwatch sel" style="background:#2f5f8a" onclick="setSkin('#2f5f8a', this)"></div>
      <div class="skinSwatch" style="background:#c94a3d" onclick="setSkin('#c94a3d', this)"></div>
      <div class="skinSwatch" style="background:#3a8a4a" onclick="setSkin('#3a8a4a', this)"></div>
      <div class="skinSwatch" style="background:#8a4fe0" onclick="setSkin('#8a4fe0', this)"></div>
      <div class="skinSwatch" style="background:#d69a3e" onclick="setSkin('#d69a3e', this)"></div>
      <div class="skinSwatch" style="background:#e0e0e0" onclick="setSkin('#e0e0e0', this)"></div>
      <div class="skinSwatch" style="background:#e05fa8" onclick="setSkin('#e05fa8', this)"></div>
    </div>
    <div id="wsMain">
      <div class="worldCard" onclick="startWorld('crystal')">
        <div class="wt">💎 עולם הקריסטל</div>
        <div class="wd">מצא ובנה את הקריסטל לפני היום החמישי כדי לעצור את הלילה הנצחי.</div>
      </div>
      <div class="worldCard" onclick="startWorld('survival')">
        <div class="wt">🌙 הישרדות רגילה</div>
        <div class="wd">בלי קריסטל ובלי לילה נצחי — רק לילות רגילים. פשוט לשרוד ולבנות כמה שרוצים.</div>
      </div>
      <div class="worldCard" style="cursor:default; border-color:#4a9aff;">
        <div class="wt">🕶️ תלת־מימד — גוף ראשון</div>
        <div class="wd">רואים את העולם מהעיניים שלך: עצים, מפלצות, חיות, חברים והכול. הג׳ויסטיק מסובב ימינה/שמאלה והולך קדימה/אחורה. בחר עולם:</div>
        <div style="display:flex; gap:6px; margin-top:10px; justify-content:center; flex-wrap:wrap;">
          <button onclick="start3D('survival')" class="dayPick" style="background:#2a4a6a; border-color:#4a9aff;">🌙 הישרדות</button>
          <button onclick="start3D('crystal')" class="dayPick" style="background:#2a4a6a; border-color:#4a9aff;">💎 קריסטל</button>
          <button onclick="start3D('challenge')" class="dayPick" style="background:#2a4a6a; border-color:#4a9aff;">⚔️ אתגר</button>
        </div>
      </div>
      <div class="worldCard" style="cursor:default;">
        <div class="wt">⚔️ אתגר — לילה נצחי</div>
        <div class="wd">בלי קריסטל. בחר באיזה יום יתחיל הלילה הנצחי — ואז המשחק מתחיל:</div>
        <div style="display:flex; gap:6px; margin-top:10px; justify-content:center; flex-wrap:wrap;">
          <button onclick="startChallenge(1)" class="dayPick">יום 1</button>
          <button onclick="startChallenge(2)" class="dayPick">יום 2</button>
          <button onclick="startChallenge(3)" class="dayPick">יום 3</button>
          <button onclick="startChallenge(4)" class="dayPick">יום 4</button>
          <button onclick="startChallenge(5)" class="dayPick">יום 5</button>
        </div>
      </div>
      <div class="worldCard" onclick="openSharedMenu()">
        <div class="wt">🌐 עולם משותף (עם חברים)</div>
        <div class="wd">שחק יחד עם המשפחה/חברים דרך קוד קצר. אפשר גם לשחק לבד.</div>
      </div>
      <div class="worldCard locked" onclick="askWorldCode()">
        <div class="wt">🔒 עולם ניסיון (דורש קוד)</div>
        <div class="wd">עולם בדיקה עם כל הבלוקים והחומרים מוכנים, כדי לבדוק באגים במהירות. הזן קוד סודי.</div>
      </div>
      <div id="wsCodeWrap" style="display:none;">
        <input type="text" id="wsCodeInput" inputmode="numeric" placeholder="קוד סודי">
        <button onclick="submitWorldCode()">פתח</button>
      </div>
      <div id="savesSection" style="display:none;">
        <div class="sub" style="margin-top:18px;">📂 עולמות שמורים</div>
        <div id="savesList" style="width:min(88vw,340px);"></div>
        <div style="width:min(88vw,340px); margin-top:14px; border-top:1px solid #4a4230; padding-top:12px;">
          <div class="sub" style="margin:0 0 8px;">🔑 קוד שמירה (עובד גם דרך Shortcut)</div>
          <div style="display:flex; gap:6px; margin-bottom:8px;">
            <button onclick="setSaveCodeStyle('emoji'); makeSaveCode();" style="flex:1; padding:8px; background:#5a3a6a; color:#fff; border:none; border-radius:6px; font-family:inherit; font-size:11px; cursor:pointer;">😀 קוד אימוג׳ים</button>
            <button onclick="setSaveCodeStyle('letters'); makeSaveCode();" style="flex:1; padding:8px; background:#3a4a6a; color:#fff; border:none; border-radius:6px; font-family:inherit; font-size:11px; cursor:pointer;">🔤 קוד אותיות</button>
          </div>
          <div style="display:flex; gap:6px; margin-bottom:10px;">
            <button onclick="makeSaveCode()" style="flex:1; padding:9px; background:#3a5a2a; color:#fff; border:none; border-radius:6px; font-family:inherit; font-size:12px; cursor:pointer;">📤 צור קוד שמירה</button>
          </div>
          <div id="saveCodeBox" style="display:none; margin-bottom:12px;">
            <textarea id="saveCodeArea" rows="3" dir="ltr" onclick="this.select()" style="width:100%; box-sizing:border-box; font-size:10px; background:#0d1018; color:#8fe0a0; border:1px solid #4a4230; border-radius:6px; padding:6px; direction:ltr; unicode-bidi:plaintext; text-align:left;"></textarea>
            <button onclick="copySaveCode()" style="width:100%; margin-top:5px; padding:8px; background:#2f5a8a; color:#fff; border:none; border-radius:6px; font-family:inherit; font-size:12px; cursor:pointer;">📋 העתק</button>
          </div>
          <textarea id="loadCodeArea" rows="3" dir="ltr" placeholder="הדבק כאן קוד שמירה כדי לטעון עולם" style="width:100%; box-sizing:border-box; font-size:10px; background:#0d1018; color:#fff; border:1px solid #4a4230; border-radius:6px; padding:6px; direction:ltr; unicode-bidi:plaintext; text-align:left;"></textarea>
          <button onclick="loadFromCode()" style="width:100%; margin-top:5px; padding:9px; background:#5a4a2a; color:#fff; border:none; border-radius:6px; font-family:inherit; font-size:12px; cursor:pointer;">📥 טען מקוד שמירה</button>
        </div>
      </div>
    </div>

    <div id="sharedMenu" style="display:none; flex-direction:column; align-items:center;">
      <div class="sub">🌐 עולם משותף — בחר סוג עולם</div>
      <div class="worldCard sharedTypeCard sel" id="sharedCrystalCard" onclick="setSharedMode('crystal')">
        <div class="wt">💎 קריסטל</div><div class="wd">משחקים יחד עם מטרת הקריסטל.</div>
      </div>
      <div class="worldCard sharedTypeCard" id="sharedSurvivalCard" onclick="setSharedMode('survival')">
        <div class="wt">🌙 הישרדות רגילה</div><div class="wd">לילות רגילים, בלי לילה נצחי — פשוט לשרוד יחד.</div>
      </div>
      <div class="worldCard sharedTypeCard" id="sharedChallengeCard" onclick="setSharedMode('challenge')">
        <div class="wt">⚔️ אתגר — לילה נצחי</div><div class="wd">בלי קריסטל, לילה נצחי מיום 2. קשה מאוד — יחד תשרדו יותר!</div>
      </div>
      <div style="display:flex; gap:8px; width:min(88vw,340px); margin-top:6px;">
        <button class="sharedBtn" onclick="sharedSolo()">🎮 לבד</button>
        <button class="sharedBtn" onclick="sharedHost()">📡 פתח לחברים</button>
        <button class="sharedBtn" onclick="sharedJoin()">🔗 הצטרף</button>
      </div>
      <button class="sharedBack" onclick="closeSharedMenu()">← חזור</button>
    </div>
  </div>

  <div id="netPanel">
    <div class="bx">
      <span id="netX" onclick="closeNetPanel()">✕</span>
      <h2 id="netTitle">📡 חיבור</h2>
      <div class="bsub" id="netStatus">ממתין...</div>
      <div id="netHostView" style="display:none;">
        <div class="netLbl">הקוד שלך — מסור אותו לחבר שיצטרף:</div>
        <input id="netHostCode" readonly value="----" onclick="this.select()">
        <button class="netBtn" onclick="copyHostCode()">📋 העתק קוד</button>
        <div class="bsub" style="margin-top:10px;">החבר בוחר "עולם משותף → 🔗 הצטרף" ומקליד את הקוד. צריך שלשניכם יהיה אינטרנט (נקודה חמה סלולרית עובדת).</div>
      </div>
      <div id="netJoinView" style="display:none;">
        <div class="netLbl">הכנס את הקוד שקיבלת מהמארח:</div>
        <input id="netJoinCode" inputmode="numeric" placeholder="למשל 1234">
        <button class="netBtn" onclick="netDoJoin()">🔗 התחבר</button>
      </div>
    </div>
  </div>
</div>

<script>
const canvas = document.getElementById('game');
let ctx = canvas.getContext('2d');   // 'let' so the 3D view can temporarily redirect drawing into an offscreen sprite canvas
const screenCtx = ctx;
// Run any existing 2D drawing code into an offscreen canvas, so the 3D view reuses the SAME artwork.
function renderToCanvas(w, h, fn){
  const c = document.createElement('canvas'); c.width=w; c.height=h;
  const oc = c.getContext('2d'); const saved = ctx;
  ctx = oc; try{ fn(oc); } catch(e){} finally { ctx = saved; }
  return c;
}
let W, H;
function resizeCanvas(){
  // Use the canvas's OWN rendered box so the backing store always matches what's on screen.
  // (On mobile the viewport height changes when the toolbar shows/hides without firing 'resize';
  //  if the backing store goes stale the CSS stretches it and circles render as ellipses.)
  const rect = canvas.getBoundingClientRect();
  if (rect.width < 2 || rect.height < 2) return;
  const dpr = window.devicePixelRatio || 1;
  const bw = Math.round(rect.width * dpr), bh = Math.round(rect.height * dpr);
  if (canvas.width !== bw || canvas.height !== bh){ canvas.width = bw; canvas.height = bh; }
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  W = rect.width; H = rect.height;
}
// keep the backing store in sync with the real display size every frame (cheap: just a measure + compare)
function syncCanvasSize(){ const rect = canvas.getBoundingClientRect(); if (rect.width>1 && (Math.abs(rect.width-W)>0.5 || Math.abs(rect.height-H)>0.5)) resizeCanvas(); }
window.addEventListener('resize', resizeCanvas);
if (window.visualViewport){ window.visualViewport.addEventListener('resize', resizeCanvas); window.visualViewport.addEventListener('scroll', resizeCanvas); }
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
  // In co-op, guests can't use the secret code to hand themselves items unless the host allows it.
  if (net.active && !net.isHost && !guestCheatsAllowed){ showToast('🔒 המארח חסם שימוש בקוד סודי לאורחים'); document.getElementById('cheatCodeInput').value=''; return; }
  if (val === CHEAT_CODE){
    document.getElementById('cheatCodeInput').value='';
    document.getElementById('settingsPanel').style.display='none';
    document.getElementById('cheatPanel').style.display='block';
    showToast('תפריט מפתח נפתח 🔑');
  } else if (val === '2020'){
    document.getElementById('cheatCodeInput').value='';
    const d = prompt('כמה ימים עד הלילה הנצחי? (נוכחי: '+userEternalDay+')', String(userEternalDay));
    const parsed = parseInt(d);
    if (!isNaN(parsed) && parsed >= 1){ userEternalDay = parsed; if(gameMode==='crystal'||gameMode==='test') eternalNightDay = parsed; showToast('🔑 כמות הימים עודכנה ל-'+parsed); }
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
function cheatToggleGuestCheats(checked){ guestCheatsAllowed = checked; if(net.active && net.isHost) netSend({ t:'perm', cheats:checked }); showToast(checked ? '🤝 אורחים יכולים להשתמש בצ׳יטים' : '🔒 צ׳יטים חסומים לאורחים'); }
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
// gentle rising three-note chime when two plants crossbreed into a new species
function sfxCrossbreed(){ beep(523,0.10,'sine',0.06); setTimeout(()=>beep(659,0.10,'sine',0.06),90); setTimeout(()=>beep(784,0.14,'sine',0.07),180); }
// soft magical sip when drinking a potion
function sfxPotion(){ beep(440,0.09,'triangle',0.07); setTimeout(()=>beep(880,0.12,'sine',0.06),80); }

let keys = {};
window.addEventListener('keydown', e => { keys[e.key.toLowerCase()] = true; ensureAudio(); if (fishing && (e.key===' '||e.key==='Spacebar')) tryFishHook(); }); window.addEventListener('keyup', e => { keys[e.key.toLowerCase()] = false; });

// Tap-to-build: while placing, tap anywhere on the map (within reach) to drop a block right there.
let tapTarget = null;
function buildFromScreen(clientX, clientY){
  if (!player.placingItem) return false;
  const rect = canvas.getBoundingClientRect();
  const wx = (clientX - rect.left - W/2)/gameZoom + player.x;
  const wy = (clientY - rect.top  - H/2)/gameZoom + player.y;
  if (Math.hypot(wx-player.x, wy-player.y) > TILE*4.5){ showToast('רחוק מדי — התקרב כדי לבנות שם'); return false; }
  tapTarget = { tx: Math.floor(wx/TILE), ty: Math.floor(wy/TILE) };
  tryInteract();
  tapTarget = null;
  return true;
}
canvas.addEventListener('touchstart', e=>{ ensureAudio(); if(fishing){ tryFishHook(); e.preventDefault(); return; } if(!player.placingItem) return; const t=e.changedTouches[0]; if(buildFromScreen(t.clientX, t.clientY)) e.preventDefault(); }, {passive:false});
canvas.addEventListener('mousedown', e=>{ if(!player.placingItem) return; buildFromScreen(e.clientX, e.clientY); });
let joyActive=false, joyDX=0, joyDY=0, joyTouchId=null; const joyZone = document.getElementById('joyZone'); const joyStick = document.getElementById('joyStick'); let JOY_R = 48;
function joyStart(e){ ensureAudio(); const t = e.changedTouches?e.changedTouches[0]:e; joyTouchId = e.changedTouches?t.identifier:'mouse'; joyActive=true; joyMove(e); }
function joyMove(e){ if(!joyActive) return; let t; if (e.changedTouches){ t = Array.from(e.changedTouches).find(tt=>tt.identifier===joyTouchId); if(!t) return; } else t = e; const rect = joyZone.getBoundingClientRect(); const cx = rect.left+rect.width/2, cy = rect.top+rect.height/2; let dx = t.clientX-cx, dy = t.clientY-cy; const dist = Math.hypot(dx,dy); if (dist > JOY_R){ dx = dx/dist*JOY_R; dy = dy/dist*JOY_R; } joyStick.style.transform = `translate(calc(-50% + ${dx}px), calc(-50% + ${dy}px))`; joyDX = dx/JOY_R; joyDY = dy/JOY_R; }
function joyEnd(){ joyActive=false; joyDX=0; joyDY=0; joyTouchId=null; joyStick.style.transform='translate(-50%,-50%)'; }
joyZone.addEventListener('touchstart', e=>{e.preventDefault(); joyStart(e);}, {passive:false}); joyZone.addEventListener('touchmove', e=>{e.preventDefault(); joyMove(e);}, {passive:false}); joyZone.addEventListener('touchend', e=>{e.preventDefault(); joyEnd();}, {passive:false}); joyZone.addEventListener('touchcancel', e=>{e.preventDefault(); joyEnd();}, {passive:false});
let actionHeld = false; const actionBtn = document.getElementById('actionBtn'); actionBtn.addEventListener('touchstart', e=>{e.preventDefault(); ensureAudio(); if(fishing){ tryFishHook(); return; } actionHeld=true;}, {passive:false}); actionBtn.addEventListener('touchend', e=>{e.preventDefault(); actionHeld=false;}, {passive:false});
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

const T = { GRASS:0, TREE:1, ROCK:2, COAL:3, IRONROCK:4, WATER:5, BUSH:6, SAND:7, CACTUS:8, SNOW:9, PINE:10, WALL:11, CAMPFIRE:12, TRUNK:13, CRAFTING_TABLE:14, SAPLING:15, SKULL:16, UPGRADED_TABLE:17, FURNACE:18, WHEAT:19, CROP:20, ALTAR_FLOOR:21, TABLET:22, CRYSTAL_ORE:23, CRYSTAL_DEVICE:24, PLACED_TORCH:25, WALL_THORN:26, BONE_WALL:27, LUCKY:28, CAVE_IN:29, CAVE_UP:30, CAVE_CRYSTAL:31, BEEHIVE:32, GARDEN_TABLE:33, CAVE_WALL:34, CAVE_FLOOR:35 };
// Crossbreeding species tree (Cookie-Clicker style). Plant seeds -> wheat.
// When a plant FINISHES growing it checks its neighbours ONCE; a matching pair of
// different mature plants may sprout a new species in a free tile (each with its own chance).
// All plants are drawn on the canvas (no emojis) so a big field stays smooth.
const PLANT_SPECIES = {
  wheat:       { color:'#e2b13c', tier:0, product:'wheat' },
  clover:      { color:'#3aa35a', tier:1, product:'clover' },
  sunflower:   { color:'#f2c94c', tier:1, product:'sunflower' },
  herb:        { color:'#4a9a3a', tier:2, product:'herb' },
  poppy:       { color:'#e0473a', tier:2, product:'poppy' },
  bluebell:    { color:'#5b7ce0', tier:2, product:'bluebell' },
  goldenrod:   { color:'#f0b429', tier:3, product:'goldenrod' },
  glowcap:     { color:'#e05a6a', tier:3, product:'glowcap' },
  nightshade:  { color:'#7a4bd0', tier:3, product:'nightshade' },
  crystalbloom:{ color:'#57d6e0', tier:4, product:'crystalbloom' },
  emberlily:   { color:'#ff7a2a', tier:4, product:'emberlily' },
  moonflower:  { color:'#eaf0ff', tier:5, product:'moonflower' }
};
// Mutation recipes: an unordered pair of adjacent mature species -> possible offspring (each with a chance).
// No species ever breeds into MORE of itself, so nothing can carpet the map.
function pairKey(a,b){ return a<b ? a+'|'+b : b+'|'+a; }
const CROSS = {
  'wheat|wheat':        [{sp:'clover', chance:0.12}, {sp:'sunflower', chance:0.12}],
  'clover|clover':      [{sp:'herb', chance:0.11}],
  'sunflower|sunflower':[{sp:'poppy', chance:0.11}],
  'clover|sunflower':   [{sp:'bluebell', chance:0.10}],
  'herb|poppy':         [{sp:'glowcap', chance:0.06}],
  'poppy|sunflower':    [{sp:'goldenrod', chance:0.07}],
  'bluebell|herb':      [{sp:'nightshade', chance:0.06}],
  'bluebell|glowcap':   [{sp:'crystalbloom', chance:0.04}],
  'goldenrod|poppy':    [{sp:'emberlily', chance:0.04}],
  'crystalbloom|nightshade':[{sp:'moonflower', chance:0.03}]
};
const BIOME = { FOREST:'forest', SNOW:'snow', DESERT:'desert', PLAINS:'plains' };
function biomeAt(x,y){ const nx = x/MAPW, ny = y/MAPH; if (ny < 0.45 && nx < 0.5) return BIOME.FOREST; if (ny < 0.45 && nx >= 0.5) return BIOME.SNOW; if (ny >= 0.45 && nx < 0.5) return BIOME.DESERT; return BIOME.PLAINS; }

let world;
function tileHP(t){
  if (t===T.TREE||t===T.PINE) return 3; if (t===T.ROCK||t===T.COAL) return 4; if (t===T.IRONROCK) return 6;
  if (t===T.BUSH||t===T.SKULL||t===T.WHEAT) return 1; if (t===T.CACTUS) return 2; if (t===T.WALL) return 15; if (t===T.CAMPFIRE) return 5; 
  if (t===T.TRUNK) return 2; if (t===T.CRAFTING_TABLE) return 4; if (t===T.SAPLING) return 1; if(t===T.UPGRADED_TABLE) return 6; if(t===T.FURNACE) return 8; if(t===T.CROP) return 1;
  if (t===T.TABLET) return 999999; if (t===T.CRYSTAL_ORE) return 10; if (t===T.CRYSTAL_DEVICE) return 40; if (t===T.PLACED_TORCH) return 3; if (t===T.WALL_THORN) return 20; if (t===T.BONE_WALL) return 22; if (t===T.LUCKY) return 2;
  if (t===T.CAVE_IN||t===T.CAVE_UP) return 999999; if (t===T.CAVE_CRYSTAL) return 8; if (t===T.BEEHIVE) return 3; if (t===T.GARDEN_TABLE) return 5;
  if (t===T.CAVE_WALL) return 8; if (t===T.CAVE_FLOOR) return 0; return 0;
}
// How many monster hits it takes to destroy each built item (separate from the small player-mining hp).
function enemyHitsFor(type){
  if (type===T.WALL) return 200;
  if (type===T.BONE_WALL) return 250;
  if (type===T.WALL_THORN) return 150;
  return 50; // furnace, crafting table, upgraded table, campfire
}
const REINFORCE_SHIELD = 100; // each iron reinforcement adds a 100-hit grey ring around the item
// Seeded PRNG (mulberry32) so a whole surface world can be rebuilt from one small number.
// That's what makes the "tiny save code" possible: we store the seed + only the tiles you changed.
let worldSeed = 0; let _rng = 0;
function seedRng(s){ _rng = (s>>>0) || 1; }
function rng(){ _rng |= 0; _rng = (_rng + 0x6D2B79F5) | 0; let t = Math.imul(_rng ^ (_rng>>>15), 1 | _rng); t = (t + Math.imul(t ^ (t>>>7), 61 | t)) ^ t; return ((t ^ (t>>>14)) >>> 0) / 4294967296; }
// Pure world builder: identical output for the same (seed, hasCrystal) — no globals, no Math.random.
function buildBaseWorld(seed, hasCrystal){
  seedRng(seed);
  const w = []; const riverX = Math.floor(MAPW*0.5);
  for(let y=0;y<MAPH;y++){
    w[y] = [];
    for(let x=0;x<MAPW;x++){
      const edge = x<2||y<2||x>MAPW-3||y>MAPH-3; const nearRiver = Math.abs(x - (riverX + Math.sin(y*0.15)*4)) < 1.6;
      const lakeDX = x-(MAPW*0.72), lakeDY = y-(MAPH*0.78); const inLake = Math.sqrt(lakeDX*lakeDX+lakeDY*lakeDY) < 6;
      if (edge || nearRiver || inLake){ w[y][x] = {type:T.WATER, hp:0, timer:0}; continue; }
      const b = biomeAt(x,y); const n = rng(); let tile = T.GRASS;
      if (b===BIOME.FOREST){ if (n<0.14) tile=T.TREE; else if (n<0.18) tile=T.COAL; else if (n<0.21) tile=T.ROCK; else if (n<0.23) tile=T.IRONROCK; else if (n<0.26) tile=T.BUSH; else if (n<0.29) tile=T.WHEAT; }
      else if (b===BIOME.SNOW){ tile = T.SNOW; if (n<0.12) tile=T.PINE; else if (n<0.155) tile=T.IRONROCK; else if (n<0.18) tile=T.ROCK; }
      else if (b===BIOME.DESERT){ tile = T.SAND; if (n<0.005) tile=T.SKULL; else if (n<0.09) tile=T.CACTUS; else if (n<0.13) tile=T.ROCK; else if (n<0.15) tile=T.IRONROCK; }
      else { if (n<0.06) tile=T.TREE; else if (n<0.09) tile=T.ROCK; else if (n<0.12) tile=T.BUSH; else if (n<0.15) tile=T.WHEAT; }
      w[y][x] = { type: tile, hp: tileHP(tile), timer: 0 };
    }
  }
  if (hasCrystal){
    const acx = Math.floor(MAPW/2), acy = Math.floor(MAPH/2);
    for (let y=acy-4; y<=acy+4; y++){ for (let x=acx-4; x<=acx+4; x++){ if (y<0||y>=MAPH||x<0||x>=MAPW) continue; if (Math.hypot(x-acx, y-acy) <= 4.2){ w[y][x] = { type:T.ALTAR_FLOOR, hp:0, timer:0 }; } } }
    w[acy][acx] = { type:T.TABLET, hp:tileHP(T.TABLET), timer:0 };
    let placed=false, tries=0;
    while(!placed && tries<400){ tries++; const rx = 4+Math.floor(rng()*(MAPW-8)), ry = 4+Math.floor(rng()*(MAPH-8));
      if (Math.hypot(rx-acx, ry-acy) < 10) continue; const t = w[ry][rx];
      if (t.type===T.GRASS||t.type===T.SAND||t.type===T.SNOW){ w[ry][rx] = { type:T.CRYSTAL_ORE, hp:tileHP(T.CRYSTAL_ORE), maxHp:tileHP(T.CRYSTAL_ORE), timer:0 }; placed=true; } }
  }
  let caves=0, ctries=0; const wantCaves=2+Math.floor(rng()*2);
  while (caves<wantCaves && ctries<400){ ctries++; const rx=4+Math.floor(rng()*(MAPW-8)), ry=4+Math.floor(rng()*(MAPH-8)); const t=w[ry][rx];
    if (t.type===T.GRASS||t.type===T.SAND||t.type===T.SNOW){ w[ry][rx]={type:T.CAVE_IN, hp:tileHP(T.CAVE_IN), timer:0, caveId:'cave'+caves}; caves++; } }
  return w;
}
function genWorld(){ worldSeed = (Math.random()*0x7fffffff)>>>0; world = buildBaseWorld(worldSeed, worldHasCrystal()); }

function groundColor(b, tileType){
  if (tileType===T.WATER) return '#2a5a8a';
  // Inside a cave everything sits on the same dark rock — no surface biomes bleeding through (no yellow/white patches).
  if (inCave) return (tileType===T.CAVE_FLOOR || tileType===T.ALTAR_FLOOR) ? '#33333c' : '#242430';
  if (tileType===T.CAVE_FLOOR) return '#33333c';
  if (tileType===T.ALTAR_FLOOR) return '#8a8a8a';
  if (b===BIOME.DESERT) return '#d8c27a'; if (b===BIOME.SNOW) return '#e8eef2'; return '#3a7d34';
}
function tileAt(px,py){ const tx=Math.floor(px/TILE), ty=Math.floor(py/TILE); if (ty<0||ty>=MAPH||tx<0||tx>=MAPW) return {type:T.WATER, hp:0}; return world[ty][tx]; }
function isSolid(t){ return [T.TREE, T.ROCK, T.COAL, T.IRONROCK, T.CACTUS, T.PINE, T.WALL, T.WALL_THORN, T.BONE_WALL, T.LUCKY, T.TRUNK, T.CRAFTING_TABLE, T.SAPLING, T.SKULL, T.UPGRADED_TABLE, T.FURNACE, T.TABLET, T.CRYSTAL_ORE, T.CRYSTAL_DEVICE, T.CAVE_CRYSTAL, T.BEEHIVE, T.GARDEN_TABLE, T.CAVE_WALL].includes(t.type); }
function isWater(t){ return t.type===T.WATER; }

let enemies, animals, particles, projectiles, placedTorches, chests, cropTiles, pickups;
let pickupIdSeq = 0;           // host-assigned ids for dropped-item pickups
let showPlayerNames = true;    // settings toggle for teammate name tags
let fishing = null;            // fishing state machine: { phase:'wait'|'bite', timer }
let inCave = false;            // are we in the cave dimension?
let surfaceState = null;       // saved surface world/player while inside a cave
let caveWorlds = {};           // caveId -> persistent cave world (each entrance keeps its own maze)
let currentCaveId = null;
let bossActive = false, boss = null, bossSpawnedForDay = -1;  // scheduled siege boss
let safeHouseActive = false, safeHousePrev = false;          // safe-house buff state
let player, camX, camY, time, dayNum, gameOver, countTimer=0;
let gameMode = 'crystal';      // 'crystal' | 'eternal' | 'test'
let gameStarted = false;       // stays false until a world is picked
let bonusModalOpen = false;    // pauses the world while the morning-bonus modal is up
let eternalNightDay = 5;       // effective day the eternal night begins for the current world
let userEternalDay = 5;        // the crystal-world day chosen via secret code 2020 (persists across mode switches)
let challengeStartDay = 2;      // in the eternal-night (challenge) world, the day the eternal night begins (player picks 1-5)
function startChallenge(d){ challengeStartDay = Math.max(1, Math.min(5, d||2)); startWorld('challenge'); }
function start3D(mode){ view3d = true; camAngle = Math.PI/2; startWorld(mode||'survival'); showToast('🕶️ מצב גוף ראשון! הג׳ויסטיק: ימינה/שמאלה מסתובב, קדימה/אחורה הולך'); }
function toggleView3D(){ view3d = !view3d; if (view3d) camAngle = Math.PI/2; showToast(view3d ? '🕶️ עברת לתלת־מימד (גוף ראשון)' : '🗺️ חזרת למבט מלמעלה'); }
let stats = { animalsKilled:0, monstersKilled:0, blocksDestroyed:0, maxBreakDist:2, luckyOpened:0, dailyChoices:[] };
let bonusShownForDay = 0;      // guards against re-triggering the morning bonus in the same day
let luckyQueue = [];           // pending saved choice-sets, attached to lucky blocks in order they're placed
let adminNightlyAll = false;   // admin toggle: every night auto-grant a lucky block + every bonus power
let guestCheatsAllowed = false; // host permission: may guests use the secret code / OP menu?
/* ---- P2P co-op networking (WebRTC, copy-paste signaling, works on a hotspot with no server) ---- */
let net = { active:false, isHost:false, peers:[], selfId: Math.random().toString(36).slice(2,7), name:'שחקן', _pendingHostPeer:null, peerObj:null, myCode:null, hostCode:null, lastReconnect:0, wasConnected:false };
let remotePlayers = {};        // id -> {x,y,facing,hp,name,last,color,torch}
let playerSkin = '#2f5f8a';    // chosen shirt color (shown to yourself and to teammates)
function setSkin(color, el){ playerSkin = color; document.querySelectorAll('.skinSwatch').forEach(s=>s.classList.remove('sel')); if(el) el.classList.add('sel'); }
// The name you pick once and everyone in a shared world sees above your character.
function lsGet(k){ try{ return localStorage.getItem(k); }catch(e){ return null; } }
function lsSet(k,v){ try{ localStorage.setItem(k,v); }catch(e){} }
let playerName = (lsGet('joni_playerName') || '').slice(0,14);
function setPlayerName(v){ playerName = (v||'').slice(0,14); lsSet('joni_playerName', playerName); if (net.active) net.name = playerName || (net.isHost?'מארח':'אורח'); }
function myName(){ return playerName || (net.isHost ? 'מארח' : 'אורח'); }
let netGuestDmg = {};          // host-side accumulator of damage owed to each guest, flushed over the network
let netPlayerCount = 1;        // 1 + connected guests (host view)
let enemyIdSeq = 0;            // host-assigned enemy ids for network sync
// all player positions the host must consider (its own + every connected guest)
function allPlayers(){ const arr=[{x:player.x, y:player.y, id:null}]; if(!inCave){ for(const id in remotePlayers){ const r=remotePlayers[id]; arr.push({x:r.x, y:r.y, id}); } } return arr; }   // in a private cave, only you
function nearestPlayer(x,y){ let best=null, bd=Infinity; for(const pl of allPlayers()){ const d=Math.hypot(pl.x-x, pl.y-y); if(d<bd){ bd=d; best=pl; } } return best||{x:player.x,y:player.y,id:null}; }
// route damage to whichever player an enemy reached: local player directly, guests via the network
function damagePlayer(targetId, amount){
  if (targetId==null){
    if (player.equipment.bone_shield){ amount *= 0.75; for(let i=0;i<3;i++) spawnParticle(player.x+(Math.random()*16-8), player.y+(Math.random()*16-8), Math.random()<0.5?'#fff':'#c8c8c8', 3); }  // bone shield absorbs 25%
    if(!cheatGodMode) player.health -= amount; if (!player.hurtSfxCd || player.hurtSfxCd<=0){ sfxHurt(); player.hurtSfxCd=0.5; }
  }
  else { netGuestDmg[targetId] = (netGuestDmg[targetId]||0) + amount; }
}
let netShadow = null;          // last-broadcast tile-type grid, for diffing structural world changes
let netLastPos = 0, netLastDiff = 0, netLastEnt = 0;
function resetStats(){ stats = { animalsKilled:0, monstersKilled:0, blocksDestroyed:0, maxBreakDist:2, luckyOpened:0, dailyChoices:[] }; }
function initEntities(){ enemies=[]; animals=[]; particles=[]; projectiles=[]; placedTorches=[]; chests=[]; cropTiles=[]; enemyProjectiles=[]; pickups=[]; }
function initPlayer(){
  const gx = Math.floor(MAPW/2), gy = Math.floor(MAPH*0.42);
  player = { 
    gridX:gx, gridY:gy, x:gx*TILE+TILE/2, y:gy*TILE+TILE/2, w:18,h:18, moving:false, moveFrom:{x:0,y:0}, moveTo:{x:0,y:0}, moveT:0, moveDuration:0.24, health:100, maxHealth:100, hunger:100, maxHunger:100, speed:2.5, facing:'down', 
    inv:{ wood:0, stone:0, coal:0, iron:0, iron_ingot:0, berry:0, meat:0, torch:0, bones:0, wheat:0, seeds:0, bowl:0, dough:0, bread:0, cooked_meat:0, fruit_salad:0, crystal:0, reinforcement:0, raw_fish:0, cooked_fish:0, big_fish:0, pufferfish:0, eel:0, golden_fish:0, cave_crystal:0, honey_jar:0,
          clover:0, sunflower:0, herb:0, poppy:0, bluebell:0, goldenrod:0, glowcap:0, nightshade:0, crystalbloom:0, emberlily:0, moonflower:0,
          healing_potion:0, speed_potion:0, glow_lantern:0, harvest_charm:0, calm_incense:0, strength_brew:0, moon_elixir:0,
          item_wall:0, item_wall_thorn:0, item_bone_wall:0, item_campfire:0, item_furnace:0, item_crafting_table:0, item_upgraded_table:0, item_chest:0, item_crystal_device:0, item_lucky:0, item_beehive:0, item_garden_table:0 },
    equipment:{}, activeWeapon:'sword', attackCd:0, stepSfxCd:0, nearFire:0, walkFrame:0, isWalking:false, hurtSfxCd:0,
    placingItem: null, speedBoostTimer: 0, efficiencyBoostTimer: 0, slowTimer: 0, sweetTimer: 0, glowTimer: 0, calmTimer: 0, harvestTimer: 0, strengthTimer: 0,
    gatherBonus: 0, breakReach: 2, speedBonus: 0   // permanent bonuses from morning choices
  };
}
function initGame(){
  // per-mode: 'survival' = normal nights forever (no crystal, no eternal);
  //           'challenge' = eternal night from day 2 (no crystal);
  //           'crystal' = build the crystal before the eternal night (default day 5, editable);
  //           'test' = sandbox.
  if (gameMode==='survival') eternalNightDay = 999999;
  else if (gameMode==='challenge') eternalNightDay = challengeStartDay;   // player-chosen day the eternal night begins
  else eternalNightDay = userEternalDay;   // crystal & test use the 2020-editable day
  genWorld(); initEntities(); initPlayer(); resetStats();
  time = 0; dayNum = 1; gameOver=false; tickAcc=0; countTimer=0;
  bonusShownForDay = 0; luckyQueue = [];
  inCave=false; surfaceState=null; caveWorlds={}; currentCaveId=null; bossActive=false; boss=null; bossSpawnedForDay=-1; fishing=null;
  // reset run-scoped crystal / eternal-night state (important on restart)
  crystalPlaced=false; crystalActivated=false; crystalDevicePos=null; crystalBonusDays=0;
  eternalNightActive=false; forcedDayUntil=0; enemyProjectiles=[];
  if (gameMode==='test') setupTestWorld();
  camX = player.x; camY = player.y; updateHUD(); renderBag(); changeUIScale(1.2); updateResourceCounts();
}
function worldHasCrystal(){ return gameMode==='crystal'; }   // only the crystal world spawns the crystal/tablet
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
  { id:'fishing_rod', name:'🎣 חכת דיג', cost:{wood:3, bones:2}, type:'tool', station:'table' },
  { id:'beehive', name:'🐝 כוורת דבורים', cost:{wood:6, bones:4}, type:'building', station:'table' },
  { id:'garden_table', name:'🌿 שולחן צמחים', cost:{wood:5, wheat:3, clover:1}, type:'building', station:'table' },
  { id:'arrowBone', name:'➶ 5 חצי עצם', cost:{bones:1, wood:1}, type:'ammo', give:{arrowBone:5}, station:'table' },
  
  { id:'furnace', name:'♨️ תנור אבן', cost:{stone:8}, type:'building', station:'upgraded' },
  { id:'crafting_table_dup', name:'🛠️ שולחן עבודה', cost:{wood:2}, type:'building', station:'upgraded' }, 
  { id:'upgraded_table_dup', name:'⚙️ שולחן משודרג', cost:{wood:4, stone:4, coal:2}, type:'building', station:'upgraded' }, 
  { id:'campfire_dup', name:'🏕️ מדורה', cost:{wood:4, stone:2}, type:'building', station:'upgraded' }, 
  { id:'dough', name:'🥟 בצק חיטה', cost:{wheat:1}, type:'ammo', give:{dough:1}, station:'upgraded' },
  { id:'bowl', name:'🥣 קערת עץ', cost:{wood:3}, type:'ammo', give:{bowl:1}, station:'upgraded' },
  { id:'crystal_device', name:'💎 מכשיר הקריסטל', cost:{stone:8, iron:8, crystal:1}, type:'building', station:'upgraded' },
  { id:'reinforcement', name:'⛓️ חיזוק ברזל', cost:{iron_ingot:2}, type:'ammo', give:{reinforcement:1}, station:'upgraded' },
  { id:'bone_shield', name:'🛡️ מגן עצמות', cost:{bones:15, wheat:5}, type:'tool', station:'upgraded' },
  
  { id:'bucket', name:'🪣 דלי ברזל', cost:{iron_ingot:3}, type:'tool', station:'furnace' },
  { id:'arrowIron', name:'➶ 5 חצי ברזל', cost:{wood:1, iron_ingot:1}, type:'ammo', give:{arrowIron:5}, station:'furnace' }, 
  { id:'iron_axe', name:'🪓 גרזן ברזל', cost:{wood:2, iron_ingot:2}, type:'tool', station:'furnace' }, 
  { id:'iron_pickaxe', name:'⛏️ מכוש ברזל', cost:{wood:2, iron_ingot:3}, type:'tool', station:'furnace' }, 
  { id:'iron_sword', name:'🗡️ חרב ברזל', cost:{wood:1, iron_ingot:2}, type:'tool', station:'furnace' }, 
  { id:'bread', name:'🍞 לחם חם', cost:{dough:1, coal:1}, type:'ammo', give:{bread:1}, station:'furnace' },
  { id:'smelt_iron', name:'⚪ חמם ברזל', cost:{iron:1, coal:1}, type:'ammo', give:{iron_ingot:1}, station:'furnace' },
  
  { id:'cooked_meat', name:'🍖 בשר מעושן', cost:{bowl:1, meat:1}, type:'ammo', give:{cooked_meat:1}, station:'campfire' },
  { id:'fruit_salad', name:'🥗 סלט פירות', cost:{bowl:1, berry:2}, type:'ammo', give:{fruit_salad:1}, station:'campfire' },
  { id:'cooked_fish', name:'🐠 דג צלוי', cost:{raw_fish:1, coal:1}, type:'ammo', give:{cooked_fish:1}, station:'campfire' },

  // Herbalist Table (🌿 garden station): brew special items from the plants you crossbreed
  { id:'healing_potion', name:'❤️ שיקוי ריפוי', cost:{herb:2, clover:1}, type:'ammo', give:{healing_potion:1}, station:'garden' },
  { id:'speed_potion', name:'💨 שיקוי מהירות', cost:{clover:2, sunflower:1}, type:'ammo', give:{speed_potion:1}, station:'garden' },
  { id:'glow_lantern', name:'🏮 פנס זוהר', cost:{goldenrod:1, glowcap:1}, type:'ammo', give:{glow_lantern:1}, station:'garden' },
  { id:'harvest_charm', name:'🍀 קמע יבול', cost:{clover:3, herb:1}, type:'ammo', give:{harvest_charm:1}, station:'garden' },
  { id:'calm_incense', name:'🕯️ קטורת שלווה', cost:{poppy:2, bluebell:1, honey_jar:1}, type:'ammo', give:{calm_incense:1}, station:'garden' },
  { id:'strength_brew', name:'⚔️ שיקוי כוח', cost:{nightshade:2, emberlily:1}, type:'ammo', give:{strength_brew:1}, station:'garden' },
  { id:'moon_elixir', name:'🌕 שיקוי הירח', cost:{moonflower:1, crystalbloom:1}, type:'ammo', give:{moon_elixir:1}, station:'garden' },
  { id:'garden_seeds', name:'🌱 3 זרעים', cost:{wheat:1}, type:'ammo', give:{seeds:3}, station:'garden' }
];

const names = {wood:'🪵 עץ',stone:'🪨 אבן',coal:'⚫ פחם',iron:'🔶 ברזל',iron_ingot:'⚪ ברזל מחומם',berry:'🍓 פרי',meat:'🍖 בשר',torch:'🔥 לפיד',bones:'🦴 עצם',wheat:'🌾 חיטה',seeds:'🌱 זרעים',bowl:'🥣 קערה',dough:'🥟 בצק',bread:'🍞 לחם',cooked_meat:'🍖 בשר מעושן',fruit_salad:'🥗 סלט פירות',raw_fish:'🐟 דג נא',cooked_fish:'🐠 דג צלוי',big_fish:'🐠 דג גדול',pufferfish:'🐡 דג נפוח',eel:'🐍 צלופח',golden_fish:'🥇 דג זהב',arrowBone:'➶ חצי עצם',cave_crystal:'🔮 קריסטל מערה',honey_jar:'🍯 צנצנת דבש',beehive:'🐝 כוורת דבורים',item_beehive:'🐝 כוורת דבורים (בתיק)',
  clover:'🍀 תלתן',sunflower:'🌻 חמנית',herb:'🌿 עשב מרפא',poppy:'🌺 פרג',bluebell:'🔔 פעמונית',goldenrod:'🌟 זהבית',glowcap:'🍄 פטריית זוהר',nightshade:'🟣 בּלַדוֹנָה',crystalbloom:'💠 פרח בדולח',emberlily:'🔥 שושן אש',moonflower:'🌕 פרח ירח',
  healing_potion:'❤️ שיקוי ריפוי',speed_potion:'💨 שיקוי מהירות',glow_lantern:'🏮 פנס זוהר',harvest_charm:'🍀 קמע יבול',calm_incense:'🕯️ קטורת שלווה',strength_brew:'⚔️ שיקוי כוח',moon_elixir:'🌕 שיקוי הירח',garden_table:'🌿 שולחן צמחים',item_garden_table:'🌿 שולחן צמחים (בתיק)',
  crafting_table:'🛠️ שולחן עבודה',upgraded_table:'⚙️ שולחן משודרג',furnace:'♨️ תנור אבן', chest:'📦 תיבת אחסון', campfire:'🏕️ מדורה', wall:'🧱 קיר', wall_thorn:'🌵 קיר קוצים', bone_wall:'🦴 קיר עצמות', crystal:'💎 קריסטל', reinforcement:'⛓️ חיזוק ברזל',
  item_wall:'🧱 קיר (בתיק)', item_wall_thorn:'🌵 קיר קוצים (בתיק)', item_bone_wall:'🦴 קיר עצמות (בתיק)', item_campfire:'🏕️ מדורה (בתיק)', item_furnace:'♨️ תנור (בתיק)', item_crafting_table:'🛠️ שולחן (בתיק)', item_upgraded_table:'⚙️ שולחן משודרג (בתיק)', item_chest:'📦 תיבה (בתיק)', item_crystal_device:'💎 מכשיר קריסטל (בתיק)', item_lucky:'🟨 לאקי בלוק (בתיק)'};

function canCraft(r){ for(const k in r.cost){ if((player.inv[k]||0) < r.cost[k]) return false; } return true; }

function frontPos(){
  let dirX = 0, dirY = 0;
  if (view3d){ return { fx: player.x + Math.cos(camAngle)*(TILE*1.5), fy: player.y + Math.sin(camAngle)*(TILE*1.5) }; }   // first person: you build/mine where you look
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
    let res = { table: false, upgraded: false, furnace: false, campfire: false, garden: false };
    for(let oy = -5; oy <= 5; oy++) {
        for(let ox = -5; ox <= 5; ox++) {
            const cx = tx+ox, cy = ty+oy;
            if (world[cy] && world[cy][cx]) {
                let t = world[cy][cx].type;
                if (t === T.CRAFTING_TABLE) res.table = true;
                if (t === T.UPGRADED_TABLE) { res.upgraded = true; res.table = true; }
                if (t === T.FURNACE) res.furnace = true;
                if (t === T.CAMPFIRE) res.campfire = true;
                if (t === T.GARDEN_TABLE) res.garden = true;
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
function selectTool(kind){
  if (kind==='dig'){ if(!player.equipment.shovel){ showToast('אין לך את חפירה'); return; } player.placingItem={ id:'dig', type:'dig', name:'🥄 חפירה', cost:{} }; showToast('🥄 את חפירה — לחץ על אדמה ליד מים כדי לחפור תעלה'); }
  else if (kind==='bucket'){ if(!player.equipment.bucket){ showToast('אין לך דלי'); return; } player.placingItem={ id:'bucket', type:'bucket', name:'🪣 דלי', cost:{} }; showToast('🪣 דלי — לחץ על אדמה כדי לשפוך מים, או על מים כדי למלא'); }
  else if (kind==='fish'){ if(!player.equipment.fishing_rod){ showToast('אין לך חכת דיג'); return; } player.placingItem={ id:'fish', type:'fish', name:'🎣 חכה', cost:{} }; showToast('🎣 חכת דיג — לחץ על מים כדי להתחיל לדוג'); }
  toggleBag();
}
function selectFertilize(){ if((player.inv.bones||0)<=0){ showToast('אין לך עצמות'); return; } player.placingItem={ id:'fertilize', type:'fertilize', name:'🌱 דשן', cost:{} }; toggleBag(); showToast('🌱 דשן עצמות — לחץ על יבול צומח כדי להאיץ אותו'); }

window.eatItem = function(k) { 
  if ((player.inv[k]||0) <= 0) return; 
  player.inv[k]--; 
  if (k === 'berry') { player.hunger = Math.min(player.maxHunger, player.hunger + 20); showToast('אכלת תות! 🍓'); } 
  else if (k === 'meat') { player.hunger = Math.min(player.maxHunger, player.hunger + 40); player.health = Math.min(player.maxHealth, player.health + 15); showToast('אכלת בשר! 🍖'); } 
  else if (k === 'bread') { player.hunger = Math.min(player.maxHunger, player.hunger + 80); player.health = Math.min(player.maxHealth, player.health + 35); showToast('אכלת לחם חם! 🍞'); }
  else if (k === 'cooked_meat') { player.hunger = Math.min(player.maxHunger, player.hunger + 90); player.health = Math.min(player.maxHealth, player.health + 50); showToast('אכלת בשר מעושן משובח! 🍖🔥'); }
  else if (k === 'cooked_fish') { player.hunger = Math.min(player.maxHunger, player.hunger + 50); player.health = Math.min(player.maxHealth, player.health + 20); showToast('אכלת דג צלוי! 🐠'); }
  else if (k === 'big_fish') { player.hunger = Math.min(player.maxHunger, player.hunger + 60); player.health = Math.min(player.maxHealth, player.health + 25); showToast('אכלת דג גדול! 🐠'); }
  else if (k === 'pufferfish') { player.hunger = Math.min(player.maxHunger, player.hunger + 30); showToast('אכלת דג נפוח... קצת מוזר 🐡'); }
  else if (k === 'eel') { player.hunger = Math.min(player.maxHunger, player.hunger + 45); player.health = Math.min(player.maxHealth, player.health + 15); showToast('אכלת צלופח! 🐍'); }
  else if (k === 'golden_fish') { player.hunger = player.maxHunger; player.health = Math.min(player.maxHealth, player.health + 60); showToast('אכלת דג זהב! ריפוי ענק 🥇'); }
  else if (k === 'honey_jar') { player.hunger = Math.min(player.maxHunger, player.hunger + 40); player.speedBoostTimer = 12; player.sweetTimer = 12; showToast('🍯 אנרגיה מתוקה! מהירות + חסינות לקור ל-12 שניות'); }
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

// Potions & charms brewed at the 🌿 Herbalist Table from crossbred plants
const POTIONS = {
  healing_potion: true, speed_potion: true, glow_lantern: true, harvest_charm: true, calm_incense: true, strength_brew: true, moon_elixir: true
};
window.usePotion = function(k){
  if ((player.inv[k]||0) <= 0) return;
  player.inv[k]--;
  if (k === 'healing_potion') { player.health = Math.min(player.maxHealth, player.health + 60); showToast('❤️ שיקוי ריפוי! +60 חיים'); }
  else if (k === 'speed_potion') { player.speedBoostTimer = Math.max(player.speedBoostTimer||0, 25); showToast('💨 שיקוי מהירות! מהירות מוגברת ל-25 שניות'); }
  else if (k === 'glow_lantern') { player.glowTimer = Math.max(player.glowTimer||0, 60); showToast('🏮 פנס זוהר! ראיית לילה ל-60 שניות'); }
  else if (k === 'harvest_charm') { player.harvestTimer = Math.max(player.harvestTimer||0, 45); player.efficiencyBoostTimer = Math.max(player.efficiencyBoostTimer||0, 45); showToast('🍀 קמע יבול! חציבה כפולה ויבול מהיר ל-45 שניות'); }
  else if (k === 'calm_incense') { player.calmTimer = Math.max(player.calmTimer||0, 30); showToast('🕯️ קטורת שלווה! מפלצות מתעלמות ממך ל-30 שניות'); }
  else if (k === 'strength_brew') { player.strengthTimer = Math.max(player.strengthTimer||0, 30); showToast('⚔️ שיקוי כוח! נזק כפול ל-30 שניות'); }
  else if (k === 'moon_elixir') { player.health = player.maxHealth; player.speedBoostTimer = Math.max(player.speedBoostTimer||0, 40); player.glowTimer = Math.max(player.glowTimer||0, 40); player.strengthTimer = Math.max(player.strengthTimer||0, 40); showToast('🌕 שיקוי הירח! ריפוי מלא + מהירות + זוהר + כוח ל-40 שניות'); }
  sfxPotion(); renderBag(); updateHUD();
}

window.tryInteract = function() {
    if (player.placingItem) {
        let r = player.placingItem;

        // tapTarget (set when you tap the map directly) overrides the joystick-direction target
        let tx, ty;
        if (tapTarget){ tx = tapTarget.tx; ty = tapTarget.ty; }
        else { let p = frontPos(); tx = Math.floor(p.fx / TILE); ty = Math.floor(p.fy / TILE); }
        if (ty < 0 || ty >= MAPH || tx < 0 || tx >= MAPW) { showToast('מחוץ לגבולות המפה!'); return; }
        
        let t = world[ty][tx];
        let ptx = Math.floor(player.x/TILE), pty = Math.floor(player.y/TILE);

        // Iron reinforcement: wrap an EXISTING built object to add a big chunk of durability.
        if (r.type === 'reinforce'){
          if ((player.inv.reinforcement||0) <= 0){ showToast('אין לך חיזוק ברזל בתיק!'); player.placingItem = null; return; }
          if (PLAYER_BUILT_TILES.includes(t.type)){
            player.inv.reinforcement -= 1;
            // A separate grey ring that absorbs 100 hits, then breaks. It does NOT heal the item.
            if (t.def==null){ t.def=enemyHitsFor(t.type); t.defMax=t.def; }
            t.shield = (t.shield||0) + REINFORCE_SHIELD;
            t.shieldMax = (t.shieldMax||0) + REINFORCE_SHIELD;
            t.reinforced = (t.reinforced||0) + 1;
            showToast('⛓️ הוספת הגנת ברזל! טבעת אפורה של '+REINFORCE_SHIELD+' מכות מסביב למבנה');
            if ((player.inv.reinforcement||0) <= 0) player.placingItem = null;
            renderBag();
          } else {
            showToast('כוון אל מבנה שבנית כדי לחזק אותו (קיר/תנור/מדורה...)');
          }
          return;
        }

        // Shovel: dig ground that touches water so the water spreads into it (carve channels/lakes).
        if (r.type === 'dig'){
          if (!player.equipment.shovel){ showToast('אין לך את חפירה'); player.placingItem=null; return; }
          if (t.type===T.GRASS || t.type===T.SAND || t.type===T.SNOW){
            const nearW = [[0,-1],[0,1],[-1,0],[1,0]].some(([ox,oy])=> world[ty+oy] && world[ty+oy][tx+ox] && world[ty+oy][tx+ox].type===T.WATER);
            if (nearW){ world[ty][tx] = { type:T.WATER, hp:0, timer:0 }; sfxGather(); spawnParticle(tx*TILE+16, ty*TILE+16, '#2a5a8a', 5); showToast('🥄 חפרת תעלה — המים התפשטו!'); }
            else showToast('צריך לחפור ליד מים קיימים');
          } else showToast('אפשר לחפור רק אדמה');
          return;
        }
        // Bucket: pour water on any ground tile (or the message reminds you it fills on water). Reusable.
        if (r.type === 'bucket'){
          if (!player.equipment.bucket){ showToast('אין לך דלי'); player.placingItem=null; return; }
          if (t.type===T.GRASS || t.type===T.SAND || t.type===T.SNOW){ world[ty][tx] = { type:T.WATER, hp:0, timer:0 }; sfxGather(); spawnParticle(tx*TILE+16, ty*TILE+16, '#2a5a8a', 5); showToast('🪣 שפכת מים!'); }
          else if (isWater(t)){ showToast('🪣 הדלי מלא מים — לחץ על אדמה כדי לשפוך'); }
          else showToast('אי אפשר לשפוך כאן');
          return;
        }
        // Fishing rod: tap a water tile to start fishing
        if (r.type === 'fish'){
          if (!player.equipment.fishing_rod){ showToast('אין לך חכת דיג'); player.placingItem=null; return; }
          if (isWater(t)){ startFishing(tx, ty); player.placingItem=null; }
          else showToast('🎣 צריך לכוון אל מים');
          return;
        }
        // Bone meal: instantly grow a crop
        if (r.type === 'fertilize'){
          if ((player.inv.bones||0)<=0){ showToast('אין לך עצמות'); player.placingItem=null; return; }
          if (t.type===T.CROP){ player.inv.bones-=1; if(!t.species) t.species='wheat'; t.cx=tx; t.cy=ty; t.growAt=performance.now(); if(!cropTiles.includes(t)) cropTiles.push(t); for(let i=0;i<8;i++) spawnParticle(tx*TILE+8+Math.random()*16, ty*TILE+8+Math.random()*16, (PLANT_SPECIES[t.species]||{}).color||'#73c745', 4); sfxGather(); showToast('🌱 דישנת! היבול גדל מיד'); renderBag(); if((player.inv.bones||0)<=0) player.placingItem=null; }
          else showToast('צריך לכוון אל יבול צומח 🌱');
          return;
        }

        // Building on water is now allowed (bridges/bases over the lake); only seeds still can't go on water.
        let waterBlocked = isWater(t) && r.type === 'plant';
        if (isSolid(t) || waterBlocked || (tx === ptx && ty === pty)) { showToast('המקום חסום!'); return; }

        if (r.type === 'plant') {
            if (!canCraft(r)) { showToast('חסרים משאבים!'); player.placingItem = null; return; }
            for(const k in r.cost) player.inv[k] -= r.cost[k];
            const newTile = { type:T.CROP, hp:tileHP(T.CROP), timer:0, species:'wheat', cx:tx, cy:ty, bred:false, growAt: performance.now()+opCropGrowSeconds*1000, plantedAt: performance.now() };
            world[ty][tx] = newTile;
            cropTiles.push(newTile);
            showToast('שתלת זרעים! 🌱 יגדל וייתכן שיצטלב לצמח חדש');
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
                if (net.active && !net.isHost) netSend({ t:'chest_add', x: tx*TILE+TILE/2, y: ty*TILE+TILE/2 });
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
            if (r.id==='beehive') placedType = T.BEEHIVE;
            if (r.id==='garden_table') placedType = T.GARDEN_TABLE;
            if (r.id==='lucky') placedType = T.LUCKY;

            const placedHp = tileHP(placedType);
            world[ty][tx] = { type: placedType, hp: placedHp, maxHp: placedHp, timer: 0 };
            if (PLAYER_BUILT_TILES.includes(placedType)) { world[ty][tx].def = enemyHitsFor(placedType); world[ty][tx].defMax = world[ty][tx].def; }
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

    // Cave entrance / exit (stand on the tile and press interact)
    {
      const ptile = world[player.gridY] && world[player.gridY][player.gridX];
      if (ptile){
        if (ptile.type===T.CAVE_IN){ enterCave(ptile.caveId); return; }
        if (ptile.type===T.CAVE_UP){ exitCave(); return; }
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
    // (Plant crossbreeding is no longer done here — a plant only breeds once, the moment it finishes growing. See updateCrops.)
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

/* ============ Farming: planted crop growth + one-shot crossbreeding ============ */
const CROP_DIRS = [[0,-1],[0,1],[-1,0],[1,0],[-1,-1],[1,-1],[-1,1],[1,1]];
// The instant a plant finishes growing it looks around ONCE: if a different mature plant sits next to it
// and there's a free tile, it may sprout a new species (each recipe rolls its own chance). One try, ever.
function breedOnMaturity(c){
  const x=c.cx, y=c.cy; if(x==null||y==null) return null;
  const empties=[], neigh=[];
  for(const d of CROP_DIRS){ const nx=x+d[0], ny=y+d[1]; if(ny<0||ny>=MAPH||nx<0||nx>=MAPW) continue;
    const t=world[ny][nx]; if(!t) continue;
    if(t.type===T.GRASS||t.type===T.SAND||t.type===T.SNOW) empties.push([nx,ny]);
    else if(t.type===T.CROP && t.mature && t.species) neigh.push(t.species);
  }
  if(!empties.length || !neigh.length) return null;
  // pair THIS plant with each mature neighbour and gather every offspring the recipes allow
  const cands=[];
  for(const ns of neigh){ const rec=CROSS[pairKey(c.species, ns)]; if(rec) for(const o of rec) cands.push(o); }
  if(!cands.length) return null;
  // decide + roll a chance for each candidate; first hit sprouts in a random free tile
  for(const cand of cands){ if(Math.random() < cand.chance){ const [ex,ey]=empties[Math.floor(Math.random()*empties.length)]; return {x:ex,y:ey,sp:cand.sp}; } }
  return null;
}
function updateCrops(dt){
  if (!cropTiles.length) return;
  const now = performance.now();
  const boost = (player.harvestTimer>0) ? (dt||0)*1000*2 : 0;   // 🍀 harvest charm: crops ripen ~3x faster
  const born=[];
  for (const c of cropTiles){
    if (c.type !== T.CROP || c.mature) continue;
    if (boost) c.growAt -= boost;
    const total = Math.max(1, opCropGrowSeconds*1000);
    const elapsed = total - (c.growAt - now);
    c.stage = elapsed < total*0.34 ? 0 : (elapsed < total*0.67 ? 1 : 2);
    if (now >= c.growAt){
      c.mature = true; c.stage = 3; c.hp = tileHP(T.CROP);
      if (!c.bred){ c.bred = true;                        // one breeding check, only for the host / single player
        if (!(net.active && !net.isHost)){ const b = breedOnMaturity(c);
          if (b){ const nt={ type:T.CROP, hp:tileHP(T.CROP), timer:0, species:b.sp, cx:b.x, cy:b.y, bred:false, growAt: now+opCropGrowSeconds*1000, plantedAt: now };
            world[b.y][b.x]=nt; born.push(nt);
            if (typeof sfxCrossbreed==='function') sfxCrossbreed();
            const col=(PLANT_SPECIES[b.sp]||{}).color||'#73c745';
            for(let i=0;i<8;i++) spawnParticle(b.x*TILE+8+Math.random()*16, b.y*TILE+8+Math.random()*16, col, 4);
          }
        }
      }
    }
  }
  for(const n of born) cropTiles.push(n);
  // matured crops stay CROP tiles (harvested by hand); drop them from the growth list so it stays small
  if (cropTiles.length > 400) cropTiles = cropTiles.filter(c=>c.type===T.CROP && !c.mature);
}

function update(dt){
  if (gameOver || !gameStarted || bonusModalOpen) return;
  if (net.active) netTick(dt);
  const netClient = net.active && !net.isHost;   // guests take world time & simulation from the host
  time += dt; if (!netClient && time >= CYCLE_LEN){ time = 0; dayNum++; showToast('יום '+dayNum+' מתחיל'); if (dayNum>=eternalNightDay && !crystalActivated){ if(!eternalNightActive){ eternalNightActive = true; showToast('🌑 הלילה הנצחי החל! מפלצות שונות יגיעו וינסו לשבור מה שבנית'); } }
    if (crystalActivated){ crystalBonusDays++; player.maxHealth += 10; player.maxHunger += 10; player.health = Math.min(player.maxHealth, player.health+10); player.hunger = Math.min(player.maxHunger, player.hunger+10); showToast(`💎 כוח הקריסטל גדל! +10 חיים מקס׳, +10 אוכל מקס׳, נזק גבוה יותר (יום ${crystalBonusDays} עם הקריסטל)`); }
    if (adminNightlyAll) grantNightlyAll(); else maybeShowMorningBonus();
  }
  const isNight = getNightFactor() > 0.45;
  
  countTimer += dt; if (countTimer >= 1.0) { countTimer = 0; updateResourceCounts(); if (!netClient) updateBeehives(); }

  netPlayerCount = net.active ? (1 + net.peers.filter(p=>p.open).length) : 1;
  // resource regen speeds up with more players in the world (host runs the sim): 1 player = every 0.5s, 2 = 0.25s, ...
  let effTickDelay = (net.active && net.isHost) ? Math.max(0.05, 0.5/netPlayerCount) : opTickDelay;
  if (!netClient && effTickDelay > 0) {
    tickAcc += dt;
    while (tickAcc >= effTickDelay) {
      tickAcc -= effTickDelay;
      for (let i = 0; i < opBlocksPerTick; i++) runRandomTickEngine();
    }
  }
  updateCrops(dt);   // crops ripen locally for everyone (host is still authoritative on harvest/crossbreed)

  if (player.hurtSfxCd > 0) player.hurtSfxCd -= dt;
  let dx=0, dy=0; if (keys['w']||keys['arrowup']) dy-=1; if (keys['s']||keys['arrowdown']) dy+=1; if (keys['a']||keys['arrowleft']) dx-=1; if (keys['d']||keys['arrowright']) dx+=1;
  if (joyActive && (Math.abs(joyDX)>0.2||Math.abs(joyDY)>0.2)){ dx=joyDX; dy=joyDY; }
  if (view3d){
    // First person: left/right turns your head, up/down walks the way you're looking.
    const turn = dx, fwd = -dy;
    if (Math.abs(turn) > 0.15) camAngle += turn * dt * 2.6;
    camAngle = (camAngle + Math.PI*2) % (Math.PI*2);
    dx = Math.cos(camAngle) * fwd; dy = Math.sin(camAngle) * fwd;
    // keep the 2D facing in sync so mining/building/attacking all aim where you look
    const a = camAngle;
    player.facing = (a < 0.393 || a >= 5.890) ? 'right' : a < 1.178 ? 'down-right' : a < 1.963 ? 'down'
                  : a < 2.749 ? 'down-left' : a < 3.534 ? 'left' : a < 4.320 ? 'up-left' : a < 5.105 ? 'up' : 'up-right';
  }
  let isWaterTile = isWater(tileAt(player.x, player.y)); 
  
  let currentSpeed = (player.speed + (player.speedBonus||0)) * (isWaterTile ? 0.5 : 1.0);
  if (player.speedBoostTimer && player.speedBoostTimer > 0) {
      player.speedBoostTimer -= dt;
      currentSpeed *= 1.5;
  }
  if (player.slowTimer && player.slowTimer > 0){ player.slowTimer -= dt; currentSpeed *= 0.7; }   // frost wraith chill
  updateFishing(dt);
  if (fishing){ dx=0; dy=0; }   // freeze movement while fishing

  if (Math.abs(dx) > 0.1 || Math.abs(dy) > 0.1) {
    player.isWalking = true; player.walkFrame += dt * 10;
    if (view3d){ /* facing already follows the camera, don't override it when walking backwards */ }
    else if (Math.abs(dx) > 0.1 && Math.abs(dy) > 0.1) {
        player.facing = (dy > 0 ? 'down' : 'up') + '-' + (dx > 0 ? 'right' : 'left');
    } else if (Math.abs(dx) >= Math.abs(dy)) {
        player.facing = dx > 0 ? 'right' : 'left';
    } else {
        player.facing = dy > 0 ? 'down' : 'up';
    }
  } else { player.isWalking = false; }

  if (motionGrid === 'smooth' || view3d) {   // first person always walks smoothly
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
  // Safe house buff: enclosed by walls + a heat/light source -> half hunger drain, passive heal
  const sh = safeHouseState(); safeHouseActive = sh.inside && sh.buffed;
  if (safeHouseActive !== safeHousePrev){ showToast(safeHouseActive ? '🏡 באזור מוגן — התאוששות פעילה' : '🚪 יצאת מהאזור המוגן'); safeHousePrev = safeHouseActive; }
  const seIndicator = document.getElementById('safeIndicator'); if (seIndicator) seIndicator.style.display = safeHouseActive ? 'inline-block' : 'none';
  if (player.sweetTimer > 0) player.sweetTimer -= dt;
  if (player.glowTimer > 0) player.glowTimer -= dt;
  if (player.calmTimer > 0) player.calmTimer -= dt;
  if (player.harvestTimer > 0) player.harvestTimer -= dt;
  if (player.strengthTimer > 0) player.strengthTimer -= dt;
  camX = player.x; camY = player.y; player.hunger -= dt*(safeHouseActive?0.16:0.32); if (player.hunger<=0){ player.hunger=0; if(!cheatGodMode) player.health -= dt*1.4; }
  if (safeHouseActive) player.health = Math.min(player.maxHealth, player.health + dt*2);
  if (world[player.gridY] && world[player.gridY][player.gridX]) { let pTile = world[player.gridY][player.gridX]; if(pTile.type === T.CAMPFIRE) { player.health = Math.min(player.maxHealth, player.health+dt*8); } }
  if (player.attackCd>0) player.attackCd -= dt; if ((keys[' '] || actionHeld) && !fishing) tryAction();
  const curBiome = biomeAt(Math.floor(player.x/TILE), Math.floor(player.y/TILE));
  const inEternalNight = eternalNightActive && !crystalActivated;
  // Host/solo simulate the surface; guests render the host's snapshot. BUT a player in their own cave always
  // self-simulates it locally (even a guest), since the cave is a private instance not shared over the network.
  const simSelf = inCave || !netClient;
  if (simSelf){
    const pc = netPlayerCount;   // more players -> more monsters, spawned around a random player
    // scheduled siege boss every 5th night, at night, no crystal-devices etc.
    if (isNight && !inCave && dayNum%5===0 && dayNum>0 && bossSpawnedForDay!==dayNum && !cheatNoEnemies){ bossSpawnedForDay=dayNum; spawnBoss(); }
    if (inCave){
      // dark caves swarm with monsters that pop up close, in the unlit corners, and harass you
      if (!cheatNoEnemies){ const cap = 9 + Math.floor(dayNum/3); if (Math.random() < dt*0.55 && enemies.length < cap) spawnCaveEnemy(); }
    }
    else if (bossActive){ /* while the boss is out, no normal spawns */ }
    else if (!cheatNoEnemies && (isNight || inEternalNight)){ const cap = ((inEternalNight ? 10 : 5) + Math.floor(dayNum/2)) * pc; if (Math.random() < dt*(inEternalNight?0.28:0.16)*pc && enemies.length < cap) { const a=allPlayers()[Math.floor(Math.random()*pc)]; spawnEnemy(curBiome, a.x, a.y); } } else if (!isNight) { enemies = enemies.filter(e=>e===boss); if (Math.random() < dt*0.08*pc && animals.length < 6*pc && curBiome!==BIOME.SNOW) spawnAnimal(); }
    if (cheatNoEnemies && enemies.length) enemies = enemies.filter(e=>e===boss);
    updateEnemies(dt); updateAnimals(dt);
  }
  if (simSelf) updatePickups();   // host/solo (and anyone in their cave) runs pickup collection
  updateProjectiles(dt); updateParticles(dt);
  
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

  if (player.health<=0 && !cheatGodMode){ if(net.active) respawnInCoop(); else endGame(); }
  updateHUD();
}
// In co-op, dying does NOT reset the shared world (that caused duplicate crystals/items). You respawn and keep your items.
function respawnInCoop(){
  const gx=Math.floor(MAPW/2), gy=Math.floor(MAPH*0.42);
  player.x=gx*TILE+TILE/2; player.y=gy*TILE+TILE/2; player.gridX=gx; player.gridY=gy;
  player.health=player.maxHealth; player.hunger=Math.max(player.hunger, Math.floor(player.maxHunger*0.5));
  showToast('💀 מתת — אבל חזרת לחיים! העולם המשותף ממשיך');
}
function getNightFactor() {
  if (inCave) return 1;   // caves are pitch black day or night — you need torches
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
    // ammo priority: iron > bone > wood
    const arrowType = player.inv.arrowIron>0 ? 'arrowIron' : (player.inv.arrowBone>0 ? 'arrowBone' : (player.inv.arrowWood>0 ? 'arrowWood' : null));
    if (!arrowType){ showToast('אין חצים!'); return; } player.inv[arrowType]--; renderBag();
    const arrowDmg = arrowType==='arrowIron'?7:(arrowType==='arrowBone'?5:3);
    projectiles.push({ x:player.x, y:player.y, vx:dirX*7, vy:dirY*7, dmg: arrowDmg + (crystalActivated?crystalBonusDays+2:0), life:1.2 }); sfxShoot(); return;
  }

  let toolPower = 1 + (player.equipment.axe?1:0) + (player.equipment.iron_axe?2:0) + (player.equipment.pickaxe?1:0) + (player.equipment.iron_pickaxe?2:0) + (player.gatherBonus||0);
  if (player.efficiencyBoostTimer && player.efficiencyBoostTimer > 0) {
      toolPower += 2;
  }

  const breakables = [T.TREE,T.PINE,T.ROCK,T.COAL,T.IRONROCK,T.BUSH,T.CACTUS,T.WALL,T.WALL_THORN,T.BONE_WALL,T.LUCKY,T.CAMPFIRE,T.TRUNK,T.CRAFTING_TABLE,T.UPGRADED_TABLE,T.FURNACE,T.SAPLING,T.SKULL,T.WHEAT,T.CROP,T.CRYSTAL_ORE,T.PLACED_TORCH,T.CAVE_CRYSTAL,T.BEEHIVE,T.GARDEN_TABLE,T.CAVE_WALL];
  
  let hitBlock = false;
  // Mining reach (upgradable via morning bonuses)
  for (let d = 0; d <= (player.breakReach||2); d += 0.5) {
      let fx = player.x + dirX * (d * TILE); let fy = player.y + dirY * (d * TILE); let t = tileAt(fx, fy);
      if (breakables.includes(t.type)){
        t.hp -= toolPower; sfxGather(); spawnParticle(fx,fy,'#fff',5);
        if (d > stats.maxBreakDist) stats.maxBreakDist = d;
        if (t.hp<=0){
          stats.blocksDestroyed++;
          const tx=Math.floor(fx/TILE),ty=Math.floor(fy/TILE); let b = biomeAt(tx, ty); let defaultFloor = inCave ? T.CAVE_FLOOR : ((b===BIOME.DESERT)?T.SAND:(b===BIOME.SNOW)?T.SNOW:T.GRASS);
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
          else if (t.type === T.BEEHIVE) { player.inv.item_beehive=(player.inv.item_beehive||0)+1; world[ty][tx] = {type:defaultFloor, hp:0, timer:0}; showToast('אספת את הכוורת 🐝'); }
          else if (t.type === T.LUCKY) { const savedChoices = t.luckyChoices; world[ty][tx] = {type:defaultFloor, hp:0, timer:0}; openLuckyBlock(savedChoices); }
          else if (t.type === T.CROP) {
              const sp = PLANT_SPECIES[t.species] || PLANT_SPECIES.wheat;
              world[ty][tx] = {type:defaultFloor, hp:0, timer:0};
              if (t.mature) {
                  const prod = sp.product;
                  player.inv[prod] = (player.inv[prod]||0)+1;
                  let seedsGained = Math.random() < 0.20 ? 2 : 1;
                  player.inv.seeds = (player.inv.seeds||0)+seedsGained;
                  showToast(`קטפת ${names[prod]||prod}! (+1, +${seedsGained} זרעים)`);
              } else { player.inv.seeds = (player.inv.seeds||0)+1; showToast('עקרת שתיל צעיר, קיבלת זרע בחזרה 🌱'); }
          }
          else if (t.type === T.WHEAT) {
              player.inv.wheat = (player.inv.wheat || 0) + 1;
              let seedsGained = Math.random() < 0.10 ? 2 : 1; 
              player.inv.seeds = (player.inv.seeds || 0) + seedsGained;
              world[ty][tx] = {type:defaultFloor, hp:0, timer:0};
              showToast(`קצרת חיטה בשלה! 🌾 (+1 חיטה, +${seedsGained} זרעים)`);
          }
          else {
              if (t.type===T.CAVE_CRYSTAL){ player.inv.cave_crystal=(player.inv.cave_crystal||0)+1; if(Math.random()<0.3) player.inv.crystal=(player.inv.crystal||0)+1; }
              if (t.type===T.ROCK){ if(inCave){ player.inv.stone+=3; } else { player.inv.stone+=2; if(Math.random()<0.15) player.inv.iron+=1; } }
              if (t.type===T.COAL) player.inv.coal += inCave?3:2; if (t.type===T.IRONROCK) player.inv.iron += inCave?3:2;
              if (t.type===T.BUSH) player.inv.berry+=1; if (t.type===T.CACTUS) player.inv.wood+=1;
              // CAVE_WALL falls through here: it yields nothing, it's just cleared to floor (no more leaving with 1000 stone)
              world[ty][tx] = {type:defaultFloor, hp:0, timer:0};
          } renderBag();
        } hitBlock = true; break; 
      }
  }
  if (hitBlock) return; 

  let meleeDmg = 4 + (player.equipment.iron_sword ? 4 : 0) + (crystalActivated ? crystalBonusDays+2 : 0);
  if (player.strengthTimer > 0) meleeDmg *= 2;   // ⚔️ strength brew: double melee damage
  const guest = net.active && !net.isHost;
  for (const e of enemies){ if (Math.hypot(e.x-player.x, e.y-player.y) < TILE*1.5){ sfxHit(); spawnParticle(e.x,e.y,'#e04a30',5);
    if (guest){ netSend({ t:'hit', id:e.id, dmg:meleeDmg }); return; }   // host is authoritative over enemy hp
    e.hp -= meleeDmg; enemyHitReaction(e); if(e.hp<=0){ if(e===boss){ onBossDeath(); } enemies=enemies.filter(x=>x!==e); stats.monstersKilled++; player.inv.bones += e.kind==='wolf'?3:e.kind==='siberian_wolf'?4:e.kind==='brute'?5:1; if(e.eatenLoot){ for(const k in e.eatenLoot) player.inv[k]=(player.inv[k]||0)+e.eatenLoot[k]; if(Object.keys(e.eatenLoot).length) showToast('קיבלת בחזרה חומרים שהמפלצת שברה! 🦴📦'); else showToast(`הרגת מפלצת! 🦴`); } else showToast(`הרגת מפלצת! 🦴`); renderBag(); } return; } }
  for (const a of animals){ if (Math.hypot(a.x-player.x, a.y-player.y) < TILE*1.5){ sfxHit();
    if (guest){ netSend({ t:'ahit', x:a.x, y:a.y }); return; }
    a.hp -= meleeDmg; if(a.hp<=0){ animals=animals.filter(x=>x!==a); stats.animalsKilled++; player.inv.meat+=2; player.inv.bones+=1; player.hunger=Math.min(player.maxHunger,player.hunger+15); renderBag(); } return; } }
}

// A position is "lit" if a torch/campfire/furnace is within ~4 tiles -> monsters refuse to spawn there (keeps your lit base safe).
function isNearLight(px, py){
  const tx = Math.floor(px/TILE), ty = Math.floor(py/TILE), R = 4;
  for (let oy=-R; oy<=R; oy++){ for (let ox=-R; ox<=R; ox++){ const cx=tx+ox, cy=ty+oy; if (world[cy] && world[cy][cx]){ const tt = world[cy][cx].type; if (tt===T.PLACED_TORCH || tt===T.CAMPFIRE || tt===T.FURNACE) return true; } } }
  return false;
}
const ENEMY_BASE = { wolf:{hp:6,spd:1.2,dmg:9}, siberian_wolf:{hp:8,spd:1.3,dmg:12}, scorpion:{hp:5,spd:0.8,dmg:8}, zombie:{hp:6,spd:0.9,dmg:8}, wraith:{hp:5,spd:1.6,dmg:10}, brute:{hp:16,spd:0.6,dmg:16}, archer:{hp:6,spd:0.7,dmg:6}, mummy:{hp:11,spd:0.55,dmg:8}, frost_wraith:{hp:7,spd:1.15,dmg:9} };
// Caves are dark and dangerous: monsters lurk close, spawn often, and hit a bit harder. Spawn spot must be walkable floor.
function spawnCaveEnemy(){
  const pool = dayNum>=15 ? ['zombie','wraith','brute','mummy','frost_wraith'] : dayNum>=8 ? ['zombie','wraith','brute','mummy'] : ['zombie','wraith','mummy'];
  const kind = pool[Math.floor(Math.random()*pool.length)];
  const base = ENEMY_BASE[kind]; const scale = 1 + dayNum*0.15;
  let ex, ey, ok=false;
  for (let a=0; a<16 && !ok; a++){ const ang=Math.random()*6.283, dist=140+Math.random()*140; ex=player.x+Math.cos(ang)*dist; ey=player.y+Math.sin(ang)*dist;
    const gx=Math.floor(ex/TILE), gy=Math.floor(ey/TILE); if(gx<1||gy<1||gx>=MAPW-1||gy>=MAPH-1) continue;
    const tt=world[gy][gx]; if(tt && !isSolid(tt) && tt.type!==T.WATER && !isNearLight(ex,ey)) ok=true; }
  if(!ok) return;
  const dmgScale = (1 + Math.max(0, dayNum-5)*0.05) * 1.25;   // cave monsters are tougher
  enemies.push({ id:(++enemyIdSeq), x:ex, y:ey, kind, hp:Math.round(base.hp*scale*1.15), maxHp:Math.round(base.hp*scale*1.15), speed:base.spd*(1+dayNum*0.02), dmg:base.dmg*(1+dayNum*0.04)*dmgScale, facing:'left', stuck:0, eatenLoot:{}, targetsCrystal:false, shootCd:0 });
}
function spawnEnemy(biome, anchorX, anchorY){ const ancX = (anchorX==null)?player.x:anchorX, ancY = (anchorY==null)?player.y:anchorY; let angle=Math.random()*Math.PI*2; const dist=340+Math.random()*100; let kind='zombie'; if (biome===BIOME.FOREST) kind='wolf'; else if (biome===BIOME.SNOW) kind='siberian_wolf'; else if (biome===BIOME.DESERT) kind='scorpion';
  const inEternalNight = eternalNightActive && !crystalActivated;
  // Variety grows with days survived: day10+ brings the big brute, day15+ adds wraiths, day20+ adds archers.
  let r = Math.random();
  if (dayNum>=20 && r<0.15) kind='archer';
  else if (dayNum>=15 && r<0.30) kind='wraith';
  else if (dayNum>=10 && r<0.45) kind='brute';
  if (inEternalNight && Math.random()<0.35){ kind = Math.random()<0.5 ? 'wraith' : (dayNum>=10?'brute':kind); }
  // biome specials
  if (biome===BIOME.DESERT && Math.random()<0.4) kind='mummy';
  else if (biome===BIOME.SNOW && Math.random()<0.4) kind='frost_wraith';
  const scale = 1 + dayNum*0.15; const base = ENEMY_BASE[kind];
  let ex, ey, ok=false;
  for (let attempt=0; attempt<10 && !ok; attempt++){
    ex = ancX+Math.cos(angle)*dist; ey = ancY+Math.sin(angle)*dist;
    ex = Math.max(TILE*3, Math.min((MAPW-3)*TILE, ex)); ey = Math.max(TILE*3, Math.min((MAPH-3)*TILE, ey));
    if (!isNearLight(ex, ey)) ok=true; else angle = Math.random()*Math.PI*2;
  }
  if (!ok) return; // every candidate spot was near light -> skip this spawn
  const targetsCrystal = false; // monsters only ever hunt the player, never the crystal
  // late-game, monsters hit both the player and buildings harder over time
  const dmgScale = 1 + Math.max(0, dayNum-5)*0.05;
  enemies.push({ id:(++enemyIdSeq), x:ex, y:ey, kind, hp:Math.round(base.hp*scale), maxHp:Math.round(base.hp*scale), speed:base.spd*(1+dayNum*0.02), dmg:base.dmg*(1+dayNum*0.04)*dmgScale, facing:'left', stuck:0, eatenLoot:{}, targetsCrystal, shootCd:0 });
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
  // monsters attack your base at night from day 2 (or day 5 in the crystal world), always in eternal night, and always when the boss is out
  const canBreakBlocks = bossActive || eternalNightActive || dayNum >= (gameMode==='crystal' ? eternalNightDay : 2);
  for (const e of enemies){
    // hunt the closest player (host or any teammate)
    let tgt = nearestPlayer(e.x, e.y);
    // 🕯️ calm incense: the local player is invisible to monsters — they retarget a teammate or wander off
    let calmed = (tgt.id==null && player.calmTimer>0 && e.kind!=='boss');
    if (calmed){ let best=null, bd=Infinity; for(const id in remotePlayers){ const r=remotePlayers[id]; const d=Math.hypot(r.x-e.x, r.y-e.y); if(d<bd){ bd=d; best={x:r.x,y:r.y,id}; } } if(best){ tgt=best; calmed=false; } }
    if (calmed){
      e.wanderAng = (e.wanderAng==null || Math.random()<0.02) ? Math.random()*6.283 : e.wanderAng;
      const ws = e.speed*0.4; const wx = e.x+Math.cos(e.wanderAng)*ws, wy = e.y+Math.sin(e.wanderAng)*ws;
      if(!isSolid(tileAt(wx,e.y))) e.x=wx; if(!isSolid(tileAt(e.x,wy))) e.y=wy;
      e.x = Math.max(TILE*2.2, Math.min((MAPW-2.2)*TILE, e.x)); e.y = Math.max(TILE*2.2, Math.min((MAPH-2.2)*TILE, e.y));
      e.chewCd = 0; continue;
    }
    let tx = tgt.x, ty = tgt.y; e.targetId = tgt.id;
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

    // Chew the block directly ahead in discrete hits: shield ring first, then the item's own hit-count.
    // Campfire is NOT meleeable (monsters just cross/burn on it) — only archer arrows can destroy it.
    e.chewCd = (e.chewCd||0) - dt;
    if (canBreakBlocks){
      const bx = e.x + Math.cos(ang)*TILE*0.75, by = e.y + Math.sin(ang)*TILE*0.75;
      const bt = tileAt(bx,by);
      if (PLAYER_BUILT_TILES.includes(bt.type) && bt.type!==T.CAMPFIRE){
        if (bt.def==null){ bt.def = enemyHitsFor(bt.type); bt.defMax = bt.def; }
        if (e.chewCd <= 0){
          e.chewCd = e.kind==='boss' ? 0.25 : 0.5; // boss smashes defenses fast
          const chewAmt = e.kind==='boss' ? 12 : 1;
          if (bt.shield && bt.shield > 0){ bt.shield = Math.max(0, bt.shield - chewAmt); spawnParticle(bx,by,'#c8c8c8',3); }
          else {
            bt.def -= chewAmt; spawnParticle(bx,by,'#fff',3);
            if (bt.type===T.WALL_THORN){ e.hp -= 6; spawnParticle(e.x,e.y,'#8fae4a',3); } // thorns bite back
            if (bt.def <= 0){ const bxi=Math.floor(bx/TILE), byi=Math.floor(by/TILE); destroyBuiltTile(bt, bxi, byi, e); }
          }
        }
      } else { e.chewCd = 0; }
    } else { e.chewCd = 0; }

    // Standing on/near a campfire burns enemies (they can cross it, but it hurts)
    const curTile = tileAt(e.x, e.y);
    if (curTile.type===T.CAMPFIRE){
      e.hp -= dt*9;
      if (Math.random()<dt*4) spawnParticle(e.x, e.y-6, '#ff6a00', 3);
    }

    if (Math.hypot(tx - e.x, ty - e.y) < 14) { damagePlayer(e.targetId, dt * e.dmg); if(e.kind==='frost_wraith' && e.targetId==null && !(player.sweetTimer>0)){ player.slowTimer = 3; } }
  }
  enemies = enemies.filter(e=>{
    if (e.hp<=0){ if(e===boss){ onBossDeath(); } stats.monstersKilled++; if(e.eatenLoot){ for(const k in e.eatenLoot) player.inv[k]=(player.inv[k]||0)+e.eatenLoot[k]; } player.inv.bones+=1; renderBag(); return false; }
    return true;
  });
  for (const p of enemyProjectiles){
    p.x += p.vx*TILE*dt*3; p.y += p.vy*TILE*dt*3; p.life -= dt;
    let hitPl=null; for(const pl of allPlayers()){ if(Math.hypot(pl.x-p.x, pl.y-p.y)<14){ hitPl=pl; break; } }
    if (hitPl){ damagePlayer(hitPl.id, p.dmg); p.life=0; if(hitPl.id==null) sfxHurt(); }
    else {
      const bt = tileAt(p.x,p.y);
      if (PLAYER_BUILT_TILES.includes(bt.type)){   // arrows can hit any built item incl. campfire
        if (bt.def==null){ bt.def = enemyHitsFor(bt.type); bt.defMax = bt.def; }
        if (bt.shield && bt.shield > 0) bt.shield--; else bt.def--;
        p.life=0; spawnParticle(p.x,p.y,'#fff',3);
        if (bt.def <= 0){ const bxi=Math.floor(p.x/TILE), byi=Math.floor(p.y/TILE); destroyBuiltTile(bt, bxi, byi, {eatenLoot:{}}); }
      }
    }
  }
  enemyProjectiles = enemyProjectiles.filter(p=>p.life>0);
}
function revealSpider(a){
  // turn the disguised rabbit into a fast spider enemy right where it stood
  const scale = 1 + dayNum*0.12;
  enemies.push({ id:(++enemyIdSeq), x:a.x, y:a.y, kind:'spider', hp:Math.round(8*scale), maxHp:Math.round(8*scale), speed:1.45*(1+dayNum*0.02), dmg:11*(1+dayNum*0.04), facing:'left', stuck:0, eatenLoot:{}, targetsCrystal:false, shootCd:0 });
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
function updateProjectiles(dt){ const guest = net.active && !net.isHost; for (const p of projectiles){ p.x += p.vx*TILE*dt*4; p.y += p.vy*TILE*dt*4; p.life -= dt; for (const e of enemies){ if (Math.hypot(e.x-p.x,e.y-p.y) < 14){ p.life=0; if(guest){ netSend({ t:'hit', id:e.id, dmg:p.dmg }); break; } e.hp -= p.dmg; enemyHitReaction(e); if(e.hp<=0){ if(e===boss){ onBossDeath(); } enemies=enemies.filter(x=>x!==e); stats.monstersKilled++; player.inv.bones+=2; if(e.eatenLoot){ for(const k in e.eatenLoot) player.inv[k]=(player.inv[k]||0)+e.eatenLoot[k]; } renderBag(); } } } } projectiles = projectiles.filter(p=>p.life>0); }
function spawnParticle(x,y,color,r){ particles.push({x,y,color,r:r||4,life:0.6,vy:-20}); } function updateParticles(dt){ for(const p of particles){ p.life-=dt; p.y+=p.vy*dt; } particles = particles.filter(p=>p.life>0); }
// Dropped-item pickups (used to hand materials to a teammate). Host authoritative in co-op.
window.dropItem = function(k){
  if ((player.inv[k]||0) <= 0) return;
  player.inv[k] -= 1;
  const dx = player.x + (Math.random()*16-8), dy = player.y + 22 + (Math.random()*8);
  if (net.active && !net.isHost){ netSend({ t:'drop', x:dx, y:dy, item:k, count:1 }); }
  else { pickups.push({ id:(++pickupIdSeq), x:dx, y:dy, item:k, count:1, st:performance.now() }); }
  showToast('זרקת '+((names[k]||k).split(' ')[0])); sfxGather(); renderBag();
}
function updatePickups(){
  if (!pickups || !pickups.length) return;
  const now = performance.now();
  for (let i=pickups.length-1;i>=0;i--){ const pk=pickups[i];
    if (now - (pk.st||0) < 1200) continue;   // grace period so the dropper can walk away
    if (Math.hypot(player.x-pk.x, player.y-pk.y) < TILE*0.9){ player.inv[pk.item]=(player.inv[pk.item]||0)+pk.count; sfxGather(); renderBag(); pickups.splice(i,1); continue; }
    let taken=false;
    for (const id in remotePlayers){ const rp=remotePlayers[id]; if (Math.hypot(rp.x-pk.x, rp.y-pk.y) < TILE*0.9){ if(rp._peer) sendToPeer(rp._peer, {t:'reward', items:{[pk.item]:pk.count}}); pickups.splice(i,1); taken=true; break; } }
    if (taken) continue;
  }
}

/* ============ Fishing ============ */
function sfxFishBite(){ beep(880,0.09,'square',0.08); setTimeout(()=>beep(660,0.09,'square',0.08),110); }
// Fish pool with rarity weights. Rarer catches take longer to bite and give better rewards.
const FISH_TABLE = [
  { id:'raw_fish',    name:'🐟 דג נא',    w:46, bite:1.2 },
  { id:'big_fish',    name:'🐠 דג גדול',  w:22, bite:1.1 },
  { id:'pufferfish',  name:'🐡 דג נפוח',  w:12, bite:1.0 },
  { id:'eel',         name:'🐍 צלופח',    w:9,  bite:0.85 },
  { id:'golden_fish', name:'🥇 דג זהב',   w:4,  bite:0.8 },
  { id:'old_boot',    name:'🥾 מגף ישן',  w:5,  bite:1.4, junk:true },
  { id:'treasure',    name:'💰 אוצר',     w:2,  bite:0.7, treasure:true }
];
function rollFish(){ let tot=0; for(const f of FISH_TABLE) tot+=f.w; let r=Math.random()*tot; for(const f of FISH_TABLE){ if((r-=f.w)<0) return f; } return FISH_TABLE[0]; }
function startFishing(tx, ty){
  if (fishing) return;
  const fish = rollFish();
  // rarer fish (low weight) keep you waiting longer; base 2-6s
  const wait = 2 + Math.random()*4 + (fish.w<=4 ? 3 : fish.w<=9 ? 1.5 : 0);
  fishing = { phase:'wait', timer: wait, fish };
  showToast('🎣 מחכה לדג... (~'+Math.round(wait)+' שניות)');
}
function updateFishing(dt){
  if (!fishing) return;
  fishing.timer -= dt;
  if (fishing.phase==='wait' && fishing.timer<=0){ fishing.phase='bite'; fishing.timer=fishing.fish.bite||1.1; sfxFishBite(); showToast('❗ נשיכה! לחץ עכשיו!'); }
  else if (fishing.phase==='bite' && fishing.timer<=0){ fishing=null; showToast('הדג ברח... 🌊'); }
}
function tryFishHook(){
  if (!fishing) return false;
  if (fishing.phase==='bite'){ const f=fishing.fish; fishing=null;
    if (f.junk){ player.inv.wood=(player.inv.wood||0)+1; showToast('דגת '+f.name+' (+1 עץ) 😅'); }
    else if (f.treasure){ player.inv.iron=(player.inv.iron||0)+2; player.inv.coal=(player.inv.coal||0)+2; player.inv.bones=(player.inv.bones||0)+1; showToast('🎉 דגת אוצר! +2 ברזל, +2 פחם, +1 עצם'); }
    else { player.inv[f.id]=(player.inv[f.id]||0)+1; showToast('תפסת '+f.name+'!'); }
    sfxGather(); renderBag(); return true;
  }
  return false;   // hooking too early does nothing (keep waiting)
}

/* ============ Caves dimension ============ */
// Spacious, organized cavern generator (cellular automata) — no biomes, no crystals. Bulk walls are CAVE_WALL (grey, give nothing when mined);
// only ore veins on the exposed wall faces give materials, and they're tougher to mine than on the surface.
function genCaveMap(){
  const wall=[];
  // 1) random fill with a solid border
  for(let y=0;y<MAPH;y++){ wall[y]=[]; for(let x=0;x<MAPW;x++){ wall[y][x] = (x<2||y<2||x>=MAPW-2||y>=MAPH-2) ? true : (Math.random()<0.53); } }
  // 2) smooth it into big open caverns instead of a tight 1-wide maze
  const wc=(g,x,y)=>{ let c=0; for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){ if(dx===0&&dy===0) continue; const nx=x+dx,ny=y+dy; if(nx<0||ny<0||nx>=MAPW||ny>=MAPH||g[ny][nx]) c++; } return c; };
  for(let it=0; it<5; it++){ const ng=[]; for(let y=0;y<MAPH;y++){ ng[y]=[]; for(let x=0;x<MAPW;x++){ if(x<2||y<2||x>=MAPW-2||y>=MAPH-2){ ng[y][x]=true; continue; } ng[y][x] = wc(wall,x,y) >= 5; } } for(let y=0;y<MAPH;y++)for(let x=0;x<MAPW;x++) wall[y][x]=ng[y][x]; }
  // 2b) tidy pass: dissolve lone wall spikes and fill lone floor pockets -> cleaner, more organized cave shapes
  { const ng=[]; for(let y=0;y<MAPH;y++){ ng[y]=[]; for(let x=0;x<MAPW;x++){ if(x<2||y<2||x>=MAPW-2||y>=MAPH-2){ ng[y][x]=true; continue; } const c=wc(wall,x,y); ng[y][x] = wall[y][x] ? (c>=2) : (c>=6); } } for(let y=0;y<MAPH;y++)for(let x=0;x<MAPW;x++) wall[y][x]=ng[y][x]; }
  // 3) keep only the largest connected open area so the whole cave is reachable
  const region=[]; for(let y=0;y<MAPH;y++) region[y]=new Array(MAPW).fill(0);
  let bestId=0, bestSize=0, id=0;
  for(let y=0;y<MAPH;y++)for(let x=0;x<MAPW;x++){ if(!wall[y][x] && region[y][x]===0){ id++; let size=0; const st=[[x,y]]; region[y][x]=id;
    while(st.length){ const [px,py]=st.pop(); size++; for(const [dx,dy] of [[0,-1],[0,1],[-1,0],[1,0]]){ const nx=px+dx,ny=py+dy; if(nx>=0&&ny>=0&&nx<MAPW&&ny<MAPH&&!wall[ny][nx]&&region[ny][nx]===0){ region[ny][nx]=id; st.push([nx,ny]); } } }
    if(size>bestSize){ bestSize=size; bestId=id; } } }
  for(let y=0;y<MAPH;y++)for(let x=0;x<MAPW;x++){ if(!wall[y][x] && region[y][x]!==bestId) wall[y][x]=true; }  // seal tiny disconnected pockets
  // 4) build tiles: floor = CAVE_FLOOR, bulk = CAVE_WALL
  const w=[], floors=[];
  for(let y=0;y<MAPH;y++){ w[y]=[]; for(let x=0;x<MAPW;x++){
    if(wall[y][x]) w[y][x]={type:T.CAVE_WALL, hp:tileHP(T.CAVE_WALL), maxHp:tileHP(T.CAVE_WALL), timer:0};
    else { w[y][x]={type:T.CAVE_FLOOR, hp:0, timer:0}; floors.push([x,y]); }
  } }
  // 5) ore veins ONLY on wall faces exposed to the open cave (so you can see & reach them), tougher hp
  const facesFloor=(x,y)=>{ for(const [dx,dy] of [[0,-1],[0,1],[-1,0],[1,0]]){ const nx=x+dx,ny=y+dy; if(nx>=0&&ny>=0&&nx<MAPW&&ny<MAPH && w[ny][nx].type===T.CAVE_FLOOR) return true; } return false; };
  for(let y=1;y<MAPH-1;y++)for(let x=1;x<MAPW-1;x++){ if(w[y][x].type===T.CAVE_WALL && facesFloor(x,y)){ const n=Math.random();
    if(n<0.05) w[y][x]={type:T.IRONROCK, hp:12, maxHp:12, timer:0};        // iron vein — hard
    else if(n<0.13) w[y][x]={type:T.COAL, hp:8, maxHp:8, timer:0};         // coal vein
    else if(n<0.21) w[y][x]={type:T.ROCK, hp:8, maxHp:8, timer:0};         // stone deposit (only a fraction of the faces, not every wall)
  } }
  // 6) staircase up at the most central open tile
  let sx=2, sy=2, bestD=1e18; const mcx=MAPW/2, mcy=MAPH/2;
  for(const [x,y] of floors){ const d=(x-mcx)*(x-mcx)+(y-mcy)*(y-mcy); if(d<bestD){ bestD=d; sx=x; sy=y; } }
  if(!floors.length){ sx=2; sy=2; w[2][2]={type:T.CAVE_FLOOR,hp:0,timer:0}; }
  w[sy][sx]={type:T.CAVE_UP, hp:tileHP(T.CAVE_UP), timer:0};  // staircase back up
  return { world:w, sx, sy };
}
function enterCave(caveId){
  if (inCave) return;
  // In co-op each player gets their OWN private cave; while underground you're isolated from the shared
  // surface sync (you self-simulate your cave, and you don't send/receive surface tiles or monsters).
  if (!caveId) caveId = 'c0';
  surfaceState = { world, px:player.x, py:player.y, enemies, animals, chests, cropTiles, pickups };
  currentCaveId = caveId;
  let spawnX, spawnY;
  if (caveWorlds[caveId]){ world = caveWorlds[caveId].world; spawnX=caveWorlds[caveId].sx; spawnY=caveWorlds[caveId].sy; }  // return to the SAME saved cave
  else { const cave = genCaveMap(); world = cave.world; caveWorlds[caveId] = { world:cave.world, sx:cave.sx, sy:cave.sy }; spawnX=cave.sx; spawnY=cave.sy; }
  initEntities();
  player.x = spawnX*TILE+TILE/2; player.y = spawnY*TILE+TILE/2; player.gridX=spawnX; player.gridY=spawnY;
  camX=player.x; camY=player.y; inCave=true;
  showToast('🕳️ ירדת למערה — מבוך חשוך, השתמש בלפידים!');
}
function exitCave(){
  if (!inCave || !surfaceState) return;
  if (currentCaveId && caveWorlds[currentCaveId]) caveWorlds[currentCaveId].world = world;  // persist your mining progress
  world = surfaceState.world; enemies=surfaceState.enemies; animals=surfaceState.animals; chests=surfaceState.chests; cropTiles=surfaceState.cropTiles; pickups=surfaceState.pickups||[];
  player.x=surfaceState.px; player.y=surfaceState.py; player.gridX=Math.floor(player.x/TILE); player.gridY=Math.floor(player.y/TILE);
  camX=player.x; camY=player.y; inCave=false; surfaceState=null; currentCaveId=null;
  showToast('☀️ חזרת לפני השטח');
}

// Bone Mummy fires 3 bone shards in random directions whenever it's hit.
function enemyHitReaction(e){
  if (!e) return;
  if (e.kind==='mummy'){ for(let i=0;i<3;i++){ const a=Math.random()*Math.PI*2; enemyProjectiles.push({ x:e.x, y:e.y, vx:Math.cos(a)*5, vy:Math.sin(a)*5, dmg:5, life:1.8, bone:1 }); } spawnParticle(e.x,e.y,'#e8e0d0',4); }
}

/* ============ Safe house ============ */
// enclosed by walls in all 4 directions within 5 tiles, with a heat/light source nearby
function safeHouseState(){
  const gx=player.gridX, gy=player.gridY;
  const wallTypes=[T.WALL, T.BONE_WALL, T.WALL_THORN];
  const dirs=[[0,-1],[0,1],[-1,0],[1,0]];
  for(const [dx,dy] of dirs){ let hit=false; for(let d=1; d<=5; d++){ const x=gx+dx*d, y=gy+dy*d; if(!world[y]||!world[y][x]) break; if(wallTypes.includes(world[y][x].type)){ hit=true; break; } } if(!hit) return { inside:false, buffed:false }; }
  let source=false;
  for(let oy=-5; oy<=5 && !source; oy++) for(let ox=-5; ox<=5; ox++){ const x=gx+ox, y=gy+oy; if(world[y]&&world[y][x]){ const t=world[y][x].type; if(t===T.CAMPFIRE||t===T.FURNACE||t===T.PLACED_TORCH){ source=true; break; } } }
  return { inside:true, buffed:source };
}

/* ============ Beehive & honey ============ */
function updateBeehives(){
  // called ~once per second (host/solo). Beehives near a berry bush accumulate honey and drop a jar every 90s.
  for(let y=0;y<MAPH;y++) for(let x=0;x<MAPW;x++){ const t=world[y][x]; if(!t||t.type!==T.BEEHIVE) continue;
    let nearBush=false;
    for(let oy=-3;oy<=3 && !nearBush;oy++)for(let ox=-3;ox<=3;ox++){ const nx=x+ox, ny=y+oy; if(world[ny]&&world[ny][nx]&&world[ny][nx].type===T.BUSH){ nearBush=true; break; } }
    if(!nearBush){ t.full=false; continue; }
    t.honeyT = (t.honeyT||0) + 1;
    t.full = t.honeyT > 60;   // start buzzing near the end of the cycle
    if(t.honeyT >= 90){ t.honeyT=0; t.full=false;
      // drop a honey jar pickup on an adjacent free spot
      const spots=[[1,0],[-1,0],[0,1],[0,-1]];
      for(const [ox,oy] of spots){ const nx=x+ox, ny=y+oy; if(world[ny]&&world[ny][nx]&&!isSolid(world[ny][nx])&&!isWater(world[ny][nx])){ pickups.push({ id:(++pickupIdSeq), x:nx*TILE+TILE/2, y:ny*TILE+TILE/2, item:'honey_jar', count:1, st:performance.now()-2000 }); break; } }
    }
  }
}

/* ============ Siege boss ============ */
function spawnBoss(){
  const angle=Math.random()*Math.PI*2, dist=200;
  let ex=player.x+Math.cos(angle)*dist, ey=player.y+Math.sin(angle)*dist;
  ex=Math.max(TILE*3, Math.min((MAPW-3)*TILE, ex)); ey=Math.max(TILE*3, Math.min((MAPH-3)*TILE, ey));
  boss = { id:(++enemyIdSeq), x:ex, y:ey, kind:'boss', hp:150, maxHp:150, speed:0.55, dmg:22, facing:'left', chewCd:0, eatenLoot:{}, targetsCrystal:false, big:3 };
  enemies.push(boss); bossActive=true;
  const banner=document.getElementById('bossBanner'); if(banner){ banner.textContent='רוח המדבר העתיקה התעוררה! 👑'; banner.classList.add('show'); setTimeout(()=>banner.classList.remove('show'), 6000); }
  showToast('👑 בוס הופיע! הגן על הבסיס');
}
function onBossDeath(){
  bossActive=false;
  player.inv.bones=(player.inv.bones||0)+10; player.inv.iron_ingot=(player.inv.iron_ingot||0)+5;
  player.maxHealth += 20; player.health = player.maxHealth;   // Crystal Heart
  showToast('👑 ניצחת את הבוס! 💖 לב קריסטל: +20 חיים מקס׳ ומילוי מלא, +10 עצמות, +5 ברזל מחומם');
  boss=null; renderBag(); updateHUD();
}

let openChestRef = null; function openChest(c){ openChestRef = c; document.getElementById('chestPanel').classList.add('open'); renderChest(); } function closeChest(){ document.getElementById('chestPanel').classList.remove('open'); openChestRef=null; } function renderChest(){ const list = document.getElementById('chestList'); list.innerHTML = ''; const keys = ['wood','stone','coal','iron','iron_ingot','berry','meat','bones','wheat','seeds','bowl','dough','bread','cooked_meat','fruit_salad']; keys.forEach(k=>{ if(player.inv[k]!==undefined){ const row = document.createElement('div'); row.className='chestRow'; row.innerHTML = `<span>${names[k]}: תיק ${player.inv[k]||0} | תיבה ${openChestRef.items[k]||0}</span><span><button onclick="chestTransfer('${k}',1)">➡️</button><button onclick="chestTransfer('${k}',-1)">⬅️</button></span>`; list.appendChild(row); } }); } function chestTransfer(k, dir){ if (!openChestRef) return; if (dir>0){ if ((player.inv[k]||0)>0){ player.inv[k]--; openChestRef.items[k]=(openChestRef.items[k]||0)+1; } } else { if ((openChestRef.items[k]||0)>0){ openChestRef.items[k]--; player.inv[k]=(player.inv[k]||0)+1; } } renderChest(); renderBag(); }
function endGame(){ gameOver=true; document.getElementById('msg').style.display='block'; document.getElementById('survivedDays').textContent=dayNum; } function restart(){ document.getElementById('msg').style.display='none'; initGame(); }

/* ============ World selection start screen ============ */
const WORLD_TEST_CODE = '2020';
function startWorld(mode){
  netReset();
  gameMode = mode;
  document.getElementById('worldSelect').style.display = 'none';
  initGame();
  gameStarted = true;
  ensureAudio();
  if (mode==='survival') showToast('🌙 הישרדות רגילה — לילות רגילים, בלי לילה נצחי');
  else if (mode==='challenge') showToast('⚔️ אתגר! הלילה הנצחי יתחיל ביום השני');
  else if (mode==='test') showToast('🧪 עולם ניסיון — כל הבלוקים והחומרים אצלך');
}
/* ---- shared-world submenu ---- */
let sharedMode = 'crystal';
function openSharedMenu(){ document.getElementById('wsMain').style.display='none'; document.getElementById('sharedMenu').style.display='flex'; setSharedMode('crystal'); }
function closeSharedMenu(){ document.getElementById('sharedMenu').style.display='none'; document.getElementById('wsMain').style.display='block'; }
function setSharedMode(m){ sharedMode = m;
  document.getElementById('sharedCrystalCard').classList.toggle('sel', m==='crystal');
  document.getElementById('sharedSurvivalCard').classList.toggle('sel', m==='survival');
  document.getElementById('sharedChallengeCard').classList.toggle('sel', m==='challenge');
}
function sharedSolo(){ startWorld(sharedMode); }

/* ============ P2P co-op via PeerJS: short numeric room codes, auto-connect, works on a hotspot with internet ============ */
const NET_PREFIX = 'joni-surv-';   // namespaced so our 4-digit codes don't clash with other apps on the public broker
function peerReady(){ return typeof Peer !== 'undefined'; }
// Load PeerJS on demand with fallback CDNs (the <head> preload may be slow or blocked).
let _peerLoading = null;
function ensurePeerJs(){
  if (typeof Peer !== 'undefined') return Promise.resolve(true);
  if (_peerLoading) return _peerLoading;
  const urls = [
    'https://unpkg.com/peerjs@1.5.4/dist/peerjs.min.js',
    'https://cdn.jsdelivr.net/npm/peerjs@1.5.4/dist/peerjs.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/peerjs/1.5.4/peerjs.min.js'
  ];
  _peerLoading = new Promise(resolve=>{
    let i=0;
    (function tryNext(){
      if (typeof Peer !== 'undefined') return resolve(true);
      if (i>=urls.length){ _peerLoading=null; return resolve(false); }
      const s=document.createElement('script'); s.src=urls[i++];
      s.onload=()=>{ if(typeof Peer!=='undefined') resolve(true); else tryNext(); };
      s.onerror=tryNext;
      document.head.appendChild(s);
    })();
  });
  return _peerLoading;
}
function initShadow(){ netShadow = []; for(let y=0;y<MAPH;y++){ netShadow[y]=[]; for(let x=0;x<MAPW;x++) netShadow[y][x]=world[y][x].type; } }
function makeShortCode(){ return String(1000 + Math.floor(Math.random()*9000)); } // fixed 4-digit room code 1000..9999

function openNetPanel(mode){
  document.getElementById('netPanel').classList.add('open');
  document.getElementById('netHostView').style.display = mode==='host'?'block':'none';
  document.getElementById('netJoinView').style.display = mode==='join'?'block':'none';
  document.getElementById('netTitle').textContent = mode==='host'?'📡 פתח לחברים':'🔗 הצטרף לחבר';
  document.getElementById('netStatus').textContent = mode==='host'?'יוצר קוד...':'הכנס את הקוד מהמארח';
}
function closeNetPanel(){ document.getElementById('netPanel').classList.remove('open'); }

function setConnBanner(show){ const b=document.getElementById('connBanner'); if(b) b.classList.toggle('show', !!show); }
function netWireConn(peer){
  const c = peer.conn; if(!c) return;
  c.on('open', ()=>{ peer.open=true; net.wasConnected=true; setConnBanner(false); document.getElementById('netStatus').textContent='מחובר! 🎉'; showToast('🔗 שחקן התחבר לעולם!'); if(net.isHost) netSendInitTo(peer); setTimeout(closeNetPanel, 900); });
  c.on('data', d=> netOnMessage(peer, d));
  c.on('close', ()=>{ peer.open=false; net.peers = net.peers.filter(p=>p!==peer); if(!net.isHost && net.active) setConnBanner(true); });
  c.on('error', ()=>{});
}
function sharedHost(){
  startWorld(sharedMode);
  net.active=true; net.isHost=true; net.name=playerName||'מארח'; net.peers=[]; initShadow();
  openNetPanel('host');
  document.getElementById('netHostCode').value = '····';
  document.getElementById('netStatus').textContent = 'טוען חיבור...';
  ensurePeerJs().then(ok=>{ if(ok) netHostRetry(0); else document.getElementById('netStatus').textContent='אין אינטרנט או שהחיבור חסום — התחבר לאינטרנט ונסה שוב'; });
}
function netHostRetry(attempt){
  if (attempt > 8){ document.getElementById('netStatus').textContent='לא הצלחתי ליצור קוד — נסה שוב'; return; }
  const code = makeShortCode();
  try{ net.peerObj = new Peer(NET_PREFIX+code, { debug:0 }); }catch(e){ document.getElementById('netStatus').textContent='שגיאה ביצירת חיבור'; return; }
  net.myCode = code;
  net.peerObj.on('open', ()=>{ document.getElementById('netHostCode').value = code; document.getElementById('netStatus').textContent='מסור לחבר את הקוד והמתן שיצטרף'; });
  net.peerObj.on('connection', conn=>{ const peer={ conn, id:conn.peer, open:false }; net.peers.push(peer); netWireConn(peer); });
  // if the broker link drops (internet blip), get back on it so guests keep the SAME code and can reconnect
  net.peerObj.on('disconnected', ()=>{ if(net.active && net.isHost){ try{ net.peerObj.reconnect(); }catch(e){} } });
  net.peerObj.on('error', err=>{ const t=String(err&&err.type||err||''); if (t.includes('unavailable-id')||t.includes('taken')){ try{net.peerObj.destroy();}catch(e){} netHostRetry(attempt+1); } else if (t.includes('network')||t.includes('server')){ document.getElementById('netStatus').textContent='אין חיבור לשרת — בדוק אינטרנט'; } });
}
function sharedJoin(){
  // always open the panel (on TOP of the menu) so the code field is available; PeerJS loads in the background
  net.active=true; net.isHost=false; net.name=playerName||'אורח'; net.peers=[];
  openNetPanel('join');
  showToast('🔗 הכנס את הקוד של החבר');
  // focus the input synchronously (inside the tap) so the keyboard pops up on mobile
  const inp = document.getElementById('netJoinCode');
  if (inp){ inp.value=''; try{ inp.focus(); }catch(e){} }
  ensurePeerJs().then(ok=>{ if(!ok) document.getElementById('netStatus').textContent='אין אינטרנט או שהחיבור חסום — התחבר לאינטרנט'; });
}
function netGuestConnect(){
  if (!net.peerObj || !net.hostCode) return;
  const conn = net.peerObj.connect(NET_PREFIX+net.hostCode, { reliable:true });
  const peer = { conn, id:'host', open:false }; net.peers=[peer]; netWireConn(peer);
}
function netDoJoin(){
  const code = (document.getElementById('netJoinCode').value||'').replace(/[^0-9]/g,'').trim();
  if (!code){ showToast('הכנס קוד'); return; }
  net.hostCode = code;
  document.getElementById('netStatus').textContent='טוען חיבור...';
  ensurePeerJs().then(ok=>{
    if (!ok){ document.getElementById('netStatus').textContent='אין אינטרנט או שהחיבור חסום — התחבר לאינטרנט ונסה שוב'; return; }
    document.getElementById('netStatus').textContent='מתחבר...';
    try{ net.peerObj = new Peer({ debug:0 }); }catch(e){ document.getElementById('netStatus').textContent='שגיאת חיבור'; return; }
    net.peerObj.on('open', ()=>{
      netGuestConnect();
      setTimeout(()=>{ if(net.peers[0] && !net.peers[0].open) document.getElementById('netStatus').textContent='לא נמצא מארח עם הקוד הזה — בדוק את הקוד ואת האינטרנט'; }, 7000);
    });
    // keep the broker link alive so we can reconnect after an internet blip
    net.peerObj.on('disconnected', ()=>{ if(net.active && !net.isHost){ try{ net.peerObj.reconnect(); }catch(e){} } });
    net.peerObj.on('error', err=>{ document.getElementById('netStatus').textContent='שגיאה — בדוק את הקוד והאינטרנט'; });
  });
}
// Robust copy that also works in insecure contexts (data: link / Shortcut) where the clipboard API is blocked:
// we always visibly SELECT the text so the user can copy with the phone's own menu if the API fails.
function copyTextFrom(el){
  let text='';
  try{
    if (el.tagName==='TEXTAREA' || el.tagName==='INPUT'){ const wasRO=el.readOnly; el.readOnly=false; el.focus(); el.select(); try{ el.setSelectionRange(0, (el.value||'').length); }catch(e){} el.readOnly=wasRO; text=el.value; }
    else { const r=document.createRange(); r.selectNodeContents(el); const s=window.getSelection(); s.removeAllRanges(); s.addRange(r); text=el.textContent; }
  }catch(e){}
  let ok=false;
  try{ ok=document.execCommand && document.execCommand('copy'); }catch(e){}
  if(!ok && navigator.clipboard && navigator.clipboard.writeText){ try{ navigator.clipboard.writeText(text); ok=true; }catch(e){} }
  return ok;
}
function copyHostCode(){ const el=document.getElementById('netHostCode'); const ok=copyTextFrom(el); const code=el.value||el.textContent; showToast(ok ? ('הקוד הועתק 📋: '+code) : ('הקוד מסומן — לחץ "העתק" מהתפריט של הטלפון 📋')); }

function sendToPeer(peer, obj){ if(peer && peer.conn && peer.open){ try{ peer.conn.send(obj); }catch(e){} } }
function netSend(obj){ for(const p of net.peers) sendToPeer(p, obj); }
function netRelay(except, obj){ for(const p of net.peers){ if(p!==except) sendToPeer(p, obj); } }
function netSendInitTo(peer){
  sendToPeer(peer, { t:'init', world:serializeWorld(), dayNum, time, gameMode, eternalNightDay, en:(eternalNightActive&&!crystalActivated), crystalPlaced, crystalActivated, crystalDevicePos, perm:guestCheatsAllowed, cyc:CYCLE_LEN, dusk:DUSK_LEN, dawn:DAWN_LEN, chests:chests.map(c=>({x:c.x,y:c.y,items:c.items})) });
}
function applyNetInit(msg){
  gameMode = msg.gameMode||'crystal';
  initEntities(); deserializeWorld(msg.world); initShadow(); initPlayer();
  dayNum=msg.dayNum||1; time=msg.time||0; eternalNightDay=msg.eternalNightDay||5;
  eternalNightActive=!!msg.en; crystalPlaced=!!msg.crystalPlaced; crystalActivated=!!msg.crystalActivated; crystalDevicePos=msg.crystalDevicePos||null;
  if (msg.cyc) CYCLE_LEN=msg.cyc; if (msg.dusk) DUSK_LEN=msg.dusk; if (msg.dawn) DAWN_LEN=msg.dawn;   // match host's day length
  chests = (msg.chests||[]).map(c=>({x:c.x,y:c.y,items:c.items||{}}));
  cropTiles = []; for(let y=0;y<MAPH;y++)for(let x=0;x<MAPW;x++){ const c=world[y][x]; if(c.type===T.CROP){ if(!c.species) c.species='wheat'; c.cx=x; c.cy=y; if(c.mature){ c.stage=3; c.bred=true; } else { c.growAt = performance.now()+opCropGrowSeconds*1000; cropTiles.push(c); } } }
  guestCheatsAllowed = !!msg.perm;
  resetStats(); gameOver=false; tickAcc=0; countTimer=0; bonusShownForDay=dayNum; luckyQueue=[];
  camX=player.x; camY=player.y;
  document.getElementById('worldSelect').style.display='none'; closeNetPanel();
  gameStarted=true; ensureAudio(); updateHUD(); renderBag(); changeUIScale(1.2); updateResourceCounts();
  showToast('🔗 נכנסת לעולם המשותף!');
}
function applyNetTiles(cells){
  if (inCave) return;   // I'm underground in my private cave — don't let surface tile updates overwrite it
  for(const c of cells){ const [x,y,type,hp,maxHp,stage,species,mature]=c; if(world[y]&&world[y][x]){ const tile={type,hp,timer:0}; if(maxHp)tile.maxHp=maxHp; if(stage)tile.stage=stage;
    if(PLAYER_BUILT_TILES.includes(type)){ tile.def=enemyHitsFor(type); tile.defMax=tile.def; }
    if(type===T.CROP){ tile.species = species || 'wheat'; tile.cx=x; tile.cy=y; tile.stage=stage||0; if(mature){ tile.mature=true; tile.stage=3; tile.bred=true; } else { tile.growAt = performance.now()+opCropGrowSeconds*1000; cropTiles.push(tile); } }  // both host & guest grow the crop locally
    world[y][x]=tile; if(netShadow) netShadow[y][x]=type; } }
}
function netOnMessage(peer, msg){
  try { netHandleMessage(peer, msg); } catch(e){ console.error('net message error', e); }
}
function netHandleMessage(peer, msg){
  if (!msg || typeof msg!=='object') { try{ msg=JSON.parse(msg); }catch(e){ return; } }
  if (msg.t==='init'){ applyNetInit(msg); return; }
  if (msg.t==='p'){ const prev=remotePlayers[msg.id]; const moved = prev && (Math.abs((prev.tx!=null?prev.tx:prev.x)-msg.x)>0.5||Math.abs((prev.ty!=null?prev.ty:prev.y)-msg.y)>0.5);
    remotePlayers[msg.id]={ x: prev?prev.x:msg.x, y: prev?prev.y:msg.y, tx:msg.x, ty:msg.y, facing:msg.facing, hp:msg.hp, name:msg.name, color:msg.color, torch:msg.torch, last:performance.now(), lastMove: moved?performance.now():((prev&&prev.lastMove)||0), wf:((prev&&prev.wf)||0), kills:((prev&&prev.kills)|0), _peer: net.isHost?peer:null };
    if(net.isHost) netRelay(peer, msg); return; }
  if (msg.t==='tiles'){ applyNetTiles(msg.cells); if(net.isHost) netRelay(peer, msg); return; }
  if (msg.t==='time'){ if(!net.isHost){ dayNum=msg.dayNum; time=msg.time; eternalNightActive=msg.en; if(msg.cyc)CYCLE_LEN=msg.cyc; if(msg.dusk)DUSK_LEN=msg.dusk; if(msg.dawn)DAWN_LEN=msg.dawn; } return; }
  if (msg.t==='ent'){ if(!net.isHost) applyNetEntities(msg); return; }               // guest: render host's monsters/animals/pickups/chests
  if (msg.t==='dmg'){ if(msg.to===net.selfId && !cheatGodMode && !inCave){ let amt=msg.amt; if(player.equipment.bone_shield){ amt*=0.75; for(let i=0;i<3;i++) spawnParticle(player.x+(Math.random()*16-8), player.y+(Math.random()*16-8), '#fff', 3); } player.health -= amt; if(!player.hurtSfxCd||player.hurtSfxCd<=0){ sfxHurt(); player.hurtSfxCd=0.5; } } return; }  // a monster hit me on the host's sim
  if (msg.t==='hit'){ if(net.isHost) hostApplyHit(msg, peer); return; }               // host: a guest damaged a monster
  if (msg.t==='ahit'){ if(net.isHost){ const a=animals.find(an=>Math.hypot(an.x-msg.x,an.y-msg.y)<24); if(a){ if(a.isSpider){ revealSpider(a); } else { animals=animals.filter(x=>x!==a); sendToPeer(peer,{t:'reward', items:{meat:2,bones:1}, hunger:15}); } } } return; }  // host: guest killed an animal -> reward the guest
  if (msg.t==='reward'){ if(msg.items){ for(const k in msg.items) player.inv[k]=(player.inv[k]||0)+msg.items[k]; } if(msg.hunger) player.hunger=Math.min(player.maxHunger, player.hunger+msg.hunger); renderBag(); return; }  // guest: got loot for a kill
  if (msg.t==='drop'){ if(net.isHost){ pickups.push({ id:(++pickupIdSeq), x:msg.x, y:msg.y, item:msg.item, count:msg.count }); } return; }  // host: register a dropped item
  if (msg.t==='chest_add'){ if(net.isHost){ chests.push({x:msg.x, y:msg.y, items:{}}); } return; }
  if (msg.t==='perm'){ if(!net.isHost){ guestCheatsAllowed = !!msg.cheats; showToast(msg.cheats?'🤝 המארח איפשר לך צ׳יטים':'🔒 המארח חסם צ׳יטים'); } return; }
}
function applyNetEntities(msg){
  if (inCave) return;   // ignore the host's surface monsters while I'm in my private cave (I sim my own)
  // update enemies by id so we can smoothly interpolate them (targets tx/ty) instead of teleporting
  const incoming = msg.e||[]; const byId={}; for(const e of enemies) byId[e.id]=e;
  const next=[];
  for(const s of incoming){ let e=byId[s.id]; if(e){ e.tx=s.x; e.ty=s.y; e.hp=s.hp; e.maxHp=s.mh; e.facing=s.f; } else { e={ id:s.id, x:s.x, y:s.y, tx:s.x, ty:s.y, kind:s.k, hp:s.hp, maxHp:s.mh, facing:s.f }; } next.push(e); }
  enemies = next;
  animals = (msg.a||[]).map(a=>({ x:a.x, y:a.y, isSpider:!!a.s, hp:3, maxHp:3 }));
  pickups = (msg.pk||[]).map(pk=>({ id:pk.id, x:pk.x, y:pk.y, item:pk.item, count:pk.count }));
  if (msg.ch) chests = msg.ch.map(c=>({x:c.x,y:c.y,items:c.items||{}}));
}
function hostApplyHit(msg, peer){
  const e = enemies.find(en=>en.id===msg.id); if(!e) return;
  e.hp -= msg.dmg; enemyHitReaction(e);
  spawnParticle(e.x, e.y, '#e04a30', 4);
  if (e.hp<=0){ if(e===boss){ onBossDeath(); } enemies = enemies.filter(en=>en!==e);
    // credit the kill to the GUEST who landed it (not the host), so each player's count is their own
    let credited=false;
    for (const id in remotePlayers){ if (remotePlayers[id]._peer===peer){ remotePlayers[id].kills=(remotePlayers[id].kills|0)+1; credited=true; break; } }
    if (!credited) stats.monstersKilled++;
    const bones = e.kind==='wolf'?3:e.kind==='siberian_wolf'?4:e.kind==='brute'?5:2;
    sendToPeer(peer, { t:'reward', items:{ bones } });   // the guest who killed it gets the loot
  }
}
function netSendDiff(){
  if (!netShadow) return;
  const cells=[];
  for(let y=0;y<MAPH;y++) for(let x=0;x<MAPW;x++){ const t=world[y][x]; if(netShadow[y][x]!==t.type){ netShadow[y][x]=t.type; cells.push([x,y,t.type,t.hp,t.maxHp||0,t.stage||0,t.species||0,t.mature?1:0]); } }
  if (cells.length) netSend({ t:'tiles', cells });
}
function netTick(dt){
  const now=performance.now();
  // guest self-heal: if the connection to the host is down, keep trying to reconnect to the same code
  if (!net.isHost && net.active && net.hostCode){
    const hasOpen = net.peers.some(p=>p.open);
    if (hasOpen){ if(net.wasConnected===false){ net.wasConnected=true; } setConnBanner(false); }
    else if (net.wasConnected && now - net.lastReconnect > 3000){
      net.lastReconnect = now; setConnBanner(true);
      try{
        if (!net.peerObj || net.peerObj.destroyed){ net.peerObj = new Peer({ debug:0 }); net.peerObj.on('open', netGuestConnect); net.peerObj.on('disconnected', ()=>{ try{net.peerObj.reconnect();}catch(e){} }); }
        else if (net.peerObj.disconnected){ try{ net.peerObj.reconnect(); }catch(e){} setTimeout(netGuestConnect, 800); }
        else netGuestConnect();
      }catch(e){}
    }
  }
  // smooth interpolation of remote players (and guest-side enemies) toward their latest network positions
  for (const id in remotePlayers){ const rp=remotePlayers[id]; if(rp.tx!=null){ rp.x += (rp.tx-rp.x)*0.3; rp.y += (rp.ty-rp.y)*0.3; } }
  if (!net.isHost){ for (const e of enemies){ if(e.tx!=null){ e.x += (e.tx-e.x)*0.35; e.y += (e.ty-e.y)*0.35; } } }
  if (!inCave && now-netLastPos > 80){ netLastPos=now; netSend({ t:'p', id:net.selfId, x:Math.round(player.x), y:Math.round(player.y), facing:player.facing, hp:Math.round(player.health), name:net.name, color:playerSkin, torch:((player.inv.torch||0)>0)?1:0 }); }
  if (!inCave && net.isHost && now-netLastEnt > 90){
    netLastEnt = now;
    // broadcast every monster + animal + pickup + chest so guests see (and can fight) the same threats & items
    const es = enemies.map(e=>({ id:e.id, x:Math.round(e.x), y:Math.round(e.y), k:e.kind, hp:e.hp, mh:e.maxHp, f:e.facing }));
    const as = animals.map(a=>({ x:Math.round(a.x), y:Math.round(a.y), s:a.isSpider?1:0 }));
    const pk = pickups.map(p=>({ id:p.id, x:Math.round(p.x), y:Math.round(p.y), item:p.item, count:p.count }));
    const ch = chests.map(c=>({ x:c.x, y:c.y, items:c.items }));
    netSend({ t:'ent', e:es, a:as, pk, ch });
    // pay out accumulated damage to each guest
    for (const id in netGuestDmg){ if (netGuestDmg[id] > 0.4){ netSend({ t:'dmg', to:id, amt:netGuestDmg[id] }); netGuestDmg[id]=0; } }
  }
  if (now-netLastDiff > 500){ netLastDiff=now; if(!inCave) netSendDiff(); if(net.isHost) netSend({ t:'time', dayNum, time, en:(eternalNightActive&&!crystalActivated), cyc:CYCLE_LEN, dusk:DUSK_LEN, dawn:DAWN_LEN }); }
  for (const id in remotePlayers){ if (now - remotePlayers[id].last > 3500) delete remotePlayers[id]; }
}
function netReset(){
  for (const p of net.peers){ try{ p.conn && p.conn.close(); }catch(e){} }
  if (net.peerObj){ try{ net.peerObj.destroy(); }catch(e){} net.peerObj=null; }
  net.active=false; net.isHost=false; net.peers=[]; net._pendingHostPeer=null;
  net.hostCode=null; net.wasConnected=false; net.lastReconnect=0;
  remotePlayers={}; netShadow=null; netGuestDmg={}; setConnBanner(false); closeNetPanel();
}
function drawRemotePlayers(){
  if (inCave) return;   // teammates are on the surface; don't draw them inside my private cave
  const now=performance.now();
  for (const id in remotePlayers){ const rp=remotePlayers[id];
    const moving = (now - (rp.lastMove||0)) < 320;
    if (moving) rp.wf = (rp.wf||0) + 0.35;
    const bob = moving ? Math.sin(rp.wf)*2 : 0, feet = moving ? Math.sin(rp.wf)*4 : 0;
    ctx.save(); ctx.translate(rp.x, rp.y);
    ctx.fillStyle='rgba(0,0,0,0.2)'; ctx.beginPath(); ctx.ellipse(0,9,8,3,0,0,6.3); ctx.fill();
    ctx.fillStyle='#3a2212'; ctx.fillRect(-4+feet,6,3,3); ctx.fillRect(1-feet,6,3,3);
    // little backpack behind the body
    ctx.fillStyle='#7a4a2a'; ctx.fillRect(-6,-3+bob,3,8);
    ctx.fillStyle = rp.color || '#8a5f2f'; ctx.fillRect(-5,-4+bob,10,10);
    ctx.fillStyle='#ffd1a9'; ctx.beginPath(); ctx.arc(0,-9+bob,5,0,6.3); ctx.fill();
    // hair cap
    ctx.fillStyle='#5a3a1e'; ctx.beginPath(); ctx.arc(0,-10+bob,5.2,3.14,0); ctx.fill();
    // show which way the teammate is looking
    let fdx=0, fdy=0; const f=rp.facing||'down';
    if(f.includes('right'))fdx=1; if(f.includes('left'))fdx=-1; if(f.includes('down'))fdy=1; if(f.includes('up'))fdy=-1;
    if(fdx!==0&&fdy!==0){ fdx*=0.7; fdy*=0.7; } else if(fdx===0&&fdy===0){ fdy=1; }
    ctx.strokeStyle='rgba(255,255,255,0.55)'; ctx.lineWidth=2; ctx.setLineDash([3,3]); ctx.beginPath(); ctx.moveTo(0,-2+bob); ctx.lineTo(fdx*20, -2+bob+fdy*20); ctx.stroke(); ctx.setLineDash([]);
    ctx.fillStyle='rgba(255,255,255,0.8)'; ctx.beginPath(); ctx.arc(fdx*22, -2+bob+fdy*22, 2.5, 0, 6.3); ctx.fill();
    if (rp.torch){ ctx.fillStyle='#ff9a3d'; ctx.beginPath(); ctx.ellipse(6,-8+bob,3,5,0,0,6.3); ctx.fill(); }
    if (showPlayerNames){ const nm=(rp.name||'שחקן'); ctx.font='9px "Courier New", monospace'; ctx.textAlign='center';
      const w=ctx.measureText(nm).width+8; ctx.fillStyle='rgba(0,0,0,0.6)'; ctx.fillRect(-w/2,-27,w,12);
      ctx.fillStyle='#8fe08f'; ctx.fillText(nm, 0, -18); ctx.textAlign='start'; }
    ctx.restore();
  }
}

function showWorldSelect(){
  netReset();
  gameStarted = false;
  document.getElementById('msg').style.display='none';
  document.getElementById('sharedMenu').style.display='none';
  document.getElementById('wsMain').style.display='block';
  document.getElementById('worldSelect').style.display='flex';
  refreshSavesUI();
}
function askWorldCode(){ document.getElementById('wsCodeWrap').style.display = 'flex'; document.getElementById('wsCodeInput').focus(); }

/* ============ World save / load (localStorage) ============ */
const SAVE_INDEX_KEY = 'sv_index';
// Compact serialization: run-length-encoded tile types + sparse extras (only tiles carrying state).
// Keeps a full 80x60 world down to a few KB so it fits in localStorage.
function serializeWorld(){
  const types = new Array(MAPW*MAPH); const extras = {};
  for (let y=0;y<MAPH;y++) for (let x=0;x<MAPW;x++){
    const t=world[y][x]; const i=y*MAPW+x; types[i]=t.type; const e={};
    // Only store what CAN'T be derived from the tile type on load — a fresh wall now stores nothing.
    if (t.hp!=null && t.hp!==tileHP(t.type)) e.hp=t.hp;
    if (t.maxHp!=null && t.maxHp!==tileHP(t.type)) e.m=t.maxHp;
    const dMax = enemyHitsFor(t.type);
    if (t.defMax!=null && t.defMax!==dMax) e.dm=t.defMax;
    if (t.def!=null){ const cur = (t.defMax!=null?t.defMax:dMax); if (t.def!==cur) e.d=t.def; }   // only when damaged
    if (t.shield) e.sh=t.shield; if (t.shieldMax) e.shm=t.shieldMax;
    if (t.reinforced) e.r=t.reinforced; if (t.stage) e.s=t.stage;                                 // stage 0 omitted
    if (t.species && t.species!=='wheat') e.sp=t.species; if (t.mature) e.mt=1;                    // default 'wheat' omitted
    if (Object.keys(e).length) extras[i]=e;
  }
  const rle=[]; let prev=types[0], cnt=1;
  for (let i=1;i<types.length;i++){ if(types[i]===prev) cnt++; else { rle.push(prev,cnt); prev=types[i]; cnt=1; } }
  rle.push(prev,cnt);
  return { rle, extras };
}
function deserializeWorld(w){
  world=[]; for(let y=0;y<MAPH;y++) world[y]=new Array(MAPW);
  if (Array.isArray(w)){ // legacy array-of-rows format
    for(let y=0;y<MAPH;y++) for(let x=0;x<MAPW;x++){ const o=w[y][x]; const tile={type:o.t,hp:o.hp,timer:0}; if(o.m!=null)tile.maxHp=o.m; if(o.s!=null)tile.stage=o.s; if(o.r)tile.reinforced=o.r; world[y][x]=tile; }
    return;
  }
  const types=new Array(MAPW*MAPH); let idx=0;
  const rle=w.rle||[]; for(let i=0;i<rle.length;i+=2){ const val=rle[i], n=rle[i+1]; for(let k=0;k<n;k++) types[idx++]=val; }
  const extras=w.extras||{};
  for(let i=0;i<MAPW*MAPH;i++){ const x=i%MAPW, y=Math.floor(i/MAPW); const type=types[i]==null?T.GRASS:types[i]; const tile={type,timer:0}; const e=extras[i];
    tile.hp = (e && e.hp!=null) ? e.hp : tileHP(type);
    tile.maxHp = (e && e.m!=null) ? e.m : tileHP(type);
    if (PLAYER_BUILT_TILES.includes(type)){ tile.defMax = (e && e.dm!=null) ? e.dm : enemyHitsFor(type); tile.def = (e && e.d!=null) ? e.d : tile.defMax; }
    else if (e){ if(e.d!=null)tile.def=e.d; if(e.dm!=null)tile.defMax=e.dm; }
    if (e){ if(e.sh)tile.shield=e.sh; if(e.shm)tile.shieldMax=e.shm; if(e.r)tile.reinforced=e.r; if(e.s!=null)tile.stage=e.s; if(e.sp)tile.species=e.sp; if(e.mt)tile.mature=true; }
    world[y][x]=tile;
  }
}
// Minimal per-tile signature: type + only the fields that can't be derived. Used to diff against the seeded base.
function tileSig(t){
  const o={t:t.type}; const hp=tileHP(t.type);
  if (t.hp!=null && t.hp!==hp) o.hp=t.hp;
  if (t.maxHp!=null && t.maxHp!==hp) o.m=t.maxHp;
  const dMax=enemyHitsFor(t.type);
  if (t.defMax!=null && t.defMax!==dMax) o.dm=t.defMax;
  if (t.def!=null){ const cur=(t.defMax!=null?t.defMax:dMax); if(t.def!==cur) o.d=t.def; }
  if (t.shield) o.sh=t.shield; if (t.shieldMax) o.shm=t.shieldMax;
  if (t.reinforced) o.r=t.reinforced; if (t.stage) o.s=t.stage;
  if (t.species && t.species!=='wheat') o.sp=t.species; if (t.mature) o.mt=1;
  return o;
}
function tileFromSig(o){
  const type=o.t; const tile={type,timer:0};
  tile.hp=(o.hp!=null)?o.hp:tileHP(type);
  tile.maxHp=(o.m!=null)?o.m:tileHP(type);
  if (PLAYER_BUILT_TILES.includes(type)){ tile.defMax=(o.dm!=null)?o.dm:enemyHitsFor(type); tile.def=(o.d!=null)?o.d:tile.defMax; }
  else { if(o.d!=null)tile.def=o.d; if(o.dm!=null)tile.defMax=o.dm; }
  if(o.sh)tile.shield=o.sh; if(o.shm)tile.shieldMax=o.shm; if(o.r)tile.reinforced=o.r; if(o.s!=null)tile.stage=o.s; if(o.sp)tile.species=o.sp; if(o.mt)tile.mature=true;
  return tile;
}
// Diff the live world against the seeded base -> only the tiles you actually changed. This is the tiny-save core.
function diffWorld(){
  const base = buildBaseWorld(worldSeed, worldHasCrystal()); const wd={};
  for(let y=0;y<MAPH;y++)for(let x=0;x<MAPW;x++){ const i=y*MAPW+x; const cs=tileSig(world[y][x]); if (JSON.stringify(cs)!==JSON.stringify(tileSig(base[y][x]))) wd[i]=cs; }
  return wd;
}
function applyWorldDiff(seed, wd){
  world = buildBaseWorld(seed>>>0, worldHasCrystal());
  wd = wd||{}; for(const k in wd){ const i=+k, x=i%MAPW, y=Math.floor(i/MAPW); if(world[y]&&world[y][x]) world[y][x]=tileFromSig(wd[k]); }
}
function getSaveIndex(){ try{ return JSON.parse(localStorage.getItem(SAVE_INDEX_KEY)||'[]'); }catch(e){ return []; } }
function setSaveIndex(idx){ try{ localStorage.setItem(SAVE_INDEX_KEY, JSON.stringify(idx)); }catch(e){} }
// Build the full save object (shared by localStorage save and the portable save-code).
function buildSaveData(name){
  const playerCopy = JSON.parse(JSON.stringify(Object.assign({}, player, {placingItem:null})));
  if (playerCopy.inv){ for(const k in playerCopy.inv){ if(!playerCopy.inv[k]) delete playerCopy.inv[k]; } }   // drop the many zero entries
  ['speedBoostTimer','efficiencyBoostTimer','slowTimer','sweetTimer','glowTimer','calmTimer','harvestTimer','strengthTimer','moving','moveT'].forEach(k=>{ if(!playerCopy[k]) delete playerCopy[k]; });
  // who you're playing with: their names, colors and kill counts travel with the save too
  const roster = [{ name: playerName||myName(), color: playerSkin, kills: stats.monstersKilled|0 }];
  for (const id in remotePlayers){ const rp=remotePlayers[id]; roster.push({ name: rp.name||'שחקן', color: rp.color||'#888888', kills: rp.kills|0 }); }
  const base = { v:2, name, ts:Date.now(), gameMode, dayNum, time, eternalNightDay, eternalNightActive, crystalPlaced, crystalActivated, crystalBonusDays, crystalDevicePos, challengeStartDay, roster, player:playerCopy, stats:JSON.parse(JSON.stringify(stats)), chests:JSON.parse(JSON.stringify(chests)) };
  // Tiny format: store the world SEED + only the tiles you changed. Falls back to the full world if anything looks off.
  try{ base.seed = worldSeed>>>0; base.wd = diffWorld(); }
  catch(e){ base.world = serializeWorld(); }
  return base;
}
// Restore a save object into the live game (shared by localStorage load and save-code import).
function applySaveData(data){
  netReset();
  gameMode = data.gameMode||'crystal';
  if (data.challengeStartDay) challengeStartDay = data.challengeStartDay;
  initEntities();
  if (data.world) deserializeWorld(data.world);                 // old full-world format
  else { worldSeed = (data.seed>>>0)||0; applyWorldDiff(worldSeed, data.wd); }   // tiny seed + changed-tiles format
  initPlayer(); const baseInv = player.inv; Object.assign(player, data.player); player.inv = Object.assign(baseInv, data.player.inv||{}); player.placingItem=null;   // merge saved inv over the full zeroed inventory so no key is missing
  dayNum=data.dayNum||1; time=data.time||0; eternalNightDay=data.eternalNightDay||5;
  eternalNightActive=!!data.eternalNightActive; crystalPlaced=!!data.crystalPlaced; crystalActivated=!!data.crystalActivated; crystalBonusDays=data.crystalBonusDays||0; crystalDevicePos=data.crystalDevicePos||null;
  stats = Object.assign({ animalsKilled:0,monstersKilled:0,blocksDestroyed:0,maxBreakDist:2,luckyOpened:0,dailyChoices:[] }, data.stats||{});
  chests = (data.chests||[]).map(c=>({x:c.x,y:c.y,items:c.items||{}}));
  cropTiles = []; for(let y=0;y<MAPH;y++)for(let x=0;x<MAPW;x++){ const c=world[y][x]; if(c.type===T.CROP){ if(!c.species) c.species='wheat'; c.cx=x; c.cy=y; if(c.mature){ c.stage=3; c.bred=true; } else { c.growAt = performance.now()+opCropGrowSeconds*1000; cropTiles.push(c); } } }
  bonusShownForDay=dayNum; luckyQueue=[]; gameOver=false; tickAcc=0; countTimer=0;
  camX=player.x; camY=player.y;
  document.getElementById('worldSelect').style.display='none';
  document.getElementById('msg').style.display='none';
  gameStarted=true; ensureAudio();
  updateHUD(); renderBag(); changeUIScale(1.2); updateResourceCounts();
}
function saveWorld(){
  if (!gameStarted){ showToast('אין עולם פעיל לשמור'); return; }
  const def = 'עולם יום '+dayNum;
  const name = (prompt('שם לעולם:', def) || def).slice(0,40);
  const id = 'sv_'+Date.now();
  const data = buildSaveData(name);
  let stored=false;
  try{ localStorage.setItem(id, JSON.stringify(data)); stored=true; }catch(e){}
  if (stored){ const idx = getSaveIndex(); idx.unshift({ id, name, ts:data.ts, dayNum, gameMode }); setSaveIndex(idx.slice(0,30)); showToast('💾 העולם נשמר: '+name); refreshSavesUI(); }
  else {
    // localStorage blocked (e.g. opened via a data: link) -> fall back to a copyable save-code
    showToast('השמירה הרגילה חסומה כאן — יצרתי לך קוד שמירה להעתקה 📋');
    showSaveCode(data);
  }
}
function loadWorld(id){
  let data; try{ data = JSON.parse(localStorage.getItem(id)); }catch(e){}
  if (!data){ showToast('טעינה נכשלה'); return; }
  applySaveData(data);
  showToast('📂 נטען: '+(data.name||''));
}
/* ============ Compact BINARY save format ============
   The old code stored the whole save as JSON, and most of it was junk the game recomputes anyway
   (moveFrom, moveDuration, attackCd, walkFrame...). Writing only the meaningful values as raw bytes
   shrinks a fresh-world save from ~817 JSON chars to a few dozen bytes, which is what actually makes
   the final code short. These lists are APPEND-ONLY so old codes keep working when new items are added. */
const SAVE_ITEMS = ['wood','stone','coal','iron','iron_ingot','berry','meat','torch','bones','wheat','seeds','bowl','dough','bread','cooked_meat','fruit_salad','crystal','reinforcement','raw_fish','cooked_fish','big_fish','pufferfish','eel','golden_fish','cave_crystal','honey_jar','clover','sunflower','herb','poppy','bluebell','goldenrod','glowcap','nightshade','crystalbloom','emberlily','moonflower','healing_potion','speed_potion','glow_lantern','harvest_charm','calm_incense','strength_brew','moon_elixir','item_wall','item_wall_thorn','item_bone_wall','item_campfire','item_furnace','item_crafting_table','item_upgraded_table','item_chest','item_crystal_device','item_lucky','item_beehive','item_garden_table','arrowWood','arrowIron','arrowBone'];
const SAVE_EQUIP = ['axe','pickaxe','sword','bow','iron_axe','iron_pickaxe','iron_sword','shovel','bucket','fishing_rod','bone_shield'];
const SAVE_FACING = ['down','up','left','right','down-left','down-right','up-left','up-right'];
const SAVE_WEAPON = ['sword','iron_sword','bow'];
const SAVE_MODES  = ['crystal','survival','challenge','test'];
const SAVE_SPECIES= ['wheat','clover','sunflower','herb','poppy','bluebell','goldenrod','glowcap','nightshade','crystalbloom','emberlily','moonflower'];

function BW(){ const a=[]; return {
  a, u8(v){ a.push(v&255); }, u16(v){ v=v|0; a.push((v>>8)&255, v&255); }, u32(v){ v=v>>>0; a.push((v>>>24)&255,(v>>>16)&255,(v>>>8)&255,v&255); },
  str(s){ const b=new TextEncoder().encode(String(s||'').slice(0,60)); a.push(Math.min(255,b.length)); for(let i=0;i<b.length&&i<255;i++) a.push(b[i]); },
  bytes(){ return new Uint8Array(a); } }; }
function BR(u8arr){ let i=0; const d=u8arr; return {
  u8(){ return d[i++]|0; }, u16(){ const v=(d[i]<<8)|d[i+1]; i+=2; return v; }, u32(){ const v=((d[i]<<24)>>>0)+(d[i+1]<<16)+(d[i+2]<<8)+d[i+3]; i+=4; return v>>>0; },
  str(){ const n=d[i++]|0; const s=new TextDecoder().decode(d.slice(i,i+n)); i+=n; return s; },
  left(){ return d.length-i; } }; }
function colorToRgb(c){ c=String(c||'#2f5f8a'); const m=/^#?([0-9a-f]{6})$/i.exec(c.trim()); if(m){ const n=parseInt(m[1],16); return [(n>>16)&255,(n>>8)&255,n&255]; }
  const m2=/rgb\((\d+)[ ,]+(\d+)[ ,]+(\d+)/i.exec(c); if(m2) return [+m2[1]&255,+m2[2]&255,+m2[3]&255]; return [47,95,138]; }
function rgbToColor(r,g,b){ return '#'+[r,g,b].map(v=>v.toString(16).padStart(2,'0')).join(''); }

function saveToBinary(d){
  const w=BW();
  w.u8(1);                                   // format version
  w.u32((d.seed||0)>>>0);
  w.u8(Math.max(0,SAVE_MODES.indexOf(d.gameMode||'crystal')));
  w.u16(Math.min(65535,d.dayNum||1));
  w.u16(Math.min(65535,Math.round((d.time||0)*10)));
  let flags = (d.eternalNightActive?1:0)|(d.crystalPlaced?2:0)|(d.crystalActivated?4:0)|(d.crystalDevicePos?8:0)|(d.world?16:0);
  w.u8(flags);
  w.u16(Math.min(65535,d.eternalNightDay||5)); w.u8(Math.min(255,d.crystalBonusDays||0)); w.u8(Math.min(255,d.challengeStartDay||2));
  if (d.crystalDevicePos){ w.u16(d.crystalDevicePos.tx|0); w.u16(d.crystalDevicePos.ty|0); }
  const pl=d.player||{};
  w.u16(Math.max(0,Math.round(pl.x||0))); w.u16(Math.max(0,Math.round(pl.y||0)));
  w.u16(Math.max(0,Math.round(pl.health||100))); w.u16(Math.max(0,Math.round(pl.maxHealth||100)));
  w.u16(Math.max(0,Math.round(pl.hunger||100))); w.u16(Math.max(0,Math.round(pl.maxHunger||100)));
  w.u8(Math.max(0,SAVE_FACING.indexOf(pl.facing||'down')));
  w.u8(Math.max(0,SAVE_WEAPON.indexOf(pl.activeWeapon||'sword')));
  w.u8(Math.min(255,pl.gatherBonus||0)); w.u8(Math.min(255,pl.breakReach||2)); w.u8(Math.min(255,Math.round((pl.speedBonus||0)*10)));
  let eq=0; SAVE_EQUIP.forEach((k,i)=>{ if(pl.equipment && pl.equipment[k]) eq |= (1<<i); }); w.u16(eq);
  const inv=pl.inv||{}; const ients=SAVE_ITEMS.map((k,i)=>[i,inv[k]|0]).filter(e=>e[1]>0);
  w.u8(Math.min(255,ients.length)); for(const [i,c] of ients.slice(0,255)){ w.u8(i); w.u16(Math.min(65535,c)); }
  const st=d.stats||{};
  w.u16(Math.min(65535,st.animalsKilled||0)); w.u16(Math.min(65535,st.monstersKilled||0)); w.u16(Math.min(65535,st.blocksDestroyed||0));
  w.u8(Math.min(255,Math.round(st.maxBreakDist||2))); w.u16(Math.min(65535,st.luckyOpened||0));
  const dc=(st.dailyChoices||[]).slice(0,60); w.u8(dc.length); for(const c of dc){ w.u16(c.day|0); w.str(c.label||''); }
  w.str(d.name||'');
  const ch=(d.chests||[]).slice(0,255); w.u8(ch.length);
  for(const c of ch){ w.u16(Math.round(c.x)); w.u16(Math.round(c.y)); const it=Object.keys(c.items||{}).map(k=>[SAVE_ITEMS.indexOf(k),c.items[k]|0]).filter(e=>e[0]>=0&&e[1]>0).slice(0,255);
    w.u8(it.length); for(const [i,n] of it){ w.u8(i); w.u16(Math.min(65535,n)); } }
  const roster=(d.roster||[]).slice(0,32); w.u8(roster.length);
  for(const r of roster){ w.str(r.name||''); const [rr,gg,bb]=colorToRgb(r.color); w.u8(rr); w.u8(gg); w.u8(bb); w.u16(Math.min(65535,r.kills||0)); }
  const wd=d.wd||{}; const keys=Object.keys(wd); w.u16(Math.min(65535,keys.length));
  for(const k of keys.slice(0,65535)){ const o=wd[k]; w.u16(+k & 65535); w.u8(o.t|0);
    let f=0; if(o.hp!=null)f|=1; if(o.m!=null)f|=2; if(o.d!=null)f|=4; if(o.dm!=null)f|=8; if(o.sh!=null)f|=16; if(o.s!=null)f|=32; if(o.sp!=null)f|=64; if(o.r||o.mt)f|=128;
    w.u8(f);
    if(f&1)w.u16(Math.max(0,Math.min(65535,o.hp))); if(f&2)w.u16(Math.max(0,Math.min(65535,o.m)));
    if(f&4)w.u16(Math.max(0,Math.min(65535,o.d))); if(f&8)w.u16(Math.max(0,Math.min(65535,o.dm)));
    if(f&16){ w.u16(Math.max(0,Math.min(65535,o.sh||0))); w.u16(Math.max(0,Math.min(65535,o.shm||0))); }
    if(f&32)w.u8(o.s|0);
    if(f&64)w.u8(Math.max(0,SAVE_SPECIES.indexOf(o.sp)));
    if(f&128)w.u8((o.r?1:0)|(o.mt?2:0));
  }
  return w.bytes();
}
function saveFromBinary(u8arr){
  const r=BR(u8arr); const ver=r.u8(); if(ver!==1) throw new Error('bad version');
  const d={ v:2 };
  d.seed=r.u32(); d.gameMode=SAVE_MODES[r.u8()]||'crystal';
  d.dayNum=r.u16(); d.time=r.u16()/10;
  const flags=r.u8();
  d.eternalNightActive=!!(flags&1); d.crystalPlaced=!!(flags&2); d.crystalActivated=!!(flags&4);
  d.eternalNightDay=r.u16(); d.crystalBonusDays=r.u8(); d.challengeStartDay=r.u8();
  if (flags&8){ const tx=r.u16(), ty=r.u16(); d.crystalDevicePos={ tx, ty, x:tx*TILE+TILE/2, y:ty*TILE+TILE/2 }; }
  const pl={};
  pl.x=r.u16(); pl.y=r.u16(); pl.health=r.u16(); pl.maxHealth=r.u16(); pl.hunger=r.u16(); pl.maxHunger=r.u16();
  pl.facing=SAVE_FACING[r.u8()]||'down'; pl.activeWeapon=SAVE_WEAPON[r.u8()]||'sword';
  pl.gatherBonus=r.u8(); pl.breakReach=r.u8(); pl.speedBonus=r.u8()/10;
  const eq=r.u16(); pl.equipment={}; SAVE_EQUIP.forEach((k,i)=>{ if(eq&(1<<i)) pl.equipment[k]=1; });
  pl.inv={}; const ni=r.u8(); for(let i=0;i<ni;i++){ const idx=r.u8(), c=r.u16(); const key=SAVE_ITEMS[idx]; if(key) pl.inv[key]=c; }
  pl.gridX=Math.floor(pl.x/TILE); pl.gridY=Math.floor(pl.y/TILE);
  d.player=pl;
  const st={}; st.animalsKilled=r.u16(); st.monstersKilled=r.u16(); st.blocksDestroyed=r.u16(); st.maxBreakDist=r.u8(); st.luckyOpened=r.u16();
  const ndc=r.u8(); st.dailyChoices=[]; for(let i=0;i<ndc;i++){ const day=r.u16(); const label=r.str(); st.dailyChoices.push({day,label}); }
  d.stats=st;
  d.name=r.str();
  const nch=r.u8(); d.chests=[];
  for(let i=0;i<nch;i++){ const x=r.u16(), y=r.u16(); const n=r.u8(); const items={}; for(let j=0;j<n;j++){ const idx=r.u8(), c=r.u16(); const key=SAVE_ITEMS[idx]; if(key) items[key]=c; } d.chests.push({x,y,items}); }
  const nr=r.u8(); d.roster=[]; for(let i=0;i<nr;i++){ const name=r.str(); const rr=r.u8(), gg=r.u8(), bb=r.u8(); const kills=r.u16(); d.roster.push({name,color:rgbToColor(rr,gg,bb),kills}); }
  const nwd=r.u16(); d.wd={};
  for(let i=0;i<nwd;i++){ const idx=r.u16(); const o={ t:r.u8() }; const f=r.u8();
    if(f&1)o.hp=r.u16(); if(f&2)o.m=r.u16(); if(f&4)o.d=r.u16(); if(f&8)o.dm=r.u16();
    if(f&16){ o.sh=r.u16(); o.shm=r.u16(); }
    if(f&32)o.s=r.u8();
    if(f&64)o.sp=SAVE_SPECIES[r.u8()]||'wheat';
    if(f&128){ const b=r.u8(); if(b&1)o.r=1; if(b&2)o.mt=1; }
    d.wd[idx]=o;
  }
  return d;
}

/* ---- Portable save code: works even when localStorage is blocked (Shortcut / data: link) ---- */
// Compress the save with the browser's built-in gzip so the code is MUCH shorter (usually 4-6x smaller).
// Prefix marks the format: G1 = gzip+base64, R1 = raw base64 fallback (old phones without CompressionStream).
async function gzipB64(str){
  if (typeof CompressionStream === 'undefined') return 'R1:'+btoa(unescape(encodeURIComponent(str)));
  try{
    const bytes = new TextEncoder().encode(str);
    const ab = await new Response(new Blob([bytes]).stream().pipeThrough(new CompressionStream('gzip'))).arrayBuffer();
    const u8 = new Uint8Array(ab); let bin=''; for(let i=0;i<u8.length;i++) bin += String.fromCharCode(u8[i]);
    return 'G1:'+btoa(bin);
  }catch(e){ return 'R1:'+btoa(unescape(encodeURIComponent(str))); }
}
async function gunzipB64(payload){
  const bin = atob(payload); const u8 = new Uint8Array(bin.length); for(let i=0;i<bin.length;i++) u8[i]=bin.charCodeAt(i);
  const ab = await new Response(new Blob([u8]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();
  return new TextDecoder().decode(ab);
}
async function gunzipBytesToStr(u8){
  const ab = await new Response(new Blob([u8]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();
  return new TextDecoder().decode(ab);
}
// A 1024-emoji alphabet. Because it's a big alphabet, each emoji carries 10 bits, so the code needs far
// FEWER symbols than base64 (~40% fewer) — easier to move around. Encode/decode use the same numeric
// alphabet, so it round-trips perfectly even if a given emoji shows as a blank box on some device.
const EMOJI_ALPHA=[]; for(let c=0x1F300;c<=0x1F5FF;c++) EMOJI_ALPHA.push(c); for(let c=0x1F900;c<=0x1F9FF;c++) EMOJI_ALPHA.push(c);
const EMOJI_INDEX={}; for(let i=0;i<EMOJI_ALPHA.length;i++) EMOJI_INDEX[EMOJI_ALPHA[i]]=i;
function encodeEmoji(u8){
  const B=u8.length; const r=B%5; let out=String.fromCodePoint(EMOJI_ALPHA[r]);   // header emoji = remainder (padding info)
  for(let i=0;i<B;i+=5){ const b0=u8[i]||0,b1=u8[i+1]||0,b2=u8[i+2]||0,b3=u8[i+3]||0,b4=u8[i+4]||0;
    const val=b0*4294967296+b1*16777216+b2*65536+b3*256+b4;   // 40-bit group -> four 10-bit emojis
    out+=String.fromCodePoint(EMOJI_ALPHA[Math.floor(val/1073741824)%1024])+String.fromCodePoint(EMOJI_ALPHA[Math.floor(val/1048576)%1024])+String.fromCodePoint(EMOJI_ALPHA[Math.floor(val/1024)%1024])+String.fromCodePoint(EMOJI_ALPHA[val%1024]);
  }
  return out;
}
function decodeEmoji(s){
  const idx=[]; for(const ch of s){ const k=EMOJI_INDEX[ch.codePointAt(0)]; if(k===undefined) throw new Error('bad emoji'); idx.push(k); }
  const r=idx[0]; const body=idx.slice(1); const bytes=[];
  for(let i=0;i<body.length;i+=4){ const e0=body[i]||0,e1=body[i+1]||0,e2=body[i+2]||0,e3=body[i+3]||0;
    const val=e0*1073741824+e1*1048576+e2*1024+e3;
    bytes.push(Math.floor(val/4294967296)%256, Math.floor(val/16777216)%256, Math.floor(val/65536)%256, Math.floor(val/256)%256, val%256);
  }
  if(r>0) bytes.length = bytes.length-(5-r);   // drop the padding bytes of the last group
  return new Uint8Array(bytes);
}
/* ---- Code output ----
   Payload = compact binary (optionally gzipped when that's actually smaller), then rendered either as
   letters (S:) or as emojis (M:). The emoji set is a curated 256 of the oldest, most universally supported
   emojis (Unicode 6.0/6.1, single code point, no skin tones / ZWJ / variation selectors) so they don't show
   as empty boxes. Every emoji code is decoded back and byte-compared before it's shown; if it doesn't match
   exactly, we silently fall back to letters. That's why a broken code can't be produced any more. */
const EMOJI256=(function(){ const a=[];
  for(let c=0x1F600;c<=0x1F64F;c++) a.push(c);   // smileys  (80)
  for(let c=0x1F400;c<=0x1F43E;c++) a.push(c);   // animals  (63)
  for(let c=0x1F330;c<=0x1F37C;c++) a.push(c);   // plants/food (77)
  for(let c=0x1F680;c<=0x1F6A4;c++) a.push(c);   // transport (37)
  return a.slice(0,256); })();
const EMOJI256_IDX={}; EMOJI256.forEach((cp,i)=>EMOJI256_IDX[cp]=i);
function bytesToEmoji(u8){ let s=''; for(let i=0;i<u8.length;i++) s+=String.fromCodePoint(EMOJI256[u8[i]]); return s; }
function emojiToBytes(str){ const out=[]; for(const ch of str){ const i=EMOJI256_IDX[ch.codePointAt(0)]; if(i===undefined) throw new Error('bad emoji'); out.push(i); } return new Uint8Array(out); }
function bytesToB64(u8){ let bin=''; for(let i=0;i<u8.length;i++) bin+=String.fromCharCode(u8[i]); return btoa(bin); }
function b64ToBytes(s){ const bin=atob(s); const u=new Uint8Array(bin.length); for(let i=0;i<bin.length;i++) u[i]=bin.charCodeAt(i); return u; }
async function gzipBytes(u8){ const ab=await new Response(new Blob([u8]).stream().pipeThrough(new CompressionStream('gzip'))).arrayBuffer(); return new Uint8Array(ab); }
async function gunzipBytes(u8){ const ab=await new Response(new Blob([u8]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer(); return new Uint8Array(ab); }
// Build the payload: [flag byte] + body. flag 0 = raw binary, 1 = gzipped binary.
async function buildPayload(data){
  const raw = saveToBinary(data);
  let body = raw, flag = 0;
  if (raw.length > 120 && typeof CompressionStream !== 'undefined'){
    try{ const gz = await gzipBytes(raw); if (gz.length < raw.length){ body = gz; flag = 1; } }catch(e){}
  }
  const out = new Uint8Array(body.length+1); out[0]=flag; out.set(body,1); return out;
}
async function payloadToData(payload){
  const flag = payload[0]; let body = payload.slice(1);
  if (flag===1) body = await gunzipBytes(body);
  return saveFromBinary(body);
}
let saveCodeStyle = 'emoji';   // 'emoji' or 'letters'
async function encodeSave(data, style){
  style = style || saveCodeStyle;
  try{
    const payload = await buildPayload(data);
    if (style === 'emoji'){
      const code = 'M:'+bytesToEmoji(payload);
      // self-check: decode it right back and require an exact byte match before handing it to the player
      try{ const back = emojiToBytes(code.slice(2)); let same = back.length===payload.length; if(same) for(let i=0;i<back.length;i++){ if(back[i]!==payload[i]){ same=false; break; } }
        if (same) return code; }catch(e){}
    }
    return 'S:'+bytesToB64(payload);
  }catch(e){ return await gzipB64(JSON.stringify(data)); }   // last-resort: old JSON format
}
async function decodeSave(str){
  str = (str||'').replace(/\s+/g,'').trim();   // copy/paste can sprinkle spaces or newlines — strip them
  if (str.startsWith('M:')) return await payloadToData(emojiToBytes(str.slice(2)));   // compact binary, emoji
  if (str.startsWith('S:')) return await payloadToData(b64ToBytes(str.slice(2)));     // compact binary, letters
  if (str.startsWith('E1:')) return JSON.parse(await gunzipBytesToStr(decodeEmoji(str.slice(3))));
  if (str.startsWith('G1:')) return JSON.parse(await gunzipB64(str.slice(3)));
  if (str.startsWith('R1:')) return JSON.parse(decodeURIComponent(escape(atob(str.slice(3)))));
  return JSON.parse(decodeURIComponent(escape(atob(str))));   // legacy (uncompressed) codes still load
}
async function showSaveCode(data){
  const box = document.getElementById('saveCodeBox'); const ta = document.getElementById('saveCodeArea');
  if (!box || !ta) return;
  ta.value = '⏳ מכין קוד...'; box.style.display='block';
  ta.value = await encodeSave(data || buildSaveData('עולם יום '+dayNum));
  ta.focus(); ta.select();
}
async function makeSaveCode(){
  if (!gameStarted){ showToast('אין עולם פעיל'); return; }
  await showSaveCode(buildSaveData('עולם יום '+dayNum));
  showToast('📋 סמן הכל והעתק — הדבק ל-Google Keep או לכל מקום');
}
function copySaveCode(){ const ta=document.getElementById('saveCodeArea'); if(!ta) return; const ok=copyTextFrom(ta); showToast(ok ? 'הקוד הועתק 📋' : 'הקוד מסומן — לחץ "העתק" מהתפריט של הטלפון 📋'); }
function copyStatsCode(){ const el=document.getElementById('statsCode'); if(!el) return; const ok=copyTextFrom(el); showToast(ok ? ('הקוד הועתק 📋: '+el.value) : 'הקוד מסומן — לחץ "העתק" מהתפריט של הטלפון 📋'); }
function setSaveCodeStyle(s){ saveCodeStyle = s; showToast(s==='emoji' ? '😀 קוד באימוג׳ים (קצר יותר)' : '🔤 קוד באותיות (הכי בטוח)'); }
async function loadFromCode(){
  const ta=document.getElementById('loadCodeArea'); if(!ta) return;
  const str=(ta.value||'').trim(); if(!str){ showToast('הדבק קוד שמירה קודם'); return; }
  let data; try{ data=await decodeSave(str); }catch(e){ showToast('הקוד לא תקין ❌'); return; }
  if(!data || !data.world){ showToast('הקוד לא תקין ❌'); return; }
  applySaveData(data);
  showToast('📂 נטען מקוד שמירה!');
}
function deleteSave(id){ localStorage.removeItem(id); setSaveIndex(getSaveIndex().filter(s=>s.id!==id)); refreshSavesUI(); }
function refreshSavesUI(){
  const idx = getSaveIndex(); const sec=document.getElementById('savesSection'); const list=document.getElementById('savesList');
  if (!sec) return;
  sec.style.display='block';   // always visible so the player knows where saved worlds live
  list.innerHTML = idx.length
    ? idx.map(s=>`<div class="saveRow"><span class="sName">${s.name} (יום ${s.dayNum})</span><button class="loadB" onclick="loadWorld('${s.id}')">טען</button><button class="delB" onclick="deleteSave('${s.id}')">🗑️</button></div>`).join('')
    : '<div class="saveRow"><span class="sName" style="color:#8a8266;">עדיין אין עולמות שמורים — שמור עולם דרך ⚙️ הגדרות</span></div>';
}
function submitWorldCode(){
  const val = (document.getElementById('wsCodeInput').value||'').trim();
  if (val !== WORLD_TEST_CODE){ showToast('קוד שגוי'); return; }
  // secret code also unlocks editing how many days pass before the eternal night
  const d = prompt('כמה ימים עד הלילה הנצחי? (ברירת מחדל 5)', String(userEternalDay));
  const parsed = parseInt(d);
  if (!isNaN(parsed) && parsed >= 1) userEternalDay = parsed;
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
// Health/food gains are capped at 30 (never scale higher, never doubled) — per request.
function bonusHF(){ if (Math.random()<0.05) return 6+Math.floor(Math.random()*2); const opts=[10,15,20,25,30]; return opts[Math.floor(Math.random()*opts.length)]; }
// Bonuses only ever give: max health/food (≤30), blocks/reinforcements, torches or resources. No speed / reach / mining-power.
const BONUS_POOL = [
  () => mkBonus('❤️','חיים מקסימליים', bonusHF(), v=>{ player.maxHealth+=v; player.health=Math.min(player.maxHealth, player.health+v); }),
  () => mkBonus('🍖','אוכל מקסימלי', bonusHF(), v=>{ player.maxHunger+=v; player.hunger=Math.min(player.maxHunger, player.hunger+v); }),
  () => mkBonus('🧱','קירות לתיק', scaledRound(10), v=>{ player.inv.item_wall=(player.inv.item_wall||0)+v; }),
  () => mkBonus('🌵','קירות קוצים', scaledRound(10), v=>{ player.inv.item_wall_thorn=(player.inv.item_wall_thorn||0)+v; }),
  () => mkBonus('🦴','קירות עצמות', scaledRound(10), v=>{ player.inv.item_bone_wall=(player.inv.item_bone_wall||0)+v; }),
  () => mkBonus('⛓️','חיזוקי ברזל', Math.max(2, Math.round(scaledRound(10)/3)), v=>{ player.inv.reinforcement=(player.inv.reinforcement||0)+v; }),
  () => mkBonus('🔥','לפידים', scaledRound(10), v=>{ player.inv.torch=(player.inv.torch||0)+v; }),
  () => mkBonus('📦','עץ + אבן', scaledRound(30), v=>{ player.inv.wood+=v; player.inv.stone+=v; }),
  () => mkBonus('🍞','בשר לאכילה', scaledRound(10), v=>{ player.inv.meat=(player.inv.meat||0)+v; }),
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
  if (net.active) return;   // no pausing modal during co-op (would freeze one player)
  const eligible = (dayNum > 5) || (gameMode==='challenge' && dayNum>=2) || (eternalNightActive && dayNum>=2);
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
  if (net.active){
    rows.push(['👥 שחקנים בעולם', netPlayerCount]);
    rows.push(['🕹️ התפקיד שלך', net.isHost ? 'מארח' : 'אורח']);
    for (const id in remotePlayers){ const rp=remotePlayers[id];
      rows.push(['<span style="color:'+(rp.color||'#888')+'">●</span> '+(rp.name||'שחקן'), '👾 '+(rp.kills|0)]); }
  }
  let html = rows.map(r=>`<div class="statRow"><span>${r[0]}</span><b>${r[1]}</b></div>`).join('');
  // The room code stays visible mid-game (tap to select) so a friend can still join after you've started.
  if (net.active){
    const code = net.isHost ? (net.myCode||'—') : (net.hostCode||'—');
    html += `<div class="statRow" style="flex-direction:column; align-items:stretch; gap:5px; padding-top:8px;">
      <span>🌐 קוד להצטרפות (גם באמצע משחק)</span>
      <input id="statsCode" readonly value="${code}" onclick="this.select()" dir="ltr" style="width:100%; box-sizing:border-box; text-align:center; font-size:22px; letter-spacing:4px; font-family:inherit; background:#0d1018; color:#4a9aff; border:1px solid #4a4230; border-radius:6px; padding:6px;">
      <button onclick="copyStatsCode()" style="padding:6px; background:#2f5a8a; color:#fff; border:none; border-radius:5px; font-family:inherit; font-size:11px; cursor:pointer;">📋 העתק קוד</button>
    </div>`;
  }
  document.getElementById('statsBody').innerHTML = html;
  const ch = stats.dailyChoices;
  document.getElementById('statsChoices').innerHTML = ch.length ? ch.map(c=>`<div class="statRow"><span>יום ${c.day}</span><b>${c.label}</b></div>`).join('') : '<div class="statRow"><span>עדיין לא בחרת שדרוגים</span></div>';
}

/* ============ Texture-6 visual grain ("סאונד") + damage cracks ============ */
// Per-surface toggle for the grainy noise texture unlocked at graphics level 6.
let blockNoise = { wall:true, temple:true, floor_grass:true, floor_sand:true, floor_snow:true, floor_plains:true, bone_wall:true };
function noiseKeyForTile(type){ if(type===T.WALL||type===T.CAVE_WALL) return 'wall'; if(type===T.BONE_WALL) return 'bone_wall'; if(type===T.ALTAR_FLOOR) return 'temple'; return null; }
function blockNoiseOn(type){ if (gfxLevel < 6) return false; const k = noiseKeyForTile(type); return k ? blockNoise[k] : false; }
function floorNoiseOn(b, type){ if (gfxLevel < 6) return false; if (type===T.ALTAR_FLOOR) return blockNoise.temple; if (type===T.GRASS) return blockNoise.floor_grass; if (type===T.SAND) return blockNoise.floor_sand; if (type===T.SNOW) return blockNoise.floor_snow; return false; }
// deterministic hash so grain is stable per pixel-cell (doesn't shimmer each frame)
function hash2(x,y){ let h = (x*73856093) ^ (y*19349663); h = (h ^ (h>>13)) * 1274126177; return ((h>>>0) % 1000)/1000; }
// Grain used to be recomputed pixel-by-pixel for every tile every frame (~64 ops/tile) — brutal in caves.
// Now it's baked once into a repeating 128px pattern per color and stamped with a single fillRect per tile.
const _grainPat = {};
function getGrainPattern(color){
  if (_grainPat[color]!==undefined) return _grainPat[color];
  const S=128; const c=document.createElement('canvas'); c.width=S; c.height=S; const g=c.getContext('2d');
  g.fillStyle=color; g.globalAlpha=0.28;
  for (let y=0;y<S;y+=4) for (let x=0;x<S;x+=4){ if (hash2(x,y) < 0.32) g.fillRect(x,y,2,2); }
  let pat=null; try{ pat = ctx.createPattern(c,'repeat'); }catch(e){}
  _grainPat[color]=pat; return pat;
}
function drawGrain(x, y, w, h, color){
  const pat=getGrainPattern(color); if(!pat) return;   // pattern is anchored in world space, so grain stays put as you move
  ctx.fillStyle=pat; ctx.fillRect(x, y, w, h);
}
// Fully-grown plants, all hand-drawn on the canvas (no emojis — a big garden stays smooth).
// cx = tile centre X, sy = tile top Y. Base of the plant sits near sy+26.
function drawMaturePlant(species, cx, sy){
  const baseY = sy+26;
  const stem = (col, w, fromY)=>{ ctx.fillStyle=col||'#3f7a2a'; ctx.fillRect(cx-(w||1), fromY, (w||1)*2, baseY-fromY); };
  switch(species){
    case 'wheat':
      ctx.fillStyle='#d9a441'; ctx.fillRect(cx-4, sy+13, 1.6, 13); ctx.fillRect(cx-0.8, sy+9, 1.6, 17); ctx.fillRect(cx+3, sy+14, 1.6, 12);
      ctx.fillStyle='#f4d06f';
      for(const g of [[-3.2,13],[0.1,9],[3.8,14]]){ for(let i=0;i<3;i++){ ctx.beginPath(); ctx.ellipse(cx+g[0], sy+g[1]+i*3.2, 2.1, 1.3, 0,0,6.3); ctx.fill(); } }
      break;
    case 'clover':
      stem('#2f7a3f', 1, sy+15);
      ctx.fillStyle='#3aa35a'; for(const d of [[-4,-2],[4,-2],[0,-6],[0,2]]){ ctx.beginPath(); ctx.arc(cx+d[0], sy+11+d[1], 3.4, 0, 6.3); ctx.fill(); }
      ctx.fillStyle='#8fe0a0'; ctx.beginPath(); ctx.arc(cx-1, sy+9, 1, 0, 6.3); ctx.fill();
      break;
    case 'sunflower':
      stem('#2f7a3f', 1.2, sy+13);
      ctx.fillStyle='#3aa35a'; ctx.beginPath(); ctx.ellipse(cx-4, sy+18, 3, 1.6, -0.6,0,6.3); ctx.fill();
      ctx.fillStyle='#f2c94c'; for(let i=0;i<10;i++){ const a=i/10*6.283; ctx.beginPath(); ctx.ellipse(cx+Math.cos(a)*5, sy+9+Math.sin(a)*5, 2.4, 1.3, a,0,6.3); ctx.fill(); }
      ctx.fillStyle='#6b4a1e'; ctx.beginPath(); ctx.arc(cx, sy+9, 3.1, 0, 6.3); ctx.fill();
      break;
    case 'herb':
      stem('#2f7a3f', 1, sy+8);
      ctx.fillStyle='#4a9a3a'; for(const dy of [4,9,14]){ ctx.beginPath(); ctx.ellipse(cx-3.5, sy+dy, 3.2, 1.5, -0.5,0,6.3); ctx.fill(); ctx.beginPath(); ctx.ellipse(cx+3.5, sy+dy+1.5, 3.2, 1.5, 0.5,0,6.3); ctx.fill(); }
      break;
    case 'poppy':
      stem('#2f7a3f', 1, sy+11);
      ctx.fillStyle='#e0473a'; for(let i=0;i<5;i++){ const a=i/5*6.283-1.57; ctx.beginPath(); ctx.ellipse(cx+Math.cos(a)*3.8, sy+9+Math.sin(a)*3.8, 3, 2.4, a,0,6.3); ctx.fill(); }
      ctx.fillStyle='#2a1520'; ctx.beginPath(); ctx.arc(cx, sy+9, 2.1, 0, 6.3); ctx.fill();
      break;
    case 'bluebell':
      ctx.strokeStyle='#2f7a3f'; ctx.lineWidth=1.4; ctx.beginPath(); ctx.moveTo(cx, baseY); ctx.quadraticCurveTo(cx-5, sy+12, cx-3, sy+7); ctx.stroke();
      ctx.fillStyle='#5b7ce0'; for(const b of [[-3,7],[1,10],[4,14]]){ ctx.beginPath(); ctx.moveTo(cx+b[0], sy+b[1]); ctx.lineTo(cx+b[0]-2.4, sy+b[1]+4.5); ctx.lineTo(cx+b[0]+2.4, sy+b[1]+4.5); ctx.closePath(); ctx.fill(); ctx.beginPath(); ctx.arc(cx+b[0], sy+b[1]+4.5, 2.4, 0, 3.14); ctx.fill(); }
      break;
    case 'goldenrod':
      stem('#2f7a3f', 1.2, sy+8);
      ctx.fillStyle='#f0b429'; for(let r=0;r<7;r++){ const w=1+r*0.5; for(let k=0;k<=r;k++){ ctx.beginPath(); ctx.arc(cx-w+(r?(k/r)*w*2:0), sy+6+r*2.2, 1.4, 0, 6.3); ctx.fill(); } }
      break;
    case 'glowcap':
      ctx.fillStyle='#e8e2cf'; ctx.fillRect(cx-2, sy+13, 4, 12);
      ctx.fillStyle='#e05a6a'; ctx.beginPath(); ctx.arc(cx, sy+13, 8, Math.PI, 2*Math.PI); ctx.fill(); ctx.fillRect(cx-8, sy+12, 16, 2);
      ctx.fillStyle='#fff'; ctx.beginPath(); ctx.arc(cx-3, sy+9, 1.5, 0, 6.3); ctx.arc(cx+3, sy+10, 1.2, 0, 6.3); ctx.arc(cx, sy+7, 1, 0, 6.3); ctx.fill();
      break;
    case 'nightshade':
      stem('#356b2f', 1, sy+9);
      ctx.fillStyle='#7a4bd0'; for(const b of [[-3,8],[3,10],[0,14],[-2,15]]){ ctx.beginPath(); ctx.arc(cx+b[0], sy+b[1], 2.3, 0, 6.3); ctx.fill(); }
      ctx.fillStyle='#c9a6ff'; ctx.beginPath(); ctx.arc(cx+1, sy+6, 1.6, 0, 6.3); ctx.fill();
      break;
    case 'crystalbloom':
      stem('#2f7a3f', 1, sy+13);
      if(gfxLevel>=4){ ctx.save(); ctx.globalAlpha=0.35; ctx.fillStyle='#9beef5'; ctx.beginPath(); ctx.arc(cx, sy+9, 8, 0, 6.3); ctx.fill(); ctx.restore(); }
      ctx.fillStyle='#57d6e0'; for(let i=0;i<4;i++){ const a=i/4*6.283, px=cx+Math.cos(a)*4.5, py=sy+9+Math.sin(a)*4.5; ctx.beginPath(); ctx.moveTo(cx,sy+9); ctx.lineTo(px-1.6*Math.sin(a), py+1.6*Math.cos(a)); ctx.lineTo(px+Math.cos(a)*2.5, py+Math.sin(a)*2.5); ctx.lineTo(px+1.6*Math.sin(a), py-1.6*Math.cos(a)); ctx.closePath(); ctx.fill(); }
      ctx.fillStyle='#eafcff'; ctx.beginPath(); ctx.arc(cx, sy+9, 1.8, 0, 6.3); ctx.fill();
      break;
    case 'emberlily':
      stem('#3a6b2f', 1, sy+13);
      if(gfxLevel>=4){ ctx.save(); ctx.globalAlpha=0.3; ctx.fillStyle='#ff9a3a'; ctx.beginPath(); ctx.arc(cx, sy+9, 7, 0, 6.3); ctx.fill(); ctx.restore(); }
      for(let i=0;i<5;i++){ const a=i/5*6.283-1.57; ctx.fillStyle=i%2?'#ff7a2a':'#ffb02a'; ctx.beginPath(); ctx.moveTo(cx, sy+9); ctx.lineTo(cx+Math.cos(a-0.25)*6, sy+9+Math.sin(a-0.25)*6); ctx.lineTo(cx+Math.cos(a)*7, sy+9+Math.sin(a)*7); ctx.lineTo(cx+Math.cos(a+0.25)*6, sy+9+Math.sin(a+0.25)*6); ctx.closePath(); ctx.fill(); }
      ctx.fillStyle='#fff2c0'; ctx.beginPath(); ctx.arc(cx, sy+9, 1.6, 0, 6.3); ctx.fill();
      break;
    case 'moonflower':
      stem('#3a6b4a', 1, sy+13);
      if(gfxLevel>=4){ ctx.save(); ctx.globalAlpha=0.4; ctx.fillStyle='#dfe6ff'; ctx.beginPath(); ctx.arc(cx, sy+9, 8, 0, 6.3); ctx.fill(); ctx.restore(); }
      ctx.fillStyle='#eaf0ff'; for(let i=0;i<6;i++){ const a=i/6*6.283; ctx.beginPath(); ctx.ellipse(cx+Math.cos(a)*4, sy+9+Math.sin(a)*4, 2.6, 1.7, a,0,6.3); ctx.fill(); }
      ctx.fillStyle='#bcd0ff'; ctx.beginPath(); ctx.arc(cx, sy+9, 2, 0, 6.3); ctx.fill();
      break;
    default: {
      const col=(PLANT_SPECIES[species]||{}).color||'#73c745';
      stem('#3f7a2a', 1, sy+11); ctx.fillStyle=col; ctx.beginPath(); ctx.arc(cx, sy+9, 3.5, 0, 6.3); ctx.fill();
    }
  }
}
// durability fraction for a built item: prefer the monster hit-count (def), else the player-mining hp
function builtFrac(o, type){ if(!o) return 1; if(o.defMax) return Math.max(0,o.def||0)/o.defMax; return Math.max(0,o.hp)/((o.maxHp)||tileHP(type)); }
// grey square ring shown around a reinforced item; brighter when the shield still has charge
function drawReinforceRing(sx, sy, o){
  if (!o || !o.reinforced) return;
  const sf = o.shieldMax ? Math.max(0,(o.shield||0))/o.shieldMax : 0;
  ctx.save();
  ctx.strokeStyle = sf>0 ? '#c0c0c0' : '#5a5a5a';
  ctx.lineWidth = 2.5; ctx.strokeRect(sx+1.5, sy+1.5, TILE-3, TILE-3);
  ctx.strokeStyle = 'rgba(210,210,210,'+(0.25+0.55*sf)+')'; ctx.lineWidth = 1;
  ctx.strokeRect(sx+4, sy+4, TILE-8, TILE-8);
  ctx.restore();
}
function drawCracks(cx, cy, frac){
  if (frac >= 0.98) return;
  const cracks = Math.min(10, Math.round((1-frac)*10));
  const crackLines = [[[-8,-6],[-2,2]],[[8,-4],[2,3]],[[-4,8],[3,-2]],[[6,7],[-1,-1]],[[-9,2],[-3,-1]],[[9,3],[3,1]],[[0,-10],[0,-2]],[[-6,-9],[-2,-4]],[[5,-8],[1,-3]],[[-2,9],[1,4]]];
  ctx.save(); ctx.strokeStyle = frac<=0.10 ? 'rgba(60,10,5,0.95)' : 'rgba(20,20,20,0.7)'; ctx.lineWidth = 1.3;
  for (let i=0; i<cracks && i<crackLines.length; i++){ const l = crackLines[i]; ctx.beginPath(); ctx.moveTo(cx+l[0][0], cy+l[0][1]); ctx.lineTo(cx+l[1][0], cy+l[1][1]); ctx.stroke(); }
  ctx.restore();
}
// Only tall "prop" tiles get the (expensive) drop shadow. Bulk full-tile blocks — cave walls, walls,
// ores, floors — skip it, which is the main lag fix in caves/bases where almost every tile is a block.
const SHADOW_TYPES = new Set([T.TREE, T.PINE, T.TRUNK, T.SAPLING, T.BUSH, T.CACTUS, T.CROP, T.SKULL, T.CAMPFIRE, T.CRAFTING_TABLE, T.UPGRADED_TABLE, T.PLACED_TORCH, T.BEEHIVE, T.GARDEN_TABLE, T.CRYSTAL_DEVICE, T.LUCKY]);
function drawResourceShape(t, sx, sy, tileObj){
  const cx = sx+TILE/2, cy = sy+TILE/2; ctx.save();
  if (gfxLevel >= 5 && SHADOW_TYPES.has(t)) { ctx.shadowColor = 'rgba(0,0,0,0.4)'; ctx.shadowBlur = 5; ctx.shadowOffsetY = 4; }
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
    const mature = tileObj && tileObj.mature;
    const sp = (tileObj && PLANT_SPECIES[tileObj.species]) || PLANT_SPECIES.wheat;
    ctx.fillStyle='rgba(0,0,0,0.12)'; ctx.beginPath(); ctx.ellipse(cx+1, cy+10, 6, 2.5, 0,0,6.3); ctx.fill();
    if (mature || stage>=3){ drawMaturePlant((tileObj&&tileObj.species)||'wheat', cx, sy); }
    else if (stage===0){ ctx.fillStyle='#73c745'; ctx.beginPath(); ctx.arc(cx, cy+4, 3, 0, 6.3); ctx.fill(); }
    else if (stage===1){ ctx.fillStyle='#4a8a2a'; ctx.fillRect(cx-1, cy, 2, 8); ctx.fillStyle='#73c745'; ctx.beginPath(); ctx.arc(cx, cy-1, 3.5, 0, 6.3); ctx.fill(); }
    else { ctx.fillStyle='#4a8a2a'; ctx.fillRect(cx-1, sy+10, 2, 14); ctx.fillStyle=sp.color; ctx.beginPath(); ctx.arc(cx, sy+9, 3.6, 0, 6.3); ctx.fill(); }
  } else if (t===T.GARDEN_TABLE) {
    // 🌿 Herbalist Table: wooden bench with potted plants and little bottles on top
    ctx.fillStyle='rgba(0,0,0,0.18)'; ctx.beginPath(); ctx.ellipse(cx+1, cy+13, 12, 4, 0,0,6.3); ctx.fill();
    ctx.fillStyle='#6b4a2a'; ctx.fillRect(sx+4, sy+16, 4, 12); ctx.fillRect(sx+TILE-8, sy+16, 4, 12);
    ctx.fillStyle='#3f7a2a'; ctx.fillRect(sx+2, sy+8, TILE-4, 9);
    ctx.fillStyle='#2f5d20'; ctx.fillRect(sx+2, sy+8, TILE-4, 2);
    // little clay pots
    ctx.fillStyle='#b5835a'; ctx.fillRect(sx+5, sy+4, 5, 5); ctx.fillRect(sx+TILE-10, sy+5, 5, 4);
    ctx.fillStyle='#73c745'; ctx.beginPath(); ctx.arc(sx+7.5, sy+3.5, 2.4, 0, 6.3); ctx.fill();
    ctx.fillStyle='#6ad0ff'; ctx.beginPath(); ctx.arc(sx+TILE-7.5, sy+4, 2, 0, 6.3); ctx.fill();
    // a bottle
    ctx.fillStyle='rgba(255,120,200,0.85)'; ctx.fillRect(cx-1, sy+5, 3, 5);
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
  } else if (t===T.CAVE_WALL){
    // solid grey cave rock filling the whole tile — the bulk of the maze; gives nothing when mined
    ctx.fillStyle='#41414c'; ctx.fillRect(sx,sy,TILE,TILE);
    ctx.fillStyle='#4d4d59'; ctx.fillRect(sx,sy,TILE,4); ctx.fillRect(sx,sy,4,TILE);
    ctx.fillStyle='#33333d'; ctx.fillRect(sx,sy+TILE-5,TILE,5); ctx.fillRect(sx+TILE-5,sy,5,TILE);
    ctx.fillStyle='rgba(0,0,0,0.22)'; ctx.fillRect(sx+7,sy+9,5,3); ctx.fillRect(sx+18,sy+16,6,3); ctx.fillRect(sx+12,sy+22,4,2);
    ctx.fillStyle='rgba(255,255,255,0.05)'; ctx.fillRect(sx+20,sy+6,4,2); ctx.fillRect(sx+6,sy+18,3,2);
    if (gfxLevel>=6 && blockNoiseOn(T.CAVE_WALL)) drawGrain(sx, sy, TILE, TILE, '#2c2c34');
  } else if (t===T.ROCK || t===T.COAL || t===T.IRONROCK){
    if (gfxLevel >= 5) {
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
    if (gfxLevel >= 5) { ctx.fillStyle='#1e5c2b'; ctx.fillRect(cx-3, cy-13, 6, 22); ctx.fillRect(cx-9, cy-3, 6, 3); ctx.fillRect(cx-9, cy-8, 3, 6); ctx.fillRect(cx+3, cy-7, 6, 3); ctx.fillRect(cx+6, cy-12, 3, 6); ctx.fillStyle='#fff'; ctx.fillRect(cx-1, cy-9, 1, 1); ctx.fillRect(cx+1, cy+1, 1, 1); } else { ctx.fillStyle='#2f7a3f'; ctx.fillRect(cx-3, cy-13, 6, 22); }
  } else if (t===T.WALL){
    const frac = builtFrac(tileObj, T.WALL);
    // last 10% of durability -> the wall glows red as a warning it's about to give
    let base = '#616161';
    if (frac <= 0.10) base = '#b03a2e'; else if (frac <= 0.35) base = '#8a5a4a';
    ctx.fillStyle=base; ctx.fillRect(sx+2, sy+2, TILE-4, TILE-4);
    if (blockNoiseOn(T.WALL)) drawGrain(sx+2, sy+2, TILE-4, TILE-4, frac<=0.10?'#5a1a12':'#3a3a3a');
    ctx.strokeStyle= frac<=0.10 ? '#6a1a12' : '#3a3a3a'; ctx.strokeRect(sx+2, sy+2, TILE-4, TILE-4);
    drawCracks(cx, cy, frac);
  }
  else if (t===T.WALL_THORN) {
    const frac = builtFrac(tileObj, T.WALL_THORN);
    ctx.fillStyle= frac<=0.10 ? '#5a3a1a' : '#3a5a2a'; ctx.fillRect(sx+3, sy+3, TILE-6, TILE-6); ctx.strokeStyle='#1e3a15'; ctx.strokeRect(sx+3, sy+3, TILE-6, TILE-6);
    ctx.fillStyle='#8fae4a';
    const spikes=[[cx-8,cy-8],[cx+8,cy-8],[cx-8,cy+8],[cx+8,cy+8],[cx,cy]];
    spikes.forEach(([px,py])=>{ ctx.beginPath(); ctx.moveTo(px,py-5); ctx.lineTo(px-3,py+3); ctx.lineTo(px+3,py+3); ctx.closePath(); ctx.fill(); });
    drawCracks(cx, cy, frac);
  }
  else if (t===T.BONE_WALL) {
    const frac = builtFrac(tileObj, T.BONE_WALL);
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
  else if (t===T.CAVE_IN){
    ctx.fillStyle='#2a2a2e'; ctx.fillRect(sx+3, sy+3, TILE-6, TILE-6);
    ctx.fillStyle='#111'; for(let i=0;i<4;i++){ ctx.fillRect(sx+4, sy+6+i*4, TILE-8-i*3, 3); }   // descending stairs
    ctx.fillStyle='#3a3a44'; ctx.fillRect(sx+3, sy+3, TILE-6, 2);
  }
  else if (t===T.CAVE_UP){
    ctx.fillStyle='#4a4a52'; ctx.fillRect(sx+3, sy+3, TILE-6, TILE-6);
    ctx.fillStyle='#8a8a94'; for(let i=0;i<4;i++){ ctx.fillRect(sx+4+i*3, sy+TILE-7-i*4, TILE-8-i*3, 3); }  // ascending stairs
    ctx.fillStyle='#e8e0c8'; ctx.font='bold 10px monospace'; ctx.textAlign='center'; ctx.fillText('▲', cx, cy-6); ctx.textAlign='start';
  }
  else if (t===T.CAVE_CRYSTAL){
    ctx.fillStyle='#3a3a42'; ctx.beginPath(); ctx.moveTo(cx-11,cy+8); ctx.lineTo(cx-7,cy-7); ctx.lineTo(cx+2,cy-10); ctx.lineTo(cx+11,cy+8); ctx.closePath(); ctx.fill();
    const g=ctx.createRadialGradient(cx-2,cy-3,1,cx,cy,9); g.addColorStop(0,'#a0f0ff'); g.addColorStop(0.6,'#40b0e0'); g.addColorStop(1,'#1a5a80'); ctx.fillStyle=g;
    ctx.beginPath(); ctx.moveTo(cx,cy-9); ctx.lineTo(cx+5,cy-1); ctx.lineTo(cx,cy+8); ctx.lineTo(cx-5,cy-1); ctx.closePath(); ctx.fill();
  }
  else if (t===T.BEEHIVE){
    ctx.fillStyle='#6a4a2a'; ctx.fillRect(cx-1, cy-14, 2, 5);            // hanging string
    ctx.fillStyle='#d9a835'; ctx.fillRect(cx-8, cy-9, 16, 18);           // yellow box body
    ctx.fillStyle='#b5822a'; for(let i=0;i<3;i++) ctx.fillRect(cx-8, cy-4+i*5, 16, 2);  // stripes
    ctx.fillStyle='#3a2a12'; ctx.beginPath(); ctx.arc(cx, cy+2, 2.4, 0, 6.3); ctx.fill();  // entrance hole
    if (tileObj && tileObj.full){ ctx.fillStyle='#ffe14a'; for(let i=0;i<3;i++){ const a=performance.now()*0.01+i*2; ctx.fillRect(cx+Math.cos(a)*11-1, cy-6+Math.sin(a)*8-1, 2, 2); } }  // buzzing bees
  }
  // grey reinforcement ring drawn on top of ANY reinforced built item (wall, furnace, campfire, table...)
  drawReinforceRing(sx, sy, tileObj);
  ctx.restore();
}

// Animal artwork at the current origin — shared by the top-down view and the 3D billboards.
function drawAnimalArt(a){ let hop = Math.abs(Math.sin(performance.now() * 0.008)) * 3.5; ctx.fillStyle = 'rgba(0,0,0,0.15)'; ctx.beginPath(); ctx.ellipse(0, 6, 6, 2.5, 0, 0, 6.3); ctx.fill(); ctx.fillStyle = '#f5f5f5'; ctx.beginPath(); ctx.arc(0, -2 - hop, 6, 0, 6.3); ctx.fill(); ctx.beginPath(); ctx.arc(4, -6 - hop, 4.5, 0, 6.3); ctx.fill(); ctx.fillRect(1, -14 - hop, 1.8, 6); ctx.fillRect(4, -14 - hop, 1.8, 6); if (gfxLevel >= 5) { ctx.fillStyle = '#ffb3b3'; ctx.fillRect(1.5, -12 - hop, 0.8, 4); ctx.fillStyle = '#ffffff'; ctx.beginPath(); ctx.arc(-6, -2 - hop, 2.2, 0, 6.3); ctx.fill(); } ctx.fillStyle = '#ff9999'; ctx.fillRect(6, -6 - hop, 1.5, 1.5); if (a.isSpider && getNightFactor() > 0.4){ ctx.fillStyle='#ff2b2b'; ctx.shadowColor='#ff2b2b'; ctx.shadowBlur=6; ctx.fillRect(2.5, -7 - hop, 1.8, 1.8); ctx.fillRect(5.5, -7 - hop, 1.8, 1.8); ctx.shadowBlur=0; } }
// Enemy artwork drawn at the current origin, so both the top-down view and the 3D billboards use the SAME art.
function drawEnemyArt(e, withHpBar){
    let bob = Math.sin(performance.now() * 0.008 + e.x) * 2.5; let isRight = (e.facing === 'right');
    ctx.fillStyle = 'rgba(0,0,0,0.2)'; ctx.beginPath(); ctx.ellipse(0, 7, 8, 3, 0, 0, 6.3); ctx.fill();
    if (e.kind === 'zombie') { ctx.fillStyle = '#3c7a4b'; ctx.beginPath(); ctx.ellipse(0, -2 + bob, 7, 9, 0, 0, 6.3); ctx.fill(); ctx.fillStyle = '#2c5a35'; ctx.fillRect(isRight ? 3 : -9, -3 + bob, 6, 3.5); ctx.fillStyle = '#ffea00'; if (isRight) { ctx.fillRect(2, -6 + bob, 1.5, 1.5); ctx.fillRect(5, -6 + bob, 1.5, 1.5); } else { ctx.fillRect(-5, -6 + bob, 1.5, 1.5); ctx.fillRect(-2, -6 + bob, 1.5, 1.5); } }
    else if (e.kind === 'wolf' || e.kind === 'siberian_wolf') { ctx.fillStyle = enemyColor[e.kind]; ctx.beginPath(); ctx.ellipse(0, bob, 10, 6, 0, 0, 6.3); ctx.fill(); let hX = isRight ? 7 : -7; ctx.beginPath(); ctx.arc(hX, -3 + bob, 4, 0, 6.3); ctx.fill(); ctx.beginPath(); ctx.moveTo(hX - 1, -6 + bob); ctx.lineTo(hX, -11 + bob); ctx.lineTo(hX + 1, -6 + bob); ctx.fill(); ctx.fillStyle = e.kind === 'wolf' ? '#e74c3c' : '#00d2ff'; ctx.fillRect(isRight ? hX + 1 : hX - 2, -4 + bob, 1.5, 1.5); }
    else if (e.kind === 'scorpion') { ctx.fillStyle = '#b5743b'; ctx.beginPath(); ctx.ellipse(0, 1, 9, 5, 0, 0, 6.3); ctx.fill(); ctx.strokeStyle = '#b5743b'; ctx.lineWidth = 2.5; ctx.beginPath(); if (isRight) { ctx.arc(-5, -4, 6, 0, Math.PI, true); ctx.stroke(); ctx.fillStyle = '#733f15'; ctx.fillRect(-5, -10, 2.5, 2.5); } else { ctx.arc(5, -4, 6, 0, Math.PI, true); ctx.stroke(); ctx.fillStyle = '#733f15'; ctx.fillRect(5, -10, 2.5, 2.5); } }
    else if (e.kind === 'archer') { ctx.fillStyle = '#4a3a6a'; ctx.beginPath(); ctx.ellipse(0, -2+bob, 7, 9, 0, 0, 6.3); ctx.fill(); ctx.strokeStyle='#c9a0ff'; ctx.lineWidth=2; ctx.beginPath(); ctx.arc(isRight?5:-5, -2+bob, 6, -1, 1); ctx.stroke(); ctx.fillStyle='#ffe94a'; ctx.fillRect(-2,-6+bob,1.6,1.6); ctx.fillRect(2,-6+bob,1.6,1.6); }
    else if (e.kind === 'wraith') { ctx.globalAlpha = 0.55; const wg = ctx.createRadialGradient(0,-4+bob,1,0,-2+bob,11); wg.addColorStop(0,'#c9c9ff'); wg.addColorStop(1,'#5a5a9a'); ctx.fillStyle = wg; ctx.beginPath(); ctx.arc(0,-4+bob,8,Math.PI,0); ctx.lineTo(6,6+bob); ctx.lineTo(2,2+bob); ctx.lineTo(0,7+bob); ctx.lineTo(-2,2+bob); ctx.lineTo(-6,6+bob); ctx.closePath(); ctx.fill(); ctx.globalAlpha=1; ctx.fillStyle='#1a1a2a'; ctx.beginPath(); ctx.arc(-2.5,-5+bob,1.3,0,6.3); ctx.arc(2.5,-5+bob,1.3,0,6.3); ctx.fill(); }
    else if (e.kind === 'brute') { ctx.fillStyle = '#5a3a2a'; ctx.beginPath(); ctx.ellipse(0, bob, 13, 12, 0, 0, 6.3); ctx.fill(); ctx.fillStyle='#3a2418'; ctx.fillRect(-10,-8+bob,6,6); ctx.fillRect(4,-8+bob,6,6); ctx.fillStyle='#ffea00'; ctx.fillRect(isRight?4:-9,-3+bob,2,2); ctx.fillRect(isRight?8:-5,-3+bob,2,2); }
    else if (e.kind === 'spider') { ctx.strokeStyle='#1a1a1a'; ctx.lineWidth=2; for(let s=-1;s<=1;s+=2){ for(let li=0; li<3; li++){ ctx.beginPath(); ctx.moveTo(0, bob); ctx.lineTo(s*(9+li*2), bob - 6 + li*6); ctx.stroke(); } } ctx.fillStyle='#2a2a2e'; ctx.beginPath(); ctx.ellipse(0, bob, 7, 6, 0, 0, 6.3); ctx.fill(); ctx.beginPath(); ctx.arc(0, -4+bob, 4, 0, 6.3); ctx.fill(); ctx.fillStyle='#ff3030'; ctx.fillRect(-2.5,-5+bob,1.8,1.8); ctx.fillRect(1,-5+bob,1.8,1.8); }
    else if (e.kind === 'mummy') { ctx.fillStyle='#d8cba0'; ctx.beginPath(); ctx.ellipse(0,-2+bob,7,9,0,0,6.3); ctx.fill(); ctx.strokeStyle='#b0a480'; ctx.lineWidth=1.5; for(let i=-4;i<=4;i+=3){ ctx.beginPath(); ctx.moveTo(-7,i+bob); ctx.lineTo(7,i+bob); ctx.stroke(); } ctx.fillStyle='#3a2a10'; ctx.fillRect(-3,-6+bob,2,2); ctx.fillRect(1,-6+bob,2,2); }
    else if (e.kind === 'frost_wraith') { ctx.globalAlpha=0.62; const fg=ctx.createRadialGradient(0,-4+bob,1,0,-2+bob,11); fg.addColorStop(0,'#dff4ff'); fg.addColorStop(1,'#4a8ac0'); ctx.fillStyle=fg; ctx.beginPath(); ctx.arc(0,-4+bob,8,Math.PI,0); ctx.lineTo(6,6+bob); ctx.lineTo(2,2+bob); ctx.lineTo(0,7+bob); ctx.lineTo(-2,2+bob); ctx.lineTo(-6,6+bob); ctx.closePath(); ctx.fill(); ctx.globalAlpha=1; ctx.fillStyle='#0a3a5a'; ctx.beginPath(); ctx.arc(-2.5,-5+bob,1.3,0,6.3); ctx.arc(2.5,-5+bob,1.3,0,6.3); ctx.fill(); }
    else if (e.kind === 'boss') { ctx.save(); ctx.scale(2.6,2.6); ctx.fillStyle='rgba(0,0,0,0.25)'; ctx.beginPath(); ctx.ellipse(0,6,9,3,0,0,6.3); ctx.fill(); ctx.fillStyle='#eae6d6'; ctx.beginPath(); ctx.ellipse(0,-1+bob*0.4,8,10,0,0,6.3); ctx.fill(); ctx.fillStyle='#c8c0a8'; ctx.fillRect(-8,0+bob*0.4,16,2.5); ctx.fillRect(-8,4+bob*0.4,16,2.5); ctx.fillStyle='#111'; ctx.fillRect(-4,-5+bob*0.4,3,3); ctx.fillRect(1,-5+bob*0.4,3,3); ctx.fillStyle='#ff3b3b'; ctx.fillRect(-3.4,-4.4+bob*0.4,1.4,1.4); ctx.fillRect(1.6,-4.4+bob*0.4,1.4,1.4); ctx.restore(); }
    if (withHpBar && e!==boss){ ctx.fillStyle='#222'; ctx.fillRect(-14, -18 + bob, 28, 3); ctx.fillStyle='#c94a3d'; ctx.fillRect(-14, -18 + bob, 28*(e.hp/e.maxHp), 3); }
}

/* ============ First-person 3D view (raycaster) ============
   Renders the SAME world/tiles/creatures as the top-down view, seen from the player's own eyes.
   Full-block tiles (rock, walls, ore) are raycast as solid walls; everything else that stands on the
   ground (trees, plants, tables, monsters, animals, teammates, dropped items) is drawn as a billboard
   using its real 2D artwork, so the world looks like itself. */
let view3d = false;
let camAngle = 0;                 // where you're looking, in radians
const WALL3D = {};                // tile type -> base wall color
(function(){
  // Only things that are genuinely WALLS get raycast as full-height walls.
  WALL3D[T.WALL]='#8c8c86'; WALL3D[T.CAVE_WALL]='#6e6e7c'; WALL3D[T.BONE_WALL]='#ded6c0';
  WALL3D[T.WALL_THORN]='#6b7a3a'; WALL3D[T.FURNACE]='#6a6a6a';
  WALL3D[T.CRYSTAL_DEVICE]='#7ae0ff'; WALL3D[T.TABLET]='#c0b48a'; WALL3D[T.LUCKY]='#e0c534';
})();
// Everything that just SITS on the ground is a billboard object — stone and ore veins are chunky boulders
// and crystals lying on the floor, not tall walls.
const SPRITE3D = new Set([T.TREE,T.PINE,T.TRUNK,T.SAPLING,T.CACTUS,T.BUSH,T.CROP,T.WHEAT,T.SKULL,
  T.PLACED_TORCH,T.CAMPFIRE,T.CRAFTING_TABLE,T.UPGRADED_TABLE,T.BEEHIVE,T.GARDEN_TABLE,T.CAVE_IN,T.CAVE_UP,
  T.ROCK,T.COAL,T.IRONROCK,T.CRYSTAL_ORE,T.CAVE_CRYSTAL]);
const SPRITE3D_H = { }; SPRITE3D_H[T.TREE]=2.3; SPRITE3D_H[T.PINE]=2.5; SPRITE3D_H[T.TRUNK]=0.9; SPRITE3D_H[T.CACTUS]=1.5;
SPRITE3D_H[T.CRAFTING_TABLE]=0.9; SPRITE3D_H[T.UPGRADED_TABLE]=0.9; SPRITE3D_H[T.GARDEN_TABLE]=0.9;
SPRITE3D_H[T.BUSH]=0.8; SPRITE3D_H[T.CROP]=0.8; SPRITE3D_H[T.WHEAT]=0.8; SPRITE3D_H[T.SKULL]=0.6;
SPRITE3D_H[T.CAVE_IN]=0.5; SPRITE3D_H[T.CAVE_UP]=0.5; SPRITE3D_H[T.PLACED_TORCH]=1.2;
SPRITE3D_H[T.ROCK]=0.95; SPRITE3D_H[T.COAL]=0.95; SPRITE3D_H[T.IRONROCK]=1.0;
SPRITE3D_H[T.CRYSTAL_ORE]=1.15; SPRITE3D_H[T.CAVE_CRYSTAL]=1.15;

const tileSprCache = {};
// Trees get real volume in first person: a trunk column plus a cloud of leaves (or stacked conifer tiers).
function treeSprite(kind){
  const key = 'tree3d:'+kind;
  if (tileSprCache[key]) return tileSprCache[key];
  const c = renderToCanvas(64, 96, ()=>{
    ctx.fillStyle='#6b4423'; ctx.fillRect(27, 44, 10, 52);          // trunk
    ctx.fillStyle='#54331a'; ctx.fillRect(27, 44, 3.5, 52);         // shaded side
    if (kind==='trunk') return;
    if (kind==='pine'){
      const tiers=[{y:58,w:24},{y:42,w:19},{y:27,w:14}];
      for (const t of tiers){
        ctx.fillStyle='#1c5233'; ctx.beginPath(); ctx.moveTo(32,t.y-26); ctx.lineTo(32-t.w,t.y); ctx.lineTo(32+t.w,t.y); ctx.closePath(); ctx.fill();
        ctx.fillStyle='#eef4f8'; ctx.beginPath(); ctx.moveTo(32,t.y-26); ctx.lineTo(32-t.w*0.4,t.y-14); ctx.lineTo(32+t.w*0.4,t.y-14); ctx.closePath(); ctx.fill();
      }
    } else {
      const g = ctx.createRadialGradient(24,22,3, 32,32,30);
      g.addColorStop(0,'#6cbf5e'); g.addColorStop(1,'#1f5225');
      ctx.fillStyle = g; ctx.beginPath();
      ctx.arc(19,38,14,0,6.3); ctx.arc(45,38,14,0,6.3); ctx.arc(32,20,17,0,6.3); ctx.arc(32,34,19,0,6.3);
      ctx.fill();
    }
  });
  tileSprCache[key]=c; return c;
}
function tileSprite(t, tile){
  if (t===T.TREE) return treeSprite('tree');
  if (t===T.PINE) return treeSprite('pine');
  if (t===T.TRUNK) return treeSprite('trunk');
  const key = t + (tile && tile.species ? ':'+tile.species : '') + (tile && tile.mature ? ':m' : '');
  if (tileSprCache[key]) return tileSprCache[key];
  const c = renderToCanvas(64, 64, ()=>{ drawResourceShape(t, 16, 32, tile); });
  tileSprCache[key] = c; return c;
}
// Fog has to tint only the sprite's visible pixels ('source-atop'); painting a plain rect over its
// bounding box would show up as a translucent grey square around trees.
let sprTint = null;
function tintedSprite(img, amt, col){
  if (amt < 0.03) return img;
  if (!sprTint) sprTint = document.createElement('canvas');
  if (sprTint.width!==img.width || sprTint.height!==img.height){ sprTint.width=img.width; sprTint.height=img.height; }
  const g = sprTint.getContext('2d');
  g.setTransform(1,0,0,1,0,0); g.clearRect(0,0,sprTint.width,sprTint.height);
  g.globalCompositeOperation='source-over'; g.drawImage(img,0,0);
  g.globalCompositeOperation='source-atop'; g.fillStyle='rgba('+col[0]+','+col[1]+','+col[2]+','+Math.min(0.9,amt)+')';
  g.fillRect(0,0,sprTint.width,sprTint.height);
  g.globalCompositeOperation='source-over';
  return sprTint;
}
let entScratch = null;
function entitySprite(fn){
  if (!entScratch){ entScratch = document.createElement('canvas'); entScratch.width=64; entScratch.height=64; }
  const g = entScratch.getContext('2d'); g.clearRect(0,0,64,64);
  const saved = ctx; ctx = g; g.save(); g.translate(32, 44);
  try{ fn(); }catch(e){} finally { g.restore(); ctx = saved; }
  return entScratch;
}
function shade(hex, f){
  const n=parseInt(hex.slice(1),16); let r=(n>>16)&255,g=(n>>8)&255,b=n&255;
  r=Math.round(r*f); g=Math.round(g*f); b=Math.round(b*f);
  return 'rgb('+Math.min(255,r)+','+Math.min(255,g)+','+Math.min(255,b)+')';
}
function view3dRange(){
  const nf = getNightFactor(); const torch = (player.inv.torch||0)>0 || player.glowTimer>0;
  if (inCave) return torch ? 11 : 4.5;
  if (nf > 0.5) return torch ? 10 : 6.5;
  return 24;
}
function draw3D(){
  const nf = getNightFactor();
  // Haze colour: pale sky by day (things fade INTO the distance), near-black at night and underground.
  const fogCol = inCave ? [10,10,14]
    : [Math.round(10+158*(1-nf)), Math.round(14+186*(1-nf)), Math.round(26+196*(1-nf))];
  const maxD = view3dRange();
  const posX = player.x/TILE, posY = player.y/TILE;
  const dirX = Math.cos(camAngle), dirY = Math.sin(camAngle);
  const fov = 0.72;                                   // ~72% plane -> comfortable field of view
  const planeX = -dirY*fov, planeY = dirX*fov;
  const horizon = H*0.5;
  ctx.imageSmoothingEnabled = false;   // keep the pixel art crisp instead of blurry when scaled up

  // ---- sky / ceiling ----
  if (inCave){ ctx.fillStyle = '#15151c'; ctx.fillRect(0,0,W,horizon); }
  else {
    const sky = ctx.createLinearGradient(0,0,0,horizon);
    if (nf > 0.5){ sky.addColorStop(0,'#05060d'); sky.addColorStop(1,'#141a2c'); }
    else { sky.addColorStop(0,'#5aa8e0'); sky.addColorStop(1,'#bfe0f0'); }
    ctx.fillStyle = sky; ctx.fillRect(0,0,W,horizon);
  }
  // ---- floor (cheap floor-casting so you actually see grass / sand / snow / water underfoot) ----
  ctx.fillStyle = 'rgb('+fogCol[0]+','+fogCol[1]+','+fogCol[2]+')'; ctx.fillRect(0,horizon,W,H-horizon);
  // graphics level drives the render resolution: low = chunky and fast, high = fine detail
  const q = gfxLevel;
  const rowStep = q<=2 ? 9 : q<=4 ? 6 : 4;
  const colStep = q<=2 ? 44 : q<=4 ? 32 : 22;
  for (let y = horizon+rowStep; y < H; y += rowStep){
    const rowDist = (0.5*H) / (y - horizon);
    if (rowDist > maxD) continue;
    const fog = Math.min(1, rowDist/maxD);
    for (let sx = 0; sx < W; sx += colStep){
      const cx0 = 2*(sx+colStep/2)/W - 1;
      const wx = posX + (dirX + planeX*cx0)*rowDist, wy = posY + (dirY + planeY*cx0)*rowDist;
      const tx = Math.floor(wx), ty = Math.floor(wy);
      if (tx<0||ty<0||tx>=MAPW||ty>=MAPH) continue;
      const tl = world[ty][tx]; if (!tl) continue;
      // underground the top-down palette is almost black; lift it so first person stays readable
      ctx.fillStyle = inCave ? ((tl.type===T.CAVE_FLOOR||tl.type===T.ALTAR_FLOOR) ? '#55555f' : '#3a3a44')
                             : groundColor(biomeAt(tx,ty), tl.type);
      ctx.globalAlpha = 1-fog; ctx.fillRect(sx, y, colStep+1, rowStep+1); ctx.globalAlpha = 1;
    }
  }

  // ---- walls (DDA raycast) ----
  const step = q<=2 ? 5 : q<=4 ? 3 : 2;   // ray density follows the graphics level too
  const zBuf = new Float32Array(Math.ceil(W/step)+1);
  for (let x = 0, col = 0; x < W; x += step, col++){
    const camX = 2*x/W - 1;
    const rdx = dirX + planeX*camX, rdy = dirY + planeY*camX;
    let mapX = Math.floor(posX), mapY = Math.floor(posY);
    const dDistX = Math.abs(1/(rdx||1e-9)), dDistY = Math.abs(1/(rdy||1e-9));
    let stepX, stepY, sideDistX, sideDistY;
    if (rdx < 0){ stepX=-1; sideDistX=(posX-mapX)*dDistX; } else { stepX=1; sideDistX=(mapX+1-posX)*dDistX; }
    if (rdy < 0){ stepY=-1; sideDistY=(posY-mapY)*dDistY; } else { stepY=1; sideDistY=(mapY+1-posY)*dDistY; }
    let hit = null, side = 0, dist = 0;
    for (let iter=0; iter<160; iter++){
      if (sideDistX < sideDistY){ sideDistX += dDistX; mapX += stepX; side = 0; }
      else { sideDistY += dDistY; mapY += stepY; side = 1; }
      if (mapX<0||mapY<0||mapX>=MAPW||mapY>=MAPH) break;
      dist = side===0 ? (sideDistX-dDistX) : (sideDistY-dDistY);
      if (dist > maxD) break;
      const tl = world[mapY][mapX];
      if (tl && WALL3D[tl.type] !== undefined){ hit = tl; break; }
    }
    zBuf[col] = hit ? Math.max(0.0001, dist) : 1e9;
    if (!hit) continue;
    const lineH = H / dist;
    let y0 = horizon - lineH/2, y1 = horizon + lineH/2;
    const base = WALL3D[hit.type] || '#888';
    const fog = Math.min(1, dist/maxD);
    ctx.fillStyle = shade(base, (side===1 ? 0.72 : 1) * (1-0.45*fog));
    ctx.fillRect(x, y0, step+1, y1-y0);
    // damage darkening so a wall you're mining visibly cracks apart
    const frac = hit.maxHp ? Math.max(0, hit.hp)/hit.maxHp : 1;
    if (frac < 0.99){ ctx.fillStyle='rgba(0,0,0,'+(0.45*(1-frac))+')'; ctx.fillRect(x,y0,step+1,y1-y0); }
  }

  // ---- billboards: props, monsters, animals, teammates, dropped items ----
  const sprites = [];
  const r = Math.ceil(maxD)+1;
  const px = Math.floor(posX), py = Math.floor(posY);
  for (let ty=Math.max(0,py-r); ty<=Math.min(MAPH-1,py+r); ty++)
    for (let tx=Math.max(0,px-r); tx<=Math.min(MAPW-1,px+r); tx++){
      const tl = world[ty][tx]; if (!tl || !SPRITE3D.has(tl.type)) continue;
      sprites.push({ x:tx+0.5, y:ty+0.5, img:tileSprite(tl.type, tl), h:(SPRITE3D_H[tl.type]||1.2) });
    }
  for (const e of enemies) sprites.push({ x:e.x/TILE, y:e.y/TILE, ent:e, kind:'enemy', h:(e.kind==='boss'?2.4:1.05) });
  for (const a of animals) sprites.push({ x:a.x/TILE, y:a.y/TILE, ent:a, kind:'animal', h:0.6 });
  if (pickups) for (const pk of pickups) sprites.push({ x:pk.x/TILE, y:pk.y/TILE, ent:pk, kind:'pickup', h:0.45 });
  if (net.active && !inCave) for (const id in remotePlayers){ const rp=remotePlayers[id]; sprites.push({ x:rp.x/TILE, y:rp.y/TILE, ent:rp, kind:'peer', h:1.15 }); }
  for (const s of sprites){ const ddx=s.x-posX, ddy=s.y-posY; s.d = ddx*ddx+ddy*ddy; }
  sprites.sort((a,b)=>b.d-a.d);   // far to near

  const invDet = 1/(planeX*dirY - dirX*planeY);
  for (const s of sprites){
    const rx = s.x-posX, ry = s.y-posY;
    const tX = invDet*(dirY*rx - dirX*ry);
    const tY = invDet*(-planeY*rx + planeX*ry);     // depth along the view direction
    if (tY <= 0.15 || tY > maxD) continue;
    let img = s.img;
    if (!img){
      if (s.kind==='enemy') img = entitySprite(()=>drawEnemyArt(s.ent, false));
      else if (s.kind==='animal') img = entitySprite(()=>drawAnimalArt(s.ent));
      else if (s.kind==='peer') img = entitySprite(()=>{ const rp=s.ent; ctx.fillStyle='rgba(0,0,0,0.25)'; ctx.beginPath(); ctx.ellipse(0,7,7,3,0,0,6.3); ctx.fill(); ctx.fillStyle=rp.color||'#2f5f8a'; ctx.fillRect(-5,-4,10,10); ctx.fillStyle='#e8b98a'; ctx.beginPath(); ctx.arc(0,-9,5,0,6.3); ctx.fill(); ctx.fillStyle='#5a3a1e'; ctx.beginPath(); ctx.arc(0,-11,5.2,3.14,0); ctx.fill(); });
      else if (s.kind==='pickup') img = entitySprite(()=>{ const emo=(names[s.ent.item]||'📦').split(' ')[0]; ctx.font='18px serif'; ctx.textAlign='center'; ctx.textBaseline='middle'; ctx.fillText(emo,0,0); });
      else continue;
    }
    const lineH = H/tY;
    const sh = lineH * s.h;                       // sprite height in pixels
    const sw = sh * (img.width/img.height);
    const floorY = horizon + lineH/2;             // where the ground is at this distance
    const scrX = (W/2)*(1 + tX/tY);
    const x0 = Math.floor(scrX - sw/2), y0 = Math.floor(floorY - sh);
    const fog = Math.min(1, tY/maxD);
    img = tintedSprite(img, fog*0.85, fogCol);      // distance haze, applied to the artwork only
    // draw in vertical stripes so walls correctly hide sprites behind them
    const sStep = Math.max(2, step);
    for (let sx = Math.max(0,x0); sx < Math.min(W, x0+sw); sx += sStep){
      const col = Math.floor(sx/step);
      if (zBuf[col] !== undefined && tY >= zBuf[col]) continue;
      const u = (sx-x0)/sw * img.width, uw = Math.max(1, (sStep/sw)*img.width);
      ctx.drawImage(img, u, 0, uw, img.height, sx, y0, sStep+1, sh);
    }
  }

  // ---- soft haze band right at the horizon (walls/sprites/floor already fade individually) ----
  if (q >= 3){
    const band = Math.max(60, H*0.16);
    const fg = ctx.createLinearGradient(0,horizon-band,0,horizon+band);
    fg.addColorStop(0,'rgba('+fogCol[0]+','+fogCol[1]+','+fogCol[2]+',0)');
    fg.addColorStop(0.5,'rgba('+fogCol[0]+','+fogCol[1]+','+fogCol[2]+',0.45)');
    fg.addColorStop(1,'rgba('+fogCol[0]+','+fogCol[1]+','+fogCol[2]+',0)');
    ctx.fillStyle = fg; ctx.fillRect(0,horizon-band,W,band*2);
  }
  // Darkness as a torch-lit vignette: you can see straight ahead, the edges fall away into the dark.
  if (nf > 0.02){
    const torch = (player.inv.torch||0)>0 || player.glowTimer>0;
    const edge = inCave ? (torch?0.80:0.92) : nf*(torch?0.55:0.72);
    const core = inCave ? (torch?0.06:0.30) : nf*(torch?0.04:0.22);
    const vg = ctx.createRadialGradient(W/2,horizon,Math.min(W,H)*0.06, W/2,horizon,Math.max(W,H)*0.72);
    vg.addColorStop(0,'rgba(0,0,0,'+core+')'); vg.addColorStop(1,'rgba(0,0,0,'+edge+')');
    ctx.fillStyle = vg; ctx.fillRect(0,0,W,H);
  }

  // ---- your own hands + crosshair ----
  ctx.save();
  ctx.imageSmoothingEnabled = true;
  const bobY = player.isWalking ? Math.abs(Math.sin(performance.now()*0.008))*7 : 0;
  // Arm + weapon sit in the middle at the bottom, clear of the joystick and the action buttons.
  ctx.save(); ctx.translate(W*0.52, H-4+bobY); ctx.rotate(-0.28);
  ctx.fillStyle='#e8b98a'; ctx.fillRect(-14, -4, 28, 80);
  ctx.fillStyle='#d3a274'; ctx.fillRect(-14, -4, 5, 80);
  ctx.restore();
  const wsel = player.activeWeapon;
  ctx.font='42px serif'; ctx.textAlign='center'; ctx.textBaseline='middle';
  ctx.fillText(wsel==='bow'?'🏹':(player.equipment.iron_sword?'⚔️':'🗡️'), W*0.47, H-64+bobY);
  ctx.restore();
  ctx.strokeStyle='rgba(255,255,255,0.75)'; ctx.lineWidth=2;
  ctx.beginPath(); ctx.moveTo(W/2-10,H/2); ctx.lineTo(W/2-3,H/2); ctx.moveTo(W/2+3,H/2); ctx.lineTo(W/2+10,H/2);
  ctx.moveTo(W/2,H/2-10); ctx.lineTo(W/2,H/2-3); ctx.moveTo(W/2,H/2+3); ctx.lineTo(W/2,H/2+10); ctx.stroke();
  // what you're aiming at (so building/mining is predictable)
  const fp = frontPos(); const ftx=Math.floor(fp.fx/TILE), fty=Math.floor(fp.fy/TILE);
  if (world[fty] && world[fty][ftx] && world[fty][ftx].type!==T.GRASS){
    ctx.fillStyle='rgba(255,255,255,0.85)'; ctx.font='11px "Courier New", monospace'; ctx.textAlign='center';
    ctx.fillText((names[Object.keys(T).find(k=>T[k]===world[fty][ftx].type)]||''), W/2, H/2+26);
  }
}
function draw(){
  syncCanvasSize();
  if (view3d){ ctx.clearRect(0,0,W,H); draw3D(); drawMinimap(); return; }
  ctx.clearRect(0,0,W,H); ctx.save(); ctx.translate(W/2, H/2); ctx.scale(gameZoom, gameZoom); ctx.translate(-player.x, -player.y);
  const visibleW = W / gameZoom; const visibleH = H / gameZoom;
  const startX=Math.max(0,Math.floor((player.x - visibleW/2)/TILE)), startY=Math.max(0,Math.floor((player.y - visibleH/2)/TILE));
  const endX=Math.min(MAPW,startX+Math.ceil(visibleW/TILE)+2), endY=Math.min(MAPH,startY+Math.ceil(visibleH/TILE)+2);

  for(let y=startY;y<endY;y++) for(let x=startX;x<endX;x++){
    const t = world[y][x]; const sx=x*TILE, sy=y*TILE; const b = biomeAt(x, y);
    ctx.fillStyle = groundColor(b, t.type); ctx.fillRect(sx,sy,TILE,TILE);
    if (floorNoiseOn(b, t.type)){ const gc = t.type===T.ALTAR_FLOOR ? '#565656' : t.type===T.SAND ? '#b89a55' : t.type===T.SNOW ? '#c4cdd6' : '#2a5a24'; drawGrain(sx, sy, TILE, TILE, gc); }
    if (gfxLevel >= 5) { if (t.type === T.GRASS) { ctx.fillStyle = '#2e692a'; ctx.fillRect(sx + 5, sy + 6, 2, 4); } else if (t.type === T.SAND) { ctx.fillStyle = '#c7b06b'; ctx.fillRect(sx + 2, sy + 14, 14, 1.5); } }
    if (t.type === T.WATER && gfxLevel >= 4) { ctx.fillStyle = 'rgba(255,255,255,0.08)'; ctx.fillRect(sx + 4 + Math.sin(performance.now() * 0.003 + sx)*2, sy + 10, 8, 1.5); }
    if (t.type!==T.GRASS && t.type!==T.WATER && t.type!==T.SAND && t.type!==T.SNOW && t.type!==T.ALTAR_FLOOR && t.type!==T.CAVE_FLOOR){ drawResourceShape(t.type, sx, sy, t); }
  }

  for (const c of chests){ ctx.fillStyle='#7a5a2a'; ctx.fillRect(c.x-11, c.y-8, 22, 16); ctx.fillStyle='#9a7a3a'; ctx.fillRect(c.x-11, c.y-2, 22, 3); }
  // dropped items on the ground (transfer between teammates)
  if (pickups) for (const pk of pickups){ ctx.save(); ctx.translate(pk.x, pk.y); ctx.fillStyle='rgba(0,0,0,0.25)'; ctx.beginPath(); ctx.ellipse(0,4,7,3,0,0,6.3); ctx.fill(); const bob=Math.sin(performance.now()*0.005+pk.x)*2; const emo=(names[pk.item]||'📦').split(' ')[0]; ctx.font='16px "Courier New", monospace'; ctx.textAlign='center'; ctx.textBaseline='middle'; ctx.fillText(emo, 0, -4+bob); if(pk.count>1){ ctx.font='9px monospace'; ctx.fillStyle='#fff'; ctx.fillText('x'+pk.count, 6, 6); } ctx.textAlign='start'; ctx.textBaseline='alphabetic'; ctx.restore(); }
  for (const p of particles){ ctx.globalAlpha=Math.max(0,p.life/0.6); ctx.fillStyle = p.color; ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 6.3); ctx.fill(); ctx.globalAlpha=1; }
  for (const p of projectiles){ ctx.fillStyle='#fff'; ctx.fillRect(p.x-2, p.y-2, 4, 4); }
  for (const p of enemyProjectiles){ if(p.bone){ ctx.fillStyle='#e8e0d0'; ctx.fillRect(p.x-2, p.y-3, 4, 6); } else { ctx.fillStyle='#8a2f1a'; ctx.fillRect(p.x-2, p.y-2, 4, 4); } }
  for (const a of animals){ ctx.save(); ctx.translate(a.x, a.y); drawAnimalArt(a); ctx.restore(); }
  const enemyColor = {zombie:'#3c7a4b', scorpion:'#b5743b', wolf:'#3a3a3a', siberian_wolf:'#d5e2eb'};
  for (const e of enemies){ ctx.save(); ctx.translate(e.x, e.y); drawEnemyArt(e, true); ctx.restore(); }

  if (net.active) drawRemotePlayers();

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

  // fishing indicator bubble above the player
  if (fishing){
    ctx.save(); ctx.translate(player.x, player.y-24);
    const isBite = fishing.phase==='bite';
    ctx.fillStyle = isBite ? '#ffe14a' : 'rgba(255,255,255,0.85)'; ctx.beginPath(); ctx.arc(0,0,9,0,6.3); ctx.fill();
    ctx.fillStyle='#111'; ctx.font='bold 13px monospace'; ctx.textAlign='center'; ctx.textBaseline='middle'; ctx.fillText(isBite?'!':'…', 0, 1); ctx.textAlign='start'; ctx.textBaseline='alphabetic';
    ctx.restore();
  }

  ctx.save(); ctx.translate(player.x, player.y);

  let pBob = player.isWalking ? Math.sin(player.walkFrame) * 2 : 0; let pFeet = player.isWalking ? Math.sin(player.walkFrame) * 4 : 0;
  ctx.fillStyle = 'rgba(0,0,0,0.2)'; ctx.beginPath(); ctx.ellipse(0, 9, 8, 3, 0, 0, 6.3); ctx.fill();
  
  let df = player.facing;
  if (gfxLevel < 3 && df.includes('-')) df = df.split('-')[1];

  ctx.fillStyle = playerSkin; ctx.fillRect(-5, -4 + pBob, 10, 10);
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

  if (gfxLevel >= 5 && Math.random() < 0.08) { for(let y=startY; y<endY; y++) for(let x=startX; x<endX; x++) { if((world[y][x].type === T.CAMPFIRE || world[y][x].type === T.FURNACE) && Math.random() < 0.2) spawnParticle(x*TILE + 16 + (Math.random()*16-8), y*TILE + 16, '#ffaa00', Math.random()*2+1); } }
  ctx.restore();

  /* Night darkness overlay */
  const nf = getNightFactor();
  if (nf > 0) {
    if (lightCanvas.width !== W || lightCanvas.height !== H) { lightCanvas.width = W; lightCanvas.height = H; }
    lightCtx.fillStyle = `rgba(0, 0, 0, ${nf * (inCave ? 0.92 : nightDarkness)})`; lightCtx.fillRect(0, 0, W, H); lightCtx.globalCompositeOperation = 'destination-out';
    let baseRadius = (player.inv.torch && player.inv.torch > 0) ? torchLightRadius : BASE_TORCHLESS_RADIUS;
    if (player.glowTimer > 0) baseRadius = Math.max(baseRadius, torchLightRadius * 1.5);   // 🏮 glow lantern: strong night vision
    let radius = baseRadius * gameZoom;
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
    // teammates holding a torch light up their own area for you too
    if (net.active && !inCave){ for (const id in remotePlayers){ const rp=remotePlayers[id]; if(!rp.torch) continue; const rr=torchLightRadius*gameZoom; const rx=(rp.x-player.x)*gameZoom+W/2, ry=(rp.y-player.y)*gameZoom+H/2; const g2=lightCtx.createRadialGradient(rx,ry,5*gameZoom,rx,ry,rr); g2.addColorStop(0,'rgba(0,0,0,1)'); g2.addColorStop(1,'rgba(0,0,0,0)'); lightCtx.fillStyle=g2; lightCtx.beginPath(); lightCtx.arc(rx,ry,rr,0,6.3); lightCtx.fill(); } }
    lightCtx.globalCompositeOperation = 'source-over'; ctx.drawImage(lightCanvas, 0, 0);
  }
  if (gfxLevel >= 5) { let vignGrad = ctx.createRadialGradient(W/2, H/2, Math.min(W, H) * 0.4, W/2, H/2, Math.max(W, H) * 0.75); vignGrad.addColorStop(0, 'rgba(0,0,0,0)'); vignGrad.addColorStop(1, 'rgba(0,0,0,0.5)'); ctx.fillStyle = vignGrad; ctx.fillRect(0, 0, W, H); }
  drawMinimap();
}

const mmCanvas = document.getElementById('minimap'); const mmCtx = mmCanvas.getContext('2d');
function drawMinimap(){ mmCtx.clearRect(0,0,90,90); const scale = 90/(28*TILE); const originX = player.x - 14*TILE, originY = player.y - 14*TILE; const sx0 = Math.max(0, Math.floor(originX/TILE)), sy0=Math.max(0, Math.floor(originY/TILE)); const sx1 = Math.min(MAPW, sx0+28), sy1=Math.min(MAPH, sy0+28); for (let y=sy0;y<sy1;y+=1) for (let x=sx0;x<sx1;x+=1){ const b = biomeAt(x,y); mmCtx.fillStyle = groundColor(b,world[y][x].type); mmCtx.fillRect((x*TILE-originX)*scale, (y*TILE-originY)*scale, TILE*scale+1, TILE*scale+1); } mmCtx.fillStyle = '#c94a3d'; mmCtx.beginPath(); mmCtx.arc((player.x-originX)*scale,(player.y-originY)*scale,3,0,7); mmCtx.fill(); }

function updateHUD(){ document.querySelector('#health .bar-fill').style.width = Math.max(0,(player.health/player.maxHealth)*100)+'%'; document.querySelector('#hunger .bar-fill').style.width = Math.max(0,(player.hunger/player.maxHunger)*100)+'%'; document.getElementById('dayNum').textContent = dayNum; const nf = getNightFactor(); let label = '☀️ יום'; if (inCave) label='🕳️ מערה'; else if (eternalNightActive && !crystalActivated) label = '🌑 לילה נצחי'; else if (nf>0.66) label = '🌙 לילה'; else if (nf>0.05) label = '🌆 דמדומים'; document.getElementById('timeOfDay').textContent = label;
  const bhp = document.getElementById('bossHp'); if (bossActive && boss){ bhp.classList.add('show'); document.getElementById('bossHpFill').style.width = Math.max(0,(boss.hp/boss.maxHp)*100)+'%'; } else { bhp.classList.remove('show'); } }
function renderBag(){ 
    const wr = document.getElementById('weaponRow'); wr.innerHTML=''; 
    const weapons = [{id:'sword',icon:'🗡️'},{id:'iron_sword',icon:'⚔️'},{id:'bow',icon:'🏹'}];
    weapons.forEach(w=>{
        if ((w.id==='bow' && !player.equipment.bow) || (w.id==='iron_sword' && !player.equipment.iron_sword) || (w.id==='sword' && player.equipment.iron_sword)) return;
        const d = document.createElement('div'); d.className = 'weaponIcon' + (player.activeWeapon===w.id ? ' active':''); d.textContent = w.icon; d.onclick = ()=>{ player.activeWeapon=w.id; renderBag(); }; wr.appendChild(d);
    });

    // Tools row: axe/pickaxe are passive (shown for info); shovel & bucket are selectable (tap the map to use them)
    const tr = document.getElementById('toolRow'); tr.innerHTML='';
    const tools = [ {id:'axe',icon:'🪓'},{id:'iron_axe',icon:'🪓'},{id:'pickaxe',icon:'⛏️'},{id:'iron_pickaxe',icon:'⛏️'},{id:'shovel',icon:'🥄',sel:'dig'},{id:'bucket',icon:'🪣',sel:'bucket'},{id:'fishing_rod',icon:'🎣',sel:'fish'},{id:'bone_shield',icon:'🛡️'} ];
    let anyTool=false;
    tools.forEach(t=>{ if(!player.equipment[t.id]) return; anyTool=true;
        const d=document.createElement('div');
        const active = t.sel && player.placingItem && player.placingItem.type===t.sel;
        d.className='weaponIcon'+(active?' active':''); d.textContent=t.icon; d.title=t.id;
        if (t.sel){ d.onclick=()=>{ selectTool(t.sel); }; d.style.cursor='pointer'; }
        tr.appendChild(d);
    });
    if(!anyTool){ tr.innerHTML='<span style="font-size:10px; color:#8a8266;">אין כלים עדיין — תבנה גרזן/מכוש/את חפירה/דלי</span>'; }
    
    const resList = document.getElementById('resList'); resList.innerHTML=''; 
    Object.keys(names).forEach(k=>{ 
        if(player.inv[k]!==undefined && player.inv[k]>0){
          const row = document.createElement('div'); row.className='resRow'; 
          let eatBtn = ''; if((k==='berry' || k==='meat' || k==='bread' || k==='cooked_meat' || k==='fruit_salad' || k==='cooked_fish' || k==='big_fish' || k==='pufferfish' || k==='eel' || k==='golden_fish' || k==='honey_jar') && (player.inv[k]||0) > 0) eatBtn = `<button onclick="eatItem('${k}')" style="background:#4a6b3a; border:none; color:white; padding:3px 7px; border-radius:4px; font-size:10px; margin-left:6px; cursor:pointer;">אכל</button>`;
          if(POTIONS[k] && (player.inv[k]||0) > 0) eatBtn = `<button onclick="usePotion('${k}')" style="background:#7a3a8a; border:none; color:white; padding:3px 7px; border-radius:4px; font-size:10px; margin-left:6px; cursor:pointer;">שתה</button>`;
          let placeBtn = '';
          if (k.startsWith('item_')) { const baseId = k.replace('item_',''); placeBtn = `<button onclick="placeItemFromBag('${baseId}')" style="background:#2f7aea; border:none; color:white; padding:3px 7px; border-radius:4px; font-size:10px; margin-left:6px; cursor:pointer;">📍 הצב</button>`; }
          if (k === 'torch') { placeBtn = `<button onclick="placeTorchFromBag()" style="background:#2f7aea; border:none; color:white; padding:3px 7px; border-radius:4px; font-size:10px; margin-left:6px; cursor:pointer;">📍 הצב</button>`; }
          if (k === 'reinforcement') { placeBtn = `<button onclick="selectReinforcement()" style="background:#6a6a8a; border:none; color:white; padding:3px 7px; border-radius:4px; font-size:10px; margin-left:6px; cursor:pointer;">⛓️ חזק</button>`; }
          if (k === 'bones') { placeBtn = `<button onclick="selectFertilize()" style="background:#3a6a3a; border:none; color:white; padding:3px 7px; border-radius:4px; font-size:10px; margin-left:6px; cursor:pointer;">🌱 דשן</button>`; }
          // drop button for raw materials so you can hand them to a teammate on the ground
          let dropBtn = ''; if (!k.startsWith('item_')) dropBtn = `<button onclick="dropItem('${k}')" style="background:#7a5a2a; border:none; color:white; padding:3px 6px; border-radius:4px; font-size:10px; margin-left:6px; cursor:pointer;">⬇️</button>`;
          row.innerHTML = `<span>${names[k]}</span><span>${eatBtn}${placeBtn}${dropBtn} ${player.inv[k]||0}</span>`; resList.appendChild(row);
        }
    }); 
    
    const list = document.getElementById('craftList'); list.innerHTML=''; 
    const stations = getNearbyStations();
    
    const statusDiv = document.createElement('div'); statusDiv.style.fontSize = '11px'; statusDiv.style.color = '#e8a898'; statusDiv.style.marginBottom = '8px'; statusDiv.style.padding = '4px'; statusDiv.style.background = 'rgba(0,0,0,0.2)'; statusDiv.style.borderRadius = '4px'; 
    if (stations.garden) { statusDiv.textContent = '🌿 שולחן צמחים פעיל: שיקויים וקמעות מצמחים'; statusDiv.style.color = '#73c745'; }
    else if (stations.furnace) { statusDiv.textContent = '♨️ תנור פעיל: התכה ואפייה'; statusDiv.style.color = '#ffaa00'; }
    else if (stations.upgraded) { statusDiv.textContent = '⚙️ שולחן משודרג פעיל: ציוד מתקדם ותנורים'; statusDiv.style.color = '#8a5a36'; }
    else if (stations.table) { statusDiv.textContent = '🛠️ שולחן עבודה פעיל: ציוד בסיסי'; statusDiv.style.color = '#73c745'; }
    else { statusDiv.textContent = '🎒 תיק אישי (מתכונים בסיסיים בלבד)'; }
    list.appendChild(statusDiv);

    RECIPES.forEach(r=>{
        if (r.station === 'table' && !stations.table) return;
        if (r.station === 'upgraded' && !stations.upgraded) return;
        if (r.station === 'furnace' && !stations.furnace) return;
        if (r.station === 'campfire' && !stations.campfire) return;
        if (r.station === 'garden' && !stations.garden) return;

        const ok = canCraft(r); 
        const div = document.createElement('div'); div.className = 'craftItem' + (ok ? '' : ' disabled'); if(!ok) div.style.opacity = '0.5'; 
        const reqStr = Object.entries(r.cost).map(([k,v])=>{ const emoji = names[k] ? names[k].split(' ')[0] : ''; return `${v}${emoji}`; }).join(' '); 
        div.innerHTML = `<div style="display:flex; justify-content:space-between; width:100%;"><span>${r.name}</span><span style="color:#b0a888; font-size:10px;">עלות: ${reqStr}</span></div>`; 
        div.onclick = () => craft(r); list.appendChild(div); 
    }); 
}
function showToast(msg){ const t = document.getElementById('toast'); t.textContent = msg; t.style.opacity=1; clearTimeout(t._to); t._to = setTimeout(()=>{ t.style.opacity=0; }, 1500); }

let lastTime = performance.now();
function loop(now){
  const dt = Math.min(0.05, (now-lastTime)/1000); lastTime = now;
  // A single bad frame (e.g. a malformed network message) must never kill the whole game loop / freeze movement.
  try { update(dt); } catch(e){ console.error('update error', e); }
  try { draw(); } catch(e){ console.error('draw error', e); }
  requestAnimationFrame(loop);
}
// Build a valid world behind the start screen (gameStarted stays false so it's paused) and wait for the player's choice.
// pick a random shirt color by default (and highlight its swatch)
(function(){ const sw=document.querySelectorAll('.skinSwatch'); if(sw.length){ const i=Math.floor(Math.random()*sw.length); setSkin(sw[i].style.backgroundColor, sw[i]); } })();
// restore the saved name into the start-screen field
(function(){ const inp=document.getElementById('playerNameInput'); if(inp && playerName) inp.value = playerName; })();
gameMode = 'crystal'; initGame(); gameStarted = false; refreshSavesUI(); requestAnimationFrame(loop);
</script>
</body>
</html>
