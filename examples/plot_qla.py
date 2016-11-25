from fact import qla
from fact.credentials import create_factdb_engine
import matplotlib.pyplot as plt


db = create_factdb_engine()

data = qla.get_qla_data(20161124, database=db)
binned = qla.bin_qla_data(data, bin_width_minutes=20)

qla.plot_qla(binned)

plt.show()

