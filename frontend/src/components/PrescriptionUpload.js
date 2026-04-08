import React, { useState } from 'react';
import { Upload, X, FileText, Check, Loader, CheckCircle2 } from 'lucide-react';

const API_URL = 'http://localhost:8000';

const PrescriptionUpload = ({ userId, onUploadComplete }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [file, setFile] = useState(null);
    const [isUploading, setIsUploading] = useState(false);
    const [result, setResult] = useState(null);

    const handleFileChange = (e) => {
        if (e.target.files[0]) {
            setFile(e.target.files[0]);
            setResult(null);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setIsUploading(true);
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
                setResult(data);
                if (onUploadComplete) onUploadComplete();
            } else {
                throw new Error('Upload failed');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to upload prescription');
        } finally {
            setIsUploading(false);
        }
    };

    if (!isOpen) {
        return (
            <button
                onClick={() => setIsOpen(true)}
                className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors shadow-lg"
            >
                <Upload size={18} />
                <span>Upload Prescription</span>
            </button>
        );
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in">
            <div className="bg-gray-900 rounded-2xl border border-gray-700 shadow-2xl p-6 w-[500px] max-w-full m-4">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="text-xl font-bold text-white flex items-center gap-2">
                        <FileText className="text-indigo-400" />
                        Analyze Prescription
                    </h3>
                    <button onClick={() => setIsOpen(false)} className="text-gray-400 hover:text-white">
                        <X size={24} />
                    </button>
                </div>

                {!result ? (
                    <div className="space-y-6">
                        <div className="border-2 border-dashed border-gray-700 rounded-xl p-8 text-center bg-gray-800/50 hover:bg-gray-800 transition-colors">
                            <input
                                type="file"
                                accept="image/*"
                                onChange={handleFileChange}
                                className="hidden"
                                id="prescription-file"
                            />
                            <label htmlFor="prescription-file" className="cursor-pointer flex flex-col items-center gap-3">
                                <div className="p-4 bg-indigo-500/20 rounded-full text-indigo-400">
                                    <Upload size={32} />
                                </div>
                                <div>
                                    <p className="text-lg font-medium text-white">Click to upload image</p>
                                    <p className="text-sm text-gray-400">JPG, PNG up to 10MB</p>
                                </div>
                            </label>
                        </div>

                        {file && (
                            <div className="flex items-center gap-3 p-3 bg-gray-800 rounded-lg">
                                <FileText size={20} className="text-indigo-400" />
                                <span className="text-sm text-gray-200 truncate flex-1">{file.name}</span>
                                <button onClick={() => setFile(null)} className="text-gray-500 hover:text-red-400">
                                    <X size={16} />
                                </button>
                            </div>
                        )}

                        <button
                            onClick={handleUpload}
                            disabled={!file || isUploading}
                            className="w-full py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2"
                        >
                            {isUploading ? (
                                <>
                                    <Loader size={18} className="animate-spin" />
                                    Analyzing...
                                </>
                            ) : (
                                <>
                                    <Check size={18} />
                                    Analyze with AI
                                </>
                            )}
                        </button>
                    </div>
                ) : (
                    <div className="space-y-6">
                        <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4 flex items-center gap-3">
                            <CheckCircle2 className="text-emerald-400" size={24} />
                            <div>
                                <h4 className="font-bold text-emerald-400">Analysis Complete</h4>
                                <p className="text-sm text-emerald-200/70">Record added to your history.</p>
                            </div>
                        </div>

                        <div className="bg-gray-800/80 p-5 rounded-xl border border-gray-700 max-h-80 overflow-y-auto custom-scrollbar">
                            <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                                <Check size={14} />
                                Verified Extraction
                            </h4>
                            <div className="text-sm text-gray-200 whitespace-pre-wrap font-sans leading-relaxed">
                                {result.analysis}
                            </div>
                        </div>

                        <button
                            onClick={() => { setIsOpen(false); setFile(null); setResult(null); }}
                            className="w-full py-3 bg-gray-700 text-white rounded-xl hover:bg-gray-600 font-medium"
                        >
                            Close
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default PrescriptionUpload;
