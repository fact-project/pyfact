from datetime import datetime, timezone
import pandas as pd
import numpy as np


def test_datetime_to_mjd():
    from fact.time import datetime_to_mjd, MJD_EPOCH

    assert datetime_to_mjd(MJD_EPOCH) == 0.0

    dt = datetime(2017, 1, 1, 12, 0)
    assert datetime_to_mjd(dt) == 57754.5


def test_datetime_to_mjd_pandas():
    from fact.time import datetime_to_mjd

    dates = pd.date_range('2017-05-17 12:00', freq='1d', periods=5)

    mjd = pd.Series([57890.5, 57891.5, 57892.5, 57893.5, 57894.5])

    assert all(datetime_to_mjd(dates) == mjd)


def test_datetime_to_mjd_numpy():
    from fact.time import datetime_to_mjd

    dates = np.array(['2017-05-17 12:00', '2017-05-18 12:00'], dtype='datetime64')
    mjd = np.array([57890.5, 57891.5])

    assert all(datetime_to_mjd(dates) == mjd)


def test_mjd_to_datetime_float():
    from fact.time import mjd_to_datetime, MJD_EPOCH

    assert mjd_to_datetime(0) == MJD_EPOCH

    dt = datetime(2017, 5, 17, 18, 0, tzinfo=timezone.utc)
    assert mjd_to_datetime(57890.75) == dt


def test_mjd_to_datetime_numpy():
    from fact.time import mjd_to_datetime

    mjd = np.arange(57890.0, 57891, 0.25)

    dt = np.array(
        ['2017-05-17 00:00', '2017-05-17 06:00',
         '2017-05-17 12:00', '2017-05-17 18:00'],
        dtype='datetime64[us]'
    )

    assert all(mjd_to_datetime(mjd) == dt)


def test_mjd_to_datetime_pandas():
    from fact.time import mjd_to_datetime

    mjd = pd.Series(np.arange(57890.0, 57891, 0.25))

    dt = pd.Series(pd.date_range('2017-05-17 00:00', freq='6h', periods=4))

    assert all(mjd_to_datetime(mjd) == dt)
