"""
This module contains functions to plot fact data into the camera view.
Most of the functions get added to matplotlib, so you can just use e.g.

import matplotlib.pyplot as plt
import fact.plotting as fplot
plt.factcamera(data)
plt.show()

The Viewer class starts a GUI with tkinter, that let's you click through
events

Currently these functions only work with shape (num_events, 1440), so
on a pixel bases
"""

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import os
import numpy as np
import pkg_resources as res
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

# tkinter is named differently in python2 and python3
try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    import Tkinter as tk
    import tkFileDialog as filedialog

# for python2 use imp.reload, for python3 use importlib
try:
    from importlib import reload
except ImportError:
    from imp import reload

__all__ = ['Viewer', 'get_pixel_coords', 'calc_marker_size']

def factcamera(self,
               data,
               pixelcoords=None,
               cmap='gray',
               vmin=None,
               vmax=None,
               pixelset=None,
               pixelsetcolour='g',
               ):
    self.set_aspect('equal')
    self.set_xlim(-200, 200)
    self.set_ylim(-200, 200)
    size, linewidth = calc_marker_size(self)

    if pixelcoords is None:
        pixel_x, pixel_y = get_pixel_coords()

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

Axes.factcamera = factcamera

def pltfactcamera(*args, **kwargs):
    ax = plt.gca()
    ret = ax.factcamera(*args, **kwargs)
    plt.draw_if_interactive()
    return ret

plt.factcamera = pltfactcamera

def calc_marker_size(ax):
    """
    calculate the correct marker size and linewidth for the fact pixels,
    so that plt.scatter(x, y, s=size, marker='H', linewidth=linewidth)
    produces a nice view of the fact camera

    Arguments
    ---------
    ax  : matplotlib Axes instance
        the axes you want to calculate the size for

    Returns
    -------
    size : float
    linewidth : float
    """

    fig = ax.get_figure()

    bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    width, height = bbox.width, bbox.height

    x1, x2 = ax.get_xlim()
    y1, y2 = ax.get_ylim()

    x_stretch = (x2 - x1)/400
    y_stretch = (y2 - y1)/400

    size = (min(width/(x_stretch), height/y_stretch)/5)**2 * 9.45**2
    linewidth = min(width/x_stretch, height/y_stretch)/5 * 0.5
    return size, linewidth

def get_pixel_coords(mapfile=None,
                     rotate=True,
                     columns=[0,9,10,11],
                     skiprows=1,
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
        skiprows=skiprows,
        delimiter=delimiter,
        usecols=columns,
        unpack=unpack,
    )

    pixel_x_chid = np.zeros(1440)
    pixel_y_chid = np.zeros(1440)

    pixel_x_soft*=9.5
    pixel_y_soft*=9.5

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



