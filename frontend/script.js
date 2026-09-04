/* ============================================================
   GOD'S EYE — Forensic Pipeline Frontend Controller
   ============================================================ */

const API_BASE = (window.GODSEYE_API || "").replace(/\/$/, "");
const EXPLORER_BASE = "https://etherscan.io/tx/";

/* ---- Element refs -------------------------------------------------------- */
const $ = (id) => document.getElementById(id);

const dropzone = $("dropzone");
const fileInput = $("fileInput");
const dropzoneEmpty = $("dropzoneEmpty");
const dropzonePreview = $("dropzonePreview");
const previewImg = $("previewImg");
const clearFileBtn = $("clearFile");
const metaPills = $("metaPills");
const contributorInput = $("contributor");
const runBtn = $("runBtn");

const stepper = $("stepper");
const stepEls = () => Array.from(stepper.querySelectorAll(".step"));
const linkEls = () => Array.from(stepper.querySelectorAll(".step__link"));

const statusBadge = $("statusBadge");
const telemetryEmpty = $("telemetryEmpty");
const telemetryBody = $("telemetryBody");

const auditBody = $("auditBody");
const tableEmpty = $("tableEmpty");
const auditMeta = $("auditMeta");
const refreshBtn = $("refreshBtn");

const lookupInput = $("lookupInput");
const lookupBtn = $("lookupBtn");
const lookupResult = $("lookupResult");

const toast = $("toast");

let selectedFile = null;

/* ---- Robust Lucide Icon Rendering --------------------------------------- */
function icons() {
  if (window.lucide && typeof window.lucide.createIcons === "function") {
    window.lucide.createIcons();
  } else {
    setTimeout(icons, 50);
  }
}

function showToast(msg, type = "") {
  toast.className = "toast is-show " + type;
  toast.innerHTML = "";
  const span = document.createElement("span");
  span.textContent = msg;
  toast.appendChild(span);
  clearTimeout(showToast._t);
  showToast._t = setTimeout(() => (toast.className = "toast"), 3200);
}

function truncateHash(h, head = 10, tail = 8) {
  if (!h) return "—";
  const s = String(h);
  if (s.length <= head + tail + 3) return s;
  return `${s.slice(0, head)}…${s.slice(-tail)}`;
}

function formatBytes(bytes) {
  if (!bytes && bytes !== 0) return "—";
  const u = ["B", "KB", "MB", "GB"];
  let i = 0, n = bytes;
  while (n >= 1024 && i < u.length - 1) { n /= 1024; i++; }
  return `${n.toFixed(n < 10 && i > 0 ? 1 : 0)} ${u[i]}`;
}

function normalizeTheme(theme) {
  const t = String(theme || "").toLowerCase();
  if (["success", "warning", "caution", "danger"].includes(t)) return t;
  return "caution";
}

function pctFromConfidence(conf) {
  if (conf == null) return 0;
  const n = parseFloat(String(conf).replace("%", ""));
  return Number.isFinite(n) ? Math.max(0, Math.min(100, n)) : 0;
}

/* ---- Copy to clipboard --------------------------------------------------- */
async function copyText(text) {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
    } else {
      const ta = document.createElement("textarea");
      ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      document.execCommand("copy"); document.body.removeChild(ta);
    }
    return true;
  } catch { return false; }
}

document.addEventListener("click", async (e) => {
  const btn = e.target.closest("[data-copy-target]");
  if (!btn) return;
  const target = $(btn.dataset.copyTarget);
  const val = target ? target.textContent.trim() : "";
  if (!val || val === "—") return;
  const ok = await copyText(val);
  if (ok) {
    btn.classList.add("is-copied");
    const orig = btn.innerHTML;
    btn.innerHTML = '<i data-lucide="check"></i>';
    icons();
    showToast("Copied to clipboard", "success");
    setTimeout(() => { btn.classList.remove("is-copied"); btn.innerHTML = orig; icons(); }, 1400);
  } else {
    showToast("Copy failed", "error");
  }
});

/* ============================================================
   FILE HANDLING & DRAG-DROP
   ============================================================ */
