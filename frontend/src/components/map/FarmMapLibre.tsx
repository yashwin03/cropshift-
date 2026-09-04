import React, { useEffect, useRef, useState } from 'react';
import * as MapLibreGL from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import type { FarmLocation, NearbyMarketLocation } from '../../types/api';
import { formatINR } from '../profit/ProfitComparison';

const maplibregl = MapLibreGL;

interface FarmMapLibreProps {
  farm: FarmLocation;
  markets: NearbyMarketLocation[];
  radiusKm: number;
  activeCenter: [number, number] | null;
  selectedMarket: NearbyMarketLocation | null;
  mapStyleMode: 'road' | 'satellite' | 'terrain';
  onSelectMarket: (market: NearbyMarketLocation) => void;
}

// 100% Reliable Keyless MapLibre Vector/Raster Style Definitions
const ROAD_STYLE = {
  version: 8,
  sources: {
    'osm-tiles': {
      type: 'raster',
      tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
      tileSize: 256,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    },
  },
  layers: [
    {
      id: 'osm-layer',
      type: 'raster',
      source: 'osm-tiles',
      minzoom: 0,
      maxzoom: 19,
    },
  ],
};

const SATELLITE_STYLE = {
  version: 8,
  sources: {
    'satellite-tiles': {
      type: 'raster',
      tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'],
      tileSize: 256,
      attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP',
    },
  },
  layers: [
    {
      id: 'satellite-layer',
      type: 'raster',
      source: 'satellite-tiles',
      minzoom: 0,
      maxzoom: 19,
    },
  ],
};

const TERRAIN_STYLE = {
  version: 8,
  sources: {
    'terrain-tiles': {
      type: 'raster',
      tiles: ['https://tile.opentopomap.org/{z}/{x}/{y}.png'],
      tileSize: 256,
      attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, SRTM | Style &copy; <a href="https://opentopomap.org">OpenTopoMap</a>',
    },
  },
  layers: [
    {
      id: 'terrain-layer',
      type: 'raster',
      source: 'terrain-tiles',
      minzoom: 0,
      maxzoom: 17,
    },
  ],
};

// Generate GeoJSON polygon for radius circle
function createGeoJSONCircle(center: [number, number], radiusKm: number, points: number = 64) {
  const [lng, lat] = center;
  const coords: Array<[number, number]> = [];
  const distanceX = radiusKm / (111.32 * Math.cos((lat * Math.PI) / 180));
  const distanceY = radiusKm / 110.574;

  for (let i = 0; i < points; i++) {
    const theta = (i / points) * (2 * Math.PI);
    const x = distanceX * Math.cos(theta);
    const y = distanceY * Math.sin(theta);
    coords.push([lng + x, lat + y]);
  }
  coords.push(coords[0]);

  return {
    type: 'Feature' as const,
    geometry: {
      type: 'Polygon' as const,
      coordinates: [coords],
    },
    properties: {},
  };
}

