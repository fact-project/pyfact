''' library of functions for correlating services
'''
import numpy as np
from scipy import interpolate


def interpolator(support, times_to_be_evaluated):
    '''
        support : is  a structured array with, 'Time'
                    and a lot of other fields, to be interpolated.

        times_to_be_evaluated : is a 1D array-like holding the times,
                        where the interpolation should be done
    '''
    output_array = np.zeros(len(times_to_be_evaluated), dtype=support.dtype)
    output_array['Time'] = times_to_be_evaluated

    field_names = [name for name in support.dtype.names if 'Time' not in name]
    for name in field_names:
        output_array[name] = interpolate.interp1d(
            support['Time'],
            support[name], axis=0
        )(times_to_be_evaluated)
    return output_array


class CorrelationByInterpolation(object):

    def __init__(self, service_1, service_2, delta_in_seconds):
        self.service_1 = service_1
        self.service_2 = service_2
        self.delta_in_seconds = delta_in_seconds
        self.services = [service_1, service_2]

    def correlate(self):
        ''' correlate by interpolation
        '''
        averaged_times = self.__create_average_times()
        common_averaged_times = self.__common_times(averaged_times)
        new_service_2 = interpolator(self.service_2, common_averaged_times)
        new_service_1 = interpolator(self.service_1, common_averaged_times)
        return new_service_1, new_service_2

    def __common_times(self, averaged_times):
        ''' crop times for interpolation

        times : 1D array, containting times in FACT format
        services: list of services (having a 'Time' field)

        times is cropped such, that times does not contain any time
        ealier than the earliest time in any service, and no time later
        than the latest time in any service.
        '''
        maximal_earliest = max([s['Time'][0] for s in self.services])
        minimal_latest = min([s['Time'][-1] for s in self.services])
        start, stop = np.searchsorted(
            averaged_times,
            [maximal_earliest, minimal_latest])
        return averaged_times[start:stop]

    def __create_average_times(self):
        ''' create 'near' times from the 'Time' fields self.services

        near times, are time stampfs which are nearer to each other than delta
        each group of times, which is near enough creates one averaged timestamp
        which is simply the average of the intire group of times
        '''

        list_of_averages = self.__make_average_bad_name(
            self.service_1['Time'],
            self.service_2['Time'])
        list_of_averages += self.__make_average_bad_name(
            self.service_2['Time'],
            self.service_1['Time'])
        return np.array(list_of_averages)

    def __make_average_bad_name(self, time1, time2):
        ''' helper for the fucntion above. this one is not easy to explain
            maybe this means it needs refactoring
        '''
        # convert times to seconds
        time1 *= 24 * 3600
        time2 *= 24 * 3600
        list_of_averages = []
        left_indices = np.searchsorted(
            time1,
            time2 - self.delta_in_seconds)
        right_indices = np.searchsorted(
            time1,
            time2 + self.delta_in_seconds)

        for index_in_2, tup in enumerate(zip(left_indices, right_indices)):
            left, right = tup
            this_time2 = time2[index_in_2]
            list_of_averages.append(
                (time1[left:right].sum() + this_time2) / (1 + len(time1[left:right]))
            )
        return list_of_averages


class CorrelationByIdentification(object):

    def __init__(self, service_1, service_2, delta_in_seconds):
        if service_1.shape[0] > service_2.shape[0]:
            self.longer = service_1
            self.shorter = service_2
            self.__long_1_short_2 = True
        else:
            self.longer = service_2
            self.shorter = service_1
            self.__long_1_short_2 = False

        self.delta_in_seconds = delta_in_seconds

        # a version of self.longer, which contains as many rows
        # as self.shorter, the timestamps in new_longer are as close to those
        # in self.shorter as possible
        self.__new_longer = None

    def correlate(self):
        ''' make parts of service_1 and service_2 of equal length and timestamps
        '''
        self.__new_longer = self.__identify()
        self.__cut_for_delta()
        return

    def __identify(self):
        ''' return that part of longer, which corresponds to best to shorter
        '''
        t_short = self.shorter['Time']
        t_long = self.longer['Time']
        indices_in_longer = np.searchsorted(a=t_long, v=t_short)
        a_bit_smaller = t_long.take(indices_in_longer - 1, mode='clip')
        a_bit_larger = t_long.take(indices_in_longer, mode='clip')
        indices_nearest = np.where(
            (t_short - a_bit_smaller) < (a_bit_larger - t_short),
            indices_in_longer - 1, indices_in_longer
        )
        return self.longer.take(indices_nearest, mode='clip')

    def __cut_for_delta(self):
        ''' crop services of equal length, according to timestamps
        '''
        time1 = self.shorter['Time'] * 24 * 3600
        time2 = self.__new_longer['Time'] * 24 * 3600
        good = np.abs(time1 - time2) < self.delta_in_seconds

        if self.__long_1_short_2:
            return self.__new_longer[good], self.shorter[good]
        else:
            return self.shorter[good], self.__new_longer[good]
