// ============================================================================
// FILE: frontend/src/components/VitalsCard.js
// Vital Signs Display Card Component
// ============================================================================

import React from 'react';
import { Heart, Droplet, Activity, TrendingUp } from 'lucide-react';

const VitalsCard = ({ title, value, unit, icon: Icon, color, trend }) => {
  const colorClasses = {
    red: 'from-red-500/20 to-red-600/10 text-red-100 border border-red-500/20',
    blue: 'from-blue-500/20 to-blue-600/10 text-blue-100 border border-blue-500/20',
    orange: 'from-orange-500/20 to-orange-600/10 text-orange-100 border border-orange-500/20',
    purple: 'from-purple-500/20 to-purple-600/10 text-purple-100 border border-purple-500/20',
    green: 'from-emerald-500/20 to-emerald-600/10 text-emerald-100 border border-emerald-500/20',
  };

  return (
    <div className={`glass-card bg-gradient-to-br ${colorClasses[color]} p-4 rounded-xl shadow hover:shadow-lg transition-all`}>
      <div className="flex items-center justify-between">
        <Icon size={32} />
        <span className="text-2xl font-bold">
          {typeof value === 'number' ? value.toFixed(1) : value}
        </span>
      </div>
      <p className="text-sm text-gray-300 mt-2">{title}</p>
      {unit && <p className="text-xs text-gray-400">{unit}</p>}
      {trend && (
        <div className="flex items-center mt-1 text-xs">
          <TrendingUp size={12} className="mr-1" />
          <span>{trend}</span>
        </div>
      )}
    </div>
  );
};

export default VitalsCard;


// ============================================================================
// FILE: frontend/src/components/AlertPanel.js
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


// ============================================================================
// FILE: frontend/src/components/Charts.js
// Chart Components for Data Visualization
// ============================================================================

import React from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

export const HeartRateChart = ({ data }) => (
  <div className="bg-white p-6 rounded-lg shadow">
    <h3 className="text-lg font-semibold mb-4">Heart Rate Trend</h3>
    <ResponsiveContainer width="100%" height={250}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="time" tick={{ fontSize: 10 }} />
        <YAxis domain={[40, 120]} />
        <Tooltip />
        <Legend />
        <Line
          type="monotone"
          dataKey="hr"
          stroke="#ef4444"
          strokeWidth={2}
          dot={false}
          name="Heart Rate (bpm)"
        />
      </LineChart>
    </ResponsiveContainer>
  </div>
);

export const SpO2Chart = ({ data }) => (
  <div className="bg-white p-6 rounded-lg shadow">
    <h3 className="text-lg font-semibold mb-4">Blood Oxygen Levels</h3>
    <ResponsiveContainer width="100%" height={250}>
      <AreaChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="time" tick={{ fontSize: 10 }} />
        <YAxis domain={[85, 100]} />
        <Tooltip />
        <Legend />
        <Area
          type="monotone"
          dataKey="spo2"
          stroke="#3b82f6"
          fill="#93c5fd"
          name="SpO2 (%)"
        />
      </AreaChart>
    </ResponsiveContainer>
  </div>
);

export const TemperatureChart = ({ data }) => (
  <div className="bg-white p-6 rounded-lg shadow">
    <h3 className="text-lg font-semibold mb-4">Temperature</h3>
    <ResponsiveContainer width="100%" height={250}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="time" tick={{ fontSize: 10 }} />
        <YAxis domain={[35, 40]} />
        <Tooltip />
        <Legend />
        <Line
          type="monotone"
          dataKey="temp"
          stroke="#f97316"
          strokeWidth={2}
          dot={false}
          name="Temperature (°C)"
        />
      </LineChart>
    </ResponsiveContainer>
  </div>
);

export const StressChart = ({ data }) => (
  <div className="bg-white p-6 rounded-lg shadow">
    <h3 className="text-lg font-semibold mb-4">Stress Level</h3>
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="time" tick={{ fontSize: 10 }} />
        <YAxis domain={[0, 5]} />
        <Tooltip />
        <Legend />
        <Bar dataKey="stress" fill="#a855f7" name="Stress (0-5)" />
      </BarChart>
    </ResponsiveContainer>
  </div>
);


// ============================================================================
// FILE: frontend/src/components/PatientDashboard.js
// Patient Dashboard Component
// ============================================================================

import React from 'react';
import VitalsCard from './VitalsCard';
import AlertPanel from './AlertPanel';
import { HeartRateChart, SpO2Chart } from './Charts';
import { Heart, Droplet, Activity, TrendingUp, Moon } from 'lucide-react';

