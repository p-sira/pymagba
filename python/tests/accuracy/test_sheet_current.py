# Magba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import numpy as np
from pymagba.currents import SheetCurrent
from tests.testing_util import run_test_general


def test_sheet_current():
    kwargs = {
        "current_densities": np.array([[1.0, 2.0, 3.0], [1.0, 2.0, 3.0], [1.0, 2.0, 3.0], [1.0, 2.0, 3.0]]),
        "vertices": np.array([[-0.1, -0.1, -0.1], [0.1, -0.1, -0.1], [0.0, 0.1, -0.1], [0.0, 0.0, 0.1]]),
        "faces": np.array([[0, 2, 1], [0, 1, 3], [1, 2, 3], [0, 3, 2]]),
    }
    run_test_general(
        SheetCurrent, "sheetcurrent", kwargs, rtol=1e-10, atol=1e-14
    )
