# Quantum Simulation of Atomic Layer Deposition Reactions

<p align="center">
  <img src="https://img.shields.io/badge/Quantum%20Chemistry-ALD-blueviolet?style=for-the-badge" />
  <img src="https://img.shields.io/badge/VQE-Hybrid%20Workflow-6A0DAD?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
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
- `results/figures/energy_profile.png`
- VQE convergence plots for future experiments.

## Roadmap

- Add realistic ALD precursor/surface cluster geometries.
- Validate active-space Hamiltonian construction against Qiskit Nature.
- Add transition-state and product geometries for energy-barrier estimates.
- Add noiseless and noisy VQE benchmark tables.
- Add notebook execution in CI.
- Add hardware-runtime examples with IBM Quantum backends.

## Validation status

Current validated items (as of this commit):

- **HF / FCI on H2**: implemented and tested via PySCF (small STO-3G example).
- **Diagonalization of many-body Hamiltonian**: `build_many_body_hamiltonian` constructs
  a dense occupation-number Hamiltonian; its ground-state eigenvalue matches PySCF FCI for H2.
- **Fallback VQE**: `FallbackVQESolver` performs a pure-Python variational solve
  (with classical optimizer and exact-diagonalization fallback) for small systems.
- **Jordan-Wigner mapping**: optional tests compare spectra with OpenFermion/Qiskit when available.

Note: OpenFermion and Qiskit-related validations are optional and tests will be skipped
if those packages are not installed. The fallback VQE is pedagogical and intended only
for tiny demonstration systems (H2, LiH minimal bases), not as a production quantum backend.

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
