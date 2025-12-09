import React, { useState, useEffect } from 'react';
import { Activity, Heart, Droplet, TrendingUp, AlertCircle, User, Building2, Bell, Download, Edit, Save, X, Plus, LogOut } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';

const API_URL = 'http://localhost:8000';

const App = () => {
  // Authentication & User State
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userType, setUserType] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [allUsers, setAllUsers] = useState([]);
  
  // View State
  const [view, setView] = useState('login');
  const [editingProfile, setEditingProfile] = useState(false);
  
  // Data State
  const [vitals, setVitals] = useState({
    heartRate: 72,
    spo2: 98,
    temperature: 36.8,
    stress: 2.1,
    steps: 0,
    calories: 0,
    sleepHours: 7.2
  });
  const [healthScore, setHealthScore] = useState(85);
  const [alerts, setAlerts] = useState([]);
  const [historicalData, setHistoricalData] = useState([]);
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);

  // Profile Form State
  const [profileForm, setProfileForm] = useState({
    name: '',
    age: '',
    gender: 'M',
    email: ''
  });

  // New Patient Form State
  const [newPatientForm, setNewPatientForm] = useState({
    name: '',
    email: '',
    age: '',
    gender: 'M',
    medicalHistory: '',
    allergies: '',
    bloodType: 'O+',
    emergencyContact: ''
  });

  // Fetch all users on mount
  useEffect(() => {
    fetchAllUsers();
  }, []);

  // Fetch real-time data when logged in
  useEffect(() => {
    if (isLoggedIn && currentUser && userType === 'patient') {
      fetchPatientData();
      const interval = setInterval(fetchPatientData, 5000);
      return () => clearInterval(interval);
    }
    
    if (isLoggedIn && userType === 'doctor') {
      fetchAllPatients();
      const interval = setInterval(fetchAllPatients, 5000);
      return () => clearInterval(interval);
    }
  }, [isLoggedIn, currentUser, userType]);

  // API Calls
  const fetchAllUsers = async () => {
    try {
      const response = await fetch(`${API_URL}/users/`);
      if (response.ok) {
        const data = await response.json();
        setAllUsers(data);
      }
    } catch (error) {
      console.log('Failed to fetch users - using demo mode');
      // Demo users if backend is not available
      setAllUsers([
        { id: 1, name: 'John Doe', email: 'john@example.com', age: 45, gender: 'M', user_type: 'patient' },
        { id: 2, name: 'Jane Smith', email: 'jane@example.com', age: 32, gender: 'F', user_type: 'patient' },
        { id: 3, name: 'Dr. Sarah Johnson', email: 'dr.sarah@hospital.com', age: 38, gender: 'F', user_type: 'doctor' }
      ]);
    }
  };

  const fetchPatientData = async () => {
    if (!currentUser) return;
    
    try {
      const vitalsRes = await fetch(`${API_URL}/vitals/user/${currentUser.id}/latest`);
      if (vitalsRes.ok) {
        const vitalsData = await vitalsRes.json();
        if (vitalsData.data) {
          setVitals({
            heartRate: vitalsData.data.heart_rate || 72,
            spo2: vitalsData.data.spo2 || 98,
            temperature: vitalsData.data.temperature || 36.8,
            stress: vitalsData.data.stress_level || 2.1,
            steps: vitalsData.data.steps || 0,
            calories: vitalsData.data.calories || 0,
            sleepHours: vitalsData.data.sleep_hours || 7.2
          });
        }
      }

      const scoreRes = await fetch(`${API_URL}/health-score/user/${currentUser.id}`);
      if (scoreRes.ok) {
        const scoreData = await scoreRes.json();
        setHealthScore(Math.round(scoreData.score) || 85);
      }

      const alertsRes = await fetch(`${API_URL}/alerts/user/${currentUser.id}?limit=10`);
      if (alertsRes.ok) {
        const alertsData = await alertsRes.json();
        const formattedAlerts = alertsData.map(alert => ({
          id: alert.id,
          type: alert.alert_type,
          title: alert.title,
          message: alert.message,
          time: new Date(alert.created_at).toLocaleTimeString()
        }));
        setAlerts(formattedAlerts);
      }

      const historyRes = await fetch(`${API_URL}/vitals/user/${currentUser.id}/history?limit=20`);
      if (historyRes.ok) {
        const historyData = await historyRes.json();
        const formattedHistory = historyData.map(reading => ({
          time: new Date(reading.timestamp).toLocaleTimeString(),
          hr: Math.round(reading.heart_rate),
          spo2: Math.round(reading.spo2),
          temp: parseFloat(reading.temperature.toFixed(1)),
          stress: parseFloat(reading.stress_level.toFixed(1))
        }));
        setHistoricalData(formattedHistory);
      }
    } catch (error) {
      console.log('Using demo data');
      // Generate demo historical data
      const demoHistory = Array.from({ length: 20 }, (_, i) => ({
        time: `${9 + Math.floor(i / 4)}:${(i % 4) * 15}`,
        hr: 72 + Math.random() * 10 - 5,
        spo2: 97 + Math.random() * 2,
        temp: 36.5 + Math.random() * 0.8,
        stress: 2 + Math.random() * 1.5
      }));
      setHistoricalData(demoHistory);
    }
  };

  const fetchAllPatients = async () => {
    try {
      const response = await fetch(`${API_URL}/hospital/patients`);
      if (response.ok) {
        const data = await response.json();
        setPatients(data);
      }
    } catch (error) {
      console.log('Using demo patients');
      setPatients(allUsers.filter(u => u.user_type === 'patient'));
    }
  };

  const handleLogin = (user) => {
    setCurrentUser(user);
    setUserType(user.user_type);
    setIsLoggedIn(true);
    setView('dashboard');
    setProfileForm({
      name: user.name,
      age: user.age,
      gender: user.gender,
      email: user.email
    });
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setCurrentUser(null);
    setUserType(null);
    setView('login');
    setSelectedPatient(null);
    setVitals({
      heartRate: 72,
      spo2: 98,
      temperature: 36.8,
      stress: 2.1,
      steps: 0,
      calories: 0,
      sleepHours: 7.2
    });
    setAlerts([]);
    setHistoricalData([]);
  };

  const handleSaveProfile = async () => {
    setCurrentUser({
      ...currentUser,
      name: profileForm.name,
      age: parseInt(profileForm.age),
      gender: profileForm.gender,
      email: profileForm.email
    });
    setEditingProfile(false);
    alert('Profile updated successfully!');
  };

  const handleAddPatient = async () => {
    try {
      const response = await fetch(`${API_URL}/users/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newPatientForm.name,
          email: newPatientForm.email,
          age: parseInt(newPatientForm.age),
          gender: newPatientForm.gender,
          user_type: 'patient'
        })
      });

      if (response.ok) {
        alert('Patient added successfully!');
        setNewPatientForm({
          name: '',
          email: '',
          age: '',
          gender: 'M',
          medicalHistory: '',
          allergies: '',
          bloodType: 'O+',
          emergencyContact: ''
        });
        setView('dashboard');
        fetchAllUsers();
        fetchAllPatients();
      }
    } catch (error) {
      alert('Failed to add patient - demo mode active');
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getRiskColor = (risk) => {
    if (risk === 'low') return 'bg-green-100 text-green-800';
    if (risk === 'medium') return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const getStatusColor = (status) => {
    if (status === 'stable') return 'text-green-600';
    if (status === 'warning') return 'text-yellow-600';
    return 'text-red-600';
  };

  // LOGIN SCREEN
  const LoginScreen = () => {
    const patients = allUsers.filter(u => u.user_type === 'patient');
    const doctors = allUsers.filter(u => u.user_type === 'doctor');

    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full p-8">
          <div className="text-center mb-8">
            <Activity className="text-blue-600 mx-auto mb-4" size={64} />
            <h1 className="text-4xl font-bold text-gray-800">HealthWatch AI</h1>
            <p className="text-gray-600 mt-2">AI-Powered Health Monitoring System</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="border-2 border-blue-200 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <User className="text-blue-600" size={32} />
                <h2 className="text-2xl font-bold text-gray-800">Patient Login</h2>
              </div>
              <p className="text-gray-600 mb-4">Select your profile to view your health dashboard</p>
              
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {patients.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">No patients registered</p>
                ) : (
                  patients.map(patient => (
                    <button
                      key={patient.id}
                      onClick={() => handleLogin(patient)}
                      className="w-full text-left p-4 bg-blue-50 hover:bg-blue-100 rounded-lg transition"
                    >
                      <p className="font-semibold text-gray-800">{patient.name}</p>
                      <p className="text-sm text-gray-600">Age: {patient.age} | {patient.gender === 'M' ? 'Male' : 'Female'}</p>
                    </button>
                  ))
                )}
              </div>
            </div>

            <div className="border-2 border-green-200 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <Building2 className="text-green-600" size={32} />
                <h2 className="text-2xl font-bold text-gray-800">Hospital Login</h2>
              </div>
              <p className="text-gray-600 mb-4">Medical staff access to monitor all patients</p>
              
              <div className="space-y-2">
                {doctors.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">No doctors registered</p>
                ) : (
                  doctors.map(doctor => (
                    <button
                      key={doctor.id}
                      onClick={() => handleLogin(doctor)}
                      className="w-full text-left p-4 bg-green-50 hover:bg-green-100 rounded-lg transition"
                    >
                      <p className="font-semibold text-gray-800">{doctor.name}</p>
                      <p className="text-sm text-gray-600">{doctor.email}</p>
                    </button>
                  ))
                )}
              </div>
            </div>
          </div>

          <div className="mt-8 text-center text-sm text-gray-500">
            <p>Demo System - Real-time health monitoring with AI predictions</p>
          </div>
        </div>
      </div>
    );
  };

  // PROFILE VIEW
  const ProfileView = () => (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-3xl font-bold text-gray-800">My Profile</h2>
          <button onClick={() => setView('dashboard')} className="text-gray-600 hover:text-gray-800">
            <X size={24} />
          </button>
        </div>

        <div className="space-y-6">
          <div className="flex items-center gap-6 pb-6 border-b">
            <div className="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center">
              <User className="text-blue-600" size={48} />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-gray-800">{currentUser.name}</h3>
              <p className="text-gray-600">{currentUser.user_type === 'patient' ? 'Patient' : 'Doctor'}</p>
              <p className="text-sm text-gray-500">User ID: {currentUser.id}</p>
            </div>
          </div>

          {editingProfile ? (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                <input
                  type="text"
                  value={profileForm.name}
                  onChange={(e) => setProfileForm({...profileForm, name: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Age</label>
                  <input
                    type="number"
                    value={profileForm.age}
                    onChange={(e) => setProfileForm({...profileForm, age: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Gender</label>
                  <select
                    value={profileForm.gender}
                    onChange={(e) => setProfileForm({...profileForm, gender: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="M">Male</option>
                    <option value="F">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                <input
                  type="email"
                  value={profileForm.email}
                  onChange={(e) => setProfileForm({...profileForm, email: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex gap-4 pt-4">
                <button
                  onClick={handleSaveProfile}
                  className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  <Save size={20} />
                  Save Changes
                </button>
                <button
                  onClick={() => setEditingProfile(false)}
                  className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Full Name</p>
                  <p className="text-lg font-semibold text-gray-800">{currentUser.name}</p>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Age</p>
                  <p className="text-lg font-semibold text-gray-800">{currentUser.age} years</p>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Gender</p>
                  <p className="text-lg font-semibold text-gray-800">
                    {currentUser.gender === 'M' ? 'Male' : currentUser.gender === 'F' ? 'Female' : 'Other'}
                  </p>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Email</p>
                  <p className="text-lg font-semibold text-gray-800">{currentUser.email}</p>
                </div>
              </div>

              <button
                onClick={() => setEditingProfile(true)}
                className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <Edit size={20} />
                Edit Profile
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  // ADD PATIENT VIEW
  const AddPatientView = () => (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-3xl font-bold text-gray-800">Add New Patient</h2>
          <button onClick={() => setView('dashboard')} className="text-gray-600 hover:text-gray-800">
            <X size={24} />
          </button>
        </div>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Full Name *</label>
              <input
                type="text"
                value={newPatientForm.name}
                onChange={(e) => setNewPatientForm({...newPatientForm, name: e.target.value})}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="John Doe"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email *</label>
              <input
                type="email"
                value={newPatientForm.email}
                onChange={(e) => setNewPatientForm({...newPatientForm, email: e.target.value})}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="john@example.com"
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Age *</label>
              <input
                type="number"
                value={newPatientForm.age}
                onChange={(e) => setNewPatientForm({...newPatientForm, age: e.target.value})}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="30"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Gender *</label>
              <select
                value={newPatientForm.gender}
                onChange={(e) => setNewPatientForm({...newPatientForm, gender: e.target.value})}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="M">Male</option>
                <option value="F">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Blood Type</label>
              <select
                value={newPatientForm.bloodType}
                onChange={(e) => setNewPatientForm({...newPatientForm, bloodType: e.target.value})}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
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
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Medical History</label>
            <textarea
              value={newPatientForm.medicalHistory}
              onChange={(e) => setNewPatientForm({...newPatientForm, medicalHistory: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              rows="3"
              placeholder="Any previous medical conditions, surgeries, etc."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Allergies</label>
            <input
              type="text"
              value={newPatientForm.allergies}
              onChange={(e) => setNewPatientForm({...newPatientForm, allergies: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Penicillin, Peanuts, etc."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Emergency Contact</label>
            <input
              type="text"
              value={newPatientForm.emergencyContact}
              onChange={(e) => setNewPatientForm({...newPatientForm, emergencyContact: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Name and Phone Number"
            />
          </div>

          <div className="flex gap-4 pt-4">
            <button
              onClick={handleAddPatient}
              className="flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              <Plus size={20} />
              Add Patient
            </button>
            <button
              onClick={() => setView('dashboard')}
              className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  // PATIENT DASHBOARD
  const PatientDashboard = () => (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-500 p-4 rounded">
        <p className="text-sm text-blue-900">
          🔄 Real-time health monitoring | Data updates every 5 seconds | Run backend simulator to see live data
        </p>
      </div>

      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Health Dashboard</h1>
          <p className="text-gray-600">Welcome back, {currentUser.name}</p>
        </div>
        <div className={`text-4xl font-bold ${getScoreColor(healthScore)}`}>
          {healthScore}/100
          <p className="text-sm text-gray-600">Health Score</p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-red-50 to-red-100 p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <Heart className="text-red-600" size={32} />
            <span className="text-2xl font-bold text-red-700">{Math.round(vitals.heartRate)}</span>
          </div>
          <p className="text-sm text-gray-600 mt-2">Heart Rate (bpm)</p>
        </div>

        <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <Droplet className="text-blue-600" size={32} />
            <span className="text-2xl font-bold text-blue-700">{Math.round(vitals.spo2)}%</span>
          </div>
          <p className="text-sm text-gray-600 mt-2">Blood Oxygen</p>
        </div>

        <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <Activity className="text-orange-600" size={32} />
            <span className="text-2xl font-bold text-orange-700">{vitals.temperature.toFixed(1)}°C</span>
          </div>
          <p className="text-sm text-gray-600 mt-2">Temperature</p>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <TrendingUp className="text-purple-600" size={32} />
            <span className="text-2xl font-bold text-purple-700">{vitals.stress.toFixed(1)}/5</span>
          </div>
          <p className="text-sm text-gray-600 mt-2">Stress Level</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-green-500">
          <p className="text-gray-600 text-sm">Steps Today</p>
          <p className="text-3xl font-bold text-gray-800">{vitals.steps.toLocaleString()}</p>
          <p className="text-xs text-green-600 mt-1">Target: 10,000</p>
        </div>

        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-orange-500">
          <p className="text-gray-600 text-sm">Calories Burned</p>
          <p className="text-3xl font-bold text-gray-800">{vitals.calories}</p>
          <p className="text-xs text-orange-600 mt-1">Target: 2,200</p>
        </div>

        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-indigo-500">
          <p className="text-gray-600 text-sm">Sleep Last Night</p>
          <p className="text-3xl font-bold text-gray-800">{vitals.sleepHours}h</p>
          <p className="text-xs text-indigo-600 mt-1">Target: 7-9h</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Health Trends</h3>
          {historicalData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={historicalData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" tick={{fontSize: 12}} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="hr" stroke="#ef4444" name="Heart Rate" />
                <Line type="monotone" dataKey="spo2" stroke="#3b82f6" name="SpO2" />
                <Line type="monotone" dataKey="stress" stroke="#8b5cf6" name="Stress" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-300 flex items-center justify-center text-gray-500">
              No historical data available yet
            </div>
          )}
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <Bell className="text-orange-600" />
            Recent Alerts
          </h3>
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {alerts.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No alerts</p>
            ) : (
              alerts.map(alert => (
                <div key={alert.id} className="border-l-4 border-orange-400 bg-orange-50 p-3 rounded">
                  <div className="flex items-start gap-2">
                    <AlertCircle className="text-orange-600 mt-1" size={16} />
                    <div className="flex-1">
                      <p className="font-semibold text-sm text-gray-800">{alert.title}</p>
                      <p className="text-xs text-gray-600 mt-1">{alert.message}</p>
                      <p className="text-xs text-gray-500 mt-1">{alert.time}</p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Health Recommendations</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="border-l-4 border-blue-500 bg-blue-50 p-4 rounded">
            <p className="font-semibold text-gray-800">💧 Hydration</p>
            <p className="text-sm text-gray-600 mt-1">Drink 8 glasses of water daily</p>
          </div>
          <div className="border-l-4 border-green-500 bg-green-50 p-4 rounded">
            <p className="font-semibold text-gray-800">🏃 Activity</p>
            <p className="text-sm text-gray-600 mt-1">30 minutes of moderate exercise</p>
          </div>
          <div className="border-l-4 border-purple-500 bg-purple-50 p-4 rounded">
            <p className="font-semibold text-gray-800">😴 Sleep</p>
            <p className="text-sm text-gray-600 mt-1">Maintain 7-9 hours sleep schedule</p>
          </div>
          <div className="border-l-4 border-yellow-500 bg-yellow-50 p-4 rounded">
            <p className="font-semibold text-gray-800">🧘 Stress</p>
            <p className="text-sm text-gray-600 mt-1">Practice mindfulness or meditation</p>
          </div>
        </div>
      </div>
    </div>
  );

  // HOSPITAL DASHBOARD
  const HospitalDashboard = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Hospital Dashboard</h1>
          <p className="text-gray-600">Welcome, {currentUser.name}</p>
        </div>
        <button
          onClick={() => setView('addPatient')}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          <Plus size={20} />
          Add Patient
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow">
          <p className="text-gray-600 text-sm">Total Patients</p>
          <p className="text-3xl font-bold text-blue-600">{patients.length}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <p className="text-gray-600 text-sm">Critical Cases</p>
          <p className="text-3xl font-bold text-red-600">
            {patients.filter(p => p.risk_level === 'high').length}
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <p className="text-gray-600 text-sm">Stable Patients</p>
          <p className="text-3xl font-bold text-green-600">
            {patients.filter(p => p.status === 'stable').length}
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <p className="text-gray-600 text-sm">Avg Health Score</p>
          <p className="text-3xl font-bold text-purple-600">
            {patients.length > 0 ? Math.round(patients.reduce((sum, p) => sum + (p.health_score || 85), 0) / patients.length) : 0}
          </p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-800">Patient List</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Patient</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Age</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Health Score</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Risk Level</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Updated</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {patients.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                    No patients found
                  </td>
                </tr>
              ) : (
                patients.map(patient => (
                  <tr key={patient.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => setSelectedPatient(patient)}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                          <User className="text-blue-600" size={20} />
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{patient.name}</div>
                          <div className="text-sm text-gray-500">{patient.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{patient.age}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-lg font-bold ${getScoreColor(patient.health_score || 85)}`}>
                        {patient.health_score || 85}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-sm font-semibold ${getStatusColor(patient.status || 'stable')}`}>
                        {(patient.status || 'stable').toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getRiskColor(patient.risk_level || 'low')}`}>
                        {(patient.risk_level || 'low').toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {patient.last_reading_time ? new Date(patient.last_reading_time).toLocaleString() : 'N/A'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {selectedPatient && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-2xl max-w-2xl w-full max-h-screen overflow-y-auto p-6">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-2xl font-bold text-gray-800">Patient Details</h3>
              <button onClick={() => setSelectedPatient(null)} className="text-gray-600 hover:text-gray-800">
                <X size={24} />
              </button>
            </div>

            <div className="space-y-4">
              <div className="flex items-center gap-4 pb-4 border-b">
                <div className="h-16 w-16 bg-blue-100 rounded-full flex items-center justify-center">
                  <User className="text-blue-600" size={32} />
                </div>
                <div>
                  <h4 className="text-xl font-bold text-gray-800">{selectedPatient.name}</h4>
                  <p className="text-gray-600">{selectedPatient.email}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Age</p>
                  <p className="text-lg font-semibold text-gray-800">{selectedPatient.age} years</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Gender</p>
                  <p className="text-lg font-semibold text-gray-800">
                    {selectedPatient.gender === 'M' ? 'Male' : 'Female'}
                  </p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Health Score</p>
                  <p className={`text-2xl font-bold ${getScoreColor(selectedPatient.health_score || 85)}`}>
                    {selectedPatient.health_score || 85}/100
                  </p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Risk Level</p>
                  <span className={`px-3 py-1 inline-flex text-sm font-semibold rounded-full ${getRiskColor(selectedPatient.risk_level || 'low')}`}>
                    {(selectedPatient.risk_level || 'low').toUpperCase()}
                  </span>
                </div>
              </div>

              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600 mb-2">Current Vitals</p>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>Heart Rate: <span className="font-semibold">72 bpm</span></div>
                  <div>SpO2: <span className="font-semibold">98%</span></div>
                  <div>Temperature: <span className="font-semibold">36.8°C</span></div>
                  <div>Stress: <span className="font-semibold">2.1/5</span></div>
                </div>
              </div>

              <div className="flex gap-4">
                <button className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                  View Full Records
                </button>
                <button className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300">
                  Send Message
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  // MAIN LAYOUT
  if (!isLoggedIn) {
    return <LoginScreen />;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <Activity className="text-blue-600" size={32} />
              <div>
                <h1 className="text-xl font-bold text-gray-800">HealthWatch AI</h1>
                <p className="text-xs text-gray-500">{userType === 'patient' ? 'Patient Portal' : 'Hospital Portal'}</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <button
                onClick={() => setView('dashboard')}
                className={`px-4 py-2 rounded-lg ${view === 'dashboard' ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-100'}`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setView('profile')}
                className={`px-4 py-2 rounded-lg ${view === 'profile' ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-100'}`}
              >
                Profile
              </button>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg"
              >
                <LogOut size={20} />
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {view === 'dashboard' && (userType === 'patient' ? <PatientDashboard /> : <HospitalDashboard />)}
        {view === 'profile' && <ProfileView />}
        {view === 'addPatient' && <AddPatientView />}
      </main>
    </div>
  );
};

export default App;