export default function FarmMapLibre({
  farm,
  markets,
  radiusKm,
  activeCenter,
  selectedMarket,
  mapStyleMode,
  onSelectMarket,
}: FarmMapLibreProps) {
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);

  const getStyleDefinition = (mode: 'road' | 'satellite' | 'terrain') => {
    const customUrl = import.meta.env.VITE_MAP_STYLE_URL;
    if (customUrl && mode === 'road') return customUrl;

    if (mode === 'satellite') {
      const satUrl = import.meta.env.VITE_MAP_SATELLITE_TILE_URL;
      if (satUrl) return satUrl;
      return SATELLITE_STYLE;
    }

    if (mode === 'terrain') {
      return TERRAIN_STYLE;
    }

    return ROAD_STYLE;
  };

  // 1. Initialize MapLibre GL Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    try {
      const map = new (maplibregl as any).Map({
        container: mapContainerRef.current,
        style: getStyleDefinition(mapStyleMode),
        center: [farm.longitude, farm.latitude],
        zoom: 9.5,
        pitch: 0,
      });

      map.addControl(new (maplibregl as any).NavigationControl(), 'top-right');

      mapRef.current = map;

      return () => {
        markersRef.current.forEach((m) => m.remove());
        markersRef.current = [];
        map.remove();
        mapRef.current = null;
      };
    } catch {
      // Fallback for non-WebGL/test environments
    }
  }, [mapStyleMode]);

  // 2. Update Map Recenter when activeCenter changes
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !activeCenter) return;
    map.flyTo({
      center: [activeCenter[1], activeCenter[0]],
      zoom: 10.5,
      essential: true,
    });
  }, [activeCenter]);

  // 3. Render/Update Radius Polygon & Markers
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    const farmCenter: [number, number] = [farm.longitude, farm.latitude];

    const updateMapLayers = () => {
      // Add/Update Radius Source & Layers
      const circleData = createGeoJSONCircle(farmCenter, radiusKm);

      try {
        if (map.getSource('radius-source')) {
          map.getSource('radius-source').setData(circleData);
        } else {
          map.addSource('radius-source', {
            type: 'geojson',
            data: circleData,
          });

          map.addLayer({
            id: 'radius-fill',
            type: 'fill',
            source: 'radius-source',
            paint: {
              'fill-color': '#10b981',
              'fill-opacity': 0.15,
            },
          });

          map.addLayer({
            id: 'radius-line',
            type: 'line',
            source: 'radius-source',
            paint: {
              'line-color': '#10b981',
              'line-width': 2.5,
              'line-dasharray': [2, 2],
            },
          });
        }
      } catch {
        // Handle layer updates gracefully
      }

      // Clear previous markers
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];

      // Add Farm Marker
      const farmEl = document.createElement('div');
      farmEl.className = 'w-10 h-10 bg-emerald-600 border-2 border-white rounded-full flex items-center justify-center text-white font-black text-base shadow-2xl shadow-emerald-950/80 cursor-pointer transform hover:scale-110 transition-transform';
      farmEl.innerHTML = '🏡';

      const farmPopup = new (maplibregl as any).Popup({ offset: 25 }).setHTML(`
        <div style="color: #0f172a; font-family: sans-serif; padding: 4px;">
          <strong style="font-size: 13px; color: #059669;">${farm.farm_name || 'My Farm'}</strong>
          <div style="font-size: 11px; color: #475569; margin-top: 2px;">Primary Farm Location</div>
          <div style="font-size: 10px; color: #64748b; font-family: monospace; margin-top: 4px;">${farm.latitude.toFixed(4)}° N, ${farm.longitude.toFixed(4)}° E</div>
        </div>
      `);

      const farmMarker = new (maplibregl as any).Marker({ element: farmEl })
        .setLngLat([farm.longitude, farm.latitude])
        .setPopup(farmPopup)
        .addTo(map);

      markersRef.current.push(farmMarker);

      // Add Market Markers
      markets.forEach((m) => {
        const isWithin = m.within_radius !== false;
        const isSelected = selectedMarket?.market_name === m.market_name;

        const mEl = document.createElement('div');
        const bgClass = isWithin ? 'bg-emerald-500 border-white' : 'bg-amber-500 border-white';
        const ringClass = isSelected ? 'ring-4 ring-emerald-400 scale-125 z-30' : '';

        mEl.className = `w-9 h-9 ${bgClass} ${ringClass} border-2 rounded-full flex items-center justify-center text-white font-extrabold text-sm shadow-xl cursor-pointer transform hover:scale-110 transition-transform`;
        mEl.innerHTML = '🛒';

        const priceText = m.current_price ? `${formatINR(m.current_price)} / ${m.price_unit || 'Quintal'}` : 'Current price unavailable';
        const reachText = isWithin ? `<span style="color: #059669; font-weight: bold;">WITHIN ${radiusKm} KM REACH</span>` : `<span style="color: #d97706; font-weight: bold;">OUTSIDE ${radiusKm} KM REACH</span>`;

        const mPopup = new (maplibregl as any).Popup({ offset: 25 }).setHTML(`
          <div style="color: #0f172a; font-family: sans-serif; padding: 4px; min-width: 170px;">
            <strong style="font-size: 13px; color: #1e293b;">${m.market_name}</strong>
            <div style="font-size: 11px; color: #475569; margin-top: 2px;">Distance: <strong>${m.distance_km.toFixed(1)} km straight-line</strong></div>
            <div style="font-size: 11px; margin-top: 2px;">Crop: <strong>${m.crop || 'Groundnut'}</strong></div>
            <div style="font-size: 11px; color: #059669; font-weight: bold; margin-top: 2px;">${priceText}</div>
            <div style="font-size: 10px; margin-top: 4px;">${reachText}</div>
          </div>
        `);

        mEl.addEventListener('click', () => {
          onSelectMarket(m);
        });

        const mMarker = new (maplibregl as any).Marker({ element: mEl })
          .setLngLat([m.longitude, m.latitude])
          .setPopup(mPopup)
          .addTo(map);

        markersRef.current.push(mMarker);
      });
    };

    if (map.isStyleLoaded()) {
      updateMapLayers();
    } else {
      map.once('style.load', updateMapLayers);
    }
  }, [farm, markets, radiusKm, selectedMarket]);

  return (
    <div className="w-full h-full relative" data-testid="map-container">
      <div ref={mapContainerRef} className="w-full h-full" />

      {/* Map Mode Status Badge */}
      <div className="absolute bottom-3 right-3 z-10 text-[10px] font-mono text-slate-300 bg-slate-950/85 backdrop-blur-md px-3 py-1 rounded-xl border border-slate-800 shadow-xl flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
        <span>MapLibre GL Vector Engine</span>
        <span>•</span>
        <span className="uppercase text-emerald-400 font-bold">{mapStyleMode} MODE</span>
      </div>
    </div>
  );
}
