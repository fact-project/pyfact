# pyfact
[![TravisBuildStatus](https://travis-ci.org/MaxNoe/pyfact.svg?branch=master)](https://travis-ci.org/MaxNoe/pyfact)
## A python package with utils to work with the FACT Imaging Cerenkov Telescope

install with 

```{shell session}
$ pip install git+https://github.com/maxnoe/pyfact
```
This takes automatically care of the dependencies which are installable with pip.

However, if you want to use the GUI Event Viewer you will need to install Tk __before__ you install `matplotlib` as it depends on the tkagg backend.

### functions:

`fact` includes several functions to convert the times used in fact data to more 
standard formats and vice versa.

e.g. :

```{python}
from fact import run2dt

# convert fact fNight format to python datetime object:
date = run2dt("20150101")
```


## Submodules
### plotting

Utils for plotting data into a FACT camera view. Based on matplotlib.
The function `factcamera` is added to pyplot and matplotlib Axes. 
So you can do

```{python}
import matplotlib.pyplot as plt
import fact.plotting
from numpy.random import normal

# create some pseudo data with shape (10, 1440):
data = normal(30, 5, (10, 1440))

plt.factcamera(data[0])
plt.show()

```

Or you can start an interactive Viewer which lets you click
through the events and save the images:

```{python}
from fact.plotting import Viewer()
from numpy.random import poisson

# pseudo data:
data = poisson(30, (10, 1440))

# call the Viewer with data and a label for the colorbar:
Viewer(data, "label")
```
There are also functions to get the camera_geometry from the delivered source file:

```{python}
from fact.plotting import get_pixel_coords

pixel_x, pixel_y = get_pixel_coords()
```

## dim

Some functions and classes to work with the fact dim servers


## database (not yet integrated)


If you like to look at some of the so called "Slow Data" of FACT, but are fed up with opening and closing the thousands of FITS files, you can as well just request the data from a MongoDB we set up for this purpose. 

Dependencies:

Example:

    :::shell-session
    $ cd pyfact/slow_data_db
    $ ./make_tunnel.sh      (enter the FACT std password)
    $ ipython -i slow_data_db_front_end.py
    Python 2.7.3 (default, Feb 27 2014, 19:58:35) 
    Type "copyright", "credits" or "license" for more information.

    IPython 0.12.1 -- An enhanced Interactive Python.
    ?         -> Introduction and overview of IPython's features.
    %quickref -> Quick reference.
    help      -> Python's own help system.
    object?   -> Details about 'object', use 'object??' for extra details.
    ----------------------------------------------------------------------
    you should get a very quick reaction of this script, if not yout tunnel is maybe broken
    ----------------------------------------------------------------------
    type this for a test:
        a = aux.FSC_CONTROL_TEMPERATURE.from_until(16400, 16420)
    this command takes ~40 seconds when done I do it at home

    The resulting array 'a' has a couple of fields, print them like this:
        a.dtype.names

    in order to plot for example the average sensor temperature vs. Time, you can do:
        plt.plot_date(a.Time, a.T_sens.mean(axis=1), '.')

    Have Fun!


The file, `slow_data_db_frontend.py` is of course not necessary for you to access the data in the MongoDB. You can use any other Language and any other MongoDB driver you like, as well. All this "frontend" does, is provide a (hopefully simple enough) way to access the data, and return it as a numpy array, so one can quickly plot it or do some calculations on it. The natural form for the MongoDB Python driver to return the result of a query is a list of dicts, which is not particularly useful for most of us.

Caveats:

* In case the name of a field in the DB is identical to a member of a numpy array, I don't know what happens, when you try to access them like via the dot operator. Suppose the field name ist "Time" everything is fine. You can access it via `a.Time` as well as via `a["Time"]`. But what if the name is "T"? There is member of each numpy called "T" already, which provides the transposed array.
