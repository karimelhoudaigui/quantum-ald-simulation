"""Controlled ALD-inspired proxy model definitions."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .molecule_loader import Molecule, load_molecule

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ALDProxyModel:
    """Small molecular proxy for staged ALD quantum-simulation validation."""

    name: str
    role: str
    geometry_path: Path
    basis: str
    charge: int
    spin: int
    active_space: dict[str, int]
    validation_target: str
    limitations: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        try:
            data["geometry_path"] = str(self.geometry_path.relative_to(PROJECT_ROOT))
        except ValueError:
            data["geometry_path"] = str(self.geometry_path)
        return data

    def load(self) -> Molecule:
        """Load the proxy as a PySCF-backed Molecule."""
        return load_molecule(
            self.geometry_path,
            basis=self.basis,
            charge=self.charge,
            spin=self.spin,
        )


ALD_PROXY_MODELS = [
    ALDProxyModel(
        name="surface_hydroxyl_proxy",
        role="Surface hydroxyl / ligand proton-transfer proxy",
        geometry_path=PROJECT_ROOT / "data" / "geometries" / "h2o.xyz",
        basis="sto-3g",
        charge=0,
        spin=0,
        active_space={"num_electrons": 2, "num_spatial_orbitals": 2},
        validation_target="CASCI active-space sanity check before bond-stretch scans",
        limitations="Gas-phase water is not a surface cluster; it only tests O-H local chemistry.",
    ),
    ALDProxyModel(
        name="metal_hydride_proxy",
        role="Small heteronuclear metal-ligand bond proxy",
        geometry_path=PROJECT_ROOT / "data" / "geometries" / "lih.xyz",
        basis="sto-3g",
        charge=0,
        spin=0,
        active_space={"num_electrons": 2, "num_spatial_orbitals": 2},
        validation_target="Reduced CASCI benchmark already validated against PySCF CASCI",
        limitations="LiH is a numerically convenient proxy, not an ALD precursor.",
    ),
    ALDProxyModel(
        name="aluminum_hydroxide_proxy",
        role="Minimal Al-O-H fragment for ALD-inspired precursor/surface contact",
        geometry_path=PROJECT_ROOT / "data" / "geometries" / "aloh_proxy.xyz",
        basis="sto-3g",
        charge=0,
        spin=0,
        active_space={"num_electrons": 2, "num_spatial_orbitals": 2},
        validation_target="HF/CASCI feasibility check followed by active-space refinement",
        limitations="No surface embedding, ligands, transition state or periodic boundary condition.",
    ),
]


def list_ald_proxy_models() -> list[ALDProxyModel]:
    """Return the staged ALD-inspired model catalog."""
    return list(ALD_PROXY_MODELS)


def get_ald_proxy_model(name: str) -> ALDProxyModel:
    """Return a proxy model by name."""
    for model in ALD_PROXY_MODELS:
        if model.name == name:
            return model
    available = ", ".join(model.name for model in ALD_PROXY_MODELS)
    raise KeyError(f"Unknown ALD proxy model '{name}'. Available models: {available}")
