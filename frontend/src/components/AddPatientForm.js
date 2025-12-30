import React, { useState } from 'react';
import { UserPlus, X, AlertCircle, Heart, Activity, Thermometer, Droplet, Zap, Waves, TrendingUp, ToggleLeft, ToggleRight } from 'lucide-react';
import Card from './ui/Card';
import Button from './ui/Button';

const AddPatientForm = ({ onAddPatient, onClose }) => {
    const [vitalEntryMode, setVitalEntryMode] = useState('auto'); // 'auto' or 'manual'
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        age: '',
        gender: 'M',
        phone: '',
        address: '',
        bloodType: 'O+',
        height: '',
        weight: '',
        emergencyContact: '',
        // Medical conditions
        medicalCondition: 'healthy',
        allergies: 'None known',
        chronicConditions: 'None',
        currentSymptoms: '',
        // Manual vitals
        heartRate: '',
        spo2: '',
        temperature: '',
        bp: '',
        stress: '',
        respiratoryRate: '',
        glucose: ''
    });

    const [errors, setErrors] = useState({});

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
        if (errors[e.target.name]) {
            setErrors({ ...errors, [e.target.name]: '' });
        }
    };

    const validate = () => {
        const newErrors = {};
        if (!formData.name.trim()) newErrors.name = 'Name is required';
        if (!formData.email.trim()) newErrors.email = 'Email is required';
        if (!formData.age || formData.age < 1 || formData.age > 120) newErrors.age = 'Valid age required';

        // Validate manual vitals if in manual mode
        if (vitalEntryMode === 'manual') {
            if (!formData.heartRate || formData.heartRate < 30 || formData.heartRate > 200) newErrors.heartRate = 'Valid heart rate required (30-200)';
            if (!formData.spo2 || formData.spo2 < 70 || formData.spo2 > 100) newErrors.spo2 = 'Valid SpO₂ required (70-100)';
            if (!formData.temperature || formData.temperature < 35 || formData.temperature > 42) newErrors.temperature = 'Valid temperature required (35-42)';
            if (!formData.bp.trim()) newErrors.bp = 'Blood pressure required (e.g., 120/80)';
            if (!formData.stress || formData.stress < 0 || formData.stress > 5) newErrors.stress = 'Valid stress level required (0-5)';
            if (!formData.respiratoryRate || formData.respiratoryRate < 8 || formData.respiratoryRate > 40) newErrors.respiratoryRate = 'Valid respiratory rate required (8-40)';
            if (!formData.glucose || formData.glucose < 40 || formData.glucose > 400) newErrors.glucose = 'Valid glucose required (40-400)';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const generateVitalsFromCondition = (condition) => {
        const baseVitals = {
            healthy: {
                heartRate: 70 + Math.floor(Math.random() * 10),
                spo2: 97 + Math.floor(Math.random() * 3),
                temperature: 36.5 + Math.random() * 0.5,
                bp: '120/80',
                stress: 1 + Math.random() * 1.5,
                respiratoryRate: 16,
                glucose: 90 + Math.floor(Math.random() * 20)
            },
            hypertension: {
                heartRate: 85 + Math.floor(Math.random() * 15),
                spo2: 95 + Math.floor(Math.random() * 3),
                temperature: 36.8 + Math.random() * 0.4,
                bp: '145/95',
                stress: 3 + Math.random() * 1.5,
                respiratoryRate: 18,
                glucose: 100 + Math.floor(Math.random() * 30)
            },
            diabetes: {
                heartRate: 75 + Math.floor(Math.random() * 10),
                spo2: 96 + Math.floor(Math.random() * 2),
                temperature: 36.6 + Math.random() * 0.3,
                bp: '130/85',
                stress: 2.5 + Math.random() * 1,
                respiratoryRate: 17,
                glucose: 150 + Math.floor(Math.random() * 50)
            },
            respiratory: {
                heartRate: 80 + Math.floor(Math.random() * 12),
                spo2: 90 + Math.floor(Math.random() * 4),
                temperature: 37.0 + Math.random() * 1.0,
                bp: '125/82',
                stress: 3 + Math.random() * 1,
                respiratoryRate: 22,
                glucose: 95 + Math.floor(Math.random() * 20)
            },
            cardiac: {
                heartRate: 95 + Math.floor(Math.random() * 20),
                spo2: 92 + Math.floor(Math.random() * 4),
                temperature: 36.8 + Math.random() * 0.6,
                bp: '140/90',
                stress: 4 + Math.random() * 1,
                respiratoryRate: 20,
                glucose: 105 + Math.floor(Math.random() * 25)
            }
        };

        return baseVitals[condition] || baseVitals.healthy;
    };

    const handleSubmit = (e) => {
        e.preventDefault();

        if (!validate()) {
            return;
        }

        // Get vitals based on mode
        const vitals = vitalEntryMode === 'manual' ? {
            heartRate: parseInt(formData.heartRate),
            spo2: parseInt(formData.spo2),
            temperature: parseFloat(formData.temperature),
            bp: formData.bp,
            stress: parseFloat(formData.stress),
            respiratoryRate: parseInt(formData.respiratoryRate),
            glucose: parseInt(formData.glucose)
        } : generateVitalsFromCondition(formData.medicalCondition);

        const newPatient = {
            id: Date.now(),
            name: formData.name,
            email: formData.email,
            age: parseInt(formData.age),
            gender: formData.gender,
            user_type: 'patient',
            phone: formData.phone,
            address: formData.address,
            bloodType: formData.bloodType,
            height: formData.height,
            weight: formData.weight,
            emergencyContact: formData.emergencyContact,
            allergies: formData.allergies,
            chronicConditions: formData.chronicConditions,
            medicalCondition: formData.medicalCondition,
            currentSymptoms: formData.currentSymptoms,
            vitals: vitals
        };

        onAddPatient(newPatient);
    };

    const conditionDescriptions = {
        healthy: 'Normal vitals, no chronic conditions',
        hypertension: 'Elevated blood pressure, increased heart rate',
        diabetes: 'High blood glucose, metabolic concerns',
        respiratory: 'Reduced oxygen saturation, breathing issues',
        cardiac: 'Heart rhythm irregularities, elevated HR'
    };

    return (
        <div className="fixed inset-0 z-[100] bg-black/95 backdrop-blur-xl flex items-start justify-center p-4 animate-fade-in overflow-y-auto">
            <div className="w-full max-w-5xl my-8">
                <Card className="bg-gray-900/95 border-gray-700 relative">
                    <button onClick={onClose} className="sticky top-4 right-4 float-right p-2 bg-gray-800 hover:bg-red-500/80 text-white rounded-full transition-colors z-20 shadow-lg">
                        <X size={20} />
                    </button>

                    <div className="mb-6">
                        <h2 className="text-3xl font-bold text-white flex items-center gap-3">
                            <UserPlus size={32} className="text-indigo-400" />
                            Add New Patient
                        </h2>
                        <p className="text-gray-400 mt-2">Enter patient details and vital signs</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        {/* Personal Information - Same as before */}
                        <div>
                            <h3 className="text-lg font-bold text-white mb-4 border-b border-gray-800 pb-2">Personal Information</h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="text-sm text-gray-400 mb-1 block">Full Name *</label>
                                    <input type="text" name="name" value={formData.name} onChange={handleChange} className={`input-field ${errors.name ? 'border-red-500' : ''}`} placeholder="John Doe" />
                                    {errors.name && <p className="text-red-400 text-xs mt-1">{errors.name}</p>}
                                </div>

                                <div>
                                    <label className="text-sm text-gray-400 mb-1 block">Email *</label>
                                    <input type="email" name="email" value={formData.email} onChange={handleChange} className={`input-field ${errors.email ? 'border-red-500' : ''}`} placeholder="john.doe@example.com" />
                                    {errors.email && <p className="text-red-400 text-xs mt-1">{errors.email}</p>}
                                </div>

                                <div>
                                    <label className="text-sm text-gray-400 mb-1 block">Age *</label>
                                    <input type="number" name="age" value={formData.age} onChange={handleChange} className={`input-field ${errors.age ? 'border-red-500' : ''}`} placeholder="35" min="1" max="120" />
                                    {errors.age && <p className="text-red-400 text-xs mt-1">{errors.age}</p>}
                                </div>

                                <div>
                                    <label className="text-sm text-gray-400 mb-1 block">Gender</label>
                                    <select name="gender" value={formData.gender} onChange={handleChange} className="input-field">
                                        <option value="M">Male</option>
                                        <option value="F">Female</option>
                                        <option value="O">Other</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="text-sm text-gray-400 mb-1 block">Phone</label>
                                    <input type="tel" name="phone" value={formData.phone} onChange={handleChange} className="input-field" placeholder="+1 (555) 123-4567" />
                                </div>

                                <div>
                                    <label className="text-sm text-gray-400 mb-1 block">Blood Type</label>
                                    <select name="bloodType" value={formData.bloodType} onChange={handleChange} className="input-field">
                                        <option value="A+">A+</option>
                                        <option value="A-">A-</option>
                                        <option value="B+">B+</option>
                                        <option value="B-">B-</option>
                                        <option value="AB+">AB+</option>
                                        <option value="AB-">AB-</option>
                                        <option value="O+">O+</option>
                                        <option value="O-">O-</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="text-sm text-gray-400 mb-1 block">Height (cm)</label>
                                    <input type="number" name="height" value={formData.height} onChange={handleChange} className="input-field" placeholder="170" />
                                </div>

                                <div>
                                    <label className="text-sm text-gray-400 mb-1 block">Weight (kg)</label>
                                    <input type="number" name="weight" value={formData.weight} onChange={handleChange} className="input-field" placeholder="70" />
                                </div>

                                <div className="md:col-span-2">
                                    <label className="text-sm text-gray-400 mb-1 block">Address</label>
                                    <input type="text" name="address" value={formData.address} onChange={handleChange} className="input-field" placeholder="123 Main St, City, State, ZIP" />
                                </div>

                                <div className="md:col-span-2">
                                    <label className="text-sm text-gray-400 mb-1 block">Emergency Contact</label>
                                    <input type="text" name="emergencyContact" value={formData.emergencyContact} onChange={handleChange} className="input-field" placeholder="Jane Doe - +1 (555) 987-6543" />
                                </div>
                            </div>
                        </div>

                        {/* Medical Condition */}
                        <div>
                            <h3 className="text-lg font-bold text-white mb-4 border-b border-gray-800 pb-2">Medical Information</h3>
                            <div className="space-y-4">
                                <div>
                                    <label className="text-sm text-gray-400 mb-1 block">Known Allergies</label>
                                    <input type="text" name="allergies" value={formData.allergies} onChange={handleChange} className="input-field" placeholder="Penicillin, Peanuts, etc." />
                                </div>

                                <div>
                                    <label className="text-sm text-gray-400 mb-1 block">Chronic Conditions</label>
                                    <input type="text" name="chronicConditions" value={formData.chronicConditions} onChange={handleChange} className="input-field" placeholder="Asthma, Arthritis, etc." />
                                </div>

                                <div>
                                    <label className="text-sm text-gray-400 mb-1 block">Current Symptoms</label>
                                    <textarea name="currentSymptoms" value={formData.currentSymptoms} onChange={handleChange} className="input-field" rows="3" placeholder="Describe current symptoms..." />
                                </div>
                            </div>
                        </div>

                        {/* Vital Signs Entry Mode Toggle */}
                        <div>
                            <div className="flex items-center justify-between mb-4 border-b border-gray-800 pb-2">
                                <h3 className="text-lg font-bold text-white">Vital Signs</h3>
                                <button
                                    type="button"
                                    onClick={() => setVitalEntryMode(vitalEntryMode === 'auto' ? 'manual' : 'auto')}
                                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 border border-gray-700 transition-all"
                                >
                                    {vitalEntryMode === 'auto' ? <ToggleLeft size={20} className="text-indigo-400" /> : <ToggleRight size={20} className="text-emerald-400" />}
                                    <span className="text-sm font-medium text-white">
                                        {vitalEntryMode === 'auto' ? 'Auto-Generate' : 'Manual Entry'}
                                    </span>
                                </button>
                            </div>

                            {vitalEntryMode === 'auto' ? (
                                /* Auto-Generate Mode */
                                <div className="space-y-4">
                                    <div>
                                        <label className="text-sm text-gray-400 mb-2 block">Select Condition (vitals will be generated automatically)</label>
                                        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
                                            {Object.entries(conditionDescriptions).map(([key, desc]) => (
                                                <button
                                                    key={key}
                                                    type="button"
                                                    onClick={() => setFormData({ ...formData, medicalCondition: key })}
                                                    className={`p-4 rounded-xl border-2 transition-all text-left ${formData.medicalCondition === key
                                                            ? 'border-indigo-500 bg-indigo-500/20'
                                                            : 'border-gray-700 bg-gray-800/50 hover:border-gray-600'
                                                        }`}
                                                >
                                                    <p className="font-bold text-white capitalize mb-1">{key}</p>
                                                    <p className="text-xs text-gray-400">{desc}</p>
                                                </button>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Preview */}
                                    <div className="bg-indigo-500/10 border border-indigo-500/20 p-4 rounded-xl">
                                        <h4 className="text-indigo-400 font-bold mb-3 flex items-center gap-2">
                                            <Activity size={16} />
                                            Generated Vitals Preview
                                        </h4>
                                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                                            {(() => {
                                                const vitals = generateVitalsFromCondition(formData.medicalCondition);
                                                return (
                                                    <>
                                                        <div className="flex items-center gap-2">
                                                            <Heart size={14} className="text-rose-400" />
                                                            <span className="text-gray-300">HR: {vitals.heartRate} bpm</span>
                                                        </div>
                                                        <div className="flex items-center gap-2">
                                                            <Activity size={14} className="text-cyan-400" />
                                                            <span className="text-gray-300">SpO₂: {vitals.spo2}%</span>
                                                        </div>
                                                        <div className="flex items-center gap-2">
                                                            <Thermometer size={14} className="text-amber-400" />
                                                            <span className="text-gray-300">Temp: {vitals.temperature.toFixed(1)}°C</span>
                                                        </div>
                                                        <div className="flex items-center gap-2">
                                                            <Droplet size={14} className="text-pink-400" />
                                                            <span className="text-gray-300">BP: {vitals.bp}</span>
                                                        </div>
                                                        <div className="flex items-center gap-2">
                                                            <Zap size={14} className="text-violet-400" />
                                                            <span className="text-gray-300">Stress: {vitals.stress.toFixed(1)}/5</span>
                                                        </div>
                                                        <div className="flex items-center gap-2">
                                                            <Waves size={14} className="text-blue-400" />
                                                            <span className="text-gray-300">RR: {vitals.respiratoryRate}/min</span>
                                                        </div>
                                                        <div className="flex items-center gap-2">
                                                            <TrendingUp size={14} className="text-emerald-400" />
                                                            <span className="text-gray-300">Glucose: {vitals.glucose} mg/dL</span>
                                                        </div>
                                                    </>
                                                );
                                            })()}
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                /* Manual Entry Mode */
                                <div className="bg-emerald-500/10 border border-emerald-500/20 p-6 rounded-xl">
                                    <h4 className="text-emerald-400 font-bold mb-4 flex items-center gap-2">
                                        <Activity size={16} />
                                        Enter Vital Signs Manually
                                    </h4>
                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                        <div>
                                            <label className="text-sm text-gray-400 mb-1 block flex items-center gap-2">
                                                <Heart size={14} className="text-rose-400" />
                                                Heart Rate (bpm) *
                                            </label>
                                            <input
                                                type="number"
                                                name="heartRate"
                                                value={formData.heartRate}
                                                onChange={handleChange}
                                                className={`input-field ${errors.heartRate ? 'border-red-500' : ''}`}
                                                placeholder="72"
                                                min="30"
                                                max="200"
                                            />
                                            {errors.heartRate && <p className="text-red-400 text-xs mt-1">{errors.heartRate}</p>}
                                        </div>

                                        <div>
                                            <label className="text-sm text-gray-400 mb-1 block flex items-center gap-2">
                                                <Activity size={14} className="text-cyan-400" />
                                                SpO₂ (%) *
                                            </label>
                                            <input
                                                type="number"
                                                name="spo2"
                                                value={formData.spo2}
                                                onChange={handleChange}
                                                className={`input-field ${errors.spo2 ? 'border-red-500' : ''}`}
                                                placeholder="98"
                                                min="70"
                                                max="100"
                                            />
                                            {errors.spo2 && <p className="text-red-400 text-xs mt-1">{errors.spo2}</p>}
                                        </div>

                                        <div>
                                            <label className="text-sm text-gray-400 mb-1 block flex items-center gap-2">
                                                <Thermometer size={14} className="text-amber-400" />
                                                Temperature (°C) *
                                            </label>
                                            <input
                                                type="number"
                                                step="0.1"
                                                name="temperature"
                                                value={formData.temperature}
                                                onChange={handleChange}
                                                className={`input-field ${errors.temperature ? 'border-red-500' : ''}`}
                                                placeholder="36.6"
                                                min="35"
                                                max="42"
                                            />
                                            {errors.temperature && <p className="text-red-400 text-xs mt-1">{errors.temperature}</p>}
                                        </div>

                                        <div>
                                            <label className="text-sm text-gray-400 mb-1 block flex items-center gap-2">
                                                <Droplet size={14} className="text-pink-400" />
                                                Blood Pressure *
                                            </label>
                                            <input
                                                type="text"
                                                name="bp"
                                                value={formData.bp}
                                                onChange={handleChange}
                                                className={`input-field ${errors.bp ? 'border-red-500' : ''}`}
                                                placeholder="120/80"
                                            />
                                            {errors.bp && <p className="text-red-400 text-xs mt-1">{errors.bp}</p>}
                                        </div>

                                        <div>
                                            <label className="text-sm text-gray-400 mb-1 block flex items-center gap-2">
                                                <Zap size={14} className="text-violet-400" />
                                                Stress Level (0-5) *
                                            </label>
                                            <input
                                                type="number"
                                                step="0.1"
                                                name="stress"
                                                value={formData.stress}
                                                onChange={handleChange}
                                                className={`input-field ${errors.stress ? 'border-red-500' : ''}`}
                                                placeholder="2.5"
                                                min="0"
                                                max="5"
                                            />
                                            {errors.stress && <p className="text-red-400 text-xs mt-1">{errors.stress}</p>}
                                        </div>

                                        <div>
                                            <label className="text-sm text-gray-400 mb-1 block flex items-center gap-2">
                                                <Waves size={14} className="text-blue-400" />
                                                Respiratory Rate *
                                            </label>
                                            <input
                                                type="number"
                                                name="respiratoryRate"
                                                value={formData.respiratoryRate}
                                                onChange={handleChange}
                                                className={`input-field ${errors.respiratoryRate ? 'border-red-500' : ''}`}
                                                placeholder="16"
                                                min="8"
                                                max="40"
                                            />
                                            {errors.respiratoryRate && <p className="text-red-400 text-xs mt-1">{errors.respiratoryRate}</p>}
                                        </div>

                                        <div>
                                            <label className="text-sm text-gray-400 mb-1 block flex items-center gap-2">
                                                <TrendingUp size={14} className="text-emerald-400" />
                                                Glucose (mg/dL) *
                                            </label>
                                            <input
                                                type="number"
                                                name="glucose"
                                                value={formData.glucose}
                                                onChange={handleChange}
                                                className={`input-field ${errors.glucose ? 'border-red-500' : ''}`}
                                                placeholder="95"
                                                min="40"
                                                max="400"
                                            />
                                            {errors.glucose && <p className="text-red-400 text-xs mt-1">{errors.glucose}</p>}
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Action Buttons */}
                        <div className="flex gap-3 pt-4 border-t border-gray-800">
                            <Button type="submit" variant="primary" icon={UserPlus} className="flex-1">
                                Add Patient
                            </Button>
                            <Button type="button" variant="secondary" onClick={onClose}>
                                Cancel
                            </Button>
                        </div>
                    </form>
                </Card>
            </div>
        </div>
    );
};

export default AddPatientForm;
