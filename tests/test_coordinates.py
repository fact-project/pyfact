import pandas as pd
import numpy as np


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
