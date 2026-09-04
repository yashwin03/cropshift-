import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../common/Button';
import { createFutureCropLot, createStockLot, uploadQualityCertificate, publishFarmerStockLot } from '../../services/api';
import apiClient from '../../services/apiClient';
import { IconPlus } from '../common/Icons';
import type { Farm } from '../../types/api';

interface PlanCropModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

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

interface MarketPriceData {
  crop_id: number;
  crop_name: string;
  price: number | null;
  price_unit: string;
  market_name: string;
  price_date?: string | null;
  min_target_price: number | null;
  max_target_price: number | null;
  loading: boolean;
  error: string | null;
}

export default function PlanCropModal({ isOpen, onClose, onSuccess }: PlanCropModalProps) {
  let navigate: ReturnType<typeof useNavigate>;
  try {
    navigate = useNavigate();
  } catch {
    navigate = (() => {}) as any;
  }
  const [cropStage, setCropStage] = useState<'PLANNING' | 'GROWING' | 'READY_FOR_HARVEST' | 'HARVESTED'>('GROWING');
  const [cropId, setCropId] = useState<number>(2);
  const [areaAcres, setAreaAcres] = useState<string>('2.5');
  const [quantity, setQuantity] = useState<string>('30');
  const [harvestDate, setHarvestDate] = useState<string>(() => {
    const d = new Date();
    d.setMonth(d.getMonth() + 2);
    return d.toISOString().split('T')[0];
  });
  const [targetPrice, setTargetPrice] = useState<string>('6400');
  const [qualityGrade, setQualityGrade] = useState<string>('A');
  const [growthStageName, setGrowthStageName] = useState<string>('Pod Filling');
  const [notes, setNotes] = useState<string>('');

  const [marketPriceInfo, setMarketPriceInfo] = useState<MarketPriceData>({
    crop_id: 2,
    crop_name: 'Groundnut',
    price: null,
    price_unit: 'quintal',
    market_name: '',
    price_date: null,
    min_target_price: null,
    max_target_price: null,
    loading: false,
    error: null,
  });

  const [certFile, setCertFile] = useState<File | null>(null);
  const [certFileError, setCertFileError] = useState<string | null>(null);

  const [farms, setFarms] = useState<Farm[]>([]);
  const [selectedFarmId, setSelectedFarmId] = useState<number | null>(null);
  const [farmsLoading, setFarmsLoading] = useState<boolean>(true);
  const [farmsError, setFarmsError] = useState<string | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const handleCertFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCertFileError(null);
    setError('');
    const file = e.target.files?.[0];
    if (!file) return;

    const allowedExtensions = ['pdf', 'jpg', 'jpeg', 'png'];
    const ext = file.name.split('.').pop()?.toLowerCase() || '';
    const allowedMimeTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];

    if (!allowedExtensions.includes(ext) && !allowedMimeTypes.includes(file.type)) {
      setCertFileError('Invalid file type. Please upload a PDF, JPG, or PNG document.');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setCertFileError('File size exceeds 10MB limit. Please upload a smaller document.');
      return;
    }

    setCertFile(file);
  };

  const handleRemoveCertFile = () => {
    setCertFile(null);
    setCertFileError(null);
  };

  // Fetch Market Price & Target Range whenever cropId or selectedFarmId changes
  useEffect(() => {
    if (!isOpen || !cropId) return;
    let isMounted = true;
    setMarketPriceInfo((prev) => ({ ...prev, loading: true, error: null }));

    const url = `/api/v1/markets/${cropId}${selectedFarmId ? `?farm_id=${selectedFarmId}` : ''}`;
    apiClient.get<any>(url)
      .then((res) => {
        if (!isMounted) return;
        const data = res.data;
        if (data && data.price != null) {
          const p = Number(data.price);
          const minP = data.min_target_price != null ? Number(data.min_target_price) : Math.round(p * 0.95);
          const maxP = data.max_target_price != null ? Number(data.max_target_price) : Math.round(p * 1.05);

          setMarketPriceInfo({
            crop_id: data.crop_id || cropId,
            crop_name: data.crop_name || 'Selected Crop',
            price: p,
            price_unit: data.price_unit || 'quintal',
            market_name: data.market_name || 'APMC Market',
            price_date: data.price_date || null,
            min_target_price: minP,
            max_target_price: maxP,
            loading: false,
            error: null,
          });
          setTargetPrice(String(p));
        } else {
          setMarketPriceInfo({
            crop_id: cropId,
            crop_name: 'Selected Crop',
            price: null,
            price_unit: 'quintal',
            market_name: '',
            price_date: null,
            min_target_price: null,
            max_target_price: null,
            loading: false,
            error: 'Market price unavailable. Please try again.',
          });
        }
      })
      .catch(() => {
        if (!isMounted) return;
        setMarketPriceInfo({
          crop_id: cropId,
          crop_name: 'Selected Crop',
          price: null,
          price_unit: 'quintal',
          market_name: '',
          price_date: null,
          min_target_price: null,
          max_target_price: null,
          loading: false,
          error: 'Market price unavailable. Please try again.',
        });
      });

    return () => {
      isMounted = false;
    };
  }, [isOpen, cropId, selectedFarmId]);

  const priceNum = targetPrice ? parseFloat(targetPrice) : NaN;
  const priceValidationError = (() => {
    if (marketPriceInfo.loading) return null;
    if (marketPriceInfo.error) return marketPriceInfo.error;
    if (marketPriceInfo.min_target_price !== null && marketPriceInfo.max_target_price !== null) {
      if (!targetPrice || isNaN(priceNum)) {
        return 'Please enter a valid target price.';
      }
      if (priceNum < marketPriceInfo.min_target_price || priceNum > marketPriceInfo.max_target_price) {
        return `Target price must be between ₹${marketPriceInfo.min_target_price.toLocaleString()} and ₹${marketPriceInfo.max_target_price.toLocaleString()} per quintal based on today's market price.`;
      }
    }
    return null;
  })();


  useEffect(() => {
    if (!isOpen) return;
    let isMounted = true;
    setFarmsLoading(true);
    setFarmsError(null);

    // 1. Fetch authenticated farmer's farms
    apiClient.get<Farm[] | { farms: Farm[] } | null>('/api/v1/farms/my-farms')
      .then((res) => {
        if (!isMounted) return;
        const raw = res.data;
        const list: Farm[] = Array.isArray(raw)
          ? raw
          : Array.isArray((raw as any)?.farms)
          ? (raw as any).farms
          : [];
        setFarms(list);
        if (list.length > 0) {
          setSelectedFarmId(list[0].id);
        } else {
          // Fallback check on /api/v1/farms/me
          return apiClient.get<Farm>('/api/v1/farms/me').then((meRes) => {
            if (!isMounted) return;
            if (meRes.data && meRes.data.id) {
              setFarms([meRes.data]);
              setSelectedFarmId(meRes.data.id);
            } else {
              setFarms([]);
              setSelectedFarmId(null);
              setFarmsError('Please complete your Farm Profile before adding a crop.');
            }
          });
        }
      })
      .catch(() => {
        // Fallback to single farm lookup
        apiClient.get<Farm>('/api/v1/farms/me')
          .then((res) => {
            if (!isMounted) return;
            if (res.data && res.data.id) {
              setFarms([res.data]);
              setSelectedFarmId(res.data.id);
            } else {
              setFarms([]);
              setSelectedFarmId(null);
              setFarmsError('Please complete your Farm Profile before adding a crop.');
            }
          })
          .catch(() => {
            if (!isMounted) return;
            setFarms([]);
            setSelectedFarmId(null);
            setFarmsError('Please complete your Farm Profile before adding a crop.');
          });
      })
      .finally(() => {
        if (isMounted) setFarmsLoading(false);
      });

    // 2. Safely prefill crop fields from existing cultivation records if available
    apiClient.get<any[]>('/api/v1/cultivation-records')
      .then((recRes) => {
        if (!isMounted) return;
        if (Array.isArray(recRes.data) && recRes.data.length > 0) {
          const latestRec = recRes.data[0];
          if (latestRec.crop_id) setCropId(latestRec.crop_id);
          if (latestRec.area_acres) setAreaAcres(String(latestRec.area_acres));
          if (latestRec.expected_yield_quintals) setQuantity(String(latestRec.expected_yield_quintals));
          if (latestRec.expected_harvest_date) setHarvestDate(latestRec.expected_harvest_date);
          if (latestRec.cultivation_stage) {
            const st = latestRec.cultivation_stage;
            if (st === 'PLANNED') setCropStage('PLANNING');
            else if (st === 'GROWING') setCropStage('GROWING');
            else if (st === 'READY_FOR_HARVEST') setCropStage('READY_FOR_HARVEST');
            else if (st === 'HARVESTED') setCropStage('HARVESTED');
          }
        }
      })
      .catch(() => {});

    return () => {
      isMounted = false;
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccessMsg('');

    const safeFarms = Array.isArray(farms) ? farms : [];
    if (farmsError || safeFarms.length === 0) {
      setError('Please complete your Farm Profile before adding a crop.');
      setLoading(false);
      return;
    }

    const farmId = selectedFarmId || safeFarms[0]?.id;
    if (!farmId) {
      setError('No valid farm selected. Please complete your Farm Profile.');
      setLoading(false);
      return;
    }

    const qtyNum = parseFloat(quantity);
    const acresNum = parseFloat(areaAcres) || 2.5;
    const priceNum = targetPrice ? parseFloat(targetPrice) : undefined;

    if (isNaN(qtyNum) || qtyNum <= 0) {
      setError('Please enter a valid positive quantity in quintals.');
      setLoading(false);
      return;
    }

    if (isNaN(acresNum) || acresNum <= 0) {
      setError('Please enter a valid land area in acres.');
      setLoading(false);
      return;
    }

    if (priceValidationError) {
      setError(priceValidationError);
      setLoading(false);
      return;
    }

    if (priceNum !== undefined && (isNaN(priceNum) || priceNum <= 0)) {
      setError('Price per quintal must be greater than 0.');
      setLoading(false);
      return;
    }


    try {
      if (cropStage === 'HARVESTED') {
        if (!certFile) {
          setError('Quality certificate is required for already harvested crops.');
          setLoading(false);
          return;
        }

        // Direct physical StockLot
        const stockLot = await createStockLot({
          crop_id: cropId,
          farm_id: farmId,
          actual_quantity_quintals: qtyNum,
          actual_harvest_date: harvestDate || new Date().toISOString().split('T')[0],
          asking_price_per_quintal: priceNum || 6200,
          quality_grade: qualityGrade || 'A',
        });

        if (stockLot?.id) {
          await uploadQualityCertificate(stockLot.id, certFile);
          await publishFarmerStockLot(stockLot.id);
        }

        setSuccessMsg('Harvested Stock Lot published to Marketplace with Quality Certificate Uploaded!');
      } else {
        // Standing / Planned FutureCropLot
        const sowingDate = new Date();
        sowingDate.setMonth(sowingDate.getMonth() - 1);
        const sowingStr = sowingDate.toISOString().split('T')[0];
        const harvestEnd = harvestDate || new Date().toISOString().split('T')[0];

        await createFutureCropLot({
          crop_id: cropId,
          farm_id: farmId,
          planned_acres: acresNum,
          expected_quantity_quintals: qtyNum,
          asking_price_per_quintal: priceNum,
          planned_sowing_date: sowingStr,
          expected_harvest_start: harvestEnd,
          expected_harvest_end: harvestEnd,
          quality_grade: qualityGrade || 'A',
          status: 'OPEN',
        });
        setSuccessMsg(`Crop recorded in Marketplace under stage: ${cropStage.replace(/_/g, ' ')}!`);
      }

      setTimeout(() => {
        setLoading(false);
        setSuccessMsg('');
        onSuccess?.();
        onClose();
      }, 1000);
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || 'Failed to add crop entry to Marketplace. Please try again.';
      setError(msg);
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
      <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-xl w-full my-auto max-h-[88vh] shadow-2xl flex flex-col overflow-hidden text-slate-100">
        
        {/* Header */}
        <div className="flex justify-between items-center border-b border-slate-800 p-4 sm:p-5 shrink-0 bg-slate-900">
          <div>
            <div className="inline-flex items-center gap-1.5 text-[10px] font-black text-emerald-400 uppercase tracking-wider bg-emerald-950 px-2.5 py-0.5 rounded-full border border-emerald-500/30 mb-1">
              <IconPlus size={12} />
              <span>Add Crop to Marketplace</span>
            </div>
            <h3 className="text-lg sm:text-xl font-black text-white">List Crop Availability & Procurement Lot</h3>
          </div>
          <button
            onClick={onClose}
            type="button"
            className="text-slate-400 hover:text-white text-lg font-bold p-1.5 rounded-lg transition-colors cursor-pointer"
            aria-label="Close modal"
          >
            ✕
          </button>
        </div>

        {/* Scrollable Body Form */}
        <form id="plan-crop-form" onSubmit={handleSubmit} className="flex-1 flex flex-col min-h-0 overflow-hidden text-xs">
          <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-4">
          
          {/* No Farm Warning Banner */}
          {!farmsLoading && (farmsError || farms.length === 0) && (
            <div className="p-4 bg-amber-950/80 border border-amber-500/50 rounded-2xl text-amber-200 space-y-2">
              <div className="font-extrabold text-sm flex items-center gap-2">
                ⚠️ Farm Profile Required
              </div>
              <p className="text-xs">
                Please complete your Farm Profile before adding a crop to the marketplace.
              </p>
              <button
                type="button"
                onClick={() => {
                  onClose();
                  navigate('/farm-info');
                }}
                className="inline-block px-3 py-1.5 bg-amber-500 text-slate-950 font-black rounded-lg text-xs hover:bg-amber-400 cursor-pointer"
              >
                Go to My Farm Profile →
              </button>
            </div>
          )}

          {/* Multiple Farms Selection Dropdown */}
          {(() => {
            const safeFarms = Array.isArray(farms) ? farms : [];
            if (farmsLoading || safeFarms.length <= 1) return null;
            return (
              <div>
                <label className="block text-xs font-extrabold text-slate-300 uppercase tracking-wider mb-1">
                  Select Your Farm
                </label>
                <select
                  value={selectedFarmId || ''}
                  onChange={(e) => setSelectedFarmId(Number(e.target.value))}
                  className="w-full p-3 bg-slate-950 border border-slate-800 rounded-xl font-bold text-white focus:ring-2 focus:ring-amber-500"
                >
                  {safeFarms.map((f) => (
                    <option key={f.id} value={f.id}>
                      {f.district || 'Farm'} (Farm #{f.id} — {f.land_area_acre} Acres)
                    </option>
                  ))}
                </select>
              </div>
            );
          })()}

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

          <div>
            <label className="block font-extrabold text-slate-300 mb-1">Select Crop</label>
            <select
              value={cropId}
              onChange={(e) => setCropId(Number(e.target.value))}
              className="w-full p-3 bg-slate-950 border border-slate-800 rounded-xl font-bold text-white focus:ring-2 focus:ring-amber-500"
            >
              {SUPPORTED_CROPS.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          {/* Current Market Price Pop-Up / Info Card */}
          <div className="p-3.5 bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950 border border-emerald-500/40 rounded-2xl space-y-2 shadow-lg">
            {marketPriceInfo.loading ? (
              <div className="text-xs text-slate-400 font-bold animate-pulse flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                Fetching current market price & recommended range...
              </div>
            ) : marketPriceInfo.error ? (
              <div className="text-xs text-red-400 font-bold flex items-center gap-1.5">
                ⚠️ {marketPriceInfo.error}
              </div>
            ) : (
              <>
                <div className="flex justify-between items-center text-xs">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-emerald-400" />
                    <span className="font-extrabold text-emerald-300 uppercase tracking-wider">
                      {marketPriceInfo.crop_name}
                    </span>
                  </div>
                  {marketPriceInfo.price_date ? (
                    <span className="text-[10px] text-slate-400 font-bold bg-slate-900 px-2 py-0.5 rounded-md border border-slate-800">
                      Updated: {marketPriceInfo.price_date}
                    </span>
                  ) : (
                    <span className="text-[10px] text-slate-400 font-bold bg-slate-900 px-2 py-0.5 rounded-md border border-slate-800">
                      {marketPriceInfo.market_name || 'APMC Market'}
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-3 pt-2 border-t border-slate-800/80">
                  <div className="bg-slate-900/90 p-2.5 rounded-xl border border-slate-800">
                    <div className="text-[10px] text-slate-400 font-extrabold uppercase tracking-wider mb-0.5">
                      Today's Market Price
                    </div>
                    <div className="text-base font-black text-emerald-400">
                      ₹{marketPriceInfo.price?.toLocaleString()} <span className="text-[10px] text-slate-400 font-semibold">/ Quintal</span>
                    </div>
                  </div>
                  <div className="bg-slate-900/90 p-2.5 rounded-xl border border-slate-800">
                    <div className="text-[10px] text-slate-400 font-extrabold uppercase tracking-wider mb-0.5">
                      Recommended Target Price
                    </div>
                    <div className="text-base font-black text-amber-400">
                      ₹{marketPriceInfo.min_target_price?.toLocaleString()} – ₹{marketPriceInfo.max_target_price?.toLocaleString()} <span className="text-[10px] text-slate-400 font-semibold">/ Quintal</span>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-extrabold text-slate-300 mb-1">
                {cropStage === 'HARVESTED' ? 'Harvested Quantity (Q)' : 'Expected Quantity (Q)'}
              </label>
              <input
                type="number"
                min="0.1"
                step="any"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                placeholder="e.g. 30"
                className="w-full p-3 bg-slate-950 border border-slate-800 rounded-xl font-bold text-white focus:ring-2 focus:ring-amber-500 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                required
              />
            </div>

            <div>
              <label className="block font-extrabold text-slate-300 mb-1">
                {cropStage === 'HARVESTED' ? 'Selling Price (₹ / Q)' : 'Target Price (₹ / Q)'}
              </label>
              <input
                type="number"
                min="1"
                step="any"
                value={targetPrice}
                onChange={(e) => setTargetPrice(e.target.value)}
                placeholder={marketPriceInfo.price ? `e.g. ${marketPriceInfo.price}` : "e.g. 6400"}
                className={`w-full p-3 bg-slate-950 border ${
                  priceValidationError ? 'border-red-500 ring-1 ring-red-500/50' : 'border-slate-800 focus:ring-2 focus:ring-amber-500'
                } rounded-xl font-bold text-white [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none`}
              />
            </div>
          </div>

          {priceValidationError && (
            <div className="p-2.5 bg-red-950/80 border border-red-500/50 rounded-xl text-xs text-red-200 font-bold flex items-center gap-2">
              <span>⚠️</span>
              <span>{priceValidationError}</span>
            </div>
          )}


          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-extrabold text-slate-300 mb-1">Land Area (Acres)</label>
              <input
                type="number"
                min="0.1"
                step="any"
                value={areaAcres}
                onChange={(e) => setAreaAcres(e.target.value)}
                placeholder="e.g. 2.5"
                className="w-full p-3 bg-slate-950 border border-slate-800 rounded-xl font-bold text-white focus:ring-2 focus:ring-amber-500 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
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
                <option value="A">Grade A (Premium / High Quality)</option>
                <option value="B">Grade B (Standard Market Quality)</option>
                <option value="C">Grade C (Commercial Processing)</option>
              </select>
            </div>
          )}

          {cropStage === 'HARVESTED' && (
            <div className="space-y-1.5 p-3.5 bg-slate-950/80 border border-slate-800 rounded-2xl">
              <label className="block font-extrabold text-slate-300">
                Quality Certificate <span className="text-amber-400 font-bold">*</span>
              </label>
              <p className="text-[11px] text-slate-400 leading-snug">
                Required for harvested crops. Upload the quality certificate issued for this harvested stock.
              </p>

              {!certFile ? (
                <label className="mt-2 flex flex-col items-center justify-center p-4 border-2 border-dashed border-slate-700 hover:border-amber-500/80 rounded-xl cursor-pointer bg-slate-900/60 hover:bg-slate-900 transition-all text-center">
                  <span className="text-xs font-black text-amber-400 flex items-center gap-1.5">
                    📄 Upload Quality Certificate
                  </span>
                  <span className="text-[10px] text-slate-400 mt-1">
                    Accepts PDF, JPG, JPEG, PNG (Max 10MB)
                  </span>
                  <input
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png"
                    onChange={handleCertFileChange}
                    className="hidden"
                  />
                </label>
              ) : (
                <div className="mt-2 flex items-center justify-between p-3 bg-slate-900 border border-emerald-500/40 rounded-xl">
                  <div className="flex items-center gap-2.5 overflow-hidden">
                    <div className="w-8 h-8 rounded-lg bg-emerald-950 flex items-center justify-center text-emerald-400 font-bold text-sm shrink-0 border border-emerald-500/30">
                      📄
                    </div>
                    <div className="truncate">
                      <div className="font-extrabold text-xs text-slate-100 truncate">{certFile.name}</div>
                      <div className="text-[10px] text-emerald-400 font-semibold mt-0.5">
                        {(certFile.size / (1024 * 1024)).toFixed(2)} MB &bull; Quality Certificate Selected
                      </div>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={handleRemoveCertFile}
                    className="text-[11px] text-red-400 hover:text-red-300 font-bold px-2.5 py-1 bg-red-950/60 hover:bg-red-900/80 rounded-lg border border-red-800/50 cursor-pointer shrink-0 transition-colors"
                  >
                    Remove
                  </button>
                </div>
              )}

              {certFileError && (
                <div className="text-[11px] font-bold text-red-400 mt-1">
                  ⚠️ {certFileError}
                </div>
              )}
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
          </div>

          {/* Sticky Footer */}
          <div className="p-4 border-t border-slate-800 bg-slate-950 shrink-0 flex justify-end gap-3">
            <Button type="button" variant="outline" onClick={onClose} disabled={loading} className="bg-slate-900 text-slate-300 border-slate-800 hover:bg-slate-850">
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              isLoading={loading}
              disabled={loading || Boolean(farmsError && (Array.isArray(farms) ? farms.length : 0) === 0) || (cropStage === 'HARVESTED' && !certFile) || Boolean(priceValidationError)}
              className="bg-amber-500 text-slate-950 font-black hover:bg-amber-400 disabled:opacity-50"
            >
              Publish to Marketplace
            </Button>

          </div>
        </form>
      </div>
    </div>
  );
}
