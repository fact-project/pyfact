import numpy as np


def test_neighbors():
    from fact.instrument.camera import get_neighbor_matrix

    neighbors = get_neighbor_matrix()

    assert neighbors[1144, 259]
    assert neighbors[1144, 1143]
    assert neighbors[1144, 1146]
    assert neighbors[1144, 1147]
    assert neighbors[1144, 287]
    assert neighbors[1144, 284]
    assert not neighbors[1144, 256]
    assert not neighbors[1144, 281]

    assert np.all(neighbors.diagonal() == 0)


def test_n_neighbors():
    from fact.instrument.camera import get_num_neighbors

    n_neighbors = get_num_neighbors()

    assert n_neighbors[54] == 3
    assert n_neighbors[86] == 3
    assert n_neighbors[81] == 4
