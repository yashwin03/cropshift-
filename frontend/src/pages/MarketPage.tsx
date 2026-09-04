import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import MarketCard from '../components/market/MarketCard';
import Spinner from '../components/common/Spinner';
import ErrorState from '../components/common/ErrorState';
import EmptyState from '../components/common/EmptyState';
import { getRecommendation } from '../utils/storage';
import { getMarkets } from '../services/api';
import type { MarketItem } from '../types/api';

import { useApiState } from '../hooks/useApiState';

export default function MarketPage() {
  const navigate = useNavigate();
  const activeRec = getRecommendation();
  const currentCropState = useApiState<MarketItem>();
  const recommendedCropState = useApiState<MarketItem>();

  const fetchMarketData = async () => {
    if (!activeRec) return;

    // Current crop id (default to 1 - Paddy if missing or mapped from known string names)
    const currentCropId = activeRec.current_crop_profit === 32000 ? 1 : 1;
    // Recommended crop id (default to 2 - Groundnut or 3 - Cotton)
    let recommendedCropId = 2;
    if (activeRec.recommended_crop === 'Cotton') {
      recommendedCropId = 3;
    } else if (activeRec.recommended_crop === 'Paddy') {
      recommendedCropId = 1;
    }

    await Promise.all([
      currentCropState.run(getMarkets(currentCropId)),
      recommendedCropState.run(getMarkets(recommendedCropId)),
    ]);
  };

  useEffect(() => {
    fetchMarketData();
  }, []);

  if (!activeRec) {
    return (
      <div className="max-w-4xl mx-auto py-8 px-4">
        <EmptyState
          title="No Farm Analysis Found"
          message="Please analyze your farm first to compare market information for your crop choices."
          actionLabel="Go to Farm Analysis"
          onAction={() => navigate('/analyze')}
        />
      </div>
    );
  }

  const isLoading = currentCropState.loading || recommendedCropState.loading;
  const error = currentCropState.error || recommendedCropState.error;
  const currentMarket = currentCropState.data;
  const recommendedMarket = recommendedCropState.data;

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-xl mx-auto py-8">
        <ErrorState message={error} onRetry={fetchMarketData} />
      </div>
    );
  }

  if (!currentMarket && !recommendedMarket) {
    return (
      <div className="max-w-4xl mx-auto py-8 px-4">
        <EmptyState
          title="No Market Data Available"
          message="This information is not available for your farm yet."
          actionLabel="Go to Farm Analysis"
          onAction={() => navigate('/analyze')}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-extrabold text-gray-900 leading-tight">
          Market Intelligence
        </h1>
        <p className="text-gray-600 mt-1">
          Compare local crop prices, market distances, and price trends.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {currentMarket && (
          <MarketCard market={currentMarket} title="Current Crop Market" />
        )}
        {recommendedMarket && (
          <MarketCard market={recommendedMarket} title="Recommended Crop Market" />
        )}
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm text-blue-800 flex items-start gap-2.5">
        <span className="text-base" aria-hidden="true">ℹ️</span>
        <p>
          Market price trend represents current price movements in local markets. A rising trend indicates favorable selling conditions.
        </p>
      </div>
    </div>
  );
}
