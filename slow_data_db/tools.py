import numpy as np
import pymongo
import logging
import time 
import calendar
from scipy import interpolate

def cursor_to_rec_array(cursor):
    array = cursor_to_structured_array(cursor)
    return array.view(np.recarray)

def cursor_to_structured_array(cursor):
    N = cursor.count()
    if N > 1000:
        logging.warning("loading {} documents form database"
                     " .. might take a while".format(N))

    structured_array_dtype = make_numpy_dtype_from_cursor(cursor)
    array = np.zeros(N, structured_array_dtype)

    for counter, document in enumerate(cursor):
        for field_name in structured_array_dtype.names:
            array[field_name][counter] = document[field_name]

    return array

def make_numpy_dtype_from_cursor(cursor):

	collection_of_this_cursor = cursor.collection
	example_document = collection_of_this_cursor.find_one()
	if example_document is None:
		# collection is empty
		raise LookupError('associated collection of cursor is empty.')

	return make_numpy_dtype_from_document(example_document)

def make_numpy_dtype_from_document(doc):

    list_of_names_n_types = []
    for field_name in doc:
        if '_id' in field_name:
            continue
        element = doc[field_name]
        element_array = np.array(element)
        list_of_names_n_types.append(
            ( str(field_name), 
              element_array.dtype.str, 
              element_array.shape)
        )

    return np.dtype(list_of_names_n_types)    
    
#------------------------------------------------------------------------------------
# interpolator
# zeit konzidenz finder -- time adjazenz matrix macher oder so

def common_times_to_be_evaluated(support_A, support_B, times_to_be_evaluated):
    tA = support_A["Time"]    
    tB = support_B["Time"]
    times_to_be_evaluated = times_to_be_evaluated[  times_to_be_evaluated >= max(tA[0],tB[0])  ]
    times_to_be_evaluated = times_to_be_evaluated[times_to_be_evaluated <= min(tA[-1],tB[-1])]

    return times_to_be_evaluated
def interpolator(support, times_to_be_evaluated):
    """
        support : is  a structured array with, "Time" 
                    and a lot of other fields, to be interpolated.

        times_to_be_evaluated : is a 1D array-like holding the times, 
                        where the interpolation should be done
    """
    t = support["Time"]
    #times_to_be_evaluated = times_to_be_evaluated[times_to_be_evaluated >= t[0]]
    #times_to_be_evaluated = times_to_be_evaluated[times_to_be_evaluated <= t[-1]]

    field_names = [name for name in support.dtype.names if not "Time" in name]
    interpolators_for_fields = {}
    for name in field_names:
        interpolators_for_fields[name] = interpolate.interp1d(t, support[name], axis=0)


    output_array = np.zeros(len(times_to_be_evaluated), dtype=support.dtype)

    for name in field_names:
        output_array[name] = interpolators_for_fields[name](times_to_be_evaluated)

    output_array["Time"] = times_to_be_evaluated
    return output_array


def create_time_averages_from(A,B, delta):
    tA = A["Time"]
    tB = B["Time"]

    print time.ctime()
    list_of_averages = []

    iAl = np.searchsorted(tA, tB-delta)
    iAr = np.searchsorted(tA, tB+delta)

    for index_in_B,tup in enumerate(zip(iAl,iAr)):
        left,right = tup
        tb = tB[index_in_B]
        list_of_averages.append((tA[left:right].sum() + tb) / (1+len(tA[left:right])))

    iBl = np.searchsorted(tB, tA-delta)
    iBr = np.searchsorted(tB, tA+delta)

    print time.ctime()
    for index_in_A,tup in enumerate(zip(iBl,iBr)):
        left,right = tup
        ta = tA[index_in_A]
        list_of_averages.append((tB[left:right].sum() + ta) / (1+len(tB[left:right])))
    

    return list_of_averages


def make_time_distance_matrix(A,B):
    tA = A["Time"][:, np.newaxis]
    tB = B["Time"][np.newaxis, :]

    time_distance_matrix = np.abs(tA - tB)
    return time_distance_matrix

def create_time_averages_from_time_distance_matrix(tdm,A,B,delta):
    tA = A["Time"]
    tB = B["Time"]

    list_of_averages = []

    for a_index in range(len(tA)):
        hits = np.where( tdm[a_index,:] < delta)[0]
        N = len(hits)
        if N == 0:
            continue
        t = (tB[hits].sum() + tA[a_index]) / (1+N)
        list_of_averages.append(t)

    for b_index in range(len(tB)):
        hits = np.where( tdm[:,b_index] < delta)[0]
        N = len(hits)
        if N == 0:
            continue
        t = (tA[hits].sum() + tB[b_index]) / (1+N)
        list_of_averages.append(t)

    return np.array(list_of_averages)

def a(svc_a, svc_b, start, stop, delta):
    A = svc_a.from_until(start,stop)
    B = svc_b.from_until(start,stop)

    tdm = tools.make_time_distance_matrix(A, B) *24*3600 # in seconds
    delta=10 # seconds
    
    tt = tools.create_time_averages_from_time_distance_matrix(tdm,A,B,delta)
    
    ttt = tools.common_times_to_be_evaluated(A,B,tt)
    Bi = tools.interpolator(B, ttt)
    Ai = tools.interpolator(A, ttt)

    return Ai, Bi

def datestr_to_facttime(str):
    return calendar.timegm(time.strptime(str,"%Y%m%d %H:%M")) / (24.*3600.)


def facttime_to_datestr(t):
    tup = time.gmtime(t*24*3600)
    return time.strftime("%Y%m%d %H:%M", tup)