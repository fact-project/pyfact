'''
This module contains functions to deal with several time formats
in astronomy in general and for the FACT telescope in particular.

FACT uses a Modified Julian Date with an epoch of 1970-01-01T00:00Z,
same as unix time. We will call this FJD.
Most of the time, e.g. in aux fits files, a column called `Time` will use
this modified julian date and also give the reference in the fits header
keyword `MJDREF = 40587`, unit as `TIMEUNIT = d` and `TIMESYS = UTC`.
'''
from datetime import datetime, timedelta, timezone
import warnings

import dateutil
import dateutil.parser
import numpy as np

import pandas as pd

OFFSET = (datetime(1970, 1, 1) - datetime(1, 1, 1)).days

UNIX_EPOCH = datetime(1970, 1, 1, 0, 0, tzinfo=timezone.utc)
MJD_EPOCH = datetime(1858, 11, 17, 0, 0, tzinfo=timezone.utc)


def datetime_to_numpy(dt):
    '''
    Convert a python datetime object to numpy.datetime64
    '''
    return np.array(dt.timestamp()).astype('datetime64[s]')


def unixtime_to_mjd(unixtime):
    '''
    Convert a unix timestamp to mjd
    '''
    return (unixtime - (MJD_EPOCH - UNIX_EPOCH).total_seconds()) / 3600 / 24


def mjd_to_unixtime(mjd):
    '''
    Convert an mjd timestamp to unix
    '''
    return (mjd + (MJD_EPOCH - UNIX_EPOCH).total_seconds()) * 3600 * 24


def datetime_to_mjd(dt, epoch=MJD_EPOCH):
    '''
    Convert a datetime to julian date float.
    This function can handle python dates, numpy arrays and pandas Series.

    Parameters
    ----------
    dt: datetime, np.ndarray[datetime64], pd.DateTimeIndex, pd.Series[datetime64]
        The datetime object to convert to mjd
    epoch: datetime
        The epoch, default is classic MJD (1858-11-17T00:00)
    '''
    # handle numpy arrays
    if isinstance(dt, np.ndarray):
        jd_ns = (dt - datetime_to_numpy(epoch)).astype('timedelta64[ns]').astype(float)
        return jd_ns / 1e9 / 3600 / 24

    # assume datetimes without timezone are utc
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    elif isinstance(dt, pd.DatetimeIndex):
        if dt.tz is None:
            dt = dt.tz_localize(timezone.utc)
    elif isinstance(dt, pd.Series):
        if dt.dt.tz is None:
            dt = dt.dt.tz_localize(timezone.utc)
        return (dt - epoch).dt.total_seconds() / 24 / 3600

    return (dt - epoch).total_seconds() / 24 / 3600


def mjd_to_datetime(jd, epoch=MJD_EPOCH):
    '''
    Convert a julian date float to datetime.
    This function can handle python int, float, numpy arrays and pandas Series.

    Parameters
    ----------
    dt: int, float, np.ndarray, pd.Series
        The datetime object to convert to mjd
    epoch: datetime
        The epoch, default is classic MJD (1858-11-17T00:00)
    '''
    if isinstance(jd, (int, float)):
        delta = timedelta(microseconds=jd * 24 * 3600 * 1e6)
        return epoch + delta

    if isinstance(jd, pd.Series):
        delta = (jd * 24 * 3600 * 1e9).astype('timedelta64[ns]')
        return epoch + delta

    # other types will be returned as numpy array if possible
    jd = np.asanyarray(jd)
    delta = (jd * 24 * 3600 * 1e9).astype('timedelta64[ns]')
    return datetime_to_numpy(epoch) + delta


def fjd_to_datetime(fjd):
    '''
    Convert a FACT julian date float to datetime, epoch is 1970-01-01T00:00Z
    This function can handle python int, float, numpy arrays and pandas Series.
    '''
    return mjd_to_datetime(fjd, epoch=UNIX_EPOCH)


def datetime_to_fjd(dt):
    '''
    Convert a datetime to FACT julian date float, epoch is 1970-01-01T00:00Z.
    This function can handle python dates, numpy arrays and pandas Series.
    '''
    return datetime_to_mjd(dt, epoch=UNIX_EPOCH)


def iso_to_datetime(iso):
    '''
    parse iso8601 to timezone aware datetime instance,
    if timezone specification is missing, UTC is assumed.
    '''
    if isinstance(iso, (bytes, bytearray)):
        iso = iso.decode('ascii')

    if isinstance(iso, str):
        dt = dateutil.parser.parse(iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=dateutil.tz.tzutc())
        return dt

    if isinstance(iso, pd.Series):
        if isinstance(iso.iloc[0], bytes):
            iso = iso.str.decode('ascii')

    return pd.Series(pd.to_datetime(iso))


def to_night(timestamp=None):
    '''
    gives the date for a day change at noon instead of midnight
    '''
    if timestamp is None:
        timestamp = datetime.utcnow()
    if timestamp.hour < 12:
        timestamp = timestamp - timedelta(days=1)
    return timestamp


def to_night_int(date):
    '''
    return FACT night integer for date
    '''
    date -= timedelta(days=0.5)
    if isinstance(date, pd.Series):
        return date.dt.year * 10000 + date.dt.month * 100 + date.dt.day
    return date.year * 10000 + date.month * 100 + date.day
