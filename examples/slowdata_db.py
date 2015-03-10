from __future__ import print_function
import sys
import matplotlib.pyplot as plt
from fact.time import iso2dt, fjd, OFFSET
from fact.slowdata import connect
import pymongo

start_time = fjd(iso2dt("01.04.2013 12:34:56.789"))
stop_time = fjd(iso2dt("03.04.2013"))

print("connecting to FACT slowdata DB ...")
try:
	db = connect(
		host='localhost',
		port=37017,
		db_name='aux')
except pymongo.errors.ConnectionFailure as e:
	print("... was not able to connect to DB. maybe the tunnel is not open?.")
	print("\n\n")
	sys.exit(-1)


print("requesting some data from the slowdata DB, might take a while...")
interesting_data = db.MAGIC_WEATHER_DATA.from_until(start_time, stop_time)

#interesting_data is a numpy structured array
print("dtype of interesting_data {}".format(interesting_data.dtype))

plt.figure()
plt.plot_date(interesting_data['Time'] + OFFSET, interesting_data['T'], '.', label="outside temperature")
plt.plot_date(interesting_data['Time'] + OFFSET, interesting_data['T_dew'], '.', label="dewpoint")
plt.ylabel("Temperature [deg C]")
plt.xlabel("Date")
plt.title("Some interesting_data")
plt.legend()
plt.show()