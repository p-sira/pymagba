# Magba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import numpy as np
from pymagba.fields import cylinder_B, dipole_B, cuboid_B
from pymagba.magnets import CylinderMagnet, Dipole, CuboidMagnet


def test_cylinder_B():
    diameter = 5e-3
    height = 10e-3
    pol = [0, 0, 1]
    pos = [0, 0, 0]
    points = [[0, 0, 10e-3], [10e-3, 0, 0]]

    # Using Magnet class
    mag = CylinderMagnet(
        diameter=diameter, height=height, polarization=pol, position=pos
    )
    b_class = mag.compute_B(points)

    # Using field function
    b_func = cylinder_B(
        points, diameter=diameter, height=height, polarization=pol, position=pos
    )

    np.testing.assert_allclose(b_class, b_func)


def test_dipole_B():
    moment = [0, 0, 1]
    pos = [0, 0, 0]
    points = [[0, 0, 10e-3], [10e-3, 0, 0]]

    # Using Magnet class
    mag = Dipole(moment=moment, position=pos)
    b_class = mag.compute_B(points)

    # Using field function
    b_func = dipole_B(points, moment=moment, position=pos)

    np.testing.assert_allclose(b_class, b_func)


def test_cuboid_B():
    dims = [5e-3, 5e-3, 5e-3]
    pol = [0, 0, 1]
    pos = [0, 0, 0]
    points = [[0, 0, 10e-3], [10e-3, 0, 0]]

    # Using Magnet class
    mag = CuboidMagnet(dimensions=dims, polarization=pol, position=pos)
    b_class = mag.compute_B(points)

    # Using field function
    b_func = cuboid_B(points, dimensions=dims, polarization=pol, position=pos)

    np.testing.assert_allclose(b_class, b_func)


if __name__ == "__main__":
    test_cylinder_B()
    test_dipole_B()
    test_cuboid_B()
    print("All tests passed!")
