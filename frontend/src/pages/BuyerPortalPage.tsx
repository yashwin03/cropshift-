import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import { useAuth } from '../contexts/AuthContext';
import type { BuyerDemand } from '../types/api';

const MOCK_DEMANDS: BuyerDemand[] = [
  {
    id: 201,
    buyer_id: 1,
    crop_id: 1,
    crop_name: 'Groundnut (Kadir-6)',
    variety: 'Kadir-6',
    quantity_quintals: 200,
    target_price_per_quintal: 6350,
    delivery_district: 'Dharwad Industrial Hub',
    status: 'ACTIVE',
    company_name: 'Karnataka Agro Processing Ltd.',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    posted_date: '2 hours ago',
  },
  {
    id: 202,
    buyer_id: 1,
    crop_id: 2,
    crop_name: 'Sunflower',
    variety: 'KBSH-44',
    quantity_quintals: 150,
    target_price_per_quintal: 6150,
    delivery_district: 'Belagavi Cluster',
    status: 'ACTIVE',
    company_name: 'Deccan Oil Mills Corp',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    posted_date: '1 day ago',
  },
];

export default function BuyerPortalPage() {
  const { token, setRole } = useAuth();
  const [demands, setDemands] = useState<BuyerDemand[]>(MOCK_DEMANDS);
  const [showDemandModal, setShowDemandModal] = useState<boolean>(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Form state
  const [cropRequired, setCropRequired] = useState('Groundnut');
  const [quantity, setQuantity] = useState('100');
  const [targetPrice, setTargetPrice] = useState('6300');
  const [location, setLocation] = useState('Dharwad Mandi');

  useEffect(() => {
    if (!token) return;
    fetch('/api/v1/buyer/demands/me', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data && Array.isArray(data) && data.length > 0) {
          setDemands(data);
        }
      })
      .catch(() => {});
  }, [token]);

  const handlePostDemand = async (e: React.FormEvent) => {
    e.preventDefault();
    const qtyNum = parseFloat(quantity) || 100;
    const priceNum = parseFloat(targetPrice) || 6300;

    if (token) {
      try {
        const res = await fetch('/api/v1/buyer/demands', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            crop_id: 1,
            variety: cropRequired,
            quantity_quintals: qtyNum,
            target_price_per_quintal: priceNum,
            delivery_district: location,
          }),
        });

        if (res.ok) {
          const created: BuyerDemand = await res.json();
          setDemands([created, ...demands]);
          setShowDemandModal(false);
          setSuccessMessage(`Posted buyer demand DEMAND-${created.id} for ${created.crop_name || cropRequired}!`);
          setTimeout(() => setSuccessMessage(null), 5000);
          return;
        }
      } catch {
        // Fallback
      }
    }

    const newDemand: BuyerDemand = {
      id: 200 + demands.length + 1,
      buyer_id: 1,
      crop_id: 1,
      crop_name: cropRequired,
      quantity_quintals: qtyNum,
      target_price_per_quintal: priceNum,
      delivery_district: location,
      company_name: 'My Wholesale Corp',
      posted_date: 'Just now',
      status: 'ACTIVE',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    setDemands([newDemand, ...demands]);
    setShowDemandModal(false);
    setSuccessMessage(`Posted buyer demand DEMAND-${newDemand.id} for ${cropRequired}!`);
    setTimeout(() => setSuccessMessage(null), 5000);
  };

  const handleCancelDemand = async (demandId: number) => {
    if (token) {
      try {
        const res = await fetch(`/api/v1/buyer/demands/${demandId}`, {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          setDemands(demands.filter((d) => d.id !== demandId));
          setSuccessMessage(`Cancelled buyer demand DEMAND-${demandId}.`);
          setTimeout(() => setSuccessMessage(null), 5000);
          return;
        }
      } catch {
        // Fallback
      }
    }
    setDemands(demands.filter((d) => d.id !== demandId));
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Buyer Portal Header */}
      <div className="bg-slate-900/90 backdrop-blur-2xl border border-blue-900/40 p-6 rounded-3xl shadow-2xl space-y-4">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <div className="inline-flex items-center gap-2 bg-blue-950/80 text-blue-300 text-xs font-bold px-3.5 py-1 rounded-full border border-blue-700/50">
              <span>Commercial Buyer Portal</span>
              <span>•</span>
              <span>Farmer Crop Discovery & Procurement Marketplace</span>
            </div>
            <h1 className="text-2xl md:text-3xl font-black text-white mt-2 tracking-tight">
              Farmer Procurement Overview
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 mt-1 max-w-2xl">
              Procure oilseeds directly from regional farmers with complete quality metrics and offer management.
            </p>
          </div>

          <Button
            variant="primary"
            onClick={() => setShowDemandModal(true)}
            className="bg-blue-600 hover:bg-blue-500 text-white font-extrabold text-xs py-2.5 px-4 shadow-lg shadow-blue-900/50"
          >
            + Post Procurement Requirement
          </Button>
        </div>
      </div>

      {/* 5 Primary Action Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <button
          type="button"
          onClick={() => setShowDemandModal(true)}
          className="p-4 bg-slate-900/80 backdrop-blur-xl border border-slate-800 hover:border-blue-500/60 rounded-2xl text-left transition-all space-y-1 group shadow-xl"
        >
          <div className="font-extrabold text-white text-xs group-hover:text-blue-400">Post Requirement</div>
          <div className="text-[10px] text-slate-400">Specify oilseed demand</div>
        </button>

        <Link
          to="/bidding"
          onClick={() => setRole('buyer')}
          className="p-4 bg-slate-900/80 backdrop-blur-xl border border-slate-800 hover:border-blue-500/60 rounded-2xl text-left transition-all space-y-1 group block shadow-xl"
        >
          <div className="font-extrabold text-white text-xs group-hover:text-blue-400">Find Planned Crops</div>
          <div className="text-[10px] text-slate-400">Discover pre-sowing lots</div>
        </Link>

        <Link
          to="/bidding"
          onClick={() => setRole('buyer')}
          className="p-4 bg-slate-900/80 backdrop-blur-xl border border-slate-800 hover:border-blue-500/60 rounded-2xl text-left transition-all space-y-1 group block shadow-xl"
        >
          <div className="font-extrabold text-white text-xs group-hover:text-blue-400">Find Harvested Crops</div>
          <div className="text-[10px] text-slate-400">View ready stock inventory</div>
        </Link>

        <Link
          to="/bidding"
          onClick={() => setRole('buyer')}
          className="p-4 bg-slate-900/80 backdrop-blur-xl border border-slate-800 hover:border-blue-500/60 rounded-2xl text-left transition-all space-y-1 group block shadow-xl"
        >
          <div className="text-xl">⚡</div>
          <div className="font-extrabold text-white text-xs group-hover:text-blue-400">My Offers</div>
          <div className="text-[10px] text-slate-400">Track submitted bids</div>
        </Link>

        <Link
          to="/bidding"
          onClick={() => setRole('buyer')}
          className="p-4 bg-slate-900/80 backdrop-blur-xl border border-slate-800 hover:border-blue-500/60 rounded-2xl text-left transition-all space-y-1 group block shadow-xl"
        >
          <div className="text-xl">🤝</div>
          <div className="font-extrabold text-white text-xs group-hover:text-blue-400">My Deals</div>
          <div className="text-[10px] text-slate-400">Accepted trade allocations</div>
        </Link>
      </div>

      {/* Success Alert */}
      {successMessage && (
        <div className="p-4 bg-blue-950/80 border border-blue-500/40 text-blue-200 rounded-2xl font-bold text-xs shadow-xl flex items-center justify-between">
          <span>✅ {successMessage}</span>
          <button type="button" onClick={() => setSuccessMessage(null)} className="text-blue-400 hover:underline">
            Dismiss
          </button>
        </div>
      )}

      {/* Active Buyer Demands List */}
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-black text-white">Live Buyer Procurement Demands ({demands.length})</h2>
          <Link
            to="/bidding"
            onClick={() => setRole('buyer')}
            className="text-xs font-bold text-blue-400 hover:text-blue-300"
          >
            Go to Active Bidding Auctions &rarr;
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {demands.map((demand) => (
            <div
              key={demand.id}
              className="bg-slate-900/90 backdrop-blur-2xl p-5 rounded-2xl border border-slate-800 shadow-xl space-y-4"
            >
              <div className="flex justify-between items-center">
                <Badge variant="neutral" className="text-xs font-bold bg-blue-950 text-blue-300 border border-blue-800">
                  DEMAND-{demand.id}
                </Badge>
                <span className="text-xs font-bold text-slate-400">{demand.company_name || 'Commercial Buyer'}</span>
              </div>

              <div>
                <h3 className="text-base font-black text-white">{demand.crop_name || demand.variety || 'Groundnut'}</h3>
                <p className="text-xs text-slate-400">{demand.quantity_quintals} Quintals required at {demand.delivery_district}</p>
              </div>

              <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 flex justify-between items-center">
                <div>
                  <span className="block text-[10px] uppercase font-bold text-slate-400">Target Offer Price</span>
                  <span className="text-xl font-black text-blue-400">₹{demand.target_price_per_quintal.toLocaleString()}/Q</span>
                </div>
                <div className="text-right">
                  <span className="block text-[10px] uppercase font-bold text-slate-400">Quantity Needed</span>
                  <span className="text-sm font-bold text-white">{demand.quantity_quintals} Quintals</span>
                </div>
              </div>

              <div className="flex justify-between items-center text-xs pt-2 border-t border-slate-800">
                <span className="text-slate-400">Posted {demand.posted_date || 'Recently'}</span>
                <div className="flex gap-3 items-center">
                  <button
                    type="button"
                    onClick={() => handleCancelDemand(demand.id)}
                    className="text-rose-400 hover:underline font-bold text-xs"
                  >
                    Cancel Demand
                  </button>
                  <Link
                    to="/bidding"
                    className="text-blue-400 font-bold hover:underline"
                  >
                    View Farmer Lots &rarr;
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Post Buyer Demand Modal */}
      {showDemandModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 rounded-3xl max-w-md w-full p-6 space-y-4 shadow-2xl border border-slate-800">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <h3 className="text-base font-black text-white">Post Procurement Requirement</h3>
              <button
                type="button"
                onClick={() => setShowDemandModal(false)}
                className="text-slate-400 hover:text-white font-bold text-xl"
              >
                ×
              </button>
            </div>

            <form onSubmit={handlePostDemand} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-bold uppercase tracking-wider mb-1">
                  Required Crop
                </label>
                <input
                  type="text"
                  required
                  value={cropRequired}
                  onChange={(e) => setCropRequired(e.target.value)}
                  className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white font-semibold focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-bold uppercase tracking-wider mb-1">
                  Quantity Needed (Quintals)
                </label>
                <input
                  type="number"
                  required
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white font-semibold focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-bold uppercase tracking-wider mb-1">
                  Target Buying Price (₹ per Quintal)
                </label>
                <input
                  type="number"
                  required
                  value={targetPrice}
                  onChange={(e) => setTargetPrice(e.target.value)}
                  className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white font-semibold focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-bold uppercase tracking-wider mb-1">
                  Delivery / Mandi Location
                </label>
                <input
                  type="text"
                  required
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white font-semibold focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="flex gap-2 pt-2">
                <Button type="button" variant="outline" className="flex-1 bg-slate-950 text-slate-300" onClick={() => setShowDemandModal(false)}>
                  Cancel
                </Button>
                <Button type="submit" variant="primary" className="flex-1 bg-blue-600 hover:bg-blue-500">
                  Publish Procurement Demand
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
