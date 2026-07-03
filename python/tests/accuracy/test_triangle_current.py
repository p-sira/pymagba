# Magba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import numpy as np
from pymagba.currents import TriangleCurrent
from tests.testing_util import run_test_general


def test_triangle_current():
    kwargs = {
        "current_density": np.array([1.0, 2.0, 3.0]),
        "vertices": np.array([[-0.1, -0.1, -0.1], [0.1, -0.1, -0.1], [0.0, 0.1, -0.1]]),
    }
    run_test_general(
        TriangleCurrent, "trianglecurrent", kwargs, rtol=1e-10, atol=1e-14
    )
