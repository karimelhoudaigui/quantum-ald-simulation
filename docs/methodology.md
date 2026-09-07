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
6. **Noise and mitigation**: deterministic depolarizing studies are combined
   with zero-noise extrapolation and linear CDR-style calibration.
7. **ALD proxy staging**: small gas-phase fragments define controlled
   active-space testbeds before surface-cluster calculations.
8. **Visualization**: energy profiles and convergence curves are saved in
   `results/figures/`.

## Limitations

- Current molecules are validation systems, not full ALD surface models.
- Hamiltonian construction is an educational bridge and should be validated for
  production active-space studies.
- VQE examples are intentionally compact to remain runnable on local machines.
- Realistic ALD chemistry will require surface cluster models, transition-state
  geometries, and larger active-space selection.
- Current ALD-inspired models are proxy fragments and should not be interpreted
  as validated ALD reaction mechanisms.
