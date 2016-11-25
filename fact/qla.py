import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter


def dorner_binning(data, bin_width_minutes=20):
    bin_number = 0
    ontime_sum = 0
    bins = []
    for key, row in data.iterrows():
        if ontime_sum + row.fOnTimeAfterCuts > bin_width_minutes * 60:
            bin_number += 1
            ontime_sum = 0
        bins.append(bin_number)
        ontime_sum += row['fOnTimeAfterCuts']
    return pd.Series(bins, index=data.index)


def groupby_observation_blocks(runs):
    ''' Groupby for consecutive runs of the same source'''
    runs = runs.sort_values('fRunStart')
    new_source = runs.fSourceName != runs.fSourceName.shift(1)
    observation_blocks = new_source.cumsum()
    return runs.groupby(observation_blocks)


def get_qla_data(night, database_engine):
    ''' this will get the QLA results to call if you have to send an alert '''
    keys = [
        'QLA.fRunID',
        'QLA.fNight',
        'QLA.fNumExcEvts',
        'QLA.fNumSigEvts',
        'QLA.fNumBgEvts',
        'QLA.fOnTimeAfterCuts',
        'RunInfo.fRunStart',
        'RunInfo.fRunStop',
        'Source.fSourceName',
        'Source.fSourceKEY',
    ]

    sql_query = """SELECT {comma_sep_keys}
        FROM AnalysisResultsRunLP QLA
        LEFT JOIN RunInfo
        ON QLA.fRunID = RunInfo.fRunID AND QLA.fNight = RunInfo.fNight
        LEFT JOIN Source
        ON RunInfo.fSourceKEY = Source.fSourceKEY
        WHERE QLA.fNight = {night}
    """
    sql_query = sql_query.format(
        comma_sep_keys=', '.join(keys),
        night=night,
    )

    data = pd.read_sql_query(
        sql_query,
        database_engine,
        parse_dates=['fRunStart', 'fRunStop'],
    )

    # drop rows with NaNs from the table, these are unfinished qla results
    data.dropna(inplace=True)

    if len(data.index) == 0:
        return

    data.sort_values('fRunStart', inplace=True)
    data.reset_index(inplace=True)

    return data


def bin_qla_data(data, bin_width_minutes):
    grouped = groupby_observation_blocks(data)
    binned = pd.DataFrame()
    for block, group in grouped:
        group = group.copy()
        group['bin'] = dorner_binning(group, bin_width_minutes)
        agg = group.groupby('bin').aggregate({
            'fOnTimeAfterCuts': 'sum',
            'fNumExcEvts': 'sum',
            'fNumSigEvts': 'sum',
            'fNumBgEvts': 'sum',
            'fRunStart': 'min',
            'fRunStop': 'max',
            'fSourceName': lambda x: x.iloc[0],
        })
        agg['rate'] = agg.fNumExcEvts / agg.fOnTimeAfterCuts * 3600
        agg['xerr'] = (agg.fRunStop - agg.fRunStart) / 2
        agg['timeMean'] = agg.fRunStart + agg.xerr
        agg['yerr'] = np.sqrt(agg.fNumSigEvts + 0.2 * agg.fNumBgEvts)
        agg['yerr'] /= agg.fOnTimeAfterCuts / 3600
        # remove last bin if it has less then 90% OnTime of the required
        # binning
        if agg['fOnTimeAfterCuts'].iloc[-1] < 0.9 * 60 * bin_width_minutes:
            agg = agg.iloc[:-1]
        binned = binned.append(agg, ignore_index=True)

    binned['significance'] = li_ma_significance(
        binned.fNumSigEvts, binned.fNumBgEvts * 5, 0.2
    )

    return binned


def li_ma_significance(N_on, N_off, alpha=0.2):
    N_on = np.array(N_on, copy=False, ndmin=1)
    N_off = np.array(N_off, copy=False, ndmin=1)

    with np.errstate(divide='ignore', invalid='ignore'):
        p_on = N_on / (N_on + N_off)
        p_off = N_off / (N_on + N_off)

        t1 = N_on * np.log(((1 + alpha) / alpha) * p_on)
        t2 = N_off * np.log((1 + alpha) * p_off)

        ts = (t1 + t2)
        significance = np.sqrt(ts * 2)

    significance[np.isnan(significance)] = 0
    significance[N_on < alpha * N_off] = 0

    return significance


def plot_qla(binned_qla_data, outputfile=None):
    '''
    Create a plot of the binned qla results

    returns the two axes used: ax_rate is the upper axes for the rates
    and ax_sig is the lower axes for the significance
    '''
    plt.style.use('ggplot')

    fig = plt.figure(figsize=(15/2.54, 10/2.54))

    ax_sig = fig.add_axes([0.12, 0.15, 0.85, 0.2])
    ax_rate = fig.add_axes([0.12, 0.4, 0.85, 0.40], sharex=ax_sig)

    colors = [e['color'] for e in plt.rcParams['axes.prop_cycle']]
    for (name, group), color in zip(binned_qla_data.groupby('fSourceName'), colors):
        if len(group.index) == 0:
            continue

        ax_rate.errorbar(
            x=group.timeMean.values,
            y=group.rate.values,
            xerr=group.xerr.values,
            yerr=group.yerr.values,
            label=name,
            fmt='o',
            mec='none',
            color=color,
        )

        ax_sig.errorbar(
            x=group.timeMean.values,
            y=group.significance.values,
            xerr=group.xerr.values,
            label=name,
            fmt='o',
            mec='none',
            color=color,
        )
    ax_rate.legend(
        loc='lower center',
        ncol=3,
        columnspacing=0.5,
        numpoints=1,
        handletextpad=0.1,
        bbox_to_anchor=[0.5, 1.01],
    )
    ax_rate.set_ylabel('Excess Event Rate / $\mathrm{h}^{-1}$')

    ax_sig.axhline(3, color='darkgray')
    ax_sig.set_ylabel('$S_{\mathrm{Li/Ma}} \,\, / \,\, \sigma$')

    ymax = max(3.25, np.ceil(ax_sig.get_ylim()[1]))
    ax_sig.set_ylim(0, ymax)
    ax_sig.set_yticks(np.arange(0, ymax + 0.1, ymax // 4 + 1))

    plt.setp(ax_rate.get_xticklabels(), visible=False)

    plt.setp(ax_sig.get_xticklabels(), rotation=30, va='top', ha='right')
    ax_sig.xaxis.set_major_formatter(DateFormatter('%H:%M'))

    if outputfile is not None:
        fig.savefig(outputfile)

    return ax_rate, ax_sig
