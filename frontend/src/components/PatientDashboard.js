// ============================================================================
// FILE: frontend/src/components/patientdashboard.js
// Patient Dashboard Component
// ============================================================================

import React from 'react';
import { Heart, Droplet, Activity, TrendingUp } from 'lucide-react';

const VitalsCard = ({ title, value, unit, icon: Icon, color }) => {
  const colorClasses = {
    red: 'from-red-50 to-red-100 text-red-700',
    blue: 'from-blue-50 to-blue-100 text-blue-700',
    orange: 'from-orange-50 to-orange-100 text-orange-700',
    purple: 'from-purple-50 to-purple-100 text-purple-700',
  };

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color]} p-4 rounded-lg shadow`}>
      <div className="flex items-center justify-between">
        <Icon size={32} />
        <span className="text-2xl font-bold">
          {typeof value === 'number' ? value.toFixed(1) : value}
        </span>
      </div>
      <p className="text-sm text-gray-600 mt-2">{title}</p>
      {unit && <p className="text-xs text-gray-500">{unit}</p>}
    </div>
  );
};

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
    </div>
  );
};

export default PatientDashboard;