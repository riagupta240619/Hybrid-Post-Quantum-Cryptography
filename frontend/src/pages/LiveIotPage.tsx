import { useCallback, useEffect, useState } from "react";
import { Activity, CheckCircle2, Radio, RefreshCw, Send, TriangleAlert } from "lucide-react";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { api } from "../services/api";
import type { IotMessage, IotStatus } from "../types/api";

export function LiveIotPage() {
  const [status,setStatus]=useState<IotStatus|null>(null); const [messages,setMessages]=useState<IotMessage[]>([]);
  const [deviceId,setDeviceId]=useState("temperature-sensor-001"); const [sequence,setSequence]=useState(1); const [temperature,setTemperature]=useState("24.8"); const [sending,setSending]=useState(false); const [error,setError]=useState<string|null>(null);
  const refresh=useCallback(async()=>{try{const [s,m]=await Promise.all([api.iotStatus(),api.iotMessages()]);setStatus(s);setMessages(m);setError(null)}catch(e){setError(e instanceof Error?e.message:"Could not load IoT status")}},[]);
  useEffect(()=>{void refresh();const t=window.setInterval(()=>void refresh(),2500);return()=>window.clearInterval(t)},[refresh]);
  async function publish(){setSending(true);setError(null);try{await api.publishTelemetry({device_id:deviceId.trim(),sequence,telemetry:{temperature_c:Number(temperature),humidity_percent:61.2,battery_percent:87,sequence}});setSequence(v=>v+1);await refresh()}catch(e){setError(e instanceof Error?e.message:"Publish failed")}finally{setSending(false)}}
  return <div className="space-y-7">
    <div className="flex flex-wrap items-end justify-between gap-4"><div><p className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-mint">IoT security</p><h1 className="font-display text-3xl font-semibold md:text-4xl">Live Telemetry</h1><p className="mt-2 max-w-2xl text-sm text-muted">Watch encrypted MQTT messages move through verification, replay protection, and decryption.</p></div><Button variant="secondary" onClick={()=>void refresh()}><RefreshCw size={14}/>Refresh</Button></div>
    {error&&<div className="rounded-md border border-amber/25 bg-amber/10 px-4 py-3 text-sm text-amber">{error}</div>}
    <div className="grid gap-4 md:grid-cols-3">
      <Card className="p-5"><Radio className="text-mint" size={18}/><div className="mt-4 text-xs uppercase text-muted">MQTT broker</div><div className="mt-1 font-display font-semibold">{status?.broker??"Loading..."}</div><div className="mt-2 text-xs text-muted">{status?.connected?"Connected":"Unavailable"}</div></Card>
      <Card className="p-5"><Activity className="text-mint" size={18}/><div className="mt-4 text-xs uppercase text-muted">Replay protection</div><div className="mt-1 font-display font-semibold">{status?.replay_protection?"Enabled":"Disabled"}</div><div className="mt-2 text-xs text-muted">Sequence validation at gateway</div></Card>
      <Card className="p-5"><Activity className="text-mint" size={18}/><div className="mt-4 text-xs uppercase text-muted">Buffered events</div><div className="mt-1 font-display text-2xl font-semibold">{messages.length}</div><div className="mt-2 text-xs text-muted">Gateway event buffer</div></Card>
    </div>
    <Card className="p-5"><div className="flex items-center gap-3"><Send size={18} className="text-mint"/><div><h2 className="font-display font-semibold">Publish test telemetry</h2><p className="text-xs text-muted">Uses the real hybrid encryption + MQTT endpoint.</p></div></div><div className="mt-5 grid gap-4 md:grid-cols-[1fr_140px_140px_auto] md:items-end">
      <label className="text-xs font-medium text-muted">Device ID<input value={deviceId} onChange={e=>setDeviceId(e.target.value)} className="mt-2 w-full rounded-md border border-line bg-ink px-3 py-2.5 text-sm outline-none focus:border-mint"/></label>
      <label className="text-xs font-medium text-muted">Temperature<input value={temperature} onChange={e=>setTemperature(e.target.value)} type="number" step="0.1" className="mt-2 w-full rounded-md border border-line bg-ink px-3 py-2.5 text-sm outline-none focus:border-mint"/></label>
      <label className="text-xs font-medium text-muted">Sequence<input value={sequence} onChange={e=>setSequence(Number(e.target.value))} type="number" min="0" className="mt-2 w-full rounded-md border border-line bg-ink px-3 py-2.5 text-sm outline-none focus:border-mint"/></label>
      <Button onClick={()=>void publish()} disabled={sending||!status?.connected}><Send size={14}/>{sending?"Sending...":"Publish"}</Button>
    </div></Card>
    <Card className="overflow-hidden"><div className="border-b border-line px-5 py-4"><h2 className="font-display font-semibold">Gateway event stream</h2><p className="mt-1 text-xs text-muted">Auto-refreshes every 2.5 seconds.</p></div><div className="divide-y divide-line">
      {messages.length===0?<p className="px-5 py-8 text-sm text-muted">Waiting for telemetry...</p>:messages.map((m,i)=>{const ok=m.security.verified===true;return <div key={m.received_at+i} className="grid gap-3 px-5 py-4 md:grid-cols-[1fr_160px_160px] md:items-center"><div className="flex items-start gap-3">{ok?<CheckCircle2 className="mt-0.5 text-mint" size={17}/>:<TriangleAlert className="mt-0.5 text-amber" size={17}/>}<div><div className="text-sm font-medium">{m.device_id??"Unknown device"}</div><div className="mt-1 text-xs text-muted">{ok?"Signature verified · decrypted · replay check passed":m.error??"Security validation failed"}</div></div></div><div className="text-xs text-muted">{m.security.sequence!==undefined?"Sequence #"+String(m.security.sequence):"No sequence"}</div><div className="text-right text-xs text-muted">{new Date(m.received_at).toLocaleTimeString()}</div></div>})}
    </div></Card>
  </div>;
}
