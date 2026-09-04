import apiClient from './apiClient';
import type { PeerProofResponse } from '../types/api';

export async function getPeerProof(
  cropId: number,
  farmId?: number,
  district?: string,
  radiusKm: number = 50,
  latitude?: number,
  longitude?: number
): Promise<PeerProofResponse> {
  const params: Record<string, any> = { radius_km: radiusKm };
  if (farmId) params.farm_id = farmId;
  if (district) params.district = district;
  if (latitude != null) params.latitude = latitude;
  if (longitude != null) params.longitude = longitude;

  const response = await apiClient.get<PeerProofResponse>(`/api/v1/peer-proof/${cropId}`, { params });
  return response.data;
}

export async function requestPeerContact(peerProofId: number): Promise<{
  id: number;
  farmer_display_name: string;
  district: string;
  state: string;
  phone: string;
  email: string;
  contactable: boolean;
  verification_status: string;
}> {
  const response = await apiClient.post('/peer-proof/contact-request', { peer_proof_id: peerProofId });
  return response.data;
}
