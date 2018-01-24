from functools import lru_cache
from configparser import SafeConfigParser
from getpass import getpass
from simplecrypt import decrypt
from io import StringIO
from pkg_resources import resource_stream
from sqlalchemy import create_engine
import socket
import os


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
    if 'FACT_PASSWORD' in os.environ:
        passwd = os.environ['FACT_PASSWORD']
    else:
        passwd = getpass('Please enter the current, universal FACT password: ')

    with resource_stream('fact', 'credentials/credentials.encrypted') as f:
        decrypted = decrypt(passwd, f.read()).decode('utf-8')

    config = SafeConfigParser()
    config.readfp(StringIO(decrypted))

    return config


def create_factdb_engine(database=None):
    '''
    returns a sqlalchemy.Engine pointing to the factdata database

    The different hostname on isdc machines is handled correctly.
    '''
    spec = 'mysql+pymysql://{user}:{password}@{host}/{database}'

    creds = get_credentials()
    config = dict(creds['database'])

    if socket.gethostname().startswith('isdc'):
        config['host'] = 'lp-fact'

    if database is not None:
        config['database'] = database

    return create_engine(
        spec.format(**config),
        connect_args={'ssl': {'ssl-mode': 'preferred'}},
    )
