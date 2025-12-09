// ============================================================================
// FILE: frontend/src/components/charts.js
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

export default {
  HeartRateChart,
  SpO2Chart,
  TemperatureChart,
  StressChart
};