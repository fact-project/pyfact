import matplotlib.pyplot as plt

__all__ = ['calc_linewidth', 'calc_text_size']


def calc_linewidth(ax=None):
    """
    calculate the correct linewidth for the fact pixels,
    so that the patches fit nicely together

    Arguments
    ---------
    ax  : matplotlib Axes instance
        the axes you want to calculate the size for

    Returns
    -------
    linewidth : float
    """

    if ax is None:
        ax = plt.gca()

    fig = ax.get_figure()

    bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    width, height = bbox.width, bbox.height

    x1, x2 = ax.get_xlim()
    y1, y2 = ax.get_ylim()

    x_stretch = (x2 - x1) / 400
    y_stretch = (y2 - y1) / 400

    linewidth = min(width / x_stretch, height / y_stretch) / 10
    return linewidth


def calc_text_size(ax=None):
    if ax is None:
        ax = plt.gca()
    linewidth = calc_linewidth(ax)

    textsize = linewidth*5

    return textsize
