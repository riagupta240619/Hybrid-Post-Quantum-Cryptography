export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

export interface Device {
  id: number;
  device_id: string;
  device_type: string;
  status: string;
  created_at: string;
  last_seen: string | null;
}

export interface DeviceCreate {
  device_id: string;
  device_type: string;
}