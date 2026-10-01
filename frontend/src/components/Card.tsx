import type { HTMLAttributes, PropsWithChildren } from "react";

export function Card({
  children,
  className = "",
  ...props
}: PropsWithChildren<HTMLAttributes<HTMLElement>>) {
  return (
    <section
      className={`rounded-md border border-line bg-panel ${className}`}
      {...props}
    >
      {children}
    </section>
  );
}
