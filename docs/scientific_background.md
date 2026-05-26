# Scientific Background

Atomic Layer Deposition (ALD) is a vapor-phase thin-film growth technique based
on self-limiting surface reactions. The electronic structure of precursor
molecules, transition states and surface fragments can involve correlation
effects that motivate reduced active-space quantum simulations.

This repository provides a compact hybrid classical-quantum workflow:

1. molecular geometries are loaded from XYZ files;
2. classical Hartree-Fock or DFT references are computed with PySCF;
3. active spaces are defined to reduce the electronic problem;
4. fermionic Hamiltonians are mapped to qubit Hamiltonians;
5. VQE is used as a prototype ground-state solver;
6. noise and mitigation utilities support near-term quantum studies.

The current geometries are small reference systems (`H2`, `LiH`, `H2O`) used to
validate the workflow before moving to realistic ALD precursor/surface models.

## Key Concepts

- **Hartree-Fock (HF)**: mean-field approximation used as a baseline.
- **Active space**: a selected subset of electrons and orbitals retained for
  correlated or quantum simulation.
- **Fermion-to-qubit mapping**: transformation from electronic operators to
  Pauli operators, e.g. Jordan-Wigner.
- **VQE**: variational quantum-classical algorithm for estimating ground-state
  energies.
- **Error mitigation**: post-processing strategies for noisy quantum estimates.
