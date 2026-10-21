import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import InspectorDrawer from './components/InspectorDrawer';
import Toast from './components/Toast';

import FleetOverviewView from './views/FleetOverviewView';
import AlertsTriageView from './views/AlertsTriageView';
import WaveformStudioView from './views/WaveformStudioView';
import PackDiagnosticsView from './views/PackDiagnosticsView';
import StationCabinetsView from './views/StationCabinetsView';
import AttributionEngineView from './views/AttributionEngineView';
import ReviewerDefenseView from './views/ReviewerDefenseView';

import telemetryData from './data/telemetryData';

export default function App() {
  const [currentView, setCurrentView] = useState('overview');
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [alertsState, setAlertsState] = useState(telemetryData.alerts || []);
  const [toasts, setToasts] = useState([]);

  const addToast = (message, type = 'info') => {
    const id = Date.now() + Math.random().toString(36).substring(2, 6);
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 4000);
  };

  const handleDismissToast = (id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

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
    addToast(`Alert ${alertId} status marked as ACKNOWLEDGED.`, 'warning');
  };

  const handleResolve = (alertId) => {
    setAlertsState(prev => prev.map(a => 
      a.alert_id === alertId ? { ...a, status: 'RESOLVED' } : a
    ));
    if (selectedAlert && selectedAlert.alert_id === alertId) {
      setSelectedAlert(prev => ({ ...prev, status: 'RESOLVED' }));
    }
    addToast(`Alert ${alertId} successfully marked as RESOLVED.`, 'success');
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
    addToast('Audit evidence bundle exported as JSON.', 'success');
  };

  const handleSearchChange = (val) => {
    setSearchQuery(val);
    if (val.trim() && currentView !== 'alerts' && currentView !== 'defense') {
      setCurrentView('alerts');
    }
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
      case 'defense':
        return <ReviewerDefenseView />;
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
          onSearchChange={handleSearchChange}
          onExportData={handleExportData}
          onRefresh={() => {
            addToast('Telemetry snapshot synchronized with live stream (1,937 sessions).', 'info');
          }}
          onNavigate={setCurrentView}
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

      {/* Apple HIG Toast Region */}
      <Toast toasts={toasts} onDismiss={handleDismissToast} />
    </div>
  );
}
