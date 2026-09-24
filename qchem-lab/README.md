# Q-CHEM Lab

Standalone React interface for the validated `quantum-ald-simulation`
`ExperimentConfig -> run_experiment() -> ExperimentResult` workflow.

## Local development

Start the scientific API from the repository root:

```bash
python -m pip install -e ".[service,chemistry,quantum]"
python scripts/serve_experiment_api.py
```

Start the interface in another terminal:

```bash
cd qchem-lab
npm install
npm run dev
```

Open `http://127.0.0.1:5173/`. The Vite development server proxies
`/api/chemistry` to `http://127.0.0.1:8002`. For a separately hosted API, set
`VITE_CHEMISTRY_API_BASE_URL` to its origin. The frontend never fabricates
scientific results when the API is unavailable.

## Checks

```bash
npm test
npm run build
```

The backend queue is intentionally in memory for this MVP. Restarting the API
loses existing job identifiers and results.

## GitHub Pages

The Pages workflow publishes the static interface under
`/quantum-ald-simulation/`. GitHub Pages does not run the Python chemistry
service. Set the repository variable `QCHEM_API_BASE_URL` to a public HTTPS
deployment of `quantum_ald.service.api` to enable experiments on the published
site.
