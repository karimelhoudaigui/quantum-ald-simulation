# Q-CHEM Lab

Standalone React quantum-chemistry console. Molecular integrals and RHF run in
the visitor's browser through the vendored IQCP WebAssembly engine. AO-to-MO
transforms, CASCI/FCI, Jordan-Wigner resource mapping and exact-statevector
UCCSD VQE run in a separate local Web Worker.

## Local development

```bash
cd qchem-lab
npm install
npm run dev
```

Open `http://127.0.0.1:5173/`. No Python service or API environment variable is
required.

## Checks

```bash
npm test
npm run build
```

## GitHub Pages

The Pages workflow publishes the static interface under
`/quantum-ald-simulation/`, including the local Worker and WASM binaries. The
scientific calculation uses the visitor's CPU and does not submit molecule
data to a remote compute service.

The vendored IQCP revision, checksums and MIT notice are recorded in
`public/wasm/README.md` and `public/wasm/IQCP-LICENSE.txt`.

## Scientific scope

The browser RHF path currently accepts neutral, closed-shell singlets. The
statevector path supports up to 8 active spatial orbitals and a maximum CI
sector dimension of 1200. Larger full-space FCI requests return a structured
partial result while their RHF and feasible active-space calculations remain
available.
