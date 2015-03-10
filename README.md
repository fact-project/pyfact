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

## slowdata

If you like to look at some of the so called "Slow Data" of FACT, you can request the data from a MongoDB. 
In order to access this db, you currently need to tunnel the database port to your machine, e.g. like this.
```{bash}
ssh -f -L 37017:localhost:27017 fact@ihp-pc41.ethz.ch -N
```

In case you'd like to open this tunnel always, when you log into your machine, you might want to 
put something like this into your .bashrc:
```{bash}
check_tunnel (){
    ps aux | grep "ssh -f -L 37017:localhost:27017" | grep fact >/dev/null
}
if ! check_tunnel ; then
    ssh -f -L 37017:localhost:27017 fact@ihp-pc41.ethz.ch -N
fi
```

Once you've opened that tunnel, try e.g. this...
```{python}
import matplotlib.pyplot as plt
from fact.time import iso2dt, fjd, OFFSET
from fact.slowdata import db

start_time = fjd(iso2dt("01.04.2013 12:34:56.789"))
stop_time = fjd(iso2dt("03.04.2013"))
interesting_data = db.MAGIC_WEATHER_DATA.from_until(start_time, stop_time)

#interesting_data is a numpy structured array
print("dtype of interesting_data {}".format(interesting_data.dtype))

plt.figure()
plt.plot_date(interesting_data['Time'] + OFFSET, interesting_data['T'], '.', label="outside temperature")
plt.plot_date(interesting_data['Time'] + OFFSET, interesting_data['T_dew'], '.', label="dewpoint")
plt.ylabel("Temperature [deg C]")
plt.xlabel("Date")
plt.title("Some interesting_data")
plt.legend()
plt.show()
```

## dim

Some functions and classes to work with the fact dim servers
