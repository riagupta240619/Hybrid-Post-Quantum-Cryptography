import { useEffect, useState } from "react";
import { CheckCircle2, ShieldAlert, TriangleAlert } from "lucide-react";
import { Card } from "../components/Card";
import { api } from "../services/api";
import type { IotMessage } from "../types/api";

export function SecurityEventsPage() {
  const [messages,setMessages]=useState<IotMessage[]>([]);
  useEffect(()=>{let active=true;async function load(){try{const data=await api.iotMessages();if(active)setMessages(data)}catch{}}void load();const t=window.setInterval(()=>void load(),3000);return()=>{active=false;window.clearInterval(t)}},[]);
  const blocked=messages.filter(m=>m.security.verified!==true);
  return <div className="space-y-7">
    <div><p className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-mint">Detection</p><h1 className="font-display text-3xl font-semibold md:text-4xl">Security Events</h1><p className="mt-2 max-w-2xl text-sm text-muted">Security decisions produced by the live MQTT gateway.</p></div>
    <div className="grid gap-4 md:grid-cols-3"><Card className="p-5"><ShieldAlert className="text-mint" size={18}/><div className="mt-4 text-xs uppercase text-muted">Events</div><div className="mt-1 font-display text-2xl font-semibold">{messages.length}</div></Card><Card className="p-5"><CheckCircle2 className="text-mint" size={18}/><div className="mt-4 text-xs uppercase text-muted">Accepted</div><div className="mt-1 font-display text-2xl font-semibold">{messages.length-blocked.length}</div></Card><Card className="p-5"><TriangleAlert className="text-amber" size={18}/><div className="mt-4 text-xs uppercase text-muted">Blocked</div><div className="mt-1 font-display text-2xl font-semibold">{blocked.length}</div></Card></div>
    <Card className="overflow-hidden"><div className="border-b border-line px-5 py-4"><h2 className="font-display font-semibold">Event log</h2></div><div className="divide-y divide-line">{messages.length===0?<p className="px-5 py-8 text-sm text-muted">No security events recorded yet.</p>:messages.map((m,i)=>{const ok=m.security.verified===true;const replay=!ok&&(m.error??"").toLowerCase().includes("replay");return <div key={m.received_at+i} className="grid gap-3 px-5 py-4 md:grid-cols-[1fr_180px_180px] md:items-center"><div className="flex items-start gap-3">{ok?<CheckCircle2 className="mt-0.5 text-mint" size={17}/>:<TriangleAlert className="mt-0.5 text-amber" size={17}/>}<div><div className="text-sm font-medium">{ok?"Telemetry accepted":replay?"Replay attempt blocked":"Security validation blocked"}</div><div className="mt-1 text-xs text-muted">{m.device_id??"Unknown device"} · {m.error??"ML-DSA verified · replay check passed"}</div></div></div><div className="text-xs text-muted">{m.security.sequence!==undefined?"Sequence #"+String(m.security.sequence):"—"}</div><div className="text-right text-xs text-muted">{new Date(m.received_at).toLocaleString()}</div></div>})}</div></Card>
  </div>;
}
