import type {
  CryptoInfo,
  DecryptResponse,
  Device,
  DeviceCreate,
  EncryptResponse,
  HealthResponse,
  IotMessage,
  IotPublishResponse,
  IotStatus,
} from "../types/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body: unknown = await response.json();
      if (typeof body === "object" && body !== null && "detail" in body) {
        const detail = body.detail;
        if (typeof detail === "string") message = detail;
      }
    } catch {
      message = `Request failed (${response.status})`;
    }
    throw new Error(message);
  }

  return (await response.json()) as T;
}

export const api = {
  health: () => request<HealthResponse>("/api/v1/health"),
  listDevices: () => request<Device[]>("/api/v1/devices"),
  createDevice: (device: DeviceCreate) =>
    request<Device>("/api/v1/devices", {
      method: "POST",
      body: JSON.stringify(device),
    }),
  cryptoInfo: () => request<CryptoInfo>("/api/v1/crypto/info"),
  encrypt: (payload: {
    plaintext: string;
    device_id: string;
    associated_data?: string;
    sequence?: number;
  }) =>
    request<EncryptResponse>("/api/v1/crypto/encrypt", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  decrypt: (packageData: EncryptResponse["package"]) =>
    request<DecryptResponse>("/api/v1/crypto/decrypt", {
      method: "POST",
      body: JSON.stringify({ package: packageData }),
    }),
  iotStatus: () => request<IotStatus>("/api/v1/iot/status"),
  iotMessages: () => request<IotMessage[]>("/api/v1/iot/messages"),
  provisionDevice: (deviceId: string) => request<CryptoIdentity>(`/api/v1/security/devices/${encodeURIComponent(deviceId)}/provision`, { method: "POST" }),\n  deviceCrypto: (deviceId: string) => request<CryptoIdentity>(`/api/v1/security/devices/${encodeURIComponent(deviceId)}/crypto`),\n  securityEvents: () => request<SecurityEvent[]>(`/api/v1/security/events`),\n  auditLogs: () => request<AuditLog[]>(`/api/v1/security/audit`),\n  runBenchmark: (payload: { iterations: number; payload_bytes: number }) => request<BenchmarkResponse>("/api/v1/benchmarks/run", { method: "POST", body: JSON.stringify(payload) }),\n  benchmarkHistory: () => request<Array<Record<string, unknown>>>("/api/v1/benchmarks/history"),\n  publishTelemetry: (payload: {
    device_id: string;
    telemetry: Record<string, unknown>;
    associated_data?: string;
    sequence: number;
  }) =>
    request<IotPublishResponse>("/api/v1/iot/publish", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
