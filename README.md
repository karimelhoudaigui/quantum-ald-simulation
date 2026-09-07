# Quantum Simulation of Atomic Layer Deposition Reactions

<p align="center">
  <img src="https://img.shields.io/badge/Quantum%20Chemistry-ALD-blueviolet?style=for-the-badge" />
  <img src="https://img.shields.io/badge/VQE-Hybrid%20Workflow-6A0DAD?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/github/actions/workflow/status/karimelhoudaigui/quantum-ald-simulation/tests.yml?branch=main&style=for-the-badge&label=tests" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />
</p>

This repository implements a reproducible scientific workflow for **hybrid quantum-classical simulation of Atomic Layer Deposition (ALD) reaction models**, including molecular preprocessing, active-space reduction, Hamiltonian mapping, VQE prototyping, noise modeling, error mitigation and visualization.

## Overview

The project provides a compact research framework for:

1. loading molecular geometries;
2. running classical electronic-structure references with PySCF;
3. defining active spaces for quantum simulation;
4. mapping fermionic Hamiltonians to qubit operators;
5. prototyping VQE simulations with Qiskit;
6. adding simplified noise and mitigation studies;
7. generating reaction-energy figures and reproducible tables.

The current examples use small molecules (`H2`, `LiH`, `H2O`) as validation systems before extending the workflow to realistic ALD precursor and surface-fragment chemistry.

## Scientific Motivation

Atomic Layer Deposition is a key thin-film deposition process in semiconductor manufacturing and nanotechnology. Its surface reactions may involve bond breaking, bond formation and electronic correlation effects that are challenging for classical approximations.

Hybrid quantum algorithms such as VQE provide a possible route for studying reduced active-space models on near-term quantum hardware. This repository investigates how such a workflow can be organized and tested in a transparent scientific software project.

## Methodology

The methodology consists of:

- **Classical preprocessing**: HF and DFT calculations with PySCF.
- **Active-space reduction**: compact CAS(n,m) definitions and AVAS hooks.
- **Hamiltonian mapping**: Jordan-Wigner and Bravyi-Kitaev transformations through OpenFermion.
- **Variational simulation**: Qiskit VQE wrappers with configurable ansatz and optimizer.
- **Noise studies**: depolarizing and thermal relaxation models.
- **Error mitigation**: zero-noise extrapolation and simplified CDR correction.
- **Visualization**: energy profiles and convergence plots.

For a compact explanation of the scientific assumptions and representations,
see `docs/technical_background.md`.

## Repository Structure

```text
quantum-ald-simulation/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── requirements.txt
├── environment.yml
├── pyproject.toml
│
├── data/
│   └── geometries/
│
├── src/
│   └── quantum_ald/
│       ├── molecule_loader.py
│       ├── classical_methods.py
│       ├── active_space.py
│       ├── hamiltonian_mapping.py
│       ├── vqe_solver.py
│       ├── noise_models.py
│       ├── error_mitigation.py
│       └── plotting.py
│
├── scripts/
│   ├── run_hf.py
│   ├── run_vqe.py
│   └── plot_energy_profile.py
│
├── notebooks/
├── docs/
├── tests/
└── results/
```

## Installation

For the lightweight package and tests:

