/**
 * Vunoh Global — Diaspora Assistant Frontend
 * Multi-page app: Dashboard, New Request (with entity form), Tracking, All Tasks
 * Enhanced with premium card layouts
 */

const API = 'http://127.0.0.1:8000/api';

let allTasks = [];
let pendingAIResult = null;

// ─────────────────────────────────────────────
// NAVIGATION
// ─────────────────────────────────────────────
function navigate(page) {
  document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const target = document.getElementById(`page-${page}`);
  if (target) { target.classList.remove('hidden'); target.classList.add('active'); }

  document.querySelectorAll('.snav-link').forEach(l => {
    l.classList.toggle('active', l.dataset.page === page);
  });
  document.querySelectorAll('.tnav-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.page === page);
  });

  closeSidebar();

  if (page === 'dashboard') loadDashboard();
  if (page === 'new') { loadRecentEnhanced(); resetNewRequest(); }
  if (page === 'requests') loadRequestsEnhanced();
}

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('sbOverlay').classList.toggle('open');
}
function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sbOverlay').classList.remove('open');
}

// ─────────────────────────────────────────────
// NOTIFICATIONS
// ─────────────────────────────────────────────
const notifications = [];

function toggleNotifications() {
  document.getElementById('notifPanel').classList.toggle('open');
  document.getElementById('notifOverlay').classList.toggle('open');
}

function pushNotification(title, body, type = 'info') {
  notifications.unshift({ title, body, type, time: new Date() });
  renderNotifications();
  ['notifBadge','notifBadgeD'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.style.display = 'block';
  });
}

function renderNotifications() {
  const list = document.getElementById('notifList');
  if (!notifications.length) { list.innerHTML = '<p class="notif-empty">No notifications yet</p>'; return; }
  list.innerHTML = notifications.slice(0, 10).map(n => `
    <div class="notif-item ${n.type}">
      <div class="notif-item-title">${n.title}</div>
      <div class="notif-item-body">${n.body}</div>
    </div>`).join('');
}

// ─────────────────────────────────────────────
// DASHBOARD
// ─────────────────────────────────────────────
async function loadDashboard() {
  const filter = document.getElementById('dashStatusFilter')?.value || '';
  try {
    const [statsRes, tasksRes] = await Promise.all([
      fetch(`${API}/tasks/stats/`),
      fetch(`${API}/tasks/`)
    ]);
    const stats = await statsRes.json();
    const tasksData = await tasksRes.json();
    allTasks = tasksData.tasks || [];

    const total = stats.total || 0;
    const completed = stats.by_status?.completed || 0;
    const eff = total > 0 ? ((completed / total) * 100).toFixed(1) : '98.4';
    animateNumber('effNum', parseFloat(eff), 1);
    animateNumber('totalNum', total);
    document.getElementById('effHint').textContent = `Optimized across ${total} active mandates`;
    document.getElementById('highRiskNum').textContent = stats.high_risk_count || 0;

    const pips = document.getElementById('miniPips');
    if (pips) {
      const colors = ['#f0a500','#60a5fa','#34d399','#a78bfa','#ff6b6b'];
      pips.innerHTML = ['F','L','O','S','?'].map((l,i) => `<div class="mini-pip" style="background:${colors[i]}22;color:${colors[i]};border-color:${colors[i]}44">${l}</div>`).join('');
    }

    const bc = document.getElementById('barChart');
    if (bc) {
      const pending = stats.by_status?.pending || 0;
      const inProg = stats.by_status?.in_progress || 0;
      const heights = [30, 45, 55, pending*3+10, inProg*4+15, completed*3+20, total*2+10];
      const max = Math.max(...heights, 1);
      bc.innerHTML = heights.map((h, i) => `<div class="bar-chart-bar${i===heights.length-1?' current':''}" style="height:${(h/max*100).toFixed(0)}%"></div>`).join('');
    }

    let filtered = allTasks;
    if (filter) filtered = allTasks.filter(t => t.status === filter);
    renderLedger(filtered);

  } catch (e) {
    document.getElementById('ledgerBody').innerHTML = `<tr><td colspan="6" class="tload" style="color:var(--red)">Failed to load. Is the backend running?</td></tr>`;
  }
}

