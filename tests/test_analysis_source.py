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


def test_theta():
    from fact.io import read_data
    from fact.analysis import calc_theta_camera

    df = read_data('tests/resources/gammas.hdf5', key='events')

    theta = calc_theta_camera(
        df.source_x_prediction, df.source_y_prediction,
        df.zd_source_calc, df.az_source_calc,
        df.zd_tracking, df.az_tracking,
    )

    assert len(theta) == len(df)


def test_theta_offs():
    from fact.io import read_data
    from fact.analysis import calc_theta_offs_camera

    df = read_data('tests/resources/gammas.hdf5', key='events')

    theta_offs = calc_theta_offs_camera(
        df.source_x_prediction, df.source_y_prediction,
        df.zd_source_calc, df.az_source_calc,
        df.zd_tracking, df.az_tracking,
        n_off=5
    )

    assert len(theta_offs) == 5
    assert all(len(theta_off) == len(df) for theta_off in theta_offs)


if __name__ == '__main__':
    test_theta()
