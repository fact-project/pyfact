from datetime import datetime, timezone
import pandas as pd
import numpy as np


def test_to_night_int_datetime():
    """ In FACT a day goes from noon to noon and is sometimes referred by a
    single integer: 20151231 for example refers to the night beginning
    on 31.12.2015 evening and lasting until 01.01.2016 morning.
    """
    from fact.time import to_night_int
    from datetime import datetime

    assert to_night_int(datetime(2015, 12, 31, 18, 0)) == 20151231
    assert to_night_int(datetime(2016, 1, 1, 4, 0)) == 20151231


def test_night_integer_pandas():
    """ docu see test above
    """
    from fact.time import to_night_int
    from pandas import to_datetime

    dates = to_datetime([
        "2015-12-31 14:40:15",  # afternoon --> 20151231
        "2016-01-01 04:40:15",  # early morning --> 20151231
        "'2016-01-01 12:40:15"   # next day after noon --> 20160101
    ])
    df = pd.DataFrame({'dates': dates})

    assert (to_night_int(dates) == [20151231, 20151231, 20160101]).all()
    assert (to_night_int(df['dates']) == [20151231, 20151231, 20160101]).all()


def test_datetime_to_mjd():
    from fact.time import datetime_to_mjd, MJD_EPOCH

    assert datetime_to_mjd(MJD_EPOCH) == 0.0

    dt = datetime(2017, 1, 1, 12, 0)
    assert datetime_to_mjd(dt) == 57754.5


def test_datetime_to_mjd_pandas():
    from fact.time import datetime_to_mjd

    dates = pd.date_range('2017-05-17 12:00', freq='1d', periods=5)
    mjd = pd.Series([57890.5, 57891.5, 57892.5, 57893.5, 57894.5])

    df = pd.DataFrame({'dates': dates})

    assert all(datetime_to_mjd(dates) == mjd)
    assert all(datetime_to_mjd(df['dates']) == mjd)


def test_datetime_to_mjd_numpy():
    from fact.time import datetime_to_mjd

    dates = np.array(['2017-05-17 12:00', '2017-05-18 12:00'], dtype='datetime64')
    mjd = np.array([57890.5, 57891.5])

    assert all(datetime_to_mjd(dates) == mjd)


def test_mjd_to_datetime_float():
    from fact.time import mjd_to_datetime, MJD_EPOCH

    assert mjd_to_datetime(0.0) == MJD_EPOCH

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


def test_fjd_to_datetime():
    from fact.time import fjd_to_datetime

    assert fjd_to_datetime(16000.0) == datetime(2013, 10, 22, 0, 0, tzinfo=timezone.utc)
    fjds = pd.Series([0, 365, 18000.5])
    dates = pd.to_datetime(['1970-01-01T00:00', '1971-01-01T00:00', '2019-04-14T12:00'])
    df = pd.DataFrame({'fjds': fjds})
    assert (fjd_to_datetime(fjds) == dates).all()
    assert (fjd_to_datetime(df['fjds']) == pd.Series(dates)).all()


def test_iso_to_datetime():
    from fact.time import iso_to_datetime

    assert iso_to_datetime('2017-01-01T00:00') == datetime(2017, 1, 1, 0, 0, tzinfo=timezone.utc)
    assert iso_to_datetime('2017-01-01T00:00Z') == datetime(2017, 1, 1, 0, 0, tzinfo=timezone.utc)
    assert iso_to_datetime('2017-01-01T00:00+2') == datetime(2016, 12, 31, 22, 0, tzinfo=timezone.utc)

    timestamps = ['2017-01-01T20:00', '2017-01-01T22:00']
    dates = pd.date_range(start='2017-01-01T20:00', freq='2h', periods=2)
    assert (iso_to_datetime(timestamps) == dates).all()
