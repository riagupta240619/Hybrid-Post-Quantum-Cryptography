import { useCallback, useEffect, useState, type FormEvent } from "react";
import { Plus, RefreshCw } from "lucide-react";
import { Button } from "../components/Button";
import { Card } from "../components/Card";
import { api } from "../services/api";
import type { Device } from "../types/api";

function formatDate(value: string | null): string {
  if (!value) return "Never seen";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function DevicesPage() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [deviceId, setDeviceId] = useState("");
  const [deviceType, setDeviceType] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const refreshDevices = useCallback(async () => {
    setLoading(true);
    try {
      setDevices(await api.listDevices());
      setError(null);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Could not load devices",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refreshDevices();
  }, [refreshDevices]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    setNotice(null);
    try {
      await api.createDevice({
        device_id: deviceId.trim(),
        device_type: deviceType.trim(),
      });
      setDeviceId("");
      setDeviceType("");
      setNotice("Device registered.");
      await refreshDevices();
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Could not create device",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-7">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="mb-2 text-xs font-semibold uppercase text-mint">
            Inventory
          </p>
          <h1 className="font-display text-3xl font-semibold">Devices</h1>
          <p className="mt-2 text-sm text-muted">
            Registered devices stored in the platform database.
          </p>
        </div>
        <Button
          variant="secondary"
          onClick={() => void refreshDevices()}
          disabled={loading}
          aria-label="Refresh devices"
        >
          <RefreshCw size={15} /> Refresh
        </Button>
      </div>

      <Card className="p-5">
        <h2 className="font-display text-base font-semibold">
          Register device
        </h2>
        <form
          className="mt-4 grid gap-4 sm:grid-cols-[1fr_1fr_auto] sm:items-end"
          onSubmit={handleSubmit}
        >
          <label className="block text-xs font-medium text-muted">
            Device ID
            <input
              className="mt-2 block w-full rounded-md border border-line bg-ink px-3 py-2.5 text-sm text-white outline-none transition placeholder:text-[#647270] focus:border-mint"
              value={deviceId}
              onChange={(event) => setDeviceId(event.target.value)}
              placeholder="sensor-001"
              maxLength={128}
              required
            />
          </label>
          <label className="block text-xs font-medium text-muted">
            Device type
            <input
              className="mt-2 block w-full rounded-md border border-line bg-ink px-3 py-2.5 text-sm text-white outline-none transition placeholder:text-[#647270] focus:border-mint"
              value={deviceType}
              onChange={(event) => setDeviceType(event.target.value)}
              placeholder="temperature-sensor"
              maxLength={64}
              required
            />
          </label>
          <Button type="submit" disabled={saving}>
            <Plus size={16} />
            {saving ? "Registering..." : "Add device"}
          </Button>
        </form>
        {error && (
          <p
            role="alert"
            className="mt-4 rounded-md border border-amber/25 bg-amber/10 px-3 py-2 text-sm text-amber"
          >
            {error}
          </p>
        )}
        {notice && (
          <p role="status" className="mt-4 text-sm text-mint">
            {notice}
          </p>
        )}
      </Card>

      <Card className="overflow-hidden">
        <div className="flex items-center justify-between border-b border-line px-5 py-4">
          <h2 className="font-display text-base font-semibold">
            Registered devices
          </h2>
          <span className="text-xs text-muted">{devices.length} total</span>
        </div>
        {loading ? (
          <p className="px-5 py-8 text-sm text-muted">Loading devices...</p>
        ) : devices.length === 0 ? (
          <p className="px-5 py-8 text-sm text-muted">
            No devices registered yet.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[620px] text-left text-sm">
              <thead className="bg-[#141c1e] text-xs uppercase text-muted">
                <tr>
                  <th className="px-5 py-3 font-medium">Device</th>
                  <th className="px-5 py-3 font-medium">Type</th>
                  <th className="px-5 py-3 font-medium">Status</th>
                  <th className="px-5 py-3 font-medium">Last seen</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {devices.map((device) => (
                  <tr key={device.id}>
                    <td className="px-5 py-4 font-medium text-white">
                      {device.device_id}
                    </td>
                    <td className="px-5 py-4 text-muted">
                      {device.device_type}
                    </td>
                    <td className="px-5 py-4">
                      <span className="inline-flex items-center rounded-full border border-line bg-ink px-2.5 py-1 text-xs text-muted">
                        {device.status}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-muted">
                      {formatDate(device.last_seen)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
