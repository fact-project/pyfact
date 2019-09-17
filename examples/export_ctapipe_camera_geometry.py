from astropy.table import Table
from fact.instrument import get_pixel_coords
import astropy.units as u
import numpy as np

x, y = get_pixel_coords()
x = (x * u.mm).to(u.m)
y = (y * u.mm).to(u.m)
pix_id = np.arange(1440)

radius = np.sqrt(np.diff(x)**2 + np.diff(y)**2).min() / 2
pix_area = 1.5 * np.sqrt(3) * radius**2


t = Table()

t['pix_id'] = pix_id

# convert from fact coords into hess/cta camera coordinate system
t['pix_x'] = -y
t['pix_y'] = -x

t['pix_area'] = pix_area
t.meta['TAB_TYPE'] = 'ctapipe.instrument.CameraGeometry'
t.meta['PIX_TYPE'] = 'hexagonal'
t.meta['CAM_ID'] = 'FACT'
t.meta['PIX_ROT'] = 30.0
t.meta['CAM_ROT'] = 0.0
t.meta['SOURCE'] = 'pyfact'
t.meta['TAB_VER'] = '1'


t.write('FACT.camgeom.fits.gz', overwrite=True)
