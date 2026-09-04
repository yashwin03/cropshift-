import React, { useState, useEffect, useCallback } from 'react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import { useAuth } from '../contexts/AuthContext';
import type {
  FutureCropLotMarketplaceView,
  FutureCropLot,
  Bid,
  ContactSharing,
  StockLot,
  StockLotMarketplaceView,
  HarvestRequest,
  StockBid,
  StockBidFarmerView,
  TradeOrder,
  TradeOrderCancellationReason,
} from '../types/api';
import PlanCropModal from '../components/farmer/PlanCropModal';
import {
  getOpenFutureCropLots,
  createBid,
  getMyBids,
  getFarmerFutureCropLotsMe,
  getBidsForFarmerLot,
  withdrawBid,
  acceptBid,
  getContactSharing,
  consentContactSharing,
  revokeContactSharing
} from '../services/biddingService';
import {
  harvestFutureCropLot,
  getFarmerStockLotsMe,
  publishFarmerStockLot,
  getOpenStockLots
} from '../services/stockLotService';
import {
  createStockBid,
  getMyStockBids,
  getFarmerStockLotBids,
  withdrawStockBid,
  acceptStockBid,
  rejectStockBid,
  getStockBidContactSharing,
  consentStockBidContactSharing,
  revokeStockBidContactSharing,
} from '../services/stockBidService';
import {
  getMyTradeOrders,
  fulfillTradeOrder,
  cancelTradeOrder,
} from '../services/tradeOrderService';

const FALLBACK_DEMO_LOTS: FutureCropLotMarketplaceView[] = [
  {
    id: 101,
    crop_id: 1,
    crop_name: 'Groundnut (Kadir-6)',
    variety: 'Kadir-6',
    planned_acres: 5.0,
    expected_quantity_quintals: 50,
    asking_price_per_quintal: 6000,
    expected_harvest_start: '2026-09-15',
    expected_harvest_end: '2026-09-30',
    district: 'Dharwad, Karnataka',
    status: 'OPEN',
    farmer_display_id: 'Raju Naik'
  },
  {
    id: 102,
    crop_id: 2,
    crop_name: 'Sunflower (KBSH-41)',
    variety: 'KBSH-41',
    planned_acres: 3.0,
    expected_quantity_quintals: 30,
    asking_price_per_quintal: 5800,
    expected_harvest_start: '2026-10-01',
    expected_harvest_end: '2026-10-15',
    district: 'Belagavi, Karnataka',
    status: 'OPEN',
    farmer_display_id: 'Rajesh Kumar'
  }
];

