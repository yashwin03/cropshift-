import React, { useState } from 'react';
import Card from '../common/Card';

interface ScoreItemConfig {
  key: string;
  name: string;
  score: number;
  weightLabel: string;
  description: string;
  colorClass: string;
  bgClass: string;
}

interface ScoreBreakdownProps {
  suitabilityScore: number;
  profitabilityScore: number;
  marketScore: number;
  riskScore: number;
  className?: string;
}

export default function ScoreBreakdown({
  suitabilityScore,
  profitabilityScore,
  marketScore,
  riskScore,
  className = '',
}: ScoreBreakdownProps) {
  const [isFormulaOpen, setIsFormulaOpen] = useState(false);

  const getBarColor = (score: number) => {
    if (score >= 80) return 'bg-green-600';
    if (score >= 60) return 'bg-amber-500';
    return 'bg-red-500';
  };

  const getScoreBadge = (score: number) => {
    if (score >= 80) return 'bg-green-50 text-green-800 border-green-200';
    if (score >= 60) return 'bg-amber-50 text-amber-800 border-amber-200';
    return 'bg-red-50 text-red-800 border-red-200';
  };

  const scoreItems: ScoreItemConfig[] = [
    {
      key: 'suitability',
      name: 'Suitability',
      score: suitabilityScore,
      weightLabel: '35% of score',
      description: 'How well this crop fits your land, soil type, and water availability',
      colorClass: getBarColor(suitabilityScore),
      bgClass: getScoreBadge(suitabilityScore),
    },
    {
      key: 'profitability',
      name: 'Profitability',
      score: profitabilityScore,
      weightLabel: '30% of score',
      description: 'How much more or less profit you could earn compared to your current crop',
      colorClass: getBarColor(profitabilityScore),
      bgClass: getScoreBadge(profitabilityScore),
    },
    {
      key: 'market',
      name: 'Market',
      score: marketScore,
      weightLabel: '20% of score',
      description: 'How good current local market prices and buyer access are in your district',
      colorClass: getBarColor(marketScore),
      bgClass: getScoreBadge(marketScore),
    },
    {
      key: 'risk',
      name: 'Risk',
      score: riskScore,
      weightLabel: '15% of score',
      description: 'How much could go wrong (price fluctuation, drought vulnerability, and pests)',
      colorClass: getBarColor(riskScore),
      bgClass: getScoreBadge(riskScore),
    },
  ];

  return (
    <Card className={className}>
      <div className="mb-4">
        <h2 className="text-base font-extrabold text-gray-900 uppercase tracking-wide">
          Score Breakdown & Factors
        </h2>
        <p className="text-xs text-gray-500 mt-0.5">
          The overall Safety Score combines 4 essential agricultural and financial factors.
        </p>
      </div>

      {/* 4 Factor Bars */}
      <div className="space-y-4">
        {scoreItems.map(item => (
          <div key={item.key} data-testid={`score-item-${item.key}`} className="space-y-1.5">
            {/* Header: Name, Weight, Score */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-bold text-gray-900 text-sm">{item.name}</span>
                <span className="text-xs text-gray-400 font-medium px-2 py-0.5 bg-gray-100 rounded">
                  {item.weightLabel}
                </span>
              </div>
              <span
                data-testid={`score-value-${item.key}`}
                className={`text-xs font-bold px-2 py-0.5 rounded border ${item.bgClass}`}
              >
                {item.score} / 100
              </span>
            </div>

            {/* Visual Bar */}
            <div className="w-full bg-gray-100 rounded-full h-2.5 overflow-hidden">
              <div
                className={`h-2.5 rounded-full transition-all duration-500 ease-out ${item.colorClass}`}
                style={{ width: `${Math.max(0, Math.min(100, item.score))}%` }}
                role="progressbar"
                aria-valuenow={item.score}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-label={`${item.name} score: ${item.score} out of 100`}
              />
            </div>

            {/* Plain-Language Explanation */}
            <p className="text-xs text-gray-500 leading-snug">{item.description}</p>
          </div>
        ))}
      </div>

      {/* "How is this calculated?" Expandable Accordion Panel */}
      <div className="mt-6 pt-4 border-t border-gray-100">
        <button
          type="button"
          onClick={() => setIsFormulaOpen(prev => !prev)}
          className="flex items-center justify-between w-full text-left text-xs font-bold text-primary hover:text-primary-700 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded px-1 transition-colors"
          aria-expanded={isFormulaOpen}
          data-testid="toggle-calculation-details"
        >
          <span className="flex items-center gap-1.5">
            <span aria-hidden="true">ℹ️</span> How is this Safety Score calculated?
          </span>
          <svg
            className={`w-4 h-4 transform transition-transform duration-200 ${
              isFormulaOpen ? 'rotate-180 text-primary-700' : 'text-gray-400'
            }`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {isFormulaOpen && (
          <div
            data-testid="calculation-details-panel"
            className="mt-3 p-3.5 bg-gray-50 rounded-lg text-xs text-gray-700 space-y-2 border border-gray-200"
          >
            <p className="font-semibold text-gray-900">
              Formula Breakdown (Standard Decision Weights):
            </p>
            <ul className="list-disc list-inside space-y-1 text-gray-600 pl-1">
              <li>
                <strong>Suitability (35%):</strong> Evaluates soil chemistry, seasonal water access, and agro-climatic zone fit.
              </li>
              <li>
                <strong>Profitability (30%):</strong> Assesses estimated net margin, input costs, and yield estimates.
              </li>
              <li>
                <strong>Market (20%):</strong> Evaluates mandi prices within 50km, transportation access, and seasonal demand.
              </li>
              <li>
                <strong>Risk (15%):</strong> Considers historical price volatility, climate stress tolerance, and pest resistance.
              </li>
            </ul>
            <p className="text-[11px] text-gray-500 pt-1 italic">
              All scoring weights and composite evaluations are computed by the CropShift decision engine.
            </p>
          </div>
        )}
      </div>
    </Card>
  );
}
