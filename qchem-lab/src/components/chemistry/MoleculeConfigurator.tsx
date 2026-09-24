import {
  Atom,
  Cpu,
  Download,
  Info,
  Loader2,
  Play,
  Plus,
  RotateCcw,
  Trash2,
  Upload,
} from "lucide-react";
import { useMemo, useRef } from "react";

import { ELEMENT_OPTIONS, MOLECULE_PRESETS } from "../../config/chemistry";
import { useChemistryExperiment } from "../../hooks/useChemistryExperiment";
import { parseXyz, serializeXyz } from "../../lib/chemistryXyz";
import {
  useChemistryStore,
  validateChemistryDraft,
} from "../../stores/chemistryStore";
import type {
  ActiveSpaceDraft,
  AtomDraft,
  ChemistryMethod,
  ChemistryValidationError,
} from "../../types/chemistry";
import { IconButton } from "../ui/IconButton";

const methodLabels: Record<ChemistryMethod, string> = {
  hf: "HF",
  casci: "CASCI",
  fci: "FCI",
  vqe: "VQE",
};

export function MoleculeConfigurator() {
  const state = useChemistryStore();
  const { runExperiment, isActive } = useChemistryExperiment();
  const fileInput = useRef<HTMLInputElement | null>(null);
  const immediateErrors = useMemo(() => validateChemistryDraft(state), [state]);
  const errors = state.validationErrors.length > 0 ? state.validationErrors : immediateErrors;

  const importXyz = async (file: File) => {
    try {
      const atoms = parseXyz(await file.text());
      state.replaceAtoms(atoms, file.name.replace(/\.xyz$/i, ""));
      state.setValidationErrors([]);
    } catch (error) {
      state.setValidationErrors([
        {
          code: "invalid_xyz",
          field: "molecule.atoms",
          message: error instanceof Error ? error.message : "Unable to parse XYZ file.",
        },
      ]);
    }
  };

  return (
    <aside className="flex min-h-0 min-w-0 max-w-full flex-col overflow-x-hidden overflow-y-auto overscroll-contain border-b border-border bg-muted/30 p-4 sm:p-5 lg:h-[100svh] lg:border-b-0 lg:border-r">
      <div className="mb-6 flex items-center justify-between gap-3">
        <div className="flex min-w-0 items-center gap-3">
          <img
            src={`${import.meta.env.BASE_URL}qchem-logo.png`}
            alt=""
            aria-hidden="true"
            className="h-10 w-10 shrink-0 object-contain"
          />
          <div className="min-w-0">
            <h2 className="text-lg font-semibold">Q-CHEM Lab</h2>
            <p className="text-sm text-foreground/60">Electronic Structure</p>
          </div>
        </div>
        <IconButton label="Reset chemistry configuration" onClick={state.reset}>
          <RotateCcw size={15} />
        </IconButton>
      </div>

      <div className="space-y-6">
        <ConfigSection title="Molecule" icon={<Atom size={16} />}>
          <label className="block text-sm">
            <span className="font-medium text-foreground/75">Preset</span>
            <select
              aria-label="Molecule preset"
              value={state.selectedPreset}
              onChange={(event) => state.setPreset(event.target.value)}
              className="mt-2 w-full rounded-md border border-border bg-background px-3 py-2 outline-none focus:ring-2 focus:ring-primary"
            >
              {Object.entries(MOLECULE_PRESETS).map(([key, preset]) => (
                <option key={key} value={key}>
                  {preset.name}
                </option>
              ))}
              <option value="custom">Custom</option>
            </select>
          </label>

          <div className="mt-4 grid grid-cols-[3.7rem_repeat(3,minmax(0,1fr))_2.25rem] gap-1 text-[10px] font-medium uppercase text-foreground/45">
            <span>Atom</span>
            <span>X</span>
            <span>Y</span>
            <span>Z</span>
            <span className="sr-only">Delete</span>
          </div>
          <div className="mt-2 space-y-2">
            {state.atoms.map((atom, index) => (
              <AtomRow key={atom.id} atom={atom} index={index} />
            ))}
          </div>
          <FieldErrors errors={errors} prefix="molecule.atoms" />

          <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-3 lg:grid-cols-1 xl:grid-cols-3">
            <button
              type="button"
              onClick={state.addAtom}
              className="inline-flex items-center justify-center gap-2 rounded-md border border-border px-3 py-2 text-xs font-semibold transition hover:bg-background focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <Plus size={14} /> Add atom
            </button>
            <button
              type="button"
              onClick={() => fileInput.current?.click()}
              className="inline-flex items-center justify-center gap-2 rounded-md border border-border px-3 py-2 text-xs font-semibold transition hover:bg-background focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <Upload size={14} /> Import XYZ
            </button>
            <button
              type="button"
              disabled={state.atoms.length === 0}
              onClick={() => downloadText("molecule.xyz", serializeXyz(state.moleculeName, state.atoms))}
              className="inline-flex items-center justify-center gap-2 rounded-md border border-border px-3 py-2 text-xs font-semibold transition hover:bg-background focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-40"
            >
              <Download size={14} /> Export XYZ
            </button>
            <input
              ref={fileInput}
              className="hidden"
              type="file"
              accept=".xyz,text/plain"
              aria-label="Import XYZ file"
              onChange={(event) => {
                const file = event.target.files?.[0];
                if (file) void importXyz(file);
                event.currentTarget.value = "";
              }}
            />
          </div>

          <div className="mt-4 grid grid-cols-2 gap-3">
            <NumberField label="Charge" value={state.charge} onChange={state.setCharge} />
            <NumberField label="Spin" value={state.spin} min={0} onChange={state.setSpin} />
            <label className="text-sm">
              <span className="font-medium text-foreground/75">Basis</span>
              <select
                value={state.basis}
                onChange={(event) => state.setBasis(event.target.value)}
                className="mt-2 w-full rounded-md border border-border bg-background px-3 py-2 outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="sto-3g">STO-3G</option>
                <option value="6-31g">6-31G</option>
              </select>
            </label>
            <label className="text-sm">
              <span className="font-medium text-foreground/75">Unit</span>
              <select
                value={state.unit}
                onChange={(event) => state.setUnit(event.target.value as "angstrom" | "bohr")}
                className="mt-2 w-full rounded-md border border-border bg-background px-3 py-2 outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="angstrom">angstrom</option>
                <option value="bohr">bohr</option>
              </select>
            </label>
          </div>
          <p className="mt-3 flex items-center gap-1.5 text-xs text-foreground/45" title="PySCF spin convention">
            <Info size={13} /> spin = Nα − Nβ = 2S
          </p>
          <FieldErrors errors={errors} prefix="molecule." exclude="molecule.atoms" />
        </ConfigSection>

        <ConfigSection title="Active spaces">
          <div className="space-y-3">
            {state.activeSpaces.map((activeSpace, index) => (
              <ActiveSpaceEditor key={activeSpace.id} activeSpace={activeSpace} index={index} errors={errors} />
            ))}
          </div>
          <button
            type="button"
            onClick={state.addActiveSpace}
            className="mt-3 inline-flex w-full items-center justify-center gap-2 rounded-md border border-border px-3 py-2 text-xs font-semibold transition hover:bg-background focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <Plus size={14} /> Add active space
          </button>
          <FieldErrors errors={errors} prefix="active_spaces" exact />
        </ConfigSection>

        <ConfigSection title="Methods">
          <div className="grid grid-cols-2 gap-2">
            {(Object.keys(methodLabels) as ChemistryMethod[]).map((method) => (
              <label
                key={method}
                className="flex items-center gap-2 rounded-md border border-border bg-background/70 px-3 py-2 text-sm"
              >
                <input
                  type="checkbox"
                  checked={state.methods[method]}
                  disabled={method === "casci" && state.methods.vqe}
                  onChange={(event) => state.setMethod(method, event.target.checked)}
                  className="h-4 w-4 accent-primary"
                />
                {methodLabels[method]}
              </label>
            ))}
          </div>
          {state.methods.vqe ? (
            <p className="mt-3 text-xs leading-5 text-foreground/50">
              CASCI is required as the active-space reference for VQE.
            </p>
          ) : null}
          <FieldErrors errors={errors} prefix="methods" />
        </ConfigSection>

        <ConfigSection title="Quantum">
          <div className="grid grid-cols-2 gap-3">
            <SelectField label="Mapping" value="jordan-wigner" disabled>
              <option value="jordan-wigner">Jordan-Wigner</option>
            </SelectField>
            <SelectField label="Ansatz" value={state.ansatzType} disabled={!state.methods.vqe}>
              <option value="uccsd">UCCSD</option>
            </SelectField>
            <NumberField
              label="Repetitions"
              value={state.reps}
              min={1}
              disabled={!state.methods.vqe}
              onChange={(reps) => state.setQuantumConfig({ reps })}
            />
            <SelectField label="Optimizer" value={state.optimizer} disabled={!state.methods.vqe}>
              <option value="slsqp">SLSQP</option>
            </SelectField>
            <NumberField
              label="Max iterations"
              value={state.maxiter}
              min={1}
              disabled={!state.methods.vqe}
              onChange={(maxiter) => state.setQuantumConfig({ maxiter })}
            />
            <SelectField label="Backend" value={state.executionMode} disabled={!state.methods.vqe}>
              <option value="exact_statevector">Exact statevector</option>
              <option disabled>Shots simulator · Coming soon</option>
              <option disabled>Noisy simulator · Coming soon</option>
              <option disabled>QPU · Coming soon</option>
            </SelectField>
          </div>
          <FieldErrors errors={errors} prefix="ansatz" />
          <FieldErrors errors={errors} prefix="solver" />
        </ConfigSection>

        {state.networkError ? (
          <p role="alert" className="rounded-md border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-200">
            {state.networkError}
          </p>
        ) : null}

        <div className="space-y-2">
          <button
            type="button"
            onClick={runExperiment}
            disabled={isActive || immediateErrors.length > 0}
            className="flex w-full items-center justify-center gap-2 rounded-md bg-primary px-4 py-3 text-sm font-semibold text-background transition hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-background disabled:cursor-not-allowed disabled:opacity-45"
          >
            {isActive ? <Loader2 className="animate-spin" size={16} /> : <Play size={16} />}
            {isActive ? "EXPERIMENT RUNNING" : "RUN EXPERIMENT"}
          </button>
          <button
            type="button"
            disabled
            title="Hardware execution will be enabled when a provider is configured"
            className="flex w-full items-center justify-center gap-2 rounded-md border border-primary/35 bg-primary/[0.04] px-4 py-3 text-sm font-semibold text-primary opacity-55"
          >
            <Cpu size={16} />
            RUN HARDWARE
          </button>
        </div>
      </div>
    </aside>
  );
}

