import React, { useState, useMemo } from 'react';
import { 
  AlertTriangle, 
  Filter, 
  CheckCircle, 
  Clock, 
  Search, 
  ChevronRight, 
  FileSpreadsheet, 
  ExternalLink,
  ShieldAlert
} from 'lucide-react';

export default function AlertsTriageView({ data, onSelectAlert, searchQuery }) {
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [ownerFilter, setOwnerFilter] = useState('ALL');

  const alerts = data.alerts || [];

  const filteredAlerts = useMemo(() => {
    return alerts.filter(alert => {
      // Status filter
      if (statusFilter !== 'ALL' && (alert.status || 'OPEN') !== statusFilter) {
        return false;
      }
      // Severity filter
      if (severityFilter !== 'ALL' && alert.severity !== severityFilter) {
        return false;
      }
      // Owner filter
      if (ownerFilter !== 'ALL' && alert.owner_category !== ownerFilter) {
        return false;
      }
      // Text search
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        const matchEntity = (alert.entity_id || '').toLowerCase().includes(query);
        const matchOwner = (alert.owner_category || '').toLowerCase().includes(query);
        const matchFeature = (alert.feature_ids ? alert.feature_ids.join(' ') : '').toLowerCase().includes(query);
        const matchId = (alert.alert_id || '').toLowerCase().includes(query);
        if (!matchEntity && !matchOwner && !matchFeature && !matchId) {
          return false;
        }
      }
      return true;
    });
  }, [alerts, statusFilter, severityFilter, ownerFilter, searchQuery]);

  return (
    <div className="view-container">
      {/* View Header */}
      <div className="view-header">
        <div>
          <h1 className="view-title">Incident Triage & Alert Management</h1>
          <p className="view-subtitle">
            Actionable attribution queue with statistical confidence intervals and cross-asset physical proofs.
          </p>
        </div>
      </div>

      {/* Filter Control Bar */}
      <div className="card" style={{ padding: '16px 20px' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', alignItems: 'center', justifyContent: 'space-between' }}>
          {/* Status Tabs */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>Status:</span>
            <div className="segmented-control">
              {['ALL', 'OPEN', 'ACKNOWLEDGED', 'RESOLVED'].map(st => (
                <button
                  key={st}
                  type="button"
                  className={`segmented-btn ${statusFilter === st ? 'active' : ''}`}
                  onClick={() => setStatusFilter(st)}
                >
                  {st}
                </button>
              ))}
            </div>
          </div>

          {/* Severity Filters */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>Severity:</span>
            <div className="segmented-control">
              {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM'].map(sev => (
                <button
                  key={sev}
                  type="button"
                  className={`segmented-btn ${severityFilter === sev ? 'active' : ''}`}
                  onClick={() => setSeverityFilter(sev)}
                >
                  {sev}
                </button>
              ))}
            </div>
          </div>

          {/* Owner Filters */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>Owner:</span>
            <select
              value={ownerFilter}
              onChange={(e) => setOwnerFilter(e.target.value)}
              style={{
                padding: '6px 10px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-subtle)',
                backgroundColor: '#ffffff',
                fontSize: '12px',
                fontWeight: 500,
                color: 'var(--text-primary)'
              }}
            >
              <option value="ALL">All Owners</option>
              <option value="CHARGER_DOCK">Charger Dock</option>
              <option value="PACK">Battery Pack</option>
              <option value="CELL_CHEMISTRY">Cell Chemistry</option>
              <option value="ENVIRONMENT">Environment / Grid</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Incident Table */}
      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-secondary)' }}>
            Showing {filteredAlerts.length} of {alerts.length} Registered Telemetry Incidents
          </div>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            Click any row to open the complete inspection drawer
          </span>
        </div>

        <div className="data-table-container" style={{ border: 'none', borderRadius: 0 }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Severity</th>
                <th>Asset Entity ID</th>
                <th>Owner Domain</th>
                <th>Responsible Team</th>
                <th>Anomaly Feature</th>
                <th>Observed Residual</th>
                <th>Z-Score</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredAlerts.length === 0 ? (
                <tr>
                  <td colSpan="9" style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)' }}>
                    No alerts match the selected filter criteria.
                  </td>
                </tr>
              ) : (
                filteredAlerts.map(alert => (
                  <tr key={alert.alert_id} onClick={() => onSelectAlert(alert)}>
                    <td>
                      <span className={`badge ${alert.severity === 'CRITICAL' ? 'badge-red' : alert.severity === 'HIGH' ? 'badge-amber' : 'badge-blue'}`}>
                        {alert.severity}
                      </span>
                    </td>
                    <td style={{ fontWeight: 600, fontFamily: 'var(--font-mono)' }}>
                      {alert.entity_id}
                    </td>
                    <td>
                      <span className="badge badge-gray">
                        {alert.owner_category}
                      </span>
                    </td>
                    <td style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                      {alert.owner_team || 'infrastructure_ops'}
                    </td>
                    <td style={{ fontWeight: 500, color: 'var(--text-primary)' }}>
                      {alert.feature_ids ? alert.feature_ids[0] : 'Telemetry Deviation'}
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>
                      {typeof alert.observed_value === 'number' ? alert.observed_value.toFixed(4) : alert.observed_value} {alert.observed_unit}
                    </td>
                    <td style={{ fontWeight: 600, color: 'var(--system-red)', fontFamily: 'var(--font-mono)' }}>
                      +{typeof alert.residual_normalized === 'number' ? alert.residual_normalized.toFixed(1) : '120.0'}σ
                    </td>
                    <td>
                      <span className={`badge ${alert.status === 'RESOLVED' ? 'badge-green' : alert.status === 'ACKNOWLEDGED' ? 'badge-blue' : 'badge-amber'}`}>
                        {alert.status || 'OPEN'}
                      </span>
                    </td>
                    <td>
                      <button
                        type="button"
                        className="btn-secondary"
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectAlert(alert);
                        }}
                        style={{ padding: '4px 8px', fontSize: '11px' }}
                      >
                        <span>Inspect</span>
                        <ChevronRight size={12} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
