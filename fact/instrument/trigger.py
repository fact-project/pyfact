'''
The varoius trigger types of the FACT camera.

For a full overview of the FACT trigger types, see the 
[Phd of Patrick Vogler, table 4.3.b, page 93]
(http://e-collection.library.ethz.ch/eserv/eth:48381/eth-48381-02.pdf)

The trigger type IDs also encode the N-out-of-4 trigger patten logic, but here 
are only trigger type IDs for N=1 as it is the most common.
'''

#: Self triggered, these events are likely to contain photon clusters.
PHYSICS = 4
#: These events are likely to contain only night sky background photons.
PEDESTAL = 1024
#: The external light pulser which is located in the center of the reflector 
#: dish.
LIGHT_PULSER_EXTERNAL = 260
#: The internal lightpulser was deactivated in May 2014.
LIGHT_PULSER_INTERNAL = 512
#: Not sure, seems to be for the DRS4 time calibration.
TIME_CALIBRATION = 33792
#: These events are likely to contain only night sky background photons.
#: Here the GPS module is used as reference clock.  The GPS is sometimes 
#: connected to EXT1 and sometimes to EXT2.
EXT1 = 1
#: See EXT1.
EXT2 = 2