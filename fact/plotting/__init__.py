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
import numpy as np
import pkg_resources as res
import matplotlib.pyplot as plt

from .utils import get_pixel_coords, calc_text_size, calc_marker_size

try:
    from .viewer import Viewer
    __all__ = ['Viewer', 'get_pixel_coords', 'calc_marker_size', 'calc_text_size']
except:
    print("Matplotlib was build without tkagg support, the Viewer will not be available")
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

    for px, py, chid in zip(pixel_x, pixel_y, range(1440)):
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