function ConfigSection({ title, icon, children }: { title: string; icon?: React.ReactNode; children: React.ReactNode }) {
  return (
    <section className="border-t border-border pt-5 first:border-t-0 first:pt-0">
      <div className="mb-3 flex items-center gap-2">
        {icon ? <span className="text-primary">{icon}</span> : null}
        <h3 className="text-xs font-semibold uppercase tracking-wide text-foreground/60">{title}</h3>
      </div>
      {children}
    </section>
  );
}

function AtomRow({ atom, index }: { atom: AtomDraft; index: number }) {
  const updateAtom = useChemistryStore((state) => state.updateAtom);
  const removeAtom = useChemistryStore((state) => state.removeAtom);
  const selectAtom = useChemistryStore((state) => state.selectAtom);
  const selected = useChemistryStore((state) => state.selectedAtomId === atom.id);
  return (
    <div
      className={`grid grid-cols-[3.7rem_repeat(3,minmax(0,1fr))_2.25rem] gap-1 rounded-md ${selected ? "ring-2 ring-primary" : ""}`}
      onFocus={() => selectAtom(atom.id)}
    >
      <select
        aria-label={`Atom ${index + 1} element`}
        value={atom.symbol}
        onChange={(event) => updateAtom(atom.id, { symbol: event.target.value })}
        className="min-w-0 rounded-md border border-border bg-background px-1.5 py-2 text-xs outline-none focus:ring-2 focus:ring-primary"
      >
        {ELEMENT_OPTIONS.map((element) => (
          <option key={element}>{element}</option>
        ))}
      </select>
      {(["x", "y", "z"] as const).map((coordinate) => (
        <input
          key={coordinate}
          type="number"
          step="0.01"
          aria-label={`Atom ${index + 1} ${coordinate.toUpperCase()}`}
          value={atom[coordinate]}
          onChange={(event) => updateAtom(atom.id, { [coordinate]: Number(event.target.value) })}
          className="min-w-0 rounded-md border border-border bg-background px-1.5 py-2 font-mono text-xs outline-none focus:ring-2 focus:ring-primary"
        />
      ))}
      <IconButton label={`Delete atom ${index + 1}`} onClick={() => removeAtom(atom.id)}>
        <Trash2 size={14} />
      </IconButton>
    </div>
  );
}

