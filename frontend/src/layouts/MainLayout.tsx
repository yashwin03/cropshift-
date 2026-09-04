import React, { useState } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { USE_MOCKS } from '../mocks';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage, type Language } from '../contexts/LanguageContext';
import { getFarmDetails } from '../utils/storage';
import Button from '../components/common/Button';
import FarmerBottomNav from '../components/common/FarmerBottomNav';
import AgriTerrain3D from '../components/3d/AgriTerrain3D';
import {
  IconPlant,
  IconChartBar,
  IconUser,
  IconCoins,
  IconStore,
  IconFileText,
  IconMapPin,
  IconPhone,
  IconBuilding,
  IconSparkles,
} from '../components/common/Icons';

interface MainLayoutProps {
  children: React.ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [copiedId, setCopiedId] = useState(false);
  const { user, logout, activeRole } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const navigate = useNavigate();
  const location = useLocation();

  const isLoginPage = location.pathname === '/login';

  if (isLoginPage) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 sm:p-6 font-sans">
        {children}
      </div>
    );
  }

  const farmerId = user?.farmer_id || 'FS-000123';
  const farmerName = user?.username || 'Farmer';

  const handleCopyFarmerId = () => {
    navigator.clipboard?.writeText(farmerId);
    setCopiedId(true);
    setTimeout(() => setCopiedId(false), 2000);
  };

  const farmerNavItems = [
    { path: '/', label: 'Home Dashboard', icon: <IconChartBar size={18} className="text-amber-400" /> },
    { path: '/recommendation', label: 'Crop Simulator', icon: <IconPlant size={18} className="text-emerald-400" />, badge: '3D' },
    { path: '/farm-info', label: 'My Farm Profile', icon: <IconUser size={18} className="text-blue-400" /> },
    { path: '/profit', label: 'Profit & Market', icon: <IconCoins size={18} className="text-amber-400" /> },
    { path: '/bidding', label: 'Marketplace', icon: <IconStore size={18} className="text-emerald-400" />, isLive: true },
    { path: '/subsidies', label: 'Subsidies & Schemes', icon: <IconFileText size={18} className="text-purple-400" /> },
    { path: '/map', label: 'Map Explorer', icon: <IconMapPin size={18} className="text-amber-400" />, badge: '3D' },
    { path: '/ivr', label: 'Offline Support', icon: <IconPhone size={18} className="text-emerald-400" /> },
  ];

  const buyerNavItems = [
    { path: '/buyer', label: 'Home Buyer Command', icon: <IconBuilding size={18} className="text-blue-400" /> },
    { path: '/bidding', label: 'Marketplace', icon: <IconStore size={18} className="text-emerald-400" />, isLive: true },
  ];

  const navItems = activeRole === 'buyer' ? buyerNavItems : farmerNavItems;

  return (
    <div className="min-h-screen flex bg-slate-950 text-slate-100 font-sans relative overflow-hidden">
      {/* Ambient 3D Topographic Terrain Canvas Background */}
      <AgriTerrain3D activeRole={activeRole} />

      {/* Demo Banner if mock active */}
      {USE_MOCKS && (
        <div className="fixed top-0 left-0 right-0 bg-amber-500 text-slate-950 text-[11px] font-black text-center py-1 z-50 shadow-md">
          Demo Mode — CropShift Dual Portal
        </div>
      )}

      {/* 1. LEFT SPATIAL SIDEBAR (Desktop) */}
      <aside className={`fixed inset-y-0 left-0 z-40 w-64 bg-slate-900/90 backdrop-blur-2xl border-r border-slate-800/80 flex flex-col justify-between transition-transform duration-300 ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}>
        <div className="p-5 space-y-6 overflow-y-auto">
          {/* Brand Logo & Tagline */}
          <div className="space-y-1">
            <NavLink to={activeRole === 'buyer' ? '/buyer' : '/'} className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-emerald-500 to-green-400 flex items-center justify-center font-black text-slate-950 shadow-lg shadow-emerald-500/20">
                🌱
              </div>
              <span className="text-xl font-black tracking-tight text-white flex items-center">
                <span>Crop</span>
                <span className="text-emerald-400">Shift</span>
              </span>
            </NavLink>
            <p className="text-[10px] text-slate-400 font-medium tracking-wide">
              Know Your Market Before You Sow.
            </p>
          </div>

          {/* Navigation Menu */}
          <nav className="space-y-1.5" aria-label="Main Navigation">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={() => setIsSidebarOpen(false)}
                  className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-bold transition-all ${
                    isActive
                      ? 'bg-gradient-to-r from-emerald-600 to-emerald-700 text-white shadow-lg shadow-emerald-900/40 ring-1 ring-emerald-400/40'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/70'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-base">{item.icon}</span>
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="text-[9px] font-extrabold px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                      {item.badge}
                    </span>
                  )}
                  {item.isLive && (
                    <span className="text-[9px] font-black px-1.5 py-0.5 rounded bg-purple-500 text-white animate-pulse">
                      LIVE
                    </span>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Sidebar Bottom Card — Farmer ID & Profile */}
        <div className="p-4 border-t border-slate-800/80 bg-slate-950/60 space-y-3">
          <div className="p-3 bg-slate-900 rounded-xl border border-slate-800 space-y-1.5">
            <div className="text-[10px] uppercase font-extrabold text-slate-400 tracking-wider">Farmer ID</div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-black text-emerald-400 font-mono tracking-wider">{farmerId}</span>
              <button
                type="button"
                onClick={handleCopyFarmerId}
                className="text-xs text-slate-400 hover:text-white p-1 rounded hover:bg-slate-800 transition-colors"
                title="Copy Farmer ID"
              >
                {copiedId ? '✓' : '📋'}
              </button>
            </div>
            <div className="text-[10px] text-slate-400 truncate">
              {getFarmDetails()?.state || 'Karnataka'} • {getFarmDetails()?.district || 'Shivamogga'} District
            </div>
          </div>

          <button
            type="button"
            onClick={() => navigate('/farm-info')}
            className="w-full py-2 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white rounded-xl text-xs font-bold border border-slate-700 flex items-center justify-center gap-2 transition-colors"
          >
            <span>⚙️</span> Profile & Settings
          </button>
        </div>
      </aside>

      {/* 2. MAIN CONTENT AREA */}
      <div className="flex-1 flex flex-col md:pl-64 min-w-0 z-10">
        {/* Top Header Bar */}
        <header className="sticky top-0 z-30 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800/80 px-4 sm:px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="md:hidden p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-900 border border-slate-800"
              aria-label="Toggle Navigation Sidebar"
            >
              ☰
            </button>

            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base sm:text-lg font-black text-white flex items-center gap-1.5">
                  <span>Welcome back,</span>
                  <span className="text-emerald-400">{farmerName}</span>
                  <span className="text-xs text-emerald-400">✓</span>
                </h1>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">
                Happy farming! Let's grow the best together.
              </p>
            </div>
          </div>

          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 bg-slate-900/90 border border-emerald-500/30 rounded-full text-xs">
            <span className="text-slate-400 font-medium">Your Farmer ID</span>
            <span className="font-mono font-black text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded-full border border-emerald-500/40">
              {farmerId}
            </span>
            <button
              type="button"
              onClick={handleCopyFarmerId}
              className="text-slate-400 hover:text-white text-xs"
            >
              {copiedId ? '✓' : '📋'}
            </button>
          </div>

          <div className="flex items-center gap-3">
            <div className="relative">
              <button
                type="button"
                onClick={() => setShowNotifications(!showNotifications)}
                className="relative p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white transition-colors"
                aria-label="Notifications"
              >
                <span className="text-sm">🔔</span>
                <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-emerald-500" />
              </button>

              {showNotifications && (
                <div className="absolute right-0 mt-2 w-72 bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-3 z-50 space-y-2 text-xs">
                  <div className="flex justify-between items-center pb-2 border-b border-slate-800 font-bold text-white">
                    <span>Smart Notifications</span>
                    <span className="text-[10px] text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded-full border border-emerald-500/30">
                      2 New
                    </span>
                  </div>
                  <div className="space-y-2 text-slate-300">
                    <div className="p-2 bg-slate-950 rounded-xl border border-slate-800">
                      <div className="font-bold text-white">Raichur APMC Price Alert</div>
                      <div className="text-[11px] text-slate-400">Groundnut up +2.3% to ₹6,420/Quintal today.</div>
                    </div>
                    <div className="p-2 bg-slate-950 rounded-xl border border-slate-800">
                      <div className="font-bold text-white">Optimal Sowing Window</div>
                      <div className="text-[11px] text-slate-400">Ideal weather & soil moisture for Groundnut sowing.</div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="flex items-center gap-1.5 px-2 py-1 bg-slate-900 border border-slate-800 rounded-xl text-xs font-bold text-slate-200">
              <span>🌐</span>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value as Language)}
                className="bg-transparent text-white font-bold text-xs focus:outline-none cursor-pointer"
                aria-label="Language Selector"
              >
                <option value="en" className="bg-slate-900 text-white">English</option>
                <option value="kn" className="bg-slate-900 text-white">ಕನ್ನಡ (Kannada)</option>
                <option value="hi" className="bg-slate-900 text-white">हिंदी (Hindi)</option>
              </select>
            </div>

            <div className="flex items-center gap-2 border-l border-slate-800 pl-3">
              <div className="w-8 h-8 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 flex items-center justify-center font-black text-xs">
                👤
              </div>
              <div className="hidden md:flex flex-col text-left text-xs">
                <span className="font-bold text-white leading-none">{farmerName}</span>
                <span className="text-[10px] text-slate-400 capitalize">{activeRole}</span>
              </div>
              {user ? (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    logout();
                    navigate('/login');
                  }}
                  className="text-xs py-1 px-2.5 bg-slate-900 border-slate-800 text-slate-300 hover:text-white"
                >
                  Logout
                </Button>
              ) : (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate('/login')}
                  className="text-xs py-1 px-2.5 bg-slate-900 border-slate-800 text-slate-300 hover:text-white"
                >
                  Login
                </Button>
              )}
            </div>
          </div>
        </header>

        {/* Main Body */}
        <main className="flex-1 p-4 sm:p-6 space-y-6">
          {children}
        </main>

        <footer className="p-4 border-t border-slate-900 text-center text-xs text-slate-600">
          CropShift Agricultural Command Center • Know Your Market Before You Sow
        </footer>
      </div>

      {/* Mobile Bottom Navigation Bar */}
      {activeRole === 'farmer' && <FarmerBottomNav />}
    </div>
  );
}
