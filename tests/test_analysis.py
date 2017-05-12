def test_proton_obstime():
    from fact.analysis.statistics import calc_proton_obstime
    n_simulated = 780046520
    t = calc_proton_obstime(
        n_events=n_simulated,
        spectral_index=2.7,
        max_impact=400,
        viewcone=5,
        e_min=100,
        e_max=200e3,
    )
    assert int(t) == 15397
