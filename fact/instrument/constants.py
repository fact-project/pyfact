'''
Constants describing the FACT telescope

.. py:data:: PIXEL_SPACING_MM

    Grid constant of the hexagonal grid in mm

.. py:data:: FOCAL_LENGTH_MM

    FACT's reflector focal length in mm
'''
import numpy as np

PIXEL_SPACING_IN_MM = 9.5
FOCAL_LENGTH_MM = 4889
PINCUSHION_DISTORTION_SLOPE = 0.031/1.5
#.. py:data:: PINCUSHION_DISTORTION_SLOPE
#:The segmented imaging reflector of FACT is well described using the thin lens
#:equation. However, the most prominent deviation from the thin lens, is the 
#:imaging reflectors pincushin distortion. The pincushin distortion projects 
#:incomning light further away from the optical axis as it is expected from the 
#:thin lens equation. The additional outward pin-cushin distortion gets stronger
#:the further the distance to the optical axis is.
#:
#:``actual_projection_angle = (1 + PINCUSHION_DISTORTION_SLOPE) * thin_lens_prediction_angle``
#:    
#:Example:
#:According to the tĥin lens model one expects incoming light of 1.5 deg 
#:incident angle relative to the optical axis to be projected in:
#:
#:``tan(1.5deg)*focal_length = 128.02mm``
#:
#:distance to the optical axis on the image sensor screen.
#:But the reflector actually projects this incoming light further to the 
#:outside to:
#:
#:``128.02mm * (1 + PINCUSHION_DISTORTION_SLOPE) = 130.67mm``
#:
#:As one can see, the correction is minor. It is only half a pixel at the outer
#:rim of the field of view.
#:
#:.. image:: figures/pincushin_distortion_slope.png

FOV_PER_PIXEL_DEG = np.rad2deg(2 * np.arctan(0.5 * PIXEL_SPACING_IN_MM / FOCAL_LENGTH_MM))
