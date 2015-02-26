from nose.tools import raises

# if you want to test if something works:
def test1():
    assert 1 == 1

# if you want to be sure that something actually raises an exception:
@raises(AssertionError)
def test2():
    assert 1 == 2

def test_tk():
    from matplotlib.backends import _tkagg

def test_cameraplot():
    import matplotlib.pyplot as plt
    import fact.plotting
    from numpy.random import uniform
    import os

    data = uniform(0, 20, 1440)
    plt.factcamera(data)
    plt.savefig("test.pdf")

    assert os.path.isfile("test.pdf")
    os.remove("test.pdf")
