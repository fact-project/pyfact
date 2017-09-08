import pkg_resources as res
import numpy as np
from functools import lru_cache
import pandas as pd

from .constants import (
    FOCAL_LENGTH_MM, PINCUSHION_DISTORTION_SLOPE,
    PIXEL_SPACING_MM, FOV_PER_PIXEL_DEG
)


def camera_distance_mm_to_deg(distance_mm):
    '''
    Transform a distance in mm in the camera plane
    to it's approximate equivalent in degrees.
    '''

    return distance_mm * FOV_PER_PIXEL_DEG / PIXEL_SPACING_MM


pixel_mapping = np.genfromtxt(
    res.resource_filename('fact', 'resources/FACTmap111030.txt'),
    names=[
        'softID', 'hardID', 'geom_i', 'geom_j',
        'G-APD', 'V_op', 'HV_B', 'HV_C',
        'pos_X', 'pos_Y', 'radius'
    ],
    dtype=None,
)

non_standard_pixel_chids = dict(
    dead=[927, 80, 873],
    crazy=[863, 297, 868],
    twins=[            # the signals of these pairs of pixels are the same
        (1093, 1094),
        (527, 528),
        (721, 722),
    ]
)


GEOM_2_SOFTID = {
    (i, j): soft for i, j, soft in zip(
        pixel_mapping['geom_i'], pixel_mapping['geom_j'], pixel_mapping['softID']
    )}


def reorder_softid2chid(array):
    '''
    Returns view to the given array, remapped from softid order
    to chid order (e.g. MARS ordering to fact-tools ordering)
    '''
    return array[CHID_2_SOFTID]


@lru_cache(maxsize=1)
def get_pixel_dataframe():
    ''' return pixel mapping as pd.DataFrame

    '''
    pm = pd.DataFrame(pixel_mapping)
    pm.sort_values('hardID', inplace=True)
    # after sorting the CHID is in principle the index
    # of pm, but I'll like to have it explicitely
    pm['CHID'] = np.arange(len(pm))

    pm['trigger_patch_id'] = pm['CHID'] // 9
    pm['bias_patch_id'] = pm['HV_B'] * 32 + pm['HV_C']

    bias_patch_sizes = pm.bias_patch_id.value_counts().sort_index()
    pm['bias_patch_size'] = bias_patch_sizes[pm.bias_patch_id].values

    pm['x'] = -pm.pos_Y.values * PIXEL_SPACING_MM
    pm['y'] = pm.pos_X.values * PIXEL_SPACING_MM

    pm['x_angle'] = np.rad2deg(
        np.arctan(pm.x / FOCAL_LENGTH_MM) *
        (1 + PINCUSHION_DISTORTION_SLOPE)
    )
    pm['y_angle'] = np.rad2deg(
        np.arctan(pm.y / FOCAL_LENGTH_MM) *
        (1 + PINCUSHION_DISTORTION_SLOPE)
    )

    return pm


FOV_RADIUS = np.hypot(
    get_pixel_dataframe().x_angle, get_pixel_dataframe().y_angle
).max()


patch_indices = get_pixel_dataframe()[[
        'trigger_patch_id',
        'bias_patch_id',
        'bias_patch_size',
    ]].drop_duplicates().reset_index(drop=True)


@np.vectorize
def geom2soft(i, j):
    return GEOM_2_SOFTID[(i, j)]


def softid2chid(softid):
    return hardid2chid(pixel_mapping['hardID'])[softid]


def softid2hardid(softid):
    return pixel_mapping['hardID'][softid]


def hardid2chid(hardid):
    crate = hardid // 1000
    board = (hardid // 100) % 10
    patch = (hardid // 10) % 10
    pixel = (hardid % 10)
    return pixel + 9 * patch + 36 * board + 360 * crate


CHID_2_SOFTID = np.empty(1440, dtype=int)
for softid in range(1440):
    hardid = pixel_mapping['hardID'][softid]
    chid = hardid2chid(hardid)
    CHID_2_SOFTID[chid] = softid


def chid2softid(chid):
    return CHID_2_SOFTID[chid]


def hardid2softid(hardid):
    return chid2softid(hardid2chid(hardid))


def get_pixel_coords():
    '''
    Calculate the pixel coordinates from the standard pixel-map file
    by default it gets rotated by 90 degrees clockwise to show the same
    orientation as MARS and fact-tools
    '''
    df = get_pixel_dataframe()

    return df.x.values, df.y.values


@lru_cache(maxsize=1)
def bias_to_trigger_patch_map():
    by_chid = pixel_mapping['hardID'].argsort()

    bias_channel = pixel_mapping[by_chid]['HV_B'] * 32 + pixel_mapping[by_chid]['HV_C']

    _, idx = np.unique(bias_channel, return_index=True)

    return bias_channel[np.sort(idx)]


def combine_bias_patch_current_to_trigger_patch_current(bias_patch_currents):
    """
    For this to work, you need to know that the calibrated currents in FACT
    which are delivered by the program FEEDBACK for all 320 bias patches
    are given as "uA per pixel per bias patch", not as "uA per bias patch"
    So if you want to combine these currents into one value given as:
    "uA per trigger patch" or "uA per pixel per trigger patch", you need to know
    the number of pixels in a bias patch.

    Luckily this is given by our patch_indices() DataFrame
    """

    pi = patch_indices()
    fourers = pi[pi.bias_patch_size == 4].sort_values('trigger_patch_id')
    fivers = pi[pi.bias_patch_size == 5].sort_values('trigger_patch_id')

    b_c = bias_patch_currents  # just to shorten the name
    t_c = b_c[fourers.bias_patch_id.values] * 4/9 + b_c[fivers.bias_patch_id.values] * 5/9

    trigger_patch_currents = t_c  # unshorten the name
    return trigger_patch_currents


def take_apart_trigger_values_for_bias_patches(trigger_rates):
    """
    Assumption is you have 160 values from trigger patches,
    such as the trigger rates per patch, or the trigger threshold per patch
    or whatever else you cant find per patch.

    And for some reason you say: Well this is valid for the entire trigger
    patch really, but I believe it also correlates with the bias patch
    """
    pi = patch_indices().sort_values('bias_patch_id')

    return trigger_rates[pi.trigger_patch_id.values]
