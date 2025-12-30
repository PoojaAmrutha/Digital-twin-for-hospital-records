import React from 'react';
import { Activity, User, Building2, ChevronRight } from 'lucide-react';
import Card from './ui/Card';

const LoginView = ({ allUsers, onLogin }) => {
    const [loginRole, setLoginRole] = React.useState('patient'); // 'patient' or 'doctor'
    const [email, setEmail] = React.useState('');
    const [password, setPassword] = React.useState('');
    const [error, setError] = React.useState('');
    const [isLoading, setIsLoading] = React.useState(false);

    const API_URL = 'http://localhost:8000';

    const handleLoginSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Login failed');
            }

            const user = await response.json();
            
            // Verify role matches
            if (user.user_type !== loginRole) {
                 throw new Error(`This account belongs to a ${user.user_type}, but you are trying to login as a ${loginRole}.`);
            }

            onLogin(user);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-6 bg-app overflow-hidden relative">
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] bg-indigo-600/20 rounded-full blur-[120px] animate-pulse-soft"></div>
                <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] bg-purple-600/20 rounded-full blur-[120px] animate-pulse-soft" style={{ animationDelay: '1s' }}></div>
            </div>

            <div className="max-w-4xl w-full grid grid-cols-1 md:grid-cols-2 gap-16 items-center animate-fade-in relative z-10">

                {/* Left Side: Branding */}
                <div className="space-y-8 hidden md:block">
                    <div>
                        <div className="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-gradient-to-br from-indigo-600 to-violet-600 text-white shadow-lg shadow-indigo-500/30 mb-8 border border-white/10">
                            <Activity size={40} />
                        </div>
                        <h1 className="text-6xl font-bold text-white mb-6 tracking-tight">
                            HealthWatch <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">AI</span>
                        </h1>
                        <p className="text-xl text-gray-400 leading-relaxed font-light">
                            Experience the future of healthcare monitoring.
                            <span className="text-gray-300 block mt-2">Real-time analytics. AI Predictions. Digital Twins.</span>
                        </p>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="p-5 bg-gray-900/60 rounded-2xl backdrop-blur-md border border-gray-800 hover:border-indigo-500/50 transition-colors group">
                            <p className="text-4xl font-bold text-white group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-indigo-400 group-hover:to-cyan-400 transition-all">99.9%</p>
                            <p className="text-sm text-gray-500 mt-1 uppercase tracking-wider font-semibold">Reliability</p>
                        </div>
                        <div className="p-5 bg-gray-900/60 rounded-2xl backdrop-blur-md border border-gray-800 hover:border-pink-500/50 transition-colors group">
                            <p className="text-4xl font-bold text-white group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-pink-400 group-hover:to-rose-400 transition-all">24/7</p>
                            <p className="text-sm text-gray-500 mt-1 uppercase tracking-wider font-semibold">Monitoring</p>
                        </div>
                    </div>
                </div>

                {/* Right Side: Login Form */}
                <Card className="bg-gray-900/40 border-gray-700/50">
                    <div className="mb-6 flex gap-4 p-1 bg-gray-800/50 rounded-xl">
                         <button 
                            onClick={() => setLoginRole('patient')}
                            className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-all ${loginRole === 'patient' ? 'bg-indigo-600 text-white shadow-lg' : 'text-gray-400 hover:text-white'}`}
                         >
                            Patient Login
                         </button>
                         <button 
                            onClick={() => setLoginRole('doctor')}
                            className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-all ${loginRole === 'doctor' ? 'bg-emerald-600 text-white shadow-lg' : 'text-gray-400 hover:text-white'}`}
                         >
                            Doctor Login
                         </button>
                    </div>

                    <div className="mb-8">
                        <h2 className="text-2xl font-bold text-white mb-2">{loginRole === 'patient' ? 'Patient Portal' : 'Medical Staff Portal'}</h2>
                        <p className="text-gray-400 text-sm">Sign in to access your dashboard</p>
                    </div>

                    <form onSubmit={handleLoginSubmit} className="space-y-4">
                        <div>
                            <label className="text-sm text-gray-400 mb-1 block">Email Address</label>
                            <div className="relative">
                                <User className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
                                <input 
                                    type="email" 
                                    required
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="w-full bg-gray-950 border border-gray-800 rounded-xl py-3 pl-10 pr-4 text-white focus:outline-none focus:border-indigo-500 transition-colors"
                                    placeholder="name@example.com"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="text-sm text-gray-400 mb-1 block">Password</label>
                            <div className="relative">
                                <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
                                <input 
                                    type="password" 
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full bg-gray-950 border border-gray-800 rounded-xl py-3 pl-10 pr-4 text-white focus:outline-none focus:border-indigo-500 transition-colors"
                                    placeholder="••••••••"
                                />
                            </div>
                        </div>

                        {error && (
                            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
                                {error}
                            </div>
                        )}

                        <button 
                            type="submit" 
                            disabled={isLoading}
                            className={`w-full py-3 rounded-xl font-bold text-white shadow-lg transition-all ${
                                loginRole === 'patient' 
                                ? 'bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 shadow-indigo-500/25' 
                                : 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 shadow-emerald-500/25'
                            } ${isLoading ? 'opacity-70 cursor-not-allowed' : 'hover:-translate-y-0.5'}`}
                        >
                            {isLoading ? 'Signing In...' : 'Sign In'}
                        </button>

                        <div className="text-center mt-4">
                            <p className="text-xs text-gray-500">
                                Don't have an account? <span className="text-indigo-400 cursor-pointer hover:underline">Register (Coming Soon)</span>
                            </p>
                        </div>
                    </form>
                </Card>
            </div>
        </div>
    );
};

export default LoginView;

