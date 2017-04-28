import numpy as np
import pandas as pd

from .statistics import li_ma_significance

default_off_keys = tuple('Theta_Off_{}_deg'.format(i) for i in range(1, 6))


def calc_run_summary_source_independent(
        events, runs,
        prediction_threshold,
        theta2_cut,
        prediction_key='signal_prediction',
        theta_key='Theta_deg',
        theta_off_keys=default_off_keys,
        ):
    '''
    Calculate run summaries for the given theta^2 and signal prediction cuts.

    Parameters
    ----------
    events: pd.DataFrame
        DataFrame with event data, needs to contain the columns
        `'night'`, `'run'`, `theta_key` and the `theta_off_keys`
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

    runs['n_on'] = on_data.groupby(['night', 'run_id']).size()
    runs['n_on'].fillna(0, inplace=True)

    runs['n_off'] = off_data.groupby(['night', 'run_id']).size()
    runs['n_off'].fillna(0, inplace=True)

    runs['significance'] = li_ma_significance(
        runs['n_on'], runs['n_off'], 1 / len(off_data)
    )

    runs.reset_index(inplace=True)

    return runs


def split_on_off_source_independent(
        events,
        theta2_cut,
        theta_key='Theta_deg',
        theta_off_keys=default_off_keys,
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

    off_data = pd.concat([
        events.query('{} <= {}'.format(theta_off_key, theta_cut))
        for theta_off_key in theta_off_keys
    ])

    return on_data, off_data