function handleFile(file) {
  if (!file) return;
  if (!file.type.startsWith("image/")) {
    showToast("Only image assets are accepted", "error");
    return;
  }
  selectedFile = file;

  const url = URL.createObjectURL(file);
  previewImg.src = url;
  previewImg.onload = () => {
    $("metaDims").textContent = `${previewImg.naturalWidth}×${previewImg.naturalHeight}px`;
    URL.revokeObjectURL(url);
  };

  dropzoneEmpty.hidden = true;
  dropzonePreview.hidden = false;
  metaPills.hidden = false;

  $("metaName").textContent = file.name;
  $("metaSize").textContent = formatBytes(file.size);
  $("metaType").textContent = (file.type.split("/")[1] || "img").toUpperCase();

  updateRunState();
  icons();
}

function clearFile() {
  selectedFile = null;
  fileInput.value = "";
  previewImg.src = "";
  dropzoneEmpty.hidden = false;
  dropzonePreview.hidden = true;
  metaPills.hidden = true;
  updateRunState();
}

function updateRunState() {
  const hasFile = Boolean(selectedFile);
  const hasCompany = Boolean(contributorInput.value.trim());
  runBtn.disabled = !(hasFile && hasCompany);
}

contributorInput.addEventListener("input", updateRunState);

dropzone.addEventListener("click", (e) => {
  if (e.target.closest(".dropzone__clear")) return;
  fileInput.click();
});
dropzone.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") { e.preventDefault(); fileInput.click(); }
});
fileInput.addEventListener("change", (e) => handleFile(e.target.files[0]));
clearFileBtn.addEventListener("click", (e) => { e.stopPropagation(); clearFile(); });

["dragenter", "dragover"].forEach((ev) =>
  dropzone.addEventListener(ev, (e) => { e.preventDefault(); dropzone.classList.add("is-drag"); })
);
["dragleave", "drop"].forEach((ev) =>
  dropzone.addEventListener(ev, (e) => { e.preventDefault(); dropzone.classList.remove("is-drag"); })
);
dropzone.addEventListener("drop", (e) => {
  const file = e.dataTransfer?.files?.[0];
  if (file) handleFile(file);
});

/* ============================================================
   PIPELINE STEPPER
   ============================================================ */
function resetStepper() {
  stepEls().forEach((s) => s.classList.remove("is-active", "is-processing", "is-pass", "is-fail"));
  linkEls().forEach((l) => l.classList.remove("is-filled"));
}

function animateProcessing() {
  return new Promise((resolve) => {
    resetStepper();
    const steps = stepEls();
    const links = linkEls();
    let i = 0;
    const tick = () => {
      if (i > 0) steps[i - 1].classList.remove("is-processing");
      if (i >= steps.length) { resolve(); return; }
      steps[i].classList.add("is-active", "is-processing");
      if (i > 0 && links[i - 1]) links[i - 1].classList.add("is-filled");
      i++;
      animateProcessing._t = setTimeout(tick, 420);
    };
    tick();
  });
}

function applyStepResults(checks) {
  clearTimeout(animateProcessing._t);
  const steps = stepEls();
  const links = linkEls();
  steps.forEach((s) => s.classList.remove("is-active", "is-processing"));

  steps.forEach((step, idx) => {
    const key = step.dataset.key;
    const raw = checks ? checks[key] : undefined;
    const passed = isPass(raw);
    setTimeout(() => {
      step.classList.remove("is-pass", "is-fail");
      step.classList.add(passed ? "is-pass" : "is-fail");
      if (idx > 0 && links[idx - 1]) links[idx - 1].classList.add("is-filled");
    }, idx * 220);
  });
}

function isPass(v) {
  if (v == null) return false;
  const s = String(v).trim().toUpperCase();
  return s === "✅" || s === "PASS" || s === "TRUE" || s === "OK" || s === "VERIFIED";
}

/* ============================================================
   RUN PIPELINE
   ============================================================ */
runBtn.addEventListener("click", runPipeline);

