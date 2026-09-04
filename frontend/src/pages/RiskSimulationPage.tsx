import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../components/common/Card';
import Spinner from '../components/common/Spinner';
import ErrorState from '../components/common/ErrorState';
import EmptyState from '../components/common/EmptyState';
import DecisionBadge from '../components/score/DecisionBadge';
import { getFarmDetails, getRecommendation } from '../utils/storage';
import { runRiskSimulation } from '../services/api';
import type { RiskSimulationResponse, Decision } from '../types/api';

// Config labels for Scenarios
const SCENARIOS = [
  { key: 'baseline' as const, title: 'Normal Conditions', desc: 'Typical weather, yield, and market prices as forecasted.' },
  { key: 'price_down' as const, title: 'If Prices Fall', desc: 'Market price drop of 20% due to local surplus or high supply.' },
  { key: 'yield_down' as const, title: 'If Yield Drops', desc: 'Crop yield reduction of 15% from late monsoon or soil issues.' },
  { key: 'water_risk' as const, title: 'If Water Becomes Scarce', desc: 'Severe water deficit limiting irrigation capabilities.' },
];

import { useApiState } from '../hooks/useApiState';

export default function RiskSimulationPage() {
  const navigate = useNavigate();
  const farm = getFarmDetails();
  const recommendation = getRecommendation();
  const apiState = useApiState<RiskSimulationResponse>();
  const [priceVariance, setPriceVariance] = useState(0.8);
  const [yieldVariance, setYieldVariance] = useState(0.7);

  const fetchRiskSimulation = async () => {
    if (!farm || !recommendation) return;
    // Endpoint requires farm_id and crop_id (the recommended crop index/mapping)
    await apiState.run(runRiskSimulation(farm.farm_id, 2, priceVariance, yieldVariance));
  };

  useEffect(() => {
    fetchRiskSimulation();
  }, [priceVariance, yieldVariance]);

  const loading = apiState.loading;
  const error = apiState.error;
  const data = apiState.data;

  if (!farm || !recommendation) {
    return (
      <div className="max-w-4xl mx-auto py-8 px-4">
        <EmptyState
          title="No Active Recommendation"
          message="Risk simulation requires active farm details and a crop recommendation. Please go back and complete your profile."
          actionLabel="Complete Profile"
          onAction={() => window.location.assign('/analyze')}
        />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[350px]">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-4xl mx-auto py-8">
        <ErrorState
          title="Simulation Failed"
          message={error || 'Could not simulate risk scenarios.'}
          onRetry={fetchRiskSimulation}
        />
      </div>
    );
  }

  const baselineDecision = data.baseline.decision;

  // Visual helper functions
  const getSafetyScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-700 bg-green-50 border-green-200';
    if (score >= 60) return 'text-amber-700 bg-amber-50 border-amber-200';
    return 'text-red-700 bg-red-50 border-red-200';
  };

  const getProgressColor = (score: number) => {
    if (score >= 80) return 'bg-green-600';
    if (score >= 60) return 'bg-amber-500';
    return 'bg-red-500';
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-gray-900 leading-tight">
          Risk Simulation
        </h1>
        <p className="text-gray-600 mt-1">
          Explore how alternative scenarios impact your recommended shift to <span className="font-semibold text-primary">{recommendation.recommended_crop}</span>.
        </p>
      </div>

      <Card className="p-6 bg-white border border-gray-200">
        <h2 className="text-xl font-bold mb-4">Adjust Variance Scenarios</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Price Variance: {Math.round((priceVariance - 1) * 100)}%
            </label>
            <input
              type="range"
              min="0.5"
              max="1.5"
              step="0.05"
              value={priceVariance}
              onChange={(e) => setPriceVariance(parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Yield Variance: {Math.round((yieldVariance - 1) * 100)}%
            </label>
            <input
              type="range"
              min="0.5"
              max="1.5"
              step="0.05"
              value={yieldVariance}
              onChange={(e) => setYieldVariance(parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
          </div>
        </div>
      </Card>

      {/* Responsive Scenario Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {SCENARIOS.map(sc => {
          const result = data[sc.key];
          const hasDecisionChanged = result.decision !== baselineDecision;

          return (
            <Card
              key={sc.key}
              data-testid={`scenario-card-${sc.key}`}
              className={`transition-all duration-300 relative overflow-hidden border ${
                hasDecisionChanged && sc.key !== 'baseline'
                  ? 'border-red-300 shadow-md ring-2 ring-red-100'
                  : 'border-gray-200 hover:shadow-md'
              }`}
            >
              {/* Alert Badge for changed decision */}
              {hasDecisionChanged && sc.key !== 'baseline' && (
                <div 
                  data-testid="decision-changed-alert"
                  className="absolute top-0 right-0 bg-red-600 text-white text-[10px] uppercase font-bold tracking-widest px-3 py-1 rounded-bl-xl shadow-sm z-10"
                >
                  Decision Changed
                </div>
              )}

              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-bold text-gray-900">{sc.title}</h3>
                  <p className="text-xs text-gray-500 mt-0.5">{sc.desc}</p>
                </div>

                <div className="flex items-center justify-between gap-4 p-3 bg-gray-50 rounded-xl border border-gray-100">
                  <div className="space-y-1">
                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block">
                      Safety Score
                    </span>
                    <span
                      data-testid={`safety-score-${sc.key}`}
                      className={`text-lg font-extrabold px-2.5 py-0.5 rounded-full border ${getSafetyScoreColor(
                        result.safety_score
                      )}`}
                    >
                      {result.safety_score}
                    </span>
                  </div>

                  <div className="space-y-1 text-right">
                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block">
                      Recommendation
                    </span>
                    <DecisionBadge size="sm" decision={result.decision} />
                  </div>
                </div>

                {/* Progress bar visual */}
                <div className="w-full bg-gray-100 h-1.5 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full ${getProgressColor(result.safety_score)}`} 
                    style={{ width: `${result.safety_score}%` }} 
                  />
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Safety Score Comparison Bar Chart */}
      <Card className="p-6 bg-white border border-gray-200" headerTag="h2" title="Safety Score Scenario Comparison">
        <div className="space-y-4">
          {SCENARIOS.map(sc => {
            const result = data[sc.key];
            const isBaseline = sc.key === 'baseline';
            
            return (
              <div key={sc.key} className="space-y-1">
                <div className="flex justify-between text-sm font-semibold text-gray-700">
                  <span>{sc.title}</span>
                  <span>{result.safety_score}</span>
                </div>
                <div className="w-full bg-gray-100 h-6 rounded-lg overflow-hidden border border-gray-200">
                  <div 
                    data-testid={`bar-${sc.key}`}
                    className={`h-full rounded-lg transition-all duration-500 flex items-center pl-3 text-xs font-bold text-white ${
                      isBaseline ? 'bg-primary-600' : 'bg-slate-500'
                    }`}
                    style={{ width: `${result.safety_score}%` }}
                  >
                    {result.safety_score >= 15 && `${result.safety_score}%`}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
}
