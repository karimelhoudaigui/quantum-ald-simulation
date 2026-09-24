import { Activity, FlaskConical } from "lucide-react";

import { CHEMISTRY_STEP_LABELS } from "../../config/chemistry";
import { useChemistryStore } from "../../stores/chemistryStore";
import type { ChemistryPipelineStep } from "../../types/chemistry";
import { Panel } from "../ui/Panel";
import { PipelineStepCard } from "../ui/PipelineStepCard";
import { StatusBadge } from "../ui/StatusBadge";

const idleSteps: ChemistryPipelineStep[] = CHEMISTRY_STEP_LABELS.map(([id, label]) => ({
  id,
  label,
  status: "pending",
  message: null,
}));

export function ChemistryPipelineRunner() {
  const job = useChemistryStore((state) => state.job);
  const networkError = useChemistryStore((state) => state.networkError);
  const steps = job?.steps ?? idleSteps;
  const showActiveSpaceProgress = Boolean(job && job.total_active_spaces > 0);

  return (
    <Panel>
      <div className="mb-4 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-foreground/50">Pipeline</p>
          <h2 className="mt-1 text-lg font-semibold sm:text-xl">Molecular Electronic Structure + VQE</h2>
          <p className="mt-1 font-mono text-[11px] text-foreground/40">
            schema 1 · exact statevector · Jordan-Wigner
          </p>
        </div>
        <div className="flex items-center gap-2">
          <FlaskConical size={17} className="text-primary" />
          <StatusBadge status={job?.status ?? "pending"} />
        </div>
      </div>

      <div className="mb-4 h-2 overflow-hidden rounded-full bg-background">
        <div
          className="h-full bg-primary transition-all duration-500"
          style={{ width: `${job?.progress ?? 0}%` }}
        />
      </div>

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 xl:grid-cols-6">
        {steps.map((step) => (
          <PipelineStepCard key={step.id} step={step} />
        ))}
      </div>

      <div
        aria-hidden={!showActiveSpaceProgress}
        className={`mt-4 flex flex-wrap items-center justify-between gap-2 rounded-md border border-border bg-background/60 px-3 py-2 text-xs ${
          showActiveSpaceProgress ? "visible" : "invisible"
        }`}
      >
          <span className="flex items-center gap-2 text-foreground/60">
            <Activity size={14} className="text-primary" /> Active-space progress
          </span>
          <span className="font-mono text-primary">
            {job?.completed_active_spaces ?? 0} / {job?.total_active_spaces ?? 0}
          </span>
      </div>

      {networkError ? (
        <p role="alert" className="mt-4 rounded-md border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-200">
          {networkError}
        </p>
      ) : null}
    </Panel>
  );
}
