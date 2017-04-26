import pandas as pd
import peewee
from .models import RunInfo, Source, RunType
from ..credentials import create_factdb_engine
from ..time import night_integer


SECOND = peewee.SQL('SECOND')
run_duration = peewee.fn.TIMESTAMPDIFF(
    SECOND, RunInfo.frunstart, RunInfo.frunstop
)
ontime = (run_duration * RunInfo.feffectiveon)


def read_into_dataframe(query, engine=None):
    ''' read the result of a peewee query object into a pandas DataFrame '''
    engine = engine or create_factdb_engine()
    sql, params = query.sql()
    
    with engine.connect() as conn:
        df = pd.read_sql_query(sql, conn, params=params)

    return df


def get_correct_ontime(start=None, end=None, engine=None):
    '''
    The database field fOnTime underestimates the real ontime by about 5 seconds
    because of how the number is calculated from the FTM auxfiles.
    A better estimate can be obtained by taking (fRunStop - fRunStart) * fEffectiveOn.

    Parameters
    ----------
    start : int or datetime.date
        First night to select, either in fact int format or as date
    end : int or datetime.date
        Last night to select, either in fact int format or as date
    engine: sqlalchemy.Engine
        The engine connected to the database.
        If None, fact.credentials.create_factdb_engine will be used to create one.

    Source: D. Neise, A. Biland. Also see github.com/dneise/about_fact_ontime
    '''

    query = RunInfo.select(
        RunInfo.fnight.alias('night'),
        RunInfo.frunid.alias('run_id'),
        RunInfo.frunstart.alias('start'),
        RunInfo.frunstart.alias('stop'),
        ontime.alias('ontime'),
    )

    if start is not None:
        start = night_integer(start) if not isinstance(start, int) else start
        query = query.where(RunInfo.fnight >= start)

    if end is not None:
        end = night_integer(end) if not isinstance(end, int) else end
        query = query.where(RunInfo.fnight <= end)

    df = read_into_dataframe(query, engine=engine)

    return df


def get_ontime_by_source_and_runtype(engine=None):
    query = (
        RunInfo
        .select(
            peewee.fn.SUM(ontime).alias('ontime'),
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
            peewee.fn.SUM(ontime).alias('ontime'),
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
