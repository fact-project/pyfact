from matplotlib.patches import RegularPolygon
from matplotlib.collections import PatchCollection

import numpy as np
import matplotlib.pyplot as plt

from ..instrument import get_pixel_coords
from .utils import calc_linewidth, calc_text_size

lastpixel = -1


def onpick(event):
    global lastpixel
    hitpixel = event.ind[0]
    if hitpixel != lastpixel:
        lastpixel = hitpixel
        plot = event.artist

        ecols = plot.get_edgecolors()
        before = np.array(ecols[hitpixel])
        ecols[hitpixel] = [1, 0, 0, 1]
        plot.set_edgecolors(ecols)
        plt.draw()
        ecols[hitpixel] = before

        print('chid:', hitpixel)
        print('value', plot.get_array()[hitpixel])


def camera(
        data,
        ax=None,
        cmap='gray',
        vmin=None,
        vmax=None,
        pixelcoords=None,
        edgecolor='k',
        linewidth=None,
        picker=False,
        ):
    '''
    Parameters
    ----------

    data : array like with shape 1440
        the data you want to plot into the pixels
    ax : a matplotlib.axes.Axes instace or None
        The matplotlib axes in which to plot. If None, plt.gca() is used
    cmap : str or matplotlib colormap instance
        the colormap to use for plotting the 'dataset'
        [default: gray]
    vmin : float
        the minimum for the colorbar, if None min(data) is used
        [default: None]
    vmax : float
        the maximum for the colorbar, if None max(data) is used
        [default: None]
    pixelcoords : the coordinates for the pixels in form [x-values, y-values]
        if None, the package resource is used
        [default: None]
    edgecolor : any matplotlib color
        the color around the pixel
    picker: bool
        if True then the the pixel are made clickable to show information
    '''

    if ax is None:
        ax = plt.gca()

    ax.set_aspect('equal')

    if picker is True:
        fig = ax.get_figure()
        fig.canvas.mpl_connect('pick_event', onpick)

    # if the axes limit is still (0,1) assume new axes
    if ax.get_xlim() == (0, 1) and ax.get_ylim() == (0, 1):
        ax.set_xlim(-200, 200)
        ax.set_ylim(-200, 200)

    if pixelcoords is None:
        pixel_x, pixel_y = get_pixel_coords()
    else:
        pixel_x, pixel_y = pixelcoords

    if vmin is None:
        vmin = np.min(data)
    if vmax is None:
        vmax = np.max(data)

    edgecolors = np.array(1440 * [edgecolor])
    patches = []
    for x, y, ec in zip(pixel_x, pixel_y, edgecolors):
        patches.append(
            RegularPolygon(
                xy=(x, y),
                numVertices=6,
                radius=9.51/np.sqrt(3),
                orientation=0.,   # in radians
            )
        )

    if linewidth is None:
        linewidth = calc_linewidth(ax=ax)

    collection = PatchCollection(patches, picker=0)
    collection.set_linewidth(linewidth)
    collection.set_edgecolors(edgecolors)
    collection.set_cmap(cmap)
    collection.set_array(data)
    collection.set_clim(vmin, vmax)

    ax.add_collection(collection)
    plt.draw_if_interactive()
    return collection


def pixelids(ax=None, size=None, pixelcoords=None, *args, **kwargs):
    '''
    plot the chids into the pixels
    '''
    if pixelcoords is None:
        pixel_x, pixel_y = get_pixel_coords()
    else:
        pixel_x, pixel_y = pixelcoords

    if ax is None:
        ax = plt.gca()

    if size is None:
        size = calc_text_size(ax)

    x1, x2 = ax.get_xlim()
    y1, y2 = ax.get_ylim()

    maskx = np.logical_and(pixel_x + 4.5 < x2, pixel_x - 4.5 > x1)
    masky = np.logical_and(pixel_y + 4.5 < y2, pixel_y - 4.5 > y1)
    mask = np.logical_and(maskx, masky)

    chids = np.arange(1440)
    for px, py, chid in zip(pixel_x[mask], pixel_y[mask], chids[mask]):
        ax.text(
            px, py,
            str(chid),
            size=size,
            va='center',
            ha='center',
            **kwargs
        )

    plt.draw_if_interactive()


def mark_pixel(pixels, color='g', ax=None, linewidth=None):
    ''' surrounds pixels given by pixels with a border '''
    pixel_x, pixel_y = get_pixel_coords()

    if ax is None:
        ax = plt.gca()

    patches = []
    for xy in zip(pixel_x[pixels], pixel_y[pixels]):
        patches.append(
            RegularPolygon(
                xy=xy,
                numVertices=6,
                radius=9.5 / np.sqrt(3),
                orientation=0.,   # in radians
                fill=False,
            )
        )

    if linewidth is None:
        linewidth = calc_linewidth(ax=ax)

    collection = PatchCollection(patches, picker=0)
    collection.set_linewidth(linewidth)
    collection.set_edgecolors(color)
    collection.set_facecolor('none')

    ax.add_collection(collection)

    plt.draw_if_interactive()
    return collection
