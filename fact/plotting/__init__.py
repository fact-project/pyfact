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
from __future__ import print_function
from matplotlib.axes import Axes
from matplotlib.patches import RegularPolygon, Polygon
from matplotlib.collections import PatchCollection, PolyCollection
import matplotlib.colors as colors
from matplotlib import docstring

import numpy as np
import pkg_resources as res
import matplotlib.pyplot as plt
import warnings

from .utils import get_pixel_coords, calc_text_size, calc_marker_size

try:
    from .viewer import Viewer
    __all__ = ['Viewer', 'get_pixel_coords', 'calc_marker_size', 'calc_text_size']
except:
    warnings.warn("Matplotlib was build without tkagg support"
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
               linewidth=0.5,
               picker=5
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

    if pixelcoords is None:
        pixel_x, pixel_y = get_pixel_coords()
    else:
        pixel_x, pixel_y = pixelcoords

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

    edgecolors = np.array(1440*["k"])
    edgecolors[pixelset] = pixelsetcolour

    patches = []
    for x, y, ec in zip(pixel_x, pixel_y, edgecolors):
        patches.append(
            RegularPolygon(
                xy=(x, y),
                numVertices=6,
                radius=5,
                orientation=0.,   # in radians
                picker=picker,
            )
        )

    collection = PatchCollection(patches)
    collection.set_linewidth(linewidth)
    collection.set_edgecolors(edgecolors)
    collection.set_cmap(cmap)
    collection.set_array(data)
    collection.set_clim(vmin, vmax)
    collection.set_picker(picker)

    self.add_collection(collection)
    return collection

def factbias(self,
               data,
               pixelcoords=None,
               cmap='gray',
               vmin=None,
               vmax=None,
               pixelset=None,
               pixelsetcolour='g',
               linewidth=0.5,
               picker=5
               ):
    """
    Attributes
    ----------

    data     : array like with shape 320
            the data you want to plot into the bias patches
    pixelset : boolean array with shape 320
        the bias patches where pixelset is True are marked with 'pixelsetcolour'
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

    if pixelcoords is None:
        pixel_x, pixel_y = get_pixel_coords()
    else:
        pixel_x, pixel_y = pixelcoords

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

    edgecolors = np.array(1440*["k"])
    edgecolors[pixelset] = pixelsetcolour

    pocs = make_trigger_patches(pixel_x, pixel_y)
    collection = PatchCollection(pocs)
    self.add_collection(collection)
    return collection


def make_trigger_patches(pixel_x, pixel_y):
    pocs = []
    for trg_patch_id in range(160):
        points = np.zeros((9 * 6, 2))
        for i in range(9):
            x = pixel_x[trg_patch_id * 9 + i]
            y = pixel_y[trg_patch_id * 9 + i]
            
            hex = RegularPolygon(
                xy=(x, y),
                numVertices=6,
                radius=5.2,
                orientation=0)
            # each hexagon-patch contains 7 vertices, but start and end are thesame
            points[i * 6 : (i+1) * 6, :] = hex.get_verts()[:6, :]

        # leftmost = points[ points[:,0].arg.min() ]

        # get rid of all points in the points array, which are threefold contained
        how_often = np.zeros((9 * 6), dtype=np.int)
        already_seen = np.zeros((9 * 6), dtype=np.bool)
        outer_points = []
        for j in range(9 * 6):
            if already_seen[j]:
                continue

            distance_to_j = np.linalg.norm(points - points[j], axis=1)
            how_often[j] = (distance_to_j < 1).sum()
            already_seen[distance_to_j < 1] = True

            if how_often[j] == 1:
                outer_points.append(points[j])
            elif how_often[j] == 2:
                new_point = points[distance_to_j<1,:].mean(axis=0)
                outer_points.append(new_point)

        #if trg_patch_id == 0:
        #    plt.figure()
        #    k = trg_patch_id
        #    plt.scatter(points[:,0], points[:,1], c=how_often)
        

        # now the outer points might be in any order, but for 
        # creating a polygon we need to bring them into a useful order 
        # for plotting. 
        # I try this method:
        #   choose any point, choose the next nearest point, choose the next nearest point 
        #   and so on. (The distance to any nearest point should not be larger than (radius + 1%). )
        
        sorted_outer_points = sort_points(outer_points.pop(), outer_points)

        pocs.append(Polygon(np.array(sorted_outer_points)))
    return pocs


def sort_points(this_point, non_sorted, _sorted=None):
    if _sorted is None:
        _sorted=[this_point]

    np_non_sorted = np.array(non_sorted)
    two_nearest_points = np.linalg.norm(np_non_sorted-this_point, axis=1).argsort()[:2]

    
    nearest_point = non_sorted.pop(min_index)    
    _sorted.append(nearest_point)
    
    if non_sorted:
        _sorted = sort_points(nearest_point, non_sorted, _sorted)
    
    return _sorted  


def make_trigger_patches2(pixel_x, pixel_y):
    pocs = []
    for trg_patch_id in range(160):
        

        hexes = []
        for i in range(9):
            x = pixel_x[trg_patch_id * 9 + i]
            y = pixel_y[trg_patch_id * 9 + i]
            
            hex = RegularPolygon(
                xy=(x, y),
                numVertices=6,
                radius=5.2,
                orientation=0)
            hexes.append(hex)

        


            # each hexagon-patch contains 7 vertices, but start and end are thesame
            points[i * 6 : (i+1) * 6, :] = hex.get_verts()[:6, :]

        # leftmost = points[ points[:,0].arg.min() ]

        # get rid of all points in the points array, which are threefold contained
        how_often = np.zeros((9 * 6), dtype=np.int)
        already_seen = np.zeros((9 * 6), dtype=np.bool)
        outer_points = []
        for j in range(9 * 6):
            if already_seen[j]:
                continue

            distance_to_j = np.linalg.norm(points - points[j], axis=1)
            how_often[j] = (distance_to_j < 1).sum()
            already_seen[distance_to_j < 1] = True

            if how_often[j] == 1:
                outer_points.append(points[j])
            elif how_often[j] == 2:
                new_point = points[distance_to_j<1,:].mean(axis=0)
                outer_points.append(new_point)

        #if trg_patch_id == 0:
        #    plt.figure()
        #    k = trg_patch_id
        #    plt.scatter(points[:,0], points[:,1], c=how_often)
        

        # now the outer points might be in any order, but for 
        # creating a polygon we need to bring them into a useful order 
        # for plotting. 
        # I try this method:
        #   choose any point, choose the next nearest point, choose the next nearest point 
        #   and so on. (The distance to any nearest point should not be larger than (radius + 1%). )
        
        sorted_outer_points = sort_points(outer_points.pop(), outer_points)

        pocs.append(Polygon(np.array(sorted_outer_points)))
    return pocs





@docstring.copy_dedent(factcamera)
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

@docstring.copy_dedent(ax_pixelids)
def plt_pixelids(*args, **kwargs):
    ax = plt.gca()
    ax.factpixelids(*args, **kwargs)
    ret = plt.draw_if_interactive()
    return ret

# add functions to matplotlib
Axes.factcamera = factcamera
Axes.factcamera = factcamera
plt.factcamera = pltfactcamera
Axes.factpixelids = ax_pixelids
plt.factpixelids = plt_pixelids
