import pandas as pd
import tempfile
import numpy as np
import h5py
import pytest


def test_to_h5py():
    from fact.io import to_h5py, read_h5py

    df = pd.DataFrame({
        'x': np.random.normal(size=50),
        'N': np.random.randint(0, 10, dtype='uint8')
    })

    with tempfile.NamedTemporaryFile() as f:
        to_h5py(df, f.name, key='test')

        with h5py.File(f.name, 'r') as hf:

            assert 'test' in hf.keys()

            g = hf['test']

            assert 'x' in g.keys()
            assert 'N' in g.keys()

        df2 = read_h5py(f.name, key='test')

        assert all(df.dtypes == df2.dtypes)
        assert all(df['x'] == df2['x'])
        assert all(df['N'] == df2['N'])


def test_to_h5py_string():
    from fact.io import to_h5py, read_h5py

    df = pd.DataFrame({
        'name': ['Mrk 501', 'Mrk 421', 'Crab'],
    })

    with tempfile.NamedTemporaryFile() as f:
        to_h5py(df, f.name, key='test')
        df2 = read_h5py(f.name, key='test')

        assert all(df.dtypes == df2.dtypes)
        assert all(df['name'] == df2['name'])


def test_to_h5py_datetime():
    from fact.io import to_h5py, read_h5py

    df = pd.DataFrame({
        't_ns': pd.date_range('2017-01-01', freq='1ns', periods=100),
        't_us': pd.date_range('2017-01-01', freq='1us', periods=100),
        't_ms': pd.date_range('2017-01-01', freq='1ms', periods=100),
        't_s': pd.date_range('2017-01-01', freq='1s', periods=100),
        't_d': pd.date_range('2017-01-01', freq='1d', periods=100),
    })

    with tempfile.NamedTemporaryFile() as f:
        to_h5py(df, f.name, key='test')
        df2 = read_h5py(f.name, key='test')

        for col in df.columns:
            assert all(df[col] == df2[col])


def test_to_h5py_append():
    from fact.io import to_h5py, read_h5py

    df1 = pd.DataFrame({
        'x': np.random.normal(size=50),
        'N': np.random.randint(0, 10, dtype='uint8')
    })
    df2 = pd.DataFrame({
        'x': np.random.normal(size=50),
        'N': np.random.randint(0, 10, dtype='uint8')
    })

    with tempfile.NamedTemporaryFile() as f:
        to_h5py(df1, f.name, key='test', index=False)
        to_h5py(df2, f.name, key='test', mode='a', index=False)

        df_read = read_h5py(f.name, key='test')
        df_written = pd.concat([df1, df2], ignore_index=True)

        for col in df_written.columns:
            assert all(df_read[col] == df_written[col])


def test_to_h5py_append_second_group():
    from fact.io import to_h5py, read_h5py

    df1 = pd.DataFrame({
        'x': np.random.normal(size=50),
        'N': np.random.randint(0, 10, dtype='uint8')
    })
    df2 = pd.DataFrame({
        'x': np.random.normal(size=50),
        'N': np.random.randint(0, 10, dtype='uint8')
    })

    with tempfile.NamedTemporaryFile() as f:
        to_h5py(df1, f.name, key='g1', index=False)
        to_h5py(df2, f.name, key='g2', index=False)

        df_g1 = read_h5py(f.name, key='g1')
        df_g2 = read_h5py(f.name, key='g2')

        for col in df_g1.columns:
            assert all(df_g1[col] == df1[col])

        for col in df_g2.columns:
            assert all(df_g2[col] == df2[col])


def test_write_data_csv():
    from fact.io import write_data

    df = pd.DataFrame({
        'x': np.random.normal(size=50),
        'N': np.random.randint(0, 10, dtype='uint8')
    })

    with tempfile.NamedTemporaryFile(suffix='.csv') as f:
        write_data(df, f.name)


def test_write_data_json():
    from fact.io import write_data

    df = pd.DataFrame({
        'x': np.random.normal(size=50),
        'N': np.random.randint(0, 10, dtype='uint8')
    })

    with tempfile.NamedTemporaryFile(suffix='.json') as f:
        write_data(df, f.name)


def test_write_data_jsonlines():
    from fact.io import write_data

    df = pd.DataFrame({
        'x': np.random.normal(size=50),
        'N': np.random.randint(0, 10, dtype='uint8')
    })

    with tempfile.NamedTemporaryFile(suffix='.jsonl') as f:
        write_data(df, f.name)


def test_write_data_pandas_hdf():
    from fact.io import write_data

    df = pd.DataFrame({
        'x': np.random.normal(size=50),
        'N': np.random.randint(0, 10, dtype='uint8')
    })

    with tempfile.NamedTemporaryFile(suffix='.hdf5') as f:
        write_data(df, f.name, use_h5py=False)


