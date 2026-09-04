import React from 'react';
import type { Decision } from '../../types/api';

/* ─── Label + style map ───────────────────────────────────────────────────── */

const DECISION_MAP: Record<
  Decision,
  { label: string; icon: string; className: string }
> = {
  SWITCH: {
    label: 'Good to Switch',
    icon: '✅',
    className:
      'bg-green-100 text-green-800 border border-green-300',
  },
  CAUTION: {
    label: 'Proceed with Caution',
    icon: '⚠️',
    className:
      'bg-amber-100 text-amber-800 border border-amber-300',
  },
  DONT_SWITCH: {
    label: 'Stay with Current Crop',
    icon: '🚫',
    className:
      'bg-red-100 text-red-800 border border-red-300',
  },
};

/* ─── Props ───────────────────────────────────────────────────────────────── */

interface DecisionBadgeProps {
  decision: Decision;
  /** 'sm' = compact pill (default), 'lg' = large prominent badge */
  size?: 'sm' | 'lg';
  className?: string;
}

/* ─── Component ───────────────────────────────────────────────────────────── */

export default function DecisionBadge({
  decision,
  size = 'sm',
  className = '',
}: DecisionBadgeProps) {
  const { label, icon, className: variantClass } = DECISION_MAP[decision];

  const sizeClass =
    size === 'lg'
      ? 'px-5 py-2.5 text-base font-extrabold rounded-xl gap-2'
      : 'px-3 py-1 text-sm font-semibold rounded-full gap-1.5';

  return (
    <span
      data-decision={decision}
      className={`inline-flex items-center ${sizeClass} ${variantClass} ${className}`}
    >
      <span aria-hidden="true">{icon}</span>
      {label}
    </span>
  );
}
