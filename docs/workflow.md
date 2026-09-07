# Workflow

```text
XYZ Geometries
   ↓
PySCF Molecule
   ↓
HF / DFT Reference Calculation
   ↓
Active Space Selection
   ↓
Fermionic Hamiltonian
   ↓
Qubit Mapping
   ↓
VQE Simulation
   ↓
Noise / Error Mitigation
   ↓
Energy Tables and Figures
```

## Main Commands

```bash
python scripts/run_hf.py
python scripts/plot_energy_profile.py
python scripts/prepare_ald_proxy_models.py
python -m pytest
```

Full VQE execution requires the optional quantum stack:

```bash
pip install -e ".[chemistry,quantum]"
python scripts/run_vqe.py
python scripts/run_h2_qiskit_vqe.py
python scripts/run_h2_noisy_vqe.py
python scripts/reproduce_scientific_results.py --strict
```

The default GitHub Actions test workflow remains lightweight. The manual
`Scientific Validation` workflow installs the full chemistry and quantum stack,
runs the reproduction script in strict mode and uploads generated result files.
