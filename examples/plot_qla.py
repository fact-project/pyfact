from fact.qla import get_qla_data, plot_qla
from fact.analysis import bin_runs
import matplotlib.pyplot as plt

runs = get_qla_data(
    20140622, 20140624,
    sources=['Mrk 501', '1ES 1959+650', 'Crab', 'Mrk 421'],
)

qla_results = bin_runs(
    runs,
    bin_width_minutes=20,
    discard_ontime_fraction=0.9,
)
plot_qla(qla_results)

plt.show()
