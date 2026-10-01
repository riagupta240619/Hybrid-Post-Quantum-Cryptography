import { useEffect, useState } from "react";
import { CheckCircle2, Cpu, Database, KeyRound, Radio, RefreshCw, Server, ShieldCheck } from "lucide-react";
import { Button } from "../components/Button";
import { Card } from "../components/Card";
import { StatusBadge } from "../components/StatusBadge";
import { api } from "../services/api";
import type { CryptoIdentity, CryptoInfo, HealthResponse, IotStatus } from "../types/api";

export function SystemPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [crypto, setCrypto] = useState<CryptoInfo | null>(null);
  const [iot, setIot] = useState<IotStatus | null>(null);
  const [gateway, setGateway] = useState<CryptoIdentity | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    setError(null);
    try {
      const [h, c, i] = await Promise.all([api.health(), api.cryptoInfo(), api.iotStatus()]);
      setHealth(h);
      setCrypto(c);
      setIot(i);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not load platform status");
    }
  }

  useEffect(() => { void refresh(); }, []);

  async function provisionGateway() {
    setBusy(true);
    setError(null);
    try {
      setGateway(await api.provisionGateway());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Gateway provisioning failed");
    } finally {
      setBusy(false);
    }
  }

  const services = [
    { name: "FastAPI", icon: Server, state: Boolean(health) },
    { name: "PostgreSQL", icon: Database, state: Boolean(health) },
    { name: "MQTT / Mosquitto", icon: Radio, state: Boolean(iot?.connected) },
    { name: "Hybrid crypto", icon: ShieldCheck, state: Boolean(crypto) },
  ];

  return (
    <div className="space-y-7">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-mint">Platform</p>
          <h1 className="font-display text-3xl font-semibold md:text-4xl">System Status</h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">Inspect service health, cryptographic configuration, and the gateway identity.</p>
        </div>
        <Button variant="secondary" onClick={() => void refresh()}><RefreshCw size={14}/>Refresh</Button>
      </div>

      {error && <div className="rounded-md border border-amber/25 bg-amber/10 px-4 py-3 text-sm text-amber">{error}</div>}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {services.map(({ name, icon: Icon, state }) => (
          <Card key={name} className="p-5">
            <div className="flex items-center justify-between"><Icon size={18} className="text-mint"/><StatusBadge status={state ? "connected" : "disconnected"}/></div>
            <div className="mt-4 font-display font-semibold">{name}</div>
          </Card>
        ))}
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <Card className="p-5">
          <div className="flex items-center gap-3"><KeyRound size={18} className="text-mint"/><div><h2 className="font-display font-semibold">Cryptographic configuration</h2><p className="text-xs text-muted">Active protocol metadata</p></div></div>
          {crypto ? (
            <div className="mt-5 space-y-2">
              {[["Classical KEM", crypto.classical_kem], ["Post-quantum KEM", crypto.pq_kem], ["KDF", crypto.kdf], ["AEAD", crypto.aead], ["Signature", crypto.signature], ["Key storage", crypto.key_storage]].map(([label, value]) => (
                <div key={label} className="flex items-center justify-between gap-4 rounded-md border border-line bg-ink px-3 py-2.5 text-sm"><span className="text-muted">{label}</span><span className="font-medium text-right">{value}</span></div>
              ))}
              <div className="flex items-center gap-2 pt-3 text-xs text-mint"><CheckCircle2 size={14}/>Private keys are not exposed through metadata.</div>
            </div>
          ) : <p className="mt-5 text-sm text-muted">Loading crypto metadata...</p>}
        </Card>

        <Card className="p-5">
          <div className="flex items-center gap-3"><Cpu size={18} className="text-mint"/><div><h2 className="font-display font-semibold">IoT gateway</h2><p className="text-xs text-muted">MQTT and replay controls</p></div></div>
          {iot ? (
            <div className="mt-5 space-y-2">
              {[["Broker", iot.broker], ["Telemetry topic", iot.telemetry_topic], ["Replay protection", iot.replay_protection ? "Enabled" : "Disabled"], ["Device identity mode", iot.device_identity_mode ? "Enabled" : "Disabled"]].map(([label, value]) => (
                <div key={label} className="flex items-center justify-between gap-4 rounded-md border border-line bg-ink px-3 py-2.5 text-sm"><span className="text-muted">{label}</span><span className="font-medium text-right">{value}</span></div>
              ))}
            </div>
          ) : <p className="mt-5 text-sm text-muted">Loading MQTT status...</p>}
        </Card>
      </div>

      <Card className="p-5">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div><h2 className="font-display font-semibold">Gateway cryptographic identity</h2><p className="mt-1 text-xs text-muted">Provision or refresh the gateway's process-memory identity.</p></div>
          <Button onClick={() => void provisionGateway()} disabled={busy}><KeyRound size={14}/>{busy ? "Provisioning..." : "Provision gateway"}</Button>
        </div>
        {gateway && <div className="mt-5 grid gap-3 md:grid-cols-3">{[["X25519", gateway.x25519_public_key], ["ML-KEM-768", gateway.mlkem_public_key], ["ML-DSA-65", gateway.mldsa_public_key]].map(([name, value]) => <div key={name} className="rounded-md border border-line bg-ink p-3"><div className="text-xs font-semibold">{name}</div><div className="mt-2 break-all font-mono text-[10px] leading-4 text-muted">{value}</div></div>)}</div>}
      </Card>
    </div>
  );
}
