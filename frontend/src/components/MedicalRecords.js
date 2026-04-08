import React, { useState } from 'react';
import { FileText, Image as ImageIcon, X, Eye, File, Calendar, Maximize2 } from 'lucide-react';
import Card from './ui/Card';
import Button from './ui/Button';

const MedicalRecords = () => {
    const [activeTab, setActiveTab] = useState('all');
    const [selectedRecord, setSelectedRecord] = useState(null); // Lightbox State

    // Sample Data (Hardcoded for Demo)
    const [records, setRecords] = useState([
        {
            id: 1,
            title: 'MRI Knee Scan',
            type: 'image',
            date: '2023-11-15',
            doctor: 'Dr. Sarah Johnson',
            category: 'scan',
            url: '/assets/mri_scan.png',
            details: 'T2 Sequence showing minimal joint effusion. Ligaments intact.'
        },
        {
            id: 2,
            title: 'Chest X-Ray (PA View)',
            type: 'image',
            date: '2023-12-01',
            doctor: 'Dr. Mike Smith',
            category: 'scan',
            url: '/assets/xray_chest.png',
            details: 'Clear lung fields. No cardiomegaly or pulmonary edema.'
        },
        {
            id: 3,
            title: 'Complete Blood Count',
            type: 'report',
            date: '2023-10-20',
            doctor: 'Pathology Lab',
            category: 'report',
            url: '/assets/lab_report.png',
            details: 'Hemoglobin 14.5 g/dL. WBC count 6.8k. All within normal range.'
        },
        {
            id: 4,
            title: 'Vaccination Certificate',
            type: 'report',
            date: '2023-01-15',
            doctor: 'Clinic Staff',
            category: 'vaccine',
            url: null
        }
    ]);



    const filteredRecords = activeTab === 'all'
        ? records
        : records.filter(r => r.category === activeTab || (activeTab === 'scan' && r.type === 'image'));

    return (
        <div className="space-y-6 animate-fade-in pb-10">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h2 className="text-3xl font-bold text-white">Medical Records</h2>
                    <p className="text-gray-400 mt-1">Manage your reports, scans, and documents</p>
                </div>
            </div>


            {/* --- Lightbox Modal --- */}
            {
                selectedRecord && (
                    <div className="fixed inset-0 z-[100] bg-black/90 backdrop-blur-xl flex items-center justify-center p-4 animate-fade-in" onClick={() => setSelectedRecord(null)}>
                        <div className="max-w-5xl w-full h-[90vh] flex flex-col md:flex-row gap-6" onClick={e => e.stopPropagation()}>

                            {/* Image Area */}
                            <div className="flex-1 bg-black rounded-2xl overflow-hidden flex items-center justify-center border border-gray-800 shadow-2xl relative">
                                {selectedRecord.url ? (
                                    <img src={selectedRecord.url} alt={selectedRecord.title} className="max-w-full max-h-full object-contain" />
                                ) : (
                                    <FileText size={100} className="text-gray-600" />
                                )}
                                <button onClick={() => setSelectedRecord(null)} className="absolute top-4 right-4 p-2 bg-black/50 text-white rounded-full hover:bg-red-500/80 transition-colors">
                                    <X size={24} />
                                </button>
                            </div>

                            {/* Sidebar Details */}
                            <div className="w-full md:w-80 bg-gray-900/80 backdrop-blur-md rounded-2xl p-6 border border-gray-700 flex flex-col">
                                <div>
                                    <h3 className="text-xl font-bold text-white mb-2">{selectedRecord.title}</h3>
                                    <span className="px-2 py-1 bg-indigo-500/20 text-indigo-400 text-xs rounded-md uppercase tracking-wider font-semibold">
                                        {selectedRecord.category}
                                    </span>
                                </div>

                                <div className="mt-8 space-y-6">
                                    <div>
                                        <p className="text-sm text-gray-500 mb-1">Doctor / Source</p>
                                        <p className="text-gray-200 font-medium flex items-center gap-2">
                                            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                                            {selectedRecord.doctor}
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-500 mb-1">Date Added</p>
                                        <p className="text-gray-200 font-medium">{selectedRecord.date}</p>
                                    </div>
                                    {selectedRecord.details && (
                                        <div className="p-4 bg-gray-800 rounded-xl border border-gray-700">
                                            <p className="text-sm text-gray-400 mb-2">AI Analysis</p>
                                            <p className="text-sm text-gray-300 leading-relaxed">
                                                {selectedRecord.details}
                                            </p>
                                        </div>
                                    )}
                                </div>

                                <div className="mt-auto pt-6">
                                    <Button variant="primary" className="w-full justify-center">Download</Button>
                                </div>
                            </div>
                        </div>
                    </div>
                )
            }

            {/* Upload Modal (Overlay) - Removed in favor of PrescriptionUpload */}

            {/* Filters */}
            <div className="flex gap-2 overflow-x-auto pb-2">
                {['all', 'report', 'scan', 'vaccine'].map(tab => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={`px-4 py-2 rounded-full text-sm font-medium capitalize transition-all ${activeTab === tab
                            ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/40 transform scale-105'
                            : 'bg-gray-800 text-gray-400 hover:bg-gray-700 border border-gray-700'
                            }`}
                    >
                        {tab === 'all' ? 'All Documents' : tab + 's'}
                    </button>
                ))}
            </div>

            {/* Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredRecords.map(record => (
                    <Card
                        key={record.id}
                        onClick={() => setSelectedRecord(record)}
                        className="group cursor-pointer hover:-translate-y-2 hover:shadow-neon transition-all duration-300 border-gray-800 bg-gray-900/50"
                    >
                        <div className="relative aspect-[4/3] bg-gray-800 rounded-lg overflow-hidden mb-4 border border-gray-700">
                            {record.url ? (
                                <img
                                    src={record.url}
                                    alt={record.title}
                                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                                />
                            ) : (
                                <div className="w-full h-full flex items-center justify-center bg-gray-800 group-hover:bg-gray-750 transition-colors">
                                    <FileText size={48} className="text-gray-600 group-hover:text-indigo-400 transition-colors" />
                                </div>
                            )}

                            <div className="absolute inset-0 bg-black/40 backdrop-blur-[2px] opacity-0 group-hover:opacity-100 transition-all duration-300 flex items-center justify-center">
                                <div className="bg-indigo-600/90 p-3 rounded-full shadow-lg transform translate-y-4 group-hover:translate-y-0 transition-transform duration-300">
                                    <Maximize2 size={24} className="text-white" />
                                </div>
                            </div>
                        </div>

                        <div className="flex items-start justify-between">
                            <div>
                                <h4 className="font-bold text-gray-200 line-clamp-1 group-hover:text-indigo-400 transition-colors">{record.title}</h4>
                                <div className="flex items-center gap-2 mt-1 text-sm text-gray-400">
                                    <Calendar size={14} />
                                    <span>{record.date}</span>
                                </div>
                                <p className="text-xs text-indigo-300 mt-2 font-medium bg-indigo-500/10 inline-block px-2 py-1 rounded border border-indigo-500/20">
                                    {record.doctor}
                                </p>
                            </div>

                            <div className={`p-2 rounded-lg ${record.type === 'image' ? 'bg-purple-900/30 text-purple-400' : 'bg-blue-900/30 text-blue-400'
                                }`}>
                                {record.type === 'image' ? <ImageIcon size={18} /> : <File size={18} />}
                            </div>
                        </div>
                    </Card>
                ))}
            </div>
        </div >
    );
};

export default MedicalRecords;