function ActiveSpaceEditor({
  activeSpace,
  index,
  errors,
}: {
  activeSpace: ActiveSpaceDraft;
  index: number;
  errors: ChemistryValidationError[];
}) {
  const update = useChemistryStore((state) => state.updateActiveSpace);
  const remove = useChemistryStore((state) => state.removeActiveSpace);
  return (
    <article className="rounded-md border border-border bg-background/70 p-3">
      <div className="mb-3 flex items-center justify-between">
        <p className="font-mono text-xs font-semibold text-primary">
          CAS({activeSpace.n_active_electrons},{activeSpace.n_active_orbitals})
        </p>
        <IconButton label={`Delete active space ${index + 1}`} onClick={() => remove(activeSpace.id)}>
          <Trash2 size={14} />
        </IconButton>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <NumberField
          label="Electrons"
          value={activeSpace.n_active_electrons}
          min={1}
          onChange={(n_active_electrons) => update(activeSpace.id, { n_active_electrons })}
        />
        <NumberField
          label="Orbitals"
          value={activeSpace.n_active_orbitals}
          min={1}
          onChange={(n_active_orbitals) => update(activeSpace.id, { n_active_orbitals })}
        />
      </div>
      <label className="mt-3 block text-xs">
        <span className="text-foreground/60">Selection</span>
        <select
          value={activeSpace.selection_mode}
          onChange={(event) =>
            update(activeSpace.id, {
              selection_mode: event.target.value as "canonical" | "manual",
            })
          }
          className="mt-1 w-full rounded-md border border-border bg-background px-2 py-2 outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="canonical">canonical</option>
          <option value="manual">manual</option>
        </select>
      </label>
      {activeSpace.selection_mode === "manual" ? (
        <label className="mt-3 block text-xs">
          <span className="text-foreground/60">Orbital indices</span>
          <input
            value={activeSpace.orbitalIndicesInput}
            placeholder="0, 1"
            onChange={(event) => update(activeSpace.id, { orbitalIndicesInput: event.target.value })}
            className="mt-1 w-full rounded-md border border-border bg-background px-2 py-2 font-mono outline-none focus:ring-2 focus:ring-primary"
          />
        </label>
      ) : null}
      <FieldErrors errors={errors} prefix={`active_spaces[${index}]`} />
    </article>
  );
}

