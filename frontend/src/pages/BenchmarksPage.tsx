import { useEffect, useState } from "react";
import { BarChart3, Gauge, History, Play, Timer } from "lucide-react";
import { Button } from "../components/Button";
import { Card } from "../components/Card";
import { api } from "../services/api";
import type { BenchmarkHistoryItem, BenchmarkResponse } from "../types/api";

export function BenchmarksPage() {
  const [iterations, setIterations] = useState(25);
  const [bytes, setBytes] = useState(1024);
  const [data, setData] = useState<BenchmarkResponse | null>(null);
  const [history, setHistory] = useState<BenchmarkHistoryItem[]>([]);
  const [busy, setBusy] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadHistory() {
    try {
      setHistory(await api.benchmarkHistory());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not load benchmark history");
    } finally {
      setLoadingHistory(false);
    }
  }

  useEffect(() => { void loadHistory(); }, []);

  async function run() {
    setBusy(true);
    setError(null);
    try {
      const result = await api.runBenchmark({
        iterations: Math.min(500, Math.max(3, iterations)),
        payload_bytes: Math.min(65536, Math.max(16, bytes)),
      });
      setData(result);
      await loadHistory();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Benchmark failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-7">
      <div>
        <p className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-mint">Research</p>
        <h1 className="font-display text-3xl font-semibold md:text-4xl">Cryptographic Benchmarks</h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">
          Measure classical, post-quantum, and hybrid operations on the same payload and iteration count.
        </p>
      </div>

      {error && <div className="rounded-md border border-amber/25 bg-amber/10 px-4 py-3 text-sm text-amber">{error}</div>}

      <Card className="p-5">
        <div className="grid gap-4 md:grid-cols-[180px_180px_auto] md:items-end">
          <label className="text-xs text-muted">
            Iterations
            <input type="number" min="3" max="500" value={iterations} onChange={(e) => setIterations(Number(e.target.value))}
              className="mt-2 w-full rounded-md border border-line bg-ink px-3 py-2.5 text-sm outline-none focus:border-mint"/>
          </label>
          <label className="text-xs text-muted">
            Payload bytes
            <input type="number" min="16" max="65536" value={bytes} onChange={(e) => setBytes(Number(e.target.value))}
              className="mt-2 w-full rounded-md border border-line bg-ink px-3 py-2.5 text-sm outline-none focus:border-mint"/>
          </label>
          <Button onClick={() => void run()} disabled={busy}>
            <Play size={14}/>{busy ? "Running..." : "Run benchmark"}
          </Button>
        </div>
      </Card>

      {data && (
        <div className="grid gap-5 lg:grid-cols-3">
          {data.results.map((result) => (
            <Card key={result.mode} className="p-5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2"><BarChart3 size={17} className="text-mint"/><span className="font-display font-semibold capitalize">{result.mode}</span></div>
                <span className="text-xs text-muted">{result.package_bytes} B</span>
              </div>
              <div className="mt-6 grid grid-cols-2 gap-3">
                {[
                  ["Total", result.total_ms],
                  ["Keygen", result.keygen_ms],
                  ["Encap", result.encapsulation_ms],
                  ["Decap", result.decapsulation_ms],
                  ["Encrypt", result.encryption_ms],
                  ["Decrypt", result.decryption_ms],
                ].map(([label, value]) => (
                  <div key={String(label)} className="rounded-md border border-line p-3">
                    <div className="text-[10px] uppercase text-muted">{label}</div>
                    <div className="mt-1 font-display text-lg">{Number(value).toFixed(3)} ms</div>
                  </div>
                ))}
              </div>
              <div className="mt-5 flex items-center gap-2 text-xs text-muted"><Gauge size={14}/> Median per-operation timing</div>
            </Card>
          ))}
        </div>
      )}

      <Card className="overflow-hidden">
        <div className="flex items-center gap-2 border-b border-line px-5 py-4">
          <History size={17} className="text-mint"/>
          <div><h2 className="font-display font-semibold">Benchmark history</h2><p className="mt-1 text-xs text-muted">Persisted results from PostgreSQL.</p></div>
        </div>
        {loadingHistory ? <p className="px-5 py-8 text-sm text-muted">Loading benchmark history...</p> : history.length === 0 ? (
          <p className="px-5 py-8 text-sm text-muted">No benchmark runs yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[700px] text-left text-sm">
              <thead className="bg-[#141c1e] text-xs uppercase text-muted">
                <tr><th className="px-5 py-3">Mode</th><th className="px-5 py-3">Payload</th><th className="px-5 py-3">Iterations</th><th className="px-5 py-3">Total</th><th className="px-5 py-3">Package</th><th className="px-5 py-3">Created</th></tr>
              </thead>
              <tbody className="divide-y divide-line">
                {history.map((item) => (
                  <tr key={item.id}>
                    <td className="px-5 py-3 font-medium capitalize">{item.mode}</td>
                    <td className="px-5 py-3 text-muted">{item.payload_bytes} B</td>
                    <td className="px-5 py-3 text-muted">{item.iterations}</td>
                    <td className="px-5 py-3 text-muted">{item.total_ms.toFixed(3)} ms</td>
                    <td className="px-5 py-3 text-muted">{item.package_bytes} B</td>
                    <td className="px-5 py-3 text-muted">{new Date(item.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      <Card className="p-5">
        <div className="flex items-center gap-2"><Timer size={17} className="text-mint"/><h2 className="font-display font-semibold">What this measures</h2></div>
        <p className="mt-3 text-sm leading-6 text-muted">
          The benchmark separates key generation, key encapsulation, AES encryption/decryption, ML-DSA signing/verification, and package size. Results are measurements on the machine running the API, not universal performance guarantees.
        </p>
      </Card>
    </div>
  );
}
