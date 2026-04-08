import React, { useState, useEffect } from 'react';
import { Shield, CheckCircle, XCircle, Link, Activity } from 'lucide-react';

const API_URL = 'http://localhost:8000';

// Gas Forecast Widget Component
const GasForecastWidget = () => {
    const [forecast, setForecast] = useState(null);

    useEffect(() => {
        const fetchForecast = async () => {
            try {
                const res = await fetch(`${API_URL}/api/blockchain/gas-forecast`);
                if (res.ok) {
                    const data = await res.json();
                    setForecast(data); // API returns data directly, not nested
                }
            } catch (e) {
                console.error("Failed to fetch gas forecast", e);
            }
        };
        fetchForecast();
        const interval = setInterval(fetchForecast, 5000); // Polling every 5s
        return () => clearInterval(interval);
    }, []);

    if (!forecast) return null;

    return (
        <div className="bg-gray-900 border border-gray-700 rounded-xl p-4 shadow-lg col-span-3">
            <h3 className="text-sm font-bold text-gray-400 mb-3 uppercase tracking-wider flex items-center gap-2">
                <Activity size={14} className="text-purple-400" />
                Context-Aware Gas Pricing (CAGP) Forecast
            </h3>
            <div className="grid grid-cols-4 gap-4">
                <div className="text-center p-2 rounded bg-gray-800/50">
                    <p className="text-xs text-gray-500 mb-1">Safe Low</p>
                    <p className="text-lg font-mono text-emerald-400">{forecast.safeLow}</p>
                    <p className="text-[10px] text-gray-600">Wei</p>
                </div>
                <div className="text-center p-2 rounded bg-gray-800/50 border border-indigo-500/20">
                    <p className="text-xs text-indigo-300 mb-1 font-bold">Standard</p>
                    <p className="text-lg font-mono text-indigo-400">{forecast.standard}</p>
                    <p className="text-[10px] text-gray-600">Wei</p>
                </div>
                <div className="text-center p-2 rounded bg-gray-800/50">
                    <p className="text-xs text-gray-500 mb-1">Fast</p>
                    <p className="text-lg font-mono text-amber-400">{forecast.fast}</p>
                    <p className="text-[10px] text-gray-600">Wei</p>
                </div>
                <div className="text-center p-2 rounded bg-gray-800/50">
                    <p className="text-xs text-gray-500 mb-1">Congestion</p>
                    <p className={`text-lg font-mono ${forecast.congestion > 0.7 ? 'text-red-400' : 'text-emerald-400'}`}>
                        {(forecast.congestion * 100).toFixed(1)}%
                    </p>
                    <p className="text-[10px] text-gray-600">Network Load</p>
                </div>
            </div>
        </div>
    );
};

