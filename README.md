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
- `results/figures/energy_profile.png`
- VQE convergence plots for future experiments.

## Roadmap

- Add realistic ALD precursor/surface cluster geometries.
- Validate active-space Hamiltonian construction against Qiskit Nature.
- Add transition-state and product geometries for energy-barrier estimates.
- Add noiseless and noisy VQE benchmark tables.
- Add notebook execution in CI.
- Add hardware-runtime examples with IBM Quantum backends.

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
