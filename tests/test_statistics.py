from pytest import approx


def test_units():
    '''
    Test if scaling factors with different units behave nicely
    '''

    from fact.analysis import li_ma_significance
    import astropy.units as u

    n_on = 20
    n_off = 30

    t1 = 3600 * u.s
    t2 = 1 * u.h

    r = t1 / t2

    s1 = li_ma_significance(n_on, n_off)
    s2 = li_ma_significance(n_on * r, n_off * r)

    assert s2 == approx(s1)


def test_scaler():
    from fact.analysis import li_ma_significance
    import numpy as np

    s = li_ma_significance(20, 30)

    assert np.isscalar(s)


def test_list():
    from fact.analysis import li_ma_significance

    s = li_ma_significance([20, 10], [30, 20])

    assert len(s) == 2


def test_invalid():
    from fact.analysis import li_ma_significance

    s = li_ma_significance(20, 30, alpha=1)

    assert s == 0