function NumberField({
  label,
  value,
  min,
  disabled,
  onChange,
}: {
  label: string;
  value: number;
  min?: number;
  disabled?: boolean;
  onChange: (value: number) => void;
}) {
  return (
    <label className="text-sm">
      <span className="font-medium text-foreground/75">{label}</span>
      <input
        type="number"
        min={min}
        step="1"
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(Number(event.target.value))}
        className="mt-2 w-full min-w-0 rounded-md border border-border bg-background px-3 py-2 font-mono outline-none focus:ring-2 focus:ring-primary disabled:opacity-45"
      />
    </label>
  );
}

function SelectField({
  label,
  value,
  disabled,
  children,
}: {
  label: string;
  value: string;
  disabled?: boolean;
  children: React.ReactNode;
}) {
  return (
    <label className="text-sm">
      <span className="font-medium text-foreground/75">{label}</span>
      <select
        value={value}
        disabled={disabled}
        onChange={() => undefined}
        className="mt-2 w-full min-w-0 rounded-md border border-border bg-background px-2 py-2 text-xs outline-none focus:ring-2 focus:ring-primary disabled:opacity-55"
      >
        {children}
      </select>
    </label>
  );
}

function FieldErrors({
  errors,
  prefix,
  exclude,
  exact = false,
}: {
  errors: ChemistryValidationError[];
  prefix: string;
  exclude?: string;
  exact?: boolean;
}) {
  const matching = errors.filter(
    (error) =>
      (exact ? error.field === prefix : error.field.startsWith(prefix)) &&
      (!exclude || !error.field.startsWith(exclude)),
  );
  if (matching.length === 0) return null;
  return (
    <div className="mt-2 space-y-1" role="alert">
      {matching.map((error) => (
        <p key={`${error.field}-${error.message}`} className="text-xs leading-5 text-red-300">
          {error.message}
        </p>
      ))}
    </div>
  );
}

function downloadText(filename: string, contents: string) {
  const url = URL.createObjectURL(new Blob([contents], { type: "chemical/x-xyz" }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}