def test_initialize_h5py():
    from fact.io import initialize_h5py

    df = pd.DataFrame({
        'x': [1, 2, 3],
        'name': ['Crab', 'Mrk 501', 'Test'],
        't': ['2017-10-01 21:22', '2017-10-01 21:23', '2017-10-01 21:24'],
        's': [[0, 1], [0, 2], [0, 3]],
    })
    df['t'] = pd.to_datetime(df['t'])

    with tempfile.NamedTemporaryFile(suffix='.hdf5') as f:
        with h5py.File(f.name, 'w') as h5file:
            initialize_h5py(h5file, df.to_records(index=False), key='events')

        with h5py.File(f.name, 'r') as h5file:
            assert h5file['events']['name'].dtype == np.dtype('O')
            assert h5file['events']['x'].dtype == np.dtype('int64')
            assert h5file['events']['t'].dtype == np.dtype('S48')
            assert h5file['events']['s'].shape == (0, 2)


def test_append_h5py():
    from fact.io import initialize_h5py, append_to_h5py

    df = pd.DataFrame({
        'x': [1, 2, 3],
        'name': ['Crab', 'Mrk 501', 'Test'],
        't': ['2017-10-01 21:22', '2017-10-01 21:23', '2017-10-01 21:24'],
        's': [[0, 1], [0, 2], [0, 3]],
    })
    df['t'] = pd.to_datetime(df['t'])

    with tempfile.NamedTemporaryFile(suffix='.hdf5') as f:
        with h5py.File(f.name, 'w') as h5file:
            array = df.to_records(index=False)
            initialize_h5py(h5file, array, key='events')
            append_to_h5py(h5file, array, key='events')

        with h5py.File(f.name, 'r') as h5file:
            assert h5file['events']['name'].dtype == np.dtype('O')
            assert h5file['events']['x'].dtype == np.dtype('int64')
            assert h5file['events']['t'].dtype == np.dtype('S48')
            assert h5file['events']['s'].shape == (3, 2)
            assert h5file['events']['s'][0, 1] == 1
            assert h5file['events']['s'][2, 1] == 3


def test_append_3d():
    from fact.io import initialize_h5py, append_to_h5py

    array = np.zeros(100, dtype=[('x', 'float64', (3, 3))])

    with tempfile.NamedTemporaryFile(suffix='.hdf5') as f:
        with h5py.File(f.name, 'w') as h5file:
            initialize_h5py(h5file, array, key='events')

            append_to_h5py(h5file, array, key='events')
            append_to_h5py(h5file, array, key='events')


def test_write_data_h5py():
    from fact.io import write_data

    df = pd.DataFrame({
        'x': np.random.normal(size=50),
        'N': np.random.randint(0, 10, dtype='uint8')
    })

    with tempfile.NamedTemporaryFile(suffix='.hdf5') as f:
        write_data(df, f.name, use_h5py=True)


def test_write_lists_h5py():
    from fact.io import to_h5py, read_h5py

    df = pd.DataFrame({
        'x': [[1.0, 2.0], [3.0, 4.0]]
    })

    with tempfile.NamedTemporaryFile(suffix='.hdf5') as f:
        to_h5py(df, f.name)

        df = read_h5py(f.name, columns=['x'])

        assert df['x_0'].iloc[0] == 1.0


def test_write_data_root():
    from fact.io import write_data

    df = pd.DataFrame({
        'x': np.random.normal(size=50),
        'N': np.random.randint(0, 10, dtype='uint8')
    })

    with pytest.raises(IOError):
        with tempfile.NamedTemporaryFile(suffix='.root') as f:
            write_data(df, f.name)


def test_read_data_csv():
    '''
    Write a csv file from a dataframe and then read it back again.
    '''
    from fact.io import write_data, read_data

    df = pd.DataFrame({
        'x': np.random.normal(size=50).astype('float32'),
        'N': np.random.randint(0, 10, dtype='uint8', size=50)
    })

    with tempfile.NamedTemporaryFile(suffix='.csv') as f:
        write_data(df, f.name)

        dtypes = {'x': 'float32', 'N': 'uint8'}
        df_from_file = read_data(f.name, dtype=dtypes)

        assert df.equals(df_from_file)


def test_read_data_h5py():
    '''
    Create a h5py hdf5 file from a dataframe and read it back.
    '''
    from fact.io import write_data, read_data

    df = pd.DataFrame({
        'x': np.random.normal(size=50).astype('float32'),
        'N': np.random.randint(0, 10, dtype='uint8', size=50)
    })

    with tempfile.NamedTemporaryFile(suffix='.hdf5') as f:
        write_data(df, f.name, use_h5py=True, key='lecker_daten')

        df_from_file = read_data(f.name, key='lecker_daten')

        assert df.equals(df_from_file)



