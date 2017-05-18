import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.transforms as mtransforms
from mpl_toolkits.axes_grid1.parasite_axes import SubplotHost
import numpy as np
from ..time import MJD_EPOCH


# Matplotlib uses ordinal for internal date represantion
# to get from ordinal to mjd, we shift by the ordinal value
# of the MJD_EPOCH
MJD_AXES_TRANSFORM = (
    mtransforms.Affine2D().translate(MJD_EPOCH.toordinal(), 0)
)


def create_datetime_mjd_axes(fig=None, *args, **kwargs):
    '''
    Create a plot with two x-axis, bottom axis using
    dates, top axis using mjd.

    Parameters
    ----------
    fig: matplotlib.Figure or None
        the figure to use, if None use plt.gcf()

    Returns
    -------
    ax: mpl_toolkits.axes_grid1.parasite_axes.SubplotHost
        The ax for the dates
    mjd_ax: mpl_toolkits.axes_grid1.parasite_axes.ParasiteAxis
        The axis with the mjd axis

    '''
    if fig is None:
        fig = plt.gcf()

    if args == []:
        ax = SubplotHost(fig, 1, 1, 1, **kwargs)
    else:
        ax = SubplotHost(fig, *args, **kwargs)

    # The second axis shows MJD if the first axis uses dates
    mjd_ax = ax.twin(MJD_AXES_TRANSFORM)
    mjd_ax.set_viewlim_mode('transform')

    # disable unwanted axes
    mjd_ax.axis['right'].toggle(ticklabels=False, ticks=False)
    mjd_ax.axis['bottom'].toggle(ticklabels=False, ticks=False)
    mjd_ax.axis['bottom'].toggle(label=False)

    # add/remove label
    mjd_ax.axis['top'].set_label('MJD')

    # Deactivate offset
    mjd_ax.ticklabel_format(useOffset=False)

    fig.add_subplot(ax)

    return ax, mjd_ax


def plot_excess_rate(binned_runs, outputfile=None, mjd=True):
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

    gridspec = plt.GridSpec(8, 1)
    spec_sig = gridspec.new_subplotspec((6, 0), rowspan=2)
    spec_rate = gridspec.new_subplotspec((1, 0), rowspan=5)

    ax_sig = plt.subplot(spec_sig)

    if mjd is True:
        ax_rate, ax_rate_mjd = create_datetime_mjd_axes(
            fig, spec_rate, sharex=ax_sig
        )
    else:
        ax_rate = plt.subplot(spec_rate, sharex=ax_sig)

    colors = [e['color'] for e in plt.rcParams['axes.prop_cycle']]

    labels = []
    plots = []

    groups = list(sorted(
        binned_runs.groupby('source'),
        key=lambda g: g[1].time_mean.min()
    ))

    for (name, group), color in zip(groups, colors):
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
    plt.setp(ax_rate_mjd.get_xticklabels(), visible=False)
    plt.setp(ax_sig.get_xticklabels(), rotation=30, va='top', ha='right')

    ax_rate_mjd.set_xlabel('')

    if binned_runs.night.nunique() <= 7:
        ax_sig.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
    else:
        ax_sig.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))

    fig.tight_layout()

    if mjd is True:
        plt.setp(ax_rate_mjd.get_xticklabels(), visible=True)

    if outputfile is not None:
        fig.savefig(outputfile)

    if mjd is True:
        return ax_rate, ax_sig, ax_rate_mjd
    else:
        return ax_rate, ax_sig