const PatientDashboard = ({
  vitals,
  healthScore,
  alerts,
  historicalData,
  currentUser,
  onDismissAlert
}) => {
  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Health Dashboard</h1>
          <p className="text-gray-600">Welcome back, {currentUser.name}</p>
        </div>
        <div className={`text-4xl font-bold ${getScoreColor(healthScore)}`}>
          {healthScore}/100
          <p className="text-sm text-gray-600">Health Score</p>
        </div>
      </div>

      {/* Real-time Vitals Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <VitalsCard
          title="Heart Rate"
          value={vitals.heartRate}
          unit="bpm"
          icon={Heart}
          color="red"
        />
        <VitalsCard
          title="Blood Oxygen"
          value={vitals.spo2}
          unit="%"
          icon={Droplet}
          color="blue"
        />
        <VitalsCard
          title="Temperature"
          value={vitals.temperature}
          unit="°C"
          icon={Activity}
          color="orange"
        />
        <VitalsCard
          title="Stress Level"
          value={vitals.stress}
          unit="/5"
          icon={TrendingUp}
          color="purple"
        />
      </div>

      {/* Activity Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-green-500">
          <p className="text-gray-600 text-sm">Steps Today</p>
          <p className="text-3xl font-bold text-gray-800">{vitals.steps.toLocaleString()}</p>
          <p className="text-xs text-green-600 mt-1">Target: 10,000</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-orange-500">
          <p className="text-gray-600 text-sm">Calories Burned</p>
          <p className="text-3xl font-bold text-gray-800">{vitals.calories}</p>
          <p className="text-xs text-orange-600 mt-1">Target: 2,200</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-indigo-500">
          <p className="text-gray-600 text-sm">Sleep Last Night</p>
          <p className="text-3xl font-bold text-gray-800">{vitals.sleepHours}h</p>
          <p className="text-xs text-indigo-600 mt-1">Target: 7-9h</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <HeartRateChart data={historicalData} />
        <SpO2Chart data={historicalData} />
      </div>

      {/* Alerts Panel */}
      <AlertPanel alerts={alerts} onDismiss={onDismissAlert} />
    </div>
  );
};

export default PatientDashboard;


// ============================================================================
// FILE: frontend/src/components/HospitalDashboard.js
// Hospital Dashboard Component
// ============================================================================

import React, { useState } from 'react';
import { User, Download, AlertCircle } from 'lucide-react';

const HospitalDashboard = ({ patients, onViewPatient }) => {
  const [sortBy, setSortBy] = useState('status');

  const getRiskColor = (risk) => {
    if (risk === 'low') return 'bg-green-100 text-green-800';
    if (risk === 'medium') return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const getStatusColor = (status) => {
    if (status === 'stable') return 'text-green-600';
    if (status === 'warning') return 'text-yellow-600';
    return 'text-red-600';
  };

  const sortedPatients = [...patients].sort((a, b) => {
    const statusPriority = { critical: 0, warning: 1, stable: 2 };
    return statusPriority[a.status] - statusPriority[b.status];
  });

  const criticalPatients = patients.filter(p => p.status === 'critical' || p.status === 'warning');

  return (
    <div className="space-y-6 fade-in">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Hospital Monitoring</h1>
          <p className="text-gray-600">Real-time patient monitoring system</p>
        </div>
        <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
          <Download size={20} />
          Export Report
        </button>
      </div>

      {/* Priority Alerts */}
      {criticalPatients.length > 0 && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="text-red-600" />
            <h3 className="font-semibold text-red-800">High Priority Patients</h3>
          </div>
          <div className="flex gap-4 overflow-x-auto">
            {criticalPatients.map(p => (
              <div key={p.id} className="bg-white px-4 py-2 rounded shadow min-w-max">
                <p className="font-semibold">{p.name}</p>
                <p className="text-xs text-gray-600">HR: {p.hr} | SpO2: {p.spo2}%</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Patient List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Patient</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Age</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Heart Rate</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">SpO2</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Risk Level</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {sortedPatients.map(patient => (
              <tr key={patient.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <User className="text-gray-400" size={20} />
                    <span className="font-medium">{patient.name}</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-gray-600">{patient.age}</td>
                <td className="px-6 py-4">
                  <span className={patient.hr > 100 || patient.hr < 60 ? 'text-red-600 font-semibold' : ''}>
                    {patient.hr} bpm
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className={patient.spo2 < 95 ? 'text-red-600 font-semibold' : ''}>
                    {patient.spo2}%
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(patient.risk)}`}>
                    {patient.risk.toUpperCase()}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className={`font-semibold ${getStatusColor(patient.status)}`}>
                    {patient.status.toUpperCase()}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <button
                    onClick={() => onViewPatient(patient)}
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    View Details
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default HospitalDashboard;