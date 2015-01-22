""" library of functions for correlating services
"""
import numpy as np
import time 
import calendar
from scipy import interpolate


def common_times_to_be_evaluated(times, services):
    """ crop times for interpolation

    times : 1D array, containting times in FACT format
    services: list of services (having a "Time" field)

    times is cropped such, that times does not contain any time
    ealier than the earliest time in any service, and no time later
    than the latest time in any service.
    """
    maximal_earliest = max([s["Time"][0] for s in services])
    minimal_latest = min([s["Time"][-1] for s in services])
    start, stop = np.searchsorted(times, [maximal_earliest, minimal_latest])
    return times[start:stop]

def interpolator(support, times_to_be_evaluated):
    """
        support : is  a structured array with, "Time" 
                    and a lot of other fields, to be interpolated.

        times_to_be_evaluated : is a 1D array-like holding the times, 
                        where the interpolation should be done
    """
    output_array = np.zeros(len(times_to_be_evaluated), dtype=support.dtype)
    output_array["Time"] = times_to_be_evaluated
    
    field_names = [name for name in support.dtype.names if not "Time" in name]
    for name in field_names:
        output_array[name] = interpolate.interp1d(support["Time"], 
                                support[name], axis=0)(times_to_be_evaluated)
    return output_array


def create_time_averages_from(service_1, service_2, delta):
    """ create "near" times from the "Time" fields in service_1 and service_2

    near times, are time stampfs which are nearer to each other than delta
    each group of times, which is near enough creates one averaged timestamp
    which is simply the average of the intire group of times
    """
    list_of_averages = _make_average_one_direction(service_1["Time"], 
                                                    service_2["Time"], delta)
    list_of_averages += _make_average_one_direction(service_2["Time"], 
                                                    service_1["Time"], delta)
    return list_of_averages

def _make_average_one_direction(time1, time2, delta):
    """ helper for the fucntion above. this one is not easy to explain
        maybe this means it needs refactoring
    """
    list_of_averages = []
    left_indices = np.searchsorted(time1, time2-delta)
    right_indices = np.searchsorted(time1, time2+delta)
    for index_in_2, tup in enumerate(zip(left_indices, right_indices)):
        left, right = tup
        this_time2 = time2[index_in_2]
        list_of_averages.append(
                                    (time1[left:right].sum() + this_time2) 
                                    / 
                                    (1 + len(time1[left:right]))
                                )
    return list_of_averages


def correlate_dom_like(service_1, service_2, limit_in_sec):
    """ make parts of service_1 and service_2 of equal length and timestamps
    """
    if service_1.shape[0] > service_2.shape[0]:
        new_service_1 = shorten_according_to_times(service_1, service_2)
        return apply_limit(new_service_1, service_2, limit_in_sec)
    else:
        new_service_2 = shorten_according_to_times(service_2, service_1)
        return apply_limit(service_1, new_service_2, limit_in_sec)
    

def shorten_according_to_times(longer, shorter):
    """ return that part of longer, which corresponds to best to shorter
    """
    t_short = shorter['Time']
    t_long = longer['Time']
    indices_in_longer = np.searchsorted(a=t_long, v=t_short)
    a_bit_smaller = t_long.take(indices_in_longer-1, mode='clip')
    a_bit_larger = t_long.take(indices_in_longer, mode='clip')
    indices_nearest = np.where((t_short-a_bit_smaller) 
                                  < (a_bit_larger-t_short),
                                   indices_in_longer-1, 
                                   indices_in_longer)
    return longer.take(indices_nearest, mode='clip')

def apply_limit(service_1, service_2, limit_in_sec):
    """ crop services of equal length, according to timestamps
    """
    time1 = service_1['Time'] * 24 * 3600
    time2 = service_2['Time'] * 24 * 3600
    good = np.abs(time1-time2) < limit_in_sec
    return service_1[good], service_2[good]
