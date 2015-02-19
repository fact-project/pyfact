#!/usr/bin/env python3
"""
This file plots the classic EventView for every Event in a data file.
It can be imported into zour own Python scripts or called from the command
line with the options below

Usage:
    FactEventPlotter <inputfile> [options]

Options:
    --group=<group>       group from which to read, default: first found group
    --dataset=<key>       hdf5 dataset from which to read. [default: photoncharge]
    --pixelset=<key>      Special pixelset which is plotted with different border color
    --cmap=<cmap>         The matplotlib cmap to be used [default: gray]
    --pixelmap=<file>     File that contains the pixelmap [default: pixel-map.csv]
    --linecolor=<colors>  color for the pixelset [default: g]
    --vmin=<vmin>         minimal value for the colormap
    --vmax=<vmax>         maximal value for the colormap
"""

import h5py
import os
import os.path
from docopt import docopt
import matplotlib
matplotlib.use('TkAgg')
matplotlib.rcParams["text.usetex"] = False
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import numpy as np

try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    import Tkinter as tk
    import tkFileDialog as filedialog

class Viewer():
    def __init__(self,
                 dataset,
                 key,
                 pixelset=None,
                 pixelsetcolour="g",
                 mapfile="pixel-map.csv",
                 cmap="gray",
                 vmin=None,
                 vmax=None,
                 ):
        self.event = 0
        self.resizing = False
        self.dataset = dataset
        self.numEvents = len(dataset)
        self.pixelset = pixelset
        self.pixelsetcolour = pixelsetcolour
        self.key = key
        self.cmap = cmap
        self.vmin = vmin
        self.vmax = vmax
        self.pixel_x, self.pixel_y = self.get_pixel_coords(mapfile)
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
        self.root.after(100, self.redraw)
        tk.mainloop()

    def init_plot(self):
        self.width, self.height = self.fig.get_figwidth(), self.fig.get_figheight()
        self.fig.clf()
        self.ax = self.fig.add_axes((0.01, 0.01, 0.98, 0.98), aspect=1)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_xlim(-200, 200)
        self.ax.set_ylim(-200, 200)

        self.calc_marker_size()

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
                                    marker='H',
                                    s=self.size,
                                    cmap=self.cmap)
        if self.pixelset is not None:
            self.pixelsetplot = self.ax.scatter(self.pixel_x[self.pixelset[self.event]],
                                                self.pixel_y[self.pixelset[self.event]],
                                                c=self.dataset[self.event][self.pixelset[self.event]],
                                                lw=self.linewidth,
                                                edgecolor=self.pixelsetcolour,
                                                marker='H',
                                                vmin=vmin,
                                                vmax=vmax,
                                                s=self.size,
                                                cmap=self.cmap)
        self.cb = self.fig.colorbar(self.plot, ax=self.ax, label=self.key, shrink=0.95)
        self.cb.set_clim(vmin=vmin, vmax=vmax)
        # self.cb.set_ticks(np.arange(0, int(max(self.dataset[self.event])+1)))
        self.cb.draw_all()
        # self.fig.tight_layout()

    def save(self):
        filename = filedialog.asksaveasfilename(
            initialdir=os.getcwd(),
            parent=self.root,
            title="Choose a filename for the saved image",
            defaultextension=".pdf",
        )
        print(filename)
        if filename is not None:
            fig = self.fig
            # fig.tight_layout()
            fig.savefig(filename, dpi=300, bbox_inches="tight", transparent=True)

    def calc_marker_size(self):
        bbox = self.ax.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
        width, height = bbox.width, bbox.height
        self.size = (min(width/1.2, height)/5)**2 * 120
        self.linewidth = min(width/1.2, height)/5 * 1.2

    def redraw(self):
        if self.width != self.fig.get_figwidth() and self.height != self.fig.get_figheight():
            self.resizing = True
            self.calc_marker_size()
            self.plot._sizes = np.ones(self.dataset.shape[1])*self.size
            self.plot.set_linewidth(self.linewidth)
            if self.pixelset is not None:
                self.pixelsetplot._sizes = np.ones(self.dataset.shape[1])*self.size
                self.pixelsetplot.set_linewidth(self.linewidth)
            self.canvas.draw()
            self.resizing = False
        self.root.after(100, self.redraw)

    def get_pixel_coords(self, mapfile):
        softID, chid, pixel_x_soft, pixel_y_soft = np.loadtxt(mapfile,
                                                              skiprows=1,
                                                              delimiter=",",
                                                              usecols=(0,9,10,11),
                                                              unpack=True)
        pixel_x_chid = np.zeros(1440)
        pixel_y_chid = np.zeros(1440)

        pixel_x_soft*=9.5
        pixel_y_soft*=9.5

        for i in range(1440):
            pixel_x_chid[chid[i]] = pixel_x_soft[i]
            pixel_y_chid[chid[i]] = pixel_y_soft[i]
        return pixel_x_chid, pixel_y_chid

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

if __name__ == "__main__":
    args = docopt(__doc__)
    print(args)

    if args["--vmin"] is not None:
        args["--vmin"] = float(args["--vmin"])
    if args["--vmax"] is not None:
        args["--vmax"] = float(args["--vmax"])

    inputfile = h5py.File(args["<inputfile>"], "r")
    if not args["--group"]:
        group = inputfile[list(inputfile.keys())[0]]
    else:
        group = inputfile[args["--group"]]

    for key in sorted(group.keys()):
        print(key)

    dataset = group.get(args["--dataset"])

    if args["--pixelset"] is not None:
        pixelset = group.get(args["--pixelset"])
    else:
        pixelset = None

    if args["--vmin"] is not None:
        args["--vmin"] = float(args["--vmin"])
    if args["--vmax"] is not None:
        args["--vmax"] = float(args["--vmax"])

    myViewer = Viewer(dataset,
                      args["--dataset"],
                      cmap=args["--cmap"],
                      vmin=args["--vmin"],
                      vmax=args["--vmax"],
                      pixelset=pixelset,
                      pixelsetcolour=args["--linecolor"],
                      mapfile=args["--pixelmap"],
                      )
