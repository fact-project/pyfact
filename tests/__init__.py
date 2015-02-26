from nose.tools import raises

def test_tk():
    from matplotlib.backends import _tkagg

def test_cameraplot():
    import matplotlib
    matplotlib.use('agg', warn=False, force=True)
    import matplotlib.pyplot as plt
    import fact.plotting
    from numpy.random import uniform
    import os

    data = uniform(0, 20, 1440)
    plt.factcamera(data)
