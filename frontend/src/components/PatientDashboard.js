import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { Heart, Activity, Thermometer, User, Clock, Flame, Footprints, Moon, AlertOctagon } from 'lucide-react';
import Card from './ui/Card';
import StatCard from './ui/StatCard';
import SymptomChatbot from './SymptomChatbot';
import PrescriptionScanner from './PrescriptionScanner';

const PatientDashboard = ({ user, vitals, healthScore, alerts, historicalData, onVitalsUpdate }) => {
  const [riskHistory, setRiskHistory] = React.useState([]);
  const [modelStatus, setModelStatus] = React.useState(null);

  React.useEffect(() => {
    // Fetch Deterioration Risk History
    const fetchRiskHistory = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/ml/deterioration-history/${user.id}?limit=7`);
        if (res.ok) {
          const data = await res.json();
          const formatted = data.predictions.map(p => ({
            date: new Date(p.prediction_time).toLocaleDateString(undefined, { weekday: 'short' }),
            risk: p.risk_score * 100 // Convert to percentage
          })).reverse();
          setRiskHistory(formatted);

          if (data.predictions.length > 0) {
            setModelStatus(data.predictions[0].model_trained);
          }
        }
      } catch (e) {
        console.error("Failed to fetch risk history", e);
      }
    };

    fetchRiskHistory();
  }, [user.id]);

  return (
    <div className="space-y-6 animate-fade-in pb-10">
      {/* Symptom Chatbot & Prescription Scanner */}
      <div className="flex gap-4">
        <SymptomChatbot user={user} onVitalsUpdate={onVitalsUpdate} />
        <PrescriptionScanner userId={user.id} />
      </div>

      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          title="Heart Rate"
          value={`${vitals.heartRate} bpm`}
          icon={Heart}
          color="rose"
          trend="+2%"
          trendUp={true}
          subtitle="Normal resting rate"
        />
        <StatCard
          title="Blood Oxygen"
          value={`${vitals.spo2}%`}
          icon={Activity}
          color="cyan"
          trend="Stable"
          subtitle="Optimal saturation"
        />
        <StatCard
          title="Temperature"
          value={`${vitals.temperature}°C`}
          icon={Thermometer}
          color="amber"
          trend="-0.1"
          subtitle="Body temperature"
        />
        <StatCard
          title="Stress Level"
          value={vitals.stress <= 3 ? "Low" : "Moderate"}
          icon={User}
          color="violet"
          trend="Improving"
          trendUp={false}
          subtitle="Daily average"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Chart Section */}
        <div className="lg:col-span-2 space-y-6">
          {/* Heart Rate Chart */}
          <Card className="glass-card h-[400px]">
            {/* ... existing chart code ... */}
            <div className="flex justify-between items-center mb-6">
              <div>
                <h3 className="text-xl font-bold text-white">Heart Rate History</h3>
                <p className="text-sm text-gray-400">Real-time continuous monitoring (Last 20 readings)</p>
              </div>
              {/* ... buttons ... */}
            </div>
            {/* ... responsive container ... */}
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={historicalData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                  <XAxis dataKey="time" stroke="#666" style={{ fontSize: '12px' }} />
                  <YAxis stroke="#666" style={{ fontSize: '12px' }} />
                  <Tooltip contentStyle={{ backgroundColor: '#fff', border: '1px solid #ddd', borderRadius: '8px' }} />
                  <Line type="monotone" dataKey="heartRate" stroke="#ff0000" strokeWidth={4} dot={{ r: 5 }} name="Heart Rate" />
                  <Line type="monotone" dataKey="spo2" stroke="#0066ff" strokeWidth={4} dot={{ r: 5 }} name="SpO2" />
                  <Line type="monotone" dataKey="temperature" stroke="#ff9900" strokeWidth={4} dot={{ r: 5 }} name="Temperature" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>

          {/* New Deterioration Risk Trend Chart */}
          <Card className="glass-card h-[350px]">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  <Activity className="text-purple-400" />
                  AI Deterioration Risk Trend
                  {modelStatus !== null && (
                    <span className={`text-[10px] px-2 py-0.5 rounded-full border ${modelStatus
                      ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                      : 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400'
                      }`}>
                      {modelStatus ? 'Model: Trained (v1.0)' : 'Model: Untrained'}
                    </span>
                  )}
                </h3>
                <p className="text-sm text-gray-400">7-Day Multi-Modal Temporal Fusion Analysis</p>
              </div>
            </div>

            <div className="h-[250px] w-full">
              <ResponsiveContainer width="100%" height={250}>
                <AreaChart data={riskHistory}>
                  <defs>
                    <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#8884d8" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="date" stroke="#9ca3af" style={{ fontSize: '12px' }} />
                  <YAxis stroke="#9ca3af" style={{ fontSize: '12px' }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '8px', color: '#fff' }}
                    labelStyle={{ color: '#9ca3af' }}
                  />
                  <Area type="monotone" dataKey="risk" stroke="#8884d8" fillOpacity={1} fill="url(#colorRisk)" name="Risk Score (%)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="glass-card flex items-center gap-4 transition-transform hover:-translate-y-1">
              <div className="p-3 bg-purple-500/20 rounded-full text-purple-400">
                <Footprints size={24} />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Steps</p>
                <p className="text-2xl font-bold text-white">{vitals.steps}</p>
              </div>
            </Card>
            <Card className="glass-card flex items-center gap-4 transition-transform hover:-translate-y-1">
              <div className="p-3 bg-orange-500/20 rounded-full text-orange-400">
                <Flame size={24} />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Calories</p>
                <p className="text-2xl font-bold text-white">{vitals.calories}</p>
              </div>
            </Card>
            <Card className="glass-card flex items-center gap-4 transition-transform hover:-translate-y-1">
              <div className="p-3 bg-indigo-500/20 rounded-full text-indigo-400">
                <Moon size={24} />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Sleep</p>
                <p className="text-2xl font-bold text-white">{vitals.sleepHours}h</p>
              </div>
            </Card>
          </div>
        </div>

        {/* Right Sidebar: Health Score & Alerts */}
        <div className="space-y-6">
          {/* Health Score Circle */}
          <Card className="glass-card text-center relative overflow-hidden bg-gradient-to-b from-gray-800/80 to-gray-900/80 border-gray-700">
            <h3 className="text-lg font-bold text-gray-200 mb-6">Overall Health Score</h3>
            <div className="relative w-48 h-48 mx-auto mb-4 flex items-center justify-center">
              {/* SVG Progress Circle would go here, simpler div for now */}
              <div className={`w-full h-full rounded-full border-[12px] ${healthScore > 80 ? 'border-emerald-500/20' : 'border-yellow-500/20'} flex items-center justify-center relative`}>
                <div className={`absolute inset-0 rounded-full border-[12px] ${healthScore > 80 ? 'border-emerald-500' : 'border-yellow-500'} border-t-transparent animate-spin-slow`} style={{ transform: `rotate(${healthScore * 3.6}deg)` }}></div>
                <div className="text-center z-10">
                  <span className={`text-5xl font-bold ${healthScore > 80 ? 'text-emerald-400' : 'text-yellow-400'}`}>{healthScore}</span>
                  <p className="text-gray-400 text-sm mt-1">/ 100</p>
                </div>
              </div>
              <div className="absolute inset-0 rounded-full bg-emerald-500/5 blur-xl"></div>
            </div>
            <p className="text-sm text-gray-400 leading-relaxed">
              Your vitals are currently <span className="text-emerald-400 font-bold">optimal</span>. Keep up the good work!
            </p>
          </Card>

          {/* Alerts Section */}
          <div>
            <h3 className="text-white font-bold mb-4 flex items-center gap-2">
              <AlertOctagon size={18} className="text-amber-400" />
              Recent Alerts
            </h3>
            <div className="space-y-3">
              {alerts.length > 0 ? alerts.map(alert => (
                <div key={alert.id} className="bg-red-500/10 border border-red-500/20 p-4 rounded-xl flex items-start gap-3 backdrop-blur-md">
                  <div className="bg-red-500/20 p-2 rounded-lg text-red-400 mt-1">
                    <AlertOctagon size={16} />
                  </div>
                  <div>
                    <h4 className="font-bold text-red-200 text-sm">{alert.title}</h4>
                    <p className="text-xs text-red-300/80 mt-1 leading-relaxed">{alert.message}</p>
                    <p className="text-[10px] text-red-400/60 mt-2 font-mono uppercase tracking-widest">{alert.time}</p>
                  </div>
                </div>
              )) : (
                <div className="bg-emerald-500/10 border border-emerald-500/20 p-6 rounded-xl text-center">
                  <p className="text-emerald-400 font-medium">No active alerts</p>
                  <p className="text-xs text-emerald-500/60 mt-1">System monitoring active</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PatientDashboard;