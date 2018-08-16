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
    return np.array(dt.timestamp()).astype('datetime64[s]')


def unixtime_to_mjd(unixtime):
    return (unixtime - (MJD_EPOCH - UNIX_EPOCH).total_seconds()) / 3600 / 24


def mjd_to_unixtime(mjd):
    return (mjd + (MJD_EPOCH - UNIX_EPOCH).total_seconds()) * 3600 * 24


def datetime_to_mjd(dt, epoch=MJD_EPOCH):
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
    return mjd_to_datetime(fjd, epoch=UNIX_EPOCH)


def datetime_to_fjd(dt):
    return datetime_to_mjd(dt, epoch=UNIX_EPOCH)


def iso_to_datetime(iso_time_string):
    ''' parse ISO time string to timezone aware datetime instance

    example
    2015-01-23T08:08+01:00
    '''
    datetime_inst = dateutil.parser.parse(iso_time_string)
    # make aware at any cost!
    if datetime_inst.tzinfo is None:
        warnings.warn('ISO time string did not contain timezone info. I assume UTC!')
        datetime_inst = datetime_inst.replace(tzinfo=dateutil.tz.tzutc())
    return datetime_inst


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
