import clsx from "clsx";
import type { HTMLAttributes } from "react";

export function Panel({ className, ...props }: HTMLAttributes<HTMLElement>) {
  return (
    <section
      className={clsx("min-w-0 max-w-full rounded-md border border-border bg-muted/25 p-4 shadow-panel", className)}
      {...props}
    />
  );
}
