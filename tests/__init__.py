from nose.tools import raises

def test_tk():
    from matplotlib.backends import _tkagg

def test_cameraplot():
    import matplotlib.pyplot as plt
    import fact.plotting
    from numpy.random import uniform

    data = uniform(0, 20, 1440)
    plt.factcamera(data)
