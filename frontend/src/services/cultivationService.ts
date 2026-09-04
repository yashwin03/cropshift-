import apiClient from './apiClient';
import type {
  CropCultivationRecord,
  CropCultivationCreatePayload,
  CropCultivationUpdatePayload,
  RecordHarvestPayload,
} from '../types/api';

export const getCultivationRecords = async (): Promise<CropCultivationRecord[]> => {
  const response = await apiClient.get<CropCultivationRecord[]>('/api/v1/cultivation-records');
  return response.data;
};

export const getCultivationRecord = async (id: number): Promise<CropCultivationRecord> => {
  const response = await apiClient.get<CropCultivationRecord>(`/api/v1/cultivation-records/${id}`);
  return response.data;
};

export const createCultivationRecord = async (
  payload: CropCultivationCreatePayload
): Promise<CropCultivationRecord> => {
  const response = await apiClient.post<CropCultivationRecord>('/api/v1/cultivation-records', payload);
  return response.data;
};

export const updateCultivationRecord = async (
  id: number,
  payload: CropCultivationUpdatePayload
): Promise<CropCultivationRecord> => {
  const response = await apiClient.put<CropCultivationRecord>(`/api/v1/cultivation-records/${id}`, payload);
  return response.data;
};

export const deleteCultivationRecord = async (id: number): Promise<{ message: string }> => {
  const response = await apiClient.delete<{ message: string }>(`/api/v1/cultivation-records/${id}`);
  return response.data;
};

export const recordHarvest = async (
  id: number,
  payload: RecordHarvestPayload
): Promise<CropCultivationRecord> => {
  const response = await apiClient.post<CropCultivationRecord>(
    `/api/v1/cultivation-records/${id}/harvest`,
    payload
  );
  return response.data;
};
