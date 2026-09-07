from quantum_ald import get_ald_proxy_model, list_ald_proxy_models


def test_ald_proxy_catalog_has_controlled_models() -> None:
    models = list_ald_proxy_models()

    assert len(models) >= 3
    assert all(model.geometry_path.exists() for model in models)
    assert all(model.active_space["num_spatial_orbitals"] <= 2 for model in models)


def test_get_ald_proxy_model_by_name() -> None:
    model = get_ald_proxy_model("aluminum_hydroxide_proxy")

    assert model.basis == "sto-3g"
    assert "Al-O-H" in model.role
