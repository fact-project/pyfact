import random
import threading

from .dimc import dic_info_service, ONCE_ONLY, dic_release_service, dic_cmnd_callback


def dic_sync_info_service(name, description, timeout=None, default_value=None):
    """
    A synchronous call for getting the value of a service.

    This function is equivalent to `dic_info_service`, but it waits until the
    value is retrieved and returns the value of the service. For this reason a
    callback function is not needed.

    Arguments are:

       *name* Service name. same name used by server when declaring the service.

       *description* The description string of the service.

       *timeout* The number of seconds after which the service is considered to
        have failed. Optional, by default there is no timeout.

       *default_value* The value that will be returned in case the service
        doesn't succeed. Optional, default is `None`.
    """
    executed = threading.Event()
    state = dict(value=None)

    def create_callback(st):
        def _callback(*args):
            st['value'] = args
            executed.set()

        return _callback

    callback = create_callback(state)
    dim_timeout = 0
    tag = random.randint(0, 100000)
    sid = dic_info_service(
        name,
        description,
        callback,
        ONCE_ONLY,
        dim_timeout,
        tag,
        default_value
    )

    executed.wait(timeout)

    dic_release_service(sid)

    return state['value']


def dic_sync_cmnd_service(name, arguments, description, timeout=None):
    """
    A synchronous call for executing a command.

    This function works in the same way as `dic_cmnd_service`, but it waits
    until the command is executed.

    Arguments are:

       *name* Command name, same name used by server when declaring the command
       service.

       *arguments* A tuple with the values that are sent to the command as
       arguments.

       *description* The description string of the command.

       *timeout* The number of seconds after which the command is considered
       to have failed. Optional, by default there is no timeout.

    It returns an integer which indicates if the command was executed
    successfully; 1 if it was correctly sent to the server, 0 otherwise.

    """
    executed = threading.Event()
    state = dict(retcode=None)

    def create_callback(st):
        def _callback(tag, retcode):
            state['retcode'] = retcode
            executed.set()

        return _callback

    callback = create_callback(state)
    tag = 0
    dic_cmnd_callback(name, arguments, description, callback, tag)

    executed.wait(timeout)

    return state['retcode']
