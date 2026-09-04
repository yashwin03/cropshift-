import apiClient from './apiClient';
import type {
  HarvestRequest,
  StockLotCreate,
  StockLotUpdate,
  StockLot,
  StockLotMarketplaceView,
} from '../types/api';

export const harvestFutureCropLot = async (
  lotId: number,
  payload: HarvestRequest
): Promise<StockLot> => {
  const response = await apiClient.post<StockLot>(
    `/api/v1/farmer/future-crop-lots/${lotId}/harvest`,
    payload
  );
  return response.data;
};

export const createDirectStockLot = async (
  payload: StockLotCreate
): Promise<StockLot> => {
  const response = await apiClient.post<StockLot>('/api/v1/farmer/stock-lots', payload);
  return response.data;
};

export const getFarmerStockLotsMe = async (): Promise<StockLot[]> => {
  const response = await apiClient.get<StockLot[]>('/api/v1/farmer/stock-lots/me');
  return response.data;
};

export const getFarmerStockLot = async (stockId: number): Promise<StockLot> => {
  const response = await apiClient.get<StockLot>(`/api/v1/farmer/stock-lots/${stockId}`);
  return response.data;
};

export const updateFarmerStockLot = async (
  stockId: number,
  payload: StockLotUpdate
): Promise<StockLot> => {
  const response = await apiClient.put<StockLot>(
    `/api/v1/farmer/stock-lots/${stockId}`,
    payload
  );
  return response.data;
};

export const publishFarmerStockLot = async (
  stockId: number
): Promise<StockLot> => {
  const response = await apiClient.post<StockLot>(
    `/api/v1/farmer/stock-lots/${stockId}/publish`
  );
  return response.data;
};

export const cancelFarmerStockLot = async (
  stockId: number
): Promise<StockLot> => {
  const response = await apiClient.delete<StockLot>(
    `/api/v1/farmer/stock-lots/${stockId}`
  );
  return response.data;
};

export const getOpenStockLots = async (): Promise<StockLotMarketplaceView[]> => {
  const response = await apiClient.get<StockLotMarketplaceView[]>('/api/v1/stock-lots/open');
  return response.data;
};
