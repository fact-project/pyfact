import pandas as pd
import peewee
from .models import RunInfo, Source, RunType
from .database import factdata_db, connect_database


def get_ontime_by_source_and_runtype(config=None):
    if factdata_db.is_closed():
        connect_database(config=config)
    df = pd.DataFrame(list(
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
        .dicts()
        .naive()  # put selected foreign key attributes directly into the objects
    ))
    df.set_index(['source', 'runtype'], inplace=True)

    return df


def get_ontime_by_source(runtype=None, config=None):
    if factdata_db.is_closed():
        connect_database(config=config)
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

    query = (
        query
        .group_by(Source.fsourcename)
        .dicts()
        .naive()  # put selected foreign key attributes directly into the objects
    )
    df = pd.DataFrame(list(query))
    df.set_index('source', inplace=True)

    return df
