from datetime import datetime
import pandas as pd
import numpy as np


def test_mjd():
    from fact.time import datetime_to_mjd, MJD_EPOCH

    assert datetime_to_mjd(MJD_EPOCH) == 0.0

    dt = datetime(2017, 1, 1, 12, 0)
    assert datetime_to_mjd(dt) == 57754.5


def test_mjd_pandas():
    from fact.time import datetime_to_mjd

    dates = pd.date_range('2017-05-17 12:00', freq='1d', periods=5)

    mjd = pd.Series([57890.5, 57891.5, 57892.5, 57893.5, 57894.5])

    assert all(datetime_to_mjd(dates) == mjd)


def test_mjd_numpy():
    from fact.time import datetime_to_mjd

    dates = np.array(['2017-05-17 12:00', '2017-05-18 12:00'], dtype='datetime64')
    mjd = np.array([57890.5, 57891.5])

    assert all(datetime_to_mjd(dates) == mjd)
