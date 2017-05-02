import numpy as np


def power_law(energy, phi_0, gamma):
    r'''
    Simple power law

    .. math::
        \phi = \phi_0 \cdot E ^ \gamma

    Parameters
    ----------
    energy: number or array-like
        energy points to evaluate
    phi_0: float
        Flux normalization
    gamma: float
        Spectral index
    '''
    return phi_0 * energy ** gamma


def curved_power_law(energy, phi_0, a, b):
    r'''
    Curved power law

    .. math::
        \phi = \phi_0 \cdot E ^ {a - b \cdot \log(E)}

    Parameters
    ----------
    energy: number or array-like
        energy points to evaluate
    phi_0: float
        Flux normalization
    a: float
        Parameter `a`  of the curved power law
    b: float
        Parameter `b` of the curved power law
    '''
    return phi_0 * energy ** (a + b * np.log10(energy))


def li_ma_significance(n_on, n_off, alpha=0.2):
    '''
    Calculate the Li&Ma significance for given
    observations data

    Parameters
    ----------
    n_on: integer or array like
        Number of events for the on observations
    n_off: integer of array like
        Number of events for the off observations
    alpha: float
        Scaling factor for the off observations, for wobble observations
        this is 1 / number of off regions
    '''

    scalar = np.isscalar(n_on)

    n_on = np.array(n_on, copy=False, ndmin=1)
    n_off = np.array(n_off, copy=False, ndmin=1)

    with np.errstate(divide='ignore', invalid='ignore'):
        p_on = n_on / (n_on + n_off)
        p_off = n_off / (n_on + n_off)

        t1 = n_on * np.log(((1 + alpha) / alpha) * p_on)
        t2 = n_off * np.log((1 + alpha) * p_off)

        ts = (t1 + t2)
        significance = np.sqrt(ts * 2)

    significance[np.isnan(significance)] = 0
    significance[n_on < alpha * n_off] = 0

    if scalar:
        return significance[0]

    return significance


def calc_weight_simple_to_curved(energy, gamma, a, b):
    '''
    Reweigt simulated events from a simulated power law with
    spectral index `gamma` to a curved power law with parameters `a` and `b`

    Parameters
    ----------
    energy: float or array-like
        Energy of the events
    gamma: float
        Spectral index of the simulated power law
    a: float
        Parameter `a` of the target curved power law
    b: float
        Parameter `b` of the target curved power law
    '''
    return energy ** (-gamma + a + b * np.log10(energy))


def calc_weight_change_index(energy, simulated_gamma, target_gamma):
    '''
    Reweigt simulated events from a simulated power law with
    spectral index `gamma` to a curved power law with parameters `a` and `b`

    Parameters
    ----------
    energy: float or array-like
        Energy of the events
    simulated_gamma: float
        Spectral index of the simulated power law
    target_gamma: float
        Spectral index of the target power law
    '''
    return energy ** (target_gamma - simulated_gamma)


def mc_obstime(n_events, gamma, phi_0, max_impact, e_min, e_max):
    '''
    Calculate the equivalent observation time for a gamma montecarlo set

    Parameters
    ----------
    n_events: int
        Number of simulated events
    gamma: float
        Spectral index of the simulated power law
    phi_0: float
        Flux normalization of the simulated power law
    max_impact: float
        Maximal simulated impact
    e_min: float
        Mimimal simulated energy
    e_max: float
        Maximal simulated energy
    '''
    if gamma >= -1:
        raise ValueError('gamma must be < -1')

    numerator = n_events * (gamma + 1)

    t1 = phi_0 * max_impact**2 * np.pi
    t2 = e_max**(gamma + 1) - e_min**(gamma + 1)

    denominator = t1 * t2

    return numerator / denominator