function renderLedger(tasks) {
  const tbody = document.getElementById('ledgerBody');
  if (!tasks.length) {
    tbody.innerHTML = `<tr><td colspan="6"><div class="empty-state"><span class="material-symbols-outlined">inbox</span><p>No tasks found.</p></div></td></tr>`;
    return;
  }
  tbody.innerHTML = tasks.slice(0, 20).map(t => {
    const riskClass = t.risk_level;
    const intentLabel = fmtIntent(t.intent);
    return `<tr>
      <td>
        <div class="task-title-cell">
          <div class="kenyan-bar"></div>
          <div class="task-name">${intentLabel}</div>
          <div class="task-desc">${(t.original_request||'').slice(0,50)}…</div>
        </div>
      </td>
      <td>
        <select class="stat-sel" onchange="updateStatus('${t.task_code}',this.value)">
          <option value="pending" ${t.status==='pending'?'selected':''}>Pending</option>
          <option value="in_progress" ${t.status==='in_progress'?'selected':''}>In Progress</option>
          <option value="completed" ${t.status==='completed'?'selected':''}>Completed</option>
          <option value="cancelled" ${t.status==='cancelled'?'selected':''}>Cancelled</option>
        </select>
      </td>
      <td>
        <div class="risk-bar-wrap">
          <div class="risk-bar-track"><div class="risk-bar-fill ${riskClass}" style="width:${t.risk_score}%"></div></div>
          <span class="risk-num ${riskClass}">${t.risk_score}/100</span>
        </div>
      </td>
      <td><span class="team-tag t-${t.assigned_team}">${t.assigned_team}</span></td>
      <td><span class="task-id-cell" onclick="openModal('${t.task_code}')">${t.task_code}</span></td>
      <td class="text-right"><button class="view-btn" onclick="openModal('${t.task_code}')">View →</button></td>
    </tr>`;
  }).join('');
}

// ─────────────────────────────────────────────
// SUBMIT REQUEST
// ─────────────────────────────────────────────

function resetNewRequest() {
  document.getElementById('requestInput').value = '';
  document.getElementById('charCount').textContent = '0 / 2000';
  document.getElementById('entityForm').style.display = 'none';
  document.getElementById('aiLoader').style.display = 'none';
  document.getElementById('resultArea').style.display = 'none';
  document.getElementById('cmdBox').style.display = 'block';
  pendingAIResult = null;
}

document.addEventListener('DOMContentLoaded', () => {
  const ta = document.getElementById('requestInput');
  if (ta) {
    ta.addEventListener('input', () => {
      const n = ta.value.length;
      const cc = document.getElementById('charCount');
      cc.textContent = `${n} / 2000`;
      cc.style.color = n > 1800 ? 'var(--red)' : 'var(--text4)';
    });
  }
  navigate('dashboard');
});

