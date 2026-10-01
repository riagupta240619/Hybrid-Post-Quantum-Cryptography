export function StatusBadge({ status }: { status: "connected" | "disconnected" | "offline" }) {
  const styles = {
    connected: "border-mint/25 bg-mint/10 text-mint",
    disconnected: "border-amber/25 bg-amber/10 text-amber",
    offline: "border-line bg-ink text-muted",
  }[status];

  const label = status === "connected" ? "Connected" : status === "disconnected" ? "Unavailable" : "Offline";

  return (
    <span className={`inline-flex items-center gap-2 rounded-full border px-2.5 py-1 text-xs font-medium ${styles}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {label}
    </span>
  );
}