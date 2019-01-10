import numpy as np

import astropy.units as u
from astropy.coordinates import AltAz, SkyCoord
from astropy.coordinates.angle_utilities import angular_separation
import pandas as pd

from ..coordinates import CameraFrame
from ..coordinates.utils import (
    arrays_to_camera,
    arrays_to_altaz,
    arrays_to_equatorial,
)
from ..instrument.constants import LOCATION


def calc_off_position(source_x, source_y, off_index, n_off=5):
    '''
    For a given source position in camera coordinates,
    return an array with n_off off_positions

    Parameters
    ----------
    source_x: float or astropy.units.Quantity
        x position of the wanted source position
    source_y: float or astropy.units.Quantity
        y position of the wanted source position
    n_off: int
        number of off positions to calculate

    Returns
    -------
    x_off: float or astropy.units.Quantity
        x coordinate of the off position
    y_off: float or astropy.units.Quantity
        y coordinate of the off position
    '''

    if off_index < 1 or off_index > n_off:
        raise ValueError('off_index must be >= 1 and <= n_off')

    r = np.sqrt(source_x**2 + source_y**2)
    phi = np.arctan2(source_y, source_x)
    delta_phi = 2 * np.pi / (n_off + 1)
    if hasattr(phi, 'unit'):
        delta_phi *= u.rad

    x_off = r * np.cos(phi + off_index * delta_phi)
    y_off = r * np.sin(phi + off_index * delta_phi)

    return x_off, y_off


def calc_theta_equatorial(
        source_ra_prediction,
        source_dec_prediction,
        source_ra,
        source_dec):
    '''
    Calculate the angular distance between reconstructed source
    position and assumed source position, both given in the
    equatorial coordinate system.

    Parameters
    ----------
    source_ra_prediction: number or array-like
        prediction of the right ascension of the source position
        in hourangle
    source_dec_prediction: number or array-like
        prediction of the declination of the source position
        in degree
    source_ra: number or array-like
        Right ascension of the source position in hourangle
    source_dec: number or array-like
        Declination of the source position in degree

    Returns
    -------
    theta_deg: array
        theta in degrees
    '''
    source_prediction = arrays_to_equatorial(
        source_ra_prediction, source_dec_prediction,
    )
    source_pos = arrays_to_equatorial(source_ra, source_dec)

    return source_pos.separation(source_prediction).deg


def calc_theta_camera(
        source_x_prediction,
        source_y_prediction,
        source_zd,
        source_az,
        zd_pointing,
        az_pointing):
    '''
    Calculate the angular distance between reconstructed source
    position and assumed source position, where the
    prediction is given as camera coordinates and the source position
    in the horizontal coordinate system.

    Parameters
    ----------
    source_x_prediction: number or array-like
        prediction of the x postions of the source in mm
    source_y_prediction: number or array-like
        prediction of the y postions of the source in mm
    source_zd: number or array-like
        Zenith of the source position in degree
    source_az: number or array-like
        Azimuth of the source position in degree
    zd_pointing: number or array-like
        zenith angle of the pointing direction in degrees
    az_pointing: number or array-like
        azimuth angle of the pointing direction in degrees

    Returns
    -------
    theta_deg: array
        theta in degrees
    '''
    pointing = arrays_to_altaz(zd_pointing, az_pointing)
    altaz = AltAz(location=LOCATION)

    source_prediction = arrays_to_camera(
        source_x_prediction, source_y_prediction,
        pointing_direction=pointing,
    )

    source_pos = arrays_to_altaz(source_zd, source_az)
    source_prediction_alt_az = source_prediction.transform_to(altaz)
    return angular_separation(
        source_prediction_alt_az.az, source_prediction_alt_az.alt,
        source_pos.az, source_pos.alt,
    ).to(u.deg).value


def calc_theta_offs_camera(
        source_x_prediction,
        source_y_prediction,
        source_zd,
        source_az,
        zd_pointing,
        az_pointing,
        n_off=5):
    '''
    Calculate the angular distance between reconstructed source
    position and `n_off` off positions.

    Parameters
    ----------
    source_x_prediction: number or array-like
        prediction of the x coordinate of the source position in mm
    source_y_prediction: number or array-like
        prediction of the y coordinate of the source position in mm
    source_zd: number or array-like
        Zenith of the source position in degree
    source_az: number or array-like
        Azimuth of the source position in degree
    zd_pointing: number or array-like
        zenith angle of the pointing direction in degrees
    az_pointing: number or array-like
        azimuth angle of the pointing direction in degrees
    n_off: int
        How many off positions to calculate

    Returns
    -------
    theta_deg: n_off-tuple
        theta in degrees for each off position
    '''
    pointing = arrays_to_altaz(zd_pointing, az_pointing)
    source = arrays_to_altaz(source_zd, source_az)
    source_prediction = arrays_to_camera(
        source_x_prediction, source_y_prediction,
        pointing_direction=pointing,
    )

    altaz = AltAz(location=LOCATION)
    camera_frame = CameraFrame(
        location=LOCATION,
        pointing_direction=pointing
    )

    source_prediction_alt_az = source_prediction.transform_to(altaz)
    source_camera = source.transform_to(camera_frame)

    theta_offs = []

    for i in range(1, n_off + 1):
        off_x, off_y = calc_off_position(
            source_camera.x, source_camera.y, off_index=i, n_off=n_off
        )

        off_pos = SkyCoord(off_x, off_y, frame=camera_frame)
        off_pos_altaz = off_pos.transform_to(altaz)
        theta_offs.append(angular_separation(
            source_prediction_alt_az.az, source_prediction_alt_az.alt,
            off_pos_altaz.az, off_pos_altaz.alt,
        ).to(u.deg).value)
    return tuple(theta_offs)


def calc_energy_dependent_theta_cut(energy, theta_deg, bins=20, quantile=0.68):

    df = pd.DataFrame({'energy': energy, 'theta_deg': theta_deg})

    if isinstance(bins, int):
        n_bins = bins
        bins = np.percentile(energy, np.linspace(0, 100, n_bins + 1))
        bins[-1] *= 1.01

    bin_center = 0.5 * (bins[:-1] + bins[1:])

    df['bin'] = np.digitize(energy, bins=bins)
    theta_cut = df.groupby('bin')['theta_deg'].quantile(quantile)

    # make sure, events cannot be assigned to more than one region
    # so the maximum theta cut is half the wobble offset
    theta_cut[theta_cut >= 0.3] = 0.3

    # underflow equal to first bin
    theta_cut[0] = theta_cut[1]

    # overflow equal to last bin
    theta_cut[n_bins + 1] = theta_cut.loc[n_bins]

    selection_df = pd.DataFrame(index=np.arange(n_bins + 2))
    selection_df['e_low'] = np.append(-np.inf, bins)
    selection_df['e_high'] = np.append(bins, np.inf)
    selection_df['e_center'] = np.append(np.nan, np.append(bin_center, np.nan))
    selection_df['theta_cut'] = theta_cut

    return selection_df


def apply_energy_dependent_theta_cut(
    df,
    theta_cut_df,
    energy_key='gamma_energy_prediction',
):
    bins = theta_cut_df['e_low'].loc[1:]
    bin_ids = np.digitize(df[energy_key].values, bins=bins)

    regions = np.full(len(df), -1, dtype=int)

    for bin_id, cut in theta_cut_df['theta_cut'].items():
        for region in range(0, 6):
            k = 'theta_deg' if region == 0 else f'theta_deg_off_{region}'

            mask = (bin_ids == bin_id) & (df[k] < cut)
            regions[mask] = region

    return regions
