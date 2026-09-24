import clsx from "clsx";

interface MetricCardProps {
  label: string;
  value: string;
  detail?: string;
  className?: string;
}

export function MetricCard({ label, value, detail, className }: MetricCardProps) {
  return (
    <article className={clsx("h-24 min-w-0 overflow-hidden rounded-md border border-border bg-background/70 p-3", className)}>
      <p className="truncate text-xs text-foreground/55" title={label}>{label}</p>
      <p className="mt-2 truncate font-mono text-sm font-semibold leading-5 text-primary" title={value}>{value}</p>
      {detail ? <p className="mt-1 truncate text-xs text-foreground/45" title={detail}>{detail}</p> : null}
    </article>
  );
}
