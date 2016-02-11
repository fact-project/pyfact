"""
This module contains functions to plot fact data into the camera view.
Most of the functions get added to matplotlib, so you can just use e.g.

import matplotlib.pyplot as plt
import fact.plotting as fplot
plt.factcamera(data)
plt.show()

The Viewer class starts a GUI with tkinter, that let's you click through
events. You will only have access to the Viewer if you have installed
matplotlib with tcl/tk support

Currently these functions only work with shape (num_events, 1440), so
on a pixel bases
"""
from matplotlib.axes import Axes
from matplotlib.patches import RegularPolygon
from matplotlib.collections import PatchCollection
from matplotlib import docstring

import numpy as np
import matplotlib.pyplot as plt
import warnings

from .utils import get_pixel_coords, calc_text_size, calc_linewidth
from .mapping import bias_to_trigger_patch_map

try:
    from .viewer import Viewer
    __all__ = [
        'Viewer',
        'get_pixel_coords',
        'calc_marker_size',
        'calc_text_size',
    ]
except ImportError:
    warnings.warn("Matplotlib was build without tkagg support,\n"
                  "the Viewer will not be available")
    __all__ = ['get_pixel_coords', 'calc_marker_size', 'calc_text_size']

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

        print("chid:", hitpixel)
        print("value", plot.get_array()[hitpixel])


def factcamera(self,
               data,
               pixelcoords=None,
               cmap='gray',
               vmin=None,
               vmax=None,
               edgecolor='k',
               linewidth=None,
               picker=True,
               ):
    """
    Attributes
    ----------

    data     : array like with shape 1440
        the data you want to plot into the pixels
    pixelcoords : the coordinates for the pixels in form [x-values, y-values]
        if None, the package resource is used
        [default: None]
    cmap : str or matplotlib colormap instance
        the colormap to use for plotting the 'dataset'
        [default: gray]
    vmin : float
        the minimum for the colorbar, if None min(dataset[event]) is used
        [default: None]
    vmax : float
        the maximum for the colorbar, if None max(dataset[event]) is used
        [default: None]
    edgecolor : any matplotlib color
        the color around the pixel
    picker: bool
        if True then the the pixel are made clickable to show information
    """

    self.set_aspect('equal')

    if picker is True:
        fig = self.get_figure()
        fig.canvas.mpl_connect("pick_event", onpick)

    # if the axes limit is still (0,1) assume new axes
    if self.get_xlim() == (0, 1) and self.get_ylim() == (0, 1):
        self.set_xlim(-200, 200)
        self.set_ylim(-200, 200)

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
        linewidth = calc_linewidth()

    collection = PatchCollection(patches, picker=0)
    collection.set_linewidth(linewidth)
    collection.set_edgecolors(edgecolors)
    collection.set_cmap(cmap)
    collection.set_array(data)
    collection.set_clim(vmin, vmax)

    self.add_collection(collection)
    return collection


@docstring.copy_dedent(factcamera)
def pltfactcamera(*args, **kwargs):
    ax = plt.gca()
    fig = ax.get_figure()
    fig.canvas.mpl_connect("pick_event", onpick)
    ret = ax.factcamera(*args, **kwargs)
    plt.draw_if_interactive()
    plt.sci(ret)
    return ret


def ax_pixelids(self, size=None, pixelcoords=None, *args, **kwargs):
    """
    plot the chids into the pixels
    """
    if pixelcoords is None:
        pixel_x, pixel_y = get_pixel_coords()
    else:
        pixel_x, pixel_y = pixelcoords

    if size is None:
        size = calc_text_size(self)

    x1, x2 = self.get_xlim()
    y1, y2 = self.get_ylim()

    maskx = np.logical_and(pixel_x + 4.5 < x2, pixel_x - 4.5 > x1)
    masky = np.logical_and(pixel_y + 4.5 < y2, pixel_y - 4.5 > y1)
    mask = np.logical_and(maskx, masky)

    chids = np.arange(1440)
    for px, py, chid in zip(pixel_x[mask], pixel_y[mask], chids[mask]):
        self.text(
            px, py,
            str(chid),
            size=size,
            va="center",
            ha="center",
            **kwargs
        )


@docstring.copy_dedent(ax_pixelids)
def plt_pixelids(*args, **kwargs):
    ax = plt.gca()
    ax.factpixelids(*args, **kwargs)
    ret = plt.draw_if_interactive()
    return ret


def mark_pixel(ax, pixels, color='g', linewidth=None):
    ''' surrounds pixels given by pixels with a border '''
    pixel_x, pixel_y = get_pixel_coords()

    patches = []
    for xy in zip(pixel_x[pixels], pixel_y[pixels]):
        patches.append(
            RegularPolygon(
                xy=xy,
                numVertices=6,
                radius=9.5/np.sqrt(3),
                orientation=0.,   # in radians
                fill=False,
            )
        )

    if linewidth is None:
        linewidth = calc_linewidth()
    collection = PatchCollection(patches, picker=0)
    collection.set_linewidth(linewidth)
    collection.set_edgecolors(color)
    collection.set_facecolor('none')

    ax.add_collection(collection)
    return collection


@docstring.copy_dedent(mark_pixel)
def plt_mark_pixel(*args, **kwargs):
    ax = plt.gca()
    ax.fact_markpixel(*args, **kwargs)
    ret = plt.draw_if_interactive()
    return ret


# add functions to matplotlib
Axes.factcamera = factcamera
plt.factcamera = pltfactcamera
Axes.factpixelids = ax_pixelids
plt.factpixelids = plt_pixelids
Axes.fact_markpixel = mark_pixel
plt.fact_markpixel = plt_mark_pixel