async function submitRequest() {
  const msg = document.getElementById('requestInput').value.trim();
  if (!msg || msg.length < 5) { showToast('Please describe your request in more detail.','warning'); return; }

  const btn = document.getElementById('submitBtn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner-sm"></span>Analysing...';

  document.getElementById('aiLoader').style.display = 'flex';
  document.getElementById('entityForm').style.display = 'none';
  document.getElementById('resultArea').style.display = 'none';

  animateAISteps();

  try {
    const resp = await fetch(`${API}/tasks/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg })
    });

    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || 'Something went wrong');

    pendingAIResult = data;

    document.getElementById('aiLoader').style.display = 'none';
    clearAISteps();

    showEntityForm(data);
    loadRecentEnhanced();

  } catch (e) {
    document.getElementById('aiLoader').style.display = 'none';
    clearAISteps();
    document.getElementById('resultArea').style.display = 'block';
    document.getElementById('resultArea').innerHTML = `<div class="err-box">⚠️ ${e.message}</div>`;
    showToast('Request failed. Is the backend running?','error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = 'Dispatch Request <span class="material-symbols-outlined">send</span>';
  }
}

function showEntityForm(task) {
  pendingAIResult = task;
  const form = document.getElementById('entityForm');
  const grid = document.getElementById('efGrid');
  const e = task.entities || {};

  const fields = [
    { key: 'amount', label: 'Amount (KES)', type: 'number', val: e.amount },
    { key: 'recipient_name', label: 'Recipient Name', type: 'text', val: e.recipient_name },
    { key: 'recipient_phone', label: 'Recipient Phone', type: 'text', val: e.recipient_phone },
    { key: 'recipient_relationship', label: 'Relationship', type: 'text', val: e.recipient_relationship },
    { key: 'location', label: 'Location in Kenya', type: 'text', val: e.location },
    { key: 'service_type', label: 'Service Type', type: 'text', val: e.service_type },
    { key: 'document_type', label: 'Document Type', type: 'text', val: e.document_type },
    { key: 'scheduled_date', label: 'Scheduled Date', type: 'text', val: e.scheduled_date },
    { key: 'urgency_reason', label: 'Urgency Reason', type: 'text', val: e.urgency_reason },
    { key: 'additional_notes', label: 'Additional Notes', type: 'text', val: e.additional_notes },
  ].filter(f => {
    if (['amount','recipient_name','recipient_phone','location'].includes(f.key)) return true;
    if (task.intent === 'hire_service' && f.key === 'service_type') return true;
    if (task.intent === 'verify_document' && f.key === 'document_type') return true;
    return f.val !== null && f.val !== undefined && f.val !== '';
  });

  grid.innerHTML = fields.map(f => `
    <div class="ef-field">
      <label class="ef-label">${f.label}</label>
      <input class="ef-input" type="${f.type}" id="ef_${f.key}"
        value="${f.val !== null && f.val !== undefined ? f.val : ''}"
        placeholder="${f.label}"/>
    </div>
  `).join('');

  form.style.display = 'block';
  form.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

async function confirmAndCreate() {
  if (!pendingAIResult) return;

  const updatedEntities = { ...pendingAIResult.entities };
  const fields = ['amount','recipient_name','recipient_phone','recipient_relationship','location','service_type','document_type','scheduled_date','urgency_reason','additional_notes'];
  
  fields.forEach(key => {
    const el = document.getElementById(`ef_${key}`);
    if (el) {
      let val = el.value.trim() || null;
      if (key === 'amount' && val) val = parseInt(val) || null;
      updatedEntities[key] = val;
    }
  });

  const btn = document.getElementById('entityForm').querySelector('.confirm-btn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner-sm"></span>Saving...';

  try {
    const task = { ...pendingAIResult, entities: updatedEntities };
    
    document.getElementById('entityForm').style.display = 'none';
    document.getElementById('resultArea').style.display = 'block';
    document.getElementById('resultArea').innerHTML = renderResult(task);
    document.getElementById('resultArea').scrollIntoView({ behavior: 'smooth', block: 'start' });

    pushNotification(
      `Task ${task.task_code} Created`,
      `${fmtIntent(task.intent)} — Risk: ${task.risk_level.toUpperCase()} (${task.risk_score}/100)`,
      task.risk_level === 'high' ? 'high' : 'success'
    );
    showToast(`✅ Task ${task.task_code} created!`, 'success');

  } catch (e) {
    showToast('Error confirming task.', 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span class="material-symbols-outlined">check_circle</span>Confirm & Create Task';
  }
}

// ─────────────────────────────────────────────
// ENHANCED RECENT ANCHORS
// ─────────────────────────────────────────────
async function loadRecentEnhanced() {
  const grid = document.getElementById('recentGrid');
  if (!grid) return;
  try {
    const r = await fetch(`${API}/tasks/`);
    const d = await r.json();
    const tasks = (d.tasks || []).slice(0, 6);
    if (!tasks.length) { grid.innerHTML = `<div class="empty-state"><span class="material-symbols-outlined">inbox</span><p>No tasks yet. Submit your first request above!</p></div>`; return; }
    grid.innerHTML = tasks.map(t => renderPremiumAnchorCard(t)).join('');
  } catch (e) {
    grid.innerHTML = '<p style="color:var(--text3);font-size:13px">Could not load recent tasks.</p>';
  }
}

function renderPremiumAnchorCard(t) {
  const riskClass = t.risk_level;
  return `<div class="anchor-card-premium ${riskClass}-risk" onclick="openModal('${t.task_code}')">
    <div class="ac-premium-header">
      <span class="ac-premium-code">${t.task_code}</span>
      <span class="ac-premium-date">${fmtDate(t.created_at)}</span>
    </div>
    <div class="ac-premium-title">${fmtIntent(t.intent)}</div>
    <div class="ac-premium-desc">${(t.original_request || '').slice(0, 100)}${(t.original_request || '').length > 100 ? '...' : ''}</div>
    <div class="ac-premium-footer">
      <div class="ac-premium-risk">
        <span class="risk-indicator ${riskClass}"></span>
        <span class="risk-num ${riskClass}">${t.risk_score}/100</span>
      </div>
      <span class="status-tag s-${t.status}">${fmtStatus(t.status)}</span>
    </div>
  </div>`;
}

// ─────────────────────────────────────────────
// ENHANCED ALL REQUESTS
// ─────────────────────────────────────────────
async function loadRequestsEnhanced() {
  const grid = document.getElementById('reqGrid');
  grid.innerHTML = '<p class="recent-loading">Loading requests...</p>';
  try {
    const r = await fetch(`${API}/tasks/`);
    const d = await r.json();
    allTasks = d.tasks || [];
    applyFiltersEnhanced();
  } catch (e) {
    grid.innerHTML = `<div class="err-box">⚠️ Failed to load tasks.</div>`;
  }
}

function applyFiltersEnhanced() {
  const status = document.getElementById('filterStatus')?.value || '';
  const intent = document.getElementById('filterIntent')?.value || '';
  const risk   = document.getElementById('filterRisk')?.value || '';
  const filtered = allTasks.filter(t => {
    if (status && t.status !== status) return false;
    if (intent && t.intent !== intent) return false;
    if (risk   && t.risk_level !== risk) return false;
    return true;
  });
  renderReqGridEnhanced(filtered);
}

function renderReqGridEnhanced(tasks) {
  const grid = document.getElementById('reqGrid');
  if (!tasks.length) {
    grid.innerHTML = `<div class="empty-state"><span class="material-symbols-outlined">inbox</span><p>No tasks match your filters.</p></div>`;
    return;
  }
  grid.innerHTML = tasks.map(t => renderPremiumTaskCard(t)).join('');
}

function renderPremiumTaskCard(t) {
  const riskClass = t.risk_level;
  const statusClass = t.status;
  const teamClass = t.assigned_team;
  return `<div class="task-card-premium" onclick="openModal('${t.task_code}')">
    <div class="task-card-header">
      <span class="task-card-code">${t.task_code}</span>
      <span class="task-card-status s-${statusClass}">${fmtStatus(statusClass)}</span>
    </div>
    <div class="task-card-body">
      <div class="task-card-intent">${fmtIntent(t.intent)}</div>
      <div class="task-card-request">${(t.original_request || '').slice(0, 120)}${(t.original_request || '').length > 120 ? '...' : ''}</div>
      <div class="task-card-meta">
        <span class="task-card-team t-${teamClass}">${t.assigned_team}</span>
        <span class="task-card-risk-score ${riskClass}">Risk: ${t.risk_score}/100</span>
      </div>
    </div>
  </div>`;
}

// ─────────────────────────────────────────────
// TRACKING PAGE
// ─────────────────────────────────────────────
async function lookupTask() {
  const code = document.getElementById('trackInput').value.trim().toUpperCase();
  if (!code.startsWith('VNH-') || code.length < 9) {
    showToast('Enter a valid task code (VNH-XXXXX)','warning'); return;
  }

  const area = document.getElementById('trackResult');
  area.innerHTML = `<div style="text-align:center;padding:48px"><div class="spinner-md" style="margin:0 auto"></div></div>`;

  try {
    const r = await fetch(`${API}/tasks/${code}/`);
    if (!r.ok) throw new Error(`No task found: ${code}`);
    const task = await r.json();
    area.innerHTML = renderTimeline(task);
  } catch (e) {
    area.innerHTML = `<div class="err-box">⚠️ ${e.message}</div>`;
  }
}

function renderTimeline(task) {
  const e = task.entities || {};
  const steps = task.steps || [];
  const currentStep = steps.findIndex(s => !s.is_complete);
  const teamInitial = (task.assigned_team||'S')[0];

  const stepperHTML = steps.map((s, i) => {
    let cls = 'upcoming', dotContent = '';
    if (s.is_complete) { cls = 'done'; dotContent = '<span class="material-symbols-outlined">check</span>'; }
    else if (i === currentStep) {
      cls = 'active';
      dotContent = '<div class="active-pulse"></div><div style="width:6px;height:6px;border-radius:50%;background:var(--gold)"></div>';
    }
    return `<div class="stepper-item ${cls}">
      <div class="stepper-dot ${cls}">${dotContent}</div>
      <div class="stepper-title ${cls}">${s.title}</div>
      <div class="stepper-desc">${s.description}</div>
      ${s.is_complete ? `<div class="stepper-time">${fmtDate(task.updated_at)}</div>` : ''}
      ${i === currentStep ? `<div class="agent-card">
        <div class="agent-avatar">${teamInitial}</div>
        <div><div class="agent-name">${task.assigned_team} Team</div><div class="agent-meta">Assigned &amp; in progress</div></div>
        <div class="agent-ping" style="margin-left:auto"><div class="agent-ping-label">Status</div><div class="agent-ping-loc">${fmtStatus(task.status)}</div></div>
      </div>` : ''}
    </div>`;
  }).join('');

  const entityRows = Object.entries(e)
    .filter(([,v]) => v !== null && v !== undefined && v !== '' && v !== false)
    .slice(0, 4)
    .map(([k,v]) => `<div class="tsc-row"><span class="tsc-key">${fmtKey(k)}</span><span class="tsc-val">${fmtVal(k,v)}</span></div>`)
    .join('');

  const riskColor = { low:'var(--green)', medium:'var(--amber)', high:'var(--red)' }[task.risk_level];

  return `
    <div class="timeline">
      <div class="timeline-left">
        <div class="timeline-hdr">
          <div class="timeline-title">${task.task_code} Progress</div>
          <span class="status-tag s-${task.status}">${fmtStatus(task.status)}</span>
        </div>
        <div class="stepper">${stepperHTML}</div>
      </div>
      <div class="timeline-right">
        <div class="task-summary-card">
          <p class="tsc-lbl">Task Summary</p>
          ${entityRows}
          <div class="tsc-row">
            <span class="tsc-key">Risk Score</span>
            <span class="tsc-val" style="color:${riskColor}">${task.risk_score}/100 — ${task.risk_level.toUpperCase()}</span>
          </div>
          <div class="tsc-row">
            <span class="tsc-key">Team</span>
            <span class="tsc-val"><span class="team-tag t-${task.assigned_team}">${task.assigned_team}</span></span>
          </div>
        </div>
        <div class="map-card">
          <div class="map-placeholder">
            <div class="map-grid"></div>
            <span class="map-pin">📍</span>
            <span>${e.location || 'Kenya'}</span>
            <div class="live-tag">Live: ${task.assigned_team} Team Active</div>
          </div>
          <div class="map-body">
            ${task.assigned_team} team is tracking this mandate. Last update: ${fmtDate(task.updated_at)}.
          </div>
        </div>
        <div style="margin-top:4px">
          <p class="pane-lbl" style="margin-bottom:10px">Update Status</p>
          <div style="display:flex;gap:8px;flex-wrap:wrap">
            ${['pending','in_progress','completed','cancelled'].map(s => `
              <button onclick="updateStatus('${task.task_code}','${s}')" 
                class="ctrl-btn" style="${task.status===s?'border-color:var(--gold);color:var(--gold)':''}">
                ${fmtStatus(s)}
              </button>`).join('')}
          </div>
        </div>
      </div>
    </div>`;
}

// ─────────────────────────────────────────────
// STATUS UPDATE
// ─────────────────────────────────────────────
async function updateStatus(code, newStatus) {
  try {
    const r = await fetch(`${API}/tasks/${code}/status/`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    });
    if (!r.ok) throw new Error('Update failed');
    const t = allTasks.find(x => x.task_code === code);
    if (t) t.status = newStatus;
    showToast(`${code} → ${fmtStatus(newStatus)}`, 'success');
    const trackInput = document.getElementById('trackInput');
    if (trackInput && trackInput.value.toUpperCase() === code) lookupTask();
    loadDashboard();
    loadRecentEnhanced();
    loadRequestsEnhanced();
  } catch (e) {
    showToast('Failed to update status.', 'error');
  }
}

// ─────────────────────────────────────────────
// MODAL
// ─────────────────────────────────────────────
async function openModal(code) {
  document.getElementById('modalBg').classList.add('open');
  document.getElementById('modalContent').innerHTML = `<div class="modal-loading"><div class="spinner-md"></div></div>`;
  try {
    const r = await fetch(`${API}/tasks/${code}/`);
    if (!r.ok) throw new Error('Not found');
    const task = await r.json();
    document.getElementById('modalContent').innerHTML = `<div style="padding:8px">${renderResult(task)}</div>`;
  } catch (e) {
    document.getElementById('modalContent').innerHTML = `<div class="err-box" style="margin:24px">⚠️ Could not load task.</div>`;
  }
}

function closeModal(e) {
  if (!e || e.target === document.getElementById('modalBg') || e.target?.classList.contains('modal-x')) {
    document.getElementById('modalBg').classList.remove('open');
  }
}
document.addEventListener('keydown', e => { if (e.key==='Escape') closeModal({target:document.getElementById('modalBg')}); });

// ─────────────────────────────────────────────
// TABS
// ─────────────────────────────────────────────
function switchTab(btn, panelId) {
  const parent = btn.closest('.result-card') || btn.closest('.modal');
  if (!parent) return;
  parent.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  parent.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
  btn.classList.add('active');
  const panel = document.getElementById(panelId);
  if (panel) panel.classList.add('active');
}

// ─────────────────────────────────────────────
// RENDER RESULT CARD
// ─────────────────────────────────────────────
function renderResult(task) {
  const e = task.entities || {};
  const rColor = { low:'var(--green)', medium:'var(--amber)', high:'var(--red)' }[task.risk_level] || 'var(--text2)';

  const entityItems = Object.entries(e)
    .filter(([,v]) => v !== null && v !== undefined && v !== '' && v !== false)
    .map(([k,v]) => `<div class="entity-chip"><div class="e-key">${fmtKey(k)}</div><div class="e-val">${fmtVal(k,v)}</div></div>`)
    .join('');

  const riskReasons = (task.risk_reasons||[]).map(r=>`<div class="risk-item">• ${r}</div>`).join('') || '<div class="risk-item">No significant risk factors.</div>';

  const steps = (task.steps||[]).map(s=>`
    <div class="step-row">
      <div class="step-num">${s.step_number}</div>
      <div><div class="step-t">${s.title}</div><div class="step-d">${s.description}</div></div>
    </div>`).join('');

  const msgs = {};
  (task.messages||[]).forEach(m => msgs[m.channel] = m);

  const tabId = `res_${task.task_code.replace('-','_')}`;

  return `
    <div class="result-card">
      <div class="result-top">
        <div style="flex:1">
          <div class="result-code">${task.task_code}</div>
          <div class="result-badges">
            <span class="badge b-intent">${fmtIntent(task.intent)}</span>
            <span class="badge b-${task.risk_level}">${task.risk_level.toUpperCase()} RISK</span>
            <span class="badge b-${task.status}">${fmtStatus(task.status)}</span>
          </div>
          <div class="result-meta">
            <span>👥 ${task.assigned_team} Team</span>
            <span>🕐 ${fmtDate(task.created_at)}</span>
          </div>
        </div>
        <div class="score-pill" style="border-color:${rColor}33">
          <div class="score-num" style="color:${rColor}">${task.risk_score}</div>
          <div class="score-lbl">Risk Score</div>
        </div>
      </div>
      <div class="tabs">
        <button class="tab active" onclick="switchTab(this,'${tabId}_overview')">Overview</button>
        <button class="tab" onclick="switchTab(this,'${tabId}_steps')">Steps (${(task.steps||[]).length})</button>
        <button class="tab" onclick="switchTab(this,'${tabId}_messages')">Messages</button>
        <button class="tab" onclick="switchTab(this,'${tabId}_risk')">Risk Analysis</button>
      </div>
      <div class="tab-pane active" id="${tabId}_overview">
        <p class="pane-lbl">Original Request</p>
        <div class="summary-strip" style="margin-bottom:16px">${task.original_request}</div>
        <p class="pane-lbl">Extracted Details</p>
        <div class="entities-grid">${entityItems||'<p style="color:var(--text3)">No entities extracted.</p>'}</div>
      </div>
      <div class="tab-pane" id="${tabId}_steps">
        <p class="pane-lbl">Fulfilment Steps</p>
        <div class="steps-list">${steps||'<p style="color:var(--text3)">No steps generated.</p>'}</div>
      </div>
      <div class="tab-pane" id="${tabId}_messages">
        <p class="pane-lbl">Confirmation Messages</p>
        <div class="msgs-list">
          ${msgs.whatsapp ? renderMsg('whatsapp','💬 WhatsApp',msgs.whatsapp) : ''}
          ${msgs.email    ? renderMsg('email','📧 Email',msgs.email) : ''}
          ${msgs.sms      ? renderMsg('sms','📱 SMS',msgs.sms) : ''}
        </div>
      </div>
      <div class="tab-pane" id="${tabId}_risk">
        <p class="pane-lbl">Risk Score: ${task.risk_score}/100 — ${task.risk_level.toUpperCase()}</p>
        <div class="risk-list">${riskReasons}</div>
      </div>
    </div>`;
}

function renderMsg(channel, label, m) {
  return `<div class="msg-card">
    <div class="msg-top">
      <span class="msg-channel mc-${channel}">${label}</span>
      <button class="copy-btn" onclick="copyText(this,\`${esc(m.body)}\`)">Copy</button>
    </div>
    ${m.subject ? `<div class="msg-subject">Subject: ${m.subject}</div>` : ''}
    <div class="msg-body">${m.body}</div>
  </div>`;
}

// ─────────────────────────────────────────────
// EXAMPLE CHIPS
// ─────────────────────────────────────────────
const EXAMPLES = {
  'Property Verification': 'Please verify my land title deed for the plot I own in Karen, Nairobi before I finalize a sale.',
  'Express Remittance': 'I need to send KES 25,000 to my mother Grace Wanjiku in Kisumu urgently. Her M-Pesa is 0712345678.',
  'Land Surveying': 'Can you arrange a land survey for my 2-acre plot in Ruiru? I need the boundaries mapped.',
  'Legal Consult': 'I need a lawyer to review a property sale agreement for my house in Westlands.',
  'Airport Transfer': "I'm arriving at JKIA on Friday at 8PM on KQ101. I need a pickup to Kilimani.",
};

function useExample(btn) {
  const text = EXAMPLES[btn.textContent.trim()] || btn.textContent.trim();
  document.getElementById('requestInput').value = text;
  document.getElementById('requestInput').dispatchEvent(new Event('input'));
  document.getElementById('requestInput').focus();
}

// ─────────────────────────────────────────────
// AI LOADING ANIMATION
// ─────────────────────────────────────────────
let aiTimers = [];
function animateAISteps() {
  ['ais1','ais2','ais3','ais4'].forEach((id, i) => {
    aiTimers.push(setTimeout(() => {
      if (i > 0) {
        const prev = document.getElementById(['ais1','ais2','ais3','ais4'][i-1]);
        if (prev) { prev.classList.remove('active'); prev.classList.add('done'); }
      }
      const el = document.getElementById(id);
      if (el) el.classList.add('active');
    }, i * 800));
  });
}
function clearAISteps() {
  aiTimers.forEach(clearTimeout); aiTimers = [];
  ['ais1','ais2','ais3','ais4'].forEach(id => {
    const el = document.getElementById(id);
    if (el) { el.classList.remove('active','done'); }
  });
}

// ─────────────────────────────────────────────
// GLOBAL SEARCH
// ─────────────────────────────────────────────
function doGlobalSearch(val) {
  if (!val || val.length < 3) return;
  const q = val.toLowerCase();
  const match = allTasks.find(t =>
    t.task_code.toLowerCase().includes(q) ||
    (t.original_request||'').toLowerCase().includes(q)
  );
  if (match) {
    navigate('tracking');
    document.getElementById('trackInput').value = match.task_code;
    lookupTask();
  }
}

// ─────────────────────────────────────────────
// NUMBER ANIMATION
// ─────────────────────────────────────────────
function animateNumber(id, target, decimals = 0) {
  const el = document.getElementById(id);
  if (!el) return;
  const start = 0, duration = 1000, startTime = performance.now();
  function update(now) {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = (start + (target - start) * eased).toFixed(decimals);
    if (progress < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

// ─────────────────────────────────────────────
// COPY
// ─────────────────────────────────────────────
async function copyText(btn, text) {
  try {
    await navigator.clipboard.writeText(text);
    btn.textContent = 'Copied!';
    setTimeout(() => btn.textContent = 'Copy', 2000);
    showToast('Copied to clipboard','success');
  } catch { showToast('Could not copy','error'); }
}

// ─────────────────────────────────────────────
// TOAST
// ─────────────────────────────────────────────
function showToast(msg, type = 'info') {
  const stack = document.getElementById('toastStack');
  const icons = { success:'check_circle', error:'error', warning:'warning', info:'info' };
  const div = document.createElement('div');
  div.className = `toast ${type}`;
  div.innerHTML = `<span class="material-symbols-outlined toast-icon">${icons[type]||'info'}</span><span>${msg}</span><button class="toast-close" onclick="this.parentElement.remove()"><span class="material-symbols-outlined" style="font-size:14px">close</span></button>`;
  stack.appendChild(div);
  requestAnimationFrame(() => requestAnimationFrame(() => div.classList.add('show')));
  setTimeout(() => { div.classList.remove('show'); setTimeout(() => div.remove(), 400); }, 4000);
}

// ─────────────────────────────────────────────
// FORMATTERS
// ─────────────────────────────────────────────
function fmtIntent(i) {
  return { send_money:'Send Money', hire_service:'Hire Service', verify_document:'Verify Document', get_airport_transfer:'Airport Transfer', check_status:'Check Status', unknown:'Unknown' }[i] || i;
}
function fmtStatus(s) {
  return { pending:'Pending', in_progress:'In Progress', completed:'Completed', cancelled:'Cancelled' }[s] || s;
}
function fmtKey(k) {
  return k.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase());
}
function fmtVal(k, v) {
  if (typeof v === 'boolean') return v ? '✓ Yes' : '✗ No';
  if (k === 'amount' && typeof v === 'number') return `KES ${v.toLocaleString()}`;
  return String(v);
}
function fmtDate(s) {
  if (!s) return '—';
  return new Date(s).toLocaleString('en-KE', { day:'numeric', month:'short', year:'numeric', hour:'2-digit', minute:'2-digit' });
}
function esc(s) {
  return (s||'').replace(/`/g,'\\`').replace(/\$/g,'\\$');
}