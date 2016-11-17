import pkg_resources as res
import numpy as np
from functools import lru_cache
import pandas as pd

pixel_mapping = np.genfromtxt(
    res.resource_filename('fact', 'resources/FACTmap111030.txt'),
    names=[
        'softID', 'hardID', 'geom_i', 'geom_j',
        'G-APD', 'V_op', 'HV_B', 'HV_C',
        'pos_X', 'pos_Y', 'radius'
    ],
    dtype=None,
)

GEOM_2_SOFTID = {
    (i, j): soft for i, j, soft in zip(
        pixel_mapping['geom_i'], pixel_mapping['geom_j'], pixel_mapping['softID']
    )}


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


def get_pixel_coords(mapfile=None,
                     rotate=True,
                     columns=[0, 9, 10, 11],
                     skip_header=1,
                     skip_footer=0,
                     delimiter=',',
                     unpack=True,
                     ):
    '''
    Calculate the pixel coordinates from the standard pixel-map file
    by default it gets rotated by 90 degrees clockwise to show the same
    orientation as MARS and fact-tools

    Arguments
    ---------
    mapfile : str
        path/to/pixelmap.csv, if None than the package resource is used
        [defailt: None]
    rotate : bool
        if True the view is rotated by 90 degrees counter-clockwise
        [default: True]
    colums : list-like
        the columns in the file for softID, chid, x, y
        default: [0, 9, 10, 11]
    '''

    if mapfile is None:
        mapfile = res.resource_filename('fact', 'resources/pixel-map.csv')

    softID, chid, pixel_x_soft, pixel_y_soft = np.genfromtxt(
        mapfile,
        skip_header=skip_header,
        skip_footer=skip_footer,
        delimiter=delimiter,
        usecols=columns,
        unpack=unpack,
    )

    pixel_x_soft *= 9.5
    pixel_y_soft *= 9.5

    pixel_x_chid = pixel_x_soft[chid2softid(np.arange(1440))]
    pixel_y_chid = pixel_y_soft[chid2softid(np.arange(1440))]

    # rotate by 90 degrees to show correct orientation
    if rotate is True:
        pixel_x = - pixel_y_chid
        pixel_y = pixel_x_chid
    else:
        pixel_x = pixel_x_chid
        pixel_y = pixel_y_chid

    return pixel_x, pixel_y


@lru_cache(maxsize=1)
def bias_to_trigger_patch_map():
    by_chid = pixel_mapping['hardID'].argsort()

    bias_channel = pixel_mapping[by_chid]['HV_B'] * 32 + pixel_mapping[by_chid]['HV_C']

    _, idx = np.unique(bias_channel, return_index=True)

    return bias_channel[np.sort(idx)]

@lru_cache(maxsize=1)
def pixel_dataframe():
    ''' return pixel mapping as pd.DataFrame

    '''
    pm = pd.DataFrame(pixel_mapping)
    pm.sort_values('hardID', inplace=True)
    # after sorting the CHID is in principle the index
    # of pm, but I'll like to have it explicitely
    pm['CHID'] = np.arange(len(pm))

    pm['trigger_patch_id'] = pm['CHID'] // 9
    pm['bias_patch_id'] = (
        pm['HV_B'] * 32 + pm['HV_C'] )

    bias_patch_sizes = pm.bias_patch_id.value_counts().sort_index()
    pm['bias_patch_size'] = bias_patch_sizes[pm.bias_patch_id].values

    return pm

@lru_cache(maxsize=1)
def patch_indices():
    pi = pixel_dataframe()[[
        'trigger_patch_id',
        'bias_patch_id',
        'bias_patch_size',
    ]]
    pi = pi.drop_duplicates()
    pi.reset_index(drop=True, inplace=True)
    return pi

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

    trigger_patch_currents = t_c # unshorten the name
    return  trigger_patch_currents

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