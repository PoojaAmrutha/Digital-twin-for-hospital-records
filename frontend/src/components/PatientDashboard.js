import React from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { Heart, Activity, Thermometer, User, Clock, Flame, Footprints, Moon, AlertOctagon } from 'lucide-react';
import Card from './ui/Card';
import StatCard from './ui/StatCard';
import SymptomChatbot from './SymptomChatbot';

const PatientDashboard = ({ user, vitals, healthScore, alerts, historicalData, onVitalsUpdate }) => {
  return (
    <div className="space-y-6 animate-fade-in pb-10">
      {/* Symptom Chatbot */}
      <SymptomChatbot user={user} onVitalsUpdate={onVitalsUpdate} />

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
          <Card className="h-[400px]">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h3 className="text-xl font-bold text-white">Heart Rate History</h3>
                <p className="text-sm text-gray-400">Real-time continuous monitoring (Last 20 readings)</p>
              </div>
              <div className="flex gap-2">
                {['1H', '24H', '1W'].map(p => (
                  <button key={p} className="px-3 py-1 text-xs font-medium rounded-lg bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700 transition-colors">
                    {p}
                  </button>
                ))}
              </div>
            </div>

            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={historicalData}>
                  <defs>
                    <linearGradient id="colorHr" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis
                    dataKey="time"
                    stroke="#475569"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis
                    stroke="#475569"
                    fontSize={12}
                    domain={['dataMin - 10', 'dataMax + 10']}
                    tickLine={false}
                    axisLine={false}
                  />
                  <Tooltip
                    contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', borderRadius: '12px', border: '1px solid #334155', color: '#fff' }}
                    itemStyle={{ color: '#fff' }}
                  />
                  <Area
                    type="monotone"
                    dataKey="hr"
                    stroke="#f43f5e"
                    strokeWidth={3}
                    fillOpacity={1}
                    fill="url(#colorHr)"
                    animationDuration={1000}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="flex items-center gap-4 bg-gray-900/60 transition-transform hover:-translate-y-1">
              <div className="p-3 bg-purple-500/20 rounded-full text-purple-400">
                <Footprints size={24} />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Steps</p>
                <p className="text-2xl font-bold text-white">{vitals.steps}</p>
              </div>
            </Card>
            <Card className="flex items-center gap-4 bg-gray-900/60 transition-transform hover:-translate-y-1">
              <div className="p-3 bg-orange-500/20 rounded-full text-orange-400">
                <Flame size={24} />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Calories</p>
                <p className="text-2xl font-bold text-white">{vitals.calories}</p>
              </div>
            </Card>
            <Card className="flex items-center gap-4 bg-gray-900/60 transition-transform hover:-translate-y-1">
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
          <Card className="text-center relative overflow-hidden bg-gradient-to-b from-gray-800/80 to-gray-900/80 border-gray-700">
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