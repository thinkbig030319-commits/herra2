/* ══════════════════════════════════════════
   SENTINEL  script.js
   Backend: http://localhost:8000
══════════════════════════════════════════ */

const API = "http://localhost:8000";

/* ── Multi-color Matrix Rain ─────────────── */
(function matrix() {
  const canvas = document.getElementById("matrixCanvas");
  const ctx    = canvas.getContext("2d");
  const CHARS  = "アイウエオカキクケコサシスセタチツナニABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&<>[]|\\";
  const FS     = 14;
  const PALETTE = ["#00ff88","#00d2ff","#c040ff","#ffb300"];
  let cols, drops, colors;

  function resize() {
    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;
    cols   = Math.floor(canvas.width / FS);
    drops  = Array(cols).fill(1);
    colors = Array.from({length: cols}, () => PALETTE[Math.floor(Math.random() * PALETTE.length)]);
  }

  function draw() {
    ctx.fillStyle = "rgba(10,22,40,0.07)";   /* lighter fade — matches bg */
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.font = FS + "px 'Share Tech Mono',monospace";

    for (let i = 0; i < drops.length; i++) {
      const ch = CHARS[Math.floor(Math.random() * CHARS.length)];
      const x  = i * FS, y = drops[i] * FS;

      if (y < 30) {
        ctx.globalAlpha = 1;
        ctx.fillStyle   = "#ffffff";
      } else {
        ctx.globalAlpha = Math.random() * 0.55 + 0.25;
        ctx.fillStyle   = colors[i];
      }
      ctx.fillText(ch, x, y);
      ctx.globalAlpha = 1;

      if (y > canvas.height && Math.random() > 0.975) {
        drops[i]  = 0;
        colors[i] = PALETTE[Math.floor(Math.random() * PALETTE.length)];
      }
      drops[i]++;
    }
  }

  resize();
  window.addEventListener("resize", resize);
  setInterval(draw, 50);
})();

