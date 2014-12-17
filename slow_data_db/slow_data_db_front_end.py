import time
import pymongo
from pymongo import MongoClient
import numpy as np
#------------------------------------------------------------------------------
class FACT_db_time_slice_of_collection(object):
    
    def __init__(self,collection,key):
        self.__collection = collection
        self.__key = key
    
    # a valid time stamp to test 16420
    def from_until(self,start_unix_time, end_unix_time):
        start = self.__unix2crazyFACT_MJD(start_unix_time)
        end = self.__unix2crazyFACT_MJD(end_unix_time)       
        cursor = self.__collection.find({"Time": {"$gte": start, "$lt": end}})
        return self.__monog_curser2numpy_array(cursor)

    def __unix2crazyFACT_MJD(self,unix_time_stamp):
        return unix_time_stamp 
        
    def __monog_curser2numpy_array(self,cursor):
        array = np.resize(0.0, cursor.count())
        for counter, document in enumerate(cursor):
            array[counter] = document[self.__key]
        return array
#------------------------------------------------------------------------------
class FACT_db_collection(object):
    
    def __init__(self,collection):  
        self.__get_keys_of_collection_assuming_they_are_the_same_for_all_documents(collection)
        for key in self.__keys:
            setattr(self, key, FACT_db_time_slice_of_collection(collection, key))
                
    def __get_keys_of_collection_assuming_they_are_the_same_for_all_documents(self,coll):
        self.__keys = coll.find_one()
        del self.__keys['_id']
        del self.__keys['QoS']
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

    def has_service(self, name):
        """
        Hi this is a text.
        @param name: this is the name we give it
        @return: returns a bool if this instance has the asked service
        """
        if name in self.database.collection_names():
            return True
        else:
            return False
            
    def __print_list(self,list_to_print):
        for item in list_to_print:
            print item
    
    def print_all_services(self):
        self.__print_list(self.database.collection_names())
 
    def __get_subset_of_services_containing(self,signature):
        subset = []
        for service_name in self.database.collection_names():
            if signature in service_name:
                subset.append(service_name)
        return subset
    
    def print_all_services_containing_snippset(self,snippset):
        subset_of_services = \
            self.__get_subset_of_services_containing(snippset)
        if not subset_of_services:
            print 'There is no service containing the snippset', snippset
        else:
            self.__print_list(subset_of_services)
                 
#------------------------------------------------------------------------------
client = MongoClient('localhost')

aux= AuxDataBaseFrontEnd(client.aux)

