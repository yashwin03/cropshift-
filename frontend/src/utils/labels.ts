import type { 
  Decision, 
  Trend, 
  DataStatus, 
  Relevance, 
  EligibilityStatus 
} from '../types/api';

export const DECISION_LABELS: Record<Decision, string> = {
  SWITCH: 'Good to Switch',
  CAUTION: 'Switch with Caution',
  DONT_SWITCH: 'Better to Continue'
};

export const TREND_LABELS: Record<Trend, string> = {
  RISING: 'Prices Rising',
  STABLE: 'Prices Steady',
  FALLING: 'Prices Falling'
};

export const DATA_STATUS_LABELS: Record<DataStatus, string> = {
  REAL: 'Live Data',
  STATIC: 'Reference Data',
  DEMO: 'Demo Data',
  ESTIMATED: 'Estimated'
};

export const RELEVANCE_LABELS: Record<Relevance, string> = {
  HIGH: 'High Relevance',
  MEDIUM: 'Medium Relevance',
  LOW: 'Low Relevance'
};

export const ELIGIBILITY_LABELS: Record<EligibilityStatus, string> = {
  LIKELY_ELIGIBLE: 'You may qualify — please verify',
  VERIFICATION_REQUIRED: 'Verification required',
  LIKELY_NOT_ELIGIBLE: 'Likely not applicable'
};

export const getDecisionLabel = (decision: Decision): string => DECISION_LABELS[decision] || decision;
export const getTrendLabel = (trend: Trend): string => TREND_LABELS[trend] || trend;
export const getDataStatusLabel = (status: DataStatus): string => DATA_STATUS_LABELS[status] || status;
export const getRelevanceLabel = (relevance: Relevance): string => RELEVANCE_LABELS[relevance] || relevance;
export const getEligibilityLabel = (status: EligibilityStatus): string => ELIGIBILITY_LABELS[status] || status;
