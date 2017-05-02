'''
Constants describing the FACT telescope
'''
import numpy as np

LATITUDE_DEC_DEG = 28.7616  #: FACT's latitude in decimal degrees
LONGITUDE_DEC_DEG = -17.8911   #: FACT's longitude in decimal degrees
ALTITUDE_ASL_M = 2200  #: FACT's altitude above sea level in meters

position = {
    'latitude': {
        'dir': 'N',
        'deg': 28,
        'min': 45,
        'sec': 41.9
    },
    'longitude': {
        'dir': 'W',
        'deg': 17,
        'min': 53,
        'sec': 28.0
    },
    'altitude_above_sea_level': 2200
}
#: The inner diameter of the hexagonal pixels in mm.
#: This is also the grid constant of the hex grid.
PIXEL_SPACING_IN_MM = 9.5
FOCAL_LENGTH_MM = 4889  #: FACT's reflector focal length in mm.
DISTORTION_SLOPE = 0.031/1.5

#: Field of view of a single pixel in decimal degrees
FOV_PER_PIXEL_DEG = np.rad2deg(2 * np.arctan(0.5 * PIXEL_SPACING_IN_MM / FOCAL_LENGTH_MM))
