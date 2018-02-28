import numpy as np
import pandas as pd
import re

from .statistics import li_ma_significance

default_theta_off_keys = tuple('theta_deg_off_{}'.format(i) for i in range(1, 6))
default_prediction_off_keys = tuple(
    'gamma_prediction_off_{}'.format(i) for i in range(1, 6)
)


off_key_re = re.compile('([a-zA-z1-9]+_deg)_off_([0-9])?')


def calc_run_summary_source_independent(
        events, runs,
        prediction_threshold,
        theta2_cut,
        prediction_key='gamma_prediction',
        theta_key='theta_deg',
        theta_off_keys=default_theta_off_keys,
        ):

    '''
    Calculate run summaries for the given theta^2 and signal prediction cuts.
    This function requires, that no source dependent features,
    like Theta were used in the classification.

    Parameters
    ----------
    events: pd.DataFrame
        DataFrame with event data, needs to contain the columns
        `'night'`, `'run'`, `theta_key` and the `theta_off_keys`
    prediction_threshold: float
        Threshold for the classifier prediction
    theta2_cut: float
        Selection cut for theta^2 in deg^2
    prediction_key: str:
        Key to the classifier prediction
    theta_key: str
        Column name of the column containing theta in degree
    theta_off_keys: list[str]
        Column names of the column containing theta  in degree
        for all off regions
    '''

    runs = runs.set_index(['night', 'run_id'])
    runs.sort_index(inplace=True)

    # apply prediction threshold cut
    selected = events.query(
        '{} >= {}'.format(prediction_key, prediction_threshold)
    )

    on_data, off_data = split_on_off_source_independent(
        selected, theta2_cut, theta_key, theta_off_keys
    )

    alpha = 1 / len(theta_off_keys)

    runs['n_on'] = on_data.groupby(['night', 'run_id']).size()
    runs['n_on'].fillna(0, inplace=True)

    runs['n_off'] = off_data.groupby(['night', 'run_id']).size()
    runs['n_off'].fillna(0, inplace=True)

    runs['n_excess'] = runs['n_on'] - alpha * runs['n_off']
    runs['n_excess_err'] = np.sqrt(runs['n_on'] + alpha**2 * runs['n_off'])

    runs['excess_rate_per_h'] = runs['n_excess'] / runs['ontime'] / 3600
    runs['excess_rate_per_h_err'] = runs['n_excess_err'] / runs['ontime'] / 3600

    runs['significance'] = li_ma_significance(
        runs['n_on'], runs['n_off'], alpha
    )

    runs.reset_index(inplace=True)

    return runs


def split_on_off_source_independent(
        events,
        theta2_cut,
        theta_key='theta_deg',
        theta_off_keys=default_theta_off_keys,
        ):
    '''
    Split events dataframe into on and off region

    Parameters
    ----------
    events: pd.DataFrame
        DataFrame containing event information, required are
        `theta_key` and `theta_off_keys`.
    theta2_cut: float
        Selection cut for theta^2 in deg^2
    theta_key: str
        Column name of the column containing theta in degree
    theta_off_keys: list[str]
        Column names of the column containing theta  in degree
        for all off regions
    '''
    # apply theta2_cut
    theta_cut = np.sqrt(theta2_cut)

    on_data = events.query('{} <= {}'.format(theta_key, theta_cut))

    off_dfs = []
    for region, theta_off_key in enumerate(theta_off_keys, start=1):
        off_df = events.query('{} <= {}'.format(
            theta_off_key, theta_cut)
        ).copy()

        off_df['off_region'] = region
        drop_off_columns(off_df, region, inplace=True)

        off_dfs.append(off_df)

    off_data = pd.concat(off_dfs)

    return on_data, off_data


def drop_off_columns(df, off_region, inplace=False):
    '''
    Replace the "On" column with the column
    of the respective off region.
    For example for `off_region = 1`, `theta` is replaced by
    theta_off_1 and all theta_off_<N> columns are dropped.
    Same for all other columns, containing the pattern `_off_<N>`
    '''
    if inplace is False:
        df = df.copy()

    for col in df.columns:
        m = off_key_re.match(col)
        if m:
            on_key, key_region = m.groups()
            if int(key_region) == off_region:
                df.drop(on_key, axis=1, inplace=True)
                df[on_key] = df[col]

            df.drop(col, axis=1, inplace=True)

    if inplace is False:
        return df