async function runPipeline() {
  if (!selectedFile) {
    showToast("Please select an evidence file first.", "error");
    return;
  }
  const contributor = contributorInput.value.trim();
  if (!contributor) {
    showToast("Contributor / Entity field is mandatory!", "error");
    contributorInput.focus();
    return;
  }

  runBtn.classList.add("is-loading");
  setBadge("PROCESSING", "processing");
  telemetryEmpty.hidden = true;
  telemetryBody.hidden = true;

  const anim = animateProcessing();

  const form = new FormData();
  form.append("file", selectedFile);
  form.append("contributor", contributor);

  try {
    const res = await fetch(`${API_BASE}/process-pipeline`, { method: "POST", body: form });
    if (!res.ok) throw new Error(`Backend responded ${res.status}`);
    const data = await res.json();

    await anim;
    renderTelemetry(data);
    applyStepResults(data.checks);
    showToast(`Pipeline complete — ${data.status || "DONE"}`, "success");
    loadHistory(true);
  } catch (err) {
    console.log("[v0] pipeline error:", err.message);
    clearTimeout(animateProcessing._t);
    resetStepper();
    stepEls().forEach((s) => s.classList.add("is-fail"));
    setBadge("PIPELINE ERROR", "danger");
    telemetryEmpty.hidden = false;
    telemetryEmpty.querySelector("p").textContent =
      `Unable to reach the forensic backend (${err.message}). Verify the FastAPI service is running.`;
    telemetryBody.hidden = true;
    showToast("Pipeline request failed", "error");
  } finally {
    runBtn.classList.remove("is-loading");
  }
}

function setBadge(text, theme) {
  statusBadge.textContent = text;
  statusBadge.className = "status-badge status-badge--" + (theme || "idle");
}

/* ---- Render telemetry ---------------------------------------------------- */
function renderTelemetry(d) {
  telemetryEmpty.hidden = true;
  telemetryBody.hidden = false;

  const theme = normalizeTheme(d.status_theme);
  setBadge(d.status || "UNKNOWN", theme);

  $("predVal").textContent = d.prediction || "—";
  $("modelVal").textContent = d.model_version || "—";

  const pct = pctFromConfidence(d.confidence);
  const ring = $("confRing");
  ring.style.setProperty("--pct", pct);
  $("confVal").textContent = d.confidence != null
    ? (String(d.confidence).includes("%") ? d.confidence : `${pct}%`)
    : "—";

  const ringColor = { 
    success: "var(--emerald-hot)", 
    warning: "var(--amber)", 
    caution: "var(--amber)", 
    danger: "var(--crimson-hot)" 
  }[theme] || "var(--amber)";

  ring.style.background = `conic-gradient(${ringColor} calc(${pct} * 1%), rgba(255,255,255,0.06) 0)`;
  $("confVal").style.color = ringColor;

  $("sha256Val").textContent = d.sha256 || d.image_hash || "—";
  $("phashVal").textContent = d.phash || "—";

  const callout = $("callout");
  callout.className = "callout callout--" + theme;
  $("calloutTitle").textContent = calloutTitleFor(theme);
  $("calloutMsg").textContent = d.message || "No forensic message provided.";
  const calloutIco = { 
    success: "shield-check", 
    warning: "alert-triangle", 
    caution: "alert-triangle", 
    danger: "shield-alert" 
  }[theme] || "shield-alert";
  callout.querySelector(".callout__ico").setAttribute("data-lucide", calloutIco);

  const receipt = $("receipt");
  if (d.blockchain_tx && d.blockchain_tx !== "NOT_RECORDED" && d.blockchain_tx !== "REJECTED_NOT_MINED") {
    receipt.classList.remove("is-hidden");
    $("txVal").textContent = d.blockchain_tx;
    
    // Wire up block explorer and forensic assurance certificate link
    const certUrl = d.record_id ? `${API_BASE}/export-report/${d.record_id}` : "#";
    $("txLink").href = EXPLORER_BASE + encodeURIComponent(d.blockchain_tx);
    
    let certLink = $("certActionLink");
    if (!certLink) {
      certLink = document.createElement("a");
      certLink.id = "certActionLink";
      certLink.className = "receipt__link";
      certLink.target = "_blank";
      certLink.rel = "noopener noreferrer";
      certLink.style.marginLeft = "14px";
      certLink.style.color = "var(--emerald-hot, #10b981)";
      $("txLink").parentNode.appendChild(certLink);
    }
    certLink.href = certUrl;
    certLink.innerHTML = `<i data-lucide="file-check"></i> Export Forensic Certificate (#${d.record_id || "—"})`;
    certLink.style.display = d.record_id ? "inline-flex" : "none";
  } else {
    receipt.classList.add("is-hidden");
    const certLink = $("certActionLink");
    if (certLink) certLink.style.display = "none";
  }

  icons();
}

