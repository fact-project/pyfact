from astropy.coordinates import AltAz, ICRS, SkyCoord
from astropy.time import Time
import astropy.units as u
import numpy as np
from .camera_frame import CameraFrame
from ..instrument.constants import LOCATION


def arrays_to_altaz(zenith, azimuth, obstime=None):
    frame = AltAz(location=LOCATION, obstime=obstime)
    return SkyCoord(
        az=np.asanyarray(azimuth) * u.deg,
        alt=np.asanyarray(90 - zenith) * u.deg,
        frame=frame,
    )


def arrays_to_camera(x, y, pointing_direction, obstime=None):
    frame = CameraFrame(pointing_direction=pointing_direction, obstime=obstime)
    return SkyCoord(
        x=np.asanyarray(x) * u.mm,
        y=np.asanyarray(y) * u.mm,
        frame=frame,
    )


def arrays_to_equatorial(ra, dec, obstime=None):
    return SkyCoord(
        ra=np.asanyarray(ra) * u.hourangle,
        dec=np.asanyarray(dec) * u.deg,
        obstime=obstime
    )


def equatorial_to_camera(ra, dec, zd_pointing, az_pointing, observation_time):
    '''
    Convert sky coordinates from the equatorial frame to FACT camera
    coordinates.

    Parameters
    ----------
    ra: number or array-like
        Right ascension in hourangle
    dec: number or array-like
        Declination in degrees
    zd_pointing: number or array-like
        Zenith distance of the telescope pointing direction in degree
    az_pointing: number or array-like
        Azimuth of the telescope pointing direction in degree
    observation_time: datetime or np.datetime64
        Time of the observations

    Returns
    -------
    x: number or array-like
        x-coordinate in the camera plane in mm.
        Following the axis of the the FACTPixelMap file (and FACT-Tools).
    y: number or array-like
        y-coordinate in the camera plane in mm.
        Following the axis of the the FACTPixelMap file (and FACT-Tools).
    '''
    obstime = Time(np.asanyarray(observation_time).astype(str))
    eq_coordinates = arrays_to_equatorial(ra, dec=dec, obstime=obstime)
    pointing_direction = arrays_to_altaz(zd_pointing, az_pointing)

    camera_frame = CameraFrame(pointing_direction=pointing_direction)
    cam_coordinates = eq_coordinates.transform_to(camera_frame)

    return cam_coordinates.x.to(u.mm).value, cam_coordinates.y.to(u.mm).value


def camera_to_equatorial(x, y, zd_pointing, az_pointing, observation_time):
    '''
    Convert FACT camera coordinates to sky coordinates in the equatorial (icrs)
    frame.

    Parameters
    ----------
    x: number or array-like
        x-coordinate in the camera plane in mm.
        Following the axis of the the FACTPixelMap file (and FACT-Tools).
    y: number or array-like
        y-coordinate in the camera plane in mm.
        Following the axis of the the FACTPixelMap file (and FACT-Tools).
    zd_pointing: number or array-like
        Zenith distance of the telescope pointing direction in degree
    az_pointing: number or array-like
        Azimuth of the telescope pointing direction in degree
    observation_time: datetime or np.datetime64
        Time of the observations

    Returns
    -------
    ra: number or array-like
        Right ascension in hourangle
    dec: number or array-like
        Declination in degrees
    '''
    obstime = Time(np.asanyarray(observation_time).astype(str))
    pointing_direction = arrays_to_altaz(zd_pointing, az_pointing)
    cam_coordinates = arrays_to_camera(x, y, pointing_direction, obstime=obstime)
    eq_coordinates = cam_coordinates.transform_to(ICRS)

    return eq_coordinates.ra.hourangle, eq_coordinates.dec.deg


def horizontal_to_camera(zd, az, zd_pointing, az_pointing):
    '''
    Convert sky coordinates from the equatorial frame to FACT camera
    coordinates.

    Parameters
    ----------
    zd: number or array-like
        Zenith distance in hourangle
    az: number or array-like
        azimuth in degrees
    zd_pointing: number or array-like
        Zenith distance of the telescope pointing direction in degree
    az_pointing: number or array-like
        Azimuth of the telescope pointing direction in degree
    observation_time: datetime or np.datetime64
        Time of the observations

    Returns
    -------
    x: number or array-like
        x-coordinate in the camera plane in mm.
        Following the axis of the the FACTPixelMap file (and FACT-Tools).
    y: number or array-like
        y-coordinate in the camera plane in mm.
        Following the axis of the the FACTPixelMap file (and FACT-Tools).
    '''
    altaz = arrays_to_altaz(zd, az)
    pointing_direction = arrays_to_altaz(zd_pointing, az_pointing)

    camera_frame = CameraFrame(pointing_direction=pointing_direction)
    cam_coordinates = altaz.transform_to(camera_frame)

    return cam_coordinates.x.to(u.mm).value, cam_coordinates.y.to(u.mm).value


def camera_to_horizontal(x, y, zd_pointing, az_pointing):
    '''
    Convert FACT camera coordinates to sky coordinates in the equatorial (icrs)
    frame.

    Parameters
    ----------
    x: number or array-like
        x-coordinate in the camera plane in mm.
        Following the axis of the the FACTPixelMap file (and FACT-Tools).
    y: number or array-like
        y-coordinate in the camera plane in mm.
        Following the axis of the the FACTPixelMap file (and FACT-Tools).
    zd_pointing: number or array-like
        Zenith distance of the telescope pointing direction in degree
    az_pointing: number or array-like
        Azimuth of the telescope pointing direction in degree

    Returns
    -------
    zd: number or array-like
        Zenith distance in degrees
    az: number or array-like
        Declination in degrees
    '''
    pointing_direction = arrays_to_altaz(zd_pointing, az_pointing)
    cam_coordinates = arrays_to_camera(x, y, pointing_direction)
    altaz = cam_coordinates.transform_to(AltAz(location=LOCATION))

    return altaz.zen.deg, altaz.az.deg
