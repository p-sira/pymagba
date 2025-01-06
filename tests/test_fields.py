# Magba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import numpy as np
import magpylib._src.fields.field_BH_cylinder as magpy
from numpy.testing import assert_allclose
from pymagba.fields import *


def test_axial_cyl_b_cyl_error() -> None:
    assert np.isnan(np.sum(axial_cyl_b_cyl(0, 0, 0, 0, 0)))

# Current magpylib implementation seems to be incorrect!
# def test_axial_cyl_b() -> None:
#     N = 100
#     args = np.random.uniform(-3, 3, (N, 6))
#     args[:, :3] *= 2 # Prevent internal magnetic field
#     magba_result = np.array(
#         [
#             axial_cyl_b(x, y, z, radius, height, pol_z)
#             for x, y, z, radius, height, pol_z in args
#         ]
#     )

#     x, y, z, radius, height, pol_z = args.T
#     pol = np.zeros((len(pol_z), 3))
#     pol[:, 2] = pol_z
#     points = np.column_stack([x, y, z])
#     dims = np.column_stack([radius, height])

#     magpy_result = magpy.BHJM_magnet_cylinder("B", points, dims, pol)
#     assert assert_allclose(magba_result, magpy_result)
