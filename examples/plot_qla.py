from fact.qla import get_qla_data
from fact.analysis import bin_runs
from fact.plotting import plot_excess_rate
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
ax1, ax2 = plot_excess_rate(qla_results)
ax1.grid()

plt.show()
