import React from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import EmptyState from '../components/common/EmptyState';
import DecisionBadge from '../components/score/DecisionBadge';
import SafetyScoreGauge from '../components/score/SafetyScoreGauge';
import ScoreBreakdown from '../components/score/ScoreBreakdown';
import PeerProofCard from '../components/recommendation/PeerProofCard';
import PlanCropModal from '../components/farmer/PlanCropModal';
import AddCropModal from '../components/farmer/AddCropModal';
import { getRecommendation, getFarmDetails } from '../utils/storage';
import type { TopOilseedItem } from '../types/api';
import FarmPlot3D from '../components/3d/FarmPlot3D';
import {
  IconPlant,
  IconChartBar,
  IconStore,
  IconMapPin,
  IconFileText,
  IconShield,
  IconTrophy,
  IconCheck,
  IconAlertCircle,
  IconArrowRight,
  IconTrendingUp,
  IconSparkles,
  IconPlus,
} from '../components/common/Icons';

function formatINR(amount: number): string {
  return '₹' + Math.abs(amount).toLocaleString('en-IN');
}

function ComponentProgressBar({ label, score, colorClass = 'bg-emerald-500' }: { label: string; score: number; colorClass?: string }) {
  const safeScore = Math.max(0, Math.min(100, Math.round(score)));
  return (
    <div className="space-y-1">
      <div className="flex justify-between items-center text-xs font-bold">
        <span className="text-slate-300">{label}</span>
        <span className="text-white">{safeScore}%</span>
      </div>
      <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
        <div
          className={`h-full ${colorClass} transition-all duration-500 rounded-full`}
          style={{ width: `${safeScore}%` }}
        />
      </div>
    </div>
  );
}

function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="text-xs font-black uppercase text-slate-400 tracking-wider flex items-center gap-1.5 mb-2">
      {children}
    </h3>
  );
}

function CheckItem({ text }: { text: string }) {
  return (
    <li className="flex items-start gap-2 text-xs text-slate-300 py-1">
      <span className="text-emerald-400 font-bold mt-0.5">&bull;</span>
      <span>{text}</span>
    </li>
  );
}

function WarnItem({ text }: { text: string }) {
  return (
    <li className="flex items-start gap-2 py-2 border-b border-slate-800/80 last:border-0 text-xs">
      <span className="flex-shrink-0 text-amber-400 mt-0.5">
        <IconAlertCircle size={14} />
      </span>
      <span className="text-slate-200 font-medium leading-relaxed">{text}</span>
    </li>
  );
}

const NEXT_STEPS = [
  { path: '/profit', icon: <IconChartBar size={20} className="text-emerald-400" />, label: 'Compare Money Earned & Profit', desc: 'Detailed profit calculator & break-even analysis' },
  { path: '/market', icon: <IconStore size={20} className="text-blue-400" />, label: 'Prices & Market Access', desc: 'APMC market prices, trends & buyer demand' },
  { path: '/map', icon: <IconMapPin size={20} className="text-amber-400" />, label: 'Nearby Markets & Distance', desc: 'Interactive mandi location map with transport costs' },
  { path: '/subsidies', icon: <IconFileText size={20} className="text-purple-400" />, label: 'Schemes You May Qualify For', desc: 'Government oilseed subsidy scheme matcher' },
  { path: '/risk', icon: <IconShield size={20} className="text-rose-400" />, label: 'What-If Scenarios & Risk', desc: 'Drought, price drop & pest risk simulation' },
];

