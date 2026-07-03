# Magba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import numpy as np
from pymagba.magnets import CylinderMagnet, CuboidMagnet, SourceCollection, Dipole
from tests.testing_util import _compute_field, get_points_small, load_test_array
from numpy.testing import assert_allclose
from scipy.spatial.transform import Rotation

def verify_collection(coll, name):
    points = get_points_small()

    # Base
    expected = load_test_array(f"{name}.csv")
    assert_allclose(coll.compute_B(points), expected, rtol=1e-5, atol=1e-14)

    # Translate
    coll.position = (0.01, 0.015, 0.02)
    expected = load_test_array(f"{name}-translate.csv")
    assert_allclose(coll.compute_B(points), expected, rtol=1e-5, atol=1e-14)

    # Rotate
    coll.position = (0, 0, 0)
    coll.orientation = Rotation.from_rotvec((np.pi / 3, np.pi / 4, np.pi / 5))
    expected = load_test_array(f"{name}-rotate.csv")
    assert_allclose(coll.compute_B(points), expected, rtol=1e-5, atol=1e-14)

    # Translate Rotate
    coll.position = (0.01, 0.015, 0.02)
    expected = load_test_array(f"{name}-translate-rotate.csv")
    assert_allclose(coll.compute_B(points), expected, rtol=1e-5, atol=1e-14)

def test_collection_homogeneous_cylinder():
    c1 = CylinderMagnet(position=(0.0094, 0.0, -0.006), orientation=Rotation.from_rotvec((1.2092, 1.2092, 1.2092)), diameter=3e-3, height=4e-3, polarization=(1.0, 2.0, 3.0))
    c2 = CylinderMagnet(position=(-0.0047, 0.0081, -0.006), orientation=Rotation.from_rotvec((1.5316, 0.4104, 0.4104)), diameter=4e-3, height=5e-3, polarization=(0.4, 0.5, 0.6))
    c3 = CylinderMagnet(position=(-0.0047, -0.0081, -0.006), orientation=Rotation.from_rotvec((1.5316, -0.4104, -0.4104)), diameter=5e-3, height=6e-3, polarization=(0.9, 0.8, 0.6))
    verify_collection(SourceCollection([c1, c2, c3]), "cylinder-sources")

def test_collection_homogeneous_cuboid():
    rot1 = Rotation.identity()
    rot2 = Rotation.from_rotvec([0, np.pi / 3, 0])
    rot3 = Rotation.from_rotvec([0, 0, np.pi / 3])
    c1 = CuboidMagnet(position=(0.005, 0.01, 0.015), orientation=rot1, dimensions=(0.02, 0.02, 0.03), polarization=(0.1, 0.2, 0.3))
    c2 = CuboidMagnet(position=(0.015, 0.005, 0.01), orientation=rot2, dimensions=(0.02, 0.02, 0.03), polarization=(0.1, 0.2, 0.3))
    c3 = CuboidMagnet(position=(0.01, 0.015, 0.005), orientation=rot3, dimensions=(0.02, 0.02, 0.03), polarization=(0.1, 0.2, 0.3))
    verify_collection(SourceCollection([c1, c2, c3]), "cuboid-sources")

def test_collection_heterogeneous():
    rot1 = Rotation.identity()
    rot2 = Rotation.from_rotvec([0, np.pi / 3, 0])
    rot3 = Rotation.from_rotvec([0, np.pi / 2, np.pi / 2])
    c1 = CylinderMagnet(position=(0.005, 0.01, 0.015), orientation=rot1, diameter=0.04, height=0.05, polarization=(0.1, 0.2, 0.3))
    c2 = CuboidMagnet(position=(0.015, 0.005, 0.01), orientation=rot2, dimensions=(0.02, 0.02, 0.03), polarization=(0.1, 0.2, 0.3))
    c3 = Dipole(position=(0, 0, 0), orientation=rot3, moment=(0.4, 0.5, 0.6))
    verify_collection(SourceCollection([c1, c2, c3]), "multi-sources")
