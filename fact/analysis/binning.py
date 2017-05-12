import pandas as pd
import datetime
import numpy as np

from .statistics import li_ma_significance


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


def nightly_binning(runs):
    nights = runs['night'].unique()
    bins = pd.Series(index=runs.index, dtype=int)

    for bin_id, night in enumerate(nights):
        bins.loc[runs.night == night] = bin_id

    return bins


def bin_runs(
        runs,
        alpha=0.2,
        binning_function=ontime_binning,
        **kwargs
        ):
    '''
    Bin runs using `binning_function` to assign bins to
    the individual runs.
    Calculates n_on, n_off, ontime, n_excess, excess_rate_per_h,
    excess_rate_err, li_ma_significance and bin_width

    Parameters
    ----------
    runs: pandas.DataFrame
        The analysis results and necessary metadata for each run.
        Required are: ontime, n_on, n_off, run_start, run_stop, source

    alpha: float
        The weight for the off regions, e.g. 1 / number of off regions

    binning_function: function
        A function that takes the run df and returns a
        pd.Series containing bin ids with the index of the origininal
        dataframe

    All `**kwargs` are passed to the binning function
    '''
    runs = runs.sort_values(by='run_start')
    sources = []
    for source, df in runs.groupby('source'):

        df = df.copy()
        df['bin'] = binning_function(df, **kwargs)

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

        binned['source'] = source
        binned['night'] = (
            binned.time_mean - pd.Timedelta(hours=12)
        ).dt.strftime('%Y%m%d').astype(int)

        sources.append(binned)

    return pd.concat(sources)
