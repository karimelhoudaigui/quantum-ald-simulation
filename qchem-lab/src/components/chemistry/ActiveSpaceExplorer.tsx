import { BarChart3, Boxes, TrendingUp } from "lucide-react";
import { useMemo, useState } from "react";

import { useChemistryStore } from "../../stores/chemistryStore";
import type { ChemistryComparisonRow } from "../../types/chemistry";
import { Panel } from "../ui/Panel";

type ExplorerView = "accuracy" | "resources";

export function ActiveSpaceExplorer() {
  const result = useChemistryStore((state) => state.result);
  const [view, setView] = useState<ExplorerView>("accuracy");
  const rows = result?.comparison_table ?? [];

  return (
    <Panel className="shadow-none">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs font-medium uppercase text-foreground/50">Active-space explorer</p>
          <h2 className="mt-1 text-lg font-semibold">Accuracy, resources &amp; cost</h2>
        </div>
        <div className="flex overflow-hidden rounded-md border border-border bg-background" role="tablist">
          <ViewButton active={view === "accuracy"} onClick={() => setView("accuracy")} icon={<TrendingUp size={14} />}>
            Accuracy
          </ViewButton>
          <ViewButton active={view === "resources"} onClick={() => setView("resources")} icon={<Boxes size={14} />}>
            Resources
          </ViewButton>
        </div>
      </div>

      {rows.length === 0 ? (
        <div className="flex min-h-52 items-center justify-center border-y border-border bg-background/45 text-sm text-foreground/40">
          <BarChart3 size={18} className="mr-2" /> No comparison available
        </div>
      ) : view === "accuracy" ? (
        <AccuracyChart rows={rows} />
      ) : (
        <ResourceComparison rows={rows} />
      )}
    </Panel>
  );
}

function ViewButton({
  active,
  onClick,
  icon,
  children,
}: {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      role="tab"
      aria-selected={active}
      onClick={onClick}
      className={`inline-flex items-center gap-2 px-3 py-2 text-xs font-semibold transition focus:outline-none focus:ring-2 focus:ring-primary ${
        active ? "bg-primary text-background" : "text-foreground/55 hover:bg-muted"
      }`}
    >
      {icon}
      {children}
    </button>
  );
}

function AccuracyChart({ rows }: { rows: ChemistryComparisonRow[] }) {
  const chart = useMemo(() => buildAccuracyChart(rows), [rows]);
  return (
    <div className="overflow-hidden border-y border-border bg-background/55">
      <svg viewBox="0 0 900 340" className="aspect-[9/3.4] min-h-[260px] w-full" role="img" aria-label="Energy error versus qubits">
        {[60, 120, 180, 240, 300].map((y) => (
          <line key={y} x1="72" x2="860" y1={y} y2={y} stroke="currentColor" className="text-border" strokeOpacity="0.7" />
        ))}
        <line x1="72" x2="72" y1="36" y2="300" stroke="currentColor" className="text-border" />
        <line x1="72" x2="860" y1="300" y2="300" stroke="currentColor" className="text-border" />
        <text x="72" y="24" className="fill-foreground/50 text-[12px]">absolute error (Ha, log scale)</text>
        <text x="860" y="326" textAnchor="end" className="fill-foreground/50 text-[12px]">qubits</text>
        {chart.series.map((series) => (
          <g key={series.label}>
            {series.path ? <path d={series.path} fill="none" stroke={series.color} strokeWidth="3" strokeLinecap="round" /> : null}
            {series.points.map((point) => (
              <circle key={`${series.label}-${point.x}`} cx={point.x} cy={point.y} r="6" fill={series.color} stroke="#07110f" strokeWidth="2">
                <title>{`${series.label}: ${point.value.toExponential(3)} Ha at ${point.qubits} qubits`}</title>
              </circle>
            ))}
          </g>
        ))}
        {chart.xTicks.map((tick) => (
          <g key={tick.value}>
            <line x1={tick.x} x2={tick.x} y1="300" y2="307" stroke="currentColor" className="text-border" />
            <text x={tick.x} y="324" textAnchor="middle" className="fill-foreground/55 font-mono text-[12px]">{tick.value}</text>
          </g>
        ))}
      </svg>
      <div className="flex flex-wrap gap-4 border-t border-border px-4 py-3 text-xs text-foreground/60">
        {chart.series.map((series) => (
          <span key={series.label} className="inline-flex items-center gap-2">
            <span className="h-2 w-2 rounded-full" style={{ background: series.color }} /> {series.label}
          </span>
        ))}
      </div>
    </div>
  );
}

