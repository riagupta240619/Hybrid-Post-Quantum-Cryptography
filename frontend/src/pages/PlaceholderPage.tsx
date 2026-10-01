import { Construction } from "lucide-react";
import { Card } from "../components/Card";

export function PlaceholderPage({ title }: { title: string }) {
  return (
    <div className="space-y-7">
      <div>
        <p className="mb-2 text-xs font-semibold uppercase text-mint">
          Platform
        </p>
        <h1 className="font-display text-3xl font-semibold">{title}</h1>
      </div>
      <Card className="flex items-start gap-4 p-5">
        <Construction className="mt-0.5 shrink-0 text-amber" size={19} />
        <div>
          <h2 className="font-display font-semibold">Not part of Phase 1</h2>
          <p className="mt-1 text-sm leading-6 text-muted">
            This area is reserved for a later phase. No functionality is
            available here yet.
          </p>
        </div>
      </Card>
    </div>
  );
}
