import { ArrowRight, Cpu, Fingerprint, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";
import { Card } from "../components/Card";

export function DashboardPage() {
  return (
    <div className="space-y-8">
      <div>
        <p className="mb-2 text-xs font-semibold uppercase text-mint">
          Platform overview
        </p>
        <h1 className="font-display text-3xl font-semibold">
          Good to see you.
        </h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">
          PQShield is in its foundation phase. Device registration is live;
          cryptographic workflows are not yet implemented.
        </p>
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="p-5">
          <Cpu className="mb-6 text-mint" size={20} />
          <h2 className="font-display text-lg font-semibold">
            Device registry
          </h2>
          <p className="mt-2 text-sm leading-6 text-muted">
            Register and review devices persisted in PostgreSQL.
          </p>
          <Link
            to="/devices"
            className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-mint hover:text-white"
          >
            Open devices <ArrowRight size={15} />
          </Link>
        </Card>
        <Card className="p-5">
          <ShieldCheck className="mb-6 text-amber" size={20} />
          <h2 className="font-display text-lg font-semibold">
            Service foundation
          </h2>
          <p className="mt-2 text-sm leading-6 text-muted">
            Versioned API, database sessions, CORS, and health checks are
            configured.
          </p>
          <div className="mt-5 text-xs font-medium text-muted">API v1</div>
        </Card>
        <Card className="p-5">
          <Fingerprint className="mb-6 text-muted" size={20} />
          <h2 className="font-display text-lg font-semibold">Cryptography</h2>
          <p className="mt-2 text-sm leading-6 text-muted">
            No encryption, key encapsulation, or digital signature operations
            are available in Phase 1.
          </p>
          <div className="mt-5 text-xs font-medium text-amber">
            Not implemented
          </div>
        </Card>
      </div>
    </div>
  );
}
