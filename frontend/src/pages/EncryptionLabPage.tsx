import { useEffect, useState } from "react";
import { CheckCircle2, Copy, Fingerprint, LockKeyhole, ShieldCheck } from "lucide-react";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { api } from "../services/api";
import type { CryptoInfo, EncryptPackage } from "../types/api";

const algorithms = ["X25519", "ML-KEM-768", "HKDF-SHA384", "AES-256-GCM", "ML-DSA-65"];

export function EncryptionLabPage() {
  const [plaintext, setPlaintext] = useState('{"temperature_c":24.8,"humidity_percent":61.2,"device":"sensor-001"}');
  const [deviceId, setDeviceId] = useState("demo-device");
  const [info, setInfo] = useState<CryptoInfo | null>(null);
  const [packageData, setPackageData] = useState<EncryptPackage | null>(null);
  const [decrypted, setDecrypted] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { void api.cryptoInfo().then(setInfo).catch(() => setError("Crypto service is unavailable")); }, []);

  async function encrypt() {
    setBusy(true); setError(null); setDecrypted(null);
    try { setPackageData((await api.encrypt({ plaintext, device_id: deviceId.trim() || "demo-device" })).package); }
    catch (e) { setError(e instanceof Error ? e.message : "Encryption failed"); }
    finally { setBusy(false); }
  }

  async function decrypt() {
    if (!packageData) return;
    setBusy(true); setError(null);
    try { setDecrypted((await api.decrypt(packageData)).plaintext); }
    catch (e) { setError(e instanceof Error ? e.message : "Decryption failed"); }
    finally { setBusy(false); }
  }

  async function copyPackage() {
    if (!packageData) return;
    await navigator.clipboard.writeText(JSON.stringify(packageData, null, 2));
    setCopied(true); window.setTimeout(() => setCopied(false), 1400);
  }

  return <div className="space-y-7">
    <div><p className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-mint">Cryptography</p><h1 className="font-display text-3xl font-semibold md:text-4xl">Encryption Lab</h1><p className="mt-2 max-w-2xl text-sm leading-6 text-muted">Run a real hybrid encryption round-trip and inspect the authenticated package.</p></div>
    {error && <div className="rounded-md border border-amber/25 bg-amber/10 px-4 py-3 text-sm text-amber">{error}</div>}
    <div className="grid gap-5 xl:grid-cols-[1.15fr_.85fr]">
      <Card className="p-5">
        <div className="flex items-center gap-3"><LockKeyhole size={19} className="text-mint"/><div><h2 className="font-display font-semibold">Encrypt payload</h2><p className="text-xs text-muted">AES-256-GCM + hybrid key establishment</p></div></div>
        <label className="mt-6 block text-xs font-medium text-muted">Device ID<input value={deviceId} onChange={e=>setDeviceId(e.target.value)} className="mt-2 w-full rounded-md border border-line bg-ink px-3 py-2.5 text-sm outline-none focus:border-mint"/></label>
        <label className="mt-4 block text-xs font-medium text-muted">Plaintext<textarea value={plaintext} onChange={e=>setPlaintext(e.target.value)} rows={8} className="mt-2 w-full resize-y rounded-md border border-line bg-ink px-3 py-3 font-mono text-xs leading-5 outline-none focus:border-mint"/></label>
        <div className="mt-4 flex flex-wrap gap-3"><Button onClick={()=>void encrypt()} disabled={busy||!plaintext.trim()}><LockKeyhole size={15}/>{busy?"Processing...":"Encrypt"}</Button><Button variant="secondary" onClick={()=>void decrypt()} disabled={busy||!packageData}><ShieldCheck size={15}/>Decrypt & verify</Button></div>
        {decrypted!==null && <div className="mt-4 rounded-md border border-mint/25 bg-mint/5 p-4"><div className="flex items-center gap-2 text-sm font-semibold text-mint"><CheckCircle2 size={16}/>Signature verified and payload decrypted</div><pre className="mt-3 overflow-auto whitespace-pre-wrap text-xs text-muted">{decrypted}</pre></div>}
      </Card>
      <Card className="p-5">
        <div className="flex items-center gap-3"><Fingerprint size={19} className="text-mint"/><div><h2 className="font-display font-semibold">Hybrid stack</h2><p className="text-xs text-muted">{info ? "Protocol v" + info.version : "Loading metadata..."}</p></div></div>
        <div className="mt-5 space-y-2">{algorithms.map(a=><div key={a} className="flex items-center justify-between rounded-md border border-line bg-ink px-3 py-3 text-sm"><span>{a}</span><CheckCircle2 size={15} className="text-mint"/></div>)}</div>
        {info && <div className="mt-5 rounded-md border border-line bg-ink p-4 text-xs text-muted">Private keys exposed: <span className="font-semibold text-mint">{String(info.private_keys_exposed)}</span><br/>Key storage: <span className="text-white">{info.key_storage}</span></div>}
      </Card>
    </div>
    <Card className="overflow-hidden"><div className="flex items-center justify-between border-b border-line px-5 py-4"><div><h2 className="font-display font-semibold">Authenticated package</h2><p className="mt-1 text-xs text-muted">Canonical package returned by the crypto service</p></div><Button variant="secondary" onClick={()=>void copyPackage()} disabled={!packageData}><Copy size={14}/>{copied?"Copied":"Copy"}</Button></div><pre className="max-h-[430px] overflow-auto p-5 text-xs leading-6 text-muted">{packageData?JSON.stringify(packageData,null,2):"Encrypt a payload to inspect the package."}</pre></Card>
  </div>;
}
