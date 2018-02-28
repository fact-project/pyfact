import pandas as pd
import numpy as np
from astropy.time import Time
from datetime import datetime


def test_to_astropy_time():
    from fact.coordinates.utils import to_astropy_time

    t = Time('2013-01-01 00:00')

    assert to_astropy_time(datetime(2013, 1, 1)) == t
    assert to_astropy_time(pd.Timestamp(t.unix * 1e9)) == t
    assert to_astropy_time(pd.to_datetime('2013-01-01 00:00')) == t
    assert to_astropy_time(np.array('2013-01-01 00:00', dtype='datetime64[ns]')) == t


def test_transforms():
    from fact.coordinates import camera_to_equatorial

    df = pd.DataFrame({
        'az_tracking': [0, 90, 270],
        'zd_tracking': [0, 10, 20],
        'timestamp': pd.date_range('2017-10-01 22:00Z', periods=3, freq='10min'),
        'x': [-100, 0, 150],
        'y': [0, 100, 0],
    })

    df['ra'], df['dec'] = camera_to_equatorial(
        df.x,
        df.y,
        df.zd_tracking,
        df.az_tracking,
        df.timestamp,
    )


def test_there_and_back_again():
    from fact.coordinates import camera_to_equatorial, equatorial_to_camera

    df = pd.DataFrame({
        'az_tracking': [0, 90, 270],
        'zd_tracking': [0, 10, 20],
        'timestamp': pd.date_range('2017-10-01 22:00Z', periods=3, freq='10min'),
        'x': [-100, 0, 150],
        'y': [0, 100, 0],
    })

    ra, dec = camera_to_equatorial(
        df.x,
        df.y,
        df.zd_tracking,
        df.az_tracking,
        df.timestamp,
    )

    x, y = equatorial_to_camera(ra, dec, df.zd_tracking, df.az_tracking, df.timestamp)

    assert np.allclose(x, df.x)
    assert np.allclose(y, df.y)


def test_there_and_back_again_horizontal():
    from fact.coordinates import camera_to_horizontal, horizontal_to_camera

    df = pd.DataFrame({
        'az_tracking': [0, 90, 270],
        'zd_tracking': [0, 10, 20],
        'timestamp': pd.date_range('2017-10-01 22:00Z', periods=3, freq='10min'),
        'x': [-100, 0, 150],
        'y': [0, 100, 0],
    })

    zd, az = camera_to_horizontal(df.x, df.y, df.zd_tracking, df.az_tracking)
    x, y = horizontal_to_camera(zd, az, df.zd_tracking, df.az_tracking)

    assert np.allclose(x, df.x)
    assert np.allclose(y, df.y)
