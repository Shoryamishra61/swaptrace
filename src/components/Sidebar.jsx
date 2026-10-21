import React from 'react';
import { 
  Activity, 
  AlertTriangle, 
  LineChart, 
  BatteryCharging, 
  Cpu, 
  Layers, 
  ShieldCheck, 
  Zap,
  Server
} from 'lucide-react';

export default function Sidebar({ currentView, onViewChange, alertCount }) {
  const navItems = [
    { id: 'overview', label: 'Fleet Command', icon: Activity, badge: null },
    { id: 'alerts', label: 'Incident Triage', icon: AlertTriangle, badge: alertCount, badgeType: 'danger' },
    { id: 'waveforms', label: 'Waveform Studio', icon: LineChart, badge: '5 Scenarios' },
    { id: 'packs', label: '14S Pack Topology', icon: BatteryCharging, badge: 'Fleet' },
    { id: 'stations', label: 'Station & Dock Rack', icon: Server, badge: '4 Sites' },
    { id: 'attribution', label: 'Attribution Engine', icon: Cpu, badge: 'Physics' },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="brand-badge">
          <div className="brand-logo-icon">
            <Zap size={18} strokeWidth={2.5} />
          </div>
          <div>
            <div className="brand-title">SwapTrace</div>
            <div className="brand-subtitle">Telemetry Attribution v1.0</div>
          </div>
        </div>
      </div>

      <nav className="sidebar-nav" aria-label="Main Navigation">
        <div>
          <div className="nav-section-title">Diagnostics & Telemetry</div>
          <ul className="nav-item-list">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentView === item.id;
              return (
                <li key={item.id}>
                  <button
                    type="button"
                    className={`nav-item-btn ${isActive ? 'active' : ''}`}
                    onClick={() => onViewChange(item.id)}
                    aria-current={isActive ? 'page' : undefined}
                  >
                    <Icon size={16} strokeWidth={isActive ? 2.2 : 1.8} />
                    <span>{item.label}</span>
                    {item.badge && (
                      <span className={`nav-badge ${item.badgeType === 'danger' ? 'danger' : ''}`}>
                        {item.badge}
                      </span>
                    )}
                  </button>
                </li>
              );
            })}
          </ul>
        </div>

        <div style={{ marginTop: 'auto', paddingTop: '16px' }}>
          <div className="nav-section-title">System Status</div>
          <div style={{ padding: '0 8px', fontSize: '12px', color: 'var(--text-muted)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
              <span>Precision Target:</span>
              <span style={{ fontWeight: 600, color: 'var(--system-green)' }}>95.3%</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
              <span>False Alert Burden:</span>
              <span style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>18.6 / 1k</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Safe Abstentions:</span>
              <span style={{ fontWeight: 600, color: 'var(--system-amber)' }}>47 Sessions</span>
            </div>
          </div>
        </div>
      </nav>

      <div className="sidebar-footer">
        <div className="status-indicator">
          <span className="status-dot"></span>
          <span>Pipeline Active</span>
        </div>
        <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          SEEDED N=1,937
        </span>
      </div>
    </aside>
  );
}
