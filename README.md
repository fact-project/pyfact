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
from fact.slowdata import connect

db = connect()
db.<tab>
```

For easily correlating slowdata samples by their timestamps, try this:
```{python}

import matplotlib.pyplot as plt
from fact.slowdata import connect
from fact.slowdata.correlation import CorrelationByInterpolation

db = connect()
magic_weather_sample = db.MAGIC_WEATHER_DATA.from_until(16400, 16403)
fact_camera_temp_sample = db.FSC_CONTROL_TEMPERATURE.from_until(16401, 16403)
coincidence_time_window = 5 # in seconds
correlation_generator = CorrelationByInterpolation(magic_weather_sample, 
                                                  fact_camera_temp_sample, coincidence_time_window)

(interpolated_magic_weather_sample , 
   interpolated_fact_camera_temp_sample) = correlation_generator.correlate()

# The interpolated samples are ensured to have the same "Time" field now.
# assume, we wanted to know if the temperature measured at MAGIC is correlated to 
# the temperature in the SiPM sensor area (using sensor 4, because we can)
plt.hist2d(interpolated_magic_weather_sample["T"], 
           interpolated_fact_camera_temp_sample["T_sens"][:,4])
plt.show()
```


For a comple example for requesting data and making a plot, please see `examples/slowdata_db.py`.

## dim

Some functions and classes to work with the fact dim servers
