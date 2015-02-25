from nose.tools import raises

# if you want to test if something works:
def test1():
    assert 1 == 1

# if you want to be sure that something actually raises an exception:
@raises(AssertionError)
def test2():
    assert 1 == 2
