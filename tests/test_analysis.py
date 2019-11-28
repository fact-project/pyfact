import astropy.units as u
from pytest import approx, raises


def test_proton_obstime():
    from fact.analysis.statistics import calc_proton_obstime
    n_simulated = 780046520
    t = calc_proton_obstime(
        n_events=n_simulated,
        spectral_index=-2.7,
        scatter_radius=400 * u.m,
        viewcone=5 * u.deg,
        e_min=100 * u.GeV,
        e_max=200 * u.TeV,
    )
    assert t.to(u.s).value == approx(15397.82)


def test_power():
    from fact.analysis.statistics import random_power

    a = random_power(-2.7, e_min=5 * u.GeV, e_max=10 * u.TeV, size=1000)

    assert a.shape == (1000, )
    assert a.unit == u.TeV

    with raises(ValueError):
        random_power(2.7, 5 * u.GeV, 10 * u.GeV, e_ref=1 * u.GeV, size=1)


def test_power_law_integral():
    from fact.analysis.statistics import power_law_integral, FLUX_UNIT
    import astropy.units as u
    import numpy as np

    # wolfram alpha result https://www.wolframalpha.com/input/?i=int_100%5E1000+x%5E-2
    result = power_law_integral(
        flux_normalization=1 * FLUX_UNIT,
        spectral_index=-2,
        e_min=100 * u.GeV,
        e_max=1000 * u.GeV,
        e_ref=1 * u.GeV,
    )
    assert np.isclose(result.value, 0.009)
    assert result.unit == (FLUX_UNIT * u.GeV)