```bash
git clone https://github.com/karimelhoudaigui/quantum-ald-simulation.git
cd quantum-ald-simulation
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

For the full chemistry and quantum stack:

```bash
python -m pip install -e ".[dev,chemistry,quantum,notebooks]"
```

With conda:

```bash
conda env create -f environment.yml
conda activate quantum-ald
python -m pip install -e .
```

## Optional Qiskit / OpenFermion setup

The validated fallback pipeline does not require Qiskit or OpenFermion. To run
the optional Jordan-Wigner/OpenFermion checks and the noiseless Qiskit VQE
workflow, install the quantum extra:

```bash
python -m pip install -e ".[quantum]"
```

If extras resolution is fragile in your environment, install the packages
directly:

```bash
python -m pip install qiskit qiskit-aer openfermion
```

On Python 3.9, recent Qiskit versions may emit deprecation warnings because
future Qiskit releases will drop Python 3.9 support. The current workflow uses
Qiskit for circuits, Pauli operators and noiseless statevector evaluation only.

## Usage

Run classical preprocessing:

```bash
python scripts/run_hf.py
```

Generate an example reaction-energy profile:

```bash
python scripts/plot_energy_profile.py
```

Run the VQE demonstration:

```bash
python scripts/run_vqe.py
```

Run the compact H2 VQE workflow (HF + FCI + optional VQE):

```bash
python scripts/run_h2_vqe.py
```

Validate the local H2 pipeline (HF + FCI + local many-body diagonalization +
fallback VQE):

```bash
python scripts/validate_h2_pipeline.py
```

Compute an H2 potential-energy curve:

```bash
python scripts/run_h2_energy_curve.py
```

Prepare a conservative LiH validation report:

```bash
python scripts/validate_lih_pipeline.py
```

Validate the H2 Jordan-Wigner mapping:

```bash
python scripts/validate_jw_h2.py
```

Run the optional noiseless Qiskit VQE backend:

```bash
python scripts/run_h2_qiskit_vqe.py
```

Run the H2 noisy VQE and mitigation workflow:

```bash
python scripts/run_h2_noisy_vqe.py
```

Generate the staged ALD-inspired proxy model catalog:

```bash
python scripts/prepare_ald_proxy_models.py --check-load
```

Reproduce the scientific validation artifacts:

```bash
python scripts/reproduce_scientific_results.py
```

Use strict mode in a full scientific environment to fail on skipped optional
workflows:

```bash
python scripts/reproduce_scientific_results.py --strict
```

Note: the project provides a pure-Python fallback VQE (`FallbackVQESolver`) that
is used when Qiskit/OpenFermion are not installed. This fallback builds a small
many-body Hamiltonian in the occupation-number basis and performs a classical
variational optimization (with exact diagonalization fallback). It is a
pedagogical demonstration for very small systems (H2, LiH minimal bases) and
not intended as a production quantum backend.

Run tests:

```bash
python -m pytest
```

## Results

Generated outputs are written to:

```text
results/tables/
results/figures/
```

Example outputs include:

- `results/tables/hf_energies.csv`
- `results/h2_validation_summary.json`
- `results/tables/h2_energy_curve.csv`
- `results/tables/h2_energy_curve.json`
- `results/figures/h2_energy_curve.png`
- `results/tables/h2_qiskit_vqe_results.json`
- `results/figures/h2_qiskit_vqe_convergence.png`
- `results/figures/energy_profile.png`
- VQE convergence plots for future experiments.

## H2 validation example

The H2/STO-3G pipeline has been validated locally with PySCF FCI as the finite-basis
reference:

```text
HF total:                       -1.116759307396 Ha
FCI total:                      -1.137283834489 Ha
Local diagonalization total:    -1.137283834489 Ha
Fallback VQE total:             -1.137283834488 Ha

diag_manybody total - FCI total: 4.440892e-16 Ha
VQE total - FCI total:           3.086420e-14 Ha
```

Reproduce it with:

```bash
python scripts/validate_h2_pipeline.py
python scripts/run_h2_vqe.py
```

The H2 potential-energy curve is generated by:

```bash
python scripts/run_h2_energy_curve.py
```

Validated curve points currently written to `results/tables/h2_energy_curve.csv`:

| H-H distance (A) | FCI total (Ha) | diag - FCI (Ha) | VQE - FCI (Ha) |
|---:|---:|---:|---:|
| 0.300 | -0.601803710766 | 8.881784e-16 | 8.926193e-14 |
| 0.500 | -1.055159794471 | 4.440892e-16 | 6.217249e-14 |
| 0.700 | -1.136189454066 | 4.440892e-16 | 4.440892e-14 |
| 0.735 | -1.137306035753 | 8.881784e-16 | 3.241851e-14 |
| 1.000 | -1.101150330233 | -4.440892e-16 | 0.000000e+00 |
| 1.500 | -0.998149353471 | -2.220446e-16 | 6.255219e-12 |
| 2.000 | -0.948641112176 | -2.220446e-16 | 1.332268e-15 |
| 2.500 | -0.936054919956 | -2.220446e-16 | 4.440892e-16 |

The lowest sampled FCI point is at 0.735 A with total energy
`-1.137306035753 Ha`.

## LiH CASCI active-space validation

LiH/STO-3G is larger than H2, so the project now validates a reduced active
space against PySCF CASCI before using it as a quantum-simulation model:

```text
LiH/STO-3G
Electrons: 4
Spatial orbitals: 6
Spin orbitals: 12
Fixed-particle sector dimension: 495

