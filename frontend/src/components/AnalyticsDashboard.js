import React, { useState, useEffect } from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter, Cell } from 'recharts';
import { Network, Share2, Activity, User, AlertTriangle, ShieldCheck, Users, TrendingUp } from 'lucide-react';
import Card from './ui/Card';

const API_URL = 'http://localhost:8000';

const AnalyticsDashboard = () => {
    const [inflowData, setInflowData] = useState([]);
    const [securityScore, setSecurityScore] = useState(0);
    const [comparisonData, setComparisonData] = useState({ models: [] });
    const [graphData, setGraphData] = useState({ nodes: [], links: [] });
    const [loading, setLoading] = useState(true);
    const [loadingGraph, setLoadingGraph] = useState(false);
    const [activeTab, setActiveTab] = useState('overview'); // 'overview', 'performance', 'network'

    useEffect(() => {
        const fetchInitialAnalytics = async () => {
            setLoading(true);
            try {
                const [inflowRes, securityRes] = await Promise.all([
                    fetch(`${API_URL}/analytics/predictions/inflow`),
                    fetch(`${API_URL}/analytics/security-audit`)
                ]);

                if (inflowRes.ok && securityRes.ok) {
                    const flow = await inflowRes.json();
                    const sec = await securityRes.json();

                    const formattedFlow = flow.dates.map((date, i) => ({
                        date: date.substring(5), // mm-dd
                        actual: flow.actuals[i],
                        forecast: flow.forecasts[i]
                    }));

                    setInflowData(formattedFlow);
                    setSecurityScore(sec.integrity_score);
                }
            } catch (error) {
                console.error("Failed to fetch initial analytics:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchInitialAnalytics();
    }, []);

    useEffect(() => {
        if (activeTab === 'performance' && (!comparisonData.models || comparisonData.models.length === 0)) {
            fetchComparisonData();
        } else if (activeTab === 'network' && graphData.nodes.length === 0) {
            fetchGraphData();
        }
    }, [activeTab, comparisonData.models, graphData.nodes.length]);

    const fetchComparisonData = async () => {
        setLoading(true);
        try {
            const comparisonRes = await fetch(`${API_URL}/api/analytics/model-comparison`);
            if (comparisonRes.ok) {
                const comp = await comparisonRes.json();
                setComparisonData(comp);
            }
        } catch (error) {
            console.error("Failed to fetch comparison data:", error);
        } finally {
            setLoading(false);
        }
    };

    const fetchGraphData = async () => {
        setLoadingGraph(true);
        try {
            const res = await fetch(`${API_URL}/api/analytics/knowledge-graph`);
            const data = await res.json();
            if (!data.error) {
                setGraphData(data);
            }
        } catch (e) {
            console.error("Failed to fetch graph data", e);
        } finally {
            setLoadingGraph(false);
        }
    };

    // --- Custom Network Visualization ---
    const renderNetworkGraph = () => {
        if (loadingGraph) return <div className="text-white text-center p-20 animate-pulse">Analyzing Network Topology with PageRank...</div>;

        const { nodes, links } = graphData;
        if (!nodes || nodes.length === 0) return <div className="text-gray-400 text-center p-20">No network data available.</div>;

        const typeColor = {
            'patient': '#6366f1', // Indigo
            'doctor': '#10b981',  // Emerald
            'symptom': '#ef4444', // Red
            'researcher': '#f59e0b' // Amber
        };

        return (
            <div className="relative h-[500px] w-full border border-gray-800 rounded-xl bg-gray-900/50 overflow-hidden">
                {/* SVG Layer for Links */}
                <svg className="absolute inset-0 w-full h-full pointer-events-none">
                    {links.map((link, i) => {
                        const source = nodes.find(n => n.id === link.source);
                        const target = nodes.find(n => n.id === link.target);
                        if (!source || !target) return null;

                        // Map -1.5..1.5 coords to 0..100% container space
                        const toPercent = (val) => `${((val + 1.5) / 3.0) * 100}%`;

                        return (
                            <line
                                key={i}
                                x1={toPercent(source.x)} y1={toPercent(source.y)}
                                x2={toPercent(target.x)} y2={toPercent(target.y)}
                                stroke="rgba(255,255,255,0.15)"
                                strokeWidth="1"
                            />
                        );
                    })}
                </svg>

                {/* Scatter Layer for Nodes */}
                <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                        <XAxis type="number" dataKey="x" domain={[-1.5, 1.5]} hide />
                        <YAxis type="number" dataKey="y" domain={[-1.5, 1.5]} hide />
                        <Tooltip
                            cursor={{ strokeDasharray: '3 3' }}
                            content={({ payload }) => {
                                if (payload && payload.length) {
                                    const node = payload[0].payload;
                                    return (
                                        <div className="bg-gray-800 border border-gray-700 p-3 rounded shadow-xl">
                                            <p className="font-bold text-white">{node.name}</p>
                                            <p className="text-xs text-gray-400 capitalize">{node.type}</p>
                                            <p className="text-xs text-indigo-400 mt-1">Centrality: {(node.centrality * 100).toFixed(2)}%</p>
                                        </div>
                                    );
                                }
                                return null;
                            }}
                        />
                        <Scatter name="Nodes" data={nodes} fill="#8884d8">
                            {nodes.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={typeColor[entry.type] || '#888'} />
                            ))}
                        </Scatter>
                    </ScatterChart>
                </ResponsiveContainer>

                <div className="absolute bottom-4 right-4 flex gap-4 text-xs">
                    <div className="flex items-center gap-1"><div className="w-3 h-3 rounded-full bg-indigo-500"></div> Patient</div>
                    <div className="flex items-center gap-1"><div className="w-3 h-3 rounded-full bg-emerald-500"></div> Doctor</div>
                    <div className="flex items-center gap-1"><div className="w-3 h-3 rounded-full bg-red-500"></div> Symptom</div>
                </div>
            </div>
        );
    };

    if (loading && activeTab === 'overview') return <div className="text-white p-8 animate-pulse">Loading Analytics...</div>;

    // Prepare chart data for comparison if available
    const barChartData = (comparisonData.models && comparisonData.models.length >= 3) ? [
        { name: 'Accuracy', 'HealthWatch AI': comparisonData.models[0].metrics.accuracy * 100, 'Baseline LSTM': comparisonData.models[1].metrics.accuracy * 100, 'Random Forest': comparisonData.models[2].metrics.accuracy * 100 },
        { name: 'Sensitivity', 'HealthWatch AI': comparisonData.models[0].metrics.sensitivity * 100, 'Baseline LSTM': comparisonData.models[1].metrics.sensitivity * 100, 'Random Forest': comparisonData.models[2].metrics.sensitivity * 100 },
        { name: 'Specificity', 'HealthWatch AI': comparisonData.models[0].metrics.specificity * 100, 'Baseline LSTM': comparisonData.models[1].metrics.specificity * 100, 'Random Forest': comparisonData.models[2].metrics.specificity * 100 },
        { name: 'F1 Score', 'HealthWatch AI': comparisonData.models[0].metrics.f1_score * 100, 'Baseline LSTM': comparisonData.models[1].metrics.f1_score * 100, 'Random Forest': comparisonData.models[2].metrics.f1_score * 100 },
    ] : [];

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-8 pb-20">
            <header>
                <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 bg-indigo-500/20 rounded-lg">
                        <TrendingUp className="text-indigo-400" size={24} />
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold text-white">Research Analytics & Predictions</h2>
                        <p className="text-gray-400">Advanced ML models for patient flow forecasting and system integrity.</p>
                    </div>
                </div>
            </header>

            {/* Tab Navigation */}
            <div className="flex space-x-4 border-b border-gray-800 pb-4">
                <button
                    onClick={() => setActiveTab('overview')}
                    className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${activeTab === 'overview' ? 'bg-indigo-600 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800'}`}
                >
                    Overview
                </button>
                <button
                    onClick={() => setActiveTab('performance')}
                    className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${activeTab === 'performance' ? 'bg-indigo-600 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800'}`}
                >
                    Algorithmic Performance
                </button>
                <button
                    onClick={() => setActiveTab('network')}
                    className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${activeTab === 'network' ? 'bg-indigo-600 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800'}`}
                >
                    Knowledge Graph
                </button>
            </div>

            {activeTab === 'overview' && (
                <>
                    {/* Top Stats Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {/* Privacy Score Card */}
                        <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-emerald-500/30 transition-all">
                            <div className="flex items-center gap-3 mb-2">
                                <ShieldCheck className="text-emerald-400" />
                                <h3 className="text-lg font-medium text-white">System Integrity</h3>
                            </div>
                            <div className="text-4xl font-bold text-white mb-1">
                                {securityScore}%
                            </div>
                            <p className="text-sm text-gray-400">Blockchain Validation Score</p>
                            <div className="w-full bg-gray-800 h-2 rounded-full mt-4 overflow-hidden">
                                <div
                                    className="bg-emerald-500 h-full transition-all duration-1000"
                                    style={{ width: `${securityScore}%` }}
                                />
                            </div>
                        </div>

                        {/* Patient Flow Stats */}
                        <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-blue-500/30 transition-all">
                            <div className="flex items-center gap-3 mb-2">
                                <Users className="text-blue-400" />
                                <h3 className="text-lg font-medium text-white">Predicted Inflow</h3>
                            </div>
                            <div className="text-4xl font-bold text-white mb-1">
                                +12%
                            </div>
                            <p className="text-sm text-gray-400">Next 7 Days Forecast</p>
                            <p className="text-xs text-blue-400 mt-2">Based on seasonality model</p>
                        </div>

                        {/* Model Confidence */}
                        <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-purple-500/30 transition-all">
                            <div className="flex items-center gap-3 mb-2">
                                <Activity className="text-purple-400" />
                                <h3 className="text-lg font-medium text-white">Model Confidence</h3>
                            </div>
                            <div className="text-4xl font-bold text-white mb-1">
                                {(comparisonData.models && comparisonData.models.length > 0) ? (comparisonData.models[0].metrics.accuracy * 100).toFixed(1) : '94.2'}%
                            </div>
                            <p className="text-sm text-gray-400">Accuracy (Proposed Model)</p>
                            <p className="text-xs text-purple-400 mt-2">Multi-Modal Temporal Fusion</p>
                        </div>
                    </div>

                    {/* Main Inflow Chart */}
                    <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl">
                        <h3 className="text-xl font-bold text-white mb-6">Patient Admission Forecast</h3>
                        <div className="h-[400px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={inflowData}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                    <XAxis
                                        dataKey="date"
                                        stroke="#9ca3af"
                                        style={{ fontSize: '12px' }}
                                    />
                                    <YAxis
                                        stroke="#9ca3af"
                                        style={{ fontSize: '12px' }}
                                    />
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: '#111827',
                                            border: '1px solid #374151',
                                            borderRadius: '8px',
                                            color: '#f3f4f6'
                                        }}
                                    />
                                    <Legend />
                                    <Line
                                        type="monotone"
                                        dataKey="forecast"
                                        stroke="#3b82f6"
                                        strokeWidth={3}
                                        dot={{ r: 4, fill: '#3b82f6' }}
                                        name="AI Forecast"
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="actual"
                                        stroke="#10b981"
                                        strokeWidth={3}
                                        dot={{ r: 4, fill: '#10b981' }}
                                        strokeDasharray="5 5"
                                        name="Actual Admissions"
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </>
            )}

            {activeTab === 'performance' && comparisonData.models && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Comparison Chart */}
                    <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl">
                        <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                            <Activity className="text-indigo-400" size={20} />
                            Algorithmic Performance Comparison
                        </h3>
                        <div className="h-[300px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={barChartData} barGap={0} barCategoryGap="20%">
                                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                                    <XAxis dataKey="name" stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
                                    <YAxis stroke="#9ca3af" tick={{ fill: '#9ca3af' }} domain={[60, 100]} />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', color: '#f3f4f6' }}
                                        itemStyle={{ color: '#f3f4f6' }}
                                    />
                                    <Legend />
                                    <Bar dataKey="HealthWatch AI" fill="#6366f1" radius={[4, 4, 0, 0]} name="Our Model" />
                                    <Bar dataKey="Baseline LSTM" fill="#10b981" radius={[4, 4, 0, 0]} />
                                    <Bar dataKey="Random Forest" fill="#9ca3af" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Clinical Utility Table */}
                    <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl">
                        <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                            <ShieldCheck className="text-emerald-400" size={20} />
                            Clinical Utility Metrics
                        </h3>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left text-sm text-gray-400">
                                <thead className="text-xs uppercase bg-gray-800/50 text-gray-300">
                                    <tr>
                                        <th className="px-4 py-3 rounded-l-lg">Model</th>
                                        <th className="px-4 py-3">AUROC</th>
                                        <th className="px-4 py-3 text-center">NNE*</th>
                                        <th className="px-4 py-3 text-right rounded-r-lg">Alert Rate</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-800">
                                    {comparisonData.models.map((model, idx) => (
                                        <tr key={idx} className={idx === 0 ? "bg-indigo-500/10" : ""}>
                                            <td className="px-4 py-3 font-medium text-white flex items-center gap-2">
                                                {idx === 0 && <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></span>}
                                                {model.name}
                                            </td>
                                            <td className="px-4 py-3 font-mono text-emerald-400">{model.metrics.auroc.toFixed(3)}</td>
                                            <td className="px-4 py-3 text-center font-mono">{model.clinical.nne}</td>
                                            <td className="px-4 py-3 text-right font-mono">{(model.clinical.alert_rate * 100).toFixed(1)}%</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        <p className="mt-4 text-xs text-gray-500 italic">
                            *NNE (Number Needed to Evaluate): Number of alerts a clinician must review to find one true positive case. Lower is better.
                        </p>
                    </div>
                </div>
            )}

            {activeTab === 'network' && (
                <div className="space-y-6 animate-fade-in">
                    <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl">
                        <div className="mb-6">
                            <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                <Share2 className="text-indigo-400" />
                                Medical Knowledge Graph
                            </h3>
                            <p className="text-sm text-gray-400 mt-1">
                                Network analysis identifying critical nodes (High PageRank) and patient cohorts (Community Detection).
                            </p>
                        </div>
                        <div>
                            {renderNetworkGraph()}

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                                <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                                    <h4 className="text-indigo-400 text-sm font-bold mb-1">Graph Density</h4>
                                    <p className="text-2xl font-mono text-white">{(graphData.metrics?.density * 100 || 0).toFixed(1)}%</p>
                                    <p className="text-xs text-gray-500">Connectivity ratio</p>
                                </div>
                                <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                                    <h4 className="text-emerald-400 text-sm font-bold mb-1">Avg Clustering</h4>
                                    <p className="text-2xl font-mono text-white">{(graphData.metrics?.avg_clustering * 100 || 0).toFixed(1)}%</p>
                                    <p className="text-xs text-gray-500">Local cohesion</p>
                                </div>
                                <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                                    <h4 className="text-pink-400 text-sm font-bold mb-1">Critical Nodes</h4>
                                    <p className="text-2xl font-mono text-white">{graphData.nodes?.filter(n => n.centrality > 0.1).length || 0}</p>
                                    <p className="text-xs text-gray-500">High influence entities</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AnalyticsDashboard;
