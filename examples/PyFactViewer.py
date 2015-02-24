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
import numpy as np
from fact.plotting import Viewer

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
