fact.coordinates package
========================

Print the location of Crab in the camera for a given time

.. code-block:: python

    >>> from astropy.coordinates import SkyCoord, AltAz
    >>> from fact.coordinates import CameraFrame
    >>> obstime = '2013-10-03 04:00'
    >>> crab = SkyCoord.from_name('Crab')
    >>> pointing = AltAz(alt='62d', az='97d')
    >>> camera_frame = CameraFrame(pointing_direction=p, obstime=obstime)
    >>> crab_camera = crab.transform_to(camera_frame)
    >>> print(crab_camera.x, crab_camera.y)
    -34.79480274879211 mm 11.27416763997078 mm


.. automodule:: fact.coordinates
    :members:
    :undoc-members:
    :show-inheritance:

Submodules
----------

fact.coordinates.camera_frame module
------------------------------------

.. automodule:: fact.coordinates.camera_frame
    :members:
    :undoc-members:
    :show-inheritance:

fact.coordinates.utils module
-----------------------------

.. automodule:: fact.coordinates.utils
    :members:
    :undoc-members:
    :show-inheritance:
