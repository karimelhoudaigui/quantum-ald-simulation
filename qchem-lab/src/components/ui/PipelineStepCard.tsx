import { Check, Circle, Loader2, X } from "lucide-react";

import type { ChemistryPipelineStep } from "../../types/chemistry";
const styles = {
  pending: "border-border bg-background/55",
  running: "border-primary/45 bg-primary/[0.08]",
  completed: "border-emerald-400/30 bg-emerald-400/[0.07]",
  failed: "border-red-500/35 bg-red-500/[0.08]",
};

const statusLabels: Record<ChemistryPipelineStep["status"], string> = {
  pending: "Pending",
  running: "Running",
  completed: "Done",
  failed: "Failed",
};

export function PipelineStepCard({ step }: { step: ChemistryPipelineStep }) {
  const icon =
    step.status === "running" ? (
      <Loader2 className="animate-spin" size={16} />
    ) : step.status === "completed" ? (
      <Check size={16} />
    ) : step.status === "failed" ? (
      <X size={16} />
    ) : (
      <Circle size={14} />
    );
  return (
    <article className={`h-36 min-w-0 overflow-hidden rounded-md border p-2.5 transition-colors xl:h-28 2xl:h-40 ${styles[step.status]}`}>
      <div
        className="flex min-w-0 items-center gap-1.5 text-[10px] font-semibold capitalize text-primary"
        title={step.status.replace(/_/g, " ")}
      >
        <span className="shrink-0">{icon}</span>
        <span className="truncate">{statusLabels[step.status]}</span>
      </div>
      <p className="mt-3 line-clamp-3 break-words text-xs font-semibold leading-4" title={step.label}>{step.label}</p>
      <p className="mt-1 line-clamp-2 break-words text-xs leading-5 text-foreground/50 xl:hidden 2xl:block" title={step.message ?? "Waiting"}>
        {step.message ?? "Waiting"}
      </p>
    </article>
  );
}
