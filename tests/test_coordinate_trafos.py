# coding: utf-8
from astropy.coordinates import SkyCoord, AltAz
import astropy.units as u
from astropy.time import Time
from fact.coordinates import CameraFrame
from fact.instrument.constants import PIXEL_SPACING_MM, LOCATION, FOV_PER_PIXEL_DEG
from pytest import approx


obstime = Time('2014-01-01 00:00')
altaz_frame = AltAz(location=LOCATION, obstime=obstime)
pointing_direction = SkyCoord(
    alt=80 * u.deg, az=-260 * u.deg,
    frame=altaz_frame,
)
cam_frame = CameraFrame(pointing_direction=pointing_direction, obstime=obstime)


def test_camera_to_altaz1():
    c = SkyCoord(
        x=10 * PIXEL_SPACING_MM * u.mm,
        y=0 * u.mm,
        frame=cam_frame,
    )

    h = c.transform_to(altaz_frame)
    print(h.zen.deg, h.az.deg)
    print(h.separation(pointing_direction).deg)
    print(10 * FOV_PER_PIXEL_DEG)
    assert h.separation(pointing_direction).deg == approx(10 * FOV_PER_PIXEL_DEG, 1e-3)


def test_camera_to_altaz2():
    c = SkyCoord(
        x=-10 * PIXEL_SPACING_MM * u.mm,
        y=0 * u.mm,
        frame=cam_frame,
    )

    h = c.transform_to(altaz_frame)
    print(h.zen.deg, h.az.deg)
    print(h.separation(pointing_direction).deg)
    assert h.separation(pointing_direction).deg == approx(10 * FOV_PER_PIXEL_DEG, 1e-3)


def test_camera_to_altaz3():
    c = SkyCoord(
        x=0 * u.mm,
        y=10 * PIXEL_SPACING_MM * u.mm,
        frame=cam_frame,
    )

    h = c.transform_to(altaz_frame)
    print(h.zen.deg, h.az.deg)
    print(h.separation(pointing_direction).deg)
    assert h.separation(pointing_direction).deg == approx(10 * FOV_PER_PIXEL_DEG, 1e-3)


def test_camera_to_altaz4():
    c = SkyCoord(
        x=-10 * u.mm,
        y=-10 * PIXEL_SPACING_MM * u.mm,
        frame=cam_frame,
    )

    h = c.transform_to(altaz_frame)
    print(h.zen.deg, h.az.deg)
    print(h.separation(pointing_direction).deg)


def test_altaz_to_camera():
    pointing_direction = SkyCoord(
        alt=60.667 * u.deg, az=96.790 * u.deg,
        frame=altaz_frame,
    )

    h = SkyCoord(
        alt=60.367 * u.deg, az=95.731 * u.deg,
        frame=altaz_frame,
    )

    c = h.transform_to(CameraFrame(pointing_direction=pointing_direction))

    print(c.x, c.y)


if __name__ == '__main__':
    test_camera_to_altaz1()
    test_camera_to_altaz2()
    test_camera_to_altaz3()
    test_camera_to_altaz4()
    test_altaz_to_camera()
