import pandas as pd
import tempfile
import numpy as np
import h5py


def test_to_h5py():
    from fact.io import to_h5py, read_h5py

    df = pd.DataFrame({
        'x': np.random.normal(size=50),
        'N': np.random.randint(0, 10, dtype='uint8')
    })

    with tempfile.NamedTemporaryFile() as f:
        to_h5py(f.name, df, key='test')

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
        to_h5py(f.name, df, key='test')
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
        to_h5py(f.name, df, key='test')
        df2 = read_h5py(f.name, key='test')

        for col in df2.columns:
            df2[col] = pd.to_datetime(df2[col].apply(bytes.decode))

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
        to_h5py(f.name, df1, key='test', index=False)
        to_h5py(f.name, df2, key='test', mode='a', index=False)

        df_read = read_h5py(f.name, key='test')
        df_written = pd.concat([df1, df2], ignore_index=True)

        for col in df_written.columns:
            assert all(df_read[col] == df_written[col])