export default function RecommendationPage() {
  const navigate = useNavigate();
  const recommendation = getRecommendation();
  const farm = getFarmDetails();
  const [isPlanModalOpen, setIsPlanModalOpen] = React.useState(false);
  const [isAddCropModalOpen, setIsAddCropModalOpen] = React.useState(false);

  if (!recommendation) {
    return (
      <div className="max-w-xl mx-auto py-8">
        <EmptyState
          title="No Recommendation Yet"
          message="Please complete the farm information form to get your crop shift recommendation."
          actionLabel="Start Analysis"
          onAction={() => navigate('/analyze')}
        />
      </div>
    );
  }

  const {
    recommended_crop = 'Groundnut',
    safety_score,
    decision = 'CONSIDER_SHIFT',
    profit_difference = 0,
    reasons = [],
    risks = [],
    farm_suitability_score,
    water_suitability_score,
    economic_potential_score,
    overall_score,
    top_oilseeds,
  } = recommendation;

  const farmSuitability = farm_suitability_score ?? recommendation.suitability_score ?? 85;
  const waterSuitability = water_suitability_score ?? recommendation.suitability_score ?? 80;
  const economicPotential = economic_potential_score ?? recommendation.profitability_score ?? 82;
  const overall = overall_score ?? safety_score ?? 84;

  const profitSign = profit_difference > 0 ? '+' : profit_difference < 0 ? '-' : '';
  const profitColorClass = profit_difference > 0 ? 'text-emerald-400 text-green-400' : profit_difference < 0 ? 'text-rose-400 text-red-400' : 'text-slate-300';
  const profitBgClass = profit_difference > 0 ? 'bg-emerald-950/40 border-emerald-500/30 bg-green-950/40 border-green-500/30' : profit_difference < 0 ? 'bg-rose-950/40 border-rose-500/30 bg-red-950/40 border-red-500/30' : 'bg-slate-950/40 border-slate-800';

  const cropIdMap: Record<string, number> = {
    'Groundnut': 2,
    'Sunflower': 3,
    'Soybean': 4,
    'Mustard': 5,
    'Sesame': 6,
    'Safflower': 8,
    'Niger': 9,
    'Castor': 10,
    'Linseed': 11,
    'Sesame (Black)': 12,
  };
  const bestCropId = cropIdMap[recommended_crop] ?? 2;

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12">
      {/* Header */}
      <div className="bg-slate-900/90 backdrop-blur-2xl p-5 rounded-3xl border border-slate-800 shadow-2xl flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <div>
          <div className="inline-flex items-center gap-2 bg-emerald-950 text-emerald-400 text-[10px] font-extrabold px-3 py-1 rounded-full border border-emerald-500/30 mb-1">
            <IconPlant size={12} className="text-emerald-400" />
            <span>Oilseed Recommendation Engine</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight leading-tight">
            Crop Simulator Analysis
          </h1>
          {farm && (
            <p className="text-xs text-slate-400 mt-0.5 flex items-center gap-1.5">
              <IconMapPin size={12} className="text-slate-400" />
              <span>Evaluated for {farm.land_area} acre{farm.land_area !== 1 ? 's' : ''} of {farm.current_crop} in {farm.district}, {farm.state}</span>
            </p>
          )}
        </div>

        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => window.print()} className="bg-slate-950 text-slate-300 border-slate-800 text-xs">
            Export PDF
          </Button>
          <Button variant="outline" size="sm" onClick={() => navigate('/analyze')} className="bg-slate-950 text-slate-300 border-slate-800 text-xs">
            Modify Inputs
          </Button>
        </div>
      </div>

      {/* 🥇 1. BEST MATCH HERO CARD */}
      <div className="bg-slate-900/90 backdrop-blur-2xl border-2 border-emerald-500/50 shadow-2xl rounded-3xl p-6 space-y-5">
        <div className="flex justify-between items-start flex-wrap gap-2">
          <div className="inline-flex items-center gap-1.5 bg-emerald-500 text-slate-950 text-xs font-black px-3.5 py-1 rounded-full shadow-lg shadow-emerald-500/20">
            <IconTrophy size={14} className="text-slate-950" />
            <span>#1 BEST MATCH</span>
          </div>
          <DecisionBadge decision={decision} size="md" />
        </div>

        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div>
            <span className="text-[11px] font-extrabold text-slate-400 uppercase tracking-wider block">Recommended Oilseed</span>
            <h2 data-testid="recommended-crop" className="text-3xl sm:text-4xl font-black text-white tracking-tight mt-0.5">
              {recommended_crop}
            </h2>
          </div>
          <button
            type="button"
            onClick={() => setIsAddCropModalOpen(true)}
            className="px-4 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-xs rounded-xl shadow-lg flex items-center gap-2 cursor-pointer transition-all hover:scale-105"
          >
            <IconPlus size={16} />
            <span>+ Add to My Crops</span>
          </button>
        </div>


        {/* Safety Score Gauge container for testid */}
        <div data-testid="safety-score" className="flex flex-col items-center text-center">
          <SafetyScoreGauge score={overall} size={140} />
        </div>

        {/* 3 Component Scores + Overall */}
        <div className="bg-slate-950 p-4 rounded-2xl border border-slate-800 space-y-3">
          <h3 className="text-xs font-black text-slate-300 uppercase tracking-wider">Suitability & Economic Component Scores</h3>
          
          <ComponentProgressBar label="Farm Suitability" score={farmSuitability} colorClass="bg-emerald-500" />
          <ComponentProgressBar label="Water / Resource Suitability" score={waterSuitability} colorClass="bg-blue-500" />
          <ComponentProgressBar label="Economic Potential" score={economicPotential} colorClass="bg-amber-500" />
          
          <div className="pt-2 border-t border-slate-800 flex justify-between items-center">
            <span className="text-xs font-extrabold text-white uppercase">Overall Safety Score</span>
            <div className="text-xl font-black text-emerald-400">
              {overall}%
            </div>
          </div>
        </div>

        {/* Estimated Profit Difference Banner */}
        <div data-testid="profit-difference" className={`flex items-center justify-between rounded-2xl border p-4 ${profitBgClass}`}>
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Estimated Net Gain Per Acre</span>
            <span className={`text-xl font-black ${profitColorClass}`}>
              {profitSign}{formatINR(profit_difference)} / acre
            </span>
          </div>
          <IconTrendingUp size={28} className={profit_difference >= 0 ? 'text-emerald-400' : 'text-red-400'} />
        </div>

        {/* Why this is #1 Explainability */}
        {reasons.length > 0 && (
          <div className="space-y-2 pt-2">
            <SectionHeading>
              <IconCheck size={14} className="text-emerald-400" />
              <span>Why This Recommendation?</span>
            </SectionHeading>
            <ul className="bg-slate-950 p-4 rounded-2xl border border-slate-800 space-y-1">
              {reasons.map((reason, i) => (
                <CheckItem key={i} text={reason} />
              ))}
            </ul>
          </div>
        )}

        {/* Risks */}
        {risks.length > 0 && (
          <div className="space-y-2">
            <SectionHeading>
              <IconAlertCircle size={14} className="text-amber-400" />
              <span>Risks to Be Aware Of</span>
            </SectionHeading>
            <ul className="bg-slate-950 p-4 rounded-2xl border border-amber-500/30 space-y-1">
              {risks.map((risk, i) => (
                <WarnItem key={i} text={risk} />
              ))}
            </ul>
          </div>
        )}

        {/* CTA to Marketplace */}
        <div className="pt-3 border-t border-slate-800 flex flex-col sm:flex-row justify-between items-center gap-3">
          <p className="text-xs text-slate-300">
            Ready to list {recommended_crop} or view buyer procurement offers?
          </p>
          <div className="flex gap-2 w-full sm:w-auto">
            <Button
              variant="primary"
              size="md"
              onClick={() => setIsPlanModalOpen(true)}
              className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-black text-xs py-2.5 px-4 flex items-center justify-center gap-2 cursor-pointer"
            >
              <IconStore size={14} />
              <span>+ Add Crop to Marketplace</span>
            </Button>
            <Button
              variant="outline"
              size="md"
              onClick={() => navigate('/bidding')}
              className="bg-slate-950 text-slate-300 border-slate-800 text-xs py-2.5 px-4 flex items-center justify-center gap-2"
            >
              <span>Explore Opportunities</span>
            </Button>
          </div>
        </div>
      </div>

      {/* 2. SCORE BREAKDOWN COMPONENT */}
      <ScoreBreakdown
        suitabilityScore={recommendation.suitability_score}
        profitabilityScore={recommendation.profitability_score}
        marketScore={recommendation.market_score}
        riskScore={recommendation.risk_score}
      />

      {/* 3. 3D FARM PLOT SIMULATOR IN RECOMMENDATION */}
      <div className="bg-slate-900/90 backdrop-blur-2xl p-5 rounded-3xl border border-slate-800 shadow-2xl space-y-4">
        <div className="text-xs font-black uppercase text-emerald-400 flex items-center gap-2">
          <IconSparkles size={14} className="text-emerald-400" />
          <span>3D Interactive Field Simulation ({recommended_crop})</span>
        </div>
        <FarmPlot3D selectedCrop={recommended_crop} />
      </div>

      {/* 4. 👥 NEARBY FARMERS GROWING THIS CROP (PEER NETWORK MAP & CARDS) */}
      <div className="space-y-2">
        <PeerProofCard
          cropId={bestCropId}
          cropName={recommended_crop}
          farmId={farm?.farm_id}
          district={farm?.district}
          latitude={farm?.latitude}
          longitude={farm?.longitude}
        />
      </div>

      {/* 4. 🌻 TOP 10 OILSEED CANDIDATE RANKINGS */}
      {top_oilseeds && top_oilseeds.length > 0 && (
        <div className="space-y-3">
          <SectionHeading>
            <IconTrophy size={14} className="text-amber-400" />
            <span>Other Suitable Oilseed Candidates (Top 10)</span>
          </SectionHeading>
          <div className="space-y-3">
            {top_oilseeds.map((item: TopOilseedItem) => (
              <div key={item.crop_id} className={`p-4 rounded-2xl backdrop-blur-2xl transition-all ${item.rank === 1 ? 'border-2 border-emerald-500 bg-slate-900/90' : 'border border-slate-800 bg-slate-900/80'}`}>
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                  <div className="flex items-center gap-3">
                    <span className="w-7 h-7 rounded-full bg-slate-950 text-white text-xs font-black flex items-center justify-center border border-slate-800">
                      #{item.rank}
                    </span>
                    <div>
                      <h4 className="text-base font-black text-white leading-tight">{item.crop_name}</h4>
                      <span className="text-xs text-slate-400 font-semibold">
                        Gain: {item.profit_difference >= 0 ? '+' : ''}{formatINR(item.profit_difference)} / acre
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 self-end sm:self-auto">
                    <DecisionBadge decision={item.decision} size="sm" />
                    <span className="text-sm font-black text-emerald-400 bg-emerald-950 px-2.5 py-1 rounded-xl border border-emerald-500/30">
                      {item.overall_score}%
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-slate-800 text-center text-xs">
                  <div className="bg-slate-950 p-2 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-400 block">Farm Suitability</span>
                    <span className="font-bold text-white">{item.farm_suitability_score}%</span>
                  </div>
                  <div className="bg-slate-950 p-2 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-400 block">Water Fit</span>
                    <span className="font-bold text-white">{item.water_suitability_score}%</span>
                  </div>
                  <div className="bg-slate-950 p-2 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-400 block">Economics</span>
                    <span className="font-bold text-white">{item.economic_potential_score}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ONWARD NAVIGATION BUTTONS */}
      <div className="space-y-3 pt-4 border-t border-slate-800">
        <SectionHeading>
          <IconArrowRight size={14} className="text-emerald-400" />
          <span>Explore Detailed Deep Dives</span>
        </SectionHeading>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {NEXT_STEPS.map((step) => (
            <button
              key={step.path}
              type="button"
              onClick={() => navigate(step.path)}
              className="p-4 bg-slate-900/90 hover:bg-slate-800/90 rounded-2xl border border-slate-800 text-left transition-all flex items-start gap-3 group"
            >
              <div className="p-2.5 bg-slate-950 rounded-xl border border-slate-800 group-hover:scale-110 transition-transform">
                {step.icon}
              </div>
              <div>
                <h4 className="text-sm font-bold text-white group-hover:text-emerald-400 transition-colors">
                  {step.label}
                </h4>
                <p className="text-xs text-slate-400 mt-0.5">{step.desc}</p>
              </div>
            </button>
          ))}
        </div>
      </div>

      <PlanCropModal
        isOpen={isPlanModalOpen}
        onClose={() => setIsPlanModalOpen(false)}
      />
      <AddCropModal
        isOpen={isAddCropModalOpen}
        onClose={() => setIsAddCropModalOpen(false)}
        initialCropName={recommended_crop}
        initialStage="GROWING"
        initialYield={24.5}
      />
    </div>
  );
}

