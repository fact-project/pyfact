# coding: utf-8
import pandas as pd
from fact.analysis import calc_theta_camera, calc_theta_offs_camera
from fact.io import read_h5py_chunked
from fact.io import create_empty_h5py_dataset, append_to_h5py_dataset
from fact.coordinates.utils import array_to_time
from fact.instrument.constants import LOCATION
from astropy.coordinates import SkyCoord, AltAz
from joblib import Parallel, delayed
import h5py
import click


def calc_theta_source(df, source):

    obstime = array_to_time(pd.to_datetime(
        df.unix_time_utc_0 * 1e6 + df.unix_time_utc_1, unit='us'
    ))

    altaz = AltAz(location=LOCATION, obstime=obstime)
    source_altaz = source.transform_to(altaz)

    df['theta_deg'] = calc_theta_camera(
        df.source_x_prediction,
        df.source_y_prediction,
        source_altaz.zen.deg,
        source_altaz.az.deg,
        zd_pointing=df.zd_tracking,
        az_pointing=df.az_tracking,
    )
    theta_offs = calc_theta_offs_camera(
        df.source_x_prediction,
        df.source_y_prediction,
        source_altaz.zen.deg,
        source_altaz.az.deg,
        zd_pointing=df.zd_tracking,
        az_pointing=df.az_tracking,
        n_off=5,
    )

    for i, theta_off in enumerate(theta_offs, start=1):
        df['theta_deg_off_{}'.format(i)] = theta_off

    return df


def calc_theta_coordinates(df):

    df['theta_deg'] = calc_theta_camera(
        df.source_x_prediction,
        df.source_y_prediction,
        df.zd_source_calc,
        df.az_source_calc,
        zd_pointing=df.zd_tracking,
        az_pointing=df.az_tracking,
    )
    theta_offs = calc_theta_offs_camera(
        df.source_x_prediction,
        df.source_y_prediction,
        df.zd_source_calc,
        df.az_source_calc,
        zd_pointing=df.zd_tracking,
        az_pointing=df.az_tracking,
        n_off=5,
    )

    for i, theta_off in enumerate(theta_offs, start=1):
        df['theta_deg_off_{}'.format(i)] = theta_off

    return df


cols = [
    'theta_deg' if i == 0 else 'theta_deg_off_{}'.format(i)
    for i in range(6)
]


@click.command()
@click.argument('INPUTFILE')
@click.option(
    '-s', '--source',
    help='Source name, if not given, take `az_source_calc`, and `zd_source_calc`'
)
@click.option('-c', '--chunksize', type=int, default=10000)
@click.option('-y', '--yes', is_flag=True, help='Do not ask to overwrite existing keys')
def main(inputfile, source, chunksize, yes):
    '''
    Calculate theta_deg and theta_deg_offs from source position in camera coordinates
    e.g. for example for files analysed with the classifier-tools

    The following keys have to be present in the h5py hdf5 file.
        * az_tracking
        * zd_tracking
        * source_x_prediction
        * source_y_prediction
        * unix_time_utc (Only if a source name is given)
    '''

    with h5py.File(inputfile, 'r') as f:
        if any(col in f['events'].keys() for col in cols) and not yes:
            click.confirm('Output keys already exist, overwrite? ', abort=True)

    if source is None:
        df_it = read_h5py_chunked(
            inputfile,
            key='events',
            columns=[
                'az_tracking',
                'zd_tracking',
                'source_x_prediction',
                'source_y_prediction',
                'az_source_calc',
                'zd_source_calc',
            ],
            chunksize=chunksize
        )
        with Parallel(-1, verbose=10) as pool:

            dfs = pool(
                delayed(calc_theta_coordinates)(df)
                for df, start, stop in df_it
            )
    else:
        crab = SkyCoord.from_name(source)

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

        with Parallel(-1, verbose=10) as pool:

            dfs = pool(
                delayed(calc_theta_source)(df, crab)
                for df, start, stop in df_it
            )

    df = pd.concat(dfs)

    with h5py.File(inputfile, mode='r+') as f:
        for i in range(6):
            if i == 0:
                col = 'theta_deg'
            else:
                col = 'theta_deg_off_{}'.format(i)

            if col in f['events']:
                del f['events'][col]
            create_empty_h5py_dataset(df[col].values, f['events'], col)
            append_to_h5py_dataset(df[col].values, f['events'][col])


if __name__ == '__main__':
    main()