function calloutTitleFor(theme) {
  return {
    success: "Integrity Verified",
    warning: "Domain Warning",
    caution: "Compliance Caution",
    danger: "Tampering / Breach Alert",
  }[theme] || "Forensic Verdict";
}

/* ============================================================
   AUDIT TRAIL
   ============================================================ */
function statusThemeFromString(status) {
  const s = String(status || "").toUpperCase();
  if (s.includes("VERIFIED")) return "success";
  if (s.includes("TAMPER")) return "danger";
  if (s.includes("PLAGIARISM") || s.includes("BREACH")) return "danger";
  if (s.includes("NON-COMPLIANT") || s.includes("REJECT")) return "warning";
  if (s.includes("DUPLICATE")) return "caution";
  return "caution";
}

function skeletonRows(n = 4) {
  auditBody.innerHTML = "";
  tableEmpty.hidden = true;
  for (let i = 0; i < n; i++) {
    const tr = document.createElement("tr");
    tr.className = "skeleton-row";
    tr.innerHTML = Array.from({ length: 9 })
      .map(() => `<td><div class="skeleton-bar" style="width:${60 + Math.random() * 40}%"></div></td>`)
      .join("");
    auditBody.appendChild(tr);
  }
}

async function loadHistory(silent = false) {
  if (!silent) {
    refreshBtn.classList.add("is-loading");
    skeletonRows();
  }
  try {
    const res = await fetch(`${API_BASE}/get-history?limit=15`);
    if (!res.ok) throw new Error(`Backend responded ${res.status}`);
    const data = await res.json();
    renderHistory(data.logs || []);
  } catch (err) {
    console.log("[v0] history error:", err.message);
    auditBody.innerHTML = "";
    tableEmpty.hidden = false;
    tableEmpty.querySelector("p").textContent =
      `Unable to load audit trail (${err.message}).`;
    auditMeta.textContent = "Offline";
  } finally {
    refreshBtn.classList.remove("is-loading");
  }
}

