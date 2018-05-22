import astropy.units as u
from pytest import approx


def test_proton_obstime():
    from fact.analysis.statistics import calc_proton_obstime
    n_simulated = 780046520
    t = calc_proton_obstime(
        n_events=n_simulated,
        spectral_index=-2.7,
        max_impact=400 * u.m,
        viewcone=5 * u.deg,
        e_min=100 * u.GeV,
        e_max=200 * u.TeV,
    )
    assert t.to(u.s).value == approx(15397.82)
