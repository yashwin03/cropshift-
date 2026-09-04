import React from 'react';
import Card from '../common/Card';
import StatusBadge from '../common/StatusBadge';
import type { ProfitabilityResponse } from '../../types/api';

/* ─── Helpers ─────────────────────────────────────────────────────────────── */

export function formatINR(amount: number): string {
  return '₹' + Math.abs(amount).toLocaleString('en-IN');
}

interface ProfitComparisonProps {
  data: ProfitabilityResponse;
  className?: string;
}

export default function ProfitComparison({ data, className = '' }: ProfitComparisonProps) {
  const { current_crop, recommended_crop, profit_difference } = data;

  const isPositive = profit_difference >= 0;
  const diffSign = isPositive ? '+' : '-';
  const diffBg = isPositive ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200';
  const diffTextColor = isPositive ? 'text-green-800' : 'text-red-800';

  const rows = [
    {
      label: 'Expected Yield',
      current: `${current_crop.expected_yield} ${current_crop.yield_unit}`,
      recommended: `${recommended_crop.expected_yield} ${recommended_crop.yield_unit}`,
      highlight: false,
    },
    {
      label: 'Production Cost',
      current: `${formatINR(current_crop.production_cost)} / acre`,
      recommended: `${formatINR(recommended_crop.production_cost)} / acre`,
      highlight: false,
    },
    {
      label: 'Expected Revenue',
      current: `${formatINR(current_crop.expected_revenue)} / acre`,
      recommended: `${formatINR(recommended_crop.expected_revenue)} / acre`,
      highlight: false,
    },
    {
      label: 'Estimated Net Profit',
      current: `${formatINR(current_crop.estimated_profit)} / acre`,
      recommended: `${formatINR(recommended_crop.estimated_profit)} / acre`,
      highlight: true,
    },
  ];

  return (
    <div className={`space-y-6 ${className}`}>
      {/* ── Highlighted Profit Difference Banner ── */}
      <div
        data-testid="profit-diff-banner"
        className={`p-5 rounded-2xl border flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 shadow-sm ${diffBg}`}
      >
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-gray-600 block mb-1">
            Estimated Profit Difference
          </span>
          <p className={`text-3xl font-extrabold ${diffTextColor}`}>
            {diffSign}{formatINR(profit_difference)}{' '}
            <span className="text-sm font-semibold text-gray-600">per acre</span>
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {isPositive
              ? `Shifting to ${recommended_crop.crop_name} could increase net profit by ${formatINR(profit_difference)} per acre.`
              : `Continuing ${current_crop.crop_name} yields ${formatINR(Math.abs(profit_difference))} more per acre than shifting.`}
          </p>
        </div>
        <div className="text-4xl self-end sm:self-center" aria-hidden="true">
          {isPositive ? '📈' : '📉'}
        </div>
      </div>

      {/* ── Two-column comparison grid on desktop, stacked on mobile ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Current Crop Card */}
        <Card className="border-gray-200 bg-white">
          <div className="flex items-center justify-between pb-3 border-b border-gray-100 mb-4">
            <div>
              <span className="text-xs font-bold text-gray-400 uppercase tracking-wider block">
                Current Crop
              </span>
              <h3 data-testid="current-crop-name" className="text-xl font-extrabold text-gray-900">
                {current_crop.crop_name}
              </h3>
            </div>
            <StatusBadge status={current_crop.data_status} />
          </div>

          <div className="space-y-3.5">
            <div>
              <span className="text-xs text-gray-500 font-medium">Expected Yield (Estimated)</span>
              <p className="text-sm font-bold text-gray-900">
                {current_crop.expected_yield} {current_crop.yield_unit}
              </p>
            </div>
            <div>
              <span className="text-xs text-gray-500 font-medium">Production Cost (Estimated)</span>
              <p className="text-sm font-bold text-gray-900">
                {formatINR(current_crop.production_cost)} <span className="text-xs font-normal text-gray-500">per acre</span>
              </p>
            </div>
            <div>
              <span className="text-xs text-gray-500 font-medium">Expected Revenue (Estimated)</span>
              <p className="text-sm font-bold text-gray-900">
                {formatINR(current_crop.expected_revenue)} <span className="text-xs font-normal text-gray-500">per acre</span>
              </p>
            </div>
            <div className="p-3 bg-gray-50 rounded-xl border border-gray-100">
              <span className="text-xs font-bold text-gray-600">Estimated Net Profit</span>
              <p className="text-lg font-extrabold text-gray-900">
                {formatINR(current_crop.estimated_profit)}{' '}
                <span className="text-xs font-semibold text-gray-500">per acre</span>
              </p>
            </div>
          </div>
        </Card>

        {/* Recommended Crop Card */}
        <Card className="border-primary-200 bg-primary-50/20 shadow-sm">
          <div className="flex items-center justify-between pb-3 border-b border-primary-100 mb-4">
            <div>
              <span className="text-xs font-bold text-primary-700 uppercase tracking-wider block">
                Recommended Crop
              </span>
              <h3 data-testid="recommended-crop-name" className="text-xl font-extrabold text-primary-900">
                {recommended_crop.crop_name}
              </h3>
            </div>
            <StatusBadge status={recommended_crop.data_status} />
          </div>

          <div className="space-y-3.5">
            <div>
              <span className="text-xs text-primary-700 font-medium">Expected Yield (Estimated)</span>
              <p className="text-sm font-bold text-gray-900">
                {recommended_crop.expected_yield} {recommended_crop.yield_unit}
              </p>
            </div>
            <div>
              <span className="text-xs text-primary-700 font-medium">Production Cost (Estimated)</span>
              <p className="text-sm font-bold text-gray-900">
                {formatINR(recommended_crop.production_cost)} <span className="text-xs font-normal text-gray-500">per acre</span>
              </p>
            </div>
            <div>
              <span className="text-xs text-primary-700 font-medium">Expected Revenue (Estimated)</span>
              <p className="text-sm font-bold text-gray-900">
                {formatINR(recommended_crop.expected_revenue)} <span className="text-xs font-normal text-gray-500">per acre</span>
              </p>
            </div>
            <div className="p-3 bg-green-100/70 rounded-xl border border-green-200">
              <span className="text-xs font-bold text-green-900">Estimated Net Profit</span>
              <p className="text-lg font-extrabold text-green-800">
                {formatINR(recommended_crop.estimated_profit)}{' '}
                <span className="text-xs font-semibold text-green-700">per acre</span>
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* ── Side-by-Side Detailed Breakdown Table ── */}
      <Card>
        <h4 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-3">
          Detailed Financial Comparison (per acre)
        </h4>

        {/* ── Mobile: stacked label-value rows (visible below md) ── */}
        <div data-testid="comparison-table-mobile" className="block md:hidden space-y-4">
          {rows.map((r, idx) => (
            <div
              key={idx}
              className={`rounded-xl border p-3 space-y-2 ${r.highlight ? 'bg-green-50/60 border-green-200' : 'bg-gray-50 border-gray-100'}`}
            >
              <p className={`text-xs font-bold uppercase tracking-wider ${r.highlight ? 'text-green-900' : 'text-gray-500'}`}>
                {r.label}
              </p>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <span className="block text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-0.5">
                    {current_crop.crop_name}
                  </span>
                  <span className={`font-bold ${r.highlight ? 'text-gray-900' : 'text-gray-800'}`}>
                    {r.current}
                  </span>
                </div>
                <div>
                  <span className="block text-[10px] font-semibold text-primary-700 uppercase tracking-wider mb-0.5">
                    {recommended_crop.crop_name}
                  </span>
                  <span className={`font-bold ${r.highlight ? 'text-green-800' : 'text-gray-800'}`}>
                    {r.recommended}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* ── Desktop: horizontal table (visible md+) ── */}
        <div data-testid="comparison-table-desktop" className="hidden md:block overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-gray-200 text-xs font-bold text-gray-500 uppercase">
                <th className="py-2.5 px-3">Metric (Estimated)</th>
                <th className="py-2.5 px-3">{current_crop.crop_name}</th>
                <th className="py-2.5 px-3 text-primary-800">{recommended_crop.crop_name}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {rows.map((r, idx) => (
                <tr key={idx} className={r.highlight ? 'bg-green-50/50 font-bold' : ''}>
                  <td className="py-2.5 px-3 text-gray-700 font-medium">{r.label}</td>
                  <td className="py-2.5 px-3 text-gray-900">{r.current}</td>
                  <td className={`py-2.5 px-3 ${r.highlight ? 'text-green-800 font-bold' : 'text-gray-900'}`}>
                    {r.recommended}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* ── Persistent Estimation Disclaimer (Required) ── */}
      <div
        data-testid="profitability-disclaimer"
        className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900 flex items-start gap-2.5"
      >
        <span className="text-base flex-shrink-0" aria-hidden="true">⚠️</span>
        <p className="leading-relaxed">
          <strong>Notice:</strong> These are estimates based on regional data. Actual results depend on weather, prices, and farming practices. Figures are indicative and not guaranteed.
        </p>
      </div>
    </div>
  );
}