HF total: -7.860313085507 Ha
FCI total: -7.881458734732 Ha

CASCI active space: 2 electrons in 2 spatial orbitals
CASCI core energy shift: -6.812098066992 Ha
PySCF CASCI total: -7.860597548130 Ha
Local CASCI total: -7.860597548130 Ha
Local - PySCF CASCI: -8.881784e-16 Ha
```

This CASCI(2,2) reduced model is not the full FCI result. It validates that the
local active-space Hamiltonian, including the PySCF core energy shift, matches
PySCF CASCI. The remaining difference between CASCI(2,2) and full FCI comes
from the active-space truncation.

## Jordan-Wigner validation

The project can explicitly validate the fermion-to-qubit Jordan-Wigner mapping
on H2:

```bash
python scripts/validate_jw_h2.py
```

The validation constructs the H2 fermionic Hamiltonian, maps it to a qubit
Hamiltonian, restricts the qubit matrix to the physical two-electron sector and
compares the resulting ground-state total energy with PySCF FCI. OpenFermion is
used when installed; otherwise the script falls back to a small dense local
Jordan-Wigner matrix for H2. PySCF is still required because the validation uses
PySCF HF/FCI references and molecular integrals.

## Optional Qiskit VQE backend

The pure-Python fallback VQE remains the always-available pedagogical backend
for tiny dense Hamiltonians. A separate optional noiseless Qiskit VQE workflow
is available for environments with Qiskit and PySCF installed:

```bash
python scripts/run_h2_qiskit_vqe.py
```

This workflow uses the local H2 Jordan-Wigner matrix decomposed into Qiskit
Pauli strings, a chemically motivated two-determinant H2 pair ansatz, SciPy
Nelder-Mead multi-start optimization and Qiskit statevector energy evaluation.
OpenFermion is not required for this H2 workflow. The result file separates two
diagnostics: `below_hf` checks whether the variational result improves on
Hartree-Fock, while `near_fci` checks whether it is within the configured FCI
tolerance.

## Noisy VQE and mitigation

The next validation layer applies a deterministic analytic depolarizing profile
to the optimized H2 VQE energy:

```bash
python scripts/run_h2_noisy_vqe.py
```

The workflow writes `results/tables/h2_noisy_vqe_mitigation.json` and
`results/figures/h2_noisy_vqe_noise_scan.png`. It reports the ideal VQE energy,
the noisy energy, a zero-noise extrapolated estimate and a one-point CDR-style
linear correction calibrated on the Hartree-Fock determinant. This is a
reproducibility scaffold before moving to shot-based Qiskit Aer execution.

## ALD-inspired proxy models

The project now includes a staged catalog of small gas-phase proxy models before
attempting larger ALD chemistry:

```bash
python scripts/prepare_ald_proxy_models.py --check-load
```

The catalog includes water as a hydroxyl proxy, LiH as a heteronuclear
metal-ligand proxy, and a minimal Al-O-H fragment in
`data/geometries/aloh_proxy.xyz`. These models are intentionally conservative:
they are active-space testbeds, not surface-embedded ALD mechanisms.

## Reproducible heavy validation

A manual GitHub Actions workflow, `.github/workflows/scientific-validation.yml`,
installs `.[dev,chemistry,quantum]` and runs:

```bash
python scripts/reproduce_scientific_results.py --strict
```

Locally, non-strict mode records missing optional dependencies as skipped and
writes `results/scientific_reproduction_summary.json`. Strict mode is intended
for full environments where PySCF, Qiskit and OpenFermion are installed.

## Current validated status

- H2/STO-3G Hartree-Fock is validated with PySCF.
- PySCF FCI is used as the exact reference inside the finite STO-3G basis.
- The local many-body Hamiltonian is validated in the fixed-electron-number sector.
- Local exact diagonalization is validated against FCI to numerical precision.
- The pure-Python fallback VQE is validated on H2.
- OpenFermion and Qiskit remain optional dependencies.
- The fallback VQE is pedagogical and intended for small systems, not scalable calculations.
- LiH CASCI(2,2) is validated against PySCF CASCI with an explicit core energy shift.
- H2 Jordan-Wigner mapping is validated against the fixed-particle FCI reference.
- H2 Qiskit VQE now has a chemically motivated pair ansatz for FCI-level H2 checks.
- H2 noisy VQE has a deterministic depolarizing model with ZNE and CDR-style correction.
- A first ALD-inspired proxy catalog exists for controlled active-space studies.
- This is still a validation scaffold, not yet a realistic ALD surface simulation.

## Natural roadmap

H2 validated point
-> H2 potential energy curve
-> Jordan-Wigner spectral validation
-> Qiskit VQE backend validation
-> LiH reduced active-space validation
-> noisy VQE
-> error mitigation
-> simplified ALD-inspired molecular models
-> surface-cluster ALD models

## For scientists & community

This project is intended as a reproducible research scaffold for hybrid quantum‑classical
experiments targeting simplified ALD reaction models. If you are a scientist or
developer interested in collaborating, reproducing results, or discussing methods,
please consider the following channels:

- **Issues & PRs**: Use GitHub Issues and Pull Requests on the repository for bug
  reports, feature requests and code contributions.
- **Discussions**: Enable or use [GitHub Discussions](https://github.com/karimelhoudaigui/quantum-ald-simulation/discussions)
  for conceptual questions, reproducibility threads, and methodological discussions.
- **Qiskit / OpenFermion communities**: For algorithmic or runtime help, the
  Qiskit community forum (https://discuss.qiskit.org) and OpenFermion channels are good
  places to ask implementation-specific questions.
- **Stack Exchange**: For focused theoretical questions, use Quantum Computing Stack Exchange
  (https://quantumcomputing.stackexchange.com).

Reproducing the H2 validation example

1. Create a Python environment and install the minimal requirements:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,chemistry]"
```

2. Reproduce the validated H2 pipeline (HF + FCI + many-body diag + fallback VQE):

```bash
python scripts/validate_h2_pipeline.py
python scripts/run_h2_vqe.py
```

Notes

- The `results/` directory contains example outputs for the H2 validation (JSON summary,
  tabular results and a convergence figure). These are included as lightweight examples.
- If you plan to run larger molecules or more realistic ALD fragments, prefer using
  `qiskit-nature` / OpenFermion for robust fermion-to-qubit transformations and
  avoid the naive many-body dense construction used here (it scales exponentially).

If you want, we can enable GitHub Discussions in the repository and add a short
CONTRIBUTING guide explaining how to open reproducible issues and attach environment
information (OS, Python, package versions, and a minimal script to reproduce).

## References

- PySCF: https://pyscf.org/
- Qiskit: https://qiskit.org/
- Qiskit Nature: https://qiskit-community.github.io/qiskit-nature/
- OpenFermion: https://quantumai.google/openfermion
- Peruzzo et al., “A variational eigenvalue solver on a photonic quantum processor,” Nature Communications, 2014.

## Author

Karim El Houdaigui

## License

MIT License. See `LICENSE`.
