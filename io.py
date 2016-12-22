from os import path
import pandas as pd
import json
from sklearn_pandas import DataFrameMapper
from sklearn.externals import joblib
from sklearn2pmml import sklearn2pmml
import h5py
import sys
import logging

log = logging.getLogger(__name__)


allowed_extensions = ('.hdf', '.hdf5', '.h5', '.json', '.csv')
native_byteorder = native_byteorder = {'little': '<', 'big': '>'}[sys.byteorder]


def write_data(df, file_path, hdf_key='table'):
    name, extension = path.splitext(file_path)
    if extension in ['.hdf', '.hdf5', '.h5']:
        df.to_hdf(file_path, key=hdf_key)
    elif extension == '.json':
        df.to_json(file_path)
    elif extension == '.csv':
        df.to_csv(file_path, delimiter=',', index=False)
    else:
        raise IOError(
            'cannot write tabular data with format {}. Allowed formats: {}'.format(
                extension, 'hdf5, json, csv'
            )
        )


def read_h5py(file_path, group_name='events', columns=None):
    '''
    Read a hdf5 file written with h5py into a dataframe

    Parameters
    ----------
    file_path: str
        file to read in
    group_name: str
        name of the hdf5 group to read in
    columns: iterable[str]
        Names of the datasets to read in. If not given read all 1d datasets
    '''
    df = pd.DataFrame()

    with h5py.File(file_path) as f:
        group = f.get(group_name)
        # get all columns of which don't have more than one value per row
        if columns is None:
            columns = [col for col in group.keys() if group[col].ndim == 1]

        for col in columns:
            if group[col].dtype.byteorder not in ('=', native_byteorder):
                df[col] = group[col][:].byteswap().newbyteorder()
            else:
                df[col] = group[col]

    return df


def read_pandas_hdf5(file_path, key=None, columns=None):
    df = pd.read_hdf(file_path, key=key, columns=columns)
    return df


def read_data(file_path, query=None, sample=-1, key=None, columns=None):
    name, extension = path.splitext(file_path)

    if extension in ['.hdf', '.hdf5', '.h5']:
        try:
            df = read_pandas_hdf5(file_path, key=key, columns=columns)
        except (TypeError, ValueError):

            df = read_h5py(file_path, columns=columns)

    elif extension == '.json':
        with open(file_path, 'r') as j:
            d = json.load(j)
            df = pd.DataFrame(d)
    else:
        raise NotImplementedError('Unknown data file extension {}'.format(extension))

    if sample > 0:
        print('Taking {} random samples'.format(sample))
        df = df.sample(sample)

    if query:
        print('Quering with string: {}'.format(query))
        df = df.copy().query(query)

    return df


def check_extension(file_path, allowed_extensions=allowed_extensions):
    p, extension = path.splitext(file_path)
    if extension not in allowed_extensions:
        raise IOError('Allowed formats: {}'.format(allowed_extensions))


def pickle_model(classifier, feature_names, model_path, label_text='label'):
    p, extension = path.splitext(model_path)
    classifier.feature_names = feature_names
    if (extension == '.pmml'):
        print("Pickling model to {} ...".format(model_path))

        mapper = DataFrameMapper([
            (feature_names, None),
            (label_text, None),
        ])

        joblib.dump(classifier, p + '.pkl', compress=4)
        sklearn2pmml(classifier, mapper,  model_path)

    else:
        joblib.dump(classifier, model_path, compress=4)
