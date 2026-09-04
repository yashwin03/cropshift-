import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import type { UserRole } from '../contexts/AuthContext';
import apiClient from '../services/apiClient';
import AgriTerrain3D from '../components/3d/AgriTerrain3D';

type AuthMode = 'login' | 'register';

export default function LoginPage() {
  const [authMode, setAuthMode] = useState<AuthMode>('login');
  const [selectedRole, setSelectedRole] = useState<UserRole>('farmer');

  // Sign In state
  const [username, setUsername] = useState('demo');
  const [password, setPassword] = useState('password123');

  // Sign Up state
  const [regUsername, setRegUsername] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');

  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const navigate = useNavigate();
  const { login } = useAuth();

  const handleRoleSelect = (role: UserRole) => {
    setSelectedRole(role);
    setError('');
    setSuccessMsg('');
    if (role === 'farmer') {
      setUsername('demo');
      setPassword('password123');
    } else {
      setUsername('buyer_demo');
      setPassword('password123');
    }
  };

  const handleFillDemo = () => {
    setError('');
    setSuccessMsg('');
    if (selectedRole === 'farmer') {
      setUsername('demo');
      setPassword('password123');
    } else {
      setUsername('buyer_demo');
      setPassword('password123');
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccessMsg('');

    try {
      const formData = new URLSearchParams();
      formData.append('username', username.trim());
      formData.append('password', password);

      const res = await apiClient.post('/api/v1/auth/token', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      const token = res.data.access_token;

      // Fetch authenticated user profile to get authoritative backend role & Farmer ID
      const userRes = await apiClient.get('/api/v1/auth/me', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const userProfile = userRes.data;
      login(token, userProfile);

      // Authoritative backend role determines post-login destination
      const authRole = (userProfile.role || 'FARMER').toString().toUpperCase();
      if (authRole === 'BUYER') {
        navigate('/buyer');
      } else {
        navigate('/');
      }
    } catch (err: any) {
      if (err?.code === 'NETWORK_ERROR' || err?.code === 'ERR_NETWORK') {
        setError('CropShift services are currently unreachable. Please check that backend service is running.');
      } else if (err?.status === 401 || err?.code === 'UNAUTHORIZED') {
        setError(err.message || 'Username or password is incorrect. If you do not have an account, please switch to Sign Up to create one.');
      } else if (err?.status === 403 || err?.code === 'FORBIDDEN') {
        setError(err.message || 'Account does not have permission for this portal.');
      } else if (err?.status === 422 || err?.code === 'VALIDATION_ERROR') {
        setError(err.message || 'Please check the information entered.');
      } else if (err?.status === 500 || err?.code === 'SERVER_ERROR') {
        setError(err.message || 'Something went wrong on the CropShift service.');
      } else if (err?.message) {
        setError(err.message);
      } else {
        setError('Incorrect username or password. If you do not have an account, please switch to Sign Up to create one.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccessMsg('');

    const cleanUsername = regUsername.trim();
    const cleanEmail = regEmail.trim();

    if (!cleanUsername) {
      setError('Username is required.');
      setIsLoading(false);
      return;
    }
    if (!cleanEmail || !cleanEmail.includes('@')) {
      setError('A valid email address is compulsory for registration.');
      setIsLoading(false);
      return;
    }
    if (!regPassword) {
      setError('Password is required.');
      setIsLoading(false);
      return;
    }

    const targetRole = selectedRole.toUpperCase();

    try {
      // 1. Register new user
      await apiClient.post('/api/v1/auth/register', {
        username: cleanUsername,
        email: cleanEmail,
        password: regPassword,
        role: targetRole,
      });

      setSuccessMsg('Account created successfully! Authorizing access...');

      // 2. Automatically log in with new credentials
      const formData = new URLSearchParams();
      formData.append('username', cleanUsername);
      formData.append('password', regPassword);

      const tokenRes = await apiClient.post('/api/v1/auth/token', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      const token = tokenRes.data.access_token;
      const userRes = await apiClient.get('/api/v1/auth/me', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const userProfile = userRes.data;
      login(token, userProfile);

      const authRole = (userProfile.role || 'FARMER').toString().toUpperCase();
      if (authRole === 'BUYER') {
        navigate('/buyer');
      } else {
        navigate('/');
      }
    } catch (err: any) {
      if (err?.code === 'NETWORK_ERROR' || err?.code === 'ERR_NETWORK') {
        setError('CropShift services are currently unreachable. Please check that backend service is running.');
      } else if (err?.message) {
        if (err.message.includes('Username already registered')) {
          setError('This username is already registered. Please choose another username or switch to Sign In.');
        } else {
          setError(err.message);
        }
      } else {
        setError('Registration failed. Please check your details and try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const isFarmer = selectedRole === 'farmer';

  return (
    <div className="relative min-h-screen w-full bg-slate-950 text-slate-100 flex flex-col justify-between overflow-x-hidden selection:bg-emerald-500 selection:text-slate-950">
      {/* Interactive 3D Topographic Agricultural Background */}
      <AgriTerrain3D activeRole={selectedRole} />

      {/* Ambient Lighting Overlay */}
      <div className="fixed inset-0 bg-gradient-to-b from-slate-950/70 via-slate-950/40 to-slate-950/80 pointer-events-none z-0" />

      {/* 3D Command Console Header */}
      <header className="relative z-10 w-full max-w-7xl mx-auto px-4 py-6 flex flex-col sm:flex-row justify-between items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-emerald-600 to-lime-400 p-0.5 shadow-lg shadow-emerald-500/20 flex items-center justify-center">
            <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center">
              <span className="text-xl">🌱</span>
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-2xl font-black text-white tracking-tight font-sans">
                Crop<span className="text-emerald-400">Shift</span>
              </span>
              <span className="text-[10px] font-extrabold uppercase tracking-widest px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                v2.0 3D HUD
              </span>
            </div>
            <p className="text-xs font-semibold text-slate-300 tracking-wide">
              Know Your Market Before You Sow.
            </p>
          </div>
        </div>

        {/* Live Command Telemetry Indicator */}
        <div className="hidden sm:flex items-center gap-3 px-4 py-2 rounded-xl bg-slate-900/60 border border-slate-800 backdrop-blur-md text-xs font-mono">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span className="text-slate-300">COMMAND NETWORK: <strong className="text-emerald-400">ONLINE</strong></span>
        </div>
      </header>

      {/* MAIN 3D INTERFACE CONTAINER */}
      <main className="relative z-10 w-full max-w-5xl mx-auto px-4 py-4 sm:py-8 flex flex-col items-center gap-8">
        
        {/* SECTION TITLE / INSTRUCTION */}
        <div className="text-center space-y-2 max-w-2xl">
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-white">
            Choose your portal
          </h1>
          <p className="text-xs sm:text-sm font-medium text-slate-300">
            Select your specialized agricultural command gateway to proceed.
          </p>
        </div>

        {/* 1. SPATIAL 3D PORTAL SELECTION OBJECTS */}
        <div className="w-full grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* FARMER PORTAL SPATIAL CARD */}
          <button
            type="button"
            onClick={() => handleRoleSelect('farmer')}
            className={`group relative text-left p-6 sm:p-7 rounded-3xl border-2 transition-all duration-300 cursor-pointer flex flex-col justify-between overflow-hidden shadow-2xl ${
              isFarmer
                ? 'bg-gradient-to-br from-emerald-950/90 via-slate-900/90 to-emerald-900/40 border-emerald-500 shadow-emerald-900/30 ring-2 ring-emerald-400/50 scale-[1.02]'
                : 'bg-slate-900/60 border-slate-800/80 hover:border-emerald-600/50 hover:bg-slate-900/80 hover:scale-[1.01]'
            }`}
            style={{
              transformStyle: 'preserve-3d',
              perspective: '1000px',
            }}
          >
            {/* Holographic Background Grid Glow */}
            <div className={`absolute inset-0 opacity-20 pointer-events-none transition-opacity duration-300 ${isFarmer ? 'opacity-40' : 'group-hover:opacity-30'}`}>
              <div className="absolute -right-10 -bottom-10 w-48 h-48 bg-emerald-500/30 rounded-full blur-3xl" />
            </div>

            <div className="relative z-10 space-y-4">
              <div className="flex items-center justify-between">
                <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">
                  🌾
                </div>
                {isFarmer && (
                  <span className="bg-emerald-500 text-slate-950 text-[10px] font-black uppercase tracking-wider px-3 py-1 rounded-full shadow-md shadow-emerald-500/30">
                    Active Portal
                  </span>
                )}
              </div>

              <div>
                <h2 className="text-xl font-extrabold text-white tracking-tight flex items-center gap-2">
                  Farmer Portal
                </h2>
                <p className="text-xs font-bold text-emerald-400 uppercase tracking-wider mt-0.5">
                  Know what to grow.
                </p>
                <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                  Get farm suitability scores, oilseed recommendations, peer advisories &amp; indicative buyer bidding.
                </p>
              </div>
            </div>

            <div className="relative z-10 pt-4 mt-4 border-t border-slate-800/60 flex items-center justify-between text-xs font-bold text-slate-400 group-hover:text-emerald-300 transition-colors">
              <span>Farm Intelligence &amp; Bidding</span>
              <span className="text-base font-black">➔</span>
            </div>
          </button>

          {/* BUYER PORTAL SPATIAL CARD */}
          <button
            type="button"
            onClick={() => handleRoleSelect('buyer')}
            className={`group relative text-left p-6 sm:p-7 rounded-3xl border-2 transition-all duration-300 cursor-pointer flex flex-col justify-between overflow-hidden shadow-2xl ${
              !isFarmer
                ? 'bg-gradient-to-br from-blue-950/90 via-slate-900/90 to-cyan-900/40 border-blue-500 shadow-blue-900/30 ring-2 ring-blue-400/50 scale-[1.02]'
                : 'bg-slate-900/60 border-slate-800/80 hover:border-blue-600/50 hover:bg-slate-900/80 hover:scale-[1.01]'
            }`}
            style={{
              transformStyle: 'preserve-3d',
              perspective: '1000px',
            }}
          >
            {/* Holographic Background Grid Glow */}
            <div className={`absolute inset-0 opacity-20 pointer-events-none transition-opacity duration-300 ${!isFarmer ? 'opacity-40' : 'group-hover:opacity-30'}`}>
              <div className="absolute -right-10 -bottom-10 w-48 h-48 bg-blue-500/30 rounded-full blur-3xl" />
            </div>

            <div className="relative z-10 space-y-4">
              <div className="flex items-center justify-between">
                <div className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">
                  🏬
                </div>
                {!isFarmer && (
                  <span className="bg-blue-500 text-slate-950 text-[10px] font-black uppercase tracking-wider px-3 py-1 rounded-full shadow-md shadow-blue-500/30">
                    Active Portal
                  </span>
                )}
              </div>

              <div>
                <h2 className="text-xl font-extrabold text-white tracking-tight flex items-center gap-2">
                  Buyer Portal
                </h2>
                <p className="text-xs font-bold text-cyan-400 uppercase tracking-wider mt-0.5">
                  Find what is being grown.
                </p>
                <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                  Post demand requirements, discover planned oilseed crops, place bids &amp; inspect stock inventory.
                </p>
              </div>
            </div>

            <div className="relative z-10 pt-4 mt-4 border-t border-slate-800/60 flex items-center justify-between text-xs font-bold text-slate-400 group-hover:text-cyan-300 transition-colors">
              <span>Procurement &amp; Mandi Network</span>
              <span className="text-base font-black">➔</span>
            </div>
          </button>
        </div>

        {/* 2. FLOATING 3D COMMAND CONSOLE (AUTH FORM PANEL) */}
        <div className="w-full max-w-xl bg-slate-900/85 backdrop-blur-2xl border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-[0_25px_60px_-15px_rgba(0,0,0,0.7)] relative overflow-hidden">
          
          {/* Subtle Accent Glow Ring */}
          <div className={`absolute -top-24 -left-24 w-64 h-64 rounded-full blur-3xl pointer-events-none ${isFarmer ? 'bg-emerald-500/15' : 'bg-blue-500/15'}`} />

          {/* AUTH TABS (SIGN IN vs SIGN UP) */}
          <div className="flex border-b border-slate-800 mb-6">
            <button
              type="button"
              onClick={() => {
                setAuthMode('login');
                setError('');
                setSuccessMsg('');
              }}
              className={`flex-1 py-3.5 text-xs sm:text-sm font-extrabold border-b-2 text-center transition-all cursor-pointer ${
                authMode === 'login'
                  ? isFarmer
                    ? 'border-emerald-500 text-emerald-400 bg-emerald-500/10'
                    : 'border-blue-500 text-blue-400 bg-blue-500/10'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              🔑 Sign In
            </button>
            <button
              type="button"
              onClick={() => {
                setAuthMode('register');
                setError('');
                setSuccessMsg('');
              }}
              className={`flex-1 py-3.5 text-xs sm:text-sm font-extrabold border-b-2 text-center transition-all cursor-pointer ${
                authMode === 'register'
                  ? isFarmer
                    ? 'border-emerald-500 text-emerald-400 bg-emerald-500/10'
                    : 'border-blue-500 text-blue-400 bg-blue-500/10'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              ✨ Sign Up (New User)
            </button>
          </div>

          {/* CONTEXTUAL ERROR ALERT BOX */}
          {error && (
            <div
              role="alert"
              className="bg-rose-950/70 border border-rose-500/50 text-rose-200 px-4 py-3.5 rounded-2xl mb-6 text-xs font-medium flex items-start gap-3 shadow-lg"
            >
              <span className="text-base">⚠️</span>
              <div className="flex-1 leading-relaxed">
                <strong className="block text-rose-400 font-bold mb-0.5">Authentication Error</strong>
                {error}
              </div>
            </div>
          )}

          {/* SUCCESS MESSAGE */}
          {successMsg && (
            <div className="bg-emerald-950/70 border border-emerald-500/50 text-emerald-200 px-4 py-3.5 rounded-2xl mb-6 text-xs font-medium flex items-start gap-3 shadow-lg">
              <span className="text-base">✅</span>
              <div className="flex-1 leading-relaxed">
                <strong className="block text-emerald-400 font-bold mb-0.5">Success</strong>
                {successMsg}
              </div>
            </div>
          )}

          {/* 3. SIGN IN FORM SECTION */}
          {authMode === 'login' ? (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-base font-extrabold text-white flex items-center gap-2">
                    <span>{isFarmer ? '🌾' : '🏢'}</span>
                    <span>{isFarmer ? 'Farmer Command Access' : 'Buyer Command Access'}</span>
                  </h2>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Enter your registered credentials to access your dashboard.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => handleRoleSelect(isFarmer ? 'buyer' : 'farmer')}
                  className="text-xs font-bold text-slate-400 hover:text-white transition-colors underline cursor-pointer"
                >
                  Switch role
                </button>
              </div>

              {/* Quick-Fill Demo Account Credentials Hint */}
              <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-2xl text-xs space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-extrabold text-slate-200">
                    Demo {isFarmer ? 'Farmer' : 'Buyer'} Credentials:
                  </span>
                  <button
                    type="button"
                    onClick={handleFillDemo}
                    className={`font-black text-xs hover:underline cursor-pointer ${isFarmer ? 'text-emerald-400' : 'text-cyan-400'}`}
                  >
                    Fill Credentials
                  </button>
                </div>
                <div className="text-slate-400 space-y-1 font-mono text-[11px]">
                  <p>
                    Username: <strong className="text-white font-bold">{isFarmer ? 'demo' : 'buyer_demo'}</strong>
                  </p>
                  <p>
                    Password: <strong className="text-white font-bold">password123</strong>
                  </p>
                </div>
              </div>

              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <label htmlFor="username" className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                    Username
                  </label>
                  <input
                    id="username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent min-h-[46px] transition-all"
                    autoComplete="username"
                    placeholder="Enter your username"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="password" className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                    Password
                  </label>
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent min-h-[46px] transition-all"
                    autoComplete="current-password"
                    placeholder="Enter your password"
                    required
                  />
                </div>

                <div className="pt-3">
                  <button
                    type="submit"
                    disabled={isLoading}
                    data-testid="login-submit-btn"
                    className={`w-full py-4 px-6 rounded-2xl font-black text-sm uppercase tracking-wider text-slate-950 transition-all duration-200 cursor-pointer shadow-xl disabled:opacity-50 disabled:cursor-not-allowed ${
                      isFarmer
                        ? 'bg-gradient-to-r from-emerald-400 via-lime-400 to-emerald-500 hover:brightness-110 shadow-emerald-950/50'
                        : 'bg-gradient-to-r from-cyan-400 via-blue-400 to-cyan-500 hover:brightness-110 shadow-blue-950/50'
                    }`}
                  >
                    {isLoading ? 'Authorizing Access…' : `Sign In as ${isFarmer ? 'Farmer' : 'Buyer'}`}
                  </button>
                </div>
              </form>

              <div className="text-center text-xs text-slate-400 pt-2">
                First-time user?{' '}
                <button
                  type="button"
                  onClick={() => {
                    setAuthMode('register');
                    setError('');
                  }}
                  className={`font-bold hover:underline cursor-pointer ${isFarmer ? 'text-emerald-400' : 'text-cyan-400'}`}
                >
                  Sign Up for a new {isFarmer ? 'Farmer' : 'Buyer'} account
                </button>
              </div>
            </div>
          ) : (
            /* 4. SIGN UP (REGISTRATION) FORM SECTION */
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-base font-extrabold text-white flex items-center gap-2">
                    <span>{isFarmer ? '🌾' : '🏢'}</span>
                    <span>Create New {isFarmer ? 'Farmer' : 'Buyer'} Account</span>
                  </h2>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Register your agricultural identity to receive your persistent ID.
                  </p>
                </div>
                <span className={`text-[10px] font-black uppercase tracking-wider px-2.5 py-1 rounded-lg border ${
                  isFarmer ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' : 'bg-blue-500/20 text-blue-300 border-blue-500/30'
                }`}>
                  Role: {selectedRole.toUpperCase()}
                </span>
              </div>

              <form onSubmit={handleRegister} className="space-y-4">
                <div>
                  <label htmlFor="regUsername" className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                    Choose Username *
                  </label>
                  <input
                    id="regUsername"
                    type="text"
                    value={regUsername}
                    onChange={(e) => setRegUsername(e.target.value)}
                    className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent min-h-[46px] transition-all"
                    placeholder="e.g. farmer_karnataka"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="regEmail" className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                    Email Address * <span className="text-emerald-400 font-bold lowercase">(compulsory)</span>
                  </label>
                  <input
                    id="regEmail"
                    type="email"
                    required
                    value={regEmail}
                    onChange={(e) => setRegEmail(e.target.value)}
                    className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent min-h-[46px] transition-all"
                    placeholder="e.g. farmer@cropshift.com"
                  />
                </div>

                <div>
                  <label htmlFor="regPassword" className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                    Choose Password *
                  </label>
                  <input
                    id="regPassword"
                    type="password"
                    value={regPassword}
                    onChange={(e) => setRegPassword(e.target.value)}
                    className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent min-h-[46px] transition-all"
                    placeholder="At least 6 characters"
                    required
                  />
                </div>

                <div className="pt-3">
                  <button
                    type="submit"
                    disabled={isLoading}
                    className={`w-full py-4 px-6 rounded-2xl font-black text-sm uppercase tracking-wider text-slate-950 transition-all duration-200 cursor-pointer shadow-xl disabled:opacity-50 disabled:cursor-not-allowed ${
                      isFarmer
                        ? 'bg-gradient-to-r from-emerald-400 via-lime-400 to-emerald-500 hover:brightness-110 shadow-emerald-950/50'
                        : 'bg-gradient-to-r from-cyan-400 via-blue-400 to-cyan-500 hover:brightness-110 shadow-blue-950/50'
                    }`}
                  >
                    {isLoading ? 'Creating Account…' : `Create Account & Sign In as ${isFarmer ? 'Farmer' : 'Buyer'}`}
                  </button>
                </div>
              </form>

              <div className="text-center text-xs text-slate-400 pt-2">
                Already registered?{' '}
                <button
                  type="button"
                  onClick={() => {
                    setAuthMode('login');
                    setError('');
                  }}
                  className={`font-bold hover:underline cursor-pointer ${isFarmer ? 'text-emerald-400' : 'text-cyan-400'}`}
                >
                  Sign In here
                </button>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* 3D HUD FOOTER */}
      <footer className="relative z-10 w-full max-w-7xl mx-auto px-4 py-6 text-center text-xs text-slate-400 border-t border-slate-900 mt-8">
        <p>© CropShift Intelligence Engine — Know Your Market Before You Sow.</p>
      </footer>
    </div>
  );
}
