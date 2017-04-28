import numpy as np
'''
Constants describing the FACT telescope

..data:: PIXEL_SPACING_MM

    Grid constant of the hexagonal grid in mm

..data:: FOCAL_LENGTH_MM

    FACT's reflector focal length in mm

..data:: DISTORTION_SLOPE

    FACT's

'''


PIXEL_SPACING_IN_MM = 9.5
FOCAL_LENGTH_MM = 4889
DISTORTION_SLOPE = 0.031/1.5

FOV_PER_PIXEL_DEG = np.rad2deg(2 * np.arctan(0.5 * PIXEL_SPACING_IN_MM / FOCAL_LENGTH_MM))
