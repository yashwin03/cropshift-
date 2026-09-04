import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import FarmMap from '../components/map/FarmMap';
import Spinner from '../components/common/Spinner';
import ErrorState from '../components/common/ErrorState';
import EmptyState from '../components/common/EmptyState';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { getFarmDetails, getRecommendation } from '../utils/storage';
import { getGeospatial } from '../services/api';
import type { GeospatialResponse, NearbyMarketLocation } from '../types/api';
import { formatINR } from '../components/profit/ProfitComparison';
import { useApiState } from '../hooks/useApiState';

export default function MapPage() {
  const navigate = useNavigate();
  const [selectedRadius, setSelectedRadius] = useState<number>(50);
  const [mapStyleMode, setMapStyleMode] = useState<'road' | 'satellite' | 'terrain'>('road');
  const [activeCenter, setActiveCenter] = useState<[number, number] | null>(null);
  const [selectedMarket, setSelectedMarket] = useState<NearbyMarketLocation | null>(null);

  const farm = getFarmDetails();
  const recommendation = getRecommendation();
  const apiState = useApiState<GeospatialResponse>();

  const fetchGeospatialData = async (radius: number = selectedRadius) => {
    if (!farm) return;
    const result = await apiState.run(getGeospatial(farm.farm_id, radius));
    if (result?.farm?.latitude && result?.farm?.longitude) {
      setActiveCenter([result.farm.latitude, result.farm.longitude]);
    }
  };

  useEffect(() => {
    fetchGeospatialData(selectedRadius);
  }, [selectedRadius]);

  const loading = apiState.loading;
  const error = apiState.error;
  const data = apiState.data;

  if (!farm) {
    return (
      <div className="max-w-4xl mx-auto py-8 px-4">
        <EmptyState
          title="No Farm Profile Found"
          message="Please analyze your farm first to visualize geospatial mandi reach."
          actionLabel="Go to Farm Analysis"
          onAction={() => navigate('/analyze')}
        />
      </div>
    );
  }

  if (loading && !data) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="max-w-xl mx-auto py-8">
        <ErrorState message={error} onRetry={() => fetchGeospatialData(selectedRadius)} />
      </div>
    );
  }

  const hasCoordinates = data?.farm?.latitude && data?.farm?.longitude;

  if (!data || !hasCoordinates) {
    return (
      <div className="max-w-4xl mx-auto py-8 px-4 space-y-6">
        <div>
          <h1 className="text-2xl font-black text-white leading-tight flex items-center gap-2">
            <span>🗺️</span> Geospatial Intelligence Map & Mandi Reach
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Visual route logistics and regional mandi reach.
          </p>
        </div>
        <EmptyState
          title="Geospatial Coordinates Missing"
          message="Farm boundary geometry is not currently available. We couldn't retrieve valid coordinates for your farm to map nearby markets."
          actionLabel="Update Location Profile"
          onAction={() => navigate('/analyze')}
        />
      </div>
    );
  }

  const allMarkets = data.nearby_markets || [];
  const marketsWithinReach = allMarkets.filter((m) => m.within_radius !== false);
  const fallbackMarketOutside = allMarkets.find((m) => m.within_radius === false);
  const bestMarket = marketsWithinReach[0] || fallbackMarketOutside;

  const handleSelectMarket = (market: NearbyMarketLocation) => {
    setSelectedMarket(market);
    setActiveCenter([market.latitude, market.longitude]);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="bg-slate-900/90 backdrop-blur-2xl p-5 rounded-3xl border border-slate-800 shadow-2xl flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="inline-flex items-center gap-2 bg-emerald-950 text-emerald-400 text-[10px] font-extrabold px-3 py-1 rounded-full border border-emerald-500/30 mb-1">
            <span>🌾 Farm → Mandi → Market Reach</span>
            <span>•</span>
            <span>PostGIS Intelligence</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight leading-tight flex items-center gap-2">
            <span>🗺️</span> Map Explorer & APMC Mandi Reach
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Centered at {farm.farm_name || 'My Farm'} in {farm.district || data.geographic_context?.district || 'Regional'}, {farm.state || data.geographic_context?.state || 'State'}
          </p>
        </div>

        {/* Map Style & Radius Controls */}
        <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
          {/* Map Style Mode */}
          <div className="bg-slate-950 p-1 rounded-xl border border-slate-800 flex items-center gap-1 text-xs">
            {(['road', 'satellite', 'terrain'] as const).map((mode) => (
              <button
                key={mode}
                type="button"
                onClick={() => setMapStyleMode(mode)}
                className={`px-2.5 py-1 rounded-lg font-bold capitalize transition-colors ${
                  mapStyleMode === mode ? 'bg-emerald-500 text-slate-950' : 'text-slate-400 hover:text-white'
                }`}
              >
                {mode}
              </button>
            ))}
          </div>

          {/* Market Reach Radius */}
          <div className="flex items-center gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800">
            <span className="text-[10px] font-extrabold text-slate-400 px-2 uppercase">Reach:</span>
            {[25, 50, 75, 100].map((radius) => (
              <button
                key={radius}
                type="button"
                onClick={() => setSelectedRadius(radius)}
                className={`px-2.5 py-1 rounded-lg text-xs font-black transition-all ${
                  selectedRadius === radius ? 'bg-emerald-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
                }`}
              >
                {radius} km
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Grid: Vector Map + Side Intelligence Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Vector Map Container */}
        <div className="lg:col-span-2 space-y-4">
          <FarmMap
            farm={data.farm!}
            markets={allMarkets}
            radiusKm={selectedRadius}
            activeCenter={activeCenter}
            selectedMarket={selectedMarket}
            mapStyleMode={mapStyleMode}
            onSelectMarket={(lat, lng) => setActiveCenter([lat, lng])}
            onSelectMarketObject={handleSelectMarket}
          />

          {/* Map Status Bar */}
          <div className="bg-slate-900/90 backdrop-blur-2xl p-3.5 rounded-2xl border border-slate-800 flex flex-wrap justify-between items-center text-xs text-slate-300 gap-2">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="font-extrabold text-white">PostGIS Spatial Engine</span>
              <span className="text-slate-500">•</span>
              <span className="text-slate-400">{data.distance_information || `${marketsWithinReach.length} markets within ${selectedRadius} km`}</span>
            </div>
            <div className="text-[11px] text-slate-400 font-mono">
              GPS: {data.farm?.latitude.toFixed(4)}° N, {data.farm?.longitude.toFixed(4)}° E
            </div>
          </div>
        </div>

        {/* Right Col: Best Reachable Market & Market List */}
        <div className="space-y-5">
          {/* Best Reachable Market Hero Card */}
          {bestMarket ? (
            <Card className="bg-slate-900/90 border-2 border-emerald-500/40 p-5 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-[10px] font-black uppercase tracking-wider text-emerald-400 bg-emerald-950 px-2.5 py-0.5 rounded-full border border-emerald-500/30">
                  {bestMarket.within_radius !== false ? '🥇 Best Reachable Mandi' : '📍 Nearest Available Mandi'}
                </span>
                <span className="text-xs font-bold text-slate-400">
                  {bestMarket.within_radius !== false ? `WITHIN ${selectedRadius} KM` : `OUTSIDE ${selectedRadius} KM`}
                </span>
              </div>

              <div>
                <h3 className="text-xl font-black text-white tracking-tight">{bestMarket.market_name}</h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  {bestMarket.district || 'Regional'}, {bestMarket.state || 'Karnataka'}
                </p>
              </div>

              <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 space-y-1.5">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-400 font-bold">Proximity Distance:</span>
                  <span className="text-white font-extrabold">{bestMarket.distance_km.toFixed(1)} km straight-line</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-400 font-bold">Relevant Crop:</span>
                  <span className="text-emerald-400 font-extrabold">{bestMarket.crop || recommendation?.recommended_crop || 'Groundnut'}</span>
                </div>
                {bestMarket.current_price && (
                  <div className="flex justify-between items-center text-xs pt-1.5 border-t border-slate-800/80">
                    <span className="text-slate-300 font-extrabold">Current Price:</span>
                    <span className="text-emerald-400 font-black text-sm">
                      {formatINR(bestMarket.current_price)} / {bestMarket.price_unit || 'Quintal'}
                    </span>
                  </div>
                )}
              </div>

              <Button
                variant="primary"
                size="sm"
                className="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-xs"
                onClick={() => handleSelectMarket(bestMarket)}
              >
                Focus {bestMarket.market_name} on Map
              </Button>
            </Card>
          ) : null}

          {/* Markets Within Radius List */}
          <Card className="bg-slate-900/90 border border-slate-800 p-4 space-y-3">
            <div className="flex justify-between items-center">
              <h3 className="text-xs font-black uppercase text-slate-200 tracking-wider">
                Mandis Within {selectedRadius} km ({marketsWithinReach.length})
              </h3>
            </div>

            {marketsWithinReach.length > 0 ? (
              <div className="space-y-2.5 max-h-[320px] overflow-y-auto pr-1">
                {marketsWithinReach.map((m, idx) => (
                  <div
                    key={m.market_id || idx}
                    onClick={() => handleSelectMarket(m)}
                    className={`p-3 rounded-xl border transition-all cursor-pointer ${
                      selectedMarket?.market_name === m.market_name
                        ? 'bg-emerald-950/40 border-emerald-500/60 shadow-lg'
                        : 'bg-slate-950 border-slate-800/80 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="text-xs font-bold text-white flex items-center gap-1.5">
                          <span>🛒</span> {m.market_name}
                        </h4>
                        <p className="text-[10px] text-slate-400 mt-0.5">
                          {m.district || 'APMC'}, {m.state || 'Karnataka'} • {m.distance_km.toFixed(1)} km straight-line
                        </p>
                      </div>
                      <span className="text-[10px] font-extrabold text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded-md border border-emerald-500/30">
                        REACHABLE
                      </span>
                    </div>

                    {m.current_price && (
                      <div className="mt-2 text-[11px] font-black text-emerald-400 flex justify-between items-center">
                        <span>{m.crop || 'Groundnut'}</span>
                        <span>{formatINR(m.current_price)} / {m.price_unit || 'Quintal'}</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              /* Trustworthy Empty State */
              <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 text-center space-y-2">
                <div className="text-xs font-bold text-amber-400 uppercase tracking-wider">
                  ⚠️ NO MARKET WITHIN {selectedRadius} KM
                </div>
                {fallbackMarketOutside ? (
                  <div className="text-xs text-slate-300">
                    Nearest available mandi is <strong className="text-white">{fallbackMarketOutside.market_name}</strong> at <strong className="text-emerald-400">{fallbackMarketOutside.distance_km.toFixed(1)} km straight-line</strong>.
                  </div>
                ) : (
                  <div className="text-xs text-slate-400">
                    No APMC mandis found in the database for this region.
                  </div>
                )}
                <div className="pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-xs bg-slate-900 border-slate-700 text-emerald-400"
                    onClick={() => setSelectedRadius(selectedRadius === 25 ? 50 : selectedRadius === 50 ? 75 : 100)}
                  >
                    Expand Radius to {selectedRadius === 25 ? '50' : selectedRadius === 50 ? '75' : '100'} km
                  </Button>
                </div>
              </div>
            )}
          </Card>
        </div>
      </div>

      {/* Selected Market Detail Drawer / Card Modal */}
      {selectedMarket && (
        <Card className="bg-slate-900/95 border-2 border-emerald-500/60 p-5 rounded-3xl shadow-2xl flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-black uppercase text-emerald-400">Selected Mandi Details</span>
              <span className="text-slate-600">•</span>
              <span className={`text-[10px] font-extrabold px-2.5 py-0.5 rounded-full ${
                selectedMarket.within_radius !== false ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/40' : 'bg-amber-950 text-amber-400 border border-amber-500/40'
              }`}>
                {selectedMarket.within_radius !== false ? `WITHIN ${selectedRadius} KM` : `OUTSIDE ${selectedRadius} KM`}
              </span>
            </div>
            <h3 className="text-xl font-black text-white">{selectedMarket.market_name}</h3>
            <p className="text-xs text-slate-300">
              Location: {selectedMarket.district || 'Regional'} District, {selectedMarket.state || 'Karnataka'} • Proximity: <strong className="text-white">{selectedMarket.distance_km.toFixed(1)} km straight-line</strong>
            </p>
          </div>

          <div className="flex items-center gap-3">
            {selectedMarket.current_price && (
              <div className="text-right">
                <span className="text-[10px] text-slate-400 uppercase font-bold block">Current Mandi Rate</span>
                <span className="text-lg font-black text-emerald-400">
                  {formatINR(selectedMarket.current_price)} / {selectedMarket.price_unit || 'Quintal'}
                </span>
              </div>
            )}
            <Button
              variant="outline"
              size="sm"
              className="border-slate-700 text-slate-300 hover:text-white"
              onClick={() => setSelectedMarket(null)}
            >
              Close
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
}
