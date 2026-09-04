import React from 'react';
import { NavLink } from 'react-router-dom';

export default function FarmerBottomNav() {
  return (
    <nav
      aria-label="Farmer Main Navigation"
      className="fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-md border-t border-gray-200 shadow-lg md:hidden"
    >
      <div className="max-w-md mx-auto px-3 h-16 flex items-center justify-between relative">
        {/* 1. Home / Farm Advisory */}
        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            `flex flex-col items-center justify-center flex-1 py-1 transition-colors ${
              isActive ? 'text-green-700 font-extrabold' : 'text-gray-500 hover:text-gray-900 font-medium'
            }`
          }
        >
          <span className="text-xl" aria-hidden="true">🏠</span>
          <span className="text-[10px] tracking-tight mt-0.5">Home</span>
        </NavLink>

        {/* 2. Map */}
        <NavLink
          to="/map"
          className={({ isActive }) =>
            `flex flex-col items-center justify-center flex-1 py-1 transition-colors ${
              isActive ? 'text-green-700 font-extrabold' : 'text-gray-500 hover:text-gray-900 font-medium'
            }`
          }
        >
          <span className="text-xl" aria-hidden="true">🗺️</span>
          <span className="text-[10px] tracking-tight mt-0.5">Map</span>
        </NavLink>

        {/* 3. Bidding — CENTRAL AND VISUALLY PROMINENT */}
        <div className="flex flex-col items-center justify-center flex-1 relative -top-3.5">
          <NavLink
            to="/bidding"
            aria-label="Bidding Marketplace"
            className={({ isActive }) =>
              `w-13 h-13 rounded-full bg-gradient-to-tr from-green-700 via-primary-700 to-green-600 text-white flex items-center justify-center shadow-md border-3 border-white transition-transform active:scale-95 ${
                isActive ? 'ring-3 ring-green-400 scale-105 shadow-green-200' : 'hover:scale-105'
              }`
            }
          >
            <span className="text-xl" aria-hidden="true">⚖️</span>
          </NavLink>
          <span className="text-[10px] font-extrabold text-green-900 tracking-tight mt-0.5">Bids</span>
        </div>

        {/* 4. IVR / Voice Advisory */}
        <NavLink
          to="/ivr"
          className={({ isActive }) =>
            `flex flex-col items-center justify-center flex-1 py-1 transition-colors ${
              isActive ? 'text-green-700 font-extrabold' : 'text-gray-500 hover:text-gray-900 font-medium'
            }`
          }
        >
          <span className="text-xl" aria-hidden="true">📞</span>
          <span className="text-[10px] tracking-tight mt-0.5">IVR Call</span>
        </NavLink>

        {/* 5. Subsidies */}
        <NavLink
          to="/subsidies"
          className={({ isActive }) =>
            `flex flex-col items-center justify-center flex-1 py-1 transition-colors ${
              isActive ? 'text-green-700 font-extrabold' : 'text-gray-500 hover:text-gray-900 font-medium'
            }`
          }
        >
          <span className="text-xl" aria-hidden="true">🏛️</span>
          <span className="text-[10px] tracking-tight mt-0.5">Subsidies</span>
        </NavLink>
      </div>
    </nav>
  );
}

