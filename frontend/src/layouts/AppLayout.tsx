import { useEffect, useState } from "react";
import {
  Activity,
  BarChart3,
  Blocks,
  Cpu,
  Fingerprint,
  LayoutDashboard,
  Shield,
  type LucideIcon,
} from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";
import { StatusBadge } from "../components/StatusBadge";
import { api } from "../services/api";
import type { HealthResponse } from "../types/api";

const navigation: { label: string; path: string; icon: LucideIcon }[] = [
  { label: "Dashboard", path: "/", icon: LayoutDashboard },
  { label: "Devices", path: "/devices", icon: Cpu },
  { label: "Encryption Lab", path: "/encryption-lab", icon: Fingerprint },
  { label: "Benchmarks", path: "/benchmarks", icon: BarChart3 },
  { label: "Audit Logs", path: "/audit-logs", icon: Activity },
];

export function AppLayout() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthUnavailable, setHealthUnavailable] = useState(false);

  useEffect(() => {
    let active = true;
    api
      .health()
      .then((result) => {
        if (active) setHealth(result);
      })
      .catch(() => {
        if (active) setHealthUnavailable(true);
      });
    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="min-h-screen bg-ink text-white md:grid md:grid-cols-[240px_1fr]">
      <aside className="border-b border-line bg-[#141c1e] md:min-h-screen md:border-b-0 md:border-r">
        <div className="flex h-16 items-center gap-3 border-b border-line px-5">
          <div className="grid h-8 w-8 place-items-center rounded-md bg-mint text-ink">
            <Shield size={17} strokeWidth={2.5} />
          </div>
          <div>
            <div className="font-display text-sm font-bold">PQSHIELD</div>
            <div className="text-[10px] uppercase text-muted">
              Security platform
            </div>
          </div>
        </div>
        <nav
          aria-label="Main navigation"
          className="flex gap-1 overflow-x-auto p-3 md:block md:space-y-1"
        >
          {navigation.map(({ label, path, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              end={path === "/"}
              className={({ isActive }) =>
                `flex shrink-0 items-center gap-3 rounded-md px-3 py-2.5 text-sm transition ${isActive ? "bg-[#273432] font-semibold text-mint" : "text-muted hover:bg-panel hover:text-white"}`
              }
            >
              <Icon size={17} strokeWidth={1.8} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="hidden px-4 pb-5 md:absolute md:bottom-0 md:block">
          <div className="flex items-center gap-2 border-t border-line pt-4 text-xs text-muted">
            <Blocks size={14} /> Phase 1 foundation
          </div>
        </div>
      </aside>

      <div className="min-w-0">
        <header className="flex h-16 items-center justify-between border-b border-line px-5 md:px-8">
          <div className="text-xs font-medium uppercase text-muted">
            Hybrid post-quantum security
          </div>
          <div className="flex items-center gap-3">
            <StatusBadge
              status={
                health
                  ? "connected"
                  : healthUnavailable
                    ? "disconnected"
                    : "offline"
              }
            />
            <span className="hidden text-xs text-muted sm:inline">
              {health ? `API v${health.version}` : "API"}
            </span>
          </div>
        </header>
        <main className="mx-auto w-full max-w-[1440px] p-5 md:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
