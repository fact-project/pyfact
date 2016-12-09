import pandas as pd
import peewee
from .models import RunInfo, Source, RunType
from ..credentials import create_factdb_engine


def get_ontime_by_source_and_runtype(engine=None):
    query, params = (
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
        .sql()
    )
    df = pd.read_sql(query, engine or create_factdb_engine(), params=params)
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

    query, params = query.group_by(Source.fsourcename).sql()
    df = pd.read_sql(query, engine or create_factdb_engine(), params=params)
    df.set_index('source', inplace=True)

    return df
