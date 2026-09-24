import clsx from "clsx";

import type { ChemistryJobStatus, ChemistryStepStatus } from "../../types/chemistry";

type Status = ChemistryJobStatus | ChemistryStepStatus;

const styles: Record<Status, string> = {
  queued: "border-amber-400/30 bg-amber-400/10 text-amber-200",
  pending: "border-border bg-background/70 text-foreground/45",
  running: "border-primary/40 bg-primary/10 text-primary",
  completed: "border-emerald-400/35 bg-emerald-400/10 text-emerald-200",
  partial: "border-amber-400/35 bg-amber-400/10 text-amber-200",
  failed: "border-red-500/35 bg-red-500/10 text-red-200",
  invalid_configuration: "border-red-500/35 bg-red-500/10 text-red-200",
};

export function StatusBadge({ status, className }: { status: Status; className?: string }) {
  return (
    <span
      className={clsx(
        "inline-flex rounded-md border px-2 py-1 text-[11px] font-semibold capitalize",
        styles[status],
        className,
      )}
    >
      {status.replace(/_/g, " ")}
    </span>
  );
}
