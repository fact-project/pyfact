'''
This module contains functions to plot fact data into the camera view.

The Viewer class starts a GUI with tkinter, that let's you click through
events. You will only have access to the Viewer if you have installed
matplotlib with tcl/tk support

Currently these functions only work with shape (num_events, 1440), so
on a pixel bases
'''
from .core import mark_pixel, camera, pixelids
from .analysis import plot_excess_rate

__all__ = [
    'camera',
    'mark_pixel',
    'pixelids',
    'plot_excess_rate',
]
