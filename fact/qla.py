import numpy as np

from .factdb import (
    read_into_dataframe,
    AnalysisResultsRunLP as QLA,
    RunInfo,
    Source
)


def get_qla_data(
        first_night=None,
        last_night=None,
        sources=None,
        database_engine=None
        ):
    '''
    Request QLA results from our database

    first_night: int or None
        If given, first night to query as FACT night integer.
    last_night: int or None
        If given, last night to query as FACT night integer.
    sources: iterable[str]
        If given, only these sources will be requested.
        Names have to match Source.fSourceName in our db.
    database_engine: sqlalchmey.Engine
        If given, the connection to use for the query.
        Else, `fact.credentials.create_factdb_engine` will be used to create it.
    '''

    query = QLA.select(
        QLA.frunid.alias('run_id'),
        QLA.fnight.alias('night'),
        QLA.fnumexcevts.alias('n_excess'),
        QLA.fnumsigevts.alias('n_on'),
        (QLA.fnumbgevts * 5).alias('n_off'),
        QLA.fontimeaftercuts.alias('ontime'),
        RunInfo.frunstart.alias('run_start'),
        RunInfo.frunstop.alias('run_stop'),
        Source.fsourcename.alias('source'),
        Source.fsourcekey.alias('source_key'),
    )

    on = (RunInfo.fnight == QLA.fnight) & (RunInfo.frunid == QLA.frunid)
    query = query.join(RunInfo, on=on)
    query = query.join(Source, on=RunInfo.fsourcekey == Source.fsourcekey)

    if first_night is not None:
        query = query.where(QLA.fnight >= first_night)
    if last_night is not None:
        query = query.where(QLA.fnight <= last_night)

    if sources is not None:
        query = query.where(Source.fsourcename.in_(sources))

    runs = read_into_dataframe(query, engine=database_engine)

    # drop rows with NaNs from the table, these are unfinished qla results
    runs.dropna(inplace=True)

    runs.sort_values('run_start', inplace=True)

    return runs