/* ── Live Clock ──────────────────────────── */
(function initClock() {
  function tick() {
    const el = document.getElementById("hudClock");
    if (!el) return;
    const d = new Date(), p = n => String(n).padStart(2,"0");
    el.textContent = `${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
  }
  tick();
  setInterval(tick, 1000);
})();

/* ── Typewriter ──────────────────────────── */
(function initTW() {
  const lines = [
    "INITIALISING THREAT DETECTION...",
    "LOADING YARA SIGNATURES...",
    "AI ENGINE ONLINE.",
    "DEEP PACKET INSPECTION ACTIVE.",
    "AWAITING AUTHENTICATION.",
  ];
  const el = document.getElementById("typewriter");
  if (!el) return;
  let pi = 0, ci = 0, del = false;
  function tick() {
    const s = lines[pi];
    el.textContent = del ? s.slice(0, --ci) : s.slice(0, ++ci);
    if (!del && ci === s.length) { del = true; return setTimeout(tick, 2000); }
    if (del && ci === 0)         { del = false; pi = (pi+1) % lines.length; }
    setTimeout(tick, del ? 30 : 58);
  }
  tick();
})();

/* ── Tab Switcher ────────────────────────── */
let curTab = "login";
function switchTab(tab) {
  curTab = tab;
  const pill = document.getElementById("tabPill");
  const tl   = document.getElementById("tLogin");
  const tr   = document.getElementById("tReg");
  const lbl  = document.getElementById("submitLbl");

  pill.classList.toggle("right", tab === "register");
  tl.classList.toggle("active", tab === "login");
  tr.classList.toggle("active", tab === "register");
  lbl.innerHTML = tab === "login" ? "⟶ &nbsp;AUTHENTICATE" : "⟶ &nbsp;CREATE ACCOUNT";
  clearMsg("authResult");
}

function ke(e) { if (e.key === "Enter") doSubmit(); }
function doSubmit() { curTab === "login" ? login() : register(); }

/* ── Password Toggle ─────────────────────── */
function togPw(btn) {
  const inp = btn.parentElement.querySelector("input");
  inp.type  = inp.type === "password" ? "text" : "password";
  btn.textContent = inp.type === "password" ? "👁" : "🔒";
}

/* ── Msg helpers ─────────────────────────── */
function setMsg(id, html, type) {
  const el = document.getElementById(id);
  if (!el) return;
  el.className = "msg is-" + type;
  el.innerHTML = html;
}
function clearMsg(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.className = "msg";
  el.innerHTML = "";
}

/* ── View switch ─────────────────────────── */
function showView(name) {
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  const v = document.getElementById(name + "View");
  if (v) v.classList.add("active");
}

/* ── Register ────────────────────────────── */
async function register() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;
  if (!username || !password) return setMsg("authResult","⚠ Both fields required.","warning");

  const btn = document.getElementById("submitBtn");
  btn.disabled = true;
  setMsg("authResult","Creating account…","info");

  try {
    const res  = await fetch(`${API}/register`, {
      method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({username, password}),
    });
    const data = await res.json();
    if (res.ok) {
      setMsg("authResult","✅ Account created. You can now login.","success");
      switchTab("login");
    } else {
      setMsg("authResult","✕ " + (data.error || "Registration failed."), "error");
    }
  } catch { setMsg("authResult","✕ Cannot reach server. Is the backend running?","error"); }
  finally { btn.disabled = false; }
}

/* ── Login ───────────────────────────────── */
async function login() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;
  if (!username || !password) return setMsg("authResult","⚠ Both fields required.","warning");

  const btn = document.getElementById("submitBtn");
  btn.disabled = true;
  setMsg("authResult","Authenticating…","info");

  try {
    const res  = await fetch(`${API}/login`, {
      method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({username, password}),
    });
    const data = await res.json();
    if (res.ok) {
      localStorage.setItem("token",  data.access_token);
      localStorage.setItem("s_user", username);
      enterScan(username);
    } else {
      setMsg("authResult","✕ " + (data.error || "Invalid credentials."), "error");
    }
  } catch { setMsg("authResult","✕ Cannot reach server. Is the backend running?","error"); }
  finally { btn.disabled = false; }
}

/* ── Logout ──────────────────────────────── */
function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("s_user");
  stopStats();
  resetScanUI();
  showView("auth");
}

/* ── Enter scan view ─────────────────────── */
function enterScan(user) {
  const el = document.getElementById("scanUser");
  if (el) el.textContent = "● " + (user||"").toUpperCase();
  showView("scan");
  startStats();
}

/* ── File handling ───────────────────────── */
function fmt(b) {
  if (b < 1024)    return b + " B";
  if (b < 1048576) return (b/1024).toFixed(1) + " KB";
  return (b/1048576).toFixed(2) + " MB";
}
function filePicked(inp) {
  if (!inp.files.length) return;
  showChosen(inp.files[0]);
  clearMsg("result");
  document.getElementById("resultDetail").style.display = "none";
}
function showChosen(f) {
  document.getElementById("dropDefault").style.display  = "none";
  document.getElementById("dropChosen").style.display   = "block";
  document.getElementById("cName").textContent = f.name;
  document.getElementById("cSize").textContent = fmt(f.size);
}
function clearFile(e) {
  e.stopPropagation();
  document.getElementById("fileInput").value            = "";
  document.getElementById("dropDefault").style.display = "block";
  document.getElementById("dropChosen").style.display  = "none";
  clearMsg("result");
  document.getElementById("resultDetail").style.display = "none";
}
function dov(e) { e.preventDefault(); document.getElementById("dropZone").classList.add("dragover"); }
function dol()  { document.getElementById("dropZone").classList.remove("dragover"); }
function dof(e) {
  e.preventDefault(); dol();
  const f = e.dataTransfer.files[0];
  if (!f) return;
  const dt = new DataTransfer(); dt.items.add(f);
  document.getElementById("fileInput").files = dt.files;
  showChosen(f);
  clearMsg("result");
  document.getElementById("resultDetail").style.display = "none";
}
function resetScanUI() {
  document.getElementById("fileInput").value            = "";
  document.getElementById("dropDefault").style.display = "block";
  document.getElementById("dropChosen").style.display  = "none";
  clearMsg("result");
  const d = document.getElementById("resultDetail");
  if (d) d.style.display = "none";
}

/* ── Scan file ───────────────────────────── */
async function scanFile() {
  const fi  = document.getElementById("fileInput");
  const btn = document.getElementById("scanBtn");
  const lbl = document.getElementById("scanLbl");
  const prg = document.getElementById("scanProg");
  const det = document.getElementById("resultDetail");

  if (!fi.files.length) return setMsg("result","⚠ Please select a file first.","warning");
  const token = localStorage.getItem("token");
  if (!token) { setMsg("result","✕ Session expired. Please login again.","error"); logout(); return; }

  btn.disabled      = true;
  lbl.textContent   = "⟳  SCANNING…";
  prg.style.display = "block";
  det.style.display = "none";
  clearMsg("result");

  const fd = new FormData();
  fd.append("file", fi.files[0]);

  try {
    const res = await fetch(`${API}/scan`, {
      method:"POST", headers:{"Authorization": `Bearer ${token}`}, body: fd,
    });
    if (res.status === 401) { logout(); return; }
    const data = await res.json();
    if (!res.ok) { setMsg("result","✕ Scan error: " + (data.error||"Unknown."),"error"); return; }
    renderResult(data);
  } catch { setMsg("result","✕ Server error. Make sure the backend is running.","error"); }
  finally {
    btn.disabled      = false;
    lbl.innerHTML     = "⟳ &nbsp;SCAN FILE";
    prg.style.display = "none";
  }
}

/* ── Render scan result ──────────────────── */
function renderResult(data) {
  const high  = data.threat_level === "HIGH";
  const pct   = (data.confidence * 100).toFixed(1);
  const clean = data.yara_result === "Clean";

  if (high) {
    const rules = !clean ? ` · ${data.yara_result}` : "";
    setMsg("result", `❌ THREAT DETECTED — ${data.ai_prediction} @ ${pct}%${rules}`, "error");
  } else {
    setMsg("result", `✅ FILE CLEAN — ${data.ai_prediction} @ ${pct}%`, "success");
  }

  // Update threat indicators
  const tn = document.getElementById("threatNum");
  if (tn) { tn.textContent = data.threat_level; tn.className = "sp-val " + (high ? "r" : "g"); }
  const ht = document.getElementById("hudThreat");
  if (ht) ht.textContent = "THREAT:" + data.threat_level;

  // Detail rows
  document.getElementById("dFile").textContent = data.filename      || "—";
  document.getElementById("dHash").textContent = data.sha256        || "—";

  const ye = document.getElementById("dYara");
  ye.textContent = data.yara_result || "—";
  ye.className   = "dv " + (clean ? "vg" : "va");

  document.getElementById("dAi").textContent   = data.ai_prediction || "—";
  document.getElementById("dConf").textContent = pct + "%";

  const te = document.getElementById("dThreat");
  te.textContent = data.threat_level || "—";
  te.className   = "dv " + (high ? "vr" : "vg");

  document.getElementById("resultDetail").style.display = "block";
}

/* ── Stats polling /stats ────────────────── */
let statsTimer = null;
async function fetchStats() {
  try {
    const data = await (await fetch(`${API}/stats`)).json();
    const cpu  = parseFloat(data.cpu)    || 0;
    const mem  = parseFloat(data.memory) || 0;
    document.getElementById("cpuFill").style.width = Math.min(cpu,100) + "%";
    document.getElementById("memFill").style.width = Math.min(mem,100) + "%";
    document.getElementById("cpuVal").textContent  = cpu.toFixed(1) + "%";
    document.getElementById("memVal").textContent  = mem.toFixed(1) + "%";
  } catch {}
}
function startStats() { fetchStats(); statsTimer = setInterval(fetchStats, 3000); }
function stopStats()  { clearInterval(statsTimer); statsTimer = null; }

/* ── Boot ────────────────────────────────── */
window.onload = () => {
  const tok  = localStorage.getItem("token");
  const user = localStorage.getItem("s_user");
  if (tok) enterScan(user || "USER");
};