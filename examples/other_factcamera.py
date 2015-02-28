import matplotlib.pyplot as plt
import fact.plotting

import numpy as np
plt.ion()

data = np.random.normal(loc=5, scale=1, size=1440)
bad_pixels = [863, 868, 297, 927, 80, 873, 1093, 1094, 527, 528, 721, 722]
f, axes = plt.subplots(2,2)

axes[0,0].plot(data, ".")
axes[0,0].set_title("Data vs pixel Id")

axes[0,1].hist(data, bins=np.linspace(0,10,100))
axes[0,1].set_title("distribution")

axes[1,0].factcamera(data, pixelset=bad_pixels, pixelsetcolour="r")
axes[1,0].set_title("bad_pixels highlighted")

axes[1,1].factcamera(data, pixelset=data>6)
axes[1,1].set_title("data > 6 highlighted")

plt.suptitle("Maximize me and see me adjust the pixel size")
