import numpy as np
import pkg_resources as res
import matplotlib.pyplot as plt

__all__ = ['get_pixel_coords', 'calc_linewidth', 'calc_text_size']


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

    x_stretch = (x2 - x1)/400
    y_stretch = (y2 - y1)/400

    linewidth = min(width/x_stretch, height/y_stretch)/10
    return linewidth


def calc_text_size(ax=None):
    if ax is None:
        ax = plt.gca()
    linewidth = calc_linewidth(ax)

    textsize = linewidth*5

    return textsize


def get_pixel_coords(mapfile=None,
                     rotate=True,
                     columns=[0, 9, 10, 11],
                     skip_header=1,
                     skip_footer=None,
                     delimiter=",",
                     unpack=True,
                     ):
    """
    Calculate the pixel coordinates from the standard pixel-map file
    by default it gets rotated by 90 degrees clockwise to show the same
    orientation as MARS and fact-tools

    Arguments
    ---------
    mapfile : str
        path/to/pixelmap.csv, if None than the package resource is used
        [defailt: None]
    rotate : bool
        if True the view is rotated by 90 degrees counter-clockwise
        [default: True]
    colums : list-like
        the columns in the file for softID, chid, x, y
        default: [0, 9, 10, 11]
    """

    if mapfile is None:
        mapfile = res.resource_filename("fact", "resources/pixel-map.csv")

    softID, chid, pixel_x_soft, pixel_y_soft = np.genfromtxt(
        mapfile,
        skip_header=skip_header,
        skip_footer=skip_footer,
        delimiter=delimiter,
        usecols=columns,
        unpack=unpack,
    )

    pixel_x_chid = np.zeros(1440)
    pixel_y_chid = np.zeros(1440)

    pixel_x_soft *= 9.5
    pixel_y_soft *= 9.5

    for i in range(1440):
        pixel_x_chid[chid[i]] = pixel_x_soft[i]
        pixel_y_chid[chid[i]] = pixel_y_soft[i]

    # rotate by 90 degrees to show correct orientation
    if rotate is True:
        pixel_x = - pixel_y_chid
        pixel_y = pixel_x_chid
    else:
        pixel_x = pixel_x_chid
        pixel_y = pixel_y_chid

    return pixel_x, pixel_y
