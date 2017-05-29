from os import path
import pandas as pd
import json
import h5py
import sys
import logging
import numpy as np
from copy import copy


__all__ = [
    'write_data',
    'to_native_byteorder',
    'read_data',
    'read_h5py',
    'read_h5py_chunked',
    'check_extension',
    'to_h5py',
]

log = logging.getLogger(__name__)


allowed_extensions = ('.hdf', '.hdf5', '.h5', '.json', '.jsonl', '.jsonlines', '.csv')
native_byteorder = native_byteorder = {'little': '<', 'big': '>'}[sys.byteorder]


def write_data(df, file_path, key='data', use_hp5y=False, **kwargs):

    name, extension = path.splitext(file_path)

    if extension in ['.hdf', '.hdf5', '.h5']:
        if use_hp5y is True:
            to_h5py(file_path, df, key=key, **kwargs)
        else:
            df.to_hdf(file_path, key=key, **kwargs)

    elif extension == '.json':
        df.to_json(file_path, **kwargs)

    elif extension in ('.jsonl', '.jsonline'):
        df.to_json(file_path, lines=True, orient='records', **kwargs)

    elif extension == '.csv':
        index = kwargs.pop('index', False)
        df.to_csv(file_path, index=index, **kwargs)

    else:
        raise IOError(
            'cannot write tabular data with format {}. Allowed formats: {}'.format(
                extension, allowed_extensions,
            )
        )


def to_native_byteorder(array):
    ''' Convert numpy array to native byteorder '''

    # '|' : not-applicable, '=': native
    if array.dtype.byteorder not in ('|', '=', native_byteorder):
        return array.byteswap().newbyteorder()

    return array


def read_h5py(file_path, key='data', columns=None, mode='r+'):
    '''
    Read a hdf5 file written with h5py into a dataframe

    Parameters
    ----------
    file_path: str
        file to read in
    key: str
        name of the hdf5 group to read in
    columns: iterable[str]
        Names of the datasets to read in. If not given read all 1d datasets
    '''
    with h5py.File(file_path, mode) as f:
        group = f.get(key)
        if group is None:
            raise IOError('File does not contain group "{}"'.format(key))

        # get all columns of which don't have more than one value per row
        if columns is None:
            columns = [col for col in group.keys() if group[col].ndim == 1]
        else:
            columns = copy(columns)

        df = pd.DataFrame()
        for col in columns:
            array = to_native_byteorder(group[col][:])

            # pandas cannot handle bytes, convert to str
            if array.dtype.kind == 'S':
                array = array.astype(str)

            if array.ndim == 1:
                df[col] = array
            elif array.ndim == 2:
                for i in range(array.shape[1]):
                    df[col + '_{}'.format(i)] = array[:, i]
            else:
                log.warning('Skipping column {}, not 1d or 2d'.format(col))

        if 'index' in df.columns:
            df.set_index('index', inplace=True)

    return df


def h5py_get_n_rows(file_path, key='data', mode='r+'):

    with h5py.File(file_path, mode) as f:
        group = f.get(key)

        if group is None:
            raise IOError('File does not contain group "{}"'.format(key))

        return group[next(iter(group.keys()))].shape[0]


def read_h5py_chunked(file_path, key='data', columns=None, chunksize=None, mode='r+'):
    '''
    Generator function to read from h5py hdf5 in chunks,
    returns an iterator over pandas dataframes.

    When chunksize is None, use 1 chunk
    '''
    with h5py.File(file_path, mode) as f:
        group = f.get(key)
        if group is None:
            raise IOError('File does not contain group "{}"'.format(key))

        # get all columns of which don't have more than one value per row
        if columns is None:
            columns = [col for col in group.keys() if group[col].ndim == 1]
        else:
            columns = copy(columns)

        n_rows = h5py_get_n_rows(file_path, key=key)

        if chunksize is None:
            n_chunks = 1
            chunksize = n_rows
        else:
            n_chunks = int(np.ceil(n_rows / chunksize))
            log.info('Splitting data into {} chunks'.format(n_chunks))

        for col in copy(columns):
            if group[col].ndim > 2:
                columns.remove(col)
                log.warning('Ignoring column {}, not 1d or 2d'.format(col))

        for chunk in range(n_chunks):

            start = chunk * chunksize
            end = min(n_rows, (chunk + 1) * chunksize)

            df = pd.DataFrame(index=np.arange(start, end))

            for col in columns:
                array = to_native_byteorder(group[col][start:end])

                # pandas cannot handle bytes, convert to str
                if array.dtype.kind == 'S':
                    array = array.astype(str)

                if array.ndim == 1:
                    df[col] = array

                else:
                    for i in range(array.shape[1]):
                        df[col + '_{}'.format(i)] = array[:, i]

            yield df, start, end


