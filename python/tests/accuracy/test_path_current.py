# Magba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import numpy as np
from pymagba.currents import PathCurrent
from tests.testing_util import run_test_general


def test_path_current():
    kwargs = {
        "vertices": np.array([[-0.1, -0.1, -0.1], [0.1, -0.1, -0.1], [0.0, 0.1, -0.1], [0.0, 0.0, 0.1]]),
        "current": 1.0,
    }
    run_test_general(
        PathCurrent, "polyline", kwargs, rtol=1e-9, atol=1e-14
    )
