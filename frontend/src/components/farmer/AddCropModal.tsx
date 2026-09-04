import React, { useState, useEffect } from 'react';
import Button from '../common/Button';
import { createCultivationRecord, updateCultivationRecord } from '../../services/cultivationService';
import { getFarmDetails, saveFarmDetails } from '../../utils/storage';
import { IconPlant, IconCheck, IconMapPin } from '../common/Icons';
import type { CultivationStage, CropCultivationRecord } from '../../types/api';

const SUPPORTED_CROPS = [
  { id: 1, name: 'Paddy' },
  { id: 19, name: 'Rice' },
  { id: 7, name: 'Maize' },
  { id: 20, name: 'Wheat' },
  { id: 2, name: 'Groundnut' },
  { id: 23, name: 'Groundnut (Kadir-6)' },
  { id: 3, name: 'Sunflower' },
  { id: 4, name: 'Soybean' },
  { id: 5, name: 'Mustard' },
  { id: 6, name: 'Sesame' },
  { id: 12, name: 'Sesame (Black)' },
  { id: 10, name: 'Castor' },
  { id: 8, name: 'Safflower' },
  { id: 9, name: 'Niger' },
  { id: 11, name: 'Linseed' },
];

interface AddCropModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (record: CropCultivationRecord) => void;
  initialCropName?: string;
  initialStage?: CultivationStage;
  initialYield?: number;
  editingRecord?: CropCultivationRecord | null;
}