class Viewer():
    """
    A tkinter based GUI to look at fact events in the camera view.

    Attributes
    ----------

    dataset  : array like with shape (num_events, 1440)
        the data you want to plot into the pixels
    label    : str
        the label for the colormap
    pixelset : boolean array with shape (num_events, 1440)
        the pixels where pixelset is True are marked with 'pixelsetcolour'
        [default: None]
    pixelsetcolour : a matplotlib conform colour representation
        the colour for the pixels in 'pixelset',
        [default: green]
    mapfile : str
        path/to/fact/pixelmap.csv
        [default pixel-map.csv]
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
    def __init__(self,
                 dataset,
                 label,
                 pixelset=None,
                 pixelsetcolour="g",
                 mapfile="pixel-map.csv",
                 cmap="gray",
                 vmin=None,
                 vmax=None,
                 ):
        matplotlib.use('TkAgg', warn=False, force=True)
        matplotlib.rcdefaults()
        self.event = 0
        self.dataset = dataset
        self.numEvents = len(dataset)
        self.pixelset = pixelset
        self.pixelsetcolour = pixelsetcolour
        self.label = label
        self.cmap = cmap
        self.vmin = vmin
        self.vmax = vmax
        self.pixel_x, self.pixel_y = get_pixel_coords()
        self.fig = Figure(figsize=(7,6), dpi=100)

        self.init_plot()

        #### GUI Stuff ####

        self.root = tk.Tk()
        self.root.geometry(("1024x768"))
        self.root.wm_title("PyFactViewer")


        buttonFrame = tk.Frame(self.root)
        plotFrame = tk.Frame(self.root)

        buttonFrame.pack(side=tk.TOP)
        plotFrame.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH)

        self.canvas = FigureCanvasTkAgg(self.fig, master=plotFrame)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.canvas._tkcanvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)
        self.root.bind('<Key>', self.on_key_event)

        self.quit_button = tk.Button(master=buttonFrame, text='Quit', command=self.quit, expand=None)
        self.next_button = tk.Button(master=buttonFrame, text='Next', command=self.next, expand=None)
        self.previous_button = tk.Button(master=buttonFrame, text='Previous', command=self.previous, expand=None)
        self.save_button = tk.Button(master=buttonFrame, text='Save Image', command=self.save, expand=None)

        self.eventstring = tk.StringVar()
        self.eventstring.set("EventNum: {:05d}".format(self.event))
        self.eventbox = tk.Label(master=buttonFrame, textvariable=self.eventstring)
        self.eventbox.pack(side=tk.LEFT)
        self.previous_button.pack(side=tk.LEFT)
        self.next_button.pack(side=tk.LEFT)
        self.quit_button.pack(side=tk.RIGHT)
        self.save_button.pack(side=tk.RIGHT)
        self.resizing = False
        self.root.bind("<Configure>", self.trigger_resize)
        tk.mainloop()

    def trigger_resize(self, event):
        if not self.resizing:
            self.resizing = True
            self.root.after(100, self.redraw)

    def init_plot(self):
        self.width, self.height = self.fig.get_figwidth(), self.fig.get_figheight()
        self.fig.clf()
        self.ax = self.fig.add_subplot(1,1,1, aspect=1)
        divider = make_axes_locatable(self.ax)
        self.cax = divider.append_axes("right", size="5%", pad=0.1)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_xlim(-200, 200)
        self.ax.set_ylim(-200, 200)

        self.size, self.linewidth = calc_marker_size(self.ax)

        if self.vmin is None:
            vmin=np.min(self.dataset[self.event])
        else:
            vmin = self.vmin
        if self.vmax is None:
            vmax=np.max(self.dataset[self.event])
        else:
            vmax = self.vmax

        self.plot = self.ax.scatter(self.pixel_x,
                                    self.pixel_y,
                                    c=self.dataset[self.event],
                                    vmin=vmin,
                                    vmax=vmax,
                                    lw=self.linewidth,
                                    marker='h',
                                    s=self.size,
                                    cmap=self.cmap)
        if self.pixelset is not None:
            self.pixelsetplot = self.ax.scatter(self.pixel_x[self.pixelset[self.event]],
                                                self.pixel_y[self.pixelset[self.event]],
                                                c=self.dataset[self.event][self.pixelset[self.event]],
                                                lw=self.linewidth,
                                                edgecolor=self.pixelsetcolour,
                                                marker='h',
                                                vmin=vmin,
                                                vmax=vmax,
                                                s=self.size,
                                                cmap=self.cmap)
        self.cb = self.fig.colorbar(self.plot, cax=self.cax, label=self.label)
        self.cb.set_clim(vmin=vmin, vmax=vmax)
        self.cb.draw_all()

    def save(self):
        filename = filedialog.asksaveasfilename(
            initialdir=os.getcwd(),
            parent=self.root,
            title="Choose a filename for the saved image",
            defaultextension=".pdf",
        )
        if filename:
            fig = self.fig
            fig.savefig(filename, dpi=300, bbox_inches="tight", transparent=True)
            print("Image sucessfully saved to", filename)

    def redraw(self):
        if self.width != self.fig.get_figwidth() or self.height != self.fig.get_figheight():
            self.size, self.linewidth = calc_marker_size(self.ax)
            self.plot._sizes = np.ones(self.dataset.shape[1])*self.size
            self.plot.set_linewidth(self.linewidth)
            if self.pixelset is not None:
                self.pixelsetplot._sizes = np.ones(self.dataset.shape[1]) * self.size
                self.pixelsetplot.set_linewidth(self.linewidth)
            self.canvas.draw()
            try:
                self.fig.tight_layout()
            except ValueError:
                pass
        self.resizing = False


    def quit(self):
        self.root.quit()     # stops mainloop
        self.root.destroy()  # this is necessary on Windows to prevent

    def next(self):
        self.event = (self.event + 1)%len(self.dataset)
        self.update()

    def previous(self):
        if self.event == 0:
            self.event = self.numEvents - 1
        else:
            self.event -= 1
        self.update()

    def on_key_event(self, event):
        if event.keysym == "Right":
            self.next()
        elif event.keysym == "Left":
            self.previous()
        elif event.keysym == "q":
            self.quit()

    def update(self):
        self.plot.set_array(self.dataset[self.event])
        self.plot.changed()
        if self.pixelset is not None:
            mask = self.pixelset[self.event]
            self.pixelsetplot.set_array(self.dataset[self.event][mask])
            self.pixelsetplot.set_offsets(np.transpose([self.pixel_x[mask], self.pixel_y[mask]]))
            self.pixelsetplot.changed()
        if self.vmin is None:
            vmin = np.min(self.dataset[self.event])
        else:
            vmin=self.vmin
        if self.vmax is None:
            vmax = np.max(self.dataset[self.event])
        else:
            vmax=self.vmax
        self.cb.set_clim(vmin=vmin, vmax=vmax)
        self.cb.draw_all()
        self.canvas.draw()
        self.eventstring.set("EventNum: {:05d}".format(self.event))
