import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import InspectorDrawer from './components/InspectorDrawer';

import FleetOverviewView from './views/FleetOverviewView';
import AlertsTriageView from './views/AlertsTriageView';
import WaveformStudioView from './views/WaveformStudioView';
import PackDiagnosticsView from './views/PackDiagnosticsView';
import StationCabinetsView from './views/StationCabinetsView';
import AttributionEngineView from './views/AttributionEngineView';

import telemetryData from './data/telemetryData';

export default function App() {
  const [currentView, setCurrentView] = useState('overview');
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [alertsState, setAlertsState] = useState(telemetryData.alerts || []);

  const handleSelectAlert = (alert) => {
    setSelectedAlert(alert);
  };

  const handleCloseDrawer = () => {
    setSelectedAlert(null);
  };

  const handleAcknowledge = (alertId) => {
    setAlertsState(prev => prev.map(a => 
      a.alert_id === alertId ? { ...a, status: 'ACKNOWLEDGED' } : a
    ));
    if (selectedAlert && selectedAlert.alert_id === alertId) {
      setSelectedAlert(prev => ({ ...prev, status: 'ACKNOWLEDGED' }));
    }
  };

  const handleResolve = (alertId) => {
    setAlertsState(prev => prev.map(a => 
      a.alert_id === alertId ? { ...a, status: 'RESOLVED' } : a
    ));
    if (selectedAlert && selectedAlert.alert_id === alertId) {
      setSelectedAlert(prev => ({ ...prev, status: 'RESOLVED' }));
    }
  };

  const handleExportData = () => {
    const jsonBlob = new Blob([JSON.stringify(telemetryData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(jsonBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `swaptrace_evidence_bundle_${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const currentDataset = {
    ...telemetryData,
    alerts: alertsState,
  };

  const renderActiveView = () => {
    switch (currentView) {
      case 'overview':
        return (
          <FleetOverviewView
            data={currentDataset}
            onSelectAlert={handleSelectAlert}
            onNavigate={(view) => setCurrentView(view)}
          />
        );
      case 'alerts':
        return (
          <AlertsTriageView
            data={currentDataset}
            onSelectAlert={handleSelectAlert}
            searchQuery={searchQuery}
          />
        );
      case 'waveforms':
        return <WaveformStudioView data={currentDataset} />;
      case 'packs':
        return <PackDiagnosticsView />;
      case 'stations':
        return <StationCabinetsView data={currentDataset} />;
      case 'attribution':
        return <AttributionEngineView data={currentDataset} />;
      default:
        return (
          <FleetOverviewView
            data={currentDataset}
            onSelectAlert={handleSelectAlert}
            onNavigate={(view) => setCurrentView(view)}
          />
        );
    }
  };

  return (
    <div className="app-container">
      {/* Apple HIG Sidebar */}
      <Sidebar
        currentView={currentView}
        onViewChange={(v) => {
          setCurrentView(v);
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }}
        alertCount={alertsState.filter(a => a.status !== 'RESOLVED').length}
      />

      {/* Main App Content Area */}
      <div className="main-wrapper">
        <Header
          currentView={currentView}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          onExportData={handleExportData}
          onRefresh={() => {
            alert('Telemetry snapshot synchronized with live stream.');
          }}
        />

        <main role="main">
          {renderActiveView()}
        </main>
      </div>

      {/* Slide-over Inspection Sheet */}
      {selectedAlert && (
        <InspectorDrawer
          item={selectedAlert}
          onClose={handleCloseDrawer}
          onAcknowledge={handleAcknowledge}
          onResolve={handleResolve}
        />
      )}
    </div>
  );
}
