def test_tk():
    from matplotlib.backends import _tkagg


def test_cameraplot():
    from fact.plotting import camera
    from numpy.random import uniform

    data = uniform(0, 20, 1440)
    camera(data)


def test_dim_import():
    import fact.dim
