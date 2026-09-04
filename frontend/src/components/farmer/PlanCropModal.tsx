import React, { useState } from 'react';
import Button from '../common/Button';
import { createFutureCropLot, createStockLot } from '../../services/api';
import { getFarmDetails } from '../../utils/storage';
import { IconPlant, IconCheck, IconPlus } from '../common/Icons';

interface PlanCropModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

const OILSEED_CROPS = [
  { id: 2, name: 'Groundnut' },
  { id: 3, name: 'Sunflower' },
  { id: 4, name: 'Soybean' },
  { id: 5, name: 'Mustard' },
  { id: 6, name: 'Sesame' },
  { id: 8, name: 'Safflower' },
  { id: 9, name: 'Niger' },
  { id: 10, name: 'Castor' },
  { id: 11, name: 'Linseed' },
];

export default function PlanCropModal({ isOpen, onClose, onSuccess }: PlanCropModalProps) {
  const farm = getFarmDetails();
  const [cropStage, setCropStage] = useState<'PLANNING' | 'GROWING' | 'READY_FOR_HARVEST' | 'HARVESTED'>('PLANNING');
  const [cropId, setCropId] = useState<number>(2);
  const [areaAcres, setAreaAcres] = useState<string>('2.5');
  const [quantity, setQuantity] = useState<string>('30');
  const [harvestDate, setHarvestDate] = useState<string>('2026-10-25');
  const [targetPrice, setTargetPrice] = useState<string>('6400');
  const [qualityGrade, setQualityGrade] = useState<string>('A');
  const [growthStageName, setGrowthStageName] = useState<string>('Pod Filling');
  const [notes, setNotes] = useState<string>('');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccessMsg('');

    const farmId = farm?.farm_id || 1;
    const qtyNum = parseFloat(quantity);
    const acresNum = parseFloat(areaAcres) || 2.5;

    if (!qtyNum || qtyNum <= 0) {
      setError('Please enter a valid quantity in quintals.');
      setLoading(false);
      return;
    }

    try {
      if (cropStage === 'HARVESTED') {
        // Create actual post-harvest StockLot (keeps expected vs actual quantity strictly separate)
        await createStockLot({
          crop_id: cropId,
          farm_id: farmId,
          actual_quantity_quintals: qtyNum,
          actual_harvest_date: harvestDate || '2025-10-15',
          asking_price_per_quintal: targetPrice ? parseFloat(targetPrice) : 6200,
          quality_grade: qualityGrade || 'A',
        });
        setSuccessMsg('Harvested Stock Lot published to Marketplace!');
      } else {
        // Create FutureCropLot for Planning, Currently Growing, or Ready for Harvest
        const sowingDate = '2025-06-15';
        const harvestEnd = harvestDate || '2025-10-25';

        await createFutureCropLot({
          crop_id: cropId,
          farm_id: farmId,
          planned_acres: acresNum,
          expected_quantity_quintals: qtyNum,
          asking_price_per_quintal: targetPrice ? parseFloat(targetPrice) : undefined,
          planned_sowing_date: sowingDate,
          expected_harvest_start: harvestDate || '2025-10-15',
          expected_harvest_end: harvestEnd,
          quality_grade: qualityGrade || 'A',
          status: 'OPEN',
        });
        setSuccessMsg(`Crop recorded in Marketplace under stage: ${cropStage.replace('_', ' ')}!`);
      }

      setTimeout(() => {
        setLoading(false);
        setSuccessMsg('');
        onSuccess?.();
        onClose();
      }, 1000);
    } catch (err: any) {
      setError(err?.message || 'Failed to add crop entry to Marketplace. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 shadow-2xl space-y-5 text-slate-100">
        <div className="flex justify-between items-center border-b border-slate-800 pb-3">
          <div>
            <div className="inline-flex items-center gap-1.5 text-[10px] font-black text-emerald-400 uppercase tracking-wider bg-emerald-950 px-2.5 py-0.5 rounded-full border border-emerald-500/30 mb-1">
              <IconPlus size={12} />
              <span>Add Crop to Marketplace</span>
            </div>
            <h3 className="text-xl font-black text-white">List Future Crop Availability & Procurement Lot</h3>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white text-lg font-bold p-1 rounded-lg transition-colors"
            aria-label="Close modal"
          >
            ✕
          </button>
        </div>

        {/* 4-Stage Selector */}
        <div className="space-y-2">
          <label className="block text-xs font-extrabold text-slate-300 uppercase tracking-wider">Select Crop Stage</label>
          <div className="grid grid-cols-2 gap-2">
            {[
              { id: 'PLANNING', label: '1. Planning to Grow', desc: 'Pre-sowing planned lot' },
              { id: 'GROWING', label: '2. Currently Growing', desc: 'Active standing crop' },
              { id: 'READY_FOR_HARVEST', label: '3. Ready for Harvest', desc: 'Harvest expected soon' },
              { id: 'HARVESTED', label: '4. Already Harvested', desc: 'Actual available stock' },
            ].map((stage) => (
              <button
                key={stage.id}
                type="button"
                onClick={() => setCropStage(stage.id as any)}
                className={`p-3 rounded-xl border text-left transition-all ${
                  cropStage === stage.id
                    ? 'bg-amber-500/20 border-amber-500 text-amber-300 shadow-md ring-1 ring-amber-400/50'
                    : 'bg-slate-950 border-slate-800 text-slate-400 hover:bg-slate-850 hover:text-slate-200'
                }`}
              >
                <div className="font-extrabold text-xs">{stage.label}</div>
                <div className="text-[10px] opacity-75 mt-0.5">{stage.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="p-3 bg-red-950/80 border border-red-500/40 rounded-xl text-xs text-red-200 font-medium">
            {error}
          </div>
        )}

        {successMsg && (
          <div className="p-3 bg-emerald-950/80 border border-emerald-500/40 rounded-xl text-xs text-emerald-200 font-bold">
            {successMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block font-extrabold text-slate-300 mb-1">Select Oilseed Crop</label>
            <select
              value={cropId}
              onChange={(e) => setCropId(Number(e.target.value))}
              className="w-full p-3 bg-slate-950 border border-slate-800 rounded-xl font-bold text-white focus:ring-2 focus:ring-amber-500"
            >
              {OILSEED_CROPS.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-extrabold text-slate-300 mb-1">
                {cropStage === 'HARVESTED' ? 'Harvested Quantity (Q)' : 'Expected Quantity (Q)'}
              </label>
              <input
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                placeholder="e.g. 30"
                className="w-full p-3 bg-slate-950 border border-slate-800 rounded-xl font-bold text-white focus:ring-2 focus:ring-amber-500"
                required
              />
            </div>

            <div>
              <label className="block font-extrabold text-slate-300 mb-1">
                {cropStage === 'HARVESTED' ? 'Selling Price (₹ / Q)' : 'Target Price (₹ / Q)'}
              </label>
              <input
                type="number"
                value={targetPrice}
                onChange={(e) => setTargetPrice(e.target.value)}
                placeholder="e.g. 6400"
                className="w-full p-3 bg-slate-950 border border-slate-800 rounded-xl font-bold text-white focus:ring-2 focus:ring-amber-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-extrabold text-slate-300 mb-1">Land Area (Acres)</label>
              <input
                type="text"
                value={areaAcres}
                onChange={(e) => setAreaAcres(e.target.value)}
                placeholder="e.g. 2.5"
                className="w-full p-3 bg-slate-950 border border-slate-800 rounded-xl font-bold text-white focus:ring-2 focus:ring-amber-500"
              />
            </div>

            <div>
              <label className="block font-extrabold text-slate-300 mb-1">
                {cropStage === 'HARVESTED' ? 'Actual Harvest Date' : 'Expected Harvest Date'}
              </label>
              <input
                type="date"
                value={harvestDate}
                onChange={(e) => setHarvestDate(e.target.value)}
                className="w-full p-3 bg-slate-950 border border-slate-800 rounded-xl font-bold text-white focus:ring-2 focus:ring-amber-500"
                required
              />
            </div>
          </div>

          {cropStage === 'GROWING' && (
            <div>
              <label className="block font-extrabold text-slate-300 mb-1">Current Growth Stage</label>
              <input
                type="text"
                value={growthStageName}
                onChange={(e) => setGrowthStageName(e.target.value)}
                placeholder="e.g. Flowering, Pod Filling, Vegetative"
                className="w-full p-3 bg-slate-950 border border-slate-800 rounded-xl font-bold text-white focus:ring-2 focus:ring-amber-500"
              />
            </div>
          )}

          {cropStage === 'HARVESTED' && (
            <div>
              <label className="block font-extrabold text-slate-300 mb-1">Quality Grade</label>
              <select
                value={qualityGrade}
                onChange={(e) => setQualityGrade(e.target.value)}
                className="w-full p-3 bg-slate-950 border border-slate-800 rounded-xl font-bold text-white focus:ring-2 focus:ring-amber-500"
              >
                <option value="A">Grade A (Premium / High Oil Content)</option>
                <option value="B">Grade B (Standard Market Quality)</option>
                <option value="C">Grade C (Commercial Processing)</option>
              </select>
            </div>
          )}

          <div>
            <label className="block font-extrabold text-slate-300 mb-1">Additional Notes</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={2}
              placeholder="e.g. Drip irrigated plot, ready for direct buyer pickup"
              className="w-full p-3 bg-slate-950 border border-slate-800 rounded-xl font-bold text-white focus:ring-2 focus:ring-amber-500"
            />
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-slate-800">
            <Button type="button" variant="outline" onClick={onClose} disabled={loading} className="bg-slate-950 text-slate-300 border-slate-800">
              Cancel
            </Button>
            <Button type="submit" variant="primary" isLoading={loading} className="bg-amber-500 text-slate-950 font-black hover:bg-amber-400">
              Publish to Marketplace
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
