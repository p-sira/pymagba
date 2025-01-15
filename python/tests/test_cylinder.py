# Magba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

from magpylib.magnet import Cylinder
import numpy as np
import pytest
from scipy.spatial.transform import Rotation
from numpy.testing import assert_allclose
from pymagba.fields.fields import *
from pymagba.sources.sources import CylinderMagnet


def test_axial_b_vs_magpy() -> None:
    N = 20
    radii = np.linspace(1e-3, 3, N)
    heights = np.linspace(1e-3, 3, N)
    pol_z = np.linspace(0, 3, N)

    R, H, P = np.meshgrid(radii, heights, pol_z, indexing="ij")
    combinations = np.array([R.flatten(), H.flatten(), P.flatten()]).T
    for r, h, pol_z in combinations:
        magpy_magnet = Cylinder(dimension=(r * 2, h), polarization=(0, 0, pol_z))
        magba_magnet = CylinderMagnet(
            radius=r, height=h, polarization=np.array([0, 0, pol_z])
        )

        points = np.random.random((200, 3)) * 5

        magpy_result = magpy_magnet.getB(points)
        magba_result = magba_magnet.get_B(points)

        assert_allclose(magba_result, magpy_result, rtol=1e-5, atol=1e-10)

def test_random_fixed_pose_b_vs_magpy() -> None:
    N = 100
    radii = np.random.random(N) * 3
    heights = np.random.random(N) * 3
    pols = np.random.uniform(-5, 5, (N, 3))

    for r, h, pol in zip(radii, heights, pols):
        magpy_magnet = Cylinder(dimension=(r * 2, h), polarization=pol)
        magba_magnet = CylinderMagnet(radius=r, height=h, polarization=pol)

        points = (np.random.random((100, 3)) - 0.5) * 5

        magpy_result = magpy_magnet.getB(points)
        magba_result = magba_magnet.get_B(points)

        assert_allclose(magba_result, magpy_result, rtol=1e-5, atol=1e-10)

def test_random_b_vs_magpy() -> None:
    N = 1000
    radii = np.random.random(N) * 3
    heights = np.random.random(N) * 3
    pols = np.random.uniform(-5, 5, (N, 3))
    positions = np.random.uniform(-3, 3, (N, 3))
    orientations = Rotation.random(N)

    for position, orientation, r, h, pol in zip(positions, orientations, radii, heights, pols):
        magpy_magnet = Cylinder(position, orientation, dimension=(r * 2, h), polarization=pol)
        magba_magnet = CylinderMagnet(position, orientation, radius=r, height=h, polarization=pol)

        points = (np.random.random((1000, 3)) - 0.5) * 5

        magpy_result = magpy_magnet.getB(points)
        magba_result = magba_magnet.get_B(points)

        assert_allclose(magba_result, magpy_result, rtol=1e-5, atol=1e-10)
