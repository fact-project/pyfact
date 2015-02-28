"""
PyDIM is a Python interface to DIM.

PyDIM could be used to create DIM clients and servers, using an API very similar
to the one that is used for C.
"""

_version = '1.3.4'

from .rpcproxy import RpcProxy
from .sync_calls import dic_sync_info_service, dic_sync_cmnd_service
from .helpers import dim_service, dim_service_tag
from .dimc import *
from .dim_servers import Dns
