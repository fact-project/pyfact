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
