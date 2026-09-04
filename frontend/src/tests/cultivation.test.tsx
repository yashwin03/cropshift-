import { vi, describe, test, expect, beforeEach } from 'vitest';
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import apiClient from '../services/apiClient';
import {
  getCultivationRecords,
  createCultivationRecord,
  updateCultivationRecord,
} from '../services/cultivationService';
import AddCropModal from '../components/farmer/AddCropModal';
import MyCropsSection from '../components/farmer/MyCropsSection';

vi.mock('../services/apiClient', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
  AxiosError: class extends Error {},
}));

describe('Crop Cultivation Record System Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('cultivationService dispatches correctly to backend endpoints', async () => {
    const mockRecord = {
      id: 1,
      farmer_id: 501,
      farm_id: 1,
      crop_id: 2,
      crop_name: 'Groundnut',
      variety: 'TMV-2',
      area_acres: 2.5,
      cultivation_stage: 'GROWING',
      evidence_status: 'FARMER_DECLARED',
      created_at: '2025-06-15',
      updated_at: '2025-06-15',
    };

    vi.mocked(apiClient.get).mockResolvedValue({ data: [mockRecord] });
    vi.mocked(apiClient.post).mockResolvedValue({ data: mockRecord });
    vi.mocked(apiClient.put).mockResolvedValue({ data: { ...mockRecord, cultivation_stage: 'READY_FOR_HARVEST' } });

    const list = await getCultivationRecords();
    expect(apiClient.get).toHaveBeenCalledWith('/api/v1/cultivation-records');
    expect(list).toEqual([mockRecord]);

    const created = await createCultivationRecord({
      farm_id: 1,
      crop_id: 2,
      area_acres: 2.5,
      cultivation_stage: 'GROWING',
    });
    expect(apiClient.post).toHaveBeenCalledWith('/api/v1/cultivation-records', {
      farm_id: 1,
      crop_id: 2,
      area_acres: 2.5,
      cultivation_stage: 'GROWING',
    });
    expect(created).toEqual(mockRecord);

    const updated = await updateCultivationRecord(1, { cultivation_stage: 'READY_FOR_HARVEST' });
    expect(apiClient.put).toHaveBeenCalledWith('/api/v1/cultivation-records/1', {
      cultivation_stage: 'READY_FOR_HARVEST',
    });
    expect(updated.cultivation_stage).toEqual('READY_FOR_HARVEST');
  });

  test('AddCropModal renders required fields and submits form', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({
      data: {
        id: 10,
        farmer_id: 501,
        farm_id: 1,
        crop_id: 2,
        crop_name: 'Groundnut',
        area_acres: 3.0,
        cultivation_stage: 'GROWING',
        evidence_status: 'FARMER_DECLARED',
      },
    });

    const handleClose = vi.fn();
    const handleSuccess = vi.fn();

    render(
      <AddCropModal
        isOpen={true}
        onClose={handleClose}
        onSuccess={handleSuccess}
        initialCropName="Groundnut"
        initialStage="GROWING"
      />
    );

    expect(screen.getByText('Add Crop to My Farm')).toBeInTheDocument();
    expect(screen.getByText(/Save Record|Confirm & Save/i)).toBeInTheDocument();

    const submitBtn = screen.getByText(/Save Record|Confirm & Save/i);
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(apiClient.post).toHaveBeenCalled();
      expect(handleSuccess).toHaveBeenCalled();
    });
  });

  test('MyCropsSection renders empty state when no crops exist', async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: [] });

    render(<MyCropsSection />);

    await waitFor(() => {
      expect(screen.getByText('No crops added yet.')).toBeInTheDocument();
    });
  });

  test('MyCropsSection renders cultivation record cards', async () => {
    const mockRecords = [
      {
        id: 101,
        farmer_id: 501,
        farm_id: 1,
        crop_id: 2,
        crop_name: 'Groundnut',
        variety: 'TMV-2',
        area_acres: 3.5,
        cultivation_stage: 'GROWING',
        evidence_status: 'FARMER_DECLARED',
        district: 'Dharwad',
        state: 'Karnataka',
        expected_yield_quintals: 30.0,
        created_at: '2025-06-15',
        updated_at: '2025-06-15',
      },
    ];

    vi.mocked(apiClient.get).mockResolvedValue({ data: mockRecords });

    render(<MyCropsSection />);

    await waitFor(() => {
      expect(screen.getByText('Groundnut')).toBeInTheDocument();
      expect(screen.getByText('TMV-2')).toBeInTheDocument();
      expect(screen.getByText(/3\.5/)).toBeInTheDocument();
      expect(screen.getAllByText('GROWING').length).toBeGreaterThan(0);
    });
  });
});
