import React, { useEffect } from 'react';
import { CheckCircle2, Info, AlertTriangle, X } from 'lucide-react';

export default function Toast({ toasts, onDismiss }) {
  if (!toasts || toasts.length === 0) return null;

  return (
    <div className="toast-container" role="region" aria-label="Notifications">
      {toasts.map(toast => {
        const Icon = toast.type === 'success' 
          ? CheckCircle2 
          : toast.type === 'warning' 
          ? AlertTriangle 
          : Info;
        
        const typeClass = toast.type === 'success' 
          ? 'toast-success' 
          : toast.type === 'warning' 
          ? 'toast-warning' 
          : 'toast-info';

        const iconColor = toast.type === 'success' 
          ? 'var(--system-green)' 
          : toast.type === 'warning' 
          ? 'var(--system-amber)' 
          : 'var(--system-blue)';

        return (
          <div
            key={toast.id}
            className={`toast ${typeClass}`}
            role="status"
            aria-live="polite"
          >
            <Icon size={16} color={iconColor} style={{ flexShrink: 0 }} />
            <div style={{ flex: 1 }}>{toast.message}</div>
            <button
              type="button"
              onClick={() => onDismiss(toast.id)}
              style={{
                background: 'none',
                border: 'none',
                padding: '2px',
                cursor: 'pointer',
                color: 'var(--text-muted)',
                display: 'flex',
                alignItems: 'center'
              }}
              aria-label="Dismiss notification"
            >
              <X size={14} />
            </button>
          </div>
        );
      })}
    </div>
  );
}
