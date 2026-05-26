# Methodology

The project is organized as a reproducible scientific workflow rather than a
single notebook.

## Pipeline

1. **Geometry loading**: molecular structures are read from `data/geometries/`.
2. **Classical preprocessing**: PySCF computes HF/DFT references.
3. **Active-space definition**: reduced CAS(n,m) models determine qubit counts.
4. **Hamiltonian mapping**: fermionic operators are mapped to qubit operators.
5. **VQE simulation**: parameterized quantum circuits estimate ground-state
   energies.
6. **Noise and mitigation**: simplified models allow near-term device studies.
7. **Visualization**: energy profiles and convergence curves are saved in
   `results/figures/`.

## Limitations

- Current molecules are validation systems, not full ALD surface models.
- Hamiltonian construction is an educational bridge and should be validated for
  production active-space studies.
- VQE examples are intentionally compact to remain runnable on local machines.
- Realistic ALD chemistry will require surface cluster models, transition-state
  geometries, and larger active-space selection.
