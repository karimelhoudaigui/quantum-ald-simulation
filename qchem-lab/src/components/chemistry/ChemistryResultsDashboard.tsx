import { AlertTriangle, ChevronDown, CircleX, FileJson, TableProperties } from "lucide-react";
import { useMemo } from "react";

import { buildExperimentConfig, useChemistryStore } from "../../stores/chemistryStore";
import type { ChemistryComparisonRow, StructuredMessage } from "../../types/chemistry";
import { IconButton } from "../ui/IconButton";
import { MetricCard } from "../ui/MetricCard";
import { StatusBadge } from "../ui/StatusBadge";

export function ChemistryResultsDashboard() {
  const job = useChemistryStore((state) => state.job);
  const result = useChemistryStore((state) => state.result);
  const metrics = useMemo(() => summarize(result?.comparison_table ?? []), [result]);
  const backendErrors = result?.errors ?? normalizeJobErrors(job?.error);

  return (
    <aside className="flex min-h-0 min-w-0 max-w-full flex-col gap-4 overflow-x-hidden overflow-y-auto overscroll-contain border-t border-border bg-muted/30 p-4 sm:p-5 lg:h-[100svh] lg:border-l lg:border-t-0">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium uppercase text-foreground/50">Results</p>
          <h2 className="text-xl font-semibold">Molecular comparison</h2>
          {job ? <StatusBadge status={job.status} className="mt-2" /> : null}
        </div>
        <div className="flex gap-2">
          <IconButton
            label="Export request JSON"
            onClick={() => downloadJson("chemistry-request.json", buildExperimentConfig(useChemistryStore.getState()))}
          >
            <FileJson size={15} />
          </IconButton>
          <IconButton
            label="Export result JSON"
            disabled={!result}
            onClick={() => result && downloadJson(`${result.experiment_id}.json`, result)}
          >
            <FileJson size={15} />
          </IconButton>
          <IconButton
            label="Export comparison CSV"
            disabled={!result?.comparison_table.length}
            onClick={() => result && downloadCsv("chemistry-comparison.csv", result.comparison_table)}
          >
            <TableProperties size={15} />
          </IconButton>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <MetricCard label="HF energy" value={formatEnergy(referenceEnergy(result, "hartree_fock"))} />
        <MetricCard
          label="FCI energy"
          value={formatEnergy(referenceEnergy(result, "fci_full_space"))}
          detail={result && referenceEnergy(result, "fci_full_space") === null ? "Unavailable" : undefined}
        />
        <MetricCard label="Min solver error" value={formatScientific(metrics.minSolverError)} />
        <MetricCard label="Total runtime" value={result ? `${(result.timings_seconds.total ?? 0).toFixed(2)} s` : "—"} />
        <MetricCard label="Max qubits" value={metrics.maxQubits === null ? "—" : String(metrics.maxQubits)} />
        <MetricCard label="CAS completed" value={result ? `${metrics.completed} / ${result.comparison_table.length}` : "—"} />
      </div>

      {result?.warnings.length ? (
        <MessageList title="Scientific warnings" icon={<AlertTriangle size={15} />} messages={result.warnings} tone="warning" />
      ) : null}
      {backendErrors.length ? (
        <MessageList title="Errors" icon={<CircleX size={15} />} messages={backendErrors} tone="error" />
      ) : null}

      <section className="min-w-0 border-t border-border pt-4">
        <div className="mb-3 flex min-w-0 items-center justify-between gap-2">
          <h3 className="shrink-0 text-sm font-semibold">Active-space results</h3>
          <span
            className="min-w-0 truncate text-right font-mono text-[10px] text-foreground/45"
            title={result?.experiment_id}
          >
            {result?.experiment_id ?? "—"}
          </span>
        </div>
        <div className="max-w-full overflow-hidden rounded-md border border-border bg-background/70">
          <table className="w-full table-fixed border-collapse text-left text-[10px]">
            <colgroup>
              <col className="w-[17%]" />
              <col className="w-[13%]" />
              <col className="w-[25%]" />
              <col className="w-[25%]" />
              <col className="w-[20%]" />
            </colgroup>
            <thead className="border-b border-border text-foreground/45">
              <tr>
                <th className="px-2 py-2 font-medium">CAS</th>
                <th className="px-1 py-2 font-medium" title="Qubits">Q</th>
                <th className="px-1 py-2 font-medium">CASCI</th>
                <th className="px-1 py-2 font-medium">VQE</th>
                <th className="px-1 py-2 font-medium" title="Absolute solver error">|Δ|</th>
              </tr>
            </thead>
            <tbody>
              {(result?.comparison_table ?? []).map((row) => (
                <tr key={row.configuration_id} className="border-b border-border/60 last:border-0">
                  <td className="truncate px-2 py-2 font-mono text-primary">{row.n_active_electrons},{row.n_active_orbitals}</td>
                  <td className="truncate px-1 py-2 font-mono">{row.num_qubits ?? "—"}</td>
                  <td className="truncate px-1 py-2 font-mono" title={formatCompact(row.casci_total_hartree)}>{formatCompact(row.casci_total_hartree)}</td>
                  <td className="truncate px-1 py-2 font-mono" title={formatCompact(row.vqe_total_hartree)}>{formatCompact(row.vqe_total_hartree)}</td>
                  <td className="truncate px-1 py-2 font-mono" title={formatScientific(row.solver_error_hartree)}>{formatScientific(row.solver_error_hartree)}</td>
                </tr>
              ))}
              {!result?.comparison_table.length ? (
                <tr><td colSpan={5} className="px-3 py-10 text-center text-foreground/35">—</td></tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>

      <section className="space-y-2 border-t border-border pt-4">
        <h3 className="text-sm font-semibold">Configuration details</h3>
        {(result?.comparison_table ?? []).map((row) => (
          <ResultDetails key={row.configuration_id} row={row} />
        ))}
      </section>
    </aside>
  );
}

function ResultDetails({ row }: { row: ChemistryComparisonRow }) {
  return (
    <details className="rounded-md border border-border bg-background/70">
      <summary className="flex cursor-pointer list-none items-center justify-between gap-2 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary">
        <span className="font-mono text-xs text-primary">CAS({row.n_active_electrons},{row.n_active_orbitals})</span>
        <ChevronDown size={14} className="text-foreground/45" />
      </summary>
      <dl className="grid grid-cols-[repeat(2,minmax(0,1fr))] gap-x-3 gap-y-2 border-t border-border p-3 text-xs">
        <Detail label="Status" value={row.status} />
        <Detail label="Pauli terms" value={row.num_pauli_terms} />
        <Detail label="Parameters" value={row.ansatz_parameters} />
        <Detail label="Circuit depth" value={row.circuit_depth} />
        <Detail label="2q gates" value={row.two_qubit_gates} />
        <Detail label="Evaluations" value={row.optimizer_evaluations} />
        <Detail label="Runtime" value={`${row.configuration_runtime_seconds.toFixed(3)} s`} />
        <Detail label="Orbitals" value={row.orbital_indices?.join(", ") ?? row.selection_mode} />
      </dl>
    </details>
  );
}

function Detail({ label, value }: { label: string; value: number | string | null }) {
  return (
    <div className="min-w-0">
      <dt className="text-foreground/45">{label}</dt>
      <dd className="mt-1 break-words font-mono text-foreground/80 [overflow-wrap:anywhere]">{value ?? "—"}</dd>
    </div>
  );
}

function MessageList({
  title,
  icon,
  messages,
  tone,
}: {
  title: string;
  icon: React.ReactNode;
  messages: StructuredMessage[];
  tone: "warning" | "error";
}) {
  const style = tone === "warning" ? "border-amber-400/30 bg-amber-400/10 text-amber-100" : "border-red-500/30 bg-red-500/10 text-red-200";
  return (
    <section className={`rounded-md border p-3 ${style}`} role={tone === "error" ? "alert" : "status"}>
      <h3 className="flex items-center gap-2 text-sm font-semibold">{icon}{title}</h3>
      <div className="mt-2 space-y-2">
        {messages.map((message, index) => (
          <div key={`${message.code}-${message.field}-${index}`}>
            <p className="font-mono text-[11px] opacity-65">{message.field} · {message.code}</p>
            <p className="mt-0.5 text-xs leading-5 [overflow-wrap:anywhere]">{message.message}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function normalizeJobErrors(error: unknown): StructuredMessage[] {
  if (!error) return [];
  if (Array.isArray(error)) return error as StructuredMessage[];
  return [error as StructuredMessage];
}

function referenceEnergy(result: ReturnType<typeof useChemistryStore.getState>["result"], key: "hartree_fock" | "fci_full_space") {
  const value = result?.results.global_references[key]?.energy_total_hartree;
  return typeof value === "number" ? value : null;
}

function summarize(rows: ChemistryComparisonRow[]) {
  const solverErrors = rows.map((row) => row.solver_error_hartree).filter((value): value is number => value !== null);
  const qubits = rows.map((row) => row.num_qubits).filter((value): value is number => value !== null);
  return {
    minSolverError: solverErrors.length ? Math.min(...solverErrors.map(Math.abs)) : null,
    maxQubits: qubits.length ? Math.max(...qubits) : null,
    completed: rows.filter((row) => row.status === "completed").length,
  };
}

function formatEnergy(value: number | null) {
  return value === null ? "—" : `${value.toFixed(8)} Ha`;
}

function formatCompact(value: number | null) {
  return value === null ? "—" : value.toFixed(6);
}

function formatScientific(value: number | null) {
  return value === null ? "—" : value.toExponential(2);
}

function downloadJson(filename: string, value: unknown) {
  downloadBlob(filename, JSON.stringify(value, null, 2), "application/json");
}

function downloadCsv(filename: string, rows: ChemistryComparisonRow[]) {
  if (rows.length === 0) return;
  const keys = Object.keys(rows[0]) as Array<keyof ChemistryComparisonRow>;
  const lines = [keys.join(","), ...rows.map((row) => keys.map((key) => csvCell(row[key])).join(","))];
  downloadBlob(filename, `${lines.join("\n")}\n`, "text/csv");
}

function csvCell(value: unknown) {
  const text = Array.isArray(value) ? value.join(";") : value == null ? "" : String(value);
  return `"${text.replace(/"/g, '""')}"`;
}

function downloadBlob(filename: string, contents: string, type: string) {
  const url = URL.createObjectURL(new Blob([contents], { type }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}
