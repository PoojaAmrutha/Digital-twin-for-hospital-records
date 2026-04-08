import React from 'react';
import { Lock, Mail, Heart, Stethoscope, Microscope, Shield } from 'lucide-react';

const LoginView = ({ allUsers, onLogin }) => {
    const [isRegistering, setIsRegistering] = React.useState(false);
    const [name, setName] = React.useState('');
    const [age, setAge] = React.useState('');
    const [gender, setGender] = React.useState('M');
    const [loginRole, setLoginRole] = React.useState('patient');

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
            let endpoint = `${API_URL}/auth/login`;
            let body = { email, password };

            if (isRegistering) {
                endpoint = `${API_URL}/users/`;
                body = {
                    name,
                    email,
                    password,
                    age: parseInt(age),
                    gender,
                    user_type: loginRole
                };
            }

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || (isRegistering ? 'Registration failed' : 'Login failed'));
            }

            const user = await response.json();

            // Note: If registering, the backend returns the created user object.
            // You might want to auto-login or ask them to login. 
            // For smooth UX, let's treat it as auto-login if the response structure is compatible.
            // (The create_user endpoint returns UserResponse, which is similar to Login response)

            if (!isRegistering && user.user_type !== loginRole) {
                throw new Error(`This account belongs to a ${user.user_type}, but you are trying to login as a ${loginRole}.`);
            }

            onLogin(user);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    const roleConfig = {
        patient: {
            icon: Heart,
            color: 'from-rose-500 via-pink-500 to-fuchsia-500',
            bgGlow: 'bg-rose-500/10',
            borderColor: 'border-rose-500/30',
            buttonBg: 'bg-gradient-to-r from-rose-600 to-pink-600 hover:from-rose-500 hover:to-pink-500',
            title: 'Patient Access',
            subtitle: 'Your health, your data'
        },
        doctor: {
            icon: Stethoscope,
            color: 'from-emerald-500 via-teal-500 to-cyan-500',
            bgGlow: 'bg-emerald-500/10',
            borderColor: 'border-emerald-500/30',
            buttonBg: 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500',
            title: 'Medical Professional',
            subtitle: 'Care with precision'
        },
        researcher: {
            icon: Microscope,
            color: 'from-amber-500 via-orange-500 to-red-500',
            bgGlow: 'bg-amber-500/10',
            borderColor: 'border-amber-500/30',
            buttonBg: 'bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500',
            title: 'Research Portal',
            subtitle: 'Advancing medical science'
        }
    };

    const currentRole = roleConfig[loginRole];
    const RoleIcon = currentRole.icon;

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex overflow-hidden relative">
            {/* Static Background - Professional & Clean */}
            <div className="absolute inset-0 bg-slate-900"></div>

            {/* Subtle Texture - Optional, but keeps it from looking flat */}
            <div className="absolute inset-0 opacity-5 bg-[radial-gradient(#cbd5e1_1px,transparent_1px)] [background-size:32px_32px] pointer-events-none"></div>

            {/* Left Side - Animated Visual */}
            <div className="hidden lg:flex lg:w-1/2 relative items-center justify-center p-12">
                <div className="relative z-10 max-w-lg">
                    {/* Clean Typography - No Animations */}
                    <h1 className="text-6xl font-bold text-white mb-6 tracking-tight">
                        Digital Twin <br />
                        <span className="text-indigo-400">Hospital Records</span>
                    </h1>
                </div>
            </div>

            {/* Right Side - Login Form */}
            <div className="w-full lg:w-1/2 flex items-center justify-center p-6 lg:p-12 relative z-10">
                <div className="w-full max-w-md bg-slate-900 rounded-2xl p-8 border border-slate-800 shadow-2xl">
                    <div className="mb-8">
                        <h2 className="text-2xl font-bold text-white">Sign In</h2>
                        <p className="text-slate-400 text-sm mt-1">Please select your role to continue</p>
                    </div>

                    {/* Role Selector */}
                    <div className="flex gap-2 mb-8 p-1.5 bg-slate-900/50 backdrop-blur-sm rounded-2xl border border-slate-800">
                        {Object.keys(roleConfig).map((role) => (
                            <button
                                key={role}
                                onClick={() => setLoginRole(role)}
                                className={`flex-1 py-2.5 px-4 rounded-xl text-sm font-semibold transition-all duration-300 ${loginRole === role
                                    ? `bg-gradient-to-r ${roleConfig[role].color} text-white shadow-lg`
                                    : 'text-slate-500 hover:text-slate-300'
                                    }`}
                            >
                                {role.charAt(0).toUpperCase() + role.slice(1)}
                            </button>
                        ))}
                    </div>

                    {/* Login Form */}
                    <form onSubmit={handleLoginSubmit} className="space-y-5">
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-2">Email Address</label>
                            <div className="relative">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 w-5 h-5" />
                                <input
                                    type="email"
                                    required
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="w-full bg-slate-900/50 backdrop-blur-sm border border-slate-700 rounded-xl py-3.5 pl-12 pr-4 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all"
                                    placeholder="your.email@example.com"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-2">Password</label>
                            <div className="relative">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 w-5 h-5" />
                                <input
                                    type="password"
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full bg-slate-900/50 backdrop-blur-sm border border-slate-700 rounded-xl py-3.5 pl-12 pr-4 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all"
                                    placeholder="Enter your password"
                                />
                            </div>
                        </div>

                        {error && (
                            <div className="p-4 bg-red-500/10 backdrop-blur-sm border border-red-500/30 rounded-xl text-red-400 text-sm flex items-start gap-3">
                                <span className="text-lg">⚠️</span>
                                <span>{error}</span>
                            </div>
                        )}

                        {/* Toggle Login/Register */}
                        <div className="flex justify-between items-center mb-6">
                            <button
                                type="button"
                                onClick={() => {
                                    setIsRegistering(!isRegistering);
                                    setError('');
                                }}
                                className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors"
                            >
                                {isRegistering ? 'Already have an account? Sign In' : "Don't have an account? Sign Up"}
                            </button>
                        </div>

                        {/* Registration Extra Fields */}
                        {isRegistering && (
                            <div className="space-y-4 animate-fadeIn">
                                <div>
                                    <label className="block text-sm font-medium text-slate-300 mb-2">Full Name</label>
                                    <input
                                        type="text"
                                        required
                                        value={name}
                                        onChange={(e) => setName(e.target.value)}
                                        className="w-full bg-slate-900/50 backdrop-blur-sm border border-slate-700 rounded-xl py-3 px-4 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all"
                                        placeholder="John Doe"
                                    />
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-slate-300 mb-2">Age</label>
                                        <input
                                            type="number"
                                            required
                                            value={age}
                                            onChange={(e) => setAge(e.target.value)}
                                            className="w-full bg-slate-900/50 backdrop-blur-sm border border-slate-700 rounded-xl py-3 px-4 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all"
                                            placeholder="30"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-slate-300 mb-2">Gender</label>
                                        <select
                                            value={gender}
                                            onChange={(e) => setGender(e.target.value)}
                                            className="w-full bg-slate-900/50 backdrop-blur-sm border border-slate-700 rounded-xl py-3 px-4 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all"
                                        >
                                            <option value="M">Male</option>
                                            <option value="F">Female</option>
                                            <option value="Other">Other</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={isLoading}
                            className={`w-full py-3 rounded-lg font-semibold text-white transition-all shadow-lg shadow-indigo-500/20 ${isLoading ? 'opacity-70 cursor-wait' : 'hover:scale-[1.02] active:scale-[0.98]'
                                } ${roleConfig[loginRole].buttonBg}`}
                        >
                            {isLoading ? 'Processing...' : (isRegistering ? 'Create Account' : 'Sign In')}
                        </button>


                    </form>
                </div>
            </div>
        </div>
    );
};

export default LoginView;

