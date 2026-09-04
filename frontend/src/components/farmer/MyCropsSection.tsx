import React, { useState, useEffect } from 'react';
import Button from '../common/Button';
import Badge from '../common/Badge';
import {
  getCultivationRecords,
  updateCultivationRecord,
  deleteCultivationRecord,
  recordHarvest,
} from '../../services/cultivationService';
import AddCropModal from './AddCropModal';
import {
  IconPlant,
  IconPlus,
  IconCheck,
} from '../common/Icons';

import type { CropCultivationRecord, CultivationStage } from '../../types/api';

export default function MyCropsSection() {
  const [records, setRecords] = useState<CropCultivationRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const [isAddModalOpen, setIsAddModalOpen] = useState<boolean>(false);
  const [editingRecord, setEditingRecord] = useState<CropCultivationRecord | null>(null);

  // Harvest modal state
  const [harvestingRecord, setHarvestingRecord] = useState<CropCultivationRecord | null>(null);
  const [actualQty, setActualQty] = useState<string>('');
  const [harvestLoading, setHarvestLoading] = useState<boolean>(false);

  const fetchRecords = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getCultivationRecords();
      setRecords(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to load cultivation records');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, []);

  const handleStageChange = async (recordId: number, newStage: CultivationStage) => {
    try {
      const updated = await updateCultivationRecord(recordId, { cultivation_stage: newStage });
      setRecords((prev) => prev.map((r) => (r.id === recordId ? updated : r)));
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to update cultivation stage');
    }
  };

  const handleRecordHarvestSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!harvestingRecord) return;
    const qty = parseFloat(actualQty);
    if (!qty || qty <= 0) {
      alert('Please enter a valid harvest quantity in quintals');
      return;
    }
    setHarvestLoading(true);
    try {
      const updated = await recordHarvest(harvestingRecord.id, {
        actual_harvest_quantity_quintals: qty,
      });
      setRecords((prev) => prev.map((r) => (r.id === harvestingRecord.id ? updated : r)));
      setHarvestingRecord(null);
      setActualQty('');
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to record harvest');
    } finally {
      setHarvestLoading(false);
    }
  };

  const handleDelete = async (recordId: number) => {
    if (!window.confirm('Are you sure you want to remove this crop record?')) return;
    try {
      await deleteCultivationRecord(recordId);
      setRecords((prev) => prev.filter((r) => r.id !== recordId));
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to delete record');
    }
  };

  const getStageBadgeVariant = (stage: CultivationStage) => {
    switch (stage) {
      case 'PLANNED':
        return 'info';
      case 'GROWING':
        return 'success';
      case 'READY_FOR_HARVEST':
        return 'warning';
      case 'HARVESTED':
        return 'neutral';
      default:
        return 'neutral';
    }
  };

  return (
    <div className="bg-slate-900/90 backdrop-blur-2xl rounded-3xl border border-slate-800 shadow-2xl p-5 sm:p-6 space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <IconPlant className="w-6 h-6 text-emerald-400" />
            <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight">
              My Farm Profile • My Crops
            </h2>
          </div>
          <p className="text-xs text-slate-400">
            Authoritative crop cultivation records registered on your farm profile
          </p>
        </div>

        <button
          type="button"
          onClick={() => {
            setEditingRecord(null);
            setIsAddModalOpen(true);
          }}
          className="px-4 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-xs rounded-xl shadow-lg flex items-center gap-2 cursor-pointer transition-all hover:scale-105"
        >
          <IconPlus size={16} />
          <span>+ Add Crop</span>
        </button>
      </div>

      {loading ? (
        <div className="py-8 text-center text-slate-400 text-xs flex items-center justify-center gap-2">
          <div className="w-4 h-4 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          <span>Loading cultivation records...</span>
        </div>
      ) : error ? (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-2xl text-rose-300 text-xs">
          {error}
        </div>
      ) : records.length === 0 ? (
        /* Empty State */
        <div className="py-10 text-center space-y-3 bg-slate-950/60 rounded-2xl border border-slate-800/80 p-6">
          <div className="w-12 h-12 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mx-auto text-emerald-400">
            <IconPlant className="w-6 h-6" />
          </div>
          <h3 className="text-base font-extrabold text-white">No crops added yet.</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Add your current or planned cultivation activity to keep your farm record authoritative and visible to regional buyer network.
          </p>
          <button
            type="button"
            onClick={() => {
              setEditingRecord(null);
              setIsAddModalOpen(true);
            }}
            className="mt-2 inline-flex items-center gap-2 px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-xs rounded-xl shadow-md transition-all"
          >
            <IconPlus size={14} />
            <span>+ Add Crop</span>
          </button>
        </div>
      ) : (
        /* Crops List */
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {records.map((rec) => (
            <div
              key={rec.id}
              className="bg-slate-950/80 border border-slate-800 hover:border-slate-700 rounded-2xl p-4 space-y-3 transition-all"
            >
              <div className="flex justify-between items-start">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-lg font-black text-white">{rec.crop_name}</h3>
                    {rec.variety && (
                      <span className="text-xs text-slate-400 bg-slate-800 px-2 py-0.5 rounded-md">
                        {rec.variety}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {rec.district ? `${rec.district}, ${rec.state || 'Karnataka'}` : 'Authoritative Farm Location'}
                  </p>
                </div>

                <Badge variant={getStageBadgeVariant(rec.cultivation_stage)}>
                  {rec.cultivation_stage.replace('_', ' ')}
                </Badge>
              </div>

              {/* Metrics */}
              <div className="grid grid-cols-2 gap-2 text-xs bg-slate-900/60 p-3 rounded-xl border border-slate-800/80">
                <div>
                  <span className="text-slate-400 block text-[10px] font-bold uppercase">Area</span>
                  <span className="text-slate-200 font-extrabold">{rec.area_acres} Acres</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] font-bold uppercase">Evidence</span>
                  <span className="text-emerald-400 font-bold">{rec.evidence_status.replace('_', ' ')}</span>
                </div>
                {rec.expected_yield_quintals != null && (
                  <div>
                    <span className="text-slate-400 block text-[10px] font-bold uppercase">Expected Yield</span>
                    <span className="text-slate-200 font-bold">{rec.expected_yield_quintals} Quintals</span>
                  </div>
                )}
                {rec.actual_harvest_quantity_quintals != null && (
                  <div>
                    <span className="text-slate-400 block text-[10px] font-bold uppercase">Actual Harvest</span>
                    <span className="text-emerald-400 font-bold">{rec.actual_harvest_quantity_quintals} Quintals</span>
                  </div>
                )}
                {rec.sowing_date && (
                  <div>
                    <span className="text-slate-400 block text-[10px] font-bold uppercase">Sowing Date</span>
                    <span className="text-slate-300">{rec.sowing_date}</span>
                  </div>
                )}
                {rec.expected_harvest_date && (
                  <div>
                    <span className="text-slate-400 block text-[10px] font-bold uppercase">Est. Harvest</span>
                    <span className="text-slate-300">{rec.expected_harvest_date}</span>
                  </div>
                )}
              </div>

              {rec.notes && (
                <p className="text-xs text-slate-400 italic bg-slate-900/40 p-2 rounded-lg border border-slate-800/50">
                  "{rec.notes}"
                </p>
              )}

              {/* Stage Transitions & Actions */}
              <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-800/80">
                <div className="flex items-center gap-1.5 text-xs">
                  <span className="text-slate-400 text-[10px] font-bold uppercase">Stage:</span>
                  <select
                    value={rec.cultivation_stage}
                    onChange={(e) => handleStageChange(rec.id, e.target.value as CultivationStage)}
                    className="bg-slate-800 border border-slate-700 text-white text-xs px-2 py-1 rounded-lg focus:outline-none focus:border-emerald-500"
                  >
                    <option value="PLANNED">PLANNED</option>
                    <option value="GROWING">GROWING</option>
                    <option value="READY_FOR_HARVEST">READY_FOR_HARVEST</option>
                    <option value="HARVESTED">HARVESTED</option>
                  </select>
                </div>

                <div className="flex items-center gap-2">
                  {rec.cultivation_stage !== 'HARVESTED' && (
                    <button
                      type="button"
                      onClick={() => setHarvestingRecord(rec)}
                      className="px-2.5 py-1 bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/30 font-bold text-xs rounded-lg transition-colors"
                    >
                      Record Harvest
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={() => {
                      setEditingRecord(rec);
                      setIsAddModalOpen(true);
                    }}
                    className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs rounded-lg transition-colors"
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    onClick={() => handleDelete(rec.id)}
                    className="px-2.5 py-1 bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 font-bold text-xs rounded-lg transition-colors"
                  >
                    Remove
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add / Edit Crop Modal */}
      <AddCropModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        editingRecord={editingRecord}
        onSuccess={() => fetchRecords()}
      />

      {/* Record Harvest Modal */}
      {harvestingRecord && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 max-w-md w-full text-slate-100 space-y-4">
            <h3 className="text-lg font-black text-white">
              Record Actual Harvest • {harvestingRecord.crop_name}
            </h3>
            <p className="text-xs text-slate-400">
              Preserves expected yield ({harvestingRecord.expected_yield_quintals || 'N/A'} Q) and updates status to HARVESTED.
            </p>

            <form onSubmit={handleRecordHarvestSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Actual Harvest Quantity (Quintals) *
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0.1"
                  value={actualQty}
                  onChange={(e) => setActualQty(e.target.value)}
                  placeholder="e.g. 21.5"
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                  required
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setHarvestingRecord(null)}
                >
                  Cancel
                </Button>
                <Button type="submit" variant="primary" size="sm" isLoading={harvestLoading}>
                  Save Harvest Quantity
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
