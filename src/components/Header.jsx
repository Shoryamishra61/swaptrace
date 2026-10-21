import React from 'react';
import { Search, Download, RefreshCw, ChevronRight } from 'lucide-react';

export default function Header({ currentView, searchQuery, onSearchChange, onExportData, onRefresh, onNavigate }) {
  const viewTitles = {
    overview: 'Fleet Command & Diagnostics',
    alerts: 'Incident Triage & Alert Management',
    waveforms: 'Multi-Sensor Telemetry Waveforms',
    packs: '14S Battery Pack Cell Topology',
    stations: 'Swapping Stations & Charging Docks',
    attribution: 'Physics Attribution & Evidence Engine',
    defense: 'Adversarial Reviewer Defense & Proofs (Gate 10)',
  };

  return (
    <header className="app-header">
      <div className="breadcrumbs">
        <span>SwapTrace</span>
        <ChevronRight size={14} />
        <span className="breadcrumb-active">{viewTitles[currentView] || 'Console'}</span>
      </div>

      <div className="header-actions">
        <div className="search-box">
          <label htmlFor="global-search-input" style={{ position: 'absolute', width: 1, height: 1, overflow: 'hidden', clip: 'rect(0,0,0,0)' }}>
            Search alerts, packs, and stations
          </label>
          <Search size={15} color="var(--text-muted)" />
          <input
            id="global-search-input"
            name="global_search"
            type="search"
            className="search-input"
            placeholder="Search alerts, packs, docks..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            aria-label="Search alerts, packs, and stations"
          />
        </div>

        <button
          type="button"
          className="btn-secondary"
          onClick={onRefresh}
          title="Reload latest telemetry snapshot"
        >
          <RefreshCw size={14} />
          <span>Sync</span>
        </button>

        <button
          type="button"
          className="btn-primary"
          onClick={onExportData}
          title="Export audit-ready JSON bundle"
        >
          <Download size={14} />
          <span>Export Evidence</span>
        </button>
      </div>
    </header>
  );
}
