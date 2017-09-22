from astropy.coordinates import AltAz, ICRS, SkyCoord
from astropy.time import Time
import astropy.units as u
import numpy as np
from .camera_frame import CameraCoordinate
from ..instrument.constants import LOCATION


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
    eq_coordinates = SkyCoord(ra=ra * u.hourangle, dec=dec * u.deg)
    pointing_direction = AltAz(
        alt=(90 - np.asanyarray(zd_pointing)) * u.deg,
        az=np.asanyarray(az_pointing) * u.deg,
    )
    observation_time = Time(np.asanyarray(observation_time).astype(str))

    altaz_frame = AltAz(obstime=observation_time, location=LOCATION)
    camera_frame = CameraCoordinate(pointing_direction=pointing_direction)

    altaz_coordinates = eq_coordinates.transform_to(altaz_frame)
    cam_coordinates = altaz_coordinates.transform_to(camera_frame)

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
    pointing_direction = AltAz(
        alt=(90 - np.asanyarray(zd_pointing)) * u.deg,
        az=np.asanyarray(az_pointing) * u.deg,
        location=LOCATION,
    )

    cam_coordinates = CameraCoordinate(
        np.asanyarray(x) * u.mm, np.asanyarray(y) * u.mm,
        pointing_direction=pointing_direction,
    )

    observation_time = Time(np.asanyarray(observation_time).astype(str))
    altaz_frame = AltAz(obstime=observation_time, location=LOCATION)
    altaz_coordinates = cam_coordinates.transform_to(altaz_frame)
    eq_coordinates = altaz_coordinates.transform_to(ICRS)

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
    pointing_direction = AltAz(
        alt=(90 - np.asanyarray(zd_pointing)) * u.deg,
        az=np.asanyarray(az_pointing) * u.deg,
    )

    altaz = AltAz(
        alt=(90 - np.asanyarray(zd)) * u.deg,
        az=np.asanyarray(az) * u.deg,
    )

    camera_frame = CameraCoordinate(pointing_direction=pointing_direction)
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
    pointing_direction = AltAz(
        alt=(90 - np.asanyarray(zd_pointing)) * u.deg,
        az=np.asanyarray(az_pointing) * u.deg,
        location=LOCATION,
    )

    cam_coordinates = CameraCoordinate(
        np.asanyarray(x) * u.mm, np.asanyarray(y) * u.mm,
        pointing_direction=pointing_direction,
    )

    altaz = cam_coordinates.transform_to(AltAz())

    return altaz.zen.deg, altaz.az.deg
