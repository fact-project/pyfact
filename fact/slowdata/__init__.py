''' FACT slow database frontent

provided for your convenience.
'''
import numpy as np
from pymongo import MongoClient
from . import settings
from . import tools
from . import correlation


__all__ = ['connect', 'correlation']


class ServiceField(object):
    ''' represents one Field of a Service
    '''

    def __init__(self, collection, key):
        self.__collection = collection
        self.__key = key

    def from_until(self, start, end):
        ''' retrieve field from start to end date as numpy array.
        '''
        cursor = self.__collection.find({'Time': {'$gte': start, '$lt': end}})
        return tools.cursor_to_structured_array(cursor)


class Service(object):
    ''' represents a FACT slow data service
    '''

    def __init__(self, collection):
        self.__collection = collection
        self.__get_service_field_names(collection)
        for key in self.__keys:
            setattr(
                self,
                key,
                ServiceField(collection, key))

        self.__keys = None

    def __get_service_field_names(self, coll):
        ''' retrieve the field names of this service

        by  using one example decument.
        '''
        self.__keys = coll.find_one()
        del self.__keys['_id']

    def from_until(self, start, end, sample_period=None, skip=None, fields=None):
        ''' retrieve service from start to end date as numpy array.

        start : starttime in FJD
        end   : end time in FJD

        keyword arguments:

        sample_period : time(in days) into which the request should be splitted --> skip
        skip   : number of periods, which should be skipped during request
        fields : list of field names to be requested [default: all fields]
        '''
        if sample_period is not None:
            sample_boundaries = np.arange(start, end, sample_period)
        else:
            sample_boundaries = np.array([start, end])

        samples_start = sample_boundaries[0:-1:skip]
        samples_end = sample_boundaries[1::skip]
        dict_list = []
        for _start, _end in zip(samples_start, samples_end):
            start_stop_dict = {'Time': {
                '$gte': float(_start),
                '$lt': float(_end)}
            }
            dict_list.append(start_stop_dict)

        if fields is not None:
            cursor = self.__collection.find({'$or': dict_list}, fields=fields)
        else:
            cursor = self.__collection.find({'$or': dict_list})

        return tools.cursor_to_structured_array(cursor)


class AuxDataBaseFrontEnd(object):

    def __init__(self, database):
        self.database = database
        self.__service_names = None  # to be initialised in __init_service_names
        self.__fill_in_services()

    def __fill_in_services(self):
        self.__init_service_names()
        for service_name in self.__service_names:
            service = Service(self.database[service_name])
            setattr(self, service_name, service)

    def __init_service_names(self):
        self.__service_names = list()
        for collection_name in self.database.collection_names():
            if 'system.indexes' not in collection_name:
                self.__service_names.append(collection_name)


def connect(host=None, port=None, db_name=None):
    if host is None:
        host = settings.host

    if port is None:
        port = settings.port

    if db_name is None:
        db_name = settings.db_name

    client = MongoClient(host, port)
    return AuxDataBaseFrontEnd(getattr(client, db_name))
