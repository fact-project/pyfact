import os.path
import re

__all__ = [
    'parse'
    'run2tree_path',
    'TemplateToPath',
    'TreePath',
]


class TemplateToPath:
    '''Turn a template like '/fac/raw/{Y}/{M}/{D}/{N}_{R}.fits.fz' into a path.
    '''

    def __init__(self, template):
        self.template = template

    def __call__(self, night, run=None, **kwargs):
        d = dict(**kwargs)

        if hasattr(night, 'fNight') and hasattr(night, 'fRunID'):
            night, run = night.fNight, night.fRunID

        night = str(night)
        if run is not None:
            d['R'] = '{:03d}'.format(int(run))

        d['N'] = night
        d['Y'] = night[0:4]
        d['M'] = night[4:6]
        d['D'] = night[6:8]
        return self.template.format(**d)


def run2tree_path(base_dir, suffix, night, run=None):
    '''Make a tree_path from a run

    base_dir:  eg. '/fact/raw' or '/fact/aux'
    suffix:    eg. '.fits.fz' or '.log' or '.AUX_FOO.fits'
    night:     eg. 20160101 or '20160101' (int or string accepted)
    run:       eg. 11 or '011' or None (int, string or None accepted)

    output:
    eg. '/fact/raw/2016/01/01/20160101_011.fits.fz' or
    '/fact/raw/2016/01/01/20160101.log'

    '''
    if run is not None:
        base_name = '{N}_{R}'
    else:
        base_name = '{N}'

    template = os.path.join(
            base_dir,
            '{Y}',
            '{M}',
            '{D}',
            base_name + suffix)
    return TemplateToPath(template)(night, run)


class TreePath:
    '''Convenience class for run2tree_path() for people who don't like partials
    '''
    def __init__(self, base_dir, suffix):
        self.base_dir = base_dir
        self.suffix = suffix

    def __call__(self, night, run=None):
        return run2tree_path(self.base_dir, self.suffix, night, run)

path_regex = re.compile(
    r'(?P<prefix>.*?)' +
    r'((/\d{4})(/\d{2})(/\d{2}))?/' +
    r'(?P<night>\d{8})' +
    r'(_?(?P<run>\d{3}))?' +
    r'(?P<suffix>.*)'
)


def parse(path):
    '''return a dict with relevant parts of the path
    for input paths like these:
     '/fact/raw/2016/01/01/20160101_011.fits.fz',
     '/fact/aux/2016/01/01/20160101.FSC_CONTROL_TEMPERATURE.fits',
     '/fact/aux/2016/01/01/20160101.log',
     '/home/guest/tbretz/gainanalysis.20130725/files/fit_bt2b/20140115_079_079.root'

    it returns dicts like these:

    {'prefix': '/fact/raw',
     'night': 20160101,
     'run': 011,
     'suffix': '.fits.fz'}
    {'prefix': '/fact/aux',
     'night': 20160101,
     'run': None,
     'suffix': '.FSC_CONTROL_TEMPERATURE.fits'}
    {'prefix': '/fact/aux',
     'night': 20160101,
     'run': None,
     'suffix': '.log'}
    {'prefix':
     '/home/guest/tbretz/gainanalysis.20130725/files/fit_bt2b',
     'night': 20140115,
     'run': 079,
     'suffix': '_079.root'}
    '''
    d = path_regex.match(path).groupdict()
    if d['run'] is not None:
        d['run'] = int(d['run'])
    d['night'] = int(d['night'])
    return d
