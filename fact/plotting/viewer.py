import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.figure import Figure
import numpy as np
import os
from .utils import calc_linewidth
from ..instrument import get_pixel_coords
from . import camera

import tkinter as tk
from tkinter import filedialog


class Viewer():
    """
    A tkinter based GUI to look at fact events in the camera view.

    Attributes
    ----------

    dataset  : array like with shape (num_events, 1440)
        the data you want to plot into the pixels
    label    : str
        the label for the colormap
    clickedcolour: a matplotlib conform colour represantation
        the coulour for clicked pixel
        [default: red]
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
                 clickedcolour="r",
                 mapfile="pixel-map.csv",
                 cmap="gray",
                 vmin=None,
                 vmax=None,
                 ):
        matplotlib.use('TkAgg', warn=False, force=True)
        matplotlib.rcdefaults()
        self.event = 0
        if dataset.shape == (1440, ):
            self.dataset = np.reshape(dataset, (1, 1440))
        elif dataset.shape[1] == 1440:
            self.dataset = dataset
        else:
            raise ValueError('Viewer expects dataset with shape (1440, )\n'
                             'or (n_events, 1440)'
                             )
        self.numEvents = dataset.shape[0]
        self.clickedcolour = clickedcolour
        self.label = label
        self.cmap = cmap
        self.vmin = vmin
        self.vmax = vmax
        self.pixel_x, self.pixel_y = get_pixel_coords()
        self.fig = Figure(figsize=(7, 6), dpi=100)

        self.init_plot()

        # ---- GUI Stuff ----

        self.root = tk.Tk()
        self.root.geometry(("1024x768"))
        self.root.wm_title("PyFactViewer")

        buttonFrame = tk.Frame(self.root)
        plotFrame = tk.Frame(self.root)
        infoFrame = tk.Frame(plotFrame)

        buttonFrame.pack(side=tk.TOP)
        plotFrame.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH)
        infoFrame.pack(side=tk.BOTTOM)

        self.canvas = FigureCanvasTkAgg(self.fig, master=plotFrame)
        self.canvas.mpl_connect("pick_event", self.onpick)
        self.canvas.mpl_connect("resize_event", self.redraw)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.canvas._tkcanvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)
        self.root.bind('<Key>', self.on_key_event)

        self.quit_button = tk.Button(master=buttonFrame,
                                     text='Quit',
                                     command=self.quit,
                                     expand=None,
                                     )
        self.next_button = tk.Button(master=buttonFrame,
                                     text='Next',
                                     command=self.next,
                                     expand=None,
                                     )
        self.previous_button = tk.Button(master=buttonFrame,
                                         text='Previous',
                                         command=self.previous,
                                         expand=None,
                                         )
        self.save_button = tk.Button(master=buttonFrame,
                                     text='Save Image',
                                     command=self.save,
                                     expand=None,
                                     )

        self.eventstring = tk.StringVar()
        self.eventstring.set("EventNum: {:05d}".format(self.event))
        self.eventbox = tk.Label(master=buttonFrame,
                                 textvariable=self.eventstring,
                                 )

        self.eventbox.pack(side=tk.LEFT)
        self.previous_button.pack(side=tk.LEFT)
        self.next_button.pack(side=tk.LEFT)
        self.quit_button.pack(side=tk.RIGHT)
        self.save_button.pack(side=tk.RIGHT)

        self.infotext = tk.StringVar()
        self.infotext.set("Click on a Pixel")
        self.infobox = tk.Label(master=infoFrame, textvariable=self.infotext)
        self.infobox.pack(side=tk.LEFT)

        self.update()
        tk.mainloop()

    def init_plot(self):
        self.width, self.height = self.fig.get_figwidth(), self.fig.get_figheight()
        self.fig.clf()
        self.ax = self.fig.add_subplot(1, 1, 1, aspect=1)
        divider = make_axes_locatable(self.ax)
        self.cax = divider.append_axes("right", size="5%", pad=0.1)
        self.ax.set_axis_off()

        if self.vmin is None:
            vmin = np.min(self.dataset[self.event])
        else:
            vmin = self.vmin
        if self.vmax is None:
            vmax = np.max(self.dataset[self.event])
        else:
            vmax = self.vmax

        self.plot = camera(
            ax=self.ax,
            data=self.dataset[self.event],
            pixelcoords=None,
            cmap=self.cmap,
            vmin=vmin,
            vmax=vmax,
            linewidth=None,
            picker=False,
        )
        self.plot.set_picker(0)
        self.clicked_pixel = None

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

    def redraw(self, event):
        self.linewidth = calc_linewidth(self.ax)
        self.fig.tight_layout(pad=0)
        self.canvas.draw()

    def quit(self):
        self.root.quit()     # stops mainloop
        self.root.destroy()  # this is necessary on Windows to prevent

    def next(self):
        self.event = (self.event + 1) % len(self.dataset)
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
        if self.vmin is None:
            vmin = np.min(self.dataset[self.event])
        else:
            vmin = self.vmin
        if self.vmax is None:
            vmax = np.max(self.dataset[self.event])
        else:
            vmax = self.vmax
        self.linewidth = calc_linewidth(self.ax)
        self.plot.set_linewidths(self.linewidth)
        self.cb.set_clim(vmin=vmin, vmax=vmax)
        self.cb.draw_all()
        self.plot.set_picker(0)
        self.canvas.draw()
        self.eventstring.set("EventNum: {:05d}".format(self.event))

    def onpick(self, event):
        hitpixel = event.ind[0]
        if hitpixel != self.clicked_pixel:
            self.clicked_pixel = hitpixel
            self.update()
            self.infotext.set(
                "chid: {:04d}, {} = {:4.2f}".format(
                    hitpixel,
                    self.label,
                    self.plot.get_array()[hitpixel]
                )
            )
