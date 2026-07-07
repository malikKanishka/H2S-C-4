'use strict';

// ---- Auth ----
const TOKEN = window.AUTH_TOKEN;
if (!TOKEN) {
  window.location.href = '/';
}

// ---- Live clock ----
function updateClock() {
  const el = document.getElementById('nav-clock');
  if (!el) return;
  const now = new Date();
  el.textContent = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}
updateClock();
setInterval(updateClock, 1000);

// ---- Toast ----
let toastTimer;
function showToast(message, type = 'success') {
  const t = document.getElementById('toast');
  t.textContent = message;
  t.className = `show toast-${type}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { t.className = ''; }, 3500);
}

// ---- Fetch wrapper ----
async function apiFetch(path, opts = {}) {
  const res = await fetch(path, {
    ...opts,
    headers: {
      'Authorization': 'Bearer ' + TOKEN,
      'Content-Type': 'application/json',
      ...(opts.headers || {})
    }
  });
  if (res.status === 401) {
    window.location.href = '/';
    throw new Error('Unauthorized');
  }
  return res;
}

// ---- Zone helpers ----
function densityClass(ratio) {
  if (ratio > 0.8) return 'danger';
  if (ratio > 0.5) return 'warning';
  return 'safe';
}
function badgeClass(cls) {
  return { safe: 'badge-safe', warning: 'badge-warning', danger: 'badge-danger' }[cls];
}
function badgeLabel(cls) {
  return { safe: 'OK', warning: 'Busy', danger: 'Critical' }[cls];
}

// ---- Render zones ----
function renderZones(zones) {
  const el = document.getElementById('zones-list');
  if (!zones || !zones.length) {
    el.innerHTML = '<p class="no-alerts">No zone data available.</p>';
    return;
  }

  // Populate broadcast zone select
  const sel = document.getElementById('alert-zone');
  if (sel) {
    const cur = sel.value;
    sel.innerHTML = zones.map(z =>
      `<option value="${z.id}" ${z.id === cur ? 'selected' : ''}>${z.name}</option>`
    ).join('');
  }

  el.innerHTML = zones.map(z => {
    const ratio = z.currentCount / z.capacity;
    const pct   = Math.min(Math.round(ratio * 100), 100);
    const cls   = densityClass(ratio);
    return `
      <div class="zone-item">
        <div class="zone-meta">
          <span class="zone-name">${z.name}</span>
          <div style="display:flex;align-items:center;gap:8px">
            <span class="zone-count">${z.currentCount.toLocaleString()} / ${z.capacity.toLocaleString()}</span>
            <span class="zone-status-badge ${badgeClass(cls)}">${badgeLabel(cls)}</span>
          </div>
        </div>
        <div class="zone-bar-track">
          <div class="zone-bar-fill ${cls}" style="width:${pct}%"></div>
        </div>
      </div>`;
  }).join('');
}

// ---- Render alerts ----
function renderAlerts(alerts) {
  const el = document.getElementById('alerts-list');
  if (!alerts || !alerts.length) {
    el.innerHTML = '<p class="no-alerts">No recent alerts.</p>';
    return;
  }
  el.innerHTML = alerts.map(a => `
    <div class="alert-item">
      <div class="alert-dot"></div>
      <div class="alert-body">
        <div class="alert-zone">${a.zoneId}</div>
        <div class="alert-message">${a.message}</div>
        <div class="alert-time">${a.createdAt ? new Date(a.createdAt).toLocaleString() : ''}</div>
      </div>
    </div>`).join('');
}

// ---- Render insights ----
function renderInsights(insights) {
  const el = document.getElementById('insights-list');
  if (!insights || !insights.length) {
    el.innerHTML = '<li>No insights available.</li>';
    return;
  }
  el.innerHTML = insights.map(i => `<li>${i}</li>`).join('');
}

// ---- Render stat cards ----
function renderStats(data) {
  const zones = data.zones || [];
  const alerts = data.alerts || [];
  const sus = data.sustainability_totals || {};

  const totalFans = zones.reduce((s, z) => s + (z.currentCount || 0), 0);
  const zonesAtRisk = zones.filter(z => z.currentCount / z.capacity > 0.8).length;

  document.getElementById('stat-fans').textContent    = totalFans.toLocaleString();
  document.getElementById('stat-risk').textContent    = zonesAtRisk;
  document.getElementById('stat-alerts').textContent  = alerts.length;
  document.getElementById('stat-points').textContent  = (sus.total_points || 0).toLocaleString();
}

// ---- Skeleton loaders ----
function showSkeletons() {
  document.getElementById('zones-list').innerHTML = `
    <div class="skeleton" style="height:48px"></div>
    <div class="skeleton" style="height:48px"></div>
    <div class="skeleton" style="height:48px"></div>`;
  document.getElementById('alerts-list').innerHTML = `
    <div class="skeleton" style="height:54px"></div>
    <div class="skeleton" style="height:54px"></div>`;
  document.getElementById('insights-list').innerHTML = `
    <li><div class="skeleton" style="width:80%"></div></li>
    <li><div class="skeleton" style="width:65%"></div></li>
    <li><div class="skeleton" style="width:72%"></div></li>`;
}

// ---- Fetch summary ----
let firstLoad = true;
async function fetchSummary(showLoader = false) {
  if (showLoader || firstLoad) showSkeletons();
  try {
    const res = await apiFetch('/api/dashboard/summary');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    renderStats(data);
    renderZones(data.zones);
    renderAlerts(data.alerts);
    renderInsights(data.insights);
    document.getElementById('last-updated').textContent =
      'Updated ' + new Date().toLocaleTimeString();
    firstLoad = false;
  } catch (err) {
    if (err.message !== 'Unauthorized') {
      showToast('Failed to load dashboard data', 'error');
      console.error(err);
    }
  }
}

// ---- Refresh button ----
document.getElementById('btn-refresh')?.addEventListener('click', async () => {
  const btn = document.getElementById('btn-refresh');
  btn.classList.add('spinning');
  btn.disabled = true;
  await fetchSummary(true);
  btn.classList.remove('spinning');
  btn.disabled = false;
});

// ---- Broadcast alert form ----
document.getElementById('broadcast-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const zoneId  = document.getElementById('alert-zone').value;
  const message = document.getElementById('alert-message').value.trim();
  const fb      = document.getElementById('broadcast-feedback');
  const btn     = document.getElementById('btn-broadcast');

  if (!message) { showToast('Please enter an alert message', 'error'); return; }

  btn.disabled = true;
  const feedback = document.getElementById('broadcast-feedback');

  if (!zoneId || !message) {
    feedback.textContent = 'Please select a zone and enter a message.';
    feedback.className = 'broadcast-feedback error';
    feedback.style.display = 'block';
    return;
  }

  const btn = document.getElementById('btn-broadcast');
  btn.disabled = true;
  btn.style.opacity = '0.7';

  try {
    const res = await fetch('/api/crowd/alert', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + TOKEN
      },
      body: JSON.stringify({ 
        zone_id: zoneId, 
        message: message,
        csrf_token: CSRF_TOKEN // Include CSRF Token
      })
    });

    const data = await res.json();
    if (res.ok) {
      feedback.textContent = 'Alert broadcasted successfully.';
      feedback.className = 'broadcast-feedback success';
      document.getElementById('alert-message').value = '';
      fetchDashboard(); // force refresh
    } else {
      feedback.textContent = data.message || 'Failed to broadcast alert.';
      feedback.className = 'broadcast-feedback error';
    }
  } catch (err) {
    feedback.textContent = 'Network error. Please try again.';
    feedback.className = 'broadcast-feedback error';
  } finally {
    feedback.style.display = 'block';
    btn.disabled = false;
    btn.style.opacity = '1';
    setTimeout(() => { feedback.style.display = 'none'; }, 4000);
  }
});

// Logout
document.getElementById('btn-logout')?.addEventListener('click', () => {
});

// ---- Init ----
fetchSummary(true);
setInterval(() => fetchSummary(), 30000);
