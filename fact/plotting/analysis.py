import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import numpy as np


def plot_excess_rate(binned_runs, outputfile=None):
    '''
    Create an excess rate plot from given data

    Parameters
    ----------
    binned_runs: pd.DataFrame
        Binned data as returned by `fact.analysis.bin_runs`
    outputfile: path
        if not None, the plot is saved to this file

    Returns
    -------
    ax_excess: matplotlib.axes.Axes
        the matplotlib Axes for the excess rate plot
    ax_significance: matplotlib.axes.Axes
        the matplotlib Axes for the significance plot
    '''
    fig = plt.figure()

    ax_sig = plt.subplot2grid((8, 1), (6, 0), rowspan=2)
    ax_rate = plt.subplot2grid((8, 1), (1, 0), rowspan=5, sharex=ax_sig)

    colors = [e['color'] for e in plt.rcParams['axes.prop_cycle']]

    labels = []
    plots = []
    for (name, group), color in zip(binned_runs.groupby('source'), colors):
        if len(group.index) == 0:
            continue

        labels.append(name)
        plots.append(ax_rate.errorbar(
            x=group.time_mean.values,
            y=group.excess_rate_per_h.values,
            xerr=group.time_width.values / 2,
            yerr=group.excess_rate_err.values,
            label=name,
            linestyle='',
            mec='none',
            color=color,
        ))

        ax_sig.errorbar(
            x=group.time_mean.values,
            y=group.significance.values,
            xerr=group.time_width.values / 2,
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
    ax_sig.set_ylabel('$S_{\mathrm{Li/Ma}} \,\, / \,\, \sigma$')

    ymax = max(3.25, np.ceil(ax_sig.get_ylim()[1]))
    ax_sig.set_ylim(0, ymax)
    ax_sig.set_yticks(np.arange(0, ymax + 0.1, ymax // 4 + 1))

    plt.setp(ax_rate.get_xticklabels(), visible=False)
    plt.setp(ax_sig.get_xticklabels(), rotation=30, va='top', ha='right')

    if binned_runs.night.nunique() <= 7:
        ax_sig.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
    else:
        ax_sig.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))

    fig.tight_layout()

    if outputfile is not None:
        fig.savefig(outputfile)

    return ax_rate, ax_sig
