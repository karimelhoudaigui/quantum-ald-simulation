# Contributing

Contributions are welcome.

## Development Setup

```bash
git clone https://github.com/karimelhoudaigui/quantum-ald-simulation
cd quantum-ald-simulation
conda env create -f environment.yml
conda activate quantum-ald
pip install -e ".[dev,chemistry,quantum,notebooks]"
```

## Code Standards

- Use clear scientific names.
- Add type hints for public functions.
- Add docstrings to modules, classes and public functions.
- Keep tests focused and reproducible.
- Run `pytest` before submitting changes.

## Submitting Changes

1. Create a feature branch.
2. Add or update tests.
3. Ensure `pytest` passes.
4. Submit a pull request with a concise scientific motivation.

## Issues

Please include:

- a minimal reproducible example;
- Python and package versions;
- the full traceback if reporting a bug.
