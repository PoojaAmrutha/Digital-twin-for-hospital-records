import React, { useState } from 'react';
import { User, Mail, Phone, Calendar, MapPin, Edit2, Save, X, Heart, Activity, AlertCircle, FileText, Shield } from 'lucide-react';
import Card from './ui/Card';
import Button from './ui/Button';

const ProfileView = ({ user, onUpdateProfile, onClose }) => {
    const [isEditing, setIsEditing] = useState(false);
    const [formData, setFormData] = useState({
        name: user.name || '',
        email: user.email || '',
        age: user.age || '',
        gender: user.gender || 'M',
        phone: user.phone || '',
        address: user.address || '',
        emergencyContact: user.emergencyContact || '',
        bloodType: user.bloodType || 'O+',
        height: user.height || '',
        weight: user.weight || '',
        allergies: user.allergies || 'None known',
        chronicConditions: user.chronicConditions || 'None',
        medications: user.medications || 'None'
    });

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSave = () => {
        onUpdateProfile(formData);
        setIsEditing(false);
    };

    return (
        <div className="fixed inset-0 z-[100] bg-black/95 backdrop-blur-xl flex items-start justify-center p-4 animate-fade-in overflow-y-auto">
            <div className="w-full max-w-5xl my-8">
                <Card className="bg-gray-900/95 border-gray-700 relative">
                    <button onClick={onClose} className="sticky top-4 right-4 float-right p-2 bg-gray-800 hover:bg-red-500/80 text-white rounded-full transition-colors z-20 shadow-lg">
                        <X size={20} />
                    </button>

                    {/* Profile Header */}
                    <div className="border-b border-gray-800 pb-6 mb-6">
                        <div className="flex items-center gap-6">
                            <div className="w-24 h-24 rounded-full bg-gradient-to-tr from-indigo-600 to-violet-600 flex items-center justify-center text-white text-4xl font-bold border-4 border-indigo-400 shadow-lg shadow-indigo-500/30">
                                {user.name.charAt(0)}
                            </div>
                            <div className="flex-1">
                                <h2 className="text-3xl font-bold text-white">{user.name}</h2>
                                <p className="text-gray-400 mt-1">{user.user_type === 'patient' ? 'Patient' : 'Doctor'} • ID: #{user.id}</p>
                                <p className="text-gray-500 text-sm mt-1">{user.email}</p>
                            </div>
                            {!isEditing && (
                                <Button variant="primary" icon={Edit2} onClick={() => setIsEditing(true)}>
                                    Edit Profile
                                </Button>
                            )}
                            {isEditing && (
                                <div className="flex gap-2">
                                    <Button variant="primary" icon={Save} onClick={handleSave}>Save</Button>
                                    <Button variant="secondary" onClick={() => setIsEditing(false)}>Cancel</Button>
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Personal Information */}
                        <div className="space-y-6">
                            <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                <User size={20} className="text-indigo-400" />
                                Personal Information
                            </h3>

                            <div className="space-y-4">
                                <div>
                                    <label className="text-sm text-gray-400 mb-1 block">Full Name</label>
                                    {isEditing ? (
                                        <input
                                            type="text"
                                            name="name"
                                            value={formData.name}
                                            onChange={handleChange}
                                            className="input-field"
                                        />
                                    ) : (
                                        <p className="text-white font-medium">{formData.name}</p>
                                    )}
                                </div>

                                <div>
                                    <label className="text-sm text-gray-400 mb-1 block">Email</label>
                                    {isEditing ? (
                                        <input
                                            type="email"
                                            name="email"
                                            value={formData.email}
                                            onChange={handleChange}
                                            className="input-field"
                                        />
                                    ) : (
                                        <p className="text-white font-medium flex items-center gap-2">
                                            <Mail size={16} className="text-gray-500" />
                                            {formData.email}
                                        </p>
                                    )}
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="text-sm text-gray-400 mb-1 block">Age</label>
                                        {isEditing ? (
                                            <input
                                                type="number"
                                                name="age"
                                                value={formData.age}
                                                onChange={handleChange}
                                                className="input-field"
                                            />
                                        ) : (
                                            <p className="text-white font-medium">{formData.age} years</p>
                                        )}
                                    </div>

                                    <div>
                                        <label className="text-sm text-gray-400 mb-1 block">Gender</label>
                                        {isEditing ? (
                                            <select
                                                name="gender"
                                                value={formData.gender}
                                                onChange={handleChange}
                                                className="input-field"
                                            >
                                                <option value="M">Male</option>
                                                <option value="F">Female</option>
                                                <option value="O">Other</option>
                                            </select>
                                        ) : (
                                            <p className="text-white font-medium">{formData.gender === 'M' ? 'Male' : formData.gender === 'F' ? 'Female' : 'Other'}</p>
                                        )}
                                    </div>
                                </div>

                                <div>
                                    <label className="text-sm text-gray-400 mb-1 block">Phone</label>
                                    {isEditing ? (
                                        <input
                                            type="tel"
                                            name="phone"
                                            value={formData.phone}
                                            onChange={handleChange}
                                            className="input-field"
                                            placeholder="+1 (555) 123-4567"
                                        />
                                    ) : (
                                        <p className="text-white font-medium flex items-center gap-2">
                                            <Phone size={16} className="text-gray-500" />
                                            {formData.phone || 'Not provided'}
                                        </p>
                                    )}
                                </div>

                                <div>
                                    <label className="text-sm text-gray-400 mb-1 block">Address</label>
                                    {isEditing ? (
                                        <textarea
                                            name="address"
                                            value={formData.address}
                                            onChange={handleChange}
                                            className="input-field"
                                            rows="2"
                                            placeholder="Street, City, State, ZIP"
                                        />
                                    ) : (
                                        <p className="text-white font-medium flex items-start gap-2">
                                            <MapPin size={16} className="text-gray-500 mt-1" />
                                            {formData.address || 'Not provided'}
                                        </p>
                                    )}
                                </div>

                                <div>
                                    <label className="text-sm text-gray-400 mb-1 block">Emergency Contact</label>
                                    {isEditing ? (
                                        <input
                                            type="text"
                                            name="emergencyContact"
                                            value={formData.emergencyContact}
                                            onChange={handleChange}
                                            className="input-field"
                                            placeholder="Name & Phone"
                                        />
                                    ) : (
                                        <p className="text-white font-medium flex items-center gap-2">
                                            <AlertCircle size={16} className="text-red-400" />
                                            {formData.emergencyContact || 'Not provided'}
                                        </p>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Medical Information */}
                        <div className="space-y-6">
                            <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                <Heart size={20} className="text-rose-400" />
                                Medical Information
                            </h3>

                            <div className="space-y-4">
                                <div className="grid grid-cols-3 gap-4">
                                    <div>
                                        <label className="text-sm text-gray-400 mb-1 block">Blood Type</label>
                                        {isEditing ? (
                                            <select
                                                name="bloodType"
                                                value={formData.bloodType}
                                                onChange={handleChange}
                                                className="input-field"
                                            >
                                                <option value="A+">A+</option>
                                                <option value="A-">A-</option>
                                                <option value="B+">B+</option>
                                                <option value="B-">B-</option>
                                                <option value="AB+">AB+</option>
                                                <option value="AB-">AB-</option>
                                                <option value="O+">O+</option>
                                                <option value="O-">O-</option>
                                            </select>
                                        ) : (
                                            <p className="text-white font-bold text-lg">{formData.bloodType}</p>
                                        )}
                                    </div>

                                    <div>
                                        <label className="text-sm text-gray-400 mb-1 block">Height (cm)</label>
                                        {isEditing ? (
                                            <input
                                                type="number"
                                                name="height"
                                                value={formData.height}
                                                onChange={handleChange}
                                                className="input-field"
                                                placeholder="170"
                                            />
                                        ) : (
                                            <p className="text-white font-medium">{formData.height || 'N/A'} cm</p>
                                        )}
                                    </div>

                                    <div>
                                        <label className="text-sm text-gray-400 mb-1 block">Weight (kg)</label>
                                        {isEditing ? (
                                            <input
                                                type="number"
                                                name="weight"
                                                value={formData.weight}
                                                onChange={handleChange}
                                                className="input-field"
                                                placeholder="70"
                                            />
                                        ) : (
                                            <p className="text-white font-medium">{formData.weight || 'N/A'} kg</p>
                                        )}
                                    </div>
                                </div>

                                <div className="bg-red-500/10 border border-red-500/20 p-4 rounded-xl">
                                    <label className="text-sm text-red-400 mb-2 block font-bold flex items-center gap-2">
                                        <AlertCircle size={16} />
                                        Known Allergies
                                    </label>
                                    {isEditing ? (
                                        <textarea
                                            name="allergies"
                                            value={formData.allergies}
                                            onChange={handleChange}
                                            className="input-field"
                                            rows="2"
                                            placeholder="List any allergies..."
                                        />
                                    ) : (
                                        <p className="text-red-300 text-sm">{formData.allergies}</p>
                                    )}
                                </div>

                                <div className="bg-amber-500/10 border border-amber-500/20 p-4 rounded-xl">
                                    <label className="text-sm text-amber-400 mb-2 block font-bold flex items-center gap-2">
                                        <Activity size={16} />
                                        Chronic Conditions
                                    </label>
                                    {isEditing ? (
                                        <textarea
                                            name="chronicConditions"
                                            value={formData.chronicConditions}
                                            onChange={handleChange}
                                            className="input-field"
                                            rows="2"
                                            placeholder="List any chronic conditions..."
                                        />
                                    ) : (
                                        <p className="text-amber-300 text-sm">{formData.chronicConditions}</p>
                                    )}
                                </div>

                                <div className="bg-emerald-500/10 border border-emerald-500/20 p-4 rounded-xl">
                                    <label className="text-sm text-emerald-400 mb-2 block font-bold flex items-center gap-2">
                                        <FileText size={16} />
                                        Current Medications
                                    </label>
                                    {isEditing ? (
                                        <textarea
                                            name="medications"
                                            value={formData.medications}
                                            onChange={handleChange}
                                            className="input-field"
                                            rows="3"
                                            placeholder="List current medications with dosage..."
                                        />
                                    ) : (
                                        <p className="text-emerald-300 text-sm">{formData.medications}</p>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Privacy & Security */}
                    <div className="mt-8 pt-6 border-t border-gray-800">
                        <h3 className="text-xl font-bold text-white flex items-center gap-2 mb-4">
                            <Shield size={20} className="text-indigo-400" />
                            Privacy & Security
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
                                <p className="text-gray-300 text-sm">Your medical data is encrypted and HIPAA compliant</p>
                            </div>
                            <div className="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
                                <p className="text-gray-300 text-sm">Only authorized healthcare providers can access your records</p>
                            </div>
                        </div>
                    </div>
                </Card>
            </div>
        </div>
    );
};

export default ProfileView;
