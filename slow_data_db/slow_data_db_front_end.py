import time
import pymongo
from pymongo import MongoClient
import numpy as np
import settings

import tools
#------------------------------------------------------------------------------
class FACT_db_time_slice_of_collection(object):
    
    def __init__(self, collection, key):
        self.__collection = collection
        self.__key = key
    
    # a valid time stamp to test 16420
    def from_until(self, start, end):
        cursor = self.__collection.find({"Time": {"$gte": start, "$lt": end}})
        return tools.cursor_to_structured_array(cursor)
        
#------------------------------------------------------------------------------
class FACT_db_collection(object):
    
    def __init__(self,collection):
        self.__collection = collection
        self.__get_keys_of_collection_assuming_they_are_the_same_for_all_documents(collection)
        for key in self.__keys:
            setattr(self, key, FACT_db_time_slice_of_collection(collection, key))
                
    def __get_keys_of_collection_assuming_they_are_the_same_for_all_documents(self,coll):
        self.__keys = coll.find_one()
        del self.__keys['_id']
        del self.__keys['QoS']

    def from_until(self, start, end):
        cursor = self.__collection.find({"Time": {"$gte": start, "$lt": end}})
        return tools.cursor_to_structured_array(cursor)


#------------------------------------------------------------------------------
class AuxDataBaseFrontEnd(object):
            
    def __init__(self, database):
        self.database = database
        self.fill_in_services()
        
    def fill_in_services(self):
        self.__init_service_names()
        for service in self.__service_names:
            FACT_coll = FACT_db_collection(self.database[service]) 
            setattr(AuxDataBaseFrontEnd, service, FACT_coll)    
                
    def __init_service_names(self):
        self.__service_names = list()
        for collection_name in self.database.collection_names():
            if 'system.indexes' not in collection_name:
                self.__service_names.append(collection_name)
                

def correlate(A, B, delta):
    tt = np.array(tools.create_time_averages_from(A,B,delta))
    ttt = tools.common_times_to_be_evaluated(A,B,tt)
    Bi = tools.interpolator(B, ttt)
    Ai = tools.interpolator(A, ttt)
    return Ai, Bi


#------------------------------------------------------------------------------
import matplotlib.pyplot as plt
plt.ion()

print '-'*70
print "you should get a very quick reaction of this script, if not yout tunnel is maybe broken"
print '-'*70

client = MongoClient(settings.host, settings.port)
db = getattr(client, settings.database_name)
aux= AuxDataBaseFrontEnd(db)

# example
print "type this for a test:"
print "       a = aux.FSC_CONTROL_TEMPERATURE.from_until(16400, 16420)"
print "this command takes ~40 seconds when done I do it at home"
print  
print "The resulting array 'a' has a couple of fields, print them like this:"
print "       a.dtype.names"
print
print "in order to plot for example the average sensor temperature vs. Time, you can do:"
print "       plt.plot_date(a.Time, a.T_sens.mean(axis=1), '.')"
print  
print "Have Fun!"


print """ Example for correlation plots:
start = tools.datestr_to_facttime("20140925 20:00")
stop = tools.datestr_to_facttime("20140926 6:00")
A = aux.FSC_CONTROL_TEMPERATURE.from_until(start, stop)
B = aux.DRIVE_CONTROL_POINTING_POSITION.from_until(start, stop)
Ai,Bi = correlate(A,B, 10)
plt.plot(Ai["T_sens"][:, 0], Bi["Zd"], ".")
"""


"""
start = tools.datestr_to_facttime("20140925 20:00")
stop = tools.datestr_to_facttime("20140927 20:00")

#A = aux.FTM_CONTROL_TRIGGER_RATES.from_until(start, stop)
#B = aux.SQM_CONTROL_DATA.from_until(start, stop)

#A = aux.FSC_CONTROL_TEMPERATURE.from_until(start, stop)
A = aux.BIAS_CONTROL_CURRENT.from_until(start, stop)
#A = aux.FSC_CONTROL_HUMIDITY.from_until(start, stop)
B = aux.BIAS_CONTROL_VOLTAGE.from_until(start, stop)

as_name = "I"
bs_name = "Uout"

#plt.figure()
#plt.title("original")
#plt.plot_date(A["Time"], A[as_name], ".")
#plt.plot_date(B["Time"], B[bs_name], ".")


Ai,Bi = correlate(A,B, 1./(24.*3600.))

#plt.figure()
#plt.title("interpolated")
#plt.plot_date(Ai["Time"], Ai[as_name], ".")
#plt.plot_date(Bi["Time"], Bi[bs_name], ".")


plt.figure()
for i in range(320):
    plt.cla()
    plt.title("corr")
    plt.plot(Ai[as_name][:,i], Bi[bs_name][:,i], ".")
    plt.xlabel(as_name)
    plt.ylabel(bs_name)
    plt.grid()
    raw_input("?")
"""
start = tools.datestr_to_facttime("20120925 20:00")
stop = tools.datestr_to_facttime("20140927 6:00")
A,B = tools.correlate_dom_like(
    aux.MAGIC_WEATHER_DATA.from_until(start, stop),
    aux.FSC_CONTROL_HUMIDITY.from_until(start, stop),
    limit_in_sec = 60.)
