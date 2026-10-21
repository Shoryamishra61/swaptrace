/**
 * SwapTrace Ops Console — Frontend Logic
 * Industrial Battery Telemetry & Diagnostics
 */

(function () {
  'use strict';

  // State Management
  const state = {
    currentView: 'fleet',
    activeFilter: 'ALL',
    searchQuery: '',
    selectedAlertId: null,
    currentScenario: 'dock_fault',
    currentGraphCase: 'dock_isolation',
    acknowledgedAlerts: new Set(),
    resolvedAlerts: new Set()
  };

  const data = window.SWAPTRACE_DATA || {
    alerts: [],
    evalReport: {},
    abstentions: [],
    curves: {},
    stations: [],
    crossingExamples: {}
  };

  // View Switching
  window.switchView = function (viewName) {
    state.currentView = viewName;

    // Update Tab Buttons
    document.querySelectorAll('.nav-tab-btn').forEach(btn => {
      const isActive = btn.getAttribute('aria-controls') === `view-${viewName}`;
      btn.classList.toggle('active', isActive);
      btn.setAttribute('aria-selected', isActive ? 'true' : 'false');
    });

    // Update Sections
    document.querySelectorAll('.view-section').forEach(sec => {
      sec.classList.toggle('active', sec.id === `view-${viewName}`);
    });

    if (viewName === 'counterfactual') {
      renderCurves(state.currentScenario);
    } else if (viewName === 'graph') {
      renderBipartiteGraph(state.currentGraphCase);
    }
  };

  // Station Grid
  function renderStations() {
    const grid = document.getElementById('station-grid');
    if (!grid) return;

    grid.innerHTML = data.stations.map(st => `
      <button type="button" class="station-card ${st.status === 'ATTENTION_REQUIRED' ? 'active' : ''}" onclick="filterByStation('${st.id}')" aria-label="Station ${st.id} status">
        <div class="station-head">
          <span class="station-id">${st.id} · ${st.name}</span>
          <span class="badge ${st.status === 'NOMINAL' ? 'badge-pass' : 'severity-pill severity-MEDIUM'}">${st.status}</span>
        </div>
        <div class="station-telemetry">
          <span>Docks: ${st.docks} Online</span>
          <span>Ambient: ${st.ambient_c}°C</span>
          <span>Grid: ${st.grid_v}V</span>
        </div>
      </button>
    `).join('');
  }

  // Filter Alerts
  window.filterAlerts = function (owner, buttonEl) {
    state.activeFilter = owner;
    if (buttonEl) {
      document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
      buttonEl.classList.add('active');
    }
    renderIncidentList();
  };

  window.handleSearch = function (query) {
    state.searchQuery = (query || '').trim().toLowerCase();
    renderIncidentList();
  };

  window.filterByStation = function (stationId) {
    const searchBox = document.getElementById('search-box');
    if (searchBox) {
      searchBox.value = stationId;
      handleSearch(stationId);
    }
  };

  // Render Incident List
  function renderIncidentList() {
    const listEl = document.getElementById('incident-list');
    const countLabel = document.getElementById('filter-count-label');
    if (!listEl) return;

    let items = [];

    if (state.activeFilter === 'ABSTAIN') {
      // Display abstained sessions
      items = data.abstentions.map((ab, idx) => ({
        isAbstention: true,
        id: `abstain-${idx}`,
        owner_category: 'ABSTAIN',
        severity: 'LOW',
        entity_id: ab.session_id || `SES-ABSTAIN-${idx + 1}`,
        observed_value: 0.0,
        expected_value: 0.0,
        observed_unit: '',
        residual_normalized: null,
        explanation: ab.explanation || 'Insufficient pack-dock crossing to confirm fault owner.',
        occurrence_count: 1,
        recommended_actions: ['Collect independent dock observation at next swap', 'Do not dispatch technician'],
        evidence: []
      }));
    } else {
      items = data.alerts.map(al => ({ ...al, isAbstention: false }));
    }

    // Apply Filter
    if (state.activeFilter !== 'ALL' && state.activeFilter !== 'ABSTAIN') {
      items = items.filter(a => a.owner_category === state.activeFilter);
    }

    // Apply Search
    if (state.searchQuery) {
      items = items.filter(a =>
        a.entity_id.toLowerCase().includes(state.searchQuery) ||
        (a.episode_key && a.episode_key.toLowerCase().includes(state.searchQuery)) ||
        (a.explanation && a.explanation.toLowerCase().includes(state.searchQuery))
      );
    }

    if (countLabel) {
      countLabel.textContent = `${items.length} Incidents`;
    }

    if (items.length === 0) {
      listEl.innerHTML = `
        <div style="padding: var(--space-xl); text-align: center; color: var(--text-muted);">
          <p><strong>No matching incidents</strong></p>
          <p style="font-size: 11px; margin-top: 4px;">Active filter: ${state.activeFilter}</p>
        </div>
      `;
      return;
    }

    // Ensure selected alert exists
    if (!state.selectedAlertId || !items.some(i => i.id === state.selectedAlertId || i.alert_id === state.selectedAlertId)) {
      state.selectedAlertId = items[0].alert_id || items[0].id;
    }

    listEl.innerHTML = items.map(item => {
      const itemId = item.alert_id || item.id;
      const isSelected = itemId === state.selectedAlertId;
      const isResolved = state.resolvedAlerts.has(itemId);
      const isAck = state.acknowledgedAlerts.has(itemId);

      return `
        <button type="button" class="incident-card ${isSelected ? 'selected' : ''}" 
             onclick="selectIncident('${itemId}')"
             role="option"
             aria-selected="${isSelected ? 'true' : 'false'}">
          <div class="incident-card-header">
            <span class="owner-badge owner-${item.owner_category}">${item.owner_category}</span>
            <span class="severity-pill severity-${item.severity}">${item.severity}</span>
          </div>
          <div style="display: flex; justify-content: space-between; align-items: baseline;">
            <span class="incident-entity">${item.entity_id}</span>
            ${isResolved ? '<span class="badge badge-pass">RESOLVED</span>' : isAck ? '<span class="badge" style="color:var(--color-dock);border-color:var(--color-dock-border)">ACKNOWLEDGED</span>' : ''}
          </div>
          <p class="incident-summary">${escapeHtml(item.explanation || '')}</p>
          <div class="incident-meta">
            <span>Occurrences: <strong>${item.occurrence_count}</strong></span>
            ${item.residual_normalized ? `<span>Residual: <strong>+${item.residual_normalized.toFixed(1)}σ</strong></span>` : '<span>Status: <strong>ABSTAINED</strong></span>'}
          </div>
        </button>
      `;
    }).join('');

    renderDetail(state.selectedAlertId);
  }

  // Select Incident
  window.selectIncident = function (id) {
    state.selectedAlertId = id;
    document.querySelectorAll('.incident-card').forEach(c => c.classList.remove('selected'));
    renderIncidentList();
  };

  // Render Detail Drilldown
  function renderDetail(id) {
    const detailEl = document.getElementById('detail-container');
    const headerTitle = document.getElementById('detail-header-title');
    const headerBadge = document.getElementById('detail-badge-owner');
    if (!detailEl) return;

    let alert = data.alerts.find(a => a.alert_id === id);
    let isAbstain = false;

    if (!alert) {
      alert = data.abstentions.find((a, idx) => `abstain-${idx}` === id);
      if (alert) {
        isAbstain = true;
        alert = {
          alert_id: id,
          entity_id: alert.session_id,
          owner_category: 'ABSTAIN',
          severity: 'LOW',
          observed_value: 11.2,
          expected_value: 15.0,
          observed_unit: 'A',
          residual_normalized: 2.1,
          explanation: alert.explanation,
          occurrence_count: 1,
          recommended_actions: [
            'Refrain from dispatching dock technician',
            'Route pack to independent dock for cross-validation'
          ],
          evidence: [
            { description: 'Single dock observation (crossing count = 1, minimum required = 2)' }
          ]
        };
      }
    }

    if (!alert) {
      detailEl.innerHTML = '<p style="color:var(--text-muted);">Select an incident from the queue to inspect evidence.</p>';
      return;
    }

    if (headerTitle) {
      headerTitle.innerHTML = `<span style="font-family:var(--font-mono);">${alert.entity_id}</span> — Root Cause Diagnosis`;
    }
    if (headerBadge) {
      headerBadge.className = `owner-badge owner-${alert.owner_category}`;
      headerBadge.textContent = alert.owner_category;
    }

    const isAck = state.acknowledgedAlerts.has(alert.alert_id);
    const isResolved = state.resolvedAlerts.has(alert.alert_id);

    detailEl.innerHTML = `
      <!-- Metric Highlights -->
      <div class="metric-grid-4">
        <div class="metric-box">
          <span class="metric-box-title">Observed Value</span>
          <span class="metric-box-value" style="color: var(--color-danger);">${alert.observed_value !== null ? alert.observed_value.toFixed(3) : '—'} <span style="font-size: 12px; font-weight: normal;">${alert.observed_unit || ''}</span></span>
        </div>
        <div class="metric-box">
          <span class="metric-box-title">Expected Cohort Baseline</span>
          <span class="metric-box-value" style="color: var(--color-success);">${alert.expected_value !== null ? alert.expected_value.toFixed(3) : '0.000'} <span style="font-size: 12px; font-weight: normal;">${alert.observed_unit || ''}</span></span>
        </div>
        <div class="metric-box">
          <span class="metric-box-title">Statistical Residual</span>
          <span class="metric-box-value" style="color: var(--color-pack);">${alert.residual_normalized ? '+' + alert.residual_normalized.toFixed(1) + 'σ' : '—'}</span>
        </div>
        <div class="metric-box">
          <span class="metric-box-title">Episode Persistence</span>
          <span class="metric-box-value">${alert.occurrence_count || 1} <span style="font-size: 12px; font-weight: normal;">sessions</span></span>
        </div>
      </div>

      <!-- Diagnostic Reasoning Statement -->
      <div class="graph-explanation" style="border-left: 3px solid var(--color-dock);">
        <strong style="color: var(--text-primary);">Diagnostic Attribution Statement:</strong><br>
        ${escapeHtml(alert.explanation || '')}
      </div>

      <!-- Evidence vs Actions Grid -->
      <div class="evidence-action-grid">
        <!-- Supporting Evidence -->
        <div class="action-box">
          <h3 class="panel-title" style="margin-bottom: var(--space-xs);">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
            Supporting Evidence Items
          </h3>
          <div class="evidence-list">
            ${(alert.evidence || []).map(ev => `
              <div class="evidence-item">
                ${escapeHtml(ev.description || '')}
                ${ev.count ? `<span style="display:block; font-family:var(--font-mono); font-size:10px; color:var(--text-muted); margin-top:2px;">Verified instances: ${ev.count}</span>` : ''}
              </div>
            `).join('') || '<p style="font-size:12px;color:var(--text-muted);">No items recorded.</p>'}
          </div>
        </div>

        <!-- Actionable Dispatch Plan -->
        <div class="action-box">
          <h3 class="panel-title" style="margin-bottom: var(--space-xs);">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
            Operator Action Checklist
          </h3>
          <p style="font-size:11px;color:var(--text-secondary);margin-bottom:var(--space-xs);">Mandatory human actions required by operational policy:</p>
          <div style="display:flex; flex-direction:column; gap:6px;">
            ${(alert.recommended_actions || []).map((act, i) => `
              <label class="action-item">
                <input type="checkbox" id="action-chk-${i}" ${isResolved ? 'checked disabled' : ''}>
                <span>${escapeHtml(act)}</span>
              </label>
            `).join('')}
          </div>

          <div class="action-buttons">
            <button type="button" class="btn btn-secondary" onclick="acknowledgeAlert('${alert.alert_id}')" ${isAck || isResolved ? 'disabled' : ''}>
              ${isAck ? 'Acknowledged ✓' : 'Acknowledge Incident'}
            </button>
            <button type="button" class="btn btn-primary" onclick="resolveAlert('${alert.alert_id}')" ${isResolved ? 'disabled' : ''}>
              ${isResolved ? 'Resolved ✓' : 'Complete & Resolve Work Order'}
            </button>
          </div>
        </div>
      </div>
    `;
  }

  window.acknowledgeAlert = function (alertId) {
    state.acknowledgedAlerts.add(alertId);
    renderIncidentList();
  };

  window.resolveAlert = function (alertId) {
    state.resolvedAlerts.add(alertId);
    renderIncidentList();
  };

  // SVG Curve Rendering
  window.loadCurveScenario = function (scenarioKey) {
    state.currentScenario = scenarioKey;
    renderCurves(scenarioKey);
  };

  function renderCurves(scenarioKey) {
    const svg = document.getElementById('primary-curve-svg');
    const tempSvg = document.getElementById('temp-curve-svg');
    const cellSvg = document.getElementById('cell-curve-svg');
    const heading = document.getElementById('curve-chart-heading');
    if (!svg || !data.curves[scenarioKey]) return;

    const points = data.curves[scenarioKey];
    const width = 800;
    const height = 240;
    const padL = 40;
    const padR = 20;
    const padT = 20;
    const padB = 30;

    const plotW = width - padL - padR;
    const plotH = height - padT - padB;

    // Headings
    if (heading) {
      if (scenarioKey === 'dock_fault') {
        heading.textContent = 'Scenario 1: Dock Current Clipping — Commanded 15.0A vs Dock Delivered 8.0A (Deficit 7.0A)';
      } else if (scenarioKey === 'pack_fault') {
        heading.textContent = 'Scenario 2: Pack Self-Heating — High Current Steps Cause Elevated Thermal Dissipation';
      } else if (scenarioKey === 'cell_fault') {
        heading.textContent = 'Scenario 3: Cell Voltage Dispersion — Weak Cell Triggers Premature Voltage Cutoff';
      } else if (scenarioKey === 'env_fault') {
        heading.textContent = 'Scenario 4: Site-Wide Ambient Thermal Derating (Station Ambient 38.5°C)';
      } else {
        heading.textContent = 'Nominal Session Baseline — Normal Constant-Current & Constant-Voltage Taper';
      }
    }

    // Scales
    const maxI = 18.0;
    const getX = t => padL + (t / 60.0) * plotW;
    const getY = val => padT + (1.0 - (val / maxI)) * plotH;

    // Build Paths
    const cmdPath = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${getX(p.minute).toFixed(1)} ${getY(p.cmd_current_a).toFixed(1)}`).join(' ');
    const dockPath = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${getX(p.minute).toFixed(1)} ${getY(p.dock_current_a).toFixed(1)}`).join(' ');
    const packPath = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${getX(p.minute).toFixed(1)} ${getY(p.pack_current_a).toFixed(1)}`).join(' ');

    // Primary Chart (Current)
    svg.innerHTML = `
      <!-- Grid Lines -->
      <line x1="${padL}" y1="${padT}" x2="${padL + plotW}" y2="${padT}" stroke="var(--border-subtle)" stroke-width="1" />
      <line x1="${padL}" y1="${getY(15)}" x2="${padL + plotW}" y2="${getY(15)}" stroke="var(--border-prominent)" stroke-dasharray="4,4" stroke-width="1" />
      <line x1="${padL}" y1="${getY(10)}" x2="${padL + plotW}" y2="${getY(10)}" stroke="var(--border-subtle)" stroke-width="1" />
      <line x1="${padL}" y1="${getY(5)}" x2="${padL + plotW}" y2="${getY(5)}" stroke="var(--border-subtle)" stroke-width="1" />
      <line x1="${padL}" y1="${padT + plotH}" x2="${padL + plotW}" y2="${padT + plotH}" stroke="var(--border-prominent)" stroke-width="1" />

      <!-- Y Axis Labels -->
      <text x="${padL - 8}" y="${getY(15) + 4}" fill="var(--text-muted)" font-size="10" font-family="var(--font-mono)" text-anchor="end">15A</text>
      <text x="${padL - 8}" y="${getY(10) + 4}" fill="var(--text-muted)" font-size="10" font-family="var(--font-mono)" text-anchor="end">10A</text>
      <text x="${padL - 8}" y="${getY(5) + 4}" fill="var(--text-muted)" font-size="10" font-family="var(--font-mono)" text-anchor="end">5A</text>
      <text x="${padL - 8}" y="${padT + plotH + 4}" fill="var(--text-muted)" font-size="10" font-family="var(--font-mono)" text-anchor="end">0A</text>

      <!-- X Axis Labels -->
      <text x="${padL}" y="${height - 8}" fill="var(--text-muted)" font-size="10" font-family="var(--font-mono)">0m</text>
      <text x="${padL + plotW * 0.5}" y="${height - 8}" fill="var(--text-muted)" font-size="10" font-family="var(--font-mono)" text-anchor="middle">30m (CC Phase)</text>
      <text x="${padL + plotW}" y="${height - 8}" fill="var(--text-muted)" font-size="10" font-family="var(--font-mono)" text-anchor="end">60m (CV Phase)</text>

      <!-- Curves -->
      <path d="${cmdPath}" fill="none" stroke="var(--color-dock)" stroke-width="2" stroke-dasharray="6,4" />
      <path d="${dockPath}" fill="none" stroke="var(--color-success)" stroke-width="2.5" />
      <path d="${packPath}" fill="none" stroke="var(--color-pack)" stroke-width="1.5" />
    `;

    // Temperature Chart
    if (tempSvg) {
      const maxT = 60.0;
      const minT = 20.0;
      const getTY = val => 15 + (1.0 - ((val - minT) / (maxT - minT))) * 125;
      const tempPath = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${(25 + (p.minute / 60) * 350).toFixed(1)} ${getTY(p.temp_c).toFixed(1)}`).join(' ');

      tempSvg.innerHTML = `
        <line x1="25" y1="${getTY(50)}" x2="375" y2="${getTY(50)}" stroke="var(--color-danger)" stroke-dasharray="3,3" stroke-width="1" />
        <text x="375" y="${getTY(50) - 3}" fill="var(--color-danger)" font-size="9" font-family="var(--font-mono)" text-anchor="end">Threshold 50°C</text>
        <path d="${tempPath}" fill="none" stroke="var(--color-pack)" stroke-width="2" />
        <text x="25" y="150" fill="var(--text-muted)" font-size="9" font-family="var(--font-mono)">0m (25°C)</text>
        <text x="375" y="150" fill="var(--text-muted)" font-size="9" font-family="var(--font-mono)" text-anchor="end">60m (${points[points.length - 1].temp_c}°C)</text>
      `;
    }

    // Cell Dispersion Chart
    if (cellSvg) {
      const maxS = 200.0;
      const getSY = val => 15 + (1.0 - (val / maxS)) * 125;
      const cellPath = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${(25 + (p.minute / 60) * 350).toFixed(1)} ${getSY(p.cell_spread_mv).toFixed(1)}`).join(' ');

      cellSvg.innerHTML = `
        <line x1="25" y1="${getSY(100)}" x2="375" y2="${getSY(100)}" stroke="var(--color-danger)" stroke-dasharray="3,3" stroke-width="1" />
        <text x="375" y="${getSY(100) - 3}" fill="var(--color-danger)" font-size="9" font-family="var(--font-mono)" text-anchor="end">Warning 100mV</text>
        <path d="${cellPath}" fill="none" stroke="var(--color-cell)" stroke-width="2" />
        <text x="25" y="150" fill="var(--text-muted)" font-size="9" font-family="var(--font-mono)">0m (${points[0].cell_spread_mv}mV)</text>
        <text x="375" y="150" fill="var(--text-muted)" font-size="9" font-family="var(--font-mono)" text-anchor="end">60m (${points[points.length - 1].cell_spread_mv}mV)</text>
      `;
    }
  }

  // Bipartite Graph Rendering
  window.loadGraphCase = function (caseKey) {
    state.currentGraphCase = caseKey;
    renderBipartiteGraph(caseKey);
  };

  function renderBipartiteGraph(caseKey) {
    const svg = document.getElementById('bipartite-svg');
    const textEl = document.getElementById('graph-explanation-text');
    const ex = data.crossingExamples[caseKey];
    if (!svg || !ex) return;

    if (textEl) {
      textEl.innerHTML = `
        <div style="font-size:14px; font-weight:700; color:var(--text-primary); margin-bottom:4px;">${escapeHtml(ex.title)}</div>
        <p>${escapeHtml(ex.conclusion || ex.explanation || '')}</p>
      `;
    }

    const sessions = ex.sessions || [];
    const docks = Array.from(new Set(sessions.map(s => s.dockId)));
    const packs = Array.from(new Set(sessions.map(s => s.packId)));

    const leftX = 140;
    const rightX = 580;
    const topY = 40;
    const spacingY = 50;

    const dockPositions = {};
    docks.forEach((d, i) => { dockPositions[d] = topY + i * spacingY; });

    const packPositions = {};
    packs.forEach((p, i) => { packPositions[p] = topY + i * spacingY; });

    // Lines
    const linesSvg = sessions.map(s => {
      const y1 = dockPositions[s.dockId];
      const y2 = packPositions[s.packId];
      const stroke = s.is_anomaly ? 'var(--color-danger)' : 'var(--color-success)';
      const width = s.is_anomaly ? 3 : 1.5;
      const opacity = s.is_anomaly ? 0.9 : 0.45;

      return `<line x1="${leftX}" y1="${y1}" x2="${rightX}" y2="${y2}" stroke="${stroke}" stroke-width="${width}" stroke-opacity="${opacity}" />`;
    }).join('');

    // Dock Nodes
    const dockNodesSvg = docks.map(d => {
      const y = dockPositions[d];
      return `
        <g transform="translate(${leftX}, ${y})">
          <circle r="8" fill="var(--bg-canvas)" stroke="var(--color-dock)" stroke-width="2.5" />
          <text x="-16" y="4" fill="var(--text-primary)" font-size="11" font-family="var(--font-mono)" text-anchor="end">${d}</text>
        </g>
      `;
    }).join('');

    // Pack Nodes
    const packNodesSvg = packs.map(p => {
      const y = packPositions[p];
      return `
        <g transform="translate(${rightX}, ${y})">
          <circle r="8" fill="var(--bg-canvas)" stroke="var(--color-pack)" stroke-width="2.5" />
          <text x="16" y="4" fill="var(--text-primary)" font-size="11" font-family="var(--font-mono)" text-anchor="start">${p}</text>
        </g>
      `;
    }).join('');

    svg.innerHTML = `
      <text x="${leftX}" y="20" fill="var(--text-muted)" font-size="11" font-weight="700" font-family="var(--font-mono)" text-anchor="middle">CHARGER DOCKS</text>
      <text x="${rightX}" y="20" fill="var(--text-muted)" font-size="11" font-weight="700" font-family="var(--font-mono)" text-anchor="middle">BATTERY PACKS</text>
      ${linesSvg}
      ${dockNodesSvg}
      ${packNodesSvg}
    `;
  }

  // Populate Scenario Table
  function renderScenarioTable() {
    const tbody = document.getElementById('scenario-table-body');
    if (!tbody || !data.evalReport || !data.evalReport.scenarios) return;

    const sc = data.evalReport.scenarios;
    const rows = [
      { id: 'S01', name: 'Bad Dock (Current Deficit)', owner: 'CHARGER_DOCK', item: sc.S01_bad_dock },
      { id: 'S02', name: 'Bad Pack (Self-Heating)', owner: 'PACK', item: sc.S02_bad_pack },
      { id: 'S03', name: 'Cell Divergence / Aging', owner: 'CELL_CHEMISTRY', item: sc.S03_cell_chemistry },
      { id: 'S04', name: 'Site Thermal Derating', owner: 'ENVIRONMENT', item: sc.S04_environment },
      { id: 'S05', name: 'Low Crossing Abstention', owner: 'INSUFFICIENT_EVIDENCE', item: sc.S05_abstention },
    ];

    tbody.innerHTML = rows.map(r => `
      <tr>
        <td><strong>${r.id}</strong></td>
        <td>${r.name}</td>
        <td><span class="owner-badge owner-${r.owner.includes('INSUFFICIENT') ? 'ABSTAIN' : r.owner}">${r.owner}</span></td>
        <td>${escapeHtml((r.item && r.item.evidence) || '—')}</td>
        <td><span class="badge-pass">${r.item && r.item.pass ? 'PASS ✓' : 'FAIL'}</span></td>
      </tr>
    `).join('');
  }

  function escapeHtml(str) {
    return (str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  // Initialize
  document.addEventListener('DOMContentLoaded', () => {
    renderStations();
    renderIncidentList();
    renderCurves('dock_fault');
    renderBipartiteGraph('dock_isolation');
    renderScenarioTable();
  });
})();