function buildAccuracyChart(rows: ChemistryComparisonRow[]) {
  const width = 788;
  const xMin = Math.min(...rows.map((row) => row.num_qubits ?? 0));
  const xMax = Math.max(...rows.map((row) => row.num_qubits ?? 0));
  const x = (qubits: number) => 72 + ((qubits - xMin) / Math.max(xMax - xMin, 1)) * width;
  const definitions = [
    ["Solver error", "solver_error_hartree", "#58dcc3"],
    ["Active-space error", "active_space_error_hartree", "#7dd3fc"],
    ["Total error", "total_error_hartree", "#fbbf24"],
  ] as const;
  const values = definitions.flatMap(([, key]) => rows.map((row) => row[key])).filter((value): value is number => value !== null).map((value) => Math.max(Math.abs(value), 1e-14));
  const minLog = Math.log10(Math.min(...values, 1e-14));
  const maxLog = Math.log10(Math.max(...values, 1e-3));
  const y = (value: number) => 300 - ((Math.log10(Math.max(Math.abs(value), 1e-14)) - minLog) / Math.max(maxLog - minLog, 1)) * 240;
  const series = definitions.map(([label, key, color]) => {
    const points = rows
      .filter((row) => row[key] !== null && row.num_qubits !== null)
      .map((row) => ({
        x: x(row.num_qubits as number),
        y: y(row[key] as number),
        value: Math.abs(row[key] as number),
        qubits: row.num_qubits as number,
      }));
    return {
      label,
      color,
      points,
      path: points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`).join(" "),
    };
  });
  return {
    series,
    xTicks: rows.map((row) => ({ value: row.num_qubits ?? 0, x: x(row.num_qubits ?? 0) })),
  };
}

function ResourceComparison({ rows }: { rows: ChemistryComparisonRow[] }) {
  const maxPauli = Math.max(...rows.map((row) => row.num_pauli_terms ?? 0), 1);
  return (
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
      {rows.map((row) => (
        <article key={row.configuration_id} className="rounded-md border border-border bg-background/70 p-3">
          <div className="flex items-center justify-between gap-2">
            <p className="font-mono text-sm font-semibold text-primary">CAS({row.n_active_electrons},{row.n_active_orbitals})</p>
            <span className="text-xs text-foreground/45">{row.status}</span>
          </div>
          <div className="mt-4 h-2 overflow-hidden rounded-full bg-muted">
            <div className="h-full bg-primary" style={{ width: `${((row.num_pauli_terms ?? 0) / maxPauli) * 100}%` }} />
          </div>
          <dl className="mt-4 grid grid-cols-2 gap-x-3 gap-y-2 text-xs">
            <Resource label="Qubits" value={row.num_qubits} />
            <Resource label="Pauli" value={row.num_pauli_terms} />
            <Resource label="Parameters" value={row.ansatz_parameters} />
            <Resource label="2q gates" value={row.two_qubit_gates} />
            <Resource label="Evaluations" value={row.optimizer_evaluations} />
            <Resource label="VQE time" value={`${row.vqe_runtime_seconds.toFixed(2)} s`} />
          </dl>
        </article>
      ))}
    </div>
  );
}

function Resource({ label, value }: { label: string; value: number | string | null }) {
  return (
    <div>
      <dt className="text-foreground/45">{label}</dt>
      <dd className="mt-1 font-mono text-foreground/80">{value ?? "—"}</dd>
    </div>
  );
}
