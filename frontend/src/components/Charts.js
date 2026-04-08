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
          stroke="#ff0000"
          strokeWidth={4}
          dot={{ r: 4 }}
          name="Heart Rate (bpm)"
        />
      </LineChart>
    </ResponsiveContainer>
  </div>
);

export const SpO2Chart = ({ data }) => (
  <div className="chart-container">
    <h3>SpO2 Levels</h3>
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="time" />
        <YAxis domain={[90, 100]} />
        <Tooltip />
        <Line
          type="monotone"
          dataKey="spo2"
          stroke="#00cc00" // Changed color for better visibility
          strokeWidth={4} // Increased stroke width
          dot={{ r: 5 }} // Increased dot size
        />
      </LineChart>
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
          stroke="#ff6600"
          strokeWidth={4}
          dot={{ r: 4 }}
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