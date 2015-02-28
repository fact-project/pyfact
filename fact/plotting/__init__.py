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
import matplotlib.colors as colors
import matplotlib.cm as cmx

import numpy as np
import pkg_resources as res
import matplotlib.pyplot as plt
import warnings

from .utils import get_pixel_coords, calc_text_size, calc_marker_size

try:
    from .viewer import Viewer
    __all__ = ['Viewer', 'get_pixel_coords', 'calc_marker_size', 'calc_text_size']
except:
    warnings.warn("Matplotlib was build without tkagg support" \
                  ", the Viewer will not be available")
    __all__ = ['get_pixel_coords', 'calc_marker_size', 'calc_text_size']

def factcamera(self,
               data,
               pixelcoords=None,
               cmap='gray',
               vmin=None,
               vmax=None,
               pixelset=None,
               pixelsetcolour='g',
               ):
    """
    Attributes
    ----------

    data     : array like with shape 1440
        the data you want to plot into the pixels
    pixelset : boolean array with shape 1440
        the pixels where pixelset is True are marked with 'pixelsetcolour'
        [default: None]
    pixelsetcolour : a matplotlib conform colour representation
        the colour for the pixels in 'pixelset',
        [default: green]
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
    """
    self.set_aspect('equal')

    # if the axes limit is still (0,1) assume new axes
    if self.get_xlim() == (0, 1) and self.get_ylim() == (0, 1):
        self.set_xlim(-200, 200)
        self.set_ylim(-200, 200)
    size, linewidth = calc_marker_size(self)

    if pixelcoords is None:
        pixel_x, pixel_y = get_pixel_coords()
    else:
        pixel_x, pixel_y = pixelcoords

    if vmin is None:
        vmin = np.min(data)
    if vmax is None:
        vmax = np.max(data)


    ret = self.scatter(pixel_x,
                       pixel_y,
                       c=data,
                       vmin=vmin,
                       vmax=vmax,
                       lw=linewidth,
                       marker='h',
                       s=size,
                       cmap=cmap
                       )

    if pixelset is not None:
        self.scatter(pixel_x[pixelset],
                     pixel_y[pixelset],
                     c=data[pixelset],
                     lw=linewidth,
                     edgecolor=pixelsetcolour,
                     marker='h',
                     vmin=vmin,
                     vmax=vmax,
                     s=size,
                     cmap=cmap
                     )
    return ret


def other_factcamera(
                    self,
                    data,
                    pixelcoords=None,
                    cmap='gray',
                    vmin=None,
                    vmax=None,
                    pixelset=None,
                    pixelsetcolour='g',
                    ):
    """
    Attributes
    ----------

    data     : array like with shape 1440
        the data you want to plot into the pixels
    pixelset : boolean array with shape 1440
        the pixels where pixelset is True are marked with 'pixelsetcolour'
        [default: None]
    pixelsetcolour : a matplotlib conform colour representation
        the colour for the pixels in 'pixelset',
        [default: green]
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
    """

    if pixelcoords is None:
        pixel_x, pixel_y = get_pixel_coords()
    else:
        pixel_x, pixel_y = pixelcoords

    pixel_r = np.ones_like(pixel_x) * 9.5/2. 

    self.set_aspect('equal')
    self.set_xlim(-200, 200)
    self.set_ylim(-200, 200)

    if vmin is None:
        vmin = np.min(data)
    if vmax is None:
        vmax = np.max(data)

    if pixelset is None:
        pixelset = np.zeros(1440, dtype=np.bool)

    _pixelset = np.array(pixelset)
    if _pixelset.shape != (1440,):
        pixelset = np.zeros(1440, dtype=np.bool)
        pixelset[_pixelset] = True
    else:
        pixelset = np.array(_pixelset, dtype=np.bool)


    cm = plt.get_cmap(cmap) 
    cNorm = colors.Normalize(vmin=vmin, vmax=vmax)
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)

    pixel_colors = scalarMap.to_rgba(data)


    for i, stuff in enumerate(zip(pixel_x, pixel_y, pixel_r)):
        x, y, r = stuff
        c = pixel_colors[i]

        linewidth = 1.
        edgecolor = "k"
        if pixelset[i]:
            linewidth = 2.
            edgecolor = pixelsetcolour

        ## AHHh I just found that this might be quicker, when I use
        # class matplotlib.collections.RegularPolyCollection
        # But I must go home now ... so I can't test it... :-(
        self.add_artist(
            RegularPolygon(
                        xy=(x, y),
                        numVertices=6,
                        radius=r,
                        orientation=0.,   # in radians
                        facecolor=c,
                        edgecolor=edgecolor,
                        linewidth=linewidth,
                        )
            )


    # I don't know what I should return here ... ahhh!
    return self

def pltother_factcamera(*args, **kwargs):
    ax = plt.gca()
    ret = ax.other_factcamera(*args, **kwargs)
    plt.draw_if_interactive()
    # I didn't know what other_factcamera should return
    # so this call didn't work :-(
    #plt.sci(ret)
    return None



def pltfactcamera(*args, **kwargs):
    ax = plt.gca()
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

    for px, py, chid in zip(pixel_x[mask], pixel_y[mask], np.arange(1440)[mask]):
        self.text(px, py, str(chid), size=size, va="center", ha="center", **kwargs)


def plt_pixelids(*args, **kwargs):
    ax = plt.gca()
    ax.factpixelids(*args, **kwargs)
    ret = plt.draw_if_interactive()
    return ret

# add functions to matplotlib
Axes.factcamera = factcamera
plt.factcamera = pltfactcamera
Axes.factpixelids = ax_pixelids
plt.factpixelids = plt_pixelids

Axes.other_factcamera = other_factcamera
plt.other_factcamera = pltother_factcamera