# Magba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import numpy as np
import magpylib._src.fields.field_BH_cylinder as magpy
from numpy.testing import assert_allclose
from pymagba.fields import *

def test_axial_cyl_b_on_axis() -> None:
    # pols = np.array(
    #     [
    #         # (0, 0, 0),
    #         (1, 2, 3),
    #         (3, 2, -1),
    #         (1, 1, 1),
    #     ]
    # )
    # dims = np.array(
    #     [
    #         # (1, 2),
    #         (2, 2),
    #         (1, 2),
    #         (3, 3),
    #     ]
    # )
    # points = np.array(
    #     [
    #         # (1, 2, 3),
    #         (1, -1, 0),
    #         (1, 1, 1),
    #         (0, 0, 0),  # inside
    #     ]
    # )
    # b_tests = [
    #     # [0.0, 0.0, 0.0],
    #     [-0.36846057, -0.10171405, -0.33006492],
    #     [0.05331225, 0.07895873, 0.10406998],
    #     [0.64644661, 0.64644661, 0.70710678],
    # ]
    # for pol, dim, point, b_test in zip(pols, dims, points, b_tests):
    #     magba_b = cyl_b(point, dim[0]/2, dim[1], tuple(pol))
    #     assert_allclose(b_test, magba_b, rtol=1e-5)

    N = 10
    radii = np.linspace(1, 3, N)
    heights = np.linspace(1, 3, N)
    pol_z = np.linspace(1, 3, N)

    R, H, P = np.meshgrid(radii, heights, pol_z, indexing="ij")
    combinations = np.array([R.flatten(), H.flatten(), P.flatten()]).T
    for r, h, pol_z in combinations:
        Z = np.linspace(h + 1e-6, 5, 100)

        for z in Z:
            magba_result = axial_cyl_b((0, 0, z), r, h, pol_z)
            magpy_result = magpy.BHJM_magnet_cylinder(
                "B",
                np.array([[0, 0, z]]),
                np.array([[r * 2, h]]),
                np.array([[0, 0, pol_z]]),
            )

            assert_allclose(
                magba_result,
                magpy_result.flatten(),
                err_msg=f"Not equal at z={z}, r={r} h={h} pol_z={pol_z}",
                rtol=1e-5
            )

        # points = np.zeros((len(Z), 3))
        # points[:, 2] = Z
        # dims = np.tile([r * 2, h], (len(Z), 1))
        # pol = np.tile([0, 0, pol_z], (len(Z), 1))

        # magba_result = np.array([cyl_b((0, 0, z), r, h, (0, 0, pol_z)) for z in Z])
        # magpy_result = magpy.BHJM_magnet_cylinder("B", points, dims, pol)

        # assert_allclose(magba_result, magpy_result, rtol=1e-5)
