import React, { useState, useEffect, useCallback } from 'react';
import type { PeerProofResponse, PeerProofPeer } from '../../types/api';
import { getPeerProof, requestPeerContact } from '../../services/peerProofService';
import Button from '../common/Button';
import PeerMapLibre from '../map/PeerMapLibre';
import { IconMapPin, IconShield } from '../common/Icons';

interface PeerProofCardProps {
  cropId: number;
  cropName: string;
  farmId?: number;
  district?: string;
  latitude?: number;
  longitude?: number;
}

export default function PeerProofCard({ cropId, cropName, farmId, district, latitude, longitude }: PeerProofCardProps) {
  const [proof, setProof] = useState<PeerProofResponse | null>(null);
  const [radiusKm, setRadiusKm] = useState<number>(50);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPeer, setSelectedPeer] = useState<PeerProofPeer | null>(null);
  const [contactedPeers, setContactedPeers] = useState<Record<number, any>>({});
  const [contactingId, setContactingId] = useState<number | null>(null);

  const fetchProof = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getPeerProof(cropId, farmId, district, radiusKm, latitude, longitude);
      setProof(data);
      if (data?.peers && data.peers.length > 0) {
        setSelectedPeer((prev) => (prev ? data.peers!.find((p) => p.id === prev.id) || data.peers![0] : data.peers![0]));
      } else {
        setSelectedPeer(null);
      }
    } catch (err: any) {
      console.error('Failed to load peer network:', err);
      setError('Unable to load farmer network at this time.');
    } finally {
      setLoading(false);
    }
  }, [cropId, farmId, district, radiusKm, latitude, longitude]);

  useEffect(() => {
    fetchProof();
  }, [fetchProof]);

  const handleRequestContact = async (peerId: number) => {
    try {
      setContactingId(peerId);
      const details = await requestPeerContact(peerId);
      setContactedPeers((prev) => ({ ...prev, [peerId]: details }));
    } catch (err: any) {
      console.error('Failed to request contact:', err);
    } finally {
      setContactingId(null);
    }
  };

  const peersList = proof?.peers || [];
  const cohortCount = proof?.cohort_count || peersList.length;
  const centerLat = proof?.center_latitude ?? latitude ?? 15.4589;
  const centerLon = proof?.center_longitude ?? longitude ?? 75.0078;

  return (
    <div className="bg-gradient-to-br from-slate-900 via-emerald-950/20 to-slate-900 border border-emerald-500/30 rounded-3xl shadow-2xl overflow-hidden">
      {/* ── HERO HEADER ── */}
      <div className="px-6 pt-6 pb-4">
        {/* Section label */}
        <div className="inline-flex items-center gap-2 text-[10px] font-black text-emerald-400 bg-emerald-950/80 px-3 py-1 rounded-full border border-emerald-500/30 mb-3 uppercase tracking-widest">
          <IconMapPin size={11} className="text-emerald-400" />
          <span>Farmer Network</span>
        </div>

        {/* Main title */}
        <h3 className="text-2xl sm:text-3xl font-black text-white tracking-tight leading-tight">
          Farmers Growing <span className="text-emerald-400">{cropName}</span> Near You
        </h3>

        {/* Subtitle count + radius toggle */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mt-3">
          {loading ? (
            <p className="text-sm text-slate-400 animate-pulse">Loading nearby farmers…</p>
          ) : error ? (
            <p className="text-sm text-rose-400">{error}</p>
          ) : !proof?.available ? (
            <p className="text-sm text-slate-400">No nearby farmers found for {cropName}.</p>
          ) : (
            <p className="text-base font-bold text-slate-200">
              <span className="text-3xl font-black text-emerald-400">{cohortCount}</span>
              {' '}farmer{cohortCount !== 1 ? 's' : ''} within{' '}
              <span className="text-amber-400">{radiusKm} km</span>
              {proof?.total_districts ? (
                <span className="text-slate-400 text-sm font-medium"> · {proof.total_districts} districts</span>
              ) : null}
            </p>
          )}

          {/* 50 / 100 KM radius toggle */}
          <div className="flex items-center gap-1 bg-slate-950/80 p-1 rounded-xl border border-emerald-500/20 shrink-0">
            <button
              type="button"
              onClick={() => setRadiusKm(50)}
              className={`px-4 py-1.5 rounded-lg text-xs font-black transition-all ${
                radiusKm === 50
                  ? 'bg-emerald-500 text-slate-950 shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              50 KM
            </button>
            <button
              type="button"
              onClick={() => setRadiusKm(100)}
              className={`px-4 py-1.5 rounded-lg text-xs font-black transition-all ${
                radiusKm === 100
                  ? 'bg-emerald-500 text-slate-950 shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              100 KM
            </button>
          </div>
        </div>
      </div>

      {/* ── MAP HERO ── */}
      <div className="px-4 pb-4">
        {loading ? (
          <div className="w-full rounded-2xl overflow-hidden border border-emerald-500/30 bg-slate-950/60 flex items-center justify-center" style={{ height: '460px' }}>
            <div className="text-center space-y-3">
              <div className="w-10 h-10 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-sm text-slate-400">Loading farmer map…</p>
            </div>
          </div>
        ) : (
          <PeerMapLibre
            centerLat={centerLat}
            centerLon={centerLon}
            radiusKm={radiusKm}
            peers={peersList}
            selectedPeerId={selectedPeer?.id || null}
            onSelectPeer={(p) => setSelectedPeer(p)}
            cropName={cropName}
          />
        )}
      </div>

      {/* ── SELECTED FARMER DETAIL ── */}
      {selectedPeer && !loading && (
        <div className="mx-4 mb-4 p-4 bg-slate-950/90 rounded-2xl border border-emerald-500/30 space-y-3">
          <div className="flex justify-between items-start flex-wrap gap-2">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="font-black text-sm text-emerald-300">{selectedPeer.peer_display_id}</span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-500/30">
                  {selectedPeer.verification_status || 'Cultivation Record'}
                </span>
              </div>
              <p className="text-xs text-slate-400">
                {selectedPeer.district}, {selectedPeer.state || 'Karnataka'} ·{' '}
                <strong className="text-amber-400">
                  {selectedPeer.distance_km != null ? `${selectedPeer.distance_km.toFixed(1)} km away` : 'Nearby'}
                </strong>
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
            <div className="bg-slate-900 p-2.5 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-400 block mb-0.5">Crop</span>
              <strong className="text-white">{selectedPeer.crop_name || cropName}</strong>
            </div>
            <div className="bg-slate-900 p-2.5 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-400 block mb-0.5">Farm Area</span>
              <strong className="text-white">{selectedPeer.acres} acres</strong>
            </div>
            <div className="bg-slate-900 p-2.5 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-400 block mb-0.5">Growth Stage</span>
              <strong className="text-amber-300">{selectedPeer.crop_stage || 'Growing'}</strong>
            </div>
            <div className="bg-slate-900 p-2.5 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-400 block mb-0.5">Est. Harvest</span>
              <strong className="text-amber-300">{selectedPeer.expected_harvest || 'Oct 2025'}</strong>
            </div>
            <div className="bg-slate-900 p-2.5 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-400 block mb-0.5">Soil Type</span>
              <span className="text-slate-200">{selectedPeer.soil_type || 'Red Laterite'}</span>
            </div>
            <div className="bg-slate-900 p-2.5 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-400 block mb-0.5">Water Source</span>
              <span className="text-slate-200">{selectedPeer.water_source || 'Borewell'}</span>
            </div>
            <div className="bg-slate-900 p-2.5 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-400 block mb-0.5">Yield</span>
              <span className="text-emerald-400 font-bold">{selectedPeer.yield_per_acre} Q/acre</span>
            </div>
            <div className="bg-slate-900 p-2.5 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-400 block mb-0.5">Selling Price</span>
              <span className="text-emerald-400 font-bold">₹{selectedPeer.selling_price?.toLocaleString()}/Q</span>
            </div>
          </div>

          {selectedPeer.contactable && !contactedPeers[selectedPeer.id] && (
            <div className="text-right">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleRequestContact(selectedPeer.id)}
                disabled={contactingId === selectedPeer.id}
                className="text-[11px] bg-slate-900 text-emerald-300 border-emerald-500/40 hover:bg-emerald-950"
              >
                {contactingId === selectedPeer.id ? 'Connecting…' : 'Request Contact Details'}
              </Button>
            </div>
          )}

          {contactedPeers[selectedPeer.id] && (
            <div className="bg-emerald-950/50 p-3 rounded-xl border border-emerald-500/30 text-xs space-y-1">
              <div className="text-emerald-300 font-bold">Contact Details Shared</div>
              <div className="text-slate-300">Phone: {contactedPeers[selectedPeer.id].phone}</div>
              <div className="text-slate-300">Email: {contactedPeers[selectedPeer.id].email}</div>
            </div>
          )}
        </div>
      )}

      {/* ── REGIONAL COUNTS BAR ── */}
      {proof?.regions && proof.regions.length > 0 && !loading && (
        <div className="mx-4 mb-4 bg-slate-950/60 p-3.5 rounded-2xl border border-slate-800 space-y-2">
          <div className="flex justify-between items-center text-xs font-bold text-slate-400">
            <span>Regional Distribution ({proof.total_districts || proof.regions.length} Districts)</span>
            <span className="text-emerald-400">{proof.total_farmers || cohortCount} total</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {proof.regions.map((reg) => (
              <span
                key={reg.district}
                className="inline-flex items-center gap-1.5 bg-slate-900 border border-slate-800 px-2.5 py-1 rounded-xl text-xs text-slate-300"
              >
                <strong className="text-white">{reg.district}:</strong>
                <span className="text-emerald-400 font-extrabold">{reg.farmer_count}</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* ── COHORT STATS ── */}
      {proof?.available && !loading && (
        <div className="mx-4 mb-4 grid grid-cols-2 sm:grid-cols-4 gap-2 bg-slate-950/60 p-3.5 rounded-2xl border border-slate-800 text-xs">
          <div>
            <span className="text-[10px] text-slate-400 block font-bold uppercase mb-0.5">Season</span>
            <span className="font-extrabold text-amber-300">{proof.season || 'Kharif 2025'}</span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 block font-bold uppercase mb-0.5">Avg Yield</span>
            <span className="font-extrabold text-emerald-400">{proof.average_yield_quintals_per_acre} Q/acre</span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 block font-bold uppercase mb-0.5">Avg Price</span>
            <span className="font-extrabold text-emerald-400">₹{proof.average_selling_price_per_quintal?.toLocaleString()}/Q</span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 block font-bold uppercase mb-0.5">Avg Net</span>
            <span className="font-extrabold text-emerald-400">₹{proof.average_net_realization_per_acre?.toLocaleString()}/acre</span>
          </div>
        </div>
      )}

      {/* ── DISCLAIMER FOOTER ── */}
      <div className="px-6 pb-5 flex items-center gap-2 text-[10px] text-slate-500">
        <IconShield size={12} className="text-slate-500 shrink-0" />
        <span>
          Privacy Protected · {proof?.data_source || 'Registered Farmer Network'}
        </span>
      </div>
    </div>
  );
}
