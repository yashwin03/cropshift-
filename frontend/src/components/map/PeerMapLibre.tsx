import React, { useEffect, useRef } from 'react';
import * as MapLibreGL from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import type { PeerProofPeer } from '../../types/api';

const maplibregl = MapLibreGL;

interface PeerMapLibreProps {
  centerLat: number;
  centerLon: number;
  radiusKm: number;
  peers: PeerProofPeer[];
  selectedPeerId: number | null;
  onSelectPeer: (peer: PeerProofPeer) => void;
  cropName?: string;
}

// Keyless OpenStreetMap standard raster style — 100% free, no API key required
const KEYLESS_OSM_MAP_STYLE = {
  version: 8,
  sources: {
    'osm-tiles': {
      type: 'raster',
      tiles: [
        'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
      ],
      tileSize: 256,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    },
  },
  layers: [
    {
      id: 'osm-tiles-layer',
      type: 'raster',
      source: 'osm-tiles',
      minzoom: 0,
      maxzoom: 19,
    },
  ],
};

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

function createFarmCenterEl(): HTMLDivElement {
  const el = document.createElement('div');
  el.style.cssText = `
    width: 44px; height: 44px;
    background: linear-gradient(135deg, #f59e0b, #d97706);
    border: 3px solid #fff;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 0 0 4px rgba(245,158,11,0.35), 0 4px 16px rgba(0,0,0,0.5);
    cursor: pointer;
    animation: pulse-farm 2s infinite;
    position: relative; z-index: 20;
  `;
  el.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
    <polyline points="9 22 9 12 15 12 15 22"/>
  </svg>`;
  return el;
}

function createPeerMarkerEl(isSelected: boolean, stage: string): HTMLDivElement {
  const el = document.createElement('div');
  const size = isSelected ? '42px' : '36px';
  const bg = isSelected
    ? 'linear-gradient(135deg, #10b981, #059669)'
    : 'linear-gradient(135deg, #34d399, #10b981)';
  const shadow = isSelected
    ? '0 0 0 5px rgba(16,185,129,0.5), 0 6px 20px rgba(0,0,0,0.6)'
    : '0 0 0 3px rgba(52,211,153,0.3), 0 4px 12px rgba(0,0,0,0.4)';
  const scale = isSelected ? 'scale(1.2)' : 'scale(1)';

  el.style.cssText = `
    width: ${size}; height: ${size};
    background: ${bg};
    border: 3px solid #fff;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    box-shadow: ${shadow};
    cursor: pointer;
    transform: ${scale};
    transition: all 0.2s ease;
    position: relative; z-index: ${isSelected ? 30 : 10};
  `;

  // Leaf/plant SVG icon - no emoji
  el.innerHTML = `<svg width="${isSelected ? 18 : 16}" height="${isSelected ? 18 : 16}" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M12 22V12M12 12C12 12 7 9 5 5c5 0 9 4 9 4s1-6 5-7c0 5-3 9-7 10z"/>
  </svg>`;

  return el;
}

export default function PeerMapLibre({
  centerLat,
  centerLon,
  radiusKm,
  peers,
  selectedPeerId,
  onSelectPeer,
  cropName = 'Crop',
}: PeerMapLibreProps) {
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);

  // Initialize map once
  useEffect(() => {
    if (!mapContainerRef.current) return;

    try {
      const zoomLevel = radiusKm <= 50 ? 8 : 7.2;
      const map = new (maplibregl as any).Map({
        container: mapContainerRef.current,
        style: KEYLESS_OSM_MAP_STYLE,
        center: [centerLon, centerLat],
        zoom: zoomLevel,
        pitch: 0,
        attributionControl: false,
      });

      map.addControl(
        new (maplibregl as any).NavigationControl({ showCompass: false }),
        'top-right'
      );
      map.addControl(
        new (maplibregl as any).AttributionControl({ compact: true }),
        'bottom-right'
      );

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
  }, [centerLat, centerLon]);

  // Update markers and radius ring whenever data changes
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    const centerPoint: [number, number] = [centerLon, centerLat];

    const updateMapLayers = () => {
      const circleData = createGeoJSONCircle(centerPoint, radiusKm);

      // Update or add radius ring
      try {
        if (map.getSource('radius-source')) {
          map.getSource('radius-source').setData(circleData);
        } else {
          map.addSource('radius-source', { type: 'geojson', data: circleData });

          map.addLayer({
            id: 'radius-fill',
            type: 'fill',
            source: 'radius-source',
            paint: { 'fill-color': '#f59e0b', 'fill-opacity': 0.07 },
          });

          map.addLayer({
            id: 'radius-line',
            type: 'line',
            source: 'radius-source',
            paint: {
              'line-color': '#f59e0b',
              'line-width': 1.5,
              'line-dasharray': [4, 3],
            },
          });
        }
      } catch {
        // Layer update error — ignore
      }

      // Remove old markers
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];

      // ── Center "Your Farm" marker ──
      const centerEl = createFarmCenterEl();

      const centerPopup = new (maplibregl as any).Popup({
        offset: 28,
        closeButton: false,
        className: 'peer-popup',
      }).setHTML(`
        <div style="background:#1e293b;color:#f8fafc;font-family:system-ui,sans-serif;padding:10px 12px;border-radius:10px;min-width:160px;border:1px solid #f59e0b40;">
          <div style="font-size:12px;font-weight:800;color:#fbbf24;margin-bottom:4px;">Your Farm</div>
          <div style="font-size:10px;color:#94a3b8;">Search center for ${cropName}</div>
          <div style="font-size:9px;color:#64748b;margin-top:3px;font-family:monospace;">${centerLat.toFixed(4)}°N ${centerLon.toFixed(4)}°E</div>
        </div>
      `);

      const centerMarker = new (maplibregl as any).Marker({ element: centerEl })
        .setLngLat([centerLon, centerLat])
        .setPopup(centerPopup)
        .addTo(map);

      markersRef.current.push(centerMarker);

      // ── Peer Farmer Markers ──
      peers.forEach((peer) => {
        if (peer.latitude == null || peer.longitude == null) return;
        const isSelected = selectedPeerId === peer.id;

        const pEl = createPeerMarkerEl(isSelected, peer.crop_stage || '');

        const distText =
          peer.distance_km != null ? `${peer.distance_km.toFixed(1)} km away` : 'Nearby';

        const pPopup = new (maplibregl as any).Popup({
          offset: 26,
          closeButton: false,
          className: 'peer-popup',
        }).setHTML(`
          <div style="background:#1e293b;color:#f8fafc;font-family:system-ui,sans-serif;padding:10px 12px;border-radius:10px;min-width:190px;border:1px solid #10b98140;">
            <div style="font-size:12px;font-weight:800;color:#34d399;margin-bottom:4px;">${peer.peer_display_id}</div>
            <div style="font-size:11px;color:#cbd5e1;margin-bottom:6px;">Growing: <strong style="color:#fff;">${peer.crop_name || cropName}</strong></div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;font-size:10px;">
              <div><span style="color:#64748b;">District</span><br><strong style="color:#e2e8f0;">${peer.district}</strong></div>
              <div><span style="color:#64748b;">Distance</span><br><strong style="color:#fbbf24;">${distText}</strong></div>
              <div><span style="color:#64748b;">Area</span><br><strong style="color:#e2e8f0;">${peer.acres} acres</strong></div>
              <div><span style="color:#64748b;">Stage</span><br><strong style="color:#a78bfa;">${peer.crop_stage || 'Growing'}</strong></div>
            </div>
            <div style="margin-top:6px;padding-top:5px;border-top:1px solid #334155;font-size:9px;color:#22c55e;font-weight:700;">Demo data — not real farmer verification</div>
          </div>
        `);

        pEl.addEventListener('click', () => {
          onSelectPeer(peer);
        });

        const pMarker = new (maplibregl as any).Marker({ element: pEl })
          .setLngLat([peer.longitude, peer.latitude])
          .setPopup(pPopup)
          .addTo(map);

        markersRef.current.push(pMarker);
      });
    };

    if (map.isStyleLoaded()) {
      updateMapLayers();
    } else {
      map.once('style.load', updateMapLayers);
    }
  }, [centerLat, centerLon, radiusKm, peers, selectedPeerId, cropName]);

  return (
    <div className="w-full relative" data-testid="peer-map-container">
      <div
        ref={mapContainerRef}
        className="w-full rounded-2xl overflow-hidden border border-emerald-500/30"
        style={{ height: '460px' }}
      />
      {/* Map overlay badges */}
      <div className="absolute top-3 left-3 z-10 flex items-center gap-2">
        <div className="text-[10px] font-bold text-white bg-slate-900/90 backdrop-blur-sm px-2.5 py-1.5 rounded-lg border border-emerald-500/40 flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>{peers.length} farmers within {radiusKm} km</span>
        </div>
      </div>
      <div className="absolute bottom-3 left-3 z-10 text-[9px] font-mono text-slate-300 bg-slate-900/80 backdrop-blur-sm px-2 py-1 rounded border border-slate-700">
        OpenStreetMap Vector Tile Engine · WGS84
      </div>
    </div>
  );
}
