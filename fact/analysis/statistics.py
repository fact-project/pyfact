import numpy as np


def random_power(spectral_index, e_min, e_max, size):
    r'''
    Draw random numbers from a power law distribution

    .. math::
        f(E) =
        \frac{1 - \gamma}
        {E_{\max}^{1 - \gamma} - E_{\min}^{1 - \gamma}}
        E^{-\gamma}

    Parameters
    ----------
    spectral_index: float
        The differential spectral index of the power law
    e_min: float
        lower energy border
    e_max: float
        upper energy border, can be np.inf
    size: int or tuple[int]
        Number of events to draw or a shape like (100, 2)
    '''
    assert spectral_index > 1.0, 'spectral_index must be > 1.0'
    u = np.random.uniform(0, 1, size)

    exponent = 1 - spectral_index

    if e_max == np.inf:
        diff = -e_min**exponent
    else:
        diff = e_max**exponent - e_min**exponent

    return (diff * u + e_min**exponent) ** (1 / exponent)


def power_law(energy, flux_normalization, spectral_index):
    r'''
    Simple power law

    .. math::
        \phi = \phi_0 \cdot E ^{-\gamma}

    Parameters
    ----------
    energy: number or array-like
        energy points to evaluate
    flux_normalization: float
        Flux normalization
    spectral_index: float
        Spectral index
    '''
    return flux_normalization * energy**(-spectral_index)


def curved_power_law(energy, flux_normalization, a, b):
    r'''
    Curved power law

    .. math::
        \phi = \phi_0 \cdot E ^ {a - b \cdot \log(E)}

    Parameters
    ----------
    energy: number or array-like
        energy points to evaluate
    flux_normalization: float
        Flux normalization
    a: float
        Parameter `a`  of the curved power law
    b: float
        Parameter `b` of the curved power law
    '''
    return flux_normalization * energy ** (a + b * np.log10(energy))


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


def calc_weight_simple_to_curved(energy, spectral_index, a, b):
    '''
    Reweight simulated events from a simulated power law with
    spectral index `spectral_index` to a curved power law with parameters `a` and `b`

    Parameters
    ----------
    energy: float or array-like
        Energy of the events
    spectral_index: float
        Spectral index of the simulated power law
    a: float
        Parameter `a` of the target curved power law
    b: float
        Parameter `b` of the target curved power law
    '''
    return energy ** (spectral_index + a + b * np.log10(energy))


def calc_weight_change_index(energy, simulated_index, target_index):
    '''
    Reweight simulated events from one power law index to another

    Parameters
    ----------
    energy: float or array-like
        Energy of the events
    simulated_index: float
        Spectral index of the simulated power law
    target_index: float
        Spectral index of the target power law
    '''
    return energy ** (target_index - simulated_index)


def calc_gamma_obstime(n_events, spectral_index, flux_normalization, max_impact, e_min, e_max):
    '''
    Calculate the equivalent observation time for a spectral_index montecarlo set

    Parameters
    ----------
    n_events: int
        Number of simulated events
    spectral_index: float
        Spectral index of the simulated power law
    flux_normalization: float
        Flux normalization of the simulated power law
    max_impact: float
        Maximal simulated impact
    e_min: float
        Mimimal simulated energy
    e_max: float
        Maximal simulated energy
    '''
    if spectral_index >= -1:
        raise ValueError('spectral_index must be < -1')

    numerator = n_events * (1 - spectral_index)

    t1 = flux_normalization * max_impact**2 * np.pi
    t2 = e_max**(1 - spectral_index) - e_min**(1 - spectral_index)

    denominator = t1 * t2

    return numerator / denominator


def power_law_integral(flux_normalisation, spectral_index, e_min, e_max):
    '''
    Return the integral of a power_law with normalisation
    `flux_normalization` and index `spectral_index`
    between `e_min` and `e_max`
    '''
    int_index = 1 - spectral_index
    return flux_normalisation / int_index * (e_max**(int_index) - e_min**(int_index))


def calc_proton_obstime(
        n_events,
        spectral_index,
        max_impact,
        viewcone,
        e_min,
        e_max,
        flux_normalization=1.8e4,
        ):
    '''
    Calculate the equivalent observation time for a proton montecarlo set

    Parameters
    ----------
    n_events: int
        Number of simulated events
    spectral_index: float
        Spectral index of the simulated power law
    max_impact: float
        Maximal simulated impact in m
    viewcone: float
        Viewcone in degrees
    e_min: float
        Mimimal simulated energy in GeV
    e_max: float
        Maximal simulated energy in GeV
    flux_normalization: float
        Flux normalisation of the cosmic rays in nucleons / (m² s sr GeV)
        Default value is (29.2) of
        http://pdg.lbl.gov/2016/reviews/rpp2016-rev-cosmic-rays.pdf
    '''
    area = np.pi * max_impact**2
    solid_angle = 2 * np.pi * (1 - np.cos(np.deg2rad(viewcone)))

    expected_integral_flux = power_law_integral(flux_normalization, 2.7, e_min, e_max)

    return n_events / area / solid_angle / expected_integral_flux
