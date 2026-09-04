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

export const uploadQualityCertificate = async (
  stockId: number,
  file: File
): Promise<StockLot> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await apiClient.post<StockLot>(
    `/api/v1/farmer/stock-lots/${stockId}/quality-certificate`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
};

export const getQualityCertificateBlob = async (
  stockId: number
): Promise<{ blob: Blob; filename: string }> => {
  const response = await apiClient.get(`/api/v1/stock-lots/${stockId}/certificate`, {
    responseType: 'blob',
  });
  const contentDisposition = response.headers['content-disposition'];
  let filename = `quality_certificate_${stockId}.pdf`;
  if (contentDisposition) {
    const match = contentDisposition.match(/filename="?([^";]+)"?/);
    if (match && match[1]) {
      filename = match[1];
    }
  }
  return { blob: response.data, filename };
};

