import os.path
import re

__all__ = [
    'parse'
    'template_to_path',
    'tree_path',
]


def template_to_path(template, night, run=None, **kwargs):
    '''Turn a template like '/fac/raw/{Y}/{M}/{D}/{N}_{R}.fits.fz' into a path.
    '''
    night = str(night)
    if run is not None:
        kwargs['R'] = '{:03d}'.format(int(run))

    kwargs['N'] = night
    kwargs['Y'] = night[0:4]
    kwargs['M'] = night[4:6]
    kwargs['D'] = night[6:8]
    return template.format(**kwargs)


def tree_path(base_dir, suffix, night, run=None):
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
    return template_to_path(template, night, run=None)


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
