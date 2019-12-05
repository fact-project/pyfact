pyfact |TravisBuildStatus| |PyPIStatus|
=======================================

A python package with utils to work with the FACT Imaging Cerenkov Telescope
----------------------------------------------------------------------------

install with

.. code:: 

     $ pip install pyfact

This takes automatically care of the dependencies which are installable
with pip.

However, if you want to use the GUI Event Viewer you will need to
install Tk **before** you install ``matplotlib`` as it depends on the
tkagg backend.

functions:
~~~~~~~~~~

``fact`` includes several functions to convert the times used in fact
data to more standard formats and vice versa.

e.g. :

.. code:: python

    from fact import run2dt

    # convert fact fNight format to python datetime object:
    date = run2dt("20150101")

Submodules
----------

io
~~

To store pandas dataframes in column-oriented storage into hdf5 files,
we created some helpfull wrappers around ``pandas`` and ``h5py``:

.. code:: python
    from fact.io import read_h5py, to_h5py
    import pandas as pd

    df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    to_h5py(df, 'test.hdf5', key='events')

    print(read_h5py('test.hdf5', key='events'))


plotting
~~~~~~~~

Utils for plotting data into a FACT camera view. Based on matplotlib.

.. code:: python

    import matplotlib.pyplot as plt
    from fact.plotting import camera
    from numpy.random import normal

    # create some pseudo data with shape (10, 1440):
    data = normal(30, 5, (10, 1440))

    camera(data[0])
    plt.show()


There are also functions to get the camera\_geometry from the delivered
source file:

.. code:: python

    from fact.plotting import get_pixel_coords

    pixel_x, pixel_y = get_pixel_coords()

factdb
------

This module contains ``peewee`` ``Models`` for our ``factdata`` MySQL database.
These were automatically created by ``peewee`` and provide means to query this database in python without writing raw sql queries.

For example, to get the total number of runs take by FACT you can do:

.. code:: python

    from fact.factdb import connect_database, RunInfo

    connect_database()  # this uses the credentials module if no config is given

    num_runs = RunInfo.select().count()

A few convenience functions are already implemented.
To get a ``pandas.DataFrame`` containing the observation time per source and runtype, you can do:


.. code:: python

    from fact.factdb import connect_database, get_ontime_per_source_and_runtype

    connect_database()

    num_runs = RunInfo.select().count()
    print(get_ontime_by_source_and_runtype())


To download the database and read it to Pandas dataframe without using peewee:

.. code:: python

     from fact import credentials
     import pandas as pd

     factDB = credentials.create_factdb_engine()
     runInfo = pd.read_sql_table(table_name="RunInfo", con=factDB)  




auxservices
-----------

Utilities to read in our aux fits files into pandas dataframes.

.. code:: python


    from fact.auxservices import MagicWeather
    from datetime import date

    weather = MagicWeather(auxdir='/fact/aux/')

    df = weather.read_date(date(2016, 1, 1))

.. |TravisBuildStatus| image:: https://travis-ci.org/fact-project/pyfact.svg?branch=master
   :target: https://travis-ci.org/fact-project/pyfact
   
.. |PyPIStatus| image:: https://badge.fury.io/py/pyfact.svg
   :target: https://pypi.python.org/pypi/pyfact

