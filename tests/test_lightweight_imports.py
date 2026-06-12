import importlib


def test_core_modules_import_without_optional_quantum_stack() -> None:
    modules = [
        "quantum_ald.molecule_loader",
        "quantum_ald.active_space",
        "quantum_ald.classical_methods",
        "quantum_ald.hamiltonian_mapping",
        "quantum_ald.vqe_solver",
    ]

    for module in modules:
        importlib.import_module(module)


def test_package_import_does_not_require_qiskit_or_openfermion() -> None:
    importlib.import_module("quantum_ald")
