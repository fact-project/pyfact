''' some functions to deal with FACT modified modified julian date

The time used most of the time in FACT is the number of days since 01.01.1970

So this time is related to unix time, since it has the same offset
(unix time is the number of seconds since 01.01.1970
(what time? noon? midnight??))
but it is also related to 'the' Modified Julian Date (MJD),
which is used by astronomers
in the sense, that it also counts days.

According to http://en.wikipedia.org/wiki/Julian_day,
there is quite a large number of
somehow modified julian dates, of which the MJD is only one.
So it might be okay, to introduce a new modification,
going by the name of FACT Julain Date (FJD).
'''
from __future__ import print_function, division
import time
import calendar
from datetime import datetime, timedelta, timezone
import logging

import dateutil
import dateutil.parser
import numpy as np

import pandas as pd

OFFSET = (datetime(1970, 1, 1) - datetime(1, 1, 1)).days

UNIX_EPOCH = datetime(1970, 1, 1, 0, 0, tzinfo=timezone.utc)
MJD_EPOCH = datetime(1858, 11, 17, 0, tzinfo=timezone.utc)
MJD_EPOCH_NUMPY = np.array(MJD_EPOCH.timestamp()).astype('datetime64[s]')


def unixtime_to_mjd(unixtime):
    return (unixtime - (MJD_EPOCH - UNIX_EPOCH).total_seconds()) / 3600 / 24


def mjd_to_unixtime(mjd):
    return (mjd + (MJD_EPOCH - UNIX_EPOCH).total_seconds()) * 3600 * 24


def datetime_to_mjd(dt):
    # handle numpy arrays
    if isinstance(dt, np.ndarray):
        mjd_ns = (dt - MJD_EPOCH_NUMPY).astype('timedelta64[ns]').astype(float)
        return mjd_ns / 1e9 / 3600 / 24

    # assume datetimes without timezone are utc
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

    elif isinstance(dt, (pd.Series, pd.DatetimeIndex)):
        if dt.tz is None:
            dt.tz = timezone.utc

    return (dt - MJD_EPOCH).total_seconds() / 24 / 3600


def mjd_to_datetime(mjd):
    if isinstance(mjd, (int, float)):
        delta = timedelta(microseconds=mjd * 24 * 3600 * 1e6)
        return MJD_EPOCH + delta

    if isinstance(mjd, pd.Series):
        delta = (mjd * 24 * 3600 * 1e9).astype('timedelta64[ns]')
        return MJD_EPOCH + delta

    # other types will be returned as numpy array if possible
    mjd = np.asanyarray(mjd)
    delta = (mjd * 24 * 3600 * 1e9).astype('timedelta64[ns]')
    return MJD_EPOCH_NUMPY + delta


def fjd(datetime_inst):
    ''' convert datetime instance to FJD
    '''
    if datetime_inst.tzinfo is None:
        logging.warning('datetime instance is not aware of its timezone.'
                        'result possibly wrong!')
    return calendar.timegm(datetime_inst.utctimetuple()) / (24. * 3600.)


def iso2dt(iso_time_string):
    ''' parse ISO time string to timezone aware datetime instance

    example
    2015-01-23T08:08+01:00
    '''
    datetime_inst = dateutil.parser.parse(iso_time_string)
    # make aware at any cost!
    if datetime_inst.tzinfo is None:
        logging.info('ISO time string did not contain timezone info. I assume UTC!')
        datetime_inst = datetime_inst.replace(tzinfo=dateutil.tz.tzutc())
    return datetime_inst


def run2dt(run_string):
    ''' parse typical FACT run file path string to datetime instance (UTC)

    example
    first you do this:

    '/path/to/file/20141231.more_text' --> '20141231'
    then call
    run2dt('20141231')
    '''
    format_ = '%Y%m%d'
    datetime_inst = datetime.strptime(run_string, format_)
    datetime_inst = datetime_inst.replace(tzinfo=dateutil.tz.tzutc())
    return datetime_inst


def facttime(time_string):
    ''' conver time-string to fact time
    '''
    return calendar.timegm(time.strptime(
        time_string, '%Y%m%d %H:%M')) / (24. * 3600.)


def to_datetime(fact_julian_date):
    ''' convert facttime to datetime instance
    '''
    unix_time = fact_julian_date * 24 * 3600
    datetime_inst = datetime.utcfromtimestamp(unix_time)
    return datetime_inst


def datestr(datetime_inst):
    ''' make iso time string from datetime instance
    '''
    return datetime_inst.isoformat('T')


def night(timestamp=None):
    '''
    gives the date for a day change at noon instead of midnight
    '''
    if timestamp is None:
        timestamp = datetime.utcnow()
    if timestamp.hour < 12:
        timestamp = timestamp - timedelta(days=1)
    return timestamp


def night_integer(date):
    ''' return FACT night integer for date
    '''
    date -= pd.Timedelta(days=0.5)
    night_int = date.year * 10000 + date.month * 100 + date.day
    return night_int
