// ============================================================================
// FILE: frontend/src/components/hospitaldashboard.js
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
                    onClick={() => onViewPatient && onViewPatient(patient)}
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