def test_tk():
    from matplotlib.backends import _tkagg


def test_cameraplot():
    from fact.plotting import camera
    from numpy.random import uniform

    data = uniform(0, 20, 1440)
    camera(data)


def test_night_integer_datetime():
    """ In FACT a day goes from noon to noon and is sometimes referred by a
    single integer: 20151231 for example refers to the night beginning
    on 31.12.2015 evening and lasting until 01.01.2016 morning.
    """
    from fact import night_integer
    from datetime import datetime

    assert night_integer(datetime(2015, 12, 31, 18, 0)) == 20151231
    assert night_integer(datetime(2016, 1, 1, 4, 0)) == 20151231


def test_night_integer_pandas_datetimeindex():
    """ docu see test above
    """
    from fact import night_integer
    from pandas import to_datetime

    dates = to_datetime([
        "2015-12-31 14:40:15",  # afternoon --> 20151231
        "2016-01-01 04:40:15",  # early morning --> 20151231
        "'2016-01-01 12:40:15"   # next day after noon --> 20160101
        ])

    assert (night_integer(dates) == [20151231, 20151231, 20160101]).all()
