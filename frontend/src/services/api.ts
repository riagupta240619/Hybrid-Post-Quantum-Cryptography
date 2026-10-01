import type { Device, DeviceCreate, HealthResponse } from "../types/api";

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
};