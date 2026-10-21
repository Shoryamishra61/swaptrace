import React, { useState } from 'react';
import { BatteryCharging, AlertCircle, CheckCircle2, Thermometer, ShieldAlert, Zap, Cpu } from 'lucide-react';

export default function PackDiagnosticsView() {
  const [selectedPackId, setSelectedPackId] = useState('PCK-006');

  const packs = [
    {
      id: 'PCK-001',
      name: 'Battery Pack 001',
      station: 'STA-01 (Taipei Hub)',
      health: '99.1%',
      cycles: 142,
      status: 'NOMINAL',
      medianVoltage: 3.652,
      maxDeltaMv: 8.2,
      temperatureC: 28.4,
      esrMohm: 14.2,
      cells: [3.651, 3.653, 3.652, 3.654, 3.652, 3.650, 3.653, 3.652, 3.651, 3.652, 3.655, 3.652, 3.653, 3.651]
    },
    {
      id: 'PCK-006',
      name: 'Battery Pack 006',
      station: 'STA-02 (New Taipei)',
      health: '92.4%',
      cycles: 418,
      status: 'IMBALANCE_DETECTED',
      medianVoltage: 3.648,
      maxDeltaMv: 44.8,
      temperatureC: 34.6,
      esrMohm: 22.8,
      // Cell 9 has anomalous voltage depression (divergence)
      cells: [3.649, 3.647, 3.650, 3.648, 3.646, 3.648, 3.649, 3.651, 3.604, 3.648, 3.649, 3.647, 3.650, 3.648]
    },
    {
      id: 'PCK-014',
      name: 'Battery Pack 014',
      station: 'STA-04 (Hsinchu Tech)',
      health: '86.7%',
      cycles: 685,
      status: 'THERMAL_DERATE',
      medianVoltage: 3.635,
      maxDeltaMv: 24.1,
      temperatureC: 41.2,
      esrMohm: 29.4,
      cells: [3.638, 3.632, 3.636, 3.634, 3.635, 3.633, 3.637, 3.635, 3.631, 3.636, 3.634, 3.639, 3.633, 3.635]
    }
  ];

  const currentPack = packs.find(p => p.id === selectedPackId) || packs[1];

  return (
    <div className="view-container">
      {/* View Header */}
      <div className="view-header">
        <div>
          <h1 className="view-title">14S Battery Pack Cell Topology & Degradation</h1>
          <p className="view-subtitle">
            Sub-millivolt individual cell voltage balancing, electrochemical dispersion, and internal impedance analytics.
          </p>
        </div>
      </div>

      {/* Pack Selector Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '14px' }}>
        {packs.map(p => {
          const isSelected = p.id === selectedPackId;
          const isFault = p.status !== 'NOMINAL';
          return (
            <button
              key={p.id}
              type="button"
              onClick={() => setSelectedPackId(p.id)}
              style={{
                padding: '16px',
                borderRadius: 'var(--radius-md)',
                border: isSelected ? '2px solid var(--system-blue)' : '1px solid var(--border-subtle)',
                backgroundColor: isSelected ? '#ffffff' : '#f8fafc',
                textAlign: 'left',
                cursor: 'pointer',
                boxShadow: isSelected ? 'var(--shadow-md)' : 'none'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontWeight: 700, fontSize: '15px', color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>
                  {p.id}
                </span>
                <span className={`badge ${isFault ? 'badge-amber' : 'badge-green'}`}>
                  {p.status}
                </span>
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>
                {p.station} · {p.cycles} Cycles
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                <span>State of Health:</span>
                <strong style={{ color: isFault ? 'var(--system-amber)' : 'var(--system-green)' }}>{p.health}</strong>
              </div>
            </button>
          );
        })}
      </div>

      {/* Selected Pack Inspection Grid */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">
              <BatteryCharging size={18} color="var(--system-blue)" />
              <span>14-Cell Series Topology Matrix: {currentPack.name} ({currentPack.id})</span>
            </h2>
            <span className="card-subtitle">
              Nominal 50.4V NMC architecture · Pack Median: {currentPack.medianVoltage}V · Thermal: {currentPack.temperatureC}°C
            </span>
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <div style={{ padding: '6px 12px', background: '#f8fafc', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)', fontSize: '12px' }}>
              Max Cell Δ: <strong style={{ color: currentPack.maxDeltaMv > 30 ? 'var(--system-red)' : 'var(--system-green)' }}>{currentPack.maxDeltaMv} mV</strong>
            </div>
            <div style={{ padding: '6px 12px', background: '#f8fafc', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)', fontSize: '12px' }}>
              ESR: <strong>{currentPack.esrMohm} mΩ</strong>
            </div>
          </div>
        </div>

        {/* 14S Cell Visualization Array */}
        <div style={{ marginBottom: '14px', fontSize: '12px', color: 'var(--text-muted)' }}>
          INDIVIDUAL CELL VOLTAGE MONITOR (C01 TO C14):
        </div>

        <div className="pack-grid-container">
          {currentPack.cells.map((volt, idx) => {
            const cellNum = idx + 1;
            const deltaMv = Math.abs((volt - currentPack.medianVoltage) * 1000);
            const isImbalanced = deltaMv > 30;

            return (
              <div
                key={cellNum}
                className={`cell-brick ${isImbalanced ? 'imbalanced' : ''}`}
              >
                <div className="cell-label">Cell {cellNum < 10 ? `0${cellNum}` : cellNum}</div>
                <div className="cell-voltage" style={{ color: isImbalanced ? 'var(--system-red)' : 'var(--text-primary)' }}>
                  {volt.toFixed(3)}V
                </div>
                <div style={{ fontSize: '10px', color: isImbalanced ? 'var(--system-red)' : 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                  {volt >= currentPack.medianVoltage ? '+' : '-'}{deltaMv.toFixed(1)}mV
                </div>
              </div>
            );
          })}
        </div>

        {/* Diagnostic Callout */}
        {currentPack.maxDeltaMv > 30 && (
          <div style={{
            marginTop: '20px',
            padding: '14px 18px',
            backgroundColor: 'var(--system-red-subtle)',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--system-red-border)',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '12px'
          }}>
            <AlertCircle size={18} color="var(--system-red)" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <div style={{ fontWeight: 600, color: 'var(--system-red)', fontSize: '13px' }}>
                Severe Cell Chemistry Imbalance Detected on Cell 09
              </div>
              <div style={{ fontSize: '12px', color: '#991b1b', marginTop: '2px' }}>
                Cell 09 exhibits a 44.8mV voltage depression below pack median during constant-current charging. 
                Root cause attributed to localized impedance increase and active material loss. Recommended action: Route pack to balancing maintenance.
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
