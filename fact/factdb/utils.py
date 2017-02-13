import pandas as pd
import peewee
from .models import RunInfo, Source, RunType
from ..credentials import create_factdb_engine


def read_into_dataframe(query, engine=None):
    ''' read the result of a peewee query object into a pandas DataFrame '''

    sql, params = query.sql()
    df = pd.read_sql_query(sql, engine or create_factdb_engine(), params=params)

    return df


def get_ontime_by_source_and_runtype(engine=None):
    query = (
        RunInfo
        .select(
            peewee.fn.SUM(RunInfo.fontime).alias('ontime'),
            Source.fsourcename.alias('source'),
            RunType.fruntypename.alias('runtype')
        )
        .join(Source, on=Source.fsourcekey == RunInfo.fsourcekey)
        .switch(RunInfo)
        .join(RunType, on=RunType.fruntypekey == RunInfo.fruntypekey)
        .group_by(Source.fsourcename, RunType.fruntypename)
    )
    df = read_into_dataframe(query, engine or create_factdb_engine())
    df.set_index(['source', 'runtype'], inplace=True)

    return df


def get_ontime_by_source(runtype=None, engine=None):
    query = (
        RunInfo
        .select(
            peewee.fn.SUM(RunInfo.fontime).alias('ontime'),
            Source.fsourcename.alias('source'),
        )
        .join(Source, on=Source.fsourcekey == RunInfo.fsourcekey)
        .switch(RunInfo)
        .join(RunType, on=RunType.fruntypekey == RunInfo.fruntypekey)
    )
    if runtype is not None:
        query = query.where(RunType.fruntypename == runtype)

    query = query.group_by(Source.fsourcename)

    df = read_into_dataframe(query, engine or create_factdb_engine())
    df.set_index('source', inplace=True)

    return df
