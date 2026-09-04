import React from 'react';
import type { DataStatus } from '../../types/api';
import { getDataStatusLabel } from '../../utils/labels';
import Badge from './Badge';

interface StatusBadgeProps {
  status: DataStatus;
  className?: string;
}

export default function StatusBadge({ status, className = '' }: StatusBadgeProps) {
  const getBadgeVariant = (s: DataStatus) => {
    switch (s) {
      case 'REAL':
        return 'success';
      case 'STATIC':
        return 'neutral';
      case 'DEMO':
        return 'warning';
      case 'ESTIMATED':
        return 'warning';
      default:
        return 'neutral';
    }
  };

  return (
    <Badge variant={getBadgeVariant(status)} className={className}>
      {getDataStatusLabel(status)}
    </Badge>
  );
}
