from quantum_ald import DepolarizingNoiseProfile


def test_depolarizing_profile_increases_with_noise_factor() -> None:
    profile = DepolarizingNoiseProfile(error_rate=0.01, one_qubit_gates=2, two_qubit_gates=1)

    low = profile.effective_probability(noise_factor=1.0)
    high = profile.effective_probability(noise_factor=2.0)

    assert 0.0 < low < high < 1.0


def test_depolarizing_profile_mixes_energy_toward_reference() -> None:
    profile = DepolarizingNoiseProfile(error_rate=0.01, one_qubit_gates=1)

    noisy = profile.mix_energy(ideal_energy=-1.0, maximally_mixed_energy=0.0)

    assert -1.0 < noisy < 0.0
