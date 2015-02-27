import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backend_bases import key_press_handler
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt
import os

from .utils import calc_marker_size, get_pixel_coords

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
