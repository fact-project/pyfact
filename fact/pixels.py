import pkg_resources as res
import numpy as np


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

from functools import lru_cache

@lru_cache(maxsize=1)
def bias_to_trigger_patch_map():
    mapfile = res.resource_filename("fact", "resources/FACTmap111030.txt")

    a = np.genfromtxt(
        mapfile,
        skip_header=14,
        names=True)
    a = a[a["hardID"].argsort()]

    bias_channel = a["HV_B"].astype(int) * 32 + a["HV_C"].astype(int)
    #hardID = a["hardID"].astype(int)
    #softID = a["softID"].astype(int)
    #chid = np.arange(len(a))
    #cont_patch_id = chid // 9

    _, idx = np.unique(bias_channel, return_index=True)

    return bias_channel[np.sort(idx)]
