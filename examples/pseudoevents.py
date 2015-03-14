import matplotlib.pyplot as plt
from fact.plotting import Viewer, get_pixel_coords
import numpy as np

plt.rcdefaults()

x, y = get_pixel_coords()

x /= 10
y /= 10

N = 20
data = np.empty((N, 1440))
for i in range(N):
    max_photoncharge = np.random.poisson(100)
    a, b = np.random.uniform(-10, 10, 2)
    phi = np.random.uniform(0, 2*np.pi)
    x1 = np.cos(phi) * x - np.sin(phi)*y
    y1 = np.sin(phi) * x + np.cos(phi)*y
    amp1 = np.random.uniform(1, 5)
    amp2 = np.random.uniform(0.1, 0.5)
    data[i,:] = np.random.poisson(
        max_photoncharge/(1+amp1*(x1-a)**2 + amp2*(y1-b)**2),
        1440
    )
    data[i,:] += np.random.normal(0, 1, 1440)

# plt.factcamera(data[0], pixelset=data[0]>4)
# plt.show()
# plt.factpixelids(color="red")
# plt.savefig("test.pdf")

Viewer(data, 'photoncharge', data>5)