function renderHistory(logs) {
  auditBody.innerHTML = "";
  if (!logs.length) {
    tableEmpty.hidden = false;
    tableEmpty.querySelector("p").textContent = "No verification records yet.";
    auditMeta.textContent = "0 records";
    return;
  }
  tableEmpty.hidden = true;
  auditMeta.textContent = `Latest ${logs.length} records`;

  logs.forEach((log) => {
    const theme = statusThemeFromString(log.status);
    const tx = log.blockchain_tx || "";
    const isMined = tx && tx !== "NOT_RECORDED" && tx !== "REJECTED_NOT_MINED";
    const cleanName = (log.filename || "asset.jpg").replace(/^\d+_/, "");
    const imgUrl = log.image_url || `${API_BASE}/uploads/${encodeURIComponent(log.filename || "")}`;

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td class="td-id">#${escapeHtml(String(log.id ?? "—"))}</td>
      <td class="td-thumb" style="width: 54px; text-align: center;">
        <img src="${imgUrl}" 
             class="audit-thumb" 
             alt="Evidence" 
             title="Click to view evidence image"
             data-img="${imgUrl}"
             data-title="${escapeHtml(cleanName)}"
             data-status="${escapeHtml(log.status || '—')}"
             onerror="this.style.opacity='0.25'; this.title='Image preview unavailable';" />
      </td>
      <td class="td-time">${escapeHtml(log.timestamp || "—")}</td>
      <td class="td-contrib">${escapeHtml(log.contributor || "—")}</td>
      <td class="td-asset"><code>${escapeHtml(cleanName)}</code></td>
      <td>
        <span class="td-detect">
          <span class="chip">${escapeHtml(log.detected_vehicle || "—")}</span>
          <span class="conf">${log.confidence != null ? escapeHtml(String(log.confidence)) + "%" : ""}</span>
        </span>
      </td>
      <td><span class="badge-cell ${theme}">${escapeHtml(log.status || "—")}</span></td>
      <td class="td-tx">${isMined
        ? `<a href="${EXPLORER_BASE + encodeURIComponent(tx)}" target="_blank" rel="noopener noreferrer">${escapeHtml(truncateHash(tx))} <i data-lucide="external-link"></i></a>`
        : `<span style="color: var(--txt-faint, #64748b);">REJECTED</span>`}</td>
      <td class="td-audit">
        <button type="button" aria-expanded="false"><i data-lucide="chevron-down"></i> Details</button>
      </td>
    `;
    auditBody.appendChild(tr);

    // Click handler for modal inspection
    const thumbImg = tr.querySelector(".audit-thumb");
    if (thumbImg) {
      thumbImg.addEventListener("click", (e) => {
        e.stopPropagation();
        if (typeof openEvidenceModal === "function") {
          openEvidenceModal(thumbImg.dataset.img, thumbImg.dataset.title, thumbImg.dataset.status);
        }
      });
    }

    const detailTr = document.createElement("tr");
    detailTr.className = "detail-row";
    detailTr.hidden = true;
    detailTr.innerHTML = `
      <td colspan="9">
        <div class="detail-inner">
          <div class="detail-item"><span class="k">Image Hash</span><span class="v">${escapeHtml(log.image_hash || "—")}</span></div>
          <div class="detail-item"><span class="k">Model Version</span><span class="v">${escapeHtml(log.model_version || "—")}</span></div>
          <div class="detail-item"><span class="k">Cryptographic Binding</span><span class="v" style="font-family:var(--font-mono); color:var(--cyan-glow, #38bdf8);">${escapeHtml(log.bound_digest || "N/A")}</span></div>
          <div class="detail-item"><span class="k">Image Integrity</span><span class="v">${checkPill(log.image_integrity)}</span></div>
          <div class="detail-item"><span class="k">Model Integrity</span><span class="v">${checkPill(log.model_integrity)}</span></div>
          <div class="detail-item"><span class="k">Result Integrity</span><span class="v">${checkPill(log.result_integrity)}</span></div>
          <div class="detail-item"><span class="k">Detail</span><span class="v">${escapeHtml(log.detail || "—")}</span></div>
          <div class="detail-item" style="grid-column:1/-1; margin-top:8px;">
            <a href="${API_BASE}/export-report/${log.id}" target="_blank" rel="noopener noreferrer" style="display:inline-flex; align-items:center; gap:6px; padding:6px 12px; background:rgba(16,185,129,0.12); border:1px solid rgba(16,185,129,0.3); border-radius:6px; color:#10b981; text-decoration:none; font-size:12px; font-weight:600;">
              <i data-lucide="printer"></i> View / Print Assurance Certificate
            </a>
          </div>
        </div>
      </td>`;
    auditBody.appendChild(detailTr);

    const btn = tr.querySelector(".td-audit button");
    btn.addEventListener("click", () => {
      const open = !detailTr.hidden;
      detailTr.hidden = open;
      btn.setAttribute("aria-expanded", String(!open));
      btn.innerHTML = open
        ? '<i data-lucide="chevron-down"></i> Details'
        : '<i data-lucide="chevron-up"></i> Hide';
      icons();
    });
  });

  icons();
}

function checkPill(v) {
  const pass = isPass(v);
  return `<span class="detail-check ${pass ? "pass" : "fail"}">${pass ? "✔ PASS" : "✕ FAIL"}</span>`;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

refreshBtn.addEventListener("click", () => loadHistory());

/* ============================================================
   JUDICIAL LOOKUP
   ============================================================ */
lookupBtn.addEventListener("click", runLookup);
lookupInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.nativeEvent?.isComposing && e.keyCode !== 229) runLookup();
});

async function runLookup() {
  const query = lookupInput.value.trim();
  if (!query) { showToast("Enter a transaction or image hash", "error"); return; }

  lookupBtn.classList.add("is-loading");
  lookupResult.hidden = false;
  lookupResult.innerHTML = `<div class="proof-card"><div class="skeleton-bar" style="height:16px;width:40%;margin-bottom:14px"></div>
    <div class="skeleton-bar" style="height:12px;width:90%;margin-bottom:8px"></div>
    <div class="skeleton-bar" style="height:12px;width:70%"></div></div>`;

  try {
    const res = await fetch(`${API_BASE}/get-history?limit=200`);
    if (!res.ok) throw new Error(`Backend responded ${res.status}`);
    const data = await res.json();
    const q = query.toLowerCase();
    const match = (data.logs || []).find((l) =>
      String(l.blockchain_tx || "").toLowerCase() === q ||
      String(l.blockchain_tx || "").toLowerCase().startsWith(q) ||
      String(l.image_hash || "").toLowerCase() === q ||
      String(l.image_hash || "").toLowerCase().startsWith(q)
    );
    renderLookup(match, query);
  } catch (err) {
    console.log("[v0] lookup error:", err.message);
    lookupResult.innerHTML = `<div class="lookup-notfound">
      <i data-lucide="server-crash"></i>
      <p>Unable to query the ledger (${escapeHtml(err.message)}).</p></div>`;
    icons();
  } finally {
    lookupBtn.classList.remove("is-loading");
  }
}

function renderLookup(log, query) {
  if (!log) {
    lookupResult.innerHTML = `<div class="lookup-notfound">
      <i data-lucide="search-x"></i>
      <p>No on-chain record matches <b>${escapeHtml(truncateHash(query, 12, 10))}</b>. The asset or transaction is not present in the immutable ledger.</p>
    </div>`;
    icons();
    return;
  }
  const theme = statusThemeFromString(log.status);
  const tx = log.blockchain_tx || "";
  const isMined = tx && tx !== "NOT_RECORDED" && tx !== "REJECTED_NOT_MINED";
  lookupResult.innerHTML = `
    <div class="proof-card">
      <div class="proof-card__head">
        <span class="proof-card__title"><i data-lucide="badge-check"></i> Immutable On-Chain Proof Located</span>
        <span class="badge-cell ${theme}">${escapeHtml(log.status || "—")}</span>
      </div>
      <div class="proof-grid">
        <div class="proof-item"><div class="proof-item__k">Record ID</div><div class="proof-item__v accent">#${escapeHtml(String(log.id ?? "—"))}</div></div>
        <div class="proof-item"><div class="proof-item__k">Timestamp</div><div class="proof-item__v">${escapeHtml(log.timestamp || "—")}</div></div>
        <div class="proof-item"><div class="proof-item__k">Contributor</div><div class="proof-item__v">${escapeHtml(log.contributor || "—")}</div></div>
        <div class="proof-item"><div class="proof-item__k">Asset</div><div class="proof-item__v">${escapeHtml(log.filename || "—")}</div></div>
        <div class="proof-item"><div class="proof-item__k">Detection</div><div class="proof-item__v accent">${escapeHtml(log.detected_vehicle || "—")} · ${escapeHtml(String(log.confidence ?? "—"))}%</div></div>
        <div class="proof-item"><div class="proof-item__k">Model Version</div><div class="proof-item__v">${escapeHtml(log.model_version || "—")}</div></div>
        <div class="proof-item" style="grid-column:1/-1"><div class="proof-item__k">Image Hash</div><div class="proof-item__v">${escapeHtml(log.image_hash || "—")}</div></div>
        <div class="proof-item" style="grid-column:1/-1"><div class="proof-item__k">Cryptographic Proof Binding</div><div class="proof-item__v accent">${escapeHtml(log.bound_digest || "N/A")}</div></div>
        <div class="proof-item" style="grid-column:1/-1"><div class="proof-item__k">Blockchain Transaction</div><div class="proof-item__v accent">${escapeHtml(tx || "—")}</div></div>
      </div>
      <div style="display:flex; gap:14px; margin-top:14px;">
        ${isMined ? `<a class="receipt__link" href="${EXPLORER_BASE + encodeURIComponent(tx)}" target="_blank" rel="noopener noreferrer"><i data-lucide="external-link"></i> View on Block Explorer</a>` : ""}
        <a class="receipt__link" href="${API_BASE}/export-report/${log.id}" target="_blank" rel="noopener noreferrer" style="color:var(--emerald-hot, #10b981);"><i data-lucide="file-check"></i> Export Judicial Certificate</a>
      </div>
    </div>`;
  icons();
}

/* ============================================================
   TABS
   ============================================================ */
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => {
      t.classList.remove("is-active");
      t.setAttribute("aria-selected", "false");
    });
    document.querySelectorAll(".panel").forEach((p) => {
      p.classList.remove("is-active");
      p.hidden = true;
    });
    tab.classList.add("is-active");
    tab.setAttribute("aria-selected", "true");
    const panel = $("panel-" + tab.dataset.tab);
    panel.hidden = false;
    panel.classList.add("is-active");
  });
});

/* ============================================================
   CLOCK
   ============================================================ */
function tickClock() {
  const now = new Date();
  const p = (n) => String(n).padStart(2, "0");
  $("clock").textContent = `${p(now.getHours())}:${p(now.getMinutes())}:${p(now.getSeconds())} UTC${now.getTimezoneOffset() <= 0 ? "+" : "-"}${Math.abs(now.getTimezoneOffset() / 60)}`;
}

/* ============================================================
   BULK DATASET INGESTION & ENTITY RISK PROFILER CONTROLLER
   ============================================================ */
const batchDropzone = $("batch-dropzone");
const batchFileInput = $("batch-file-input");
const btnRunBatch = $("btn-run-batch");
const batchContributorInput = $("batch-contributor");
const batchProgressContainer = $("batch-progress-container");
const batchProgressBar = $("batch-progress-bar");
const batchProgressStatus = $("batch-progress-status");
const batchProgressPercent = $("batch-progress-percent");
const batchBadge = $("batch-badge");

const scorecardEmptyState = $("scorecard-empty-state");
const scorecardContent = $("scorecard-content");
const metricCompliance = $("metric-compliance");
const metricTier = $("metric-tier");
const metricPenalty = $("metric-penalty");
const batchMatrixPills = $("batch-matrix-pills");

let selectedBatchFiles = [];

if (batchDropzone && batchFileInput) {
  batchDropzone.addEventListener("click", () => batchFileInput.click());

  batchDropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    batchDropzone.style.borderColor = "var(--cyan-glow, #38bdf8)";
  });

  batchDropzone.addEventListener("dragleave", () => {
    batchDropzone.style.borderColor = "#334155";
  });

  batchDropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    batchDropzone.style.borderColor = "#334155";
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleBatchFilesSelected(e.dataTransfer.files);
    }
  });

  batchFileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleBatchFilesSelected(e.target.files);
    }
  });
}

function handleBatchFilesSelected(files) {
  selectedBatchFiles = Array.from(files).filter((f) => f.type.startsWith("image/"));
  const labelEl = batchDropzone.querySelector("strong");
  if (labelEl) {
    labelEl.innerText = `${selectedBatchFiles.length} Assets Selected`;
  }
  if (batchBadge) {
    batchBadge.innerText = `${selectedBatchFiles.length} QUEUED`;
    batchBadge.style.color = "var(--cyan-glow, #38bdf8)";
    batchBadge.style.borderColor = "var(--cyan-glow, #38bdf8)";
  }
}

if (btnRunBatch) {
  btnRunBatch.addEventListener("click", async () => {
    const contributor = (batchContributorInput?.value || "").trim();
    if (!contributor) {
      showToast("Submitting Agency / Contributor is required for batch audits!", "error");
      batchContributorInput.focus();
      return;
    }
    if (selectedBatchFiles.length === 0) {
      showToast("Please select or drop image assets first.", "error");
      return;
    }

    btnRunBatch.disabled = true;
    btnRunBatch.style.opacity = "0.5";
    batchProgressContainer.style.display = "block";
    batchBadge.innerText = "PROCESSING";
    batchBadge.style.color = "var(--amber, #f59e0b)";
    batchBadge.style.borderColor = "var(--amber, #f59e0b)";

    const results = [];
    const total = selectedBatchFiles.length;

    for (let i = 0; i < total; i++) {
      const file = selectedBatchFiles[i];
      const pct = Math.round((i / total) * 100);
      batchProgressBar.style.width = `${pct}%`;
      batchProgressPercent.innerText = `${pct}%`;
      batchProgressStatus.innerText = `Ingesting: ${file.name}`;

      const formData = new FormData();
      formData.append("file", file);
      formData.append("contributor", contributor);

      try {
        const res = await fetch(`${API_BASE}/process-pipeline`, {
          method: "POST",
          body: formData,
        });
        if (res.ok) {
          const data = await res.json();
          results.push(data);
        } else {
          results.push({ status: `HTTP_${res.status}`, is_trusted: false });
        }
      } catch (err) {
        results.push({ status: "CONNECTION_ERROR", is_trusted: false });
      }
    }

    // Finalize Batch Process
    batchProgressBar.style.width = "100%";
    batchProgressPercent.innerText = "100%";
    batchProgressStatus.innerText = "Batch Ingestion Complete";
    batchBadge.innerText = "COMPLETED";
    batchBadge.style.color = "var(--emerald-hot, #10b981)";
    batchBadge.style.borderColor = "var(--emerald-hot, #10b981)";
    btnRunBatch.disabled = false;
    btnRunBatch.style.opacity = "1.0";

    renderBatchScorecard(results);
    loadHistory(true);
    showToast(`Batch execution completed for ${total} assets.`, "success");
  });
}

function renderBatchScorecard(results) {
  const total = results.length;
  if (total === 0) return;

  if (scorecardEmptyState) scorecardEmptyState.style.display = "none";
  if (scorecardContent) scorecardContent.style.display = "block";

  let verifiedCount = 0;
  const distribution = {};

  results.forEach((r) => {
    const st = r.status || "UNKNOWN";
    distribution[st] = (distribution[st] || 0) + 1;
    if (st === "VERIFIED") verifiedCount++;
  });

  const compliance = Math.round((verifiedCount / total) * 100);
  const penalty = Math.min(
    100,
    (distribution["PLAGIARISM ALERT"] || 0) * 30 +
      (distribution["IMAGE TAMPERED"] || 0) * 25 +
      (distribution["DATA POISONED"] || 0) * 35 +
      (distribution["MODEL COMPROMISED"] || 0) * 40 +
      (distribution["INFERENCE TAMPERED"] || 0) * 25 +
      (distribution["DUPLICATE ASSET"] || 0) * 10 +
      (distribution["NON-COMPLIANT ASSET"] || 0) * 5
  );

  if (metricCompliance) {
    metricCompliance.innerText = `${compliance}%`;
    metricCompliance.style.color =
      compliance > 75 ? "var(--emerald-hot, #10b981)" : compliance > 40 ? "var(--amber, #f59e0b)" : "var(--crimson-hot, #ef4444)";
  }

  let tier = "LOW / TRUSTED";
  let tierColor = "var(--emerald-hot, #10b981)";
  if (penalty >= 60) {
    tier = "CRITICAL";
    tierColor = "var(--crimson-hot, #ef4444)";
  } else if (penalty >= 30) {
    tier = "ELEVATED";
    tierColor = "#f97316";
  } else if (penalty > 0) {
    tier = "MODERATE";
    tierColor = "var(--amber, #f59e0b)";
  }

  if (metricTier) {
    metricTier.innerText = tier;
    metricTier.style.color = tierColor;
  }

  if (metricPenalty) {
    metricPenalty.innerText = penalty.toFixed(1);
  }

  if (batchMatrixPills) {
    batchMatrixPills.innerHTML = "";
    Object.entries(distribution).forEach(([status, count]) => {
      const pill = document.createElement("div");
      const isSafe = status === "VERIFIED";
      pill.style.cssText = `
        font-size: 11px;
        padding: 4px 10px;
        border-radius: 4px;
        background: ${isSafe ? "rgba(16,185,129,0.12)" : "rgba(239,68,68,0.12)"};
        color: ${isSafe ? "var(--emerald-hot, #10b981)" : "var(--crimson-hot, #ef4444)"};
        border: 1px solid ${isSafe ? "rgba(16,185,129,0.3)" : "rgba(239,68,68,0.3)"};
        font-weight: 600;
        letter-spacing: 0.3px;
      `;
      pill.innerText = `${status}: ${count}`;
      batchMatrixPills.appendChild(pill);
    });
  }

  icons();
}

/* ============================================================
   INIT
   ============================================================ */
document.addEventListener("DOMContentLoaded", () => {
  icons();
  updateRunState();
  loadHistory();
  tickClock();
  setInterval(tickClock, 1000);
});

// Fallback: guarantees icons render once all deferred CDN scripts load
window.addEventListener("load", () => {
  icons();
});