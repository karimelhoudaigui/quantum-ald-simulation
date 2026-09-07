# Contributing

Contributions are welcome. Please keep changes reproducible and explicit about
which dependencies are required.

## Development Setup

Lightweight test environment:

```bash
git clone https://github.com/karimelhoudaigui/quantum-ald-simulation
cd quantum-ald-simulation
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Full chemistry and optional quantum stack:

```bash
python -m pip install -e ".[dev,chemistry,quantum,notebooks]"
```

Conda users can also run:

```bash
conda env create -f environment.yml
conda activate quantum-ald
python -m pip install -e ".[dev]"
```

## Running Tests

Base tests:

```bash
pytest -q
```

Optional tests that require PySCF, OpenFermion, Qiskit or Qiskit Nature should
skip cleanly when those packages are not installed. Do not relax scientific
tolerances to hide energy, Hamiltonian or mapping errors.

Full scientific reproduction:

```bash
python scripts/reproduce_scientific_results.py --strict
```

Run this in an environment installed with `.[dev,chemistry,quantum]`. In a
lightweight environment, omit `--strict`; missing optional dependencies are then
recorded as skipped in `results/scientific_reproduction_summary.json`.

## Reproducing H2

With the chemistry dependencies installed:

```bash
python scripts/validate_h2_pipeline.py
python scripts/run_h2_vqe.py
python scripts/run_h2_energy_curve.py
python scripts/run_h2_qiskit_vqe.py
python scripts/run_h2_noisy_vqe.py
```

These commands reproduce the H2 HF, FCI, local many-body diagonalization and
fallback VQE validations.

## Code Standards

- Use clear scientific names.
- Add type hints for public functions.
- Add docstrings to modules, classes and public functions.
- Keep tests focused and reproducible.
- Keep Qiskit/OpenFermion/PySCF integrations optional unless the feature truly
  requires them.

## Submitting Changes

1. Create a feature branch.
2. Add or update tests.
3. Run `pytest -q`.
4. Submit a pull request with a concise scientific motivation and the commands
   used for validation.

## Reproducible Issues

Please include:

- operating system;
- Python version;
- package versions, ideally from `python -m pip freeze`;
- exact command that failed;
- complete traceback;
- a minimal script or test case that reproduces the issue;
- whether optional dependencies such as PySCF, OpenFermion, Qiskit or Qiskit
  Nature are installed.
