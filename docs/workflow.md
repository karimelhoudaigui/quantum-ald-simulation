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
python -m pytest
```

Full VQE execution requires the optional quantum stack:

```bash
pip install -e ".[chemistry,quantum]"
python scripts/run_vqe.py
```
