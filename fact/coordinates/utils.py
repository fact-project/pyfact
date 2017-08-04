from astropy.coordinates import AltAz, SkyCoord
from astropy.time import Time
import astropy.units as u
from .camera_frame import CameraFrame
from ..instrument.constants import LOCATION


def equatorial_to_camera(ra, dec, ra_pointing, dec_pointing, observation_time):
    eq_coordinates = SkyCoord(ra=ra * u.hourangle, dec=dec * u.deg)
    pointing_direction = SkyCoord(
        ra=ra_pointing * u.hourangle,
        dec=dec_pointing * u.deg,
    )
    observation_time = Time(observation_time)

    altaz_frame = AltAz(obstime=observation_time, location=LOCATION)
    camera_frame = CameraFrame(pointing_direction=pointing_direction)

    altaz_coordinates = eq_coordinates.transform_to(altaz_frame)
    cam_coordinates = altaz_coordinates.transform_to(camera_frame)

    return cam_coordinates.x.to(u.mm).value, cam_coordinates.y.to(u.mm).value


def camera_to_equatorial(x, y, ra_pointing, dec_pointing, observation_time):
    pointing_direction = SkyCoord(
        ra=ra_pointing * u.hourangle,
        dec=dec_pointing * u.deg,
    )
    observation_time = Time(observation_time)

    cam_coordinates = CameraFrame(
        x * u.mm, y*u.mm,
        pointing_direction=pointing_direction,
    )

    altaz_frame = AltAz(obstime=observation_time, location=LOCATION)
    altaz_coordinates = cam_coordinates.transform_to(altaz_frame)
    eq_coordinates = altaz_coordinates.transform_to(SkyCoord)

    return eq_coordinates.ra.hourangle, eq_coordinates.dec.deg
