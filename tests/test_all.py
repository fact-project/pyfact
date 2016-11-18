def test_tk():
    from matplotlib.backends import _tkagg


def test_cameraplot():
    from fact.plotting import camera
    from numpy.random import uniform

    data = uniform(0, 20, 1440)
    camera(data)


def test_night_integer_datetime():
    """ In FACT a day goes from noon to noon and is sometimes referred by a
    single integer: 20151231 for example refers to the night beginning
    on 31.12.2015 evening and lasting until 01.01.2016 morning.
    """
    from fact import night_integer
    from datetime import datetime

    assert night_integer(datetime(2015, 12, 31, 18, 0)) == 20151231
    assert night_integer(datetime(2016, 1, 1, 4, 0)) == 20151231


def test_night_integer_pandas_datetimeindex():
    """ docu see test above
    """
    from fact import night_integer
    from pandas import to_datetime

    dates = to_datetime([
        "2015-12-31 14:40:15",  # afternoon --> 20151231
        "2016-01-01 04:40:15",  # early morning --> 20151231
        "'2016-01-01 12:40:15"   # next day after noon --> 20160101
        ])

    assert (night_integer(dates) == [20151231, 20151231, 20160101]).all()


def test_patch_indices():
    from fact.pixels import patch_indices

    pi = patch_indices
    assert pi[pi.bias_patch_id==1].trigger_patch_id.iloc[0] == 0
    assert pi[pi.bias_patch_id==128].trigger_patch_id.iloc[0] == 40
    assert pi[pi.bias_patch_id==129].trigger_patch_id.iloc[0] == 40

    assert pi[pi.trigger_patch_id == 47].bias_patch_id.iloc[0] == 142
    assert pi[pi.trigger_patch_id == 47].bias_patch_id.iloc[1] == 143
    assert (pi[pi.trigger_patch_id == 47].bias_patch_id == [142, 143]).all()


def test_easier_use_of_patch_indices():
    from fact.pixels import patch_indices
    pi = patch_indices

    bias_patch_ids = pi.bias_patch_id.values

    # find out which are the bias patches for trigger patch 47
    trigger_patch = 47
    # double the number and add 0 or 1 to find both bias patch ids
    assert bias_patch_ids[2 * trigger_patch + 0] == 142
    assert bias_patch_ids[2 * trigger_patch + 1] == 143

    t_id_BY_b_id = pi.sort_values('bias_patch_id').trigger_patch_id.values


def test_bias_patch_values_into_trigger_patches():
    # assume you have values sorted by bias_patch_id, e.g. currents like this:
    #  currents = np.random.normal(loc=40, scale=10, size=320)
    # i.e. you have 320 values and want to know which two of them
    # should be combined into one trigger_patch.

    # so you might start by sorting by the index you have and get the one you
    # want, like this:
    from fact.pixels import patch_indices
    pi = patch_indices

    t_id_BY_b_id = pi.sort_values('bias_patch_id').trigger_patch_id.values

    # but what does this help you? sure you can say:
    assert t_id_BY_b_id[40] == 20
    assert t_id_BY_b_id[41] == 20
    assert t_id_BY_b_id[80] == 72
    assert t_id_BY_b_id[81] == 72
    # thus you learn that the bias patches 40 and 41 belong to
    # trigger patch 20 (as one might have guessed)
    # and bias_patches 80;81 belong to trigger patch 72, which one would
    # *not* have guessed, which is why we need this mapping table.

    # However it does not help you. Since you probably want this:
    # convert the two bias currents I have for each trigger patch, into a combined
    # value for this trigger patch.


def test_coords_relation_to_pos_from_dataframe():

    from fact.pixels import get_pixel_dataframe
    from fact.pixels import get_pixel_coords
    import numpy as np

    pc = get_pixel_coords()
    pd = get_pixel_dataframe()

    assert np.allclose(pc[0], -pd.pos_Y.values*9.5)
    assert np.allclose(pc[1], pd.pos_X.values*9.5)
