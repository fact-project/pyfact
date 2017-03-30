import pandas as pd
import numpy as np
import datetime


def li_ma_significance(n_on, n_off, alpha=0.2):
    '''
    Calculate the Li&Ma significance for given
    observations data

    Parameters
    ----------
    n_on: integer or array like
        Number of events for the on observations
    n_off: integer of array like
        Number of events for the off observations
    alpha: float
        Scaling factor for the off observations, for wobble observations
        this is 1 / number of off regions
    '''

    scalar = np.isscalar(n_on)

    n_on = np.array(n_on, copy=False, ndmin=1)
    n_off = np.array(n_off, copy=False, ndmin=1)

    with np.errstate(divide='ignore', invalid='ignore'):
        p_on = n_on / (n_on + n_off)
        p_off = n_off / (n_on + n_off)

        t1 = n_on * np.log(((1 + alpha) / alpha) * p_on)
        t2 = n_off * np.log((1 + alpha) * p_off)

        ts = (t1 + t2)
        significance = np.sqrt(ts * 2)

    significance[np.isnan(significance)] = 0
    significance[n_on < alpha * n_off] = 0

    if scalar:
        return significance[0]

    return significance


def ontime_binning(runs, bin_width_minutes=20):
    '''
    Calculate bin numbers for given runs.
    A new bin is created if either a bin would have more ontime
    than `bin_width_minutes` or `run_start` of the next run is
    more than `bin_width_minutes` after `run_stop` of the last run.

    Parameters
    ----------

    runs: pd.DataFrame
        DataFrame containing analysis results and meta data
        for each run
    bin_width_minutes: number
        The desired amount of ontime in each bin.
        Note: The ontime in each bin will allways be
        slightly less than `bin_width_minutes`
    '''
    bin_width_sec = bin_width_minutes * 60
    bin_number = 0
    ontime_sum = 0

    bins = []
    last_stop = runs['run_start'].iloc[0]
    delta_t_max = datetime.timedelta(seconds=bin_width_sec)

    for key, row in runs.iterrows():
        delta_t = row.run_start - last_stop
        last_stop = row.run_stop

        if ontime_sum + row.ontime > bin_width_sec or delta_t > delta_t_max:
            bin_number += 1
            ontime_sum = 0

        bins.append(bin_number)
        ontime_sum += row.ontime

    return pd.Series(bins, index=runs.index)


def qla_binning(data, bin_width_minutes=20):
    '''
    The binning algorithm as used by lightcurve.c
    '''
    bin_number = 0
    ontime_sum = 0
    bins = []
    for key, row in data.iterrows():
        if ontime_sum + row.fOnTimeAfterCuts > bin_width_minutes * 60:
            bin_number += 1
            ontime_sum = 0
        bins.append(bin_number)
        ontime_sum += row['ontime']
    return pd.Series(bins, index=data.index)


def groupby_observation_blocks(runs):
    ''' Groupby for consecutive runs of the same source'''
    runs = runs.sort_values('run_start')
    new_source = runs.fSourceName != runs.fSourceName.shift(1)
    observation_blocks = new_source.cumsum()
    return runs.groupby(observation_blocks)


def bin_runs(
        runs,
        bin_width_minutes,
        alpha=0.2,
        discard_ontime_fraction=0.9,
        binning_function=ontime_binning,
        ):
    '''
    Bin runs into bins with a desired ontime of `bin_width_minutes`
    in each bin.
    A new bin is created if either a bin would have more ontime
    than `bin_width_minutes` or `run_start` of the next run is
    more than `bin_width_minutes` after `run_stop` of the last run.

    Parameters
    ----------
    runs: pandas.DataFrame
        The analysis results and necessary metadata for each run.
        Required are: ontime, n_on, n_off, run_start, run_stop, source_name
    bin_width_minutes: float
        The desired ontime per bin, note: bins will always have less
        ontime than bin_width_minutes.
    alpha: float
        The weight for the off regions, e.g. 1 / number of off regions
    discard_ontime_fraction: float or None
        bins with less than discard_ontime_fraction * bin_width_minutes ontime
        are discarded
    binning_function: function
        A function that takes the run data and a desired bin width
        in minutes and returns a Series of bin ids
    '''
    sources = []
    for source_name, df in runs.groupby('source_name'):
        df = df.copy()
        df['bin'] = binning_function(df, bin_width_minutes)
        binned = df.groupby('bin').aggregate({
            'ontime': 'sum',
            'n_on': 'sum',
            'n_off': 'sum',
            'run_start': 'min',
            'run_stop': 'max',
        })
        binned['n_excess'] = binned.n_on - binned.n_off * alpha
        binned['excess_rate_per_h'] = binned.n_excess / binned.ontime * 3600
        binned['time_width'] = binned.run_stop - binned.run_start
        binned['time_mean'] = binned.run_start + 0.5 * binned.time_width
        binned['excess_rate_err'] = np.sqrt(binned.n_on + alpha**2 * binned.n_off)
        binned['excess_rate_err'] /= binned.ontime / 3600
        binned['significance'] = li_ma_significance(
            binned.n_on, binned.n_off, 0.2
        )
        binned['source_name'] = source_name
        binned['night'] = (
            binned.time_mean - pd.Timedelta(hours=12)
        ).dt.strftime('%Y%m%d').astype(int)

        if discard_ontime_fraction is not None:
            binned = binned.query(
                'ontime >= {}'.format(discard_ontime_fraction * 60 * bin_width_minutes)
            )

        sources.append(binned)

    return pd.concat(sources)
