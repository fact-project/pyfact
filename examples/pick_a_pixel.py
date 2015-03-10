from __future__ import print_function
import matplotlib.pyplot as plt
import fact.plotting

import numpy as np

plt.ion()

data = np.random.normal(loc=5, scale=1, size=1440*300).reshape(1440,300)

fig, axes = plt.subplots(1,2)

cam = axes[0].factcamera(data.mean(axis=1), picker=10)
axes[0].set_title("click on any pixel")

axes[1].plot(data.mean(axis=0), '.')
axes[1].set_title("mean of entire camera (as in fact-tools")

plt.suptitle("Example for choosing a pixel")


def onpick(event):
    print("onpick is called")

    #if event.artist!=line: return True
    print("event:\n", event)
    print("event.__dict__:\n", event.__dict__)
    return True


fig.canvas.mpl_connect('pick_event', onpick)

