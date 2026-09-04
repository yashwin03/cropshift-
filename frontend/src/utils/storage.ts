import type { FarmDetails } from '../mocks/fixtures';
import type { RecommendationResponse } from '../types/api';

const getUserId = () => {
  const user = localStorage.getItem('user');
  if (user) {
    try {
      const parsed = JSON.parse(user);
      return parsed.id || 'guest';
    } catch {
      return 'guest';
    }
  }
  return 'guest';
};

const getFarmKey = () => `cropshift_farm_details_${getUserId()}`;
const getRecKey = () => `cropshift_recommendation_${getUserId()}`;

export const getFarmDetails = (): FarmDetails | null => {
  const data = localStorage.getItem(getFarmKey());
  if (!data) return null;
  try {
    return JSON.parse(data) as FarmDetails;
  } catch {
    return null;
  }
};

export const saveFarmDetails = (details: FarmDetails): void => {
  localStorage.setItem(getFarmKey(), JSON.stringify(details));
};

export const getRecommendation = (): RecommendationResponse | null => {
  const data = localStorage.getItem(getRecKey());
  if (!data) return null;
  try {
    return JSON.parse(data) as RecommendationResponse;
  } catch {
    return null;
  }
};

export const saveRecommendation = (rec: RecommendationResponse): void => {
  localStorage.setItem(getRecKey(), JSON.stringify(rec));
};

export const clearFarmState = (): void => {
  localStorage.removeItem(getFarmKey());
  localStorage.removeItem(getRecKey());
};
