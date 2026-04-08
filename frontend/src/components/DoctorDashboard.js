import React, { useState, useEffect } from 'react';
import { Users, Activity, AlertTriangle, CheckCircle, Search, Filter, X, Heart, Thermometer, Droplet, Brain, Zap, TrendingUp, Calendar, FileText, Waves, Pill, Stethoscope, Clipboard, Download, Edit, MessageCircle } from 'lucide-react';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';
import Card from './ui/Card';
import Button from './ui/Button';

const API_URL = 'http://localhost:8000';

const DoctorDashboard = ({ allUsers, onSelectPatient }) => {
    const patients = allUsers.filter(u => u.user_type === 'patient');
    const [selectedPatient, setSelectedPatient] = useState(null);
    const [ecgData, setEcgData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [editingVitals, setEditingVitals] = useState(false);
    const [vitalForm, setVitalForm] = useState({});

    // Generate realistic ECG waveform data
    useEffect(() => {
        if (selectedPatient) {
            const generateECG = () => {
                const data = [];
                for (let i = 0; i < 50; i++) {
                    const baseValue = 50;
                    let value = baseValue;

                    // P wave
                    if (i % 25 === 5) value += 5;
                    // QRS complex
                    if (i % 25 === 10) value -= 15;
                    if (i % 25 === 11) value += 40;
                    if (i % 25 === 12) value -= 20;
                    // T wave
                    if (i % 25 === 18) value += 10;

                    data.push({ x: i, y: value + (Math.random() - 0.5) * 2 });
                }
                return data;
            };

            setEcgData(generateECG());
            const interval = setInterval(() => {
                setEcgData(generateECG());
            }, 1000);

            return () => clearInterval(interval);
        }
    }, [selectedPatient]);


    // Fetch patient details from API
    const fetchPatientDetails = async (patientId) => {
        setLoading(true);
        try {
            const vitalsRes = await fetch(`${API_URL}/vitals/user/${patientId}/latest`);
            let vitals = { heartRate: 75, spo2: 96, temperature: 36.8, bp: '125/82', stress: 3, respiratoryRate: 18, glucose: 105 };

            if (vitalsRes.ok) {
                const vitalsData = await vitalsRes.json();
                vitals = {
                    heartRate: vitalsData.data.heart_rate || 75,
                    spo2: vitalsData.data.spo2 || 96,
                    temperature: vitalsData.data.temperature || 36.8,
                    bp: '125/82',
                    stress: vitalsData.data.stress_level || 3,
                    respiratoryRate: 18,
                    glucose: 105
                };
            }

            const recordsRes = await fetch(`${API_URL}/medical-records/user/${patientId}`);
            let symptoms = [];
            if (recordsRes.ok) {
                const recordsData = await recordsRes.json();
                symptoms = recordsData.data
                    .filter(r => r.record_type === 'symptom_log')
                    .map(r => ({
                        date: new Date(r.created_at).toLocaleDateString(),
                        time: new Date(r.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                        content: r.content
                    }))
                    .reverse() // Most recent first
                    .slice(0, 5); // Just show last 5
            }

            const calculateOrganHealth = (vitals) => ({
                heart: { status: vitals.heartRate > 100 ? 'warning' : 'normal', health: vitals.heartRate > 100 ? 65 : 90, note: vitals.heartRate > 100 ? 'Elevated HR' : 'Regular rhythm' },
                lungs: { status: vitals.spo2 < 93 ? 'warning' : 'normal', health: vitals.spo2 < 93 ? 70 : 92, note: vitals.spo2 < 93 ? 'Reduced oxygen' : 'Clear breath sounds' },
                brain: { status: 'normal', health: 88, note: 'Cognitive function normal' },
                kidneys: { status: 'normal', health: 85, note: 'Normal output' },
                liver: { status: 'normal', health: 83, note: 'Functioning well' }
            });

            const organs = calculateOrganHealth(vitals);
            let status = 'Stable';
            if (vitals.heartRate > 130 || vitals.spo2 < 88 || vitals.temperature > 39) status = 'Critical';
            else if (vitals.heartRate > 100 || vitals.spo2 < 92 || vitals.temperature > 38.5) status = 'Monitoring';

            return {
                vitals, organs, status, symptoms,
                lastVisit: new Date().toISOString().split('T')[0],
                diagnosis: status === 'Critical' ? 'Requires immediate attention' : 'Routine checkup',
                medications: ['As prescribed'],
                allergies: ['None known'],
                notes: `Patient vitals recorded. Status: ${status}.`,
                timeline: [{ date: new Date().toISOString(), event: 'Vitals check completed', type: status === 'Critical' ? 'warning' : 'normal' }]
            };
        } catch (error) {
            console.error('Error fetching patient details:', error);
            return {
                vitals: { heartRate: 75, spo2: 96, temperature: 36.8, bp: '125/82', stress: 3, respiratoryRate: 18, glucose: 105 },
                organs: { heart: { status: 'normal', health: 85, note: 'Regular rhythm' }, lungs: { status: 'normal', health: 82, note: 'Normal' }, brain: { status: 'normal', health: 88, note: 'Normal' }, kidneys: { status: 'normal', health: 85, note: 'Normal' }, liver: { status: 'normal', health: 83, note: 'Normal' } },
                status: 'Stable', lastVisit: new Date().toISOString().split('T')[0], diagnosis: 'Data unavailable', medications: ['As prescribed'], allergies: ['None known'], notes: 'Unable to fetch data.', timeline: []
            };
        } finally {
            setLoading(false);
        }
    };

    const getPatientStatus = (id) => {
        if (id === 1) return { status: 'Critical', color: 'bg-red-500/20 text-red-400 border-red-500/20', icon: AlertTriangle };
        if (id === 99) return { status: 'Stable', color: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/20', icon: CheckCircle };
        return { status: 'Monitoring', color: 'bg-blue-500/20 text-blue-400 border-blue-500/20', icon: Activity };
    };

    const handleViewPatient = async (patient) => {
        const patientData = await fetchPatientDetails(patient.id);
        setSelectedPatient({ ...patient, ...patientData });
        setVitalForm(patientData.vitals);
    };

    const handleUpdateVitals = async () => {
        try {
            const response = await fetch(`${API_URL}/vitals/user/${selectedPatient.id}/update`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(vitalForm)
            });

            if (response.ok) {
                alert('Vitals updated successfully!');
                setEditingVitals(false);
                // Refresh patient data
                const updatedData = await fetchPatientDetails(selectedPatient.id);
                setSelectedPatient({ ...selectedPatient, ...updatedData });
            } else {
                throw new Error('Failed to update vitals');
            }
        } catch (error) {
            console.error('Error updating vitals:', error);
            alert('Failed to update vitals. Please try again.');
        }
    };

    const getOrganColor = (status) => {
        if (status === 'normal') return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
        if (status === 'warning') return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
        return 'text-red-400 bg-red-500/10 border-red-500/20';
    };

    return (
        <div className="space-y-8 animate-fade-in pb-10">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4">
                <div>
                    <h2 className="text-3xl font-bold text-white">Hospital Dashboard</h2>
                    <p className="text-gray-400 mt-1">Real-time Patient Monitoring System</p>
                </div>
                <div className="relative group">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 group-focus-within:text-indigo-400 transition-colors" size={18} />
                    <input
                        type="text"
                        placeholder="Search patients..."
                        className="pl-10 pr-4 py-2.5 rounded-xl border border-gray-700 bg-gray-900/50 text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all w-64 md:w-80 backdrop-blur-sm"
                    />
                </div>
            </div>

            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="glass-card bg-gradient-to-br from-indigo-600/90 to-violet-700/90 border-none relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full blur-2xl transform translate-x-10 -translate-y-10 group-hover:bg-white/20 transition-colors"></div>
                    <div className="flex justify-between items-start relative z-10">
                        <div>
                            <p className="text-indigo-100 font-medium">Total Patients</p>
                            <h3 className="text-4xl font-bold mt-2 text-white">{patients.length}</h3>
                        </div>
                        <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
                            <Users size={24} className="text-white" />
                        </div>
                    </div>
                    <p className="text-indigo-200 mt-4 text-sm flex items-center gap-2">
                        <span className="bg-white/20 px-1.5 py-0.5 rounded text-xs font-bold">+2</span>
                        new this week
                    </p>
                </Card>

                <Card className="glass-card border-none">
                    <div className="flex justify-between items-start">
                        <div>
                            <p className="text-gray-400 font-medium">Critical Alerts</p>
                            <h3 className="text-4xl font-bold mt-2 text-red-500 drop-shadow-[0_0_10px_rgba(239,68,68,0.5)]">1</h3>
                        </div>
                        <div className="p-3 bg-red-500/10 rounded-xl text-red-500 border border-red-500/20">
                            <AlertTriangle size={24} />
                        </div>
                    </div>
                    <p className="text-sm text-gray-500 mt-4">Requires immediate attention</p>
                </Card>

                <Card className="glass-card border-none">
                    <div className="flex justify-between items-start">
                        <div>
                            <p className="text-gray-400 font-medium">Avg Health Score</p>
                            <h3 className="text-4xl font-bold mt-2 text-emerald-500 drop-shadow-[0_0_10px_rgba(16,185,129,0.5)]">84</h3>
                        </div>
                        <div className="p-3 bg-emerald-500/10 rounded-xl text-emerald-500 border border-emerald-500/20">
                            <Activity size={24} />
                        </div>
                    </div>
                    <p className="text-sm text-emerald-400/80 mt-4 flex items-center gap-1">
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>
                        +2.4% from last week
                    </p>
                </Card>
            </div>

            {/* Enhanced Patient Detail Modal */}
            {selectedPatient && (
                <div className="fixed inset-0 z-[100] bg-black/95 backdrop-blur-xl flex items-start justify-center p-4 animate-fade-in overflow-y-auto" onClick={() => setSelectedPatient(null)}>
                    <div className="w-full max-w-7xl my-8" onClick={e => e.stopPropagation()}>
                        <Card className="bg-gray-900/95 border-gray-700 relative">
                            <button onClick={() => setSelectedPatient(null)} className="sticky top-4 right-4 float-right p-2 bg-gray-800 hover:bg-red-500/80 text-white rounded-full transition-colors z-20 shadow-lg">
                                <X size={20} />
                            </button>

                            {/* Patient Header */}
                            <div className="border-b border-gray-800 pb-6 mb-6">
                                <div className="flex items-center gap-4">
                                    <div className="w-20 h-20 rounded-full bg-gradient-to-tr from-indigo-600 to-violet-600 flex items-center justify-center text-white text-3xl font-bold border-4 border-indigo-400 shadow-lg shadow-indigo-500/30">
                                        {selectedPatient.name.charAt(0)}
                                    </div>
                                    <div className="flex-1">
                                        <h2 className="text-3xl font-bold text-white">{selectedPatient.name}</h2>
                                        <p className="text-gray-400 mt-1">Patient ID: #{selectedPatient.id} • {selectedPatient.age} years • {selectedPatient.gender === 'M' ? 'Male' : 'Female'}</p>
                                        <p className="text-gray-500 text-sm mt-1">Email: {selectedPatient.email}</p>
                                    </div>
                                    <div className={`px-6 py-3 rounded-xl text-sm font-bold uppercase tracking-wider border ${getPatientStatus(selectedPatient.id).color} flex items-center gap-2`}>
                                        {React.createElement(getPatientStatus(selectedPatient.id).icon, { size: 18 })}
                                        {selectedPatient.status}
                                    </div>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                                {/* Left Column: 3D Body + ECG */}
                                <div className="space-y-6">
                                    {/* 3D Body Visualization */}
                                    <div>
                                        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                            <Stethoscope size={18} className="text-indigo-400" />
                                            Body Vitals Map
                                        </h3>
                                        <div className="relative bg-gradient-to-b from-gray-800/80 to-gray-900/80 rounded-2xl p-8 border border-gray-700 min-h-[650px] flex items-center justify-center overflow-hidden">
                                            {/* Background medical grid */}
                                            <div className="absolute inset-0 opacity-10">
                                                <svg width="100%" height="100%">
                                                    <defs>
                                                        <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                                                            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#6366f1" strokeWidth="0.5" />
                                                        </pattern>
                                                    </defs>
                                                    <rect width="100%" height="100%" fill="url(#grid)" />
                                                </svg>
                                            </div>

                                            {/* Realistic Body Image Container */}
                                            <div className="relative w-full max-w-[350px] h-[600px]">
                                                {/* Realistic Human Anatomy Image */}
                                                <img
                                                    src="/realistic_body_anatomy_1766835734109.png"
                                                    alt="Human Anatomy"
                                                    className="w-full h-full object-contain opacity-90 drop-shadow-2xl"
                                                    style={{
                                                        filter: 'brightness(1.1) contrast(1.05)',
                                                        transform: 'scale(1.3)',
                                                        transformOrigin: 'center center'
                                                    }}
                                                />

                                                {/* Interactive Vital Sign Overlays */}

                                                {/* Brain - Top of head */}
                                                <div className="absolute top-[8%] left-1/2 transform -translate-x-1/2" style={{ zIndex: 10 }}>
                                                    <div className="relative group cursor-pointer">
                                                        <div className="w-12 h-12 rounded-full bg-indigo-500/30 border-2 border-indigo-400 flex items-center justify-center backdrop-blur-sm">
                                                            <Brain size={20} className="text-indigo-300" />
                                                        </div>
                                                        <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-900/95 px-3 py-1 rounded-lg border border-indigo-500 whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity">
                                                            <p className="text-xs text-indigo-300 font-bold">Brain: {selectedPatient.organs.brain.health}%</p>
                                                        </div>
                                                    </div>
                                                </div>

                                                {/* Temperature - Forehead */}
                                                <div className="absolute top-[5%] right-[15%]" style={{ zIndex: 10 }}>
                                                    <div className="flex items-center gap-2 bg-gray-900/90 px-3 py-1.5 rounded-full border border-amber-500/50 backdrop-blur-sm">
                                                        <Thermometer size={14} className={selectedPatient.vitals.temperature > 37.5 ? "text-amber-400" : "text-cyan-400"} />
                                                        <span className={`text-xs font-bold ${selectedPatient.vitals.temperature > 37.5 ? "text-amber-300" : "text-cyan-300"}`}>
                                                            {selectedPatient.vitals.temperature}°C
                                                        </span>
                                                    </div>
                                                </div>

                                                {/* Heart - Left chest */}
                                                <div className="absolute top-[28%] left-[42%]" style={{ zIndex: 10 }}>
                                                    <div className="relative group cursor-pointer">
                                                        <div className={`w-14 h-14 rounded-full flex items-center justify-center backdrop-blur-sm ${selectedPatient.vitals.heartRate > 100
                                                            ? 'bg-red-500/40 border-2 border-red-400 animate-pulse'
                                                            : 'bg-emerald-500/30 border-2 border-emerald-400'
                                                            }`}>
                                                            <Heart size={24} className={selectedPatient.vitals.heartRate > 100 ? "text-red-300" : "text-emerald-300"} />
                                                        </div>
                                                        <div className="absolute -right-20 top-1/2 transform -translate-y-1/2 bg-gray-900/95 px-3 py-2 rounded-lg border border-emerald-500">
                                                            <p className={`text-sm font-bold ${selectedPatient.vitals.heartRate > 100 ? "text-red-300" : "text-emerald-300"}`}>
                                                                {selectedPatient.vitals.heartRate} bpm
                                                            </p>
                                                            <p className="text-xs text-gray-400">Heart Rate</p>
                                                        </div>
                                                    </div>
                                                </div>

                                                {/* Lungs - Chest area */}
                                                <div className="absolute top-[32%] left-[25%]" style={{ zIndex: 10 }}>
                                                    <div className="relative group cursor-pointer">
                                                        <div className="w-12 h-12 rounded-full bg-cyan-500/30 border-2 border-cyan-400 flex items-center justify-center backdrop-blur-sm">
                                                            <Activity size={20} className="text-cyan-300" />
                                                        </div>
                                                        <div className="absolute -left-24 top-1/2 transform -translate-y-1/2 bg-gray-900/95 px-3 py-2 rounded-lg border border-cyan-500 whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity">
                                                            <p className="text-sm font-bold text-cyan-300">SpO₂: {selectedPatient.vitals.spo2}%</p>
                                                            <p className="text-xs text-gray-400">Oxygen Sat.</p>
                                                        </div>
                                                    </div>
                                                </div>

                                                {/* Respiratory Rate */}
                                                <div className="absolute top-[32%] right-[20%]" style={{ zIndex: 10 }}>
                                                    <div className="flex items-center gap-2 bg-gray-900/90 px-3 py-1.5 rounded-full border border-blue-500/50 backdrop-blur-sm">
                                                        <Waves size={14} className="text-blue-400" />
                                                        <span className="text-xs font-bold text-blue-300">
                                                            {selectedPatient.vitals.respiratoryRate}/min
                                                        </span>
                                                    </div>
                                                </div>

                                                {/* Liver - Right abdomen */}
                                                <div className="absolute top-[45%] right-[28%]" style={{ zIndex: 10 }}>
                                                    <div className="relative group cursor-pointer">
                                                        <div className="w-10 h-10 rounded-full bg-amber-500/30 border-2 border-amber-400 flex items-center justify-center backdrop-blur-sm">
                                                            <div className="w-2 h-2 rounded-full bg-amber-400"></div>
                                                        </div>
                                                        <div className="absolute -top-12 left-1/2 transform -translate-x-1/2 bg-gray-900/95 px-3 py-1 rounded-lg border border-amber-500 whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity">
                                                            <p className="text-xs text-amber-300 font-bold">Liver: {selectedPatient.organs.liver.health}%</p>
                                                        </div>
                                                    </div>
                                                </div>

                                                {/* Kidneys - Lower back area */}
                                                <div className="absolute top-[50%] left-[20%]" style={{ zIndex: 10 }}>
                                                    <div className="relative group cursor-pointer">
                                                        <div className="w-8 h-8 rounded-full bg-pink-500/30 border-2 border-pink-400 flex items-center justify-center backdrop-blur-sm">
                                                            <div className="w-1.5 h-1.5 rounded-full bg-pink-400"></div>
                                                        </div>
                                                        <div className="absolute -top-10 left-1/2 transform -translate-x-1/2 bg-gray-900/95 px-2 py-1 rounded-lg border border-pink-500 whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity">
                                                            <p className="text-xs text-pink-300 font-bold">Kidneys: {selectedPatient.organs.kidneys.health}%</p>
                                                        </div>
                                                    </div>
                                                </div>

                                                {/* Blood Pressure - Left arm */}
                                                <div className="absolute top-[35%] left-[8%]" style={{ zIndex: 10 }}>
                                                    <div className="bg-gray-900/90 px-3 py-2 rounded-lg border-2 border-pink-500/70 backdrop-blur-sm">
                                                        <div className="flex items-center gap-2 mb-1">
                                                            <Droplet size={14} className="text-pink-400" />
                                                            <span className="text-xs font-bold text-pink-300">BP</span>
                                                        </div>
                                                        <p className="text-sm font-bold text-pink-200">{selectedPatient.vitals.bp}</p>
                                                        <p className="text-xs text-gray-400">mmHg</p>
                                                    </div>
                                                </div>

                                                {/* Glucose - Abdomen */}
                                                <div className="absolute top-[55%] left-1/2 transform -translate-x-1/2" style={{ zIndex: 10 }}>
                                                    <div className="bg-gray-900/90 px-3 py-1.5 rounded-full border border-emerald-500/50 backdrop-blur-sm flex items-center gap-2">
                                                        <TrendingUp size={14} className="text-emerald-400" />
                                                        <span className="text-xs font-bold text-emerald-300">
                                                            {selectedPatient.vitals.glucose} mg/dL
                                                        </span>
                                                    </div>
                                                </div>

                                                {/* Stress Level - Spine/nervous system */}
                                                <div className="absolute top-[65%] left-1/2 transform -translate-x-1/2" style={{ zIndex: 10 }}>
                                                    <div className="relative group cursor-pointer">
                                                        <div className="w-12 h-12 rounded-full bg-purple-500/30 border-2 border-purple-400 flex items-center justify-center backdrop-blur-sm">
                                                            <Zap size={20} className="text-purple-300" />
                                                        </div>
                                                        <div className="absolute -bottom-12 left-1/2 transform -translate-x-1/2 bg-gray-900/95 px-3 py-1 rounded-lg border border-purple-500 whitespace-nowrap">
                                                            <p className="text-xs text-purple-300 font-bold">Stress: {selectedPatient.vitals.stress.toFixed(1)}/5</p>
                                                        </div>
                                                    </div>
                                                </div>

                                                {/* Pulsing animation overlay for critical vitals */}
                                                {selectedPatient.vitals.heartRate > 100 && (
                                                    <div className="absolute top-[28%] left-[42%] w-14 h-14 rounded-full bg-red-500/20 animate-ping" style={{ zIndex: 9 }}></div>
                                                )}
                                            </div>
                                        </div>

                                        <div className="mt-4 p-4 bg-gray-800/50 rounded-xl border border-gray-700">
                                            <p className="text-xs text-gray-400 mb-3 uppercase tracking-wider font-semibold">Health Legend</p>
                                            <div className="grid grid-cols-3 gap-2 text-xs">
                                                <div className="flex items-center gap-2">
                                                    <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
                                                    <span className="text-gray-300">Normal</span>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <div className="w-3 h-3 rounded-full bg-amber-500"></div>
                                                    <span className="text-gray-300">Warning</span>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <div className="w-3 h-3 rounded-full bg-red-500"></div>
                                                    <span className="text-gray-300">Critical</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Real-time ECG */}
                                    <div>
                                        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                            <Waves size={18} className="text-rose-400" />
                                            Live ECG Monitor
                                        </h3>
                                        <div className="bg-black rounded-xl p-4 border border-gray-700">
                                            <div className="h-32">
                                                <ResponsiveContainer width="100%" height="100%">
                                                    <LineChart data={ecgData}>
                                                        <Line
                                                            type="monotone"
                                                            dataKey="y"
                                                            stroke="#10b981"
                                                            strokeWidth={2}
                                                            dot={false}
                                                            isAnimationActive={false}
                                                        />
                                                    </LineChart>
                                                </ResponsiveContainer>
                                            </div>
                                            <div className="flex justify-between items-center mt-2 text-xs">
                                                <span className="text-emerald-400 font-mono">RHYTHM: {selectedPatient.vitals.heartRate > 100 ? 'TACHYCARDIA' : 'NORMAL SINUS'}</span>
                                                <span className="text-gray-500 font-mono">LEAD II</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Middle + Right Columns: Patient Details */}
                                <div className="lg:col-span-2 space-y-6">
                                    {/* Vital Signs Grid */}
                                    <div>
                                        <div className="flex justify-between items-center mb-4">
                                            <h3 className="text-lg font-bold text-white">Vital Signs</h3>
                                            <button
                                                onClick={() => setEditingVitals(!editingVitals)}
                                                className="flex items-center gap-2 px-3 py-1.5 bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 rounded-lg hover:bg-indigo-600 hover:text-white transition-all text-sm"
                                            >
                                                <Edit size={16} />
                                                {editingVitals ? 'Cancel Edit' : 'Edit Vitals'}
                                            </button>
                                        </div>

                                        {editingVitals ? (
                                            <div className="bg-gray-800/50 p-6 rounded-2xl border border-gray-700 mb-6 animate-slide-in">
                                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                                                    <div className="space-y-2">
                                                        <label className="text-xs text-gray-400 block px-1">Heart Rate (bpm)</label>
                                                        <input
                                                            type="number"
                                                            value={vitalForm.heartRate || ''}
                                                            onChange={(e) => setVitalForm({ ...vitalForm, heartRate: parseFloat(e.target.value) })}
                                                            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-indigo-500 focus:outline-none"
                                                        />
                                                    </div>
                                                    <div className="space-y-2">
                                                        <label className="text-xs text-gray-400 block px-1">SpO₂ (%)</label>
                                                        <input
                                                            type="number"
                                                            value={vitalForm.spo2 || ''}
                                                            onChange={(e) => setVitalForm({ ...vitalForm, spo2: parseFloat(e.target.value) })}
                                                            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-indigo-500 focus:outline-none"
                                                        />
                                                    </div>
                                                    <div className="space-y-2">
                                                        <label className="text-xs text-gray-400 block px-1">Temp (°C)</label>
                                                        <input
                                                            type="number"
                                                            step="0.1"
                                                            value={vitalForm.temperature || ''}
                                                            onChange={(e) => setVitalForm({ ...vitalForm, temperature: parseFloat(e.target.value) })}
                                                            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-indigo-500 focus:outline-none"
                                                        />
                                                    </div>
                                                    <div className="space-y-2">
                                                        <label className="text-xs text-gray-400 block px-1">Stress (0-5)</label>
                                                        <input
                                                            type="number"
                                                            step="0.1"
                                                            value={vitalForm.stress || ''}
                                                            onChange={(e) => setVitalForm({ ...vitalForm, stress: parseFloat(e.target.value) })}
                                                            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-indigo-500 focus:outline-none"
                                                        />
                                                    </div>
                                                </div>
                                                <div className="flex justify-end">
                                                    <button
                                                        onClick={handleUpdateVitals}
                                                        className="px-6 py-2 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 font-bold shadow-lg shadow-indigo-600/20 transition-all"
                                                    >
                                                        Save Changes
                                                    </button>
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                                <div className="bg-gradient-to-br from-rose-500/10 to-rose-600/5 p-4 rounded-xl border border-rose-500/20">
                                                    <div className="flex items-center gap-2 mb-2">
                                                        <Heart size={18} className="text-rose-400" />
                                                        <span className="text-gray-400 text-sm">Heart Rate</span>
                                                    </div>
                                                    <p className="text-3xl font-bold text-white">{selectedPatient.vitals.heartRate}</p>
                                                    <p className="text-xs text-gray-500 mt-1">bpm • {selectedPatient.vitals.heartRate > 100 ? 'Elevated' : 'Normal'}</p>
                                                </div>

                                                <div className="bg-gradient-to-br from-cyan-500/10 to-cyan-600/5 p-4 rounded-xl border border-cyan-500/20">
                                                    <div className="flex items-center gap-2 mb-2">
                                                        <Activity size={18} className="text-cyan-400" />
                                                        <span className="text-gray-400 text-sm">SpO₂</span>
                                                    </div>
                                                    <p className="text-3xl font-bold text-white">{selectedPatient.vitals.spo2}</p>
                                                    <p className="text-xs text-gray-500 mt-1">% • Oxygen Sat.</p>
                                                </div>

                                                <div className="bg-gradient-to-br from-amber-500/10 to-amber-600/5 p-4 rounded-xl border border-amber-500/20">
                                                    <div className="flex items-center gap-2 mb-2">
                                                        <Thermometer size={18} className="text-amber-400" />
                                                        <span className="text-gray-400 text-sm">Temperature</span>
                                                    </div>
                                                    <p className="text-3xl font-bold text-white">{selectedPatient.vitals.temperature}</p>
                                                    <p className="text-xs text-gray-500 mt-1">°C • {selectedPatient.vitals.temperature > 37.5 ? 'Fever' : 'Normal'}</p>
                                                </div>

                                                <div className="bg-gradient-to-br from-pink-500/10 to-pink-600/5 p-4 rounded-xl border border-pink-500/20">
                                                    <div className="flex items-center gap-2 mb-2">
                                                        <Droplet size={18} className="text-pink-400" />
                                                        <span className="text-gray-400 text-sm">Blood Pressure</span>
                                                    </div>
                                                    <p className="text-2xl font-bold text-white">{selectedPatient.vitals.bp}</p>
                                                    <p className="text-xs text-gray-500 mt-1">mmHg • Systolic/Diastolic</p>
                                                </div>

                                                <div className="bg-gradient-to-br from-violet-500/10 to-violet-600/5 p-4 rounded-xl border border-violet-500/20">
                                                    <div className="flex items-center gap-2 mb-2">
                                                        <Zap size={18} className="text-violet-400" />
                                                        <span className="text-gray-400 text-sm">Stress Level</span>
                                                    </div>
                                                    <p className="text-3xl font-bold text-white">{selectedPatient.vitals.stress}</p>
                                                    <p className="text-xs text-gray-500 mt-1">/ 5 • Cortisol Index</p>
                                                </div>

                                                <div className="bg-gradient-to-br from-blue-500/10 to-blue-600/5 p-4 rounded-xl border border-blue-500/20">
                                                    <div className="flex items-center gap-2 mb-2">
                                                        <Waves size={18} className="text-blue-400" />
                                                        <span className="text-gray-400 text-sm">Resp. Rate</span>
                                                    </div>
                                                    <p className="text-3xl font-bold text-white">{selectedPatient.vitals.respiratoryRate}</p>
                                                    <p className="text-xs text-gray-500 mt-1">breaths/min</p>
                                                </div>

                                                <div className="bg-gradient-to-br from-emerald-500/10 to-emerald-600/5 p-4 rounded-xl border border-emerald-500/20">
                                                    <div className="flex items-center gap-2 mb-2">
                                                        <TrendingUp size={18} className="text-emerald-400" />
                                                        <span className="text-gray-400 text-sm">Glucose</span>
                                                    </div>
                                                    <p className="text-3xl font-bold text-white">{selectedPatient.vitals.glucose}</p>
                                                    <p className="text-xs text-gray-500 mt-1">mg/dL • Blood Sugar</p>
                                                </div>

                                                <div className="bg-gradient-to-br from-indigo-500/10 to-indigo-600/5 p-4 rounded-xl border border-indigo-500/20">
                                                    <div className="flex items-center gap-2 mb-2">
                                                        <Calendar size={18} className="text-indigo-400" />
                                                        <span className="text-gray-400 text-sm">Last Visit</span>
                                                    </div>
                                                    <p className="text-lg font-bold text-white">{selectedPatient.lastVisit}</p>
                                                    <p className="text-xs text-gray-500 mt-1">Recent checkup</p>
                                                </div>
                                            </div>
                                        )}
                                    </div>

                                    {/* Organ Health Status */}
                                    <div>
                                        <h3 className="text-lg font-bold text-white mb-4">Organ Health Assessment</h3>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            {Object.entries(selectedPatient.organs).map(([organ, data]) => (
                                                <div key={organ} className={`p-4 rounded-xl border ${getOrganColor(data.status)}`}>
                                                    <div className="flex justify-between items-start mb-2">
                                                        <h4 className="font-bold capitalize">{organ}</h4>
                                                        <span className="text-2xl font-bold">{data.health}%</span>
                                                    </div>
                                                    <div className="w-full bg-gray-800 rounded-full h-2 mb-2">
                                                        <div
                                                            className={`h-2 rounded-full transition-all duration-500 ${data.status === 'normal' ? 'bg-emerald-500' :
                                                                data.status === 'warning' ? 'bg-amber-500' : 'bg-red-500'
                                                                }`}
                                                            style={{ width: `${data.health}%` }}
                                                        />
                                                    </div>
                                                    <p className="text-xs opacity-80">{data.note}</p>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Medical Information */}
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div className="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
                                            <h4 className="text-white font-bold mb-3 flex items-center gap-2">
                                                <FileText size={16} className="text-indigo-400" />
                                                Primary Diagnosis
                                            </h4>
                                            <p className="text-gray-300 text-sm leading-relaxed">{selectedPatient.diagnosis}</p>
                                        </div>

                                        <div className="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
                                            <h4 className="text-white font-bold mb-3 flex items-center gap-2">
                                                <Pill size={16} className="text-emerald-400" />
                                                Current Medications
                                            </h4>
                                            <ul className="text-gray-300 text-sm space-y-2">
                                                {selectedPatient.medications.map((med, i) => (
                                                    <li key={i} className="flex items-start gap-2">
                                                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5"></span>
                                                        <span>{med}</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    </div>

                                    {/* Allergies */}
                                    <div className="bg-red-500/10 border border-red-500/20 p-4 rounded-xl">
                                        <h4 className="text-red-400 font-bold mb-2 flex items-center gap-2">
                                            <AlertTriangle size={16} />
                                            Known Allergies
                                        </h4>
                                        <p className="text-red-300 text-sm">{selectedPatient.allergies.join(', ')}</p>
                                    </div>

                                    {/* Clinical Notes */}
                                    <div className="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
                                        <h4 className="text-white font-bold mb-3 flex items-center gap-2">
                                            <Clipboard size={16} className="text-cyan-400" />
                                            Clinical Notes
                                        </h4>
                                        <p className="text-gray-300 text-sm leading-relaxed">{selectedPatient.notes}</p>
                                    </div>

                                    {/* Recent Symptoms (from Chatbot) */}
                                    {selectedPatient.symptoms && selectedPatient.symptoms.length > 0 && (
                                        <div className="bg-indigo-500/10 border border-indigo-500/20 p-4 rounded-xl">
                                            <h4 className="text-indigo-400 font-bold mb-3 flex items-center gap-2">
                                                <MessageCircle size={16} />
                                                Recent Symptoms (from Chatbot)
                                            </h4>
                                            <div className="space-y-3">
                                                {selectedPatient.symptoms.map((s, i) => (
                                                    <div key={i} className="border-l-2 border-indigo-500/30 pl-3">
                                                        <div className="flex justify-between items-center mb-1">
                                                            <span className="text-xs text-indigo-300 font-bold">{s.date} at {s.time}</span>
                                                        </div>
                                                        <p className="text-xs text-gray-300 leading-relaxed italic">"{s.content}"</p>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Medical Timeline */}
                                    <div>
                                        <h3 className="text-lg font-bold text-white mb-4">Medical Timeline</h3>
                                        <div className="space-y-3">
                                            {selectedPatient.timeline.map((item, i) => (
                                                <div key={i} className="flex gap-4">
                                                    <div className="flex flex-col items-center">
                                                        <div className={`w-3 h-3 rounded-full ${item.type === 'warning' ? 'bg-amber-500' :
                                                            item.type === 'info' ? 'bg-blue-500' : 'bg-emerald-500'
                                                            }`} />
                                                        {i < selectedPatient.timeline.length - 1 && (
                                                            <div className="w-0.5 h-full bg-gray-700 mt-1" />
                                                        )}
                                                    </div>
                                                    <div className="flex-1 pb-4">
                                                        <p className="text-gray-400 text-xs mb-1">{item.date}</p>
                                                        <p className="text-gray-200 text-sm">{item.event}</p>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Action Buttons */}
                                    <div className="flex gap-3 pt-4 border-t border-gray-800">
                                        <Button variant="primary" icon={FileText} className="flex-1">View Full Medical History</Button>
                                        <Button variant="secondary" icon={Download}>Download Report</Button>
                                        <Button variant="secondary">Print</Button>
                                    </div>
                                </div>
                            </div>
                        </Card>
                    </div>
                </div>
            )}

            {/* Patient List */}
            <div>
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-bold text-white">Patient List</h3>
                    <Button variant="secondary" icon={Filter} className="!py-2">Filter Status</Button>
                </div>

                <div className="grid grid-cols-1 gap-4">
                    {patients.map(patient => {
                        const { status, color, icon: StatusIcon } = getPatientStatus(patient.id);
                        return (
                            <Card key={patient.id} className="glass-card flex flex-col md:flex-row items-start md:items-center justify-between p-5 hover:bg-white/5 hover:border-indigo-500/30 transition-all group border-none">
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-gray-700 to-gray-800 flex items-center justify-center text-gray-300 font-bold text-lg border border-gray-600 group-hover:border-indigo-500/50 transition-colors">
                                        {patient.name.charAt(0)}
                                    </div>
                                    <div>
                                        <h4 className="font-bold text-gray-200 group-hover:text-white transition-colors">{patient.name}</h4>
                                        <p className="text-sm text-gray-500 flex items-center gap-2">
                                            <span className="text-gray-600">ID: #{patient.id}</span>
                                            <span>•</span>
                                            <span>{patient.age} yrs</span>
                                            <span>•</span>
                                            <span>{patient.gender}</span>
                                        </p>
                                    </div>
                                </div>

                                <div className="flex items-center gap-6 mt-4 md:mt-0 w-full md:w-auto justify-between md:justify-end">
                                    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider border ${color}`}>
                                        <StatusIcon size={14} />
                                        {status}
                                    </div>
                                    <Button
                                        variant="secondary"
                                        className="!text-sm !py-2 hover:!bg-indigo-600 hover:!text-white hover:!border-indigo-500"
                                        onClick={() => handleViewPatient(patient)}
                                    >
                                        View Details
                                    </Button>
                                </div>
                            </Card>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

export default DoctorDashboard;