def read_data(file_path, **kwargs):
    '''
    This is a utility wrapper for other reading functions.
    It will look for the file extension and try to use the correct
    reader and return a dataframe.

    Currently supported are hdf5 (pandas and h5py), json, jsonlines and csv

    Parameters
    ----------
    file_path: str
        Path to the input file

    All kwargs are passed to the individual reading function:

    pandas hdf5:   pd.read_hdf
    h5py hdf5:     fact.io.read_h5py
    json:          pd.DataFrame(json.load(file))
    jsonlines:     pd.read_json
    csv:           pd.read_csv
    '''
    name, extension = path.splitext(file_path)

    if extension in ['.hdf', '.hdf5', '.h5']:
        try:
            df = pd.read_hdf(file_path, **kwargs)
        except (TypeError, ValueError):
            df = read_h5py(file_path, **kwargs)

    elif extension == '.json':
        with open(file_path, 'r') as j:
            d = json.load(j)
            df = pd.DataFrame(d)

    elif extension in ('.jsonl', '.jsonlines'):
        df = pd.read_json(file_path, lines=True, **kwargs)

    elif extension == '.csv':
        df = pd.read_csv(file_path, **kwargs)

    else:
        raise NotImplementedError('Unknown data file extension {}'.format(extension))

    return df


def check_extension(file_path, allowed_extensions=allowed_extensions):
    p, extension = path.splitext(file_path)
    if extension not in allowed_extensions:
        raise IOError('Allowed formats: {}'.format(allowed_extensions))


def to_h5py(filename, df, key='data', mode='a', dtypes=None, index=True, **kwargs):
    '''
    Write pandas dataframe to h5py style hdf5 file

    Parameters
    ----------
    filename: str
        output file name
    df: pd.DataFrame
        The data to write out
    key: str
        the name for the hdf5 group to hold all datasets, default: data
    mode: str
        'w' to overwrite existing files, 'a' to append
    dtypes: dict
        if given, a mapping of column names to dtypes for conversion.
    index: bool
        If bool, also save the index of the dataframe

    All `**kwargs` are passed to h5py.create_dataset
    '''
    assert mode in ('w', 'a'), 'mode has to be either "a" or "w"'

    array = df.to_records(index=index)

    if dtypes is not None:
        array = change_recarray_dtype(array, dtypes)

    with h5py.File(filename, mode=mode) as f:
        if key not in f:
            initialize_h5py(f, array.dtype, key=key, **kwargs)

        append_to_h5py(f, array, key=key)


def change_recarray_dtype(array, dtypes):
    '''
    Change dtypes of recarray columns

    Parameters
    ----------
    array: np.recarray
      The array to modify
    dtypes: dict
        if given, a mapping of column names to dtypes for conversion.

    Returns
    -------
    array: np.recarray
        Copy of the original array with changed dtypes
    '''

    # get a modifieabale list of dtypes
    dt = array.dtype.descr
    # create a mapping from column name to index
    idx = {k: i for i, (k, d) in enumerate(dt)}

    for col, new_type in dtypes.items():
        dt[idx[col]] = (col, new_type)

    dt = np.dtype(dt)

    return array.astype(dt)


def initialize_h5py(f, dtypes, key='events', **kwargs):
    '''
    Create a group with name `key` and empty datasets for each
    entry in dtypes.

    Parameters
    ----------
    f: h5py.File
        the hdf5 file, opened either in write or append mode
    dtypes: numpy.dtype
        the numpy dtype object of a record or structured array describing
        the columns
    key: str
        the name for the hdf5 group to hold all datasets, default: data

    All kwargs are passed to h5py create_dataset
    '''
    group = f.create_group(key)

    for name in dtypes.names:
        dtype = dtypes[name]
        maxshape = [None] + list(dtype.shape)
        shape = [0] + list(dtype.shape)

        if dtype.base == object:
            dt = h5py.special_dtype(vlen=str)

        elif dtype.type == np.datetime64:
            # save dates as ISO string, create dummy date to get correct length
            dt = np.array(0, dtype=dtype).astype('S').dtype

        else:
            dt = dtype.base

        group.create_dataset(
            name,
            shape=tuple(shape),
            maxshape=tuple(maxshape),
            dtype=dt,
            **kwargs
        )

    return group


def append_to_h5py(f, array, key='events'):
    '''
    Append a numpy record or structured array to the given hdf5 file
    The file should have been previously initialized with initialize_hdf5

    Parameters
    ----------
    f: h5py.File
        the hdf5 file, opened either in write or append mode
    array: numpy.array or numpy.recarray
        the numpy array to append
    key: str
        the name for the hdf5 group with the corresponding data sets
    '''

    group = f.get(key)

    for column in array.dtype.names:
        dataset = group.get(column)

        n_existing_rows = dataset.shape[0]
        n_new_rows = array[column].shape[0]

        dataset.resize(n_existing_rows + n_new_rows, axis=0)

        # swap byteorder if not native
        if array[column].dtype.byteorder not in ('=', native_byteorder, '|'):
            data = array[column].newbyteorder().byteswap()
        else:
            data = array[column]

        if data.dtype.type == np.datetime64:
            data = data.astype('S')

        if data.ndim == 1:
            dataset[n_existing_rows:] = data

        elif data.ndim == 2:
            dataset[n_existing_rows:, :] = data

        else:
            raise NotImplementedError('Only 1d and 2d arrays are supported at this point')
