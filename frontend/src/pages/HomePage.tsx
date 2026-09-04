import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import DecisionBadge from '../components/score/DecisionBadge';
import { getFarmDetails, getRecommendation, saveFarmDetails, saveRecommendation, clearFarmState } from '../utils/storage';
import { GOLDEN_DEMO_FARM, GOLDEN_DEMO_RECOMMENDATION } from '../mocks/fixtures';
import type { FarmDetails } from '../mocks/fixtures';
import type { RecommendationResponse } from '../types/api';
import PlanCropModal from '../components/farmer/PlanCropModal';
import FarmPlot3D from '../components/3d/FarmPlot3D';
import {
  IconPlant,
  IconMapPin,
  IconDroplet,
  IconCoins,
  IconShield,
  IconStore,
  IconUsers,
  IconArrowRight,
  IconSparkles,
  IconCheck,
  IconAlertCircle,
  IconTrophy,
} from '../components/common/Icons';

export default function HomePage() {
  const navigate = useNavigate();
  const [farm, setFarm] = useState<FarmDetails | null>(null);
  const [rec, setRec] = useState<RecommendationResponse | null>(null);
  const [isPlanModalOpen, setIsPlanModalOpen] = useState(false);
  const [selectedCrop, setSelectedCrop] = useState<string>('Groundnut');
  const [showFull3dModal, setShowFull3dModal] = useState(false);

  useEffect(() => {
    const f = getFarmDetails();
    const r = getRecommendation();
    setFarm(f);
    setRec(r);
    if (r?.recommended_crop) {
      setSelectedCrop(r.recommended_crop);
    }
  }, []);

  const handleLoadDemo = () => {
    saveFarmDetails(GOLDEN_DEMO_FARM);
    saveRecommendation(GOLDEN_DEMO_RECOMMENDATION);
    setFarm(GOLDEN_DEMO_FARM);
    setRec(GOLDEN_DEMO_RECOMMENDATION);
    setSelectedCrop(GOLDEN_DEMO_RECOMMENDATION.recommended_crop);
  };

  const handleReset = () => {
    clearFarmState();
    setFarm(null);
    setRec(null);
  };

  const getCropMetrics = (crop: string) => {
    switch (crop.toLowerCase()) {
      case 'sesame':
        return {
          score: 87,
          farmSuitability: 89,
          waterSuitability: 91,
          economicPotential: 84,
          estProfit: 52400,
          currentProfit: 32000,
          apmcPrice: 7100,
          priceTrend: '+1.8%',
          advisory: 'Sesame exhibits excellent drought tolerance for low-rainfall windows.',
        };
      case 'sunflower':
        return {
          score: 83,
          farmSuitability: 85,
          waterSuitability: 80,
          economicPotential: 86,
          estProfit: 49800,
          currentProfit: 32000,
          apmcPrice: 5850,
          priceTrend: '+3.1%',
          advisory: 'High seed oil yield. Ideal for black cotton soil with medium irrigation.',
        };
      case 'soybean':
        return {
          score: 78,
          farmSuitability: 81,
          waterSuitability: 76,
          economicPotential: 82,
          estProfit: 44200,
          currentProfit: 32000,
          apmcPrice: 4800,
          priceTrend: '+0.9%',
          advisory: 'Moderate water requirement. High nitrogen fixation benefits soil health.',
        };
      case 'mustard':
        return {
          score: 75,
          farmSuitability: 77,
          waterSuitability: 75,
          economicPotential: 79,
          estProfit: 41600,
          currentProfit: 32000,
          apmcPrice: 5400,
          priceTrend: '+1.2%',
          advisory: 'Cold hardy crop suitable for winter Rabi season in northern soils.',
        };
      default:
        return {
          score: rec?.safety_score || rec?.overall_score || 92,
          farmSuitability: rec?.farm_suitability_score || rec?.suitability_score || 90,
          waterSuitability: rec?.water_suitability_score || rec?.suitability_score || 94,
          economicPotential: rec?.economic_potential_score || rec?.profitability_score || 91,
          estProfit: rec?.expected_profit || 58000,
          currentProfit: rec?.current_crop_profit || 32000,
          apmcPrice: 6400,
          priceTrend: '+2.4%',
          advisory: 'Optimal oilseed shift. Yield stability and high demand in local mandis.',
        };
    }
  };

  const metrics = getCropMetrics(selectedCrop);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* 1. HERO HEADER BANNER */}
      <div className="bg-gradient-to-r from-emerald-950 via-slate-900 to-amber-950 text-white p-6 sm:p-8 rounded-3xl border border-amber-500/30 shadow-2xl space-y-4">
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 bg-amber-500/20 text-amber-300 text-xs font-black px-3.5 py-1 rounded-full border border-amber-500/30">
              <IconSparkles size={14} className="text-amber-400" />
              <span>Namaste, {farm?.farmer_name || 'Rajesh'}!</span>
              <span className="text-amber-500/60">&bull;</span>
              <span>CROPShift AI Decision System</span>
            </div>
            <h1 className="text-2xl sm:text-4xl font-black tracking-tight text-white leading-tight">
              Oilseed Shift & Farmer Platform
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
              Analyze soil, water, and economics to switch to high-value oilseeds like Groundnut, Sesame, and Sunflower.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button
              variant="primary"
              onClick={() => setIsPlanModalOpen(true)}
              className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-black text-xs py-2.5 px-4 shadow-xl flex items-center gap-2 cursor-pointer"
            >
              <IconStore size={16} />
              <span>+ Add Crop to Marketplace</span>
            </Button>
            <Button
              variant="outline"
              onClick={() => navigate('/analyze')}
              className="bg-slate-950/80 hover:bg-slate-900 border-slate-800 text-amber-300 font-black text-xs py-2.5 px-4 flex items-center gap-2 cursor-pointer"
            >
              <IconPlant size={16} />
              <span>Start Crop Simulator</span>
            </Button>
            <button
              type="button"
              onClick={handleLoadDemo}
              className="px-3 py-2 bg-slate-950/80 hover:bg-slate-900 border border-slate-800 text-xs text-slate-300 font-bold rounded-xl"
            >
              Load Golden Demo Data
            </button>
            {farm && (
              <button
                type="button"
                onClick={handleReset}
                className="px-3 py-2 bg-slate-950/80 hover:bg-slate-900 border border-slate-800 text-xs text-rose-400 font-bold rounded-xl"
              >
                Reset Farm Profile
              </button>
            )}
          </div>
        </div>

        {/* Quick Advisory Stats Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs pt-2 border-t border-amber-500/20">
          <div className="p-2.5 bg-slate-950/60 rounded-xl border border-slate-800/80">
            <div className="text-slate-400 font-bold text-[10px] uppercase">Farm Advisory</div>
            <div className="text-white font-extrabold mt-0.5">Optimal Shift Active</div>
          </div>
          <div className="p-2.5 bg-slate-950/60 rounded-xl border border-slate-800/80">
            <div className="text-slate-400 font-bold text-[10px] uppercase">Weather Advisory</div>
            <div className="text-white font-extrabold mt-0.5">Favorable Kharif</div>
          </div>
          <div className="p-2.5 bg-slate-950/60 rounded-xl border border-slate-800/80">
            <div className="text-slate-400 font-bold text-[10px] uppercase">Mandi Market Price</div>
            <div className="text-white font-extrabold mt-0.5">₹6,400/Q Groundnut</div>
          </div>
          <div className="p-2.5 bg-slate-950/60 rounded-xl border border-slate-800/80">
            <div className="text-slate-400 font-bold text-[10px] uppercase">Buyer Opportunities</div>
            <div className="text-white font-extrabold mt-0.5">Verified Procurement</div>
          </div>
        </div>
      </div>

      {/* LATEST RECOMMENDATION CARD */}
      {rec && (
        <div className="p-4 bg-slate-900/90 rounded-2xl border border-slate-800 flex flex-wrap justify-between items-center text-xs text-slate-300 gap-3 shadow-xl">
          <div className="flex items-center gap-3">
            <DecisionBadge decision={rec.decision || 'SWITCH'} size="sm" />
            <div>
              <div className="text-[10px] text-slate-400 font-bold uppercase">Recommended Crop</div>
              <div className="text-sm font-black text-white">{rec.recommended_crop}</div>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="text-[10px] text-slate-400 font-bold uppercase">Estimated Net Gain</div>
              <div className="text-sm font-black text-emerald-400">
                {rec.profit_difference >= 0 ? '+' : ''}₹{Math.abs(rec.profit_difference).toLocaleString('en-IN')}/acre
              </div>
            </div>
            <div className="text-right">
              <div className="text-[10px] text-slate-400 font-bold uppercase">Safety Score</div>
              <div className="text-sm font-black text-white"><span>{rec.overall_score || rec.safety_score}</span>%</div>
            </div>
            <button
              type="button"
              onClick={() => navigate('/recommendation')}
              className="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs flex items-center gap-1.5"
            >
              <span>View Full Analysis</span>
              <IconArrowRight size={14} />
            </button>
          </div>
        </div>
      )}

      {/* 2. CROP SIMULATOR 3D & FARM DETAILS */}
      <div className="bg-slate-900/90 backdrop-blur-2xl rounded-3xl border border-slate-800 shadow-2xl p-5 sm:p-6 space-y-5">
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 border-b border-slate-800/80 pb-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <IconPlant size={22} className="text-emerald-400" />
              <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight">Crop Simulator 3D</h2>
            </div>
            <p className="text-xs text-slate-400">Interactive 3D plot simulation & farm conditions</p>
          </div>

          {/* Actual Authenticated Farm Profile details or Clean Empty State */}
          {farm ? (
            <div className="flex flex-wrap gap-2 text-xs">
              {farm.farm_name && (
                <div className="px-3 py-1.5 bg-slate-950/80 rounded-xl border border-slate-800 text-slate-300">
                  Farm: <strong className="text-white">{farm.farm_name}</strong>
                </div>
              )}
              <div className="px-3 py-1.5 bg-slate-950/80 rounded-xl border border-slate-800 text-slate-300">
                Land: <strong className="text-white">{farm.land_area} Acre</strong>
              </div>
              <div className="px-3 py-1.5 bg-slate-950/80 rounded-xl border border-slate-800 text-slate-300">
                Soil: <strong className="text-white">{farm.soil_type || 'Specified'}</strong>
              </div>
              <div className="px-3 py-1.5 bg-slate-950/80 rounded-xl border border-slate-800 text-slate-300">
                Water: <strong className="text-emerald-400 font-bold">{farm.water_availability || 'Available'}</strong>
              </div>
              <div className="px-3 py-1.5 bg-slate-950/80 rounded-xl border border-slate-800 text-slate-300">
                Location: <strong className="text-white">{farm.district}, {farm.state}</strong>
              </div>
            </div>
          ) : (
            <div className="p-3 bg-amber-950/40 border border-amber-500/30 rounded-2xl flex items-center justify-between gap-4 text-xs">
              <div>
                <strong className="text-amber-300 font-black block">Complete Farm Profile</strong>
                <span className="text-slate-400 text-[11px]">No farm profile recorded yet</span>
              </div>
              <Button
                variant="primary"
                size="sm"
                onClick={() => navigate('/analyze')}
                className="bg-amber-500 text-slate-950 font-black text-xs px-3 py-1.5"
              >
                + Complete Farm Profile
              </Button>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-center">
          <div className="lg:col-span-8 relative">
            <FarmPlot3D selectedCrop={selectedCrop} />
          </div>

          <div className="lg:col-span-4 bg-slate-950/80 backdrop-blur-xl p-5 rounded-2xl border border-slate-800 space-y-4">
            <div className="text-center space-y-2">
              <div className="text-xs font-extrabold text-slate-400 uppercase tracking-wider">Suitability Score</div>
              <div className="relative w-32 h-32 mx-auto flex items-center justify-center">
                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                  <path className="text-slate-800" strokeWidth="3.5" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                  <path className="text-emerald-400" strokeDasharray={`${metrics.score}, 100`} strokeWidth="3.5" strokeLinecap="round" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                </svg>
                <div className="absolute flex flex-col items-center">
                  <span className="text-3xl font-black text-white">{metrics.score}%</span>
                  <span className="text-[10px] font-extrabold text-emerald-400 uppercase">High Fit</span>
                </div>
              </div>
            </div>

            <div className="space-y-2.5 text-xs">
              <div>
                <div className="flex justify-between text-slate-300 font-bold mb-1">
                  <span>Farm Suitability</span>
                  <span className="text-emerald-400">{metrics.farmSuitability}%</span>
                </div>
                <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-emerald-400 rounded-full" style={{ width: `${metrics.farmSuitability}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-slate-300 font-bold mb-1">
                  <span>Water Fit</span>
                  <span className="text-emerald-400">{metrics.waterSuitability}%</span>
                </div>
                <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-400 rounded-full" style={{ width: `${metrics.waterSuitability}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-slate-300 font-bold mb-1">
                  <span>Economic Potential</span>
                  <span className="text-emerald-400">{metrics.economicPotential}%</span>
                </div>
                <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-amber-400 rounded-full" style={{ width: `${metrics.economicPotential}%` }} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* QUICK ACCESS ACTION TILES */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link to="/bidding" className="p-5 bg-slate-900/90 hover:bg-slate-800/90 rounded-2xl border border-slate-800 text-left transition-all flex flex-col justify-between space-y-3 group">
          <div className="p-3 bg-amber-950/60 rounded-xl border border-amber-500/30 w-fit text-amber-400 group-hover:scale-110 transition-transform">
            <IconStore size={22} />
          </div>
          <div>
            <h3 className="text-base font-black text-white group-hover:text-amber-400 transition-colors">
              Farmer Marketplace
            </h3>
            <p className="text-xs text-slate-400 mt-1">List planned crops, available stock &amp; view buyer offers.</p>
          </div>
        </Link>

        <Link to="/recommendation" className="p-5 bg-slate-900/90 hover:bg-slate-800/90 rounded-2xl border border-slate-800 text-left transition-all flex flex-col justify-between space-y-3 group">
          <div className="p-3 bg-emerald-950/60 rounded-xl border border-emerald-500/30 w-fit text-emerald-400 group-hover:scale-110 transition-transform">
            <IconUsers size={22} />
          </div>
          <div>
            <h3 className="text-base font-black text-white group-hover:text-emerald-400 transition-colors">
              Nearby Farmer Network
            </h3>
            <p className="text-xs text-slate-400 mt-1">50km &amp; 100km radius spatial discovery map of peer oilseed growers.</p>
          </div>
        </Link>

        <Link to="/profit" className="p-5 bg-slate-900/90 hover:bg-slate-800/90 rounded-2xl border border-slate-800 text-left transition-all flex flex-col justify-between space-y-3 group">
          <div className="p-3 bg-blue-950/60 rounded-xl border border-blue-500/30 w-fit text-blue-400 group-hover:scale-110 transition-transform">
            <IconCoins size={22} />
          </div>
          <div>
            <h3 className="text-base font-black text-white group-hover:text-blue-400 transition-colors">
              Profit Calculator
            </h3>
            <p className="text-xs text-slate-400 mt-1">Compare net margins between paddy and oilseed crops.</p>
          </div>
        </Link>

        <Link to="/market" className="p-5 bg-slate-900/90 hover:bg-slate-800/90 rounded-2xl border border-slate-800 text-left transition-all flex flex-col justify-between space-y-3 group">
          <div className="p-3 bg-purple-950/60 rounded-xl border border-purple-500/30 w-fit text-purple-400 group-hover:scale-110 transition-transform">
            <IconMapPin size={22} />
          </div>
          <div>
            <h3 className="text-base font-black text-white group-hover:text-purple-400 transition-colors">
              Mandi Prices &amp; Map
            </h3>
            <p className="text-xs text-slate-400 mt-1">Real-time APMC mandi prices and transport distance explorer.</p>
          </div>
        </Link>
      </div>

      <PlanCropModal
        isOpen={isPlanModalOpen}
        onClose={() => setIsPlanModalOpen(false)}
      />
    </div>
  );
}
