# Magba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import numpy as np
from pymagba.currents import CircularCurrent
from tests.testing_util import run_test_general

def test_circular_current():
    kwargs = {
        "diameter": 1.0,
        "current": 1.0,
    }
    run_test_general(CircularCurrent, "circularcurrent", kwargs, rtol=1e-15, atol=1e-15)
