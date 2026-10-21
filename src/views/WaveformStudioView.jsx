import React, { useState } from 'react';
import { LineChart, Activity, Zap, Thermometer, Battery, Info, Gauge } from 'lucide-react';

export default function WaveformStudioView({ data }) {
  const [selectedScenario, setSelectedScenario] = useState('dock_fault');
  const [scrubberIndex, setScrubberIndex] = useState(25);

  const curves = data.curves || {};
  const activeCurve = curves[selectedScenario] || curves['normal'] || [];

  const scenarios = [
    { id: 'normal', name: 'Nominal Baseline', desc: 'Healthy CC-CV charging profile; zero anomalies', owner: 'HEALTHY' },
    { id: 'dock_fault', name: 'Charger Dock CC Derate', desc: 'Commanded vs measured current residual divergence', owner: 'CHARGER_DOCK' },
    { id: 'pack_fault', name: 'Pack Thermal Self-Heating', desc: 'Excessive internal resistance and rapid ΔT rise', owner: 'PACK' },
    { id: 'cell_fault', name: '14S Cell Imbalance Drift', desc: 'Cell voltage dispersion exceeds 35mV tolerance', owner: 'CELL_CHEMISTRY' },
    { id: 'env_fault', name: 'Site-wide Ambient Heatwave', desc: 'Station ambient > 38°C triggers thermal protection', owner: 'ENVIRONMENT' },
  ];

  const currentPoint = activeCurve[scrubberIndex] || activeCurve[0] || {
    minute: scrubberIndex,
    soc: 45,
    cmd_current_a: 15,
    dock_current_a: 12.1,
    pack_current_a: 12.1,
    pack_voltage_v: 51.2,
    temp_c: 32.4,
    cell_spread_mv: 18
  };

  // Helper to generate SVG path for a metric
  const renderSvgLine = (key, minVal, maxVal, strokeColor, strokeWidth = 2, strokeDash = '') => {
    if (!activeCurve || activeCurve.length === 0) return '';
    const width = 800;
    const height = 120;
    const padding = 10;

    const points = activeCurve.map((pt, idx) => {
      const x = padding + (idx / (activeCurve.length - 1)) * (width - 2 * padding);
      const val = pt[key] || 0;
      const normalized = (val - minVal) / (maxVal - minVal || 1);
      const y = height - padding - normalized * (height - 2 * padding);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    });

    return (
      <polyline
        fill="none"
        stroke={strokeColor}
        strokeWidth={strokeWidth}
        strokeDasharray={strokeDash}
        points={points.join(' ')}
      />
    );
  };

  return (
    <div className="view-container">
      {/* Header */}
      <div className="view-header">
        <div>
          <h1 className="view-title">Multi-Sensor Telemetry Waveform Studio</h1>
          <p className="view-subtitle">
            Synchronized 1Hz session replay inspecting voltage, current, thermal, and cell dispersion residuals.
          </p>
        </div>
      </div>

      {/* Scenario Selector Bar */}
      <div className="card" style={{ padding: '16px 20px' }}>
        <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '10px' }}>
          SELECT REPLAY BENCHMARK SCENARIO:
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px' }}>
          {scenarios.map(sc => {
            const isSelected = selectedScenario === sc.id;
            return (
              <button
                key={sc.id}
                type="button"
                onClick={() => {
                  setSelectedScenario(sc.id);
                  setScrubberIndex(25);
                }}
                style={{
                  padding: '12px 14px',
                  borderRadius: 'var(--radius-sm)',
                  border: isSelected ? '2px solid var(--system-blue)' : '1px solid var(--border-subtle)',
                  backgroundColor: isSelected ? 'var(--system-blue-subtle)' : '#ffffff',
                  textAlign: 'left',
                  cursor: 'pointer'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <span style={{ fontWeight: 600, fontSize: '13px', color: isSelected ? 'var(--system-blue)' : 'var(--text-primary)' }}>
                    {sc.name}
                  </span>
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', lineHeight: 1.3 }}>
                  {sc.desc}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Synchronous Scrubber Bar */}
      <div className="card" style={{ padding: '14px 20px', display: 'flex', alignItems: 'center', gap: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: '160px' }}>
          <Gauge size={16} color="var(--system-blue)" />
          <span style={{ fontSize: '13px', fontWeight: 600 }}>Replay Cursor:</span>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', fontWeight: 700, color: 'var(--system-blue)' }}>
            Min {currentPoint.minute} / 60
          </span>
        </div>

        <label htmlFor="waveform-time-scrubber" style={{ position: 'absolute', width: 1, height: 1, overflow: 'hidden', clip: 'rect(0,0,0,0)' }}>
          Replay Time Scrubber (minutes)
        </label>
        <input
          id="waveform-time-scrubber"
          name="waveform_scrubber"
          type="range"
          min="0"
          max={Math.max(0, activeCurve.length - 1)}
          value={scrubberIndex}
          onChange={(e) => setScrubberIndex(parseInt(e.target.value, 10))}
          style={{ flex: 1, accentColor: 'var(--system-blue)', cursor: 'pointer' }}
          aria-label="Waveform Time Scrubber"
        />

        <div style={{ display: 'flex', gap: '16px', fontSize: '12px', fontFamily: 'var(--font-mono)' }}>
          <span>SOC: <strong>{currentPoint.soc}%</strong></span>
          <span>V_pack: <strong>{currentPoint.pack_voltage_v}V</strong></span>
          <span>I_pack: <strong>{currentPoint.pack_current_a}A</strong></span>
          <span>Temp: <strong>{currentPoint.temp_c}°C</strong></span>
          <span>Cell Δ: <strong>{currentPoint.cell_spread_mv}mV</strong></span>
        </div>
      </div>

      {/* Waveform Channels */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {/* Track 1: Current Channel */}
        <div className="waveform-panel">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Zap size={15} color="var(--system-blue)" />
              <span style={{ fontSize: '13px', fontWeight: 600 }}>Channel 1: Charging Current Control (Commanded vs Measured)</span>
            </div>
            <div style={{ display: 'flex', gap: '14px', fontSize: '11px' }}>
              <span style={{ color: 'var(--text-muted)' }}>-- Commanded (A)</span>
              <span style={{ color: 'var(--system-blue)', fontWeight: 600 }}>— Measured Pack Current ({currentPoint.pack_current_a} A)</span>
            </div>
          </div>

          <div className="chart-canvas-container">
            <svg className="chart-svg" viewBox="0 0 800 120" preserveAspectRatio="none">
              {/* Grid lines */}
              <line x1="10" y1="20" x2="790" y2="20" stroke="#f1f5f9" strokeWidth="1" />
              <line x1="10" y1="60" x2="790" y2="60" stroke="#f1f5f9" strokeWidth="1" />
              <line x1="10" y1="100" x2="790" y2="100" stroke="#f1f5f9" strokeWidth="1" />

              {/* Commanded line (dashed) */}
              {renderSvgLine('cmd_current_a', 0, 20, '#94a3b8', 1.5, '4,4')}
              {/* Measured line */}
              {renderSvgLine('pack_current_a', 0, 20, '#0071e3', 2)}

              {/* Scrubber crosshair */}
              <line
                x1={10 + (scrubberIndex / (activeCurve.length - 1 || 1)) * 780}
                y1="0"
                x2={10 + (scrubberIndex / (activeCurve.length - 1 || 1)) * 780}
                y2="120"
                stroke="#dc2626"
                strokeWidth="1.5"
                strokeDasharray="2,2"
              />
            </svg>
          </div>
        </div>

        {/* Track 2: Pack Terminal Voltage Channel */}
        <div className="waveform-panel">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Activity size={15} color="var(--system-purple)" />
              <span style={{ fontSize: '13px', fontWeight: 600 }}>Channel 2: Pack Terminal Voltage (14S Stack Progression)</span>
            </div>
            <span style={{ color: 'var(--system-purple)', fontWeight: 600, fontSize: '11px', fontFamily: 'var(--font-mono)' }}>
              Current: {currentPoint.pack_voltage_v} V
            </span>
          </div>

          <div className="chart-canvas-container">
            <svg className="chart-svg" viewBox="0 0 800 120" preserveAspectRatio="none">
              <line x1="10" y1="20" x2="790" y2="20" stroke="#f1f5f9" strokeWidth="1" />
              <line x1="10" y1="60" x2="790" y2="60" stroke="#f1f5f9" strokeWidth="1" />
              <line x1="10" y1="100" x2="790" y2="100" stroke="#f1f5f9" strokeWidth="1" />

              {renderSvgLine('pack_voltage_v', 44, 58, '#7c3aed', 2)}

              <line
                x1={10 + (scrubberIndex / (activeCurve.length - 1 || 1)) * 780}
                y1="0"
                x2={10 + (scrubberIndex / (activeCurve.length - 1 || 1)) * 780}
                y2="120"
                stroke="#dc2626"
                strokeWidth="1.5"
                strokeDasharray="2,2"
              />
            </svg>
          </div>
        </div>

        {/* Track 3: Cell Voltage Dispersion Channel */}
        <div className="waveform-panel">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Battery size={15} color="var(--system-amber)" />
              <span style={{ fontSize: '13px', fontWeight: 600 }}>Channel 3: 14S Cell-to-Cell Voltage Dispersion (ΔV = max - min)</span>
            </div>
            <span style={{ color: currentPoint.cell_spread_mv > 30 ? 'var(--system-red)' : 'var(--system-green)', fontWeight: 600, fontSize: '11px', fontFamily: 'var(--font-mono)' }}>
              Spread: {currentPoint.cell_spread_mv} mV (Threshold: 35mV)
            </span>
          </div>

          <div className="chart-canvas-container">
            <svg className="chart-svg" viewBox="0 0 800 120" preserveAspectRatio="none">
              {/* Threshold line at 35mV */}
              <line x1="10" y1="40" x2="790" y2="40" stroke="#fecaca" strokeWidth="1" strokeDasharray="3,3" />

              {renderSvgLine('cell_spread_mv', 5, 55, '#d97706', 2)}

              <line
                x1={10 + (scrubberIndex / (activeCurve.length - 1 || 1)) * 780}
                y1="0"
                x2={10 + (scrubberIndex / (activeCurve.length - 1 || 1)) * 780}
                y2="120"
                stroke="#dc2626"
                strokeWidth="1.5"
                strokeDasharray="2,2"
              />
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
}
