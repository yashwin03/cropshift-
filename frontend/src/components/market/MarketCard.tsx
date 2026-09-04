import React from 'react';
import Card from '../common/Card';
import StatusBadge from '../common/StatusBadge';
import TrendIndicator from './TrendIndicator';
import type { MarketItem } from '../../types/api';
import { formatINR } from '../profit/ProfitComparison';

interface MarketCardProps {
  market: MarketItem;
  title: string;
}

export default function MarketCard({ market, title }: MarketCardProps) {
  const isPriceAvailable = market.price > 0;

  return (
    <Card className="border-gray-200 bg-white">
      <div className="flex items-center justify-between pb-3 border-b border-gray-100 mb-4">
        <div>
          <span className="text-xs font-bold text-gray-400 uppercase tracking-wider block">
            {title}
          </span>
          <h3 className="text-xl font-extrabold text-gray-900">
            {market.crop_name}
          </h3>
        </div>
        <StatusBadge status={market.data_status} />
      </div>

      <div className="space-y-4">
        {/* Price display */}
        <div>
          <span className="text-xs text-gray-500 font-medium">Market Price</span>
          {isPriceAvailable ? (
            <p className="text-2xl font-black text-gray-900">
              {formatINR(market.price)}{' '}
              <span className="text-sm font-semibold text-gray-500">
                per {market.price_unit || 'Quintal'}
              </span>
            </p>
          ) : (
            <p className="text-xl font-bold text-red-600">Price unavailable</p>
          )}
        </div>

        {/* Location & distance */}
        <div className="grid grid-cols-2 gap-4 border-t border-b border-gray-50 py-3">
          <div>
            <span className="text-xs text-gray-500 font-medium block">Market Centre</span>
            <span className="text-sm font-bold text-gray-800">{market.market_name}</span>
            <span className="text-xs text-gray-400 block">{market.market_location}</span>
          </div>
          <div>
            <span className="text-xs text-gray-500 font-medium block">Distance</span>
            <span className="text-sm font-bold text-gray-800">{market.distance_km} km</span>
          </div>
        </div>

        {/* Trend & Score */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
          <div>
            <span className="text-xs text-gray-500 font-medium block mb-1">Price Trend</span>
            <TrendIndicator trend={market.trend} />
          </div>
          <div className="flex-1 max-w-xs">
            <div className="flex justify-between text-xs text-gray-500 font-medium mb-1">
              <span>Market Score</span>
              <span className="font-bold text-gray-800">{market.market_score}/100</span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-2">
              <div
                className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${market.market_score}%` }}
              />
            </div>
          </div>
        </div>

        {/* Source info */}
        <div className="text-xs text-gray-400 pt-2 border-t border-gray-50">
          Source: {market.data_source || 'Official market repositories'}
        </div>
      </div>
    </Card>
  );
}
