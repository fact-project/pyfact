#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
An example for showing clients for DIM servers.

The client will query the values from the two services created in
`service-server.py`, thus it should be run along with that script.

"""

import sys
import time

# Import the pydim module
import fact.dim as pydim


def client_callback1(now):
    """
    Callback function for the service 1.

    Callback functions receive as many arguments as values are returned by the
    service. For example, as the service 1 returns only one string this callback
    function has only one argument. 

    """
    print "Client callback function for service 1"
    print "Message received: '%s' (%s)" % (now, type(now))


def client_callback2(val1, val2):
    """
    Callback function for service 2.

    As the service 2 returned two arguments
    """

    print "Client callback function for service 2"
    print "Values received: %s (%s) and %s (%s)" % (val1, type(val1), val2, type(val2))


def main():
    """
    A client for subscribing to two DIM services
    """

    # Again, check if a Dim DNS node has been configured.
    # Normally this is done by setting an environment variable named DIM_DNS_NODE
    # with the host name, e.g. 'localhost'.
    #
    if not pydim.dis_get_dns_node():
        print "No Dim DNS node found. Please set the environment variable DIM_DNS_NODE"
        sys.exit(1)

    # The function `dic_info_service` allows to subscribe to a service.
    # The arguments are the following:
    # 1. The name of the service.
    # 2. Service description string
    # 3. Callback function that will be called when the service is
    #    updated.
    res1 = pydim.dic_info_service("example-service-1", "C", client_callback1)
    res2 = pydim.dic_info_service("example-service-2", "F:1;I:1;", client_callback2)

    if not res1 or not res2:
        print "There was an error registering the clients"
        sys.exit(1)

    # Wait for updates
    while True:
        time.sleep(10)


if __name__ == "__main__":
    main()
