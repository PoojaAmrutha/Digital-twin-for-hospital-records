import React, { useState, useEffect } from 'react';
import { LogOut, LayoutDashboard, User, Folder, UserPlus, Shield, TrendingUp } from 'lucide-react';
import LoginView from './components/LoginView';
import PatientDashboard from './components/PatientDashboard';
import MedicalRecords from './components/MedicalRecords';
import DoctorDashboard from './components/DoctorDashboard';
import ProfileView from './components/ProfileView';
import AddPatientForm from './components/AddPatientForm';
import BlockchainView from './components/BlockchainView';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import Button from './components/ui/Button';

const API_URL = 'http://localhost:8000';

const App = () => {
  // --- State Management ---
  const [user, setUser] = useState(null);
  const [allUsers, setAllUsers] = useState([]);
  const [view, setView] = useState('login'); // login, dashboard, documents, blockchain, analytics
  const [showProfile, setShowProfile] = useState(false);
  const [showAddPatient, setShowAddPatient] = useState(false);

  // Real-time Data State
  const [vitals, setVitals] = useState({
    heartRate: 0, spo2: 0, temperature: 0, stress: 0,
    steps: 0, calories: 0, sleepHours: 0
  });
  const [healthScore, setHealthScore] = useState(0);
  const [alerts, setAlerts] = useState([]);
  const [historicalData, setHistoricalData] = useState([]);

  // --- Effects ---

  // 1. Initial Load & Session Restore
  useEffect(() => {
    // Restore session from localStorage
    const storedUser = localStorage.getItem('currentUser');
    if (storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setUser(parsedUser);
        if (parsedUser.user_type === 'researcher') {
          setView('blockchain');
        } else {
          setView('dashboard');
        }
      } catch (e) {
        console.error("Failed to parse stored user", e);
        localStorage.removeItem('currentUser');
      }
    }

    fetchAllUsers();
  }, []);

  // 2. Real-time Polling
  useEffect(() => {
    if (user && user.user_type === 'patient') {
      const fetchData = async () => {
        await Promise.all([
          fetchVitals(),
          fetchHealthScore(),
          fetchAlerts(),
          fetchHistory()
        ]);
      };

      fetchData();
      const interval = setInterval(fetchData, 3000); // Poll every 3s for "live" feel
      return () => clearInterval(interval);
    }
  }, [user]);

  // --- Demo Data Helper ---
  const getDemoData = (userId) => {
    // Sarah (ID 99) - Healthy
    if (userId === 99) {
      return {
        vitals: { heartRate: 72, spo2: 98, temperature: 36.6, stress: 2, steps: 8500, calories: 2100, sleepHours: 7.5 },
        score: 92,
        alerts: []
      };
    }
    // John (ID 1) - Critical
    if (userId === 1) {
      return {
        vitals: { heartRate: 110, spo2: 92, temperature: 38.2, stress: 4.5, steps: 1200, calories: 400, sleepHours: 4.5 },
        score: 45,
        alerts: [{ id: 1, title: 'High Heart Rate', message: 'Heart rate detected above 100 bpm while resting', created_at: new Date().toISOString() }]
      };
    }
    // Default
    return {
      vitals: { heartRate: 60 + Math.random() * 20, spo2: 95 + Math.random() * 4, temperature: 36.5, stress: 3, steps: 4000, calories: 1500, sleepHours: 6 },
      score: 75,
      alerts: []
    };
  };

  // --- API Actions ---

  const fetchAllUsers = async () => {
    try {
      const res = await fetch(`${API_URL}/users/`);
      if (res.ok) setAllUsers(await res.json());
    } catch {
      // Fallback for demo/offline
      setAllUsers([
        { id: 1, name: 'Karthik Subramaniam', email: 'karthik@example.com', age: 45, gender: 'M', user_type: 'patient' },
        { id: 2, name: 'Priya Rajan', email: 'priya@example.com', age: 32, gender: 'F', user_type: 'patient' },
        { id: 99, name: 'Ananya Swami', email: 'ananya.demo@example.com', age: 34, gender: 'F', user_type: 'patient' },
        { id: 3, name: 'Dr. Lakshmi Priya', email: 'lakshmi@hospital.com', age: 35, gender: 'F', user_type: 'doctor' },
        { id: 0, name: 'Dr. Venkat Rao', email: 'venkat@research.com', age: 40, gender: 'M', user_type: 'researcher' }
      ]);
    }
  };

  const fetchVitals = async () => {
    try {
      const res = await fetch(`${API_URL}/vitals/user/${user.id}/latest`);
      if (res.ok) {
        const { data } = await res.json();
        setVitals({
          heartRate: data.heart_rate,
          spo2: data.spo2,
          temperature: data.temperature,
          stress: data.stress_level,
          steps: data.steps,
          calories: data.calories,
          sleepHours: data.sleep_hours
        });
      } else throw new Error('API Error');
    } catch (e) {
      // Use unique demo data
      const demo = getDemoData(user.id);
      setVitals(demo.vitals);
    }
  };

  const fetchHealthScore = async () => {
    try {
      const res = await fetch(`${API_URL}/health-score/user/${user.id}`);
      if (res.ok) {
        const data = await res.json();
        setHealthScore(Math.round(data.score));
      } else throw new Error('API Error');
    } catch (e) {
      setHealthScore(getDemoData(user.id).score);
    }
  };

  const fetchAlerts = async () => {
    try {
      const res = await fetch(`${API_URL}/alerts/user/${user.id}?limit=10`);
      if (res.ok) {
        const data = await res.json();
        setAlerts(data.map(a => ({
          ...a,
          time: new Date(a.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        })));
      } else throw new Error('API Error');
    } catch (e) {
      const demoAlerts = getDemoData(user.id).alerts;
      setAlerts(demoAlerts.map(a => ({
        ...a,
        time: new Date(a.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      })));
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_URL}/vitals/user/${user.id}/history?limit=20`);
      if (res.ok) {
        const data = await res.json();
        setHistoricalData(data.map(d => ({
          time: new Date(d.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          hr: Math.round(d.heart_rate),
          spo2: Math.round(d.spo2),
          stress: d.stress_level
        })).reverse());
      } else throw new Error('API Error');
    } catch (e) {
      // Generate random history if API fails
      const demoHistory = Array.from({ length: 20 }, (_, i) => ({
        time: `${10 + Math.floor(i / 4)}:${(i % 4) * 15}`,
        hr: (user.id === 1 ? 100 : 70) + Math.random() * 10 - 5,
        spo2: 98,
        stress: 2
      }));
      setHistoricalData(demoHistory);
    }
  };

  // --- Event Handlers ---

  const handleLogin = (userData) => {
    // 1. Save to state
    setUser(userData);

    // 2. Persist to localStorage
    localStorage.setItem('currentUser', JSON.stringify(userData));

    // 3. Set view
    if (userData.user_type === 'researcher') {
      setView('blockchain');
    } else {
      setView('dashboard');
    }
  };

  const handleLogout = () => {
    // 1. Clear state
    setUser(null);
    setView('login');
    setVitals({ heartRate: 0, spo2: 0, temperature: 0, stress: 0, steps: 0, calories: 0, sleepHours: 0 });
    setAlerts([]);
    setHistoricalData([]);

    // 2. Clear localStorage
    localStorage.removeItem('currentUser');
  };

  // --- Render ---

  if (view === 'login') {
    return <LoginView allUsers={allUsers} onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen bg-app pb-20">
      {/* Navigation Bar */}
      <nav className="sticky top-0 z-50 glass-card mx-4 mt-4 border-none px-6 py-4 mb-8">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-2">
              <div className="bg-indigo-600 rounded-lg p-1.5 text-white">
                <LayoutDashboard size={20} />
              </div>
              <h1 className="text-xl font-bold text-white">
                HealthWatch AI
              </h1>
            </div>

            <div className="hidden md:flex items-center gap-1 bg-gray-800/50 p-1 rounded-lg border border-gray-700">
              {user.user_type === 'patient' && (
                <>
                  <button
                    onClick={() => setView('dashboard')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${view === 'dashboard' ? 'bg-indigo-600 text-white shadow-lg' : 'text-gray-400 hover:text-white'}`}
                  >
                    Dashboard
                  </button>
                  <button
                    onClick={() => setView('documents')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${view === 'documents' ? 'bg-indigo-600 text-white shadow-lg' : 'text-gray-400 hover:text-white'}`}
                  >
                    Medical Records
                  </button>
                </>

              )}

              {user.user_type === 'researcher' && (
                <>
                  <button
                    onClick={() => setView('blockchain')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-all flex items-center gap-1 ${view === 'blockchain' ? 'bg-indigo-600 text-white shadow-lg' : 'text-gray-400 hover:text-white'}`}
                  >
                    <Shield size={16} />
                    Blockchain Data
                  </button>
                  <button
                    onClick={() => setView('analytics')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-all flex items-center gap-1 ${view === 'analytics' ? 'bg-indigo-600 text-white shadow-lg' : 'text-gray-400 hover:text-white'}`}
                  >
                    <TrendingUp size={16} />
                    Analytics
                  </button>
                </>
              )}
            </div>
          </div>

          <div className="flex items-center gap-4">
            {user.user_type === 'doctor' && (
              <Button
                variant="primary"
                icon={UserPlus}
                onClick={() => setShowAddPatient(true)}
                className="!px-4"
              >
                Add Patient
              </Button>
            )}

            <button
              onClick={() => setShowProfile(true)}
              className="hidden md:flex items-center gap-3 px-4 py-2 bg-gray-800/50 rounded-full border border-gray-700 hover:border-indigo-500 transition-all cursor-pointer"
            >
              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-violet-500 flex items-center justify-center text-white text-sm font-medium">
                {user.name.charAt(0)}
              </div>
              <div>
                <p className="text-sm font-medium text-white">{user.name}</p>
                <p className="text-xs text-gray-400 capitalize">{user.user_type}</p>
              </div>
            </button>

            <Button
              variant="secondary"
              icon={LogOut}
              onClick={handleLogout}
              className="!px-3"
            />
          </div>
        </div>
      </nav >

      {/* Main Content */}
      < main className="dashboard-container mt-8" >
        {view === 'blockchain' && <BlockchainView />}
        {view === 'analytics' && <AnalyticsDashboard />}

        {
          user.user_type === 'patient' ? (
            <>
              {view === 'dashboard' && <PatientDashboard
                user={user}
                vitals={vitals}
                healthScore={healthScore}
                alerts={alerts}
                historicalData={historicalData}
                onVitalsUpdate={() => {
                  // Refresh vitals after chatbot updates
                  fetchVitals();
                  fetchHealthScore();
                }}
              />}
              {view === 'documents' && <MedicalRecords />}
            </>
          ) : (
            <DoctorDashboard allUsers={allUsers} onSelectPatient={() => { }} />
          )
        }
      </main >

      {/* Profile Modal */}
      {
        showProfile && (
          <ProfileView
            user={user}
            onUpdateProfile={async (updatedData) => {
              try {
                const response = await fetch(`${API_URL}/users/${user.id}`, {
                  method: 'PUT',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                    name: updatedData.name,
                    age: updatedData.age,
                    gender: updatedData.gender
                  })
                });

                if (!response.ok) {
                  throw new Error('Failed to update profile');
                }

                const updated = await response.json();
                setUser({ ...user, ...updated });
                setShowProfile(false);
                alert('Profile updated successfully!');
              } catch (error) {
                console.error('Error updating profile:', error);
                alert('Failed to update profile. Please try again.');
              }
            }}
            onClose={() => setShowProfile(false)}
          />
        )
      }

      {/* Add Patient Modal */}
      {
        showAddPatient && (
          <AddPatientForm
            onAddPatient={async (newPatient) => {
              try {
                // 1. Create user in database
                const userResponse = await fetch(`${API_URL}/users/`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                    name: newPatient.name,
                    email: newPatient.email,
                    age: newPatient.age,
                    gender: newPatient.gender,
                    user_type: 'patient'
                  })
                });

                if (!userResponse.ok) {
                  const error = await userResponse.json();
                  throw new Error(error.detail || 'Failed to create patient');
                }

                const createdUser = await userResponse.json();

                // 2. Save initial vitals for the new patient
                const vitalsResponse = await fetch(`${API_URL}/vitals/`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                    user_id: createdUser.id,
                    heart_rate: newPatient.vitals.heartRate,
                    spo2: newPatient.vitals.spo2,
                    temperature: newPatient.vitals.temperature,
                    stress_level: newPatient.vitals.stress,
                    steps: 0,
                    calories: 0,
                    sleep_hours: 7.5
                  })
                });

                if (!vitalsResponse.ok) {
                  console.error('Failed to save vitals, but user created');
                }

                // 3. Refresh user list to show new patient
                await fetchAllUsers();

                setShowAddPatient(false);
                alert(`Patient ${createdUser.name} added successfully!`);
              } catch (error) {
                console.error('Error adding patient:', error);
                alert(`Error: ${error.message}`);
              }
            }}
            onClose={() => setShowAddPatient(false)}
          />
        )
      }
    </div >
  );
};

export default App;