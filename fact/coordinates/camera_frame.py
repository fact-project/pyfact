from astropy.coordinates import (
    BaseCoordinateFrame,
    FrameAttribute,
    AltAz,
    frame_transform_graph,
    FunctionTransform
)
from astropy.coordinates.matrix_utilities import rotation_matrix
from astropy.coordinates.representation import CartesianRepresentation
import astropy.units as u

from .representation import PlanarRepresentation
from ..instrument.constants import FOCAL_LENGTH_MM
import numpy as np

focal_length = FOCAL_LENGTH_MM * u.mm


class CameraFrame(BaseCoordinateFrame):
    '''Astropy CoordinateFrame representing coordinates in the CameraPlane'''
    default_representation = PlanarRepresentation
    pointing_direction = FrameAttribute(default=None)


@frame_transform_graph.transform(FunctionTransform, CameraFrame, AltAz)
def camera_to_altaz(camera_frame, altaz):
    if camera_frame.pointing_direction is None:
        raise AttributeError('Pointing Direction must be set')

    x = camera_frame.x
    y = camera_frame.y

    z = 1 / np.sqrt(1 + (x / focal_length)**2 + (y / focal_length)**2)
    x *= z / focal_length
    y *= z / focal_length

    cartesian = CartesianRepresentation(x, y, z, copy=False)

    rot_z_az = rotation_matrix(camera_frame.pointing_direction.az, 'z')
    rot_y_zd = rotation_matrix(camera_frame.pointing_direction.zen, 'y')

    cartesian = cartesian.transform(rot_y_zd)
    cartesian = cartesian.transform(rot_z_az)

    altitude = 90 * u.deg - np.arccos(cartesian.z)
    azimuth = np.arctan2(cartesian.y, cartesian.x)

    return AltAz(
        alt=altitude, az=azimuth,
        location=altaz.location,
        obstime=altaz.obstime,
    )


@frame_transform_graph.transform(FunctionTransform, AltAz, CameraFrame)
def altaz_to_camera(altaz, camera_frame):
    cartesian = altaz.cartesian

    rot_z_az = rotation_matrix(-camera_frame.pointing_direction.az, 'z')
    rot_y_zd = rotation_matrix(-camera_frame.pointing_direction.zen, 'y')

    cartesian = cartesian.transform(rot_z_az)
    cartesian = cartesian.transform(rot_y_zd)

    return CameraFrame(
        x=cartesian.x * focal_length / cartesian.z,
        y=cartesian.y * focal_length / cartesian.z,
        pointing_direction=camera_frame.pointing_direction,
    )
