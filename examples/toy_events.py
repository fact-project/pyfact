# -*- coding:utf8 -*-
'''
Usage:
    toy_events.py (gamma | muon) [options]

Options:
    --num-events=<N>  Number of Events to create [default: 30]
    --noise=<stddev>  Standard Deviation for the white noise [default: 0.5]
    --nsb=<lambda>    Mean nsb photons per pixel [default: 1.0]
'''
import numpy as np
from fact.plotting import Viewer, get_pixel_coords
from docopt import docopt

px, py = get_pixel_coords()


def muon_ring(psf=5, mirror_radius=1.75, max_impact=None):
    if max_impact is None:
        max_impact = mirror_radius

    n_photons = np.random.poisson(350)
    mx, my = np.random.uniform(-100, 100, 2)
    r = np.random.uniform(60, 102)

    photon_theta = np.random.uniform(0, 2 * np.pi, n_photons)

    photon_x = r * np.cos(photon_theta) + mx
    photon_y = r * np.sin(photon_theta) + my

    photon_x += np.random.normal(0, psf, n_photons)
    photon_y += np.random.normal(0, psf, n_photons)

    data = pixel_content(photon_x, photon_y)
    return data


def gamma(psf=5):
    n_photons = rand_power()

    length = np.random.normal(6.5 * np.log10(n_photons), 0.2 * np.log10(n_photons))
    width = np.random.uniform(0.4 * length, 0.8 * length)
    delta = np.random.uniform(0, 2 * np.pi)

    cov = [[length**2, 0], [0, width**2]]
    cov = rotate_cov(cov, delta)

    mean = np.random.uniform(-100, 100, 2)
    photon_x, photon_y = np.random.multivariate_normal(mean, cov, n_photons).T

    data = pixel_content(photon_x, photon_y)

    return data


def pixel_content(photon_x, photon_y):
    data = np.zeros(1440)
    for x, y in zip(photon_x, photon_y):
        if np.sqrt(x**2 + y**2) > 200:
            continue
        pixel = np.argmin((x - px)**2 + (y - py)**2)
        data[pixel] += 1
    return data


def rotate_cov(cov, angle):
    rot = np.matrix([
        [np.cos(angle), -np.sin(angle)],
        [np.sin(angle), np.cos(angle)]
    ])

    cov = np.matrix(cov)

    return rot * cov * rot.T


def rand_power(N=1, gamma=2.7, a=500, b=1000):
    assert gamma > 2, 'gamma has to be > 2'
    x = np.random.rand(N)
    exp = 1 - gamma
    return (a**exp - x * (a**exp - b**exp))**(1 / exp)


def noise(sigma=0.5, n_pix=1440):
    ''' returns gaussian white noise with std dev sigma '''
    return np.random.normal(0, sigma, n_pix)


def nsb(lamb, n_pix=1440):
    return np.random.poisson(lamb, n_pix)


def main():
    args = docopt(__doc__)

    num_events = int(args['--num-events'])
    noise_sigma = float(args['--noise'])
    nsb_lambda = float(args['--nsb'])

    data = np.empty((num_events, 1440))
    for event in range(num_events):

        if args['muon']:
            data[event] = muon_ring()
        if args['gamma']:
            data[event] = gamma()

        if noise_sigma > 0:
            data[event] += noise(noise_sigma)

        if nsb_lambda > 0:
            data[event] += nsb(nsb_lambda)

    Viewer(data, 'photons', vmin=0)

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        pass
