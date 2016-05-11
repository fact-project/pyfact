from functools import lru_cache
try:
    from configparser import SafeConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser
from getpass import getpass
from simplecrypt import decrypt
from io import StringIO
from pkg_resources import resource_stream
from sqlalchemy import create_engine
import socket


__all__ = ['get_credentials', 'create_factdb_engine']


@lru_cache(1)
def get_credentials():
    '''
    Get a SafeConfigParser instance with FACT credentials
    On the first call, you will be prompted for the FACT password

    The folling credentials are stored:
    - telegram
        - token

    - database
        - user
        - password
        - host
        - database

    - twilio
        - sid
        - auth_token
        - number

    use get_credentials().get(group, element) to retrieve elements
    '''
    with resource_stream('fact', 'credentials/credentials.encrypted') as f:
        print('Please enter the current, universal FACT password')
        passwd = getpass()
        decrypted = decrypt(passwd, f.read()).decode('utf-8')

    config = SafeConfigParser()
    config.readfp(StringIO(decrypted))

    return config


def create_factdb_engine():
    '''
    returns a sqlalchemy.Engine pointing to the factdata database

    The different hostname on isdc machines is handled correctly.
    '''
    creds = get_credentials()

    if socket.gethostname().startswith('isdc'):
        spec = 'mysql+pymysql://{user}:{password}@lp-fact/{database}'
    else:
        spec = 'mysql+pymysql://{user}:{password}@{host}/{database}'

    return create_engine(spec.format(**creds['database']))
