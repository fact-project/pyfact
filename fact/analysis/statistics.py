import numpy as np
import astropy.units as u

POINT_SOURCE_FLUX_UNIT = (1 / u.GeV / u.s / u.m**2).unit
FLUX_UNIT = POINT_SOURCE_FLUX_UNIT / u.sr


@u.quantity_input
def random_power(
    spectral_index,
    e_min: u.TeV,
    e_max: u.TeV,
    size,
    e_ref: u.TeV=1 * u.TeV,
) -> u.TeV:
    r'''
    Draw random numbers from a power law distribution

    .. math::
        f(E) =
        \frac{1 - \gamma}
        ({E_{\max} / E_{\mathrm{ref}})^{\gamma - 1} - (E_{\min} / E_{\mathrm{ref}})^{\gamma - 1}}
        (E /  E_{\mathrm{ref}})^{\gamma}

    Parameters
    ----------
    spectral_index: float
        The differential spectral index of the power law
    e_min: Quantity[energy]
        lower energy border
    e_max: Quantity[energy]
        upper energy border, can be np.inf
    size: int or tuple[int]
        Number of events to draw or a shape like (100, 2)
    '''
    if spectral_index > -1.0:
        raise ValueError('spectral_index must be < -1.0')

    u = np.random.uniform(0, 1, size)

    exponent = spectral_index + 1

    if e_max == np.inf:
        diff = -(e_min / e_ref)**exponent
    else:
        diff = (e_max / e_ref)**exponent - (e_min / e_ref)**exponent

    return e_ref * (diff * u + (e_min / e_ref)**exponent) ** (1 / exponent)


def power_law(
    energy: u.TeV,
    flux_normalization: (FLUX_UNIT, POINT_SOURCE_FLUX_UNIT),
    spectral_index,
    e_ref: u.TeV=1 * u.TeV,
):
    r'''
    Simple power law

    .. math::
        \phi = \phi_0 \cdot (E / E_{\mathrm{ref}})^{\gamma}

    Parameters
    ----------
    energy: Quantity[energy]
        energy points to evaluate
    flux_normalization: Quantity[m**-2 s**-2 TeV**-1]
        Flux normalization
    spectral_index: float
        Spectral index
    e_ref: Quantity[energy]
        The reference energy
    '''
    return flux_normalization * (energy / e_ref)**(spectral_index)


@u.quantity_input
def curved_power_law(
    energy: u.TeV,
    flux_normalization: (FLUX_UNIT, POINT_SOURCE_FLUX_UNIT),
    a,
    b,
    e_ref: u.TeV=1 * u.TeV,
):
    r'''
    Curved power law

    .. math::
        \phi = \phi_0 \cdot E ^ {a + b \cdot \log_{10}(E)}

    Parameters
    ----------
    energy: number or array-like
        energy points to evaluate
    flux_normalization: float
        Flux normalization
    a: float
        Parameter `a`  of the curved power law
    b: float
        Parameter `b`  of the curved power law
    e_ref: Quantity[energy]
        The reference energy
    '''
    exp = a + b * np.log10((energy / e_ref))
    return flux_normalization * (energy / e_ref) ** exp


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


@u.quantity_input
def calc_weight_simple_to_curved(
    energy: u.TeV,
    spectral_index,
    a,
    b,
    e_ref: u.TeV = 1 * u.TeV,
):
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
    return (energy / e_ref) ** (spectral_index + a + b * np.log10(energy / e_ref))


@u.quantity_input
def calc_weight_change_index(
    energy: u.TeV,
    simulated_index,
    target_index,
    e_ref: u.TeV=1 * u.TeV,
):
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
    return (energy / e_ref) ** (target_index - simulated_index)


@u.quantity_input
def calc_gamma_obstime(
    n_events,
    spectral_index,
    flux_normalization: (FLUX_UNIT, POINT_SOURCE_FLUX_UNIT),
    max_impact: u.m,
    e_min: u.TeV,
    e_max: u.TeV,
    e_ref: u.TeV = 1 * u.TeV,
) -> u.s:
    r'''
    Calculate the equivalent observation time for a number of simulation enents

    The number of events produced by sampling from a power law with
    spectral index γ is given by

    .. math::
        N =
        A t \Phi_0 \int_{E_{\min}}^{E_{\max}}
        \left(\frac{E}{E_{\mathrm{ref}}}\right)^{\gamma}
        \,\mathrm{d}E

    Solving this for t yields

    .. math::
        t = \frac{N \cdot (\gamma - 1)}{
            E_{\mathrm{ref}} A \Phi_0
            \left(
                \left(\frac{E_{\max}}{E_{\mathrm{ref}}}\right)^{\gamma - 1}
                - \left(\frac{E_{\max}}{E_{\mathrm{ref}}}\right)^{\gamma - 1}
            \right)
        }

    Parameters
    ----------
    n_events: int
        Number of simulated events
    spectral_index: float
        Spectral index of the simulated power law, including the sign,
        so typically -2.7 or -2
    flux_normalization: float
        Flux normalization of the simulated power law
    max_impact: Quantity[length]
        Maximal simulated impact
    e_min: Quantity[energy]
        Mimimal simulated energy
    e_max: Quantity[energy]
        Maximal simulated energy
    e_ref: Quantity[energy]
        The e_ref energy
    '''
    if spectral_index >= -1:
        raise ValueError('spectral_index must be < -1')

    numerator = n_events * (spectral_index + 1)

    A = max_impact**2 * np.pi
    t1 = A * flux_normalization * e_ref
    t2 = (e_max / e_ref)**(spectral_index + 1)
    t3 = (e_min / e_ref)**(spectral_index + 1)

    denominator = t1 * (t2 - t3)

    return numerator / denominator


@u.quantity_input
def power_law_integral(
    flux_normalization: (FLUX_UNIT, POINT_SOURCE_FLUX_UNIT),
    spectral_index,
    e_min: u.TeV,
    e_max: u.TeV,
    e_ref: u.TeV = 1 * u.TeV,
):
    '''
    Return the integral of a power_law with normalisation
    `flux_normalization` and index `spectral_index`
    between `e_min` and `e_max`
    '''
    int_index = spectral_index + 1
    e_term = (e_max / e_ref)**(int_index) - (e_min / e_ref)**(int_index)

    res = flux_normalization * e_ref / int_index * e_term

    if flux_normalization.unit.is_equivalent(FLUX_UNIT):
        return res.to(1 / u.m**2 / u.s / u.sr)
    return res.to(1 / u.m**2 / u.s)


@u.quantity_input
def calc_proton_obstime(
    n_events,
    spectral_index,
    max_impact: u.m,
    viewcone: u.deg,
    e_min: u.TeV,
    e_max: u.TeV,
    flux_normalization: FLUX_UNIT = 1.8e4 * FLUX_UNIT,
    e_ref: u.GeV=1 * u.GeV,
) -> u.s:
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
    e_min: Quantity[energy]
        Mimimal simulated energy
    e_max: Quantity[energy]
        Maximal simulated energy
    flux_normalization: float
        Flux normalisation of the cosmic rays in nucleons / (m² s sr GeV)
        Default value is (29.2) of
        http://pdg.lbl.gov/2016/reviews/rpp2016-rev-cosmic-rays.pdf
    '''
    area = np.pi * max_impact**2
    solid_angle = 2 * np.pi * (1 - np.cos(viewcone)) * u.sr

    expected_integral_flux = power_law_integral(
        flux_normalization, spectral_index, e_min, e_max, e_ref
    )

    return n_events / area / solid_angle / expected_integral_flux
