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

export interface CryptoInfo {
  version: number;
  classical_kem: string;
  pq_kem: string;
  aead: string;
  signature: string;
  kdf: string;
  key_storage: string;
  private_keys_exposed: boolean;
}

export interface EncryptPackage {
  version: number;
  device_id: string;
  classical_kem: string;
  pq_kem: string;
  aead: string;
  signature: string;
  kdf: string;
  ephemeral_public_key: string;
  kem_ciphertext: string;
  nonce: string;
  associated_data: string;
  ciphertext: string;
  signature_value: string;
  sequence?: number;
}

export interface EncryptResponse {
  package: EncryptPackage;
}

export interface DecryptResponse {
  plaintext: string;
}

export interface IotStatus {
  enabled: boolean;
  connected: boolean;
  broker: string;
  telemetry_topic: string;
  replay_protection: boolean;
}

export interface IotMessage {
  device_id?: string | null;
  topic: string;
  received_at: string;
  telemetry?: Record<string, unknown> | null;
  security: Record<string, unknown>;
  error?: string | null;
}

export interface IotPublishResponse {
  device_id: string;
  topic: string;
  security: Record<string, string>;
  package: EncryptPackage;
}
