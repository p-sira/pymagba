# Magba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import numpy as np
from pymagba.magnets import TriangleMagnet
from tests.testing_util import run_test_general


def test_triangle():
    kwargs = {
        "vertices": np.array([[-0.1, -0.1, -0.1], [0.1, -0.1, 0.1], [0.0, 0.2, 0.0]]),
        "polarization": np.array((1.0, 2.0, 3.0)),
    }
    # max_mismatches is used here because spatial manipulation (Translate & Rotate)
    # causes microscopic floating-point noise for observer points landing perfectly
    # on the triangle's plane. This noise can flip the solid angle's branch cut,
    # resulting in a macroscopic jump of exactly M/2 (which is 0.5 in the X-axis for M_x=1.0).
    run_test_general(
        TriangleMagnet, "triangle", kwargs, rtol=5e-11, atol=1e-14, max_mismatches=5
    )
