# IQCP browser engine

These files are vendored from the public IQCP deployment and run entirely in
the visitor's browser:

- Upstream: https://github.com/ExaPsi/IQCP
- Source revision: `9aba6729064b59aa76906a88a9f9660bb73fd17d`
- License: MIT, included in `IQCP-LICENSE.txt`
- `iqcp-compute.worker.js` SHA-256: `81712295fbf48fb9489ffed86d35f75b66ee2c8021d5ad54638e3750fe2abaf6`
- `qc_wasm_bg.wasm` SHA-256: `963159774a08d2ff1651b1c63d8e2c32eec3cfc2683d99fe233be30fe6a12a3f`

The worker's WASM URL was changed from the upstream hashed `/assets/` URL to
the adjacent `qc_wasm_bg.wasm` file so that it works below the GitHub Pages
repository base path. No numerical code was modified.
