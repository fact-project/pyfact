from astropy.coordinates import (
    BaseCoordinateFrame,
    AltAz,
    frame_transform_graph,
    FunctionTransform,
)

try:
    from astropy.coordinates import CoordinateAttribute, TimeAttribute, EarthLocationAttribute
except ImportError:
    # for astropy <= 2.0.0
    from astropy.coordinates import (
        CoordinateAttribute,
        TimeFrameAttribute as TimeAttribute,
        EarthLocationAttribute,
    )

from astropy.coordinates.matrix_utilities import rotation_matrix
from astropy.coordinates.representation import CartesianRepresentation
import astropy.units as u

from .representation import PlanarRepresentation
from ..instrument.constants import FOCAL_LENGTH_MM, LOCATION
import numpy as np

focal_length = FOCAL_LENGTH_MM * u.mm


class CameraFrame(BaseCoordinateFrame):
    '''Astropy CoordinateFrame representing coordinates in the CameraPlane'''
    default_representation = PlanarRepresentation
    pointing_direction = CoordinateAttribute(frame=AltAz, default=None)
    obstime = TimeAttribute(default=None)
    location = EarthLocationAttribute(default=LOCATION)


@frame_transform_graph.transform(FunctionTransform, CameraFrame, AltAz)
def camera_to_altaz(camera, altaz):
    if camera.pointing_direction is None:
        raise ValueError('Pointing Direction must not be None')

    x = camera.x.copy()
    y = camera.y.copy()

    z = 1 / np.sqrt(1 + (x / focal_length)**2 + (y / focal_length)**2)
    x *= z / focal_length
    y *= z / focal_length

    cartesian = CartesianRepresentation(x, y, z, copy=False)

    rot_z_az = rotation_matrix(-camera.pointing_direction.az, 'z')
    rot_y_zd = rotation_matrix(-camera.pointing_direction.zen, 'y')

    cartesian = cartesian.transform(rot_y_zd)
    cartesian = cartesian.transform(rot_z_az)

    altitude = 90 * u.deg - np.arccos(cartesian.z)
    azimuth = np.arctan2(cartesian.y, cartesian.x)

    return AltAz(
        alt=altitude,
        az=azimuth,
        location=camera.location,
        obstime=camera.obstime,
    )


@frame_transform_graph.transform(FunctionTransform, AltAz, CameraFrame)
def altaz_to_camera(altaz, camera):
    if camera.pointing_direction is None:
        raise ValueError('Pointing Direction must not be None')

    cartesian = altaz.cartesian

    rot_z_az = rotation_matrix(camera.pointing_direction.az, 'z')
    rot_y_zd = rotation_matrix(camera.pointing_direction.zen, 'y')

    cartesian = cartesian.transform(rot_z_az)
    cartesian = cartesian.transform(rot_y_zd)

    return CameraFrame(
        x=cartesian.x * focal_length / cartesian.z,
        y=cartesian.y * focal_length / cartesian.z,
        pointing_direction=camera.pointing_direction,
        obstime=altaz.obstime,
        location=camera.location,
    )
