import types

def dim_service(fn):
    """
    A decorator function that makes easier to use normal functions as callbacks
    for DIM services.

    'fn' is a function (in general, a callable object) that doesn't
    receive arguments, and returns a function that is suited for DIM callbacks.
    """
    def svc(tag):
        # Tag argument is declared but not used
        rtn = fn()
        # The returned value must be tuple, so we try to convert simple values
        if rtn not in (types.ListType, types.TupleType):
            rtn = (rtn,)
        return rtn

    return svc


def dim_service_tag(fn):
    """
    A decorator function that makes easier to use function with an argument as
    callbacks for DIM services.

    'fn' is a function (in general, a callable object) that receives one
    argument, and returns a function that is suited for DIM callbacks. The
    argument used is the tag of the service tag registerd with DIM.
    """
    def svc(tag):
        rtn = fn(tag)
        if rtn not in (types.ListType, types.TupleType):
            rtn = (rtn,)
        return rtn

    return svc
