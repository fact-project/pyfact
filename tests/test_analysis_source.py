import astropy.units as u
from pytest import approx


def test_off_position():
    from fact.analysis.source import calc_off_position

    source_x = 50
    source_y = 0

    x_off, y_off = calc_off_position(source_x, source_y, 3, 5)
    assert x_off == approx(-50)
    assert y_off == approx(0)


def test_off_position_units():
    from fact.analysis.source import calc_off_position

    source_x = 50 * u.mm
    source_y = 0 * u.mm

    x_off, y_off = calc_off_position(source_x, source_y, 3, 5)
    assert x_off.unit == u.mm
    assert y_off.unit == u.mm
    assert x_off.to(u.mm).value == approx(-50)
    assert y_off.to(u.mm).value == approx(0)