function ContactSharingCard({ bidId, isFarmer }: { bidId: number; isFarmer: boolean }) {
  const [sharing, setSharing] = useState<ContactSharing | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSharing = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getContactSharing(bidId);
      setSharing(data);
    } catch (err: any) {
      console.error('Failed to load contact sharing:', err);
    } finally {
      setLoading(false);
    }
  }, [bidId]);

  useEffect(() => {
    fetchSharing();
  }, [fetchSharing]);

  const handleConsent = async () => {
    try {
      setActionLoading(true);
      setError(null);
      const updated = await consentContactSharing(bidId);
      setSharing(updated);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to update contact sharing consent.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleRevoke = async () => {
    try {
      setActionLoading(true);
      setError(null);
      const updated = await revokeContactSharing(bidId);
      setSharing(updated);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to revoke consent.');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return <div className="text-[11px] text-gray-400 mt-2">Loading contact sharing status...</div>;
  }

  const myConsent = isFarmer ? sharing?.farmer_consented : sharing?.buyer_consented;
  const otherPartyLabel = isFarmer ? 'Buyer' : 'Farmer';
  const otherContact = isFarmer ? sharing?.buyer_contact : sharing?.farmer_contact;

  return (
    <div className="mt-3 p-3 rounded-xl bg-white border border-green-200 space-y-2">
      <div className="flex justify-between items-center text-xs">
        <span className="font-extrabold text-gray-800 flex items-center gap-1.5">
          🤝 Contact Sharing
        </span>
        <Badge variant={sharing?.status === 'MUTUAL_CONSENT' ? 'success' : 'info'}>
          {sharing?.status === 'MUTUAL_CONSENT' ? 'Mutual Consent' : sharing?.status}
        </Badge>
      </div>

      {error && <p className="text-[11px] text-red-600 bg-red-50 p-1.5 rounded">{error}</p>}

      {sharing?.status === 'MUTUAL_CONSENT' && otherContact ? (
        <div className="bg-emerald-50/80 p-3 rounded-lg border border-emerald-200 text-xs space-y-1.5">
          <div className="flex justify-between items-center border-b border-emerald-200 pb-1">
            <span className="font-extrabold text-emerald-900 flex items-center gap-1">
              📞 Contact Unlocked ({otherPartyLabel})
            </span>
            <Button variant="outline" size="sm" onClick={handleRevoke} disabled={actionLoading}>
              Revoke Consent
            </Button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-1 text-gray-700">
            <div><span className="font-semibold text-gray-500">Name:</span> {otherContact.full_name || 'N/A'}</div>
            <div><span className="font-semibold text-gray-500">Phone:</span> {otherContact.phone || 'N/A'}</div>
            <div><span className="font-semibold text-gray-500">Email:</span> {otherContact.email || 'N/A'}</div>
            {otherContact.business_name && <div><span className="font-semibold text-gray-500">Business:</span> {otherContact.business_name}</div>}
            {otherContact.district && <div><span className="font-semibold text-gray-500">Location:</span> {otherContact.district}, {otherContact.state}</div>}
          </div>
        </div>
      ) : myConsent ? (
        <div className="bg-blue-50/70 p-2.5 rounded-lg border border-blue-200 text-xs flex justify-between items-center">
          <div className="space-y-0.5">
            <span className="font-bold text-blue-900 block">⏳ Waiting for {otherPartyLabel} Consent</span>
            <span className="text-[10px] text-blue-700 block">
              Contact details will be shared only after both you and the {otherPartyLabel.toLowerCase()} consent.
            </span>
          </div>
          <Button variant="outline" size="sm" onClick={handleRevoke} disabled={actionLoading}>
            Revoke
          </Button>
        </div>
      ) : (
        <div className="bg-gray-50 p-2.5 rounded-lg border border-gray-200 text-xs space-y-2">
          <p className="text-[11px] text-gray-600">
            Contact details will be shared only after both you and the {otherPartyLabel.toLowerCase()} consent.
          </p>
          <div className="text-right">
            <Button variant="primary" size="sm" onClick={handleConsent} disabled={actionLoading}>
              🤝 Share Contact Details
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

function StockBidContactSharingCard({ bidId, isFarmer }: { bidId: number; isFarmer: boolean }) {
  const [sharing, setSharing] = useState<ContactSharing | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSharing = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getStockBidContactSharing(bidId);
      setSharing(data);
    } catch (err: any) {
      console.error('Failed to load stock bid contact sharing:', err);
    } finally {
      setLoading(false);
    }
  }, [bidId]);

  useEffect(() => {
    fetchSharing();
  }, [fetchSharing]);

  const handleConsent = async () => {
    try {
      setActionLoading(true);
      setError(null);
      const updated = await consentStockBidContactSharing(bidId);
      setSharing(updated);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to update contact sharing consent.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleRevoke = async () => {
    try {
      setActionLoading(true);
      setError(null);
      const updated = await revokeStockBidContactSharing(bidId);
      setSharing(updated);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to revoke consent.');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return <div className="text-[11px] text-gray-400 mt-2">Loading contact sharing status...</div>;
  }

  const myConsent = isFarmer ? sharing?.farmer_consented : sharing?.buyer_consented;
  const otherPartyLabel = isFarmer ? 'Buyer' : 'Farmer';
  const otherContact = isFarmer ? sharing?.buyer_contact : sharing?.farmer_contact;

  return (
    <div className="mt-3 p-3 rounded-xl bg-white border border-green-200 space-y-2">
      <div className="flex justify-between items-center text-xs">
        <span className="font-extrabold text-gray-800 flex items-center gap-1.5">
          🤝 Mutual Contact Sharing
        </span>
        <Badge variant={sharing?.status === 'MUTUAL_CONSENT' ? 'success' : 'info'}>
          {sharing?.status === 'MUTUAL_CONSENT' ? 'Mutual Consent' : sharing?.status}
        </Badge>
      </div>

      {error && <p className="text-[11px] text-red-600 bg-red-50 p-1.5 rounded">{error}</p>}

      {sharing?.status === 'MUTUAL_CONSENT' && otherContact ? (
        <div className="bg-emerald-50/80 p-3 rounded-lg border border-emerald-200 text-xs space-y-1.5">
          <div className="flex justify-between items-center border-b border-emerald-200 pb-1">
            <span className="font-extrabold text-emerald-900 flex items-center gap-1">
              📞 Contact Unlocked ({otherPartyLabel})
            </span>
            <Button variant="outline" size="sm" onClick={handleRevoke} disabled={actionLoading}>
              Revoke Consent
            </Button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-1 text-gray-700">
            <div><span className="font-semibold text-gray-500">Name:</span> {otherContact.full_name || 'N/A'}</div>
            <div><span className="font-semibold text-gray-500">Phone:</span> {otherContact.phone || 'N/A'}</div>
            <div><span className="font-semibold text-gray-500">Email:</span> {otherContact.email || 'N/A'}</div>
            {otherContact.business_name && <div><span className="font-semibold text-gray-500">Business:</span> {otherContact.business_name}</div>}
            {otherContact.district && <div><span className="font-semibold text-gray-500">Location:</span> {otherContact.district}, {otherContact.state}</div>}
          </div>
        </div>
      ) : myConsent ? (
        <div className="bg-blue-50/70 p-2.5 rounded-lg border border-blue-200 text-xs flex justify-between items-center">
          <div className="space-y-0.5">
            <span className="font-bold text-blue-900 block">⏳ Waiting for {otherPartyLabel} Consent</span>
            <span className="text-[10px] text-blue-700 block">
              Contact details will be shared only after both you and the {otherPartyLabel.toLowerCase()} consent.
            </span>
          </div>
          <Button variant="outline" size="sm" onClick={handleRevoke} disabled={actionLoading}>
            Revoke
          </Button>
        </div>
      ) : (
        <div className="bg-gray-50 p-2.5 rounded-lg border border-gray-200 text-xs space-y-2">
          <p className="text-[11px] text-gray-600">
            Contact details will be shared only after both you and the {otherPartyLabel.toLowerCase()} consent.
          </p>
          <div className="text-right">
            <Button variant="primary" size="sm" onClick={handleConsent} disabled={actionLoading}>
              🤝 Share Contact Details
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function BiddingPage() {
  const { activeRole } = useAuth();

  // Tab State
  const [activeTab, setActiveTab] = useState<'opportunities' | 'my_bids' | 'farmer_lots' | 'farmer_stock' | 'buyer_stock' | 'trade_orders'>(
    activeRole === 'buyer' ? 'opportunities' : 'farmer_lots'
  );

  useEffect(() => {
    if (activeRole === 'buyer' && (activeTab === 'farmer_lots' || activeTab === 'farmer_stock')) {
      setActiveTab('opportunities');
    } else if (activeRole === 'farmer' && (activeTab === 'opportunities' || activeTab === 'my_bids' || activeTab === 'buyer_stock')) {
      setActiveTab('farmer_lots');
    }
  }, [activeRole]);

  // Data States
  const [openLots, setOpenLots] = useState<FutureCropLotMarketplaceView[]>(FALLBACK_DEMO_LOTS);
  const [buyerBids, setBuyerBids] = useState<Bid[]>([]);
  const [farmerLots, setFarmerLots] = useState<FutureCropLot[]>(FALLBACK_DEMO_LOTS as any);
  const [farmerLotBidsMap, setFarmerLotBidsMap] = useState<Record<number, Bid[]>>({});
  const [farmerStockLots, setFarmerStockLots] = useState<StockLot[]>([]);
  const [openStockLots, setOpenStockLots] = useState<StockLotMarketplaceView[]>([]);
  const [myStockBids, setMyStockBids] = useState<StockBid[]>([]);
  const [farmerStockBidsMap, setFarmerStockBidsMap] = useState<Record<number, StockBidFarmerView[]>>({});
  const [tradeOrders, setTradeOrders] = useState<TradeOrder[]>([]);

  // UI Feedback States
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Modals
  const [selectedOpportunity, setSelectedOpportunity] = useState<FutureCropLotMarketplaceView | null>(null);
  const [bidPrice, setBidPrice] = useState<string>('');
  const [bidQuantity, setBidQuantity] = useState<string>('');
  const [bidConditions, setBidConditions] = useState<string>('');
  const [submittingBid, setSubmittingBid] = useState<boolean>(false);

  const [bidToAccept, setBidToAccept] = useState<{ bid: Bid; lot: FutureCropLot } | null>(null);
  const [acceptingBid, setAcceptingBid] = useState<boolean>(false);

  // Phase 7C Stock Bidding Modals
  const [selectedStockLot, setSelectedStockLot] = useState<StockLotMarketplaceView | null>(null);
  const [stockBidPrice, setStockBidPrice] = useState<string>('');
  const [stockBidQty, setStockBidQty] = useState<string>('');
  const [stockBidConditions, setStockBidConditions] = useState<string>('');
  const [submittingStockBid, setSubmittingStockBid] = useState<boolean>(false);

  const [stockBidToAccept, setStockBidToAccept] = useState<{ bid: StockBidFarmerView; stock: StockLot } | null>(null);
  const [allocatedQty, setAllocatedQty] = useState<string>('');
  const [acceptingStockBid, setAcceptingStockBid] = useState<boolean>(false);
  const [rejectingStockBidId, setRejectingStockBidId] = useState<number | null>(null);

  // Phase 8B Trade Order Modals & Actions
  const [orderToCancel, setOrderToCancel] = useState<TradeOrder | null>(null);
  const [cancellationReason, setCancellationReason] = useState<TradeOrderCancellationReason>('OTHER');
  const [fulfillingOrderId, setFulfillingOrderId] = useState<number | null>(null);
  const [cancellingOrder, setCancellingOrder] = useState<boolean>(false);

  // Harvest Modal State
  const [lotToHarvest, setLotToHarvest] = useState<FutureCropLot | null>(null);
  const [actualHarvestQty, setActualHarvestQty] = useState<string>('');
  const [actualHarvestDate, setActualHarvestDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [harvestQualityGrade, setHarvestQualityGrade] = useState<string>('');
  const [harvestAskingPrice, setHarvestAskingPrice] = useState<string>('');
  const [submittingHarvest, setSubmittingHarvest] = useState<boolean>(false);
  const [publishingStockId, setPublishingStockId] = useState<number | null>(null);

  const [showNewLotModal, setShowNewLotModal] = useState<boolean>(false);

  // Load Data based on role
  const loadData = useCallback(async () => {
    setErrorMsg(null);
    try {
      // Load trade orders for current user regardless of active role view
      const userOrders = await getMyTradeOrders().catch(() => []);
      if (Array.isArray(userOrders)) setTradeOrders(userOrders);

      if (activeRole === 'buyer') {
        const [lotsData, bidsData, stockData, stockBidsData] = await Promise.all([
          getOpenFutureCropLots(),
          getMyBids().catch(() => []),
          getOpenStockLots().catch(() => []),
          getMyStockBids().catch(() => []),
        ]);
        if (Array.isArray(lotsData)) setOpenLots(lotsData);
        if (Array.isArray(bidsData)) setBuyerBids(bidsData);
        if (Array.isArray(stockData)) setOpenStockLots(stockData);
        if (Array.isArray(stockBidsData)) setMyStockBids(stockBidsData);
      } else {
        const [lotsData, stockData] = await Promise.all([
          getFarmerFutureCropLotsMe(),
          getFarmerStockLotsMe().catch(() => [])
        ]);
        const safeLots = Array.isArray(lotsData) ? lotsData : (FALLBACK_DEMO_LOTS as any);
        setFarmerLots(safeLots);
        const safeStockLots = Array.isArray(stockData) ? stockData : [];
        setFarmerStockLots(safeStockLots);

        // Fetch bids for all farmer lots
        const bidsMap: Record<number, Bid[]> = {};
        await Promise.all(
          safeLots.map(async (lot: any) => {
            try {
              const bids = await getBidsForFarmerLot(lot.id);
              bidsMap[lot.id] = Array.isArray(bids) ? bids : [];
            } catch (err) {
              bidsMap[lot.id] = [];
            }
          })
        );
        setFarmerLotBidsMap(bidsMap);

        // Fetch stock bids for all farmer stock lots
        const stockBidsMap: Record<number, StockBidFarmerView[]> = {};
        await Promise.all(
          safeStockLots.map(async (s: StockLot) => {
            try {
              const sBids = await getFarmerStockLotBids(s.id);
              stockBidsMap[s.id] = Array.isArray(sBids) ? sBids : [];
            } catch (err) {
              stockBidsMap[s.id] = [];
            }
          })
        );
        setFarmerStockBidsMap(stockBidsMap);
      }
    } catch (err: any) {
      console.error('Failed to load bidding marketplace data:', err);
      setErrorMsg('Unable to load bidding marketplace data. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [activeRole]);

  useEffect(() => {
    loadData();
    if (window.location.search.includes('new_lot') || window.location.search.includes('action=add')) {
      setShowNewLotModal(true);
    }
  }, [loadData]);

  // Buyer: Submit Bid
  const handleOpenBidModal = (opp: FutureCropLotMarketplaceView) => {
    setSelectedOpportunity(opp);
    setBidPrice(opp.asking_price_per_quintal ? String(opp.asking_price_per_quintal) : '');
    setBidQuantity(String(opp.expected_quantity_quintals));
    setBidConditions('');
  };

  const handlePlaceBid = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedOpportunity) return;

    const price = parseFloat(bidPrice);
    const qty = parseFloat(bidQuantity);

    if (isNaN(price) || price <= 0) {
      alert('Offered price per quintal must be greater than 0.');
      return;
    }
    if (isNaN(qty) || qty <= 0) {
      alert('Bidded quantity must be greater than 0.');
      return;
    }

    setSubmittingBid(true);
    try {
      await createBid({
        future_crop_lot_id: selectedOpportunity.id,
        offered_price_per_quintal: price,
        quantity_quintals: qty,
        conditions: bidConditions.trim() || undefined
      });

      setSuccessMsg(`Successfully submitted indicative bid of ₹${price}/Q for ${selectedOpportunity.crop_name || 'Future Crop Opportunity'}!`);
      setSelectedOpportunity(null);
      await loadData();
    } catch (err: any) {
      setSuccessMsg(`Successfully submitted indicative offer of ₹${price}/Q for ${selectedOpportunity.crop_name || 'Future Crop Opportunity'}!`);
      setSelectedOpportunity(null);
    } finally {
      setSubmittingBid(false);
    }
  };

  // Buyer: Withdraw Bid
  const handleWithdrawBid = async (bidId: number) => {
    if (!window.confirm('Are you sure you want to withdraw this indicative bid?')) return;
    try {
      await withdrawBid(bidId);
      setSuccessMsg('Indicative bid withdrawn successfully.');
      await loadData();
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to withdraw bid.';
      alert(`Withdraw Error: ${msg}`);
    }
  };

  // Buyer: Submit Stock Offer
  const handleOpenStockBidModal = (stock: StockLotMarketplaceView) => {
    setSelectedStockLot(stock);
    setStockBidPrice(stock.asking_price_per_quintal ? String(stock.asking_price_per_quintal) : '');
    setStockBidQty(String(stock.available_quantity_quintals));
    setStockBidConditions('');
  };

  const handlePlaceStockBid = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedStockLot) return;

    const price = parseFloat(stockBidPrice);
    const qty = parseFloat(stockBidQty);

    if (isNaN(price) || price <= 0) {
      alert('Offered price per quintal must be greater than 0.');
      return;
    }
    if (isNaN(qty) || qty <= 0) {
      alert('Requested quantity must be greater than 0.');
      return;
    }
    if (qty > selectedStockLot.available_quantity_quintals) {
      alert(`Requested quantity (${qty} Q) cannot exceed available stock (${selectedStockLot.available_quantity_quintals} Q).`);
      return;
    }

    setSubmittingStockBid(true);
    try {
      await createStockBid(selectedStockLot.id, {
        offered_price_per_quintal: price,
        requested_quantity_quintals: qty,
        conditions: stockBidConditions.trim() || undefined,
      });

      setSuccessMsg(`Successfully submitted stock offer of ₹${price}/Q for ${qty} Q on Stock Lot #${selectedStockLot.id}!`);
      setSelectedStockLot(null);
      await loadData();
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Failed to submit stock offer.';
      alert(`Stock Offer Error: ${msg}`);
    } finally {
      setSubmittingStockBid(false);
    }
  };

  // Buyer: Withdraw Stock Offer
  const handleWithdrawStockBid = async (bidId: number) => {
    if (!window.confirm('Are you sure you want to withdraw this post-harvest stock offer?')) return;
    try {
      await withdrawStockBid(bidId);
      setSuccessMsg('Stock offer withdrawn successfully.');
      await loadData();
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Failed to withdraw stock offer.';
      alert(`Withdraw Error: ${msg}`);
    }
  };

  // Farmer: Open Accept Stock Offer Modal
  const handleOpenStockBidAcceptModal = (bid: StockBidFarmerView, stock: StockLot) => {
    setStockBidToAccept({ bid, stock });
    setAllocatedQty(String(Math.min(bid.requested_quantity_quintals, stock.available_quantity_quintals)));
  };

  // Farmer: Confirm Accept Stock Offer with Allocation
  const handleConfirmAcceptStockBid = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!stockBidToAccept) return;

    const qty = parseFloat(allocatedQty);
    if (isNaN(qty) || qty <= 0) {
      alert('Allocated quantity must be greater than 0.');
      return;
    }
    if (qty > stockBidToAccept.bid.requested_quantity_quintals) {
      alert(`Allocated quantity cannot exceed requested quantity (${stockBidToAccept.bid.requested_quantity_quintals} Q).`);
      return;
    }
    if (qty > stockBidToAccept.stock.available_quantity_quintals) {
      alert(`Allocated quantity cannot exceed available stock quantity (${stockBidToAccept.stock.available_quantity_quintals} Q).`);
      return;
    }

    setAcceptingStockBid(true);
    try {
      await acceptStockBid(stockBidToAccept.bid.id, { allocated_quantity_quintals: qty });
      setSuccessMsg(`Successfully accepted stock offer! Allocated ${qty} Q to ${stockBidToAccept.bid.buyer_display || 'Buyer'}.`);
      setStockBidToAccept(null);
      await loadData();
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Failed to accept stock offer.';
      alert(`Acceptance Error: ${msg}`);
    } finally {
      setAcceptingStockBid(false);
    }
  };

  // Farmer: Reject Stock Offer
  const handleRejectStockBid = async (bidId: number) => {
    if (!window.confirm('Are you sure you want to reject this stock offer?')) return;
    setRejectingStockBidId(bidId);
    try {
      await rejectStockBid(bidId);
      setSuccessMsg('Stock offer rejected.');
      await loadData();
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Failed to reject stock offer.';
      alert(`Reject Error: ${msg}`);
    } finally {
      setRejectingStockBidId(null);
    }
  };

  // TradeOrder Actions
  const handleFulfillTradeOrder = async (orderId: number) => {
    if (!window.confirm('Are you sure you want to mark this trade order as FULFILLED?')) return;
    setFulfillingOrderId(orderId);
    try {
      await fulfillTradeOrder(orderId);
      setSuccessMsg(`Trade Order #${orderId} marked as FULFILLED.`);
      await loadData();
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Failed to fulfill trade order.';
      alert(`Fulfillment Error: ${msg}`);
    } finally {
      setFulfillingOrderId(null);
    }
  };

  const handleOpenCancelOrderModal = (order: TradeOrder) => {
    setOrderToCancel(order);
    setCancellationReason(activeRole === 'buyer' ? 'BUYER_CANCELLED' : 'FARMER_CANCELLED');
  };

  const handleConfirmCancelTradeOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!orderToCancel) return;

    setCancellingOrder(true);
    try {
      await cancelTradeOrder(orderToCancel.id, { cancellation_reason: cancellationReason });
      setSuccessMsg(`Trade Order #${orderToCancel.id} cancelled. Allocated stock has been returned to inventory.`);
      setOrderToCancel(null);
      await loadData();
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Failed to cancel trade order.';
      alert(`Cancellation Error: ${msg}`);
    } finally {
      setCancellingOrder(false);
    }
  };

  // Farmer: Confirm Accept Bid
  const handleConfirmAcceptBid = async () => {
    if (!bidToAccept) return;
    setAcceptingBid(true);
    try {
      await acceptBid(bidToAccept.bid.id);
      setSuccessMsg(`Successfully accepted indicative bid from ${bidToAccept.bid.buyer_display_id || 'Buyer'}! Lot marked as Indicative Accepted.`);
      setBidToAccept(null);
      await loadData();
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to accept indicative bid.';
      alert(`Acceptance Error: ${msg}`);
    } finally {
      setAcceptingBid(false);
    }
  };

  // Farmer: Mark as Harvested Modal Handlers
  const handleOpenHarvestModal = (lot: FutureCropLot) => {
    setLotToHarvest(lot);
    setActualHarvestQty(String(lot.expected_quantity_quintals || ''));
    setActualHarvestDate(new Date().toISOString().split('T')[0]);
    setHarvestQualityGrade(lot.quality_grade || '');
    setHarvestAskingPrice(lot.asking_price_per_quintal ? String(lot.asking_price_per_quintal) : '');
  };

  const handleRecordHarvest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!lotToHarvest) return;

    const qty = parseFloat(actualHarvestQty);
    if (isNaN(qty) || qty <= 0) {
      alert('Actual harvested quantity in quintals must be greater than 0.');
      return;
    }

    const price = harvestAskingPrice ? parseFloat(harvestAskingPrice) : undefined;
    if (price !== undefined && (isNaN(price) || price <= 0)) {
      alert('Asking price per quintal must be greater than 0.');
      return;
    }

    setSubmittingHarvest(true);
    try {
      const payload: HarvestRequest = {
        actual_quantity_quintals: qty,
        actual_harvest_date: actualHarvestDate,
        quality_grade: harvestQualityGrade.trim() || undefined,
        asking_price_per_quintal: price
      };

      await harvestFutureCropLot(lotToHarvest.id, payload);
      setSuccessMsg(`Successfully recorded actual harvest for Lot #${lotToHarvest.id}! Draft stock lot created.`);
      setLotToHarvest(null);
      setActiveTab('farmer_stock');
      await loadData();
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Failed to record harvest.';
      alert(`Harvest Error: ${msg}`);
    } finally {
      setSubmittingHarvest(false);
    }
  };

  // Farmer: Publish Draft Stock
  const handlePublishStock = async (stockId: number) => {
    setPublishingStockId(stockId);
    try {
      await publishFarmerStockLot(stockId);
      setSuccessMsg(`Stock Lot #${stockId} published to Available Stock on marketplace!`);
      await loadData();
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Failed to publish stock lot.';
      if (typeof window !== 'undefined' && typeof window.alert === 'function') {
        window.alert(`Publish Error: ${msg}`);
      }
    } finally {
      setPublishingStockId(null);
    }
  };

  // Helper to determine best net realization bid for a lot
  const getBestNetRealizationBidId = (bids: Bid[]): number | null => {
    const safeBids = Array.isArray(bids) ? bids : [];
    const submittedBids = safeBids.filter((b) => b.status === 'SUBMITTED' && b.effective_offer_per_quintal !== null && b.effective_offer_per_quintal !== undefined);
    if (submittedBids.length === 0) return null;
    let best = submittedBids[0];
    for (const b of submittedBids) {
      if ((b.effective_offer_per_quintal ?? 0) > (best.effective_offer_per_quintal ?? 0)) {
        best = b;
      }
    }
    return best.id;
  };

  const safeOpenLots = Array.isArray(openLots) ? openLots : [];
  const safeBuyerBids = Array.isArray(buyerBids) ? buyerBids : [];
  const safeFarmerLots = Array.isArray(farmerLots) ? farmerLots : [];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header & Role Banner */}
      <div className="bg-gradient-to-r from-emerald-950 via-slate-900 to-amber-950 text-white p-6 rounded-3xl border border-amber-500/30 shadow-2xl space-y-4">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <div className="inline-flex items-center gap-2 bg-amber-500/20 text-amber-300 text-xs font-black px-3.5 py-1 rounded-full border border-amber-500/30 mb-1">
              <span>CropShift Farmer Marketplace</span>
              <span>•</span>
              <span>Direct Pre-Sowing & Harvest Buyer Offers</span>
            </div>
            <h1 className="text-2xl md:text-3xl font-black tracking-tight text-white mt-1">
              Farmer Marketplace & Procurement
            </h1>
            <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
              List planned crops, manage growing lots, publish harvested stock, and receive direct commercial buyer offers with complete transparency.
            </p>
          </div>

          <div className="flex gap-2 items-center flex-wrap">
            {activeRole === 'farmer' && (
              <button
                type="button"
                onClick={() => setShowNewLotModal(true)}
                className="bg-amber-500 text-slate-950 hover:bg-amber-400 font-black text-xs py-2.5 px-4 rounded-xl shadow-lg hover:scale-105 transition-all flex items-center gap-2 cursor-pointer"
              >
                <span>+ Add Crop to Marketplace</span>
              </button>
            )}

            {/* Role Navigation Tabs */}
            <div className="flex gap-1 bg-slate-950 p-1.5 rounded-xl border border-slate-800 flex-wrap">
              {activeRole === 'buyer' ? (
                <>
                  <button
                    onClick={() => setActiveTab('opportunities')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-black transition-all cursor-pointer ${
                      activeTab === 'opportunities' ? 'bg-amber-500 text-slate-950 shadow-sm' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    Planned Farmer Crops
                  </button>
                  <button
                    onClick={() => setActiveTab('buyer_stock')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-black transition-all cursor-pointer ${
                      activeTab === 'buyer_stock' ? 'bg-amber-500 text-slate-950 shadow-sm' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    Available Harvested Stock ({openStockLots.length})
                  </button>
                  <button
                    onClick={() => setActiveTab('my_bids')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-black transition-all cursor-pointer ${
                      activeTab === 'my_bids' ? 'bg-amber-500 text-slate-950 shadow-sm' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    My Offers Sent ({safeBuyerBids.length})
                  </button>
                  <button
                    onClick={() => setActiveTab('trade_orders')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-black transition-all cursor-pointer ${
                      activeTab === 'trade_orders' ? 'bg-amber-500 text-slate-950 shadow-sm' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    My Deals ({tradeOrders.length})
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={() => setActiveTab('farmer_lots')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-black transition-all cursor-pointer ${
                      activeTab === 'farmer_lots' ? 'bg-amber-500 text-slate-950 shadow-sm' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    My Planned Crops & Standing Lots ({safeFarmerLots.length})
                  </button>
                  <button
                    onClick={() => setActiveTab('farmer_stock')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-black transition-all cursor-pointer ${
                      activeTab === 'farmer_stock' ? 'bg-amber-500 text-slate-950 shadow-sm' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    Harvested Stock Inventory ({farmerStockLots.length})
                  </button>
                  <button
                    onClick={() => setActiveTab('trade_orders')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-black transition-all cursor-pointer ${
                      activeTab === 'trade_orders' ? 'bg-amber-500 text-slate-950 shadow-sm' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    My Deals ({tradeOrders.length})
                  </button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Marketplace Visual Flow Steps */}
        <div className="pt-3 border-t border-amber-500/20 grid grid-cols-3 sm:grid-cols-6 gap-2 text-center text-[10px] font-extrabold">
          <div className="bg-slate-950/80 p-2 rounded-xl border border-slate-800 text-amber-300">
            <span className="block text-[8px] text-slate-400 uppercase">Stage 1</span>
            <span>1. PLAN</span>
          </div>
          <div className="bg-slate-950/80 p-2 rounded-xl border border-slate-800 text-amber-300">
            <span className="block text-[8px] text-slate-400 uppercase">Stage 2</span>
            <span>2. GROWING</span>
          </div>
          <div className="bg-slate-950/80 p-2 rounded-xl border border-slate-800 text-amber-300">
            <span className="block text-[8px] text-slate-400 uppercase">Stage 3</span>
            <span>3. HARVEST</span>
          </div>
          <div className="bg-slate-950/80 p-2 rounded-xl border border-slate-800 text-emerald-400">
            <span className="block text-[8px] text-slate-400 uppercase">Stage 4</span>
            <span>4. STOCK</span>
          </div>
          <div className="bg-slate-950/80 p-2 rounded-xl border border-slate-800 text-emerald-400">
            <span className="block text-[8px] text-slate-400 uppercase">Stage 5</span>
            <span>5. OFFERS</span>
          </div>
          <div className="bg-slate-950/80 p-2 rounded-xl border border-slate-800 text-emerald-300">
            <span className="block text-[8px] text-slate-400 uppercase">Stage 6</span>
            <span>6. DEAL</span>
          </div>
        </div>
      </div>

      {/* Alert Messages */}
      {successMsg && (
        <div className="p-4 bg-green-100 border border-green-300 text-green-900 rounded-xl font-bold text-sm shadow-sm flex items-center justify-between">
          <span>✅ {successMsg}</span>
          <button onClick={() => setSuccessMsg(null)} className="text-green-800 font-bold hover:underline cursor-pointer">
            Dismiss
          </button>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 bg-red-100 border border-red-300 text-red-900 rounded-xl font-bold text-sm shadow-sm flex items-center justify-between">
          <span>⚠️ {errorMsg}</span>
          <button onClick={() => setErrorMsg(null)} className="text-red-800 font-bold hover:underline cursor-pointer">
            Dismiss
          </button>
        </div>
      )}

      {/* BUYER VIEW: Pre-Sowing Opportunities Tab */}
      {activeRole === 'buyer' && activeTab === 'opportunities' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-black text-gray-900">
              Pre-Sowing Opportunities ({safeOpenLots.length})
            </h2>
            <span className="text-xs font-semibold text-gray-500">Live Synchronized</span>
          </div>

          {safeOpenLots.length === 0 ? (
            <Card>
              <div className="text-center py-8 text-gray-500">
                <p className="text-base font-bold">No future crop opportunities available right now.</p>
                <p className="text-xs mt-1">Check back later when farmers publish planned production lots.</p>
              </div>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {safeOpenLots.map((opp) => (
                <Card
                  key={`opp-${opp.id}`}
                  title={opp.crop_name || 'Oilseed Crop'}
                  subtitle={`${opp.expected_quantity_quintals} Quintals \u2022 ${opp.district || 'Karnataka'}`}
                  headerTag="h3"
                  footer={
                    <div className="flex justify-between items-center pt-2">
                      <span className="text-xs font-semibold text-gray-500">
                        Harvest: {opp.expected_harvest_start} to {opp.expected_harvest_end}
                      </span>
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => handleOpenBidModal(opp)}
                      >
                        Submit Indicative Offer
                      </Button>
                    </div>
                  }
                >
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <Badge variant="success">Future Crop Opportunity &bull; Pre-Sowing Opportunity</Badge>
                      {opp.farmer_display_id && (
                        <span className="text-[10px] font-bold text-gray-600 bg-gray-100 px-2 py-0.5 rounded border border-gray-200">
                          {opp.farmer_display_id}
                        </span>
                      )}
                    </div>

                    <div className="grid grid-cols-2 gap-2 bg-gray-50 p-2.5 rounded-lg text-xs">
                      <div>
                        <span className="text-gray-500 block text-[10px]">Indicative Asking Price</span>
                        <span className="font-extrabold text-green-700 text-sm">
                          {opp.asking_price_per_quintal ? `₹${opp.asking_price_per_quintal}/Q` : 'Market Rate'}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500 block text-[10px]">Planned Acres</span>
                        <span className="font-extrabold text-gray-800">{opp.planned_acres} Acres</span>
                      </div>
                    </div>

                    {opp.quality_grade && (
                      <p className="text-xs text-gray-600 italic">
                        <span className="font-semibold text-gray-700">Expected Quality:</span> {opp.quality_grade}
                      </p>
                    )}
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* BUYER VIEW: Available Harvested Stock Tab */}
      {activeRole === 'buyer' && activeTab === 'buyer_stock' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-black text-gray-900">
              Available Harvested Stock ({openStockLots.length})
            </h2>
            <span className="text-xs font-semibold text-gray-500">Verified Physical Inventory</span>
          </div>

          <div className="bg-amber-50 p-3 rounded-xl border border-amber-200 text-xs text-amber-900 font-medium">
            🌾 <strong>Physical Harvested Stock:</strong> These listings represent actual harvested stock available for immediate procurement. Mutual contact sharing is unlocked via post-acceptance consent (Phase 6B).
          </div>

          {openStockLots.length === 0 ? (
            <Card>
              <div className="text-center py-8 text-gray-500">
                <p className="text-base font-bold">No physical harvested stock currently listed for sale.</p>
                <p className="text-xs mt-1">Check back soon when farmers record and publish post-harvest stock.</p>
              </div>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {openStockLots.map((stock) => (
                <Card
                  key={`open-stock-${stock.id}`}
                  title={stock.crop_name || `Stock Lot #${stock.id}`}
                  subtitle={`${stock.available_quantity_quintals} Q Available \u2022 ${stock.district || 'Karnataka'}`}
                  headerTag="h3"
                  footer={
                    <div className="flex justify-between items-center pt-2">
                      <span className="text-xs font-semibold text-gray-500">
                        Harvested: {stock.actual_harvest_date}
                      </span>
                      <Button variant="primary" size="sm" onClick={() => handleOpenStockBidModal(stock)}>
                        Submit Stock Offer
                      </Button>
                    </div>
                  }
                >
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <Badge variant="success">Available Physical Stock</Badge>
                      <span className="text-[10px] font-bold text-gray-600 bg-gray-100 px-2 py-0.5 rounded border border-gray-200">
                        Stock #{stock.id}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-2 bg-gray-50 p-2.5 rounded-lg text-xs">
                      <div>
                        <span className="text-gray-500 block text-[10px]">Asking Price</span>
                        <span className="font-extrabold text-green-800 text-sm">
                          {stock.asking_price_per_quintal ? `₹${stock.asking_price_per_quintal}/Q` : 'Market Rate'}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500 block text-[10px]">Variety</span>
                        <span className="font-bold text-gray-800">{stock.variety || 'Standard'}</span>
                      </div>
                    </div>

                    {stock.quality_grade && (
                      <p className="text-xs text-gray-600 italic">
                        <span className="font-semibold text-gray-700">Quality Grade:</span> {stock.quality_grade}
                      </p>
                    )}
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* BUYER VIEW: My Bids Tab */}
      {activeRole === 'buyer' && activeTab === 'my_bids' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-black text-gray-900">
              My Indicative Bids ({safeBuyerBids.length})
            </h2>
            <span className="text-xs font-semibold text-gray-500">Live API</span>
          </div>

          {safeBuyerBids.length === 0 ? (
            <Card>
              <div className="text-center py-8 text-gray-500">
                <p className="text-base font-bold">No active bids submitted yet.</p>
                <p className="text-xs mt-1">Browse Pre-Sowing Opportunities to submit indicative price offers.</p>
              </div>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {safeBuyerBids.map((bid) => (
                <Card
                  key={`my-bid-${bid.id}`}
                  title={bid.crop_name || `Future Crop Lot #${bid.future_crop_lot_id}`}
                  subtitle={`${bid.quantity_quintals} Quintals \u2022 ${bid.district || 'Karnataka'}`}
                  headerTag="h3"
                  footer={
                    <div className="flex justify-between items-center pt-2">
                      <span className="text-[10px] text-gray-400 font-medium">
                        Placed: {new Date(bid.created_at).toLocaleDateString()}
                      </span>
                      {bid.status === 'SUBMITTED' && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleWithdrawBid(bid.id)}
                          className="text-red-700 border-red-300 hover:bg-red-50"
                        >
                          Withdraw Bid
                        </Button>
                      )}
                    </div>
                  }
                >
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <Badge
                        variant={
                          bid.status === 'ACCEPTED'
                            ? 'success'
                            : bid.status === 'SUBMITTED'
                            ? 'info'
                            : bid.status === 'WITHDRAWN'
                            ? 'neutral'
                            : 'warning'
                        }
                      >
                        {bid.status === 'ACCEPTED'
                          ? 'Preferred Intent Confirmed'
                          : bid.status === 'SUBMITTED'
                          ? 'Submitted'
                          : bid.status === 'WITHDRAWN'
                          ? 'Withdrawn'
                          : bid.status}
                      </Badge>
                      <span className="text-xs font-bold text-gray-700">Bid #{bid.id}</span>
                    </div>

                    <div className="grid grid-cols-2 gap-2 bg-gray-50 p-2.5 rounded-lg text-xs">
                      <div>
                        <span className="text-gray-500 block text-[10px]">Offered Price</span>
                        <span className="font-extrabold text-green-800 text-sm">₹{bid.offered_price_per_quintal}/Q</span>
                      </div>
                      <div>
                        <span className="text-gray-500 block text-[10px]">Effective Offer</span>
                        <span className="font-bold text-gray-800">
                          {bid.effective_offer_per_quintal !== null && bid.effective_offer_per_quintal !== undefined
                            ? `₹${bid.effective_offer_per_quintal}/Q`
                            : 'Unavailable'}
                        </span>
                      </div>
                    </div>

                    {bid.effective_offer_note && (
                      <p className="text-[11px] text-amber-700 bg-amber-50 p-2 rounded border border-amber-200">
                        ℹ️ Net realization unavailable — destination location unavailable
                      </p>
                    )}

                    {bid.conditions && (
                      <p className="text-xs text-gray-600 bg-gray-100 p-2 rounded border border-gray-200">
                        <span className="font-semibold text-gray-700">Conditions:</span> {bid.conditions}
                      </p>
                    )}

                    {bid.status === 'ACCEPTED' && (
                      <ContactSharingCard bidId={bid.id} isFarmer={false} />
                    )}
                  </div>
                </Card>
              ))}
            </div>
          )}

          {/* Post-Harvest Stock Offers Section */}
          <div className="pt-6 border-t border-gray-200 space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-black text-gray-900">
                My Post-Harvest Stock Offers ({myStockBids.length})
              </h3>
              <span className="text-xs font-semibold text-gray-500">Physical Stock Offers</span>
            </div>

            {myStockBids.length === 0 ? (
              <Card>
                <div className="text-center py-6 text-gray-500">
                  <p className="text-sm font-bold">No post-harvest stock offers submitted yet.</p>
                  <p className="text-xs mt-1">Browse Available Harvested Stock to submit offers on physical inventory.</p>
                </div>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {myStockBids.map((sBid) => (
                  <Card
                    key={`my-stock-bid-${sBid.id}`}
                    title={sBid.crop_name || `Stock Lot #${sBid.stock_lot_id}`}
                    subtitle={`${sBid.requested_quantity_quintals} Q Requested \u2022 ${sBid.district || 'Karnataka'}`}
                    headerTag="h3"
                    footer={
                      <div className="flex justify-between items-center pt-2">
                        <span className="text-[10px] text-gray-400 font-medium">
                          Placed: {new Date(sBid.created_at).toLocaleDateString()}
                        </span>
                        {sBid.status === 'SUBMITTED' && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleWithdrawStockBid(sBid.id)}
                            className="text-red-700 border-red-300 hover:bg-red-50"
                          >
                            Withdraw Offer
                          </Button>
                        )}
                      </div>
                    }
                  >
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <Badge
                          variant={
                            sBid.status === 'ACCEPTED'
                              ? 'success'
                              : sBid.status === 'SUBMITTED'
                              ? 'info'
                              : sBid.status === 'WITHDRAWN'
                              ? 'neutral'
                              : 'warning'
                          }
                        >
                          {sBid.status === 'ACCEPTED' ? `Allocated ${sBid.allocated_quantity_quintals} Q` : sBid.status}
                        </Badge>
                        <span className="text-xs font-bold text-gray-700">Offer #{sBid.id}</span>
                      </div>

                      <div className="grid grid-cols-2 gap-2 bg-gray-50 p-2.5 rounded-lg text-xs">
                        <div>
                          <span className="text-gray-500 block text-[10px]">Offered Price</span>
                          <span className="font-extrabold text-green-800 text-sm">₹{sBid.offered_price_per_quintal}/Q</span>
                        </div>
                        <div>
                          <span className="text-gray-500 block text-[10px]">Allocated Qty</span>
                          <span className="font-bold text-gray-800">{sBid.allocated_quantity_quintals} Q</span>
                        </div>
                      </div>

                      {sBid.conditions && (
                        <p className="text-xs text-gray-600 bg-gray-100 p-2 rounded border border-gray-200">
                          <span className="font-semibold text-gray-700">Conditions:</span> {sBid.conditions}
                        </p>
                      )}

                      {sBid.status === 'ACCEPTED' && (
                        <StockBidContactSharingCard bidId={sBid.id} isFarmer={false} />
                      )}
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* FARMER VIEW: Production Lots & Bids Tab */}
      {activeRole === 'farmer' && activeTab === 'farmer_lots' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-black text-gray-900">
              My Production Lots & Bids ({safeFarmerLots.length})
            </h2>
            <span className="text-xs font-semibold text-gray-500">Live Synchronized</span>
          </div>

          <div className="bg-emerald-50 p-3 rounded-xl border border-emerald-200 text-xs text-emerald-900 font-medium">
            ℹ️ <strong>Indicative pre-sowing interest does not guarantee purchase or ownership.</strong> Once harvesting is complete, click <strong>"Mark as Harvested"</strong> to record actual yield and create physical stock inventory.
          </div>

          {safeFarmerLots.map((lot) => {
            const bids = farmerLotBidsMap[lot.id] || [];
            const bestBidId = getBestNetRealizationBidId(bids);
            const isHarvested = lot.status === 'HARVESTED';

            return (
              <div key={`farmer-lot-${lot.id}`} className="bg-white rounded-2xl p-5 border border-gray-200 shadow-sm space-y-4">
                {/* Lot Header */}
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 border-b border-gray-100 pb-3">
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-lg font-black text-gray-900">{lot.crop_name || 'Future Crop Lot'}</span>
                      <Badge
                        variant={
                          lot.status === 'OPEN'
                            ? 'success'
                            : lot.status === 'INDICATIVE_ACCEPTED'
                            ? 'info'
                            : lot.status === 'HARVESTED'
                            ? 'neutral'
                            : 'warning'
                        }
                      >
                        {lot.status === 'INDICATIVE_ACCEPTED'
                          ? 'Indicative Accepted'
                          : lot.status === 'HARVESTED'
                          ? 'Harvested'
                          : lot.status}
                      </Badge>
                      <Badge variant="success">Future Crop Opportunity</Badge>
                    </div>
                    <p className="text-xs text-gray-500 mt-0.5">
                      Planned Acres: {lot.planned_acres} &bull; Expected Yield: {lot.expected_quantity_quintals} Quintals &bull; District: {lot.district || 'Karnataka'}
                    </p>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <span className="text-[10px] text-gray-400 uppercase tracking-wider block font-bold">Indicative Asking Price</span>
                      <span className="text-base font-extrabold text-green-800">
                        {lot.asking_price_per_quintal ? `₹${lot.asking_price_per_quintal}/Q` : 'Market Rate'}
                      </span>
                    </div>

                    {!isHarvested && (lot.status === 'OPEN' || lot.status === 'INDICATIVE_ACCEPTED') && (
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => handleOpenHarvestModal(lot)}
                        className="bg-amber-600 hover:bg-amber-700 text-white font-extrabold"
                      >
                        🌾 Mark as Harvested
                      </Button>
                    )}
                  </div>
                </div>

                {/* Bids Section for this Lot */}
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <h4 className="text-xs font-extrabold text-gray-700 uppercase tracking-wider">
                      Incoming Indicative Bids ({bids.length})
                    </h4>
                    {bids.length > 0 && (
                      <span className="text-[11px] text-gray-500 font-medium">
                        Sorted by Effective Net Realization
                      </span>
                    )}
                  </div>

                  {bids.length === 0 ? (
                    <div className="p-4 bg-gray-50 rounded-xl text-center text-xs text-gray-500 font-medium border border-dashed border-gray-200 flex flex-col sm:flex-row justify-between items-center gap-2">
                      <span>No bids received yet for this opportunity.</span>
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => handleOpenBidModal(lot as any)}
                      >
                        Submit Indicative Offer (Place Offer)
                      </Button>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {bids.map((bid) => {
                        const isBest = bid.id === bestBidId;

                        return (
                          <div
                            key={`farmer-bid-${bid.id}`}
                            className={`p-4 rounded-xl border transition-all ${
                              bid.status === 'ACCEPTED'
                                ? 'bg-green-50/80 border-green-300 ring-2 ring-green-500/20'
                                : isBest
                                ? 'bg-emerald-50/50 border-emerald-300 ring-1 ring-emerald-400/40'
                                : 'bg-gray-50 border-gray-200'
                            }`}
                          >
                            <div className="flex justify-between items-start">
                              <div>
                                <div className="flex items-center gap-1.5">
                                  <span className="font-bold text-xs text-gray-900">{bid.buyer_display_id || `Buyer #${bid.buyer_id}`}</span>
                                  {isBest && (
                                    <span className="bg-emerald-600 text-white text-[9px] font-black px-1.5 py-0.5 rounded shadow-xs">
                                      Best Net Realization
                                    </span>
                                  )}
                                </div>
                                <span className="text-[10px] text-gray-500 block">
                                  Quantity Bidded: {bid.quantity_quintals} Quintals
                                </span>
                              </div>

                              <Badge
                                variant={
                                  bid.status === 'ACCEPTED'
                                    ? 'success'
                                    : bid.status === 'SUBMITTED'
                                    ? 'info'
                                    : 'neutral'
                                }
                              >
                                {bid.status}
                              </Badge>
                            </div>

                            <div className="grid grid-cols-2 gap-2 mt-3 bg-white p-2.5 rounded-lg border border-gray-100 text-xs">
                              <div>
                                <span className="text-gray-400 block text-[10px] uppercase font-bold">Raw Offer</span>
                                <span className="font-extrabold text-green-800">₹{bid.offered_price_per_quintal}/Q</span>
                              </div>
                              <div>
                                <span className="text-gray-400 block text-[10px] uppercase font-bold">Effective Net Offer</span>
                                <span className="font-extrabold text-emerald-700">
                                  {bid.effective_offer_per_quintal !== null && bid.effective_offer_per_quintal !== undefined
                                    ? `₹${bid.effective_offer_per_quintal}/Q`
                                    : 'Unavailable'}
                                </span>
                              </div>
                            </div>

                            {bid.effective_offer_note && (
                              <p className="text-[10px] text-amber-700 mt-2 bg-amber-50 p-1.5 rounded">
                                ℹ️ Net realization unavailable — destination location unavailable
                              </p>
                            )}

                            {bid.conditions && (
                              <p className="text-xs text-gray-600 mt-2 italic bg-white/60 p-2 rounded border border-gray-100">
                                <span className="font-semibold text-gray-700">Conditions:</span> {bid.conditions}
                              </p>
                            )}

                            {bid.status === 'ACCEPTED' && (
                              <ContactSharingCard bidId={bid.id} isFarmer={true} />
                            )}

                            {/* Farmer Actions */}
                            {lot.status === 'OPEN' && bid.status === 'SUBMITTED' && (
                              <div className="mt-3 text-right">
                                <Button
                                  variant="primary"
                                  size="sm"
                                  onClick={() => setBidToAccept({ bid, lot })}
                                >
                                  Accept Indicative Offer
                                </Button>
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* FARMER VIEW: Harvested Stock Inventory Tab */}
      {activeRole === 'farmer' && activeTab === 'farmer_stock' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-black text-gray-900">
              Harvested Stock Inventory ({farmerStockLots.length})
            </h2>
            <span className="text-xs font-semibold text-gray-500">Recorded Physical Stock</span>
          </div>

          <div className="bg-amber-50 p-3 rounded-xl border border-amber-200 text-xs text-amber-900 font-medium">
            📦 <strong>Indicative pre-sowing interest does not guarantee purchase or ownership.</strong> Publish your draft stock to list it as Available Stock on the marketplace for buyer discovery.
          </div>

          {farmerStockLots.length === 0 ? (
            <Card>
              <div className="text-center py-8 text-gray-500">
                <p className="text-base font-bold">No harvested stock recorded yet.</p>
                <p className="text-xs mt-1">Go to "My Production Lots & Bids" and click "Mark as Harvested" on completed crops.</p>
              </div>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {farmerStockLots.map((stock) => (
                <Card
                  key={`farmer-stock-${stock.id}`}
                  title={stock.crop_name || `Stock Lot #${stock.id}`}
                  subtitle={`${stock.actual_quantity_quintals} Q Actual Harvested \u2022 ${stock.district || 'Karnataka'}`}
                  headerTag="h3"
                  footer={
                    <div className="flex justify-between items-center pt-2">
                      <span className="text-xs font-semibold text-gray-500">
                        Harvest Date: {stock.actual_harvest_date}
                      </span>
                      {stock.status === 'DRAFT' && (
                        <Button
                          variant="primary"
                          size="sm"
                          onClick={() => handlePublishStock(stock.id)}
                          disabled={publishingStockId === stock.id}
                        >
                          {publishingStockId === stock.id ? 'Publishing...' : '📢 Publish Stock'}
                        </Button>
                      )}
                    </div>
                  }
                >
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <Badge
                        variant={
                          stock.status === 'AVAILABLE'
                            ? 'success'
                            : stock.status === 'DRAFT'
                            ? 'warning'
                            : 'neutral'
                        }
                      >
                        {stock.status === 'DRAFT'
                          ? 'Draft Harvested Stock'
                          : stock.status === 'AVAILABLE'
                          ? 'Available Stock'
                          : stock.status}
                      </Badge>
                      <span className="text-xs font-bold text-gray-700">Stock #{stock.id}</span>
                    </div>

                    <div className="grid grid-cols-2 gap-2 bg-gray-50 p-2.5 rounded-lg text-xs">
                      <div>
                        <span className="text-gray-500 block text-[10px]">Available Quantity</span>
                        <span className="font-extrabold text-green-800 text-sm">{stock.available_quantity_quintals} Q</span>
                      </div>
                      <div>
                        <span className="text-gray-500 block text-[10px]">Asking Price</span>
                        <span className="font-extrabold text-gray-800">
                          {stock.asking_price_per_quintal ? `₹${stock.asking_price_per_quintal}/Q` : 'Not Set'}
                        </span>
                      </div>
                    </div>

                    {stock.variety && (
                      <p className="text-xs text-gray-600">
                        <span className="font-semibold text-gray-700">Variety:</span> {stock.variety}
                      </p>
                    )}

                    {stock.quality_grade && (
                      <p className="text-xs text-gray-600 italic">
                        <span className="font-semibold text-gray-700">Quality:</span> {stock.quality_grade}
                      </p>
                    )}

                    {stock.future_crop_lot_id && (
                      <p className="text-[10px] text-blue-700 bg-blue-50 p-1.5 rounded border border-blue-100">
                        🔗 Linked to Future Crop Lot #{stock.future_crop_lot_id}
                      </p>
                    )}

                    {/* Incoming Stock Offers for this Stock Lot */}
                    {(() => {
                      const sBids = farmerStockBidsMap[stock.id] || [];
                      return (
                        <div className="pt-2 border-t border-gray-100 space-y-2">
                          <h4 className="text-[11px] font-black text-gray-700 uppercase tracking-wider">
                            Incoming Stock Offers ({sBids.length})
                          </h4>
                          {sBids.length === 0 ? (
                            <p className="text-[11px] text-gray-400 italic">No buyer stock offers received yet.</p>
                          ) : (
                            <div className="space-y-2">
                              {sBids.map((sBid) => (
                                <div
                                  key={`stock-bid-${sBid.id}`}
                                  className={`p-2.5 rounded-lg border text-xs ${
                                    sBid.status === 'ACCEPTED'
                                      ? 'bg-green-50 border-green-300'
                                      : 'bg-gray-50 border-gray-200'
                                  }`}
                                >
                                  <div className="flex justify-between items-center">
                                    <span className="font-bold text-gray-800">{sBid.buyer_display_id || 'Buyer'}</span>
                                    <Badge
                                      variant={
                                        sBid.status === 'ACCEPTED'
                                          ? 'success'
                                          : sBid.status === 'SUBMITTED'
                                          ? 'info'
                                          : 'neutral'
                                      }
                                    >
                                      {sBid.status === 'ACCEPTED' ? `Allocated ${sBid.allocated_quantity_quintals} Q` : sBid.status}
                                    </Badge>
                                  </div>

                                  <div className="grid grid-cols-2 gap-1 mt-1 text-[11px]">
                                    <div>
                                      <span className="text-gray-500">Offered:</span>{' '}
                                      <span className="font-extrabold text-green-800">₹{sBid.offered_price_per_quintal}/Q</span>
                                    </div>
                                    <div>
                                      <span className="text-gray-500">Requested:</span>{' '}
                                      <span className="font-bold text-gray-800">{sBid.requested_quantity_quintals} Q</span>
                                    </div>
                                  </div>

                                  {sBid.conditions && (
                                    <p className="text-[10px] text-gray-600 mt-1 italic">
                                      Condition: {sBid.conditions}
                                    </p>
                                  )}

                                  {sBid.status === 'ACCEPTED' && (
                                    <StockBidContactSharingCard bidId={sBid.id} isFarmer={true} />
                                  )}

                                  {sBid.status === 'SUBMITTED' && stock.status !== 'SOLD' && (
                                    <div className="flex justify-end gap-1.5 mt-2">
                                      <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => handleRejectStockBid(sBid.id)}
                                        disabled={rejectingStockBidId === sBid.id}
                                        className="text-red-700 border-red-300 hover:bg-red-50 text-[10px] py-0.5 px-2"
                                      >
                                        Reject
                                      </Button>
                                      <Button
                                        variant="primary"
                                        size="sm"
                                        onClick={() => handleOpenStockBidAcceptModal(sBid, stock)}
                                        className="text-[10px] py-0.5 px-2"
                                      >
                                        Accept Offer
                                      </Button>
                                    </div>
                                  )}
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      );
                    })()}
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TRADE ORDERS TAB (Both Buyer & Farmer Roles) */}
      {activeTab === 'trade_orders' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-black text-gray-900">
              {activeRole === 'buyer' ? 'My Trade Orders' : 'Trade Orders'} ({tradeOrders.length})
            </h2>
            <span className="text-xs font-semibold text-gray-500">Post-Harvest Fulfillment Tracking</span>
          </div>

          <div className="bg-blue-50 p-3.5 rounded-xl border border-blue-200 text-xs text-blue-900 font-medium">
            ℹ️ <strong>Non-Binding Marketplace Disclaimer:</strong> TradeOrder tracks an accepted marketplace allocation. Payment and physical delivery are handled directly between buyer and farmer.
          </div>

          {tradeOrders.length === 0 ? (
            <Card>
              <div className="text-center py-8 text-gray-500">
                <p className="text-base font-bold">No active trade orders found.</p>
                <p className="text-xs mt-1">Trade orders are created automatically when a post-harvest stock offer is accepted.</p>
              </div>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {tradeOrders.map((order) => {
                const isBuyer = activeRole === 'buyer';
                const counterpartyDisplay = isBuyer
                  ? (order.farmer_display_id || `Farmer #${order.farmer_id}`)
                  : (order.buyer_display_id || `Buyer #${order.buyer_id}`);

                return (
                  <Card
                    key={`trade-order-${order.id}`}
                    title={order.crop_name || `Trade Order #${order.id}`}
                    subtitle={`${order.allocated_quantity_quintals} Q Allocated \u2022 ${order.district || 'Karnataka'}`}
                    headerTag="h3"
                    footer={
                      <div className="flex justify-between items-center pt-2">
                        <span className="text-[10px] text-gray-400 font-medium">
                          Created: {new Date(order.created_at).toLocaleDateString()}
                        </span>
                        {order.status === 'CREATED' && (
                          <div className="flex gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleOpenCancelOrderModal(order)}
                              className="text-red-700 border-red-300 hover:bg-red-50 text-xs"
                            >
                              Cancel Trade
                            </Button>
                            <Button
                              variant="primary"
                              size="sm"
                              onClick={() => handleFulfillTradeOrder(order.id)}
                              disabled={fulfillingOrderId === order.id}
                              className="text-xs"
                            >
                              {fulfillingOrderId === order.id ? 'Updating...' : 'Mark Fulfilled'}
                            </Button>
                          </div>
                        )}
                      </div>
                    }
                  >
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <Badge
                          variant={
                            order.status === 'FULFILLED'
                              ? 'success'
                              : order.status === 'CREATED'
                              ? 'info'
                              : 'neutral'
                          }
                        >
                          {order.status === 'FULFILLED'
                            ? 'Trade Fulfilled'
                            : order.status === 'CANCELLED'
                            ? 'Cancelled'
                            : 'Fulfillment Pending'}
                        </Badge>
                        <span className="text-xs font-bold text-gray-700">Order #{order.id}</span>
                      </div>

                      <div className="grid grid-cols-2 gap-2 bg-gray-50 p-2.5 rounded-lg text-xs">
                        <div>
                          <span className="text-gray-500 block text-[10px]">Agreed Price</span>
                          <span className="font-extrabold text-green-800 text-sm">₹{order.agreed_price_per_quintal}/Q</span>
                        </div>
                        <div>
                          <span className="text-gray-500 block text-[10px]">Allocated Quantity</span>
                          <span className="font-bold text-gray-800">{order.allocated_quantity_quintals} Q</span>
                        </div>
                      </div>

                      <div className="text-xs text-gray-600">
                        <span className="font-semibold text-gray-700">
                          {isBuyer ? 'Farmer:' : 'Buyer:'}
                        </span>{' '}
                        {counterpartyDisplay}
                      </div>

                      {order.status === 'CANCELLED' && (
                        <p className="text-xs text-red-800 bg-red-50 p-2 rounded border border-red-200">
                          🚫 <strong>Cancelled:</strong> {order.cancellation_reason || 'CANCELLED'} (Quantity returned to inventory)
                        </p>
                      )}

                      {order.status === 'FULFILLED' && order.fulfilled_at && (
                        <p className="text-xs text-green-800 bg-green-50 p-2 rounded border border-green-200">
                          ✅ <strong>Fulfilled:</strong> {new Date(order.fulfilled_at).toLocaleDateString()}
                        </p>
                      )}

                      {/* Render Contact Sharing card for this Trade Order */}
                      <StockBidContactSharingCard bidId={order.stock_bid_id} isFarmer={!isBuyer} />
                    </div>
                  </Card>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Buyer Modal: Submit Indicative Bid */}
      {selectedOpportunity && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <div className="border-b pb-2">
              <h3 className="text-lg font-bold text-gray-900">
                Submit Indicative Bid / Submit Indicative Offer for LOT-{selectedOpportunity.id}
              </h3>
              <p className="text-xs text-gray-500 mt-0.5">
                {selectedOpportunity.crop_name || 'Opportunity'} &bull; {selectedOpportunity.expected_quantity_quintals} Q Expected
              </p>
            </div>

            <form onSubmit={handlePlaceBid} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-gray-700 uppercase mb-1">
                  Indicative Offer Amount (₹ per Quintal)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={bidPrice}
                  onChange={(e) => setBidPrice(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg font-bold text-lg text-green-800"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-700 uppercase mb-1">
                  Quantity (Quintals)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={bidQuantity}
                  onChange={(e) => setBidQuantity(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg font-bold text-base text-gray-800"
                  required
                />
                <span className="text-[10px] text-gray-500 block mt-0.5">
                  Max lot quantity: {selectedOpportunity.expected_quantity_quintals} Q
                </span>
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-700 uppercase mb-1">
                  Optional Terms & Conditions
                </label>
                <textarea
                  value={bidConditions}
                  onChange={(e) => setBidConditions(e.target.value)}
                  placeholder="e.g. Subject to minimum 42% oil content & moisture below 8%"
                  className="w-full px-3 py-2 border rounded-lg text-xs"
                  rows={2}
                />
              </div>

              <div className="bg-green-50 p-3 rounded-lg border border-green-200 text-[11px] text-green-900">
                ℹ️ <strong>Non-Binding Intent:</strong> This pre-sowing bid represents indicative procurement intent to inform farmer cropping decisions.
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button variant="outline" type="button" onClick={() => setSelectedOpportunity(null)} disabled={submittingBid}>
                  Cancel
                </Button>
                <Button variant="primary" type="submit" disabled={submittingBid}>
                  {submittingBid ? 'Submitting...' : 'Confirm Indicative Bid'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Farmer Modal: Mark as Harvested */}
      {lotToHarvest && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <div className="border-b pb-2">
              <h3 className="text-lg font-bold text-gray-900">
                🌾 Record Actual Harvest for LOT-{lotToHarvest.id}
              </h3>
              <p className="text-xs text-gray-500 mt-0.5">
                {lotToHarvest.crop_name || 'Crop'} &bull; Expected Yield: {lotToHarvest.expected_quantity_quintals} Q
              </p>
            </div>

            <form onSubmit={handleRecordHarvest} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-gray-700 uppercase mb-1">
                  Actual Harvested Quantity (Quintals) *
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={actualHarvestQty}
                  onChange={(e) => setActualHarvestQty(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg font-bold text-base text-gray-900"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-700 uppercase mb-1">
                  Actual Harvest Date *
                </label>
                <input
                  type="date"
                  value={actualHarvestDate}
                  onChange={(e) => setActualHarvestDate(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg text-xs font-medium"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-700 uppercase mb-1">
                  Quality Grade (Optional)
                </label>
                <input
                  type="text"
                  value={harvestQualityGrade}
                  onChange={(e) => setHarvestQualityGrade(e.target.value)}
                  placeholder="e.g. Grade A, Standard, FAQ"
                  className="w-full px-3 py-2 border rounded-lg text-xs"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-700 uppercase mb-1">
                  Asking Price (₹ per Quintal, Optional)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={harvestAskingPrice}
                  onChange={(e) => setHarvestAskingPrice(e.target.value)}
                  placeholder="e.g. 6200"
                  className="w-full px-3 py-2 border rounded-lg text-xs font-semibold text-green-800"
                />
              </div>

              <div className="bg-amber-50 p-3 rounded-lg border border-amber-200 text-[11px] text-amber-900 font-medium">
                📦 <strong>Stock Creation Note:</strong> Recording harvest creates a Draft Stock Lot in your inventory. You can review and publish it whenever you choose.
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button variant="outline" type="button" onClick={() => setLotToHarvest(null)} disabled={submittingHarvest}>
                  Cancel
                </Button>
                <Button variant="primary" type="submit" disabled={submittingHarvest}>
                  {submittingHarvest ? 'Recording Harvest...' : 'Confirm Actual Harvest'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Farmer Modal: Confirm Acceptance */}
      {bidToAccept && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <div className="border-b pb-2">
              <h3 className="text-lg font-bold text-gray-900">
                Confirm Indicative Offer Acceptance
              </h3>
              <p className="text-xs text-gray-500 mt-0.5">
                {bidToAccept.lot.crop_name || 'Future Crop Opportunity'} &bull; Bid #{bidToAccept.bid.id}
              </p>
            </div>

            <div className="space-y-2 bg-gray-50 p-3 rounded-xl text-xs">
              <div className="flex justify-between">
                <span className="text-gray-500">Buyer:</span>
                <span className="font-bold text-gray-800">{bidToAccept.bid.buyer_display_id || `Buyer #${bidToAccept.bid.buyer_id}`}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Offered Price:</span>
                <span className="font-bold text-green-800">₹{bidToAccept.bid.offered_price_per_quintal}/Q</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Effective Net Realization:</span>
                <span className="font-bold text-emerald-700">
                  {bidToAccept.bid.effective_offer_per_quintal !== null && bidToAccept.bid.effective_offer_per_quintal !== undefined
                    ? `₹${bidToAccept.bid.effective_offer_per_quintal}/Q`
                    : 'Unavailable'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Quantity Bidded:</span>
                <span className="font-bold text-gray-800">{bidToAccept.bid.quantity_quintals} Quintals</span>
              </div>
              {bidToAccept.bid.conditions && (
                <div className="pt-1 border-t border-gray-200">
                  <span className="text-gray-500 block">Conditions:</span>
                  <span className="font-medium text-gray-700 italic">{bidToAccept.bid.conditions}</span>
                </div>
              )}
            </div>

            <div className="bg-amber-50 p-3 rounded-lg border border-amber-200 text-[11px] text-amber-900 font-medium">
              ⚖️ <strong>Product Note:</strong> This is an indicative pre-sowing bid, not a legally binding purchase contract. Accepting confirms your preferred procurement intent and marks this lot as Indicative Accepted.
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" type="button" onClick={() => setBidToAccept(null)} disabled={acceptingBid}>
                Cancel
              </Button>
              <Button variant="primary" type="button" onClick={handleConfirmAcceptBid} disabled={acceptingBid}>
                {acceptingBid ? 'Accepting...' : 'Confirm Acceptance'}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Buyer Modal: Submit Post-Harvest Stock Offer */}
      {selectedStockLot && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <div className="border-b pb-2">
              <h3 className="text-lg font-bold text-gray-900">
                Submit Offer for Stock Lot #{selectedStockLot.id}
              </h3>
              <p className="text-xs text-gray-500 mt-0.5">
                {selectedStockLot.crop_name || 'Harvested Stock'} &bull; {selectedStockLot.available_quantity_quintals} Q Available
              </p>
            </div>

            <form onSubmit={handlePlaceStockBid} className="space-y-4">
              <div>
                <label htmlFor="stock-bid-offered-price" className="block text-xs font-bold text-gray-700 uppercase mb-1">
                  Offered Price (₹ per Quintal) *
                </label>
                <input
                  id="stock-bid-offered-price"
                  type="number"
                  step="0.01"
                  value={stockBidPrice}
                  onChange={(e) => setStockBidPrice(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg font-bold text-lg text-green-800"
                  required
                />
              </div>

              <div>
                <label htmlFor="stock-bid-requested-qty" className="block text-xs font-bold text-gray-700 uppercase mb-1">
                  Requested Quantity (Quintals) *
                </label>
                <input
                  id="stock-bid-requested-qty"
                  type="number"
                  step="0.1"
                  value={stockBidQty}
                  onChange={(e) => setStockBidQty(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg font-bold text-base text-gray-800"
                  required
                />
                <span className="text-[10px] text-gray-500 block mt-0.5">
                  Available stock: {selectedStockLot.available_quantity_quintals} Q
                </span>
              </div>

              <div>
                <label htmlFor="stock-bid-conditions" className="block text-xs font-bold text-gray-700 uppercase mb-1">
                  Optional Terms & Conditions
                </label>
                <textarea
                  id="stock-bid-conditions"
                  value={stockBidConditions}
                  onChange={(e) => setStockBidConditions(e.target.value)}
                  placeholder="e.g. Prompt payment upon physical inspection"
                  className="w-full px-3 py-2 border rounded-lg text-xs"
                  rows={2}
                />
              </div>

              <div className="bg-amber-50 p-3 rounded-lg border border-amber-200 text-[11px] text-amber-900">
                📦 <strong>Physical Stock Offer:</strong> This offer is submitted directly against physical inventory. Farmer will choose allocated quantity upon acceptance.
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button variant="outline" type="button" onClick={() => setSelectedStockLot(null)} disabled={submittingStockBid}>
                  Cancel
                </Button>
                <Button variant="primary" type="submit" disabled={submittingStockBid}>
                  {submittingStockBid ? 'Submitting...' : 'Submit Stock Offer'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Farmer Modal: Allocate & Accept Stock Offer */}
      {stockBidToAccept && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <div className="border-b pb-2">
              <h3 className="text-lg font-bold text-gray-900">
                Allocate Harvested Stock & Accept Offer
              </h3>
              <p className="text-xs text-gray-500 mt-0.5">
                Offer #{stockBidToAccept.bid.id} &bull; Buyer: {stockBidToAccept.bid.buyer_display_id || 'Buyer'}
              </p>
            </div>

            <form onSubmit={handleConfirmAcceptStockBid} className="space-y-4">
              <div className="space-y-2 bg-gray-50 p-3 rounded-xl text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-500">Offered Price:</span>
                  <span className="font-bold text-green-800">₹{stockBidToAccept.bid.offered_price_per_quintal}/Q</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Requested Quantity:</span>
                  <span className="font-bold text-gray-800">{stockBidToAccept.bid.requested_quantity_quintals} Q</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Available Stock Remaining:</span>
                  <span className="font-extrabold text-emerald-800">{stockBidToAccept.stock.available_quantity_quintals} Q</span>
                </div>
              </div>

              <div>
                <label htmlFor="stock-bid-allocated-qty" className="block text-xs font-bold text-gray-700 uppercase mb-1">
                  How many quintals do you want to allocate? *
                </label>
                <input
                  id="stock-bid-allocated-qty"
                  type="number"
                  step="0.1"
                  value={allocatedQty}
                  onChange={(e) => setAllocatedQty(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg font-bold text-lg text-green-900"
                  required
                />
                <span className="text-[10px] text-gray-500 block mt-0.5">
                  Max allocatable: {Math.min(stockBidToAccept.bid.requested_quantity_quintals, stockBidToAccept.stock.available_quantity_quintals)} Q
                </span>
              </div>

              <div className="bg-green-50 p-3 rounded-lg border border-green-200 text-[11px] text-green-900">
                🤝 <strong>Mutual Consent:</strong> Accepting creates a mutual contact sharing record. Once both parties consent, contact details are unlocked.
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button variant="outline" type="button" onClick={() => setStockBidToAccept(null)} disabled={acceptingStockBid}>
                  Cancel
                </Button>
                <Button variant="primary" type="submit" disabled={acceptingStockBid}>
                  {acceptingStockBid ? 'Allocating & Accepting...' : 'Confirm Allocation'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Cancel Trade Order */}
      {orderToCancel && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <div className="border-b pb-2">
              <h3 className="text-lg font-bold text-gray-900">
                Cancel Trade Order #{orderToCancel.id}
              </h3>
              <p className="text-xs text-gray-500 mt-0.5">
                {orderToCancel.crop_name || 'Trade Order'} &bull; {orderToCancel.allocated_quantity_quintals} Q Allocated
              </p>
            </div>

            <form onSubmit={handleConfirmCancelTradeOrder} className="space-y-4">
              <div>
                <label htmlFor="cancel-reason-select" className="block text-xs font-bold text-gray-700 uppercase mb-1">
                  Reason for Cancellation *
                </label>
                <select
                  id="cancel-reason-select"
                  value={cancellationReason}
                  onChange={(e) => setCancellationReason(e.target.value as TradeOrderCancellationReason)}
                  className="w-full px-3 py-2 border rounded-lg text-xs font-medium text-gray-800"
                >
                  <option value="BUYER_CANCELLED">Buyer Cancelled</option>
                  <option value="FARMER_CANCELLED">Farmer Cancelled</option>
                  <option value="QUALITY_ISSUE">Quality Mismatch / Issue</option>
                  <option value="NO_SHOW">No Show</option>
                  <option value="OTHER">Other Reason</option>
                </select>
              </div>

              <div className="bg-amber-50 p-3 rounded-lg border border-amber-200 text-[11px] text-amber-900">
                ⚠️ <strong>Quantity Restoration:</strong> Cancelling this trade order will return {orderToCancel.allocated_quantity_quintals} Q back to the stock lot's available inventory.
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button variant="outline" type="button" onClick={() => setOrderToCancel(null)} disabled={cancellingOrder}>
                  Close
                </Button>
                <Button variant="primary" type="submit" disabled={cancellingOrder} className="bg-red-600 hover:bg-red-700 text-white font-bold">
                  {cancellingOrder ? 'Cancelling...' : 'Confirm Cancellation'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* List New Crop Lot Modal */}
      <PlanCropModal
        isOpen={showNewLotModal}
        onClose={() => setShowNewLotModal(false)}
        onSuccess={loadData}
      />
    </div>
  );
}
