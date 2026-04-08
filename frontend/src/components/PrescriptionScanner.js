import React, { useState } from 'react';
import { Upload, X, FileText, Check, Loader, CheckCircle2, Pill, Activity, User, AlertCircle } from 'lucide-react';

const API_URL = 'http://localhost:8000';

const PrescriptionScanner = ({ userId, onUploadComplete }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [file, setFile] = useState(null);
    const [isUploading, setIsUploading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleFileChange = (e) => {
        if (e.target.files[0]) {
            setFile(e.target.files[0]);
            setResult(null);
            setError(null);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setIsUploading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);
        formData.append('user_id', userId);

        try {
            const response = await fetch(`${API_URL}/prescriptions/upload`, {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                console.log("Analysis Result:", data);
                setResult(data.analysis);
                if (onUploadComplete) onUploadComplete();
            } else {
                throw new Error('Upload failed');
            }
        } catch (error) {
            console.error('Error:', error);
            setError('Failed to analyze prescription. Please try again.');
        } finally {
            setIsUploading(false);
        }
    };

    // Helper to render medication table
    const renderMedications = (meds) => {
        if (!meds || meds.length === 0) return <p className="text-gray-400 italic">No medications detected.</p>;

        return (
            <div className="overflow-hidden rounded-xl border border-gray-700">
                <table className="w-full text-left text-sm text-gray-300">
                    <thead className="bg-gray-800 text-gray-400 uppercase font-medium text-xs">
                        <tr>
                            <th className="px-4 py-3">Medicine</th>
                            <th className="px-4 py-3">Dosage</th>
                            <th className="px-4 py-3">Frequency</th>
                            <th className="px-4 py-3">Duration</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-700 bg-gray-800/50">
                        {meds.map((med, idx) => (
                            <tr key={idx} className="hover:bg-gray-700/50 transition-colors">
                                <td className="px-4 py-3 font-medium text-white">{med.name || '-'}</td>
                                <td className="px-4 py-3">{med.dosage || '-'}</td>
                                <td className="px-4 py-3">{med.frequency || '-'}</td>
                                <td className="px-4 py-3">{med.duration || '-'}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        );
    };

    if (!isOpen) {
        return (
            <button
                onClick={() => setIsOpen(true)}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-indigo-600 to-violet-600 text-white rounded-lg hover:from-indigo-700 hover:to-violet-700 transition-all shadow-lg hover:shadow-indigo-500/25"
            >
                <div className="p-1 bg-white/20 rounded-md">
                    <Upload size={16} />
                </div>
                <span className="font-medium">Scan Prescription</span>
            </button>
        );
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm animate-fade-in p-4">
            <div className="bg-gray-900 rounded-2xl border border-gray-700 shadow-2xl w-[600px] max-w-full max-h-[90vh] overflow-hidden flex flex-col">
                {/* Header */}
                <div className="flex justify-between items-center p-6 border-b border-gray-800 bg-gray-900/50">
                    <div>
                        <h3 className="text-xl font-bold text-white flex items-center gap-2">
                            <FileText className="text-indigo-400" />
                            Smart Prescription Scanner
                        </h3>

                    </div>
                    <button onClick={() => setIsOpen(false)} className="text-gray-400 hover:text-white p-2 hover:bg-gray-800 rounded-lg transition-colors">
                        <X size={24} />
                    </button>
                </div>

                <div className="p-6 overflow-y-auto custom-scrollbar flex-1">
                    {!result ? (
                        <div className="space-y-6">
                            {/* Upload Area */}
                            <div className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${file ? 'border-indigo-500/50 bg-indigo-500/5' : 'border-gray-700 bg-gray-800/30 hover:bg-gray-800/50'}`}>
                                <input
                                    type="file"
                                    accept="image/*"
                                    onChange={handleFileChange}
                                    className="hidden"
                                    id="prescription-file-scan"
                                />
                                <label htmlFor="prescription-file-scan" className="cursor-pointer flex flex-col items-center gap-4">
                                    <div className={`p-4 rounded-full ${file ? 'bg-indigo-500 text-white' : 'bg-gray-800 text-indigo-400'}`}>
                                        <Upload size={32} />
                                    </div>
                                    <div>
                                        <p className="text-lg font-medium text-white">{file ? 'Change Image' : 'Click to Upload Prescription'}</p>
                                        <p className="text-sm text-gray-400 mt-1">{file ? file.name : 'JPG, PNG up to 10MB'}</p>
                                    </div>
                                </label>
                            </div>

                            {/* Error Message */}
                            {error && (
                                <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-3 text-red-400">
                                    <AlertCircle size={20} />
                                    <p className="text-sm">{error}</p>
                                </div>
                            )}

                            {/* Action Button */}
                            <button
                                onClick={handleUpload}
                                disabled={!file || isUploading}
                                className="w-full py-4 bg-gradient-to-r from-indigo-600 to-violet-600 text-white rounded-xl font-bold hover:shadow-lg hover:shadow-indigo-500/25 disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-3 transition-all"
                            >
                                {isUploading ? (
                                    <>
                                        <Loader size={20} className="animate-spin" />
                                        Analyzing Prescription...
                                    </>
                                ) : (
                                    <>
                                        <Activity size={20} />
                                        Analyze with AI
                                    </>
                                )}
                            </button>
                        </div>
                    ) : (
                        <div className="space-y-6 animate-fade-in">
                            {/* Success Banner */}
                            <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4 flex items-center gap-3">
                                <div className="p-2 bg-emerald-500/20 rounded-full text-emerald-400">
                                    <CheckCircle2 size={20} />
                                </div>
                                <div>
                                    <h4 className="font-bold text-emerald-400">Analysis Complete</h4>
                                    <p className="text-sm text-emerald-200/70">Prescription data has been extracted and saved.</p>
                                </div>
                            </div>

                            {/* Patient Info */}
                            {(result.patient_name || result.doctor_name) && (
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
                                        <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Patient</p>
                                        <p className="font-medium text-white flex items-center gap-2">
                                            <User size={16} className="text-indigo-400" />
                                            {result.patient_name || "Unknown"}
                                        </p>
                                    </div>
                                    <div className="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
                                        <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Doctor</p>
                                        <p className="font-medium text-white">{result.doctor_name || "Unknown"}</p>
                                    </div>
                                </div>
                            )}

                            {/* Medications */}
                            <div>
                                <h4 className="text-sm font-bold text-gray-300 mb-3 flex items-center gap-2">
                                    <Pill size={16} className="text-purple-400" />
                                    Prescribed Medications
                                </h4>
                                {renderMedications(result.medications)}
                            </div>

                            {/* Diagnosis & Advice */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="bg-gray-800/30 p-4 rounded-xl border border-gray-700">
                                    <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-2">Diagnosis</h4>
                                    <p className="text-sm text-gray-300">{result.diagnosis || "Not specified"}</p>
                                </div>
                                <div className="bg-gray-800/30 p-4 rounded-xl border border-gray-700">
                                    <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-2">Advice / Instructions</h4>
                                    <p className="text-sm text-gray-300">{result.advice || "None"}</p>
                                </div>
                            </div>

                            {/* Footer Actions */}
                            <div className="pt-4 border-t border-gray-800 flex gap-4">
                                <button
                                    onClick={() => { setFile(null); setResult(null); }}
                                    className="flex-1 py-3 bg-gray-800 text-white rounded-xl hover:bg-gray-700 font-medium transition-colors"
                                >
                                    Scan Another
                                </button>
                                <button
                                    onClick={() => setIsOpen(false)}
                                    className="flex-1 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 font-medium transition-colors"
                                >
                                    Done
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default PrescriptionScanner;
