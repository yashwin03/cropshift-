import React from 'react';
import type { Trend } from '../../types/api';
import { getTrendLabel } from '../../utils/labels';

interface TrendIndicatorProps {
  trend: Trend;
  className?: string;
}

export default function TrendIndicator({ trend, className = '' }: TrendIndicatorProps) {
  const label = getTrendLabel(trend);

  let icon = '➡️';
  let colorClass = 'text-gray-600 bg-gray-50 border-gray-200';

  if (trend === 'RISING') {
    icon = '📈';
    colorClass = 'text-green-700 bg-green-50 border-green-200';
  } else if (trend === 'FALLING') {
    icon = '📉';
    colorClass = 'text-red-700 bg-red-50 border-red-200';
  } else if (trend === 'STABLE') {
    icon = '➡️';
    colorClass = 'text-blue-700 bg-blue-50 border-blue-200';
  }

  return (
    <span
      data-testid={`trend-indicator-${trend.toLowerCase()}`}
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${colorClass} ${className}`}
    >
      <span aria-hidden="true">{icon}</span>
      <span>{label}</span>
    </span>
  );
}
