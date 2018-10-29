from . import plotting
from . import auxservices
from pkg_resources import resource_string

__version__ = resource_string('fact', 'VERSION').decode().strip()


__all__ = [
    'plotting',
    'auxservices',
]