const BlockchainView = () => {
    const [chain, setChain] = useState([]);
    const [validation, setValidation] = useState({ is_valid: true, length: 0 });
    const [loading, setLoading] = useState(true);
    const [zkTrace, setZkTrace] = useState(null);
    const [verifying, setVerifying] = useState(false);

    useEffect(() => {
        fetchChainData();
    }, []);

    const fetchChainData = async () => {
        try {
            const chainRes = await fetch(`${API_URL}/blockchain/chain`);
            const validRes = await fetch(`${API_URL}/blockchain/validate`);

            if (chainRes.ok && validRes.ok) {
                setChain(await chainRes.json());
                setValidation(await validRes.json());
            }
        } catch (error) {
            console.error("Failed to fetch blockchain data", error);
        } finally {
            setLoading(false);
        }
    };

    const runZKPVerify = async () => {
        setVerifying(true);
        setZkTrace(null);
        try {
            const res = await fetch(`${API_URL}/api/blockchain/zk-verify`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: 'patient_demo' })
            });
            const data = await res.json();

            // Simulate step-by-step reveal for effect
            setZkTrace({});
            setTimeout(() => setZkTrace(prev => ({ ...prev, step_1_commitment: data.step_1_commitment })), 500);
            setTimeout(() => setZkTrace(prev => ({ ...prev, step_2_challenge: data.step_2_challenge })), 1500);
            setTimeout(() => setZkTrace(prev => ({ ...prev, step_3_response: data.step_3_response })), 2500);
            setTimeout(() => setZkTrace(prev => ({ ...prev, step_4_verification: data.step_4_verification })), 3500);
            setTimeout(() => setVerifying(false), 3500);

        } catch (e) {
            console.error(e);
            setVerifying(false);
        }
    };

    if (loading) return <div className="p-8 text-center text-white">Loading Ledger...</div>;

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <header className="mb-8">
                <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                    <Shield className="text-emerald-400" />
                    Immutable Audit Ledger
                    <span className="ml-3 text-sm font-normal text-gray-500 bg-gray-800 px-2 py-1 rounded">Ethereum Mainnet (Simulated)</span>
                </h2>
                <p className="text-gray-400 mt-2">

                </p>
            </header>


            {/* Status Card */}
            <div className={`mb-8 p-6 rounded-xl border ${validation.is_valid ? 'bg-emerald-900/20 border-emerald-500/30' : 'bg-red-900/20 border-red-500/30'} flex items-center justify-between`}>
                <div className="flex items-center gap-4">
                    {validation.is_valid ? <CheckCircle className="text-emerald-400 h-8 w-8" /> : <XCircle className="text-red-400 h-8 w-8" />}
                    <div>
                        <h3 className="text-lg font-semibold text-white">
                            {validation.is_valid ? 'System Integrity Verified' : 'TAMPER DETECTED'}
                        </h3>
                        <p className="text-sm text-gray-300">
                            Blockchain Consensus: {validation.is_valid ? 'Valid' : 'Invalid'} • Total Blocks: {validation.length}
                        </p>
                    </div>
                </div>
                <button
                    onClick={fetchChainData}
                    className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg text-sm font-medium transition-colors"
                >
                    Verify Now
                </button>
            </div>

            {/* ZKP Privacy Section */}
            <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 shadow-lg mb-8 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-4 opacity-10">
                    <Shield size={100} className="text-indigo-400" />
                </div>

                <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2 relative z-10">
                    <Shield className="text-indigo-400" />
                    Zero-Knowledge Privacy Layer
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 relative z-10">
                    <div>
                        <p className="text-gray-400 mb-6 text-sm">
                            Verify patient eligibility for clinical trials without revealing underlying medical data.
                            Uses <strong>Sigma Protocol (Schnorr)</strong> to mathematically prove knowledge of a private record.
                        </p>

                        <button
                            onClick={runZKPVerify}
                            disabled={verifying}
                            className={`px-6 py-3 rounded-xl font-bold text-white shadow-lg transition-all flex items-center gap-2 ${verifying ? 'bg-indigo-900/50 cursor-not-allowed' : 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500'
                                }`}
                        >
                            {verifying ? (
                                <>
                                    <Activity className="animate-spin" size={18} />
                                    Running Protocol...
                                </>
                            ) : (
                                <>
                                    <Shield size={18} />
                                    Run ZK-Proof Verification
                                </>
                            )}
                        </button>
                    </div>

                    <div className="space-y-3 font-mono text-xs">
                        {zkTrace && Object.keys(zkTrace).length > 0 ? (
                            <div className="space-y-3 animate-fade-in">
                                {zkTrace.step_1_commitment && (
                                    <div className="bg-gray-800/50 p-3 rounded border-l-2 border-blue-400 animate-slide-in">
                                        <p className="text-blue-400 font-bold mb-1">1. Prover Commitment</p>
                                        <p className="text-gray-300 break-all">{zkTrace.step_1_commitment.value}</p>
                                        <p className="text-gray-500 mt-1">{zkTrace.step_1_commitment.description}</p>
                                    </div>
                                )}
                                {zkTrace.step_2_challenge && (
                                    <div className="bg-gray-800/50 p-3 rounded border-l-2 border-yellow-400 animate-slide-in">
                                        <p className="text-yellow-400 font-bold mb-1">2. Verifier Challenge</p>
                                        <p className="text-gray-300">{zkTrace.step_2_challenge.value}</p>
                                        <p className="text-gray-500 mt-1">{zkTrace.step_2_challenge.description}</p>
                                    </div>
                                )}
                                {zkTrace.step_3_response && (
                                    <div className="bg-gray-800/50 p-3 rounded border-l-2 border-purple-400 animate-slide-in">
                                        <p className="text-purple-400 font-bold mb-1">3. Prover Response</p>
                                        <p className="text-gray-300 break-all">{zkTrace.step_3_response.value}</p>
                                    </div>
                                )}
                                {zkTrace.step_4_verification && (
                                    <div className={`p-3 rounded border border-emerald-500/30 bg-emerald-900/20 animate-slide-in flex items-center gap-3`}>
                                        <CheckCircle className="text-emerald-400 h-6 w-6" />
                                        <div>
                                            <p className="text-emerald-400 font-bold">Proof Verified Zero-Knowledge</p>
                                            <p className="text-gray-400 mt-0.5">Hash: {zkTrace.step_4_verification.proof_hash.substring(0, 16)}...</p>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="h-full flex items-center justify-center text-gray-600 border border-gray-800 border-dashed rounded-lg p-8">
                                Waiting for protocol initiation...
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Smart Gas Forecast Widget (CAGP) */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <GasForecastWidget />
            </div>

            {/* Chain Visualization */}
            <div className="relative">
                {/* Connecting Line (Desktop) */}
                <div className="absolute top-8 left-0 right-0 h-1 bg-gray-800 hidden lg:block -z-10" />

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {chain.map((block, index) => (
                        <div key={block.number} className="group relative">
                            {/* Connector Arrow (Mobile) */}
                            {index !== 0 && (
                                <div className="absolute -top-6 left-1/2 -translate-x-1/2 lg:hidden text-gray-600">
                                    ↓
                                </div>
                            )}

                            <div className="bg-gray-900 border border-gray-700 rounded-xl p-4 shadow-xl hover:shadow-2xl hover:border-indigo-500/50 transition-all">
                                <div className="flex justify-between items-start mb-3">
                                    <div className="bg-indigo-900/40 border border-indigo-500/30 rounded px-2 py-1 text-xs text-indigo-300 font-mono font-bold">
                                        Block #{block.number}
                                    </div>
                                    <div className="text-xs text-gray-500 ml-auto font-mono">
                                        {new Date(block.timestamp * 1000).toLocaleTimeString()}
                                    </div>
                                </div>

                                <div className="space-y-2 mb-4">
                                    <div className="text-xs">
                                        <span className="text-gray-500 block">Parent Hash</span>
                                        <span className="text-gray-400 font-mono text-[10px] break-all block truncate group-hover:whitespace-normal group-hover:bg-black/80 group-hover:absolute group-hover:z-50 group-hover:p-2 group-hover:rounded bg-gray-800/50 p-1 rounded">
                                            {block.parentHash.substring(0, 10)}...
                                        </span>
                                    </div>
                                    <div className="text-xs">
                                        <span className="text-emerald-500/70 block">Block Hash</span>
                                        <span className="text-emerald-400 font-mono text-[10px] break-all block truncate bg-emerald-500/10 p-1 rounded">
                                            {block.hash.substring(0, 10)}...
                                        </span>
                                    </div>
                                </div>

                                <div className="bg-black/30 rounded p-2 mt-2 space-y-1">
                                    <div className="flex justify-between text-[10px] text-gray-400 font-mono">
                                        <span>Gas Used:</span>
                                        <span className="text-orange-400">{block.gasUsed.toLocaleString()}</span>
                                    </div>
                                    <div className="flex justify-between text-[10px] text-gray-400 font-mono">
                                        <span>Miner:</span>
                                        <span className="text-blue-400 truncate w-20">{block.miner}</span>
                                    </div>
                                    <div className="border-t border-gray-800 my-1 pt-1">
                                        <p className="text-[10px] text-gray-300 font-mono">
                                            <span className="text-indigo-400">Txns:</span> {block.transactions.length}
                                        </p>
                                        {block.transactions.length > 0 && (
                                            <p className="text-[10px] text-gray-500 font-mono truncate mt-0.5">
                                                {block.transactions[0].data?.action || typeof block.transactions[0].data === 'string' ? (block.transactions[0].data.action || block.transactions[0].data) : 'System'}
                                            </p>
                                        )}
                                    </div>
                                </div>
                            </div>

                            {/* Connector Arrow (Desktop) */}
                            {index !== chain.length - 1 && (
                                <div className="absolute top-1/2 -right-3 hidden lg:block text-gray-600 z-10 bg-app p-1 rounded-full">
                                    <Link size={16} />
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div >
    );
};



export default BlockchainView;
