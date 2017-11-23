# coding: utf-8
import pandas as pd

from joblib import Parallel, delayed
import h5py
import click

from ...coordinates.utils import camera_to_equatorial
from ...io import read_h5py_chunked
from ...io import create_empty_h5py_dataset, append_to_h5py_dataset


def calc_ra_dec(events):
    events['obstime'] = pd.to_datetime(
        events['unix_time_utc_0'] * 1e6 + events['unix_time_utc_1'],
        unit='us',
    )

    events['ra_prediction'], events['dec_prediction'] = camera_to_equatorial(
        events['source_x_prediction'],
        events['source_y_prediction'],
        events['zd_tracking'],
        events['az_tracking'],
        events['obstime'],
    )
    return events


columns = ('ra_prediction', 'dec_prediction')


@click.command()
@click.argument('INPUTFILE', type=click.Path(exists=True, dir_okay=False))
@click.option('-c', '--chunksize', type=int, default=10000)
@click.option('-n', '--n-jobs', type=int, default=-1)
@click.option('-y', '--yes', is_flag=True, help='Do not ask to overwrite existing keys')
def main(inputfile, chunksize, n_jobs, yes):
    '''
    Calculate ra and dec from source position in camera coordinates
    e.g. for example for files analysed with the classifier-tools

    The following keys have to be present in the h5py hdf5 file.
        * az_tracking
        * zd_tracking
        * source_x_prediction
        * source_y_prediction
        * unix_time_utc
    '''

    with h5py.File(inputfile, 'r') as f:
        if any(col in f['events'].keys() for col in columns) and not yes:
            click.confirm('Output keys already exist, overwrite? ', abort=True)

    df_it = read_h5py_chunked(
        inputfile,
        key='events',
        columns=[
            'az_tracking',
            'zd_tracking',
            'source_x_prediction',
            'source_y_prediction',
            'unix_time_utc',
        ],
        chunksize=chunksize
    )
    with Parallel(n_jobs, verbose=10) as pool:

        dfs = pool(
            delayed(calc_ra_dec)(df)
            for df, start, stop in df_it
        )

    df = pd.concat(dfs)

    with h5py.File(inputfile, mode='r+') as f:
        for col in ('ra_prediction', 'dec_prediction'):
            if col in f['events']:
                del f['events'][col]
            create_empty_h5py_dataset(df[col].values, f['events'], col)
            append_to_h5py_dataset(df[col].values, f['events'][col])


if __name__ == '__main__':
    main()
