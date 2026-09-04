import React from 'react';
import FarmMapLibre from './FarmMapLibre';
import type { FarmLocation, NearbyMarketLocation } from '../../types/api';

interface FarmMapProps {
  farm: FarmLocation;
  markets: NearbyMarketLocation[];
  radiusKm?: number;
  activeCenter: [number, number] | null;
  selectedMarket?: NearbyMarketLocation | null;
  mapStyleMode?: 'road' | 'satellite' | 'terrain';
  onSelectMarket: (lat: number, lng: number) => void;
  onSelectMarketObject?: (market: NearbyMarketLocation) => void;
}

export default function FarmMap({
  farm,
  markets,
  radiusKm = 50,
  activeCenter,
  selectedMarket = null,
  mapStyleMode = 'road',
  onSelectMarket,
  onSelectMarketObject,
}: FarmMapProps) {
  const handleMarketClick = (market: NearbyMarketLocation) => {
    onSelectMarket(market.latitude, market.longitude);
    if (onSelectMarketObject) {
      onSelectMarketObject(market);
    }
  };

  return (
    <div className="w-full h-[420px] rounded-3xl overflow-hidden border border-slate-800 bg-slate-950 shadow-2xl relative z-10">
      <FarmMapLibre
        farm={farm}
        markets={markets}
        radiusKm={radiusKm}
        activeCenter={activeCenter}
        selectedMarket={selectedMarket}
        mapStyleMode={mapStyleMode}
        onSelectMarket={handleMarketClick}
      />
    </div>
  );
}
