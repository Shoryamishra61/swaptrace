import React, { useState } from 'react';
import { Server, Zap, Thermometer, ShieldAlert, CheckCircle, Activity, Gauge } from 'lucide-react';

export default function StationCabinetsView({ data }) {
  const [selectedStationId, setSelectedStationId] = useState('STA-02');

  const stationsData = {
    'STA-01': {
      name: 'Taipei Central Hub',
      address: 'Zhongzheng District, Taipei',
      ambientC: 26.2,
      gridVoltageV: 220.4,
      gridStatus: 'NOMINAL',
      slots: [
        { slot: 1, status: 'CHARGING', packId: 'PCK-001', currentA: 14.8, contactResMOhms: 12.4, tempC: 28.1 },
        { slot: 2, status: 'READY_FOR_SWAP', packId: 'PCK-002', currentA: 0.0, contactResMOhms: 11.8, tempC: 26.5 },
        { slot: 3, status: 'CHARGING', packId: 'PCK-003', currentA: 15.0, contactResMOhms: 13.1, tempC: 29.4 },
        { slot: 4, status: 'READY_FOR_SWAP', packId: 'PCK-004', currentA: 0.0, contactResMOhms: 12.0, tempC: 26.2 },
        { slot: 5, status: 'CHARGING', packId: 'PCK-005', currentA: 14.9, contactResMOhms: 12.6, tempC: 27.8 },
        { slot: 6, status: 'READY_FOR_SWAP', packId: 'PCK-007', currentA: 0.0, contactResMOhms: 11.9, tempC: 26.0 },
        { slot: 7, status: 'EMPTY', packId: 'NONE', currentA: 0.0, contactResMOhms: 0.0, tempC: 25.8 },
        { slot: 8, status: 'READY_FOR_SWAP', packId: 'PCK-008', currentA: 0.0, contactResMOhms: 12.2, tempC: 26.4 }
      ]
    },
    'STA-02': {
      name: 'New Taipei Industrial Station',
      address: 'Sanchong District, New Taipei',
      ambientC: 27.1,
      gridVoltageV: 219.8,
      gridStatus: 'NOMINAL',
      slots: [
        { slot: 1, status: 'CHARGING', packId: 'PCK-010', currentA: 14.7, contactResMOhms: 13.5, tempC: 29.2 },
        { slot: 2, status: 'READY_FOR_SWAP', packId: 'PCK-011', currentA: 0.0, contactResMOhms: 12.1, tempC: 27.0 },
        { slot: 3, status: 'CHARGING', packId: 'PCK-012', currentA: 14.9, contactResMOhms: 12.9, tempC: 28.6 },
        // Slot 4 has anomalous contact resistance!
        { slot: 4, status: 'FAULT', packId: 'PCK-006', currentA: 9.4, contactResMOhms: 68.4, tempC: 42.1, faultName: 'Excess Contact Resistance' },
        { slot: 5, status: 'READY_FOR_SWAP', packId: 'PCK-015', currentA: 0.0, contactResMOhms: 12.0, tempC: 26.8 },
        { slot: 6, status: 'CHARGING', packId: 'PCK-016', currentA: 15.0, contactResMOhms: 13.2, tempC: 28.9 },
        { slot: 7, status: 'EMPTY', packId: 'NONE', currentA: 0.0, contactResMOhms: 0.0, tempC: 26.5 },
        { slot: 8, status: 'READY_FOR_SWAP', packId: 'PCK-017', currentA: 0.0, contactResMOhms: 12.3, tempC: 27.1 }
      ]
    },
    'STA-04': {
      name: 'Hsinchu Tech Interchange',
      address: 'East District, Hsinchu Science Park',
      ambientC: 38.5,
      gridVoltageV: 204.2,
      gridStatus: 'GRID_SAG_DETECTED',
      slots: [
        { slot: 1, status: 'THERMAL_DERATE', packId: 'PCK-020', currentA: 7.5, contactResMOhms: 14.1, tempC: 44.8 },
        { slot: 2, status: 'THERMAL_DERATE', packId: 'PCK-021', currentA: 8.0, contactResMOhms: 13.9, tempC: 43.6 },
        { slot: 3, status: 'THERMAL_DERATE', packId: 'PCK-022', currentA: 7.8, contactResMOhms: 14.5, tempC: 44.2 },
        { slot: 4, status: 'THERMAL_DERATE', packId: 'PCK-023', currentA: 7.2, contactResMOhms: 14.0, tempC: 45.1 },
        { slot: 5, status: 'EMPTY', packId: 'NONE', currentA: 0.0, contactResMOhms: 0.0, tempC: 38.5 },
        { slot: 6, status: 'READY_FOR_SWAP', packId: 'PCK-024', currentA: 0.0, contactResMOhms: 13.0, tempC: 37.9 },
        { slot: 7, status: 'EMPTY', packId: 'NONE', currentA: 0.0, contactResMOhms: 0.0, tempC: 38.5 },
        { slot: 8, status: 'READY_FOR_SWAP', packId: 'PCK-025', currentA: 0.0, contactResMOhms: 13.2, tempC: 38.0 }
      ]
    }
  };

  const currentStation = stationsData[selectedStationId] || stationsData['STA-02'];

  return (
    <div className="view-container">
      {/* Header */}
      <div className="view-header">
        <div>
          <h1 className="view-title">Swapping Station Cabinets & Dock Racks</h1>
          <p className="view-subtitle">
            8-Bay charging rack diagnostics, contact resistance ($R_{'{'}contact{'}'}$), and AC grid brownout monitoring.
          </p>
        </div>
      </div>

      {/* Station Selector Bar */}
      <div style={{ display: 'flex', gap: '10px' }}>
        {Object.keys(stationsData).map(stId => {
          const st = stationsData[stId];
          const isSelected = selectedStationId === stId;
          return (
            <button
              key={stId}
              type="button"
              onClick={() => setSelectedStationId(stId)}
              style={{
                padding: '12px 18px',
                borderRadius: 'var(--radius-sm)',
                border: isSelected ? '2px solid var(--system-blue)' : '1px solid var(--border-subtle)',
                backgroundColor: isSelected ? 'var(--system-blue-subtle)' : '#ffffff',
                cursor: 'pointer',
                textAlign: 'left',
                display: 'flex',
                flexDirection: 'column',
                gap: '4px',
                minWidth: '220px'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontWeight: 700, fontSize: '14px', color: isSelected ? 'var(--system-blue)' : 'var(--text-primary)' }}>
                  {st.name}
                </span>
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                Ambient: {st.ambientC}°C · Grid: {st.gridVoltageV}V
              </div>
            </button>
          );
        })}
      </div>

      {/* Station Environment & Grid Telemetry */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-label">
            <span>Station Ambient Temp</span>
            <Thermometer size={16} color="var(--system-amber)" />
          </div>
          <div className="kpi-value" style={{ color: currentStation.ambientC > 35 ? 'var(--system-red)' : 'var(--text-primary)' }}>
            {currentStation.ambientC}°C
          </div>
          <div className="kpi-trend">
            <span>{currentStation.ambientC > 35 ? 'Excess ambient thermal load' : 'Nominal ambient envelope'}</span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">
            <span>AC Input Grid Voltage</span>
            <Activity size={16} color="var(--system-blue)" />
          </div>
          <div className="kpi-value" style={{ color: currentStation.gridVoltageV < 210 ? 'var(--system-red)' : 'var(--text-primary)' }}>
            {currentStation.gridVoltageV} V
          </div>
          <div className="kpi-trend">
            <span>Nominal 220V RMS utility feed</span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">
            <span>Rack Power Status</span>
            <Zap size={16} color="var(--system-green)" />
          </div>
          <div className="kpi-value" style={{ fontSize: '20px', color: currentStation.gridStatus === 'NOMINAL' ? 'var(--system-green)' : 'var(--system-amber)' }}>
            {currentStation.gridStatus}
          </div>
          <div className="kpi-trend">
            <span>8 Swapping Bays active</span>
          </div>
        </div>
      </div>

      {/* 8-Bay Cabinet Rack Layout */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">
              <Server size={18} color="var(--system-blue)" />
              <span>8-Bay Swapping Cabinet Architecture: {currentStation.name}</span>
            </h2>
            <span className="card-subtitle">
              Live power stage telemetry, dock contact resistance, and thermal readings across Bays 1 to 8
            </span>
          </div>
        </div>

        <div className="rack-cabinet">
          {currentStation.slots.map(slot => {
            const isFault = slot.status === 'FAULT';
            const isDerate = slot.status === 'THERMAL_DERATE';
            const isReady = slot.status === 'READY_FOR_SWAP';
            const isCharging = slot.status === 'CHARGING';

            return (
              <div
                key={slot.slot}
                className={`dock-slot-card ${isFault ? 'has-fault' : ''}`}
                style={{
                  backgroundColor: isFault ? 'var(--system-red-subtle)' : isDerate ? 'var(--system-amber-subtle)' : '#ffffff'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 700, fontSize: '13px', color: 'var(--text-primary)' }}>
                    Bay 0{slot.slot}
                  </span>
                  <span className={`badge ${isFault ? 'badge-red' : isDerate ? 'badge-amber' : isReady ? 'badge-green' : isCharging ? 'badge-blue' : 'badge-gray'}`}>
                    {slot.status}
                  </span>
                </div>

                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                  Pack: <strong style={{ color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>{slot.packId}</strong>
                </div>

                <div style={{ marginTop: '6px', display: 'flex', flexDirection: 'column', gap: '3px', fontSize: '11px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Current:</span>
                    <strong style={{ fontFamily: 'var(--font-mono)' }}>{slot.currentA.toFixed(1)} A</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Contact R:</span>
                    <strong style={{ color: slot.contactResMOhms > 30 ? 'var(--system-red)' : 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>
                      {slot.contactResMOhms.toFixed(1)} mΩ
                    </strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Bay Temp:</span>
                    <strong style={{ fontFamily: 'var(--font-mono)' }}>{slot.tempC.toFixed(1)}°C</strong>
                  </div>
                </div>

                {isFault && (
                  <div style={{ marginTop: '4px', fontSize: '10px', color: 'var(--system-red)', fontWeight: 600 }}>
                    ⚠️ {slot.faultName || 'Contact Resistance Spike'}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