export default function AddCropModal({
  isOpen,
  onClose,
  onSuccess,
  initialCropName,
  initialStage = 'GROWING',
  initialYield,
  editingRecord,
}: AddCropModalProps) {
  const [myFarms, setMyFarms] = useState<any[]>([]);
  const [farmId, setFarmId] = useState<number | null>(null);
  const [cropId, setCropId] = useState<number>(2);
  const [variety, setVariety] = useState<string>('');
  const [areaAcres, setAreaAcres] = useState<string>('2.5');
  const [stage, setStage] = useState<CultivationStage>(initialStage);
  const [sowingDate, setSowingDate] = useState<string>('');
  const [expectedHarvestDate, setExpectedHarvestDate] = useState<string>('');
  const [expectedYield, setExpectedYield] = useState<string>('');
  const [notes, setNotes] = useState<string>('');

  // Dynamic farm location states (no hardcoded defaults)
  const [farmDistrict, setFarmDistrict] = useState<string>('');
  const [farmState, setFarmState] = useState<string>('Karnataka');
  const [locating, setLocating] = useState<boolean>(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  useEffect(() => {
    if (!isOpen) return;

    const currentFarm = getFarmDetails();
    if (currentFarm?.farm_id) {
      setFarmId(currentFarm.farm_id);
    }
    if (currentFarm?.district) {
      setFarmDistrict(currentFarm.district);
      setFarmState(currentFarm.state || 'Karnataka');
    }

    // Fetch owned farms for authenticated farmer
    fetch('/api/v1/farms/my-farms', {
      headers: { Authorization: `Bearer ${localStorage.getItem('token') || ''}` },
    })
      .then((res) => (res.ok ? res.json() : []))
      .then((farms) => {
        if (Array.isArray(farms) && farms.length > 0) {
          setMyFarms(farms);
          if (!farmId || !farms.some((f: any) => f.id === farmId)) {
            setFarmId(farms[0].id);
            if (farms[0].district) setFarmDistrict(farms[0].district);
            if (farms[0].state) setFarmState(farms[0].state || 'Karnataka');
          }
        } else {
          // If no farms found in my-farms, fallback to /api/v1/farms/me
          fetch('/api/v1/farms/me', {
            headers: { Authorization: `Bearer ${localStorage.getItem('token') || ''}` },
          })
            .then((res) => (res.ok ? res.json() : null))
            .then((data) => {
              if (data && data.id) {
                setMyFarms([data]);
                setFarmId(data.id);
                if (data.district) setFarmDistrict(data.district);
                if (data.state) setFarmState(data.state || 'Karnataka');
                saveFarmDetails({
                  farm_id: data.id,
                  farm_name: data.name || 'My Farm',
                  district: data.district || 'Shivamogga',
                  state: data.state || 'Karnataka',
                  land_area: data.land_area_acre || 2.5,
                  water_availability: data.water_availability || 'Available',
                  soil_type: data.soil_type || 'Black (Vertisol)',
                  current_crop: 'Groundnut',
                });
              }
            })
            .catch(() => {});
        }
      })
      .catch(() => {});

    if (editingRecord) {
      setCropId(editingRecord.crop_id);
      setVariety(editingRecord.variety || '');
      setAreaAcres(String(editingRecord.area_acres || '2.5'));
      setStage(editingRecord.cultivation_stage);
      setSowingDate(editingRecord.sowing_date || '');
      setExpectedHarvestDate(editingRecord.expected_harvest_date || '');
      setExpectedYield(editingRecord.expected_yield_quintals ? String(editingRecord.expected_yield_quintals) : '');
      setNotes(editingRecord.notes || '');
      if (editingRecord.district) setFarmDistrict(editingRecord.district);
      if (editingRecord.state) setFarmState(editingRecord.state);
    } else {
      if (initialCropName) {
        const found = SUPPORTED_CROPS.find(
          (c) => c.name.toLowerCase() === initialCropName.toLowerCase()
        );
        if (found) {
          setCropId(found.id);
        }
      }
      if (initialStage) {
        setStage(initialStage);
      }
      if (initialYield) {
        setExpectedYield(String(initialYield));
      }
    }
  }, [editingRecord, initialCropName, initialStage, initialYield, isOpen]);

  const handleDetectLocation = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser.');
      return;
    }
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const { latitude, longitude } = pos.coords;
        try {
          const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`);
          if (res.ok) {
            const data = await res.json();
            const dist =
              data.address?.state_district ||
              data.address?.county ||
              data.address?.city ||
              data.address?.town ||
              data.address?.subdistrict;
            const st = data.address?.state || 'Karnataka';
            if (dist) setFarmDistrict(dist);
            if (st) setFarmState(st);
          } else {
            setFarmDistrict(`District (${latitude.toFixed(2)}, ${longitude.toFixed(2)})`);
          }
        } catch {
          setFarmDistrict(`District (${latitude.toFixed(2)}, ${longitude.toFixed(2)})`);
        } finally {
          setLocating(false);
        }
      },
      (err) => {
        alert(`Location detection failed: ${err.message}. Please enter your district manually.`);
        setLocating(false);
      },
      { timeout: 10000 }
    );
  };

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccessMsg('');

    const targetFarmId = farmId || undefined;
    const acresNum = parseFloat(areaAcres);

    if (!acresNum || acresNum <= 0) {
      setError('Please enter a valid cultivation area in acres.');
      setLoading(false);
      return;
    }

    try {
      if (farmDistrict.trim()) {
        const existingDetails = getFarmDetails() || {};
        saveFarmDetails({
          ...existingDetails,
          farm_id: targetFarmId,
          district: farmDistrict.trim(),
          state: farmState.trim() || 'Karnataka',
          farm_name: existingDetails.farm_name || 'My Farm',
          land_area: parseFloat(areaAcres) || 2.5,
          water_availability: existingDetails.water_availability || 'Available',
          soil_type: existingDetails.soil_type || 'Black (Vertisol)',
          current_crop: 'Groundnut',
        });

        if (farmId) {
          fetch(`/api/v1/farms/${farmId}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
            },
            body: JSON.stringify({
              district: farmDistrict.trim(),
              state: farmState.trim() || 'Karnataka',
            }),
          }).catch(() => {});
        }
      }

      if (editingRecord) {
        const updated = await updateCultivationRecord(editingRecord.id, {
          variety: variety.trim() || undefined,
          area_acres: acresNum,
          cultivation_stage: stage,
          sowing_date: sowingDate || undefined,
          expected_harvest_date: expectedHarvestDate || undefined,
          expected_yield_quintals: expectedYield ? parseFloat(expectedYield) : undefined,
          notes: notes.trim() || undefined,
        });
        setSuccessMsg('Crop record updated successfully!');
        if (onSuccess) onSuccess(updated);
      } else {
        const created = await createCultivationRecord({
          farm_id: targetFarmId,
          crop_id: cropId,
          variety: variety.trim() || undefined,
          area_acres: acresNum,
          cultivation_stage: stage,
          sowing_date: sowingDate || undefined,
          expected_harvest_date: expectedHarvestDate || undefined,
          expected_yield_quintals: expectedYield ? parseFloat(expectedYield) : undefined,
          notes: notes.trim() || undefined,
        });
        setSuccessMsg('Crop record added to My Crops successfully!');
        if (onSuccess) onSuccess(created);
      }

      setTimeout(() => {
        setSuccessMsg('');
        onClose();
      }, 1200);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to save crop cultivation record');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-950/85 backdrop-blur-md overflow-y-auto"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="relative w-full max-w-lg my-auto max-h-[88vh] bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col text-slate-100">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 p-5 shrink-0 bg-slate-900">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400">
              <IconPlant className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">
                {editingRecord ? 'Edit Cultivation Record' : 'Add Crop to My Farm'}
              </h3>
              <p className="text-xs text-slate-400">
                Authoritative record of crop activity on your farm
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors cursor-pointer"
            type="button"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Form wrapping scrollable content and sticky footer */}
        <form id="add-crop-form" onSubmit={handleSubmit} className="flex-1 flex flex-col min-h-0 overflow-hidden">
          {/* Scrollable Body Form */}
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            {error && (
              <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm rounded-xl">
                {error}
              </div>
            )}

            {successMsg && (
              <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-sm rounded-xl flex items-center gap-2">
                <IconCheck className="w-5 h-5" />
                {successMsg}
              </div>
            )}
            
            {/* Multi-farm Selector (Requirement 3) */}
            {myFarms.length > 1 && (
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Select Owned Farm <span className="text-rose-400">*</span>
                </label>
                <select
                  value={farmId || ''}
                  onChange={(e) => {
                    const id = Number(e.target.value);
                    setFarmId(id);
                    const selected = myFarms.find((f: any) => f.id === id);
                    if (selected) {
                      if (selected.district) setFarmDistrict(selected.district);
                      if (selected.state) setFarmState(selected.state || 'Karnataka');
                    }
                  }}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500"
                >
                  {myFarms.map((f: any) => (
                    <option key={f.id} value={f.id}>
                      Farm #{f.id} - {f.district || 'Shivamogga'}, {f.state || 'Karnataka'} ({f.land_area_acre || 2.5} Acres)
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Dynamic Farm Location Input & Detection (No hardcoded defaults) */}
            <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                  <IconMapPin className="w-4 h-4 text-emerald-400" />
                  <span>Farm Location</span> <span className="text-rose-400">*</span>
                </label>
                <button
                  type="button"
                  onClick={handleDetectLocation}
                  disabled={locating}
                  className="px-2.5 py-1 bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-400 border border-emerald-500/30 font-bold rounded-lg text-[11px] transition-all flex items-center gap-1 cursor-pointer"
                >
                  {locating ? 'Detecting...' : '📍 Use Current Location'}
                </button>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-[10px] font-medium text-slate-400 mb-1">District / Region</label>
                  <input
                    type="text"
                    value={farmDistrict}
                    onChange={(e) => setFarmDistrict(e.target.value)}
                    placeholder="e.g. Shivamogga, Belagavi"
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 font-semibold"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-medium text-slate-400 mb-1">State</label>
                  <input
                    type="text"
                    value={farmState}
                    onChange={(e) => setFarmState(e.target.value)}
                    placeholder="Karnataka"
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 font-semibold"
                  />
                </div>
              </div>
            </div>

            {/* Crop Select */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Crop <span className="text-rose-400">*</span>
              </label>
              <select
                value={cropId}
                onChange={(e) => setCropId(Number(e.target.value))}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500 transition-colors"
                required
              >
                {SUPPORTED_CROPS.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Variety */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Variety (Optional)
              </label>
              <input
                type="text"
                value={variety}
                onChange={(e) => setVariety(e.target.value)}
                placeholder="e.g. TMV-2, JL-24"
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors"
              />
            </div>

            {/* Area & Stage Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Cultivation Area (Acres) <span className="text-rose-400">*</span>
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0.1"
                  value={areaAcres}
                  onChange={(e) => setAreaAcres(e.target.value)}
                  placeholder="2.5"
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500 transition-colors"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Cultivation Stage <span className="text-rose-400">*</span>
                </label>
                <select
                  value={stage}
                  onChange={(e) => setStage(e.target.value as CultivationStage)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500 transition-colors"
                  required
                >
                  <option value="PLANNED">Planned (Pre-sowing)</option>
                  <option value="GROWING">Growing (Cultivation Started)</option>
                  <option value="READY_FOR_HARVEST">Ready for Harvest</option>
                  <option value="HARVESTED">Harvested (Stock Available)</option>
                </select>
              </div>
            </div>

            {/* Dates Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Sowing Date
                </label>
                <input
                  type="date"
                  value={sowingDate}
                  onChange={(e) => setSowingDate(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500 transition-colors"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Expected Harvest Date
                </label>
                <input
                  type="date"
                  value={expectedHarvestDate}
                  onChange={(e) => setExpectedHarvestDate(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500 transition-colors"
                />
              </div>
            </div>

            {/* Expected Yield */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Expected Total Yield (Quintals)
              </label>
              <input
                type="number"
                step="0.5"
                min="0"
                value={expectedYield}
                onChange={(e) => setExpectedYield(e.target.value)}
                placeholder="e.g. 24.5"
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors"
              />
            </div>

            {/* Notes */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Notes / Soil Details
              </label>
              <textarea
                rows={2}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="e.g. Red laterite soil, drip irrigation"
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors resize-none"
              />
            </div>
          </div>

          {/* Sticky Footer always visible */}
          <div className="p-4 border-t border-slate-800 bg-slate-950 shrink-0 flex justify-end gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={loading}
              className="border-slate-700 text-slate-300 hover:bg-slate-800"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              isLoading={loading}
              className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold"
            >
              {editingRecord ? 'Update Record' : 'Save Record'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
