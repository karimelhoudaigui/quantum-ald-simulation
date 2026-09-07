from quantum_ald import CDR, ZNE


def test_zne_linear_extrapolation() -> None:
    zne = ZNE(noise_factors=[1.0, 2.0, 3.0])
    mitigated = zne.execute(lambda factor: 2.0 + 0.5 * factor)
    assert abs(mitigated - 2.0) < 1e-10


def test_cdr_identity_correction() -> None:
    cdr = CDR()
    assert cdr.execute(noisy_result=0.5, ideal_result=0.4) == 0.4


def test_cdr_linear_fit() -> None:
    cdr = CDR().fit([1.0, 2.0, 3.0], [2.0, 4.0, 6.0])
    assert abs(cdr.correct(4.0) - 8.0) < 1e-10
