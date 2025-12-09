// ============================================================================
// FILE: frontend/src/components/alertpanel.js
// Alert Notifications Panel Component
// ============================================================================

import React from 'react';
import { Bell, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';

const AlertPanel = ({ alerts, onDismiss }) => {
  const getAlertIcon = (type) => {
    switch (type) {
      case 'critical':
        return <AlertCircle className="text-red-600" size={20} />;
      case 'danger':
        return <AlertTriangle className="text-orange-600" size={20} />;
      case 'warning':
        return <AlertTriangle className="text-yellow-600" size={20} />;
      default:
        return <Info className="text-blue-600" size={20} />;
    }
  };

  const getAlertColor = (type) => {
    switch (type) {
      case 'critical':
        return 'bg-red-50 border-red-500';
      case 'danger':
        return 'bg-orange-50 border-orange-500';
      case 'warning':
        return 'bg-yellow-50 border-yellow-500';
      default:
        return 'bg-blue-50 border-blue-500';
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-center gap-2 mb-4">
        <Bell className="text-red-600" />
        <h3 className="text-lg font-semibold">Recent Alerts</h3>
        {alerts.length > 0 && (
          <span className="ml-auto bg-red-600 text-white text-xs px-2 py-1 rounded-full">
            {alerts.length}
          </span>
        )}
      </div>
      
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {alerts.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Bell size={48} className="mx-auto mb-2 opacity-20" />
            <p>No alerts. All vitals are normal!</p>
          </div>
        ) : (
          alerts.map((alert, index) => (
            <div
              key={alert.id || index}
              className={`p-3 rounded-lg border-l-4 ${getAlertColor(alert.type)} fade-in`}
            >
              <div className="flex justify-between items-start">
                <div className="flex gap-2 flex-1">
                  {getAlertIcon(alert.type)}
                  <div className="flex-1">
                    <p className="font-semibold text-sm">{alert.title}</p>
                    <p className="text-xs text-gray-600 mt-1">{alert.message}</p>
                    <p className="text-xs text-gray-500 mt-1">{alert.time}</p>
                  </div>
                </div>
                {onDismiss && (
                  <button
                    onClick={() => onDismiss(index)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X size={16} />
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AlertPanel;