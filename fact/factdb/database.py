from peewee import MySQLDatabase
import wrapt
from ..credentials import get_credentials

factdata_db = MySQLDatabase(None)


def connect_database(config=None):
    if config is None:
        config = get_credentials()['database']
    factdata_db.init(**config)
    factdata_db.connect()
