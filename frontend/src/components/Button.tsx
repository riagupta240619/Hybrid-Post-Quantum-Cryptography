import type { ButtonHTMLAttributes, PropsWithChildren } from "react";

type ButtonProps = PropsWithChildren<
  ButtonHTMLAttributes<HTMLButtonElement>
> & {
  variant?: "primary" | "secondary";
};

export function Button({
  children,
  className = "",
  variant = "primary",
  ...props
}: ButtonProps) {
  const style =
    variant === "primary"
      ? "bg-mint text-ink hover:bg-[#a3efd0]"
      : "border border-line bg-panel text-white hover:border-muted";

  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-md px-4 py-2.5 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-50 ${style} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
