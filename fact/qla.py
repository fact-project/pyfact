import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

from .factdb import (
    read_into_dataframe,
    AnalysisResultsRunLP as QLA,
    RunInfo,
    Source
)


def get_qla_data(
        first_night,
        last_night=None,
        sources=None,
        database_engine=None
        ):
    '''
    Request QLA results from our database
    '''

    if last_night is None:
        last_night = first_night

    query = QLA.select(
        QLA.frunid.alias('run_id'),
        QLA.fnight.alias('night'),
        QLA.fnumexcevts.alias('n_excess'),
        QLA.fnumsigevts.alias('n_on'),
        (QLA.fnumbgevts * 5).alias('n_off'),
        QLA.fontimeaftercuts.alias('ontime'),
        RunInfo.frunstart.alias('run_start'),
        RunInfo.frunstop.alias('run_stop'),
        Source.fsourcename.alias('source_name'),
        Source.fsourcekey.alias('source_key'),
    )

    on = (RunInfo.fnight == QLA.fnight) & (RunInfo.frunid == QLA.frunid)
    query = query.join(RunInfo, on=on)
    query = query.join(Source, on=RunInfo.fsourcekey == Source.fsourcekey)
    query = query.where(QLA.fnight >= first_night)
    query = query.where(QLA.fnight <= last_night)

    if sources is not None:
        query = query.where(Source.fsourcename.in_(sources))

    runs = read_into_dataframe(query, engine=database_engine)

    # drop rows with NaNs from the table, these are unfinished qla results
    runs.dropna(inplace=True)

    runs.sort_values('run_start', inplace=True)

    return runs


def plot_qla(binned_qla_data, outputfile=None):
    '''
    Create a plot of the binned qla results

    returns the two axes used: ax_rate is the upper axes for the rates
    and ax_sig is the lower axes for the significance
    '''
    fig = plt.figure()

    ax_sig = plt.subplot2grid((8, 1), (6, 0), rowspan=2)
    ax_rate = plt.subplot2grid((8, 1), (1, 0), rowspan=5, sharex=ax_sig)

    colors = [e['color'] for e in plt.rcParams['axes.prop_cycle']]

    labels = []
    plots = []
    for (name, group), color in zip(binned_qla_data.groupby('source_name'), colors):
        if len(group.index) == 0:
            continue

        labels.append(name)
        plots.append(ax_rate.errorbar(
            x=group.time_mean.values,
            y=group.excess_rate_per_h.values,
            xerr=group.xerr.values,
            yerr=group.excess_rate_err.values,
            label=name,
            linestyle='',
            mec='none',
            color=color,
        ))

        ax_sig.errorbar(
            x=group.time_mean.values,
            y=group.significance.values,
            xerr=group.xerr.values,
            label=name,
            linestyle='',
            mec='none',
            color=color,
        )

    fig.legend(
        plots,
        labels,
        loc='upper center',
        ncol=3,
        columnspacing=0.5,
        numpoints=1,
        handletextpad=0.1,
        bbox_to_anchor=[0.5, 0.99],
    )
    ax_rate.set_ylabel('Excess Event Rate / $\mathrm{h}^{-1}$')

    ax_sig.axhline(3, color='darkgray')
    ax_sig.set_ylabel('$S_{\mathrm{Li/Ma}} \,\, / \,\, \sigma$')

    ymax = max(3.25, np.ceil(ax_sig.get_ylim()[1]))
    ax_sig.set_ylim(0, ymax)
    ax_sig.set_yticks(np.arange(0, ymax + 0.1, ymax // 4 + 1))

    plt.setp(ax_rate.get_xticklabels(), visible=False)

    plt.setp(ax_sig.get_xticklabels(), rotation=30, va='top', ha='right')

    if binned_qla_data.night.nunique() <= 7:
        ax_sig.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
    else:
        ax_sig.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))

    fig.tight_layout()

    if outputfile is not None:
        fig.savefig(outputfile)

    return ax_rate, ax_sig
