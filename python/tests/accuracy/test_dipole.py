# Magba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import numpy as np
from pymagba.magnets import Dipole
from tests.testing_util import run_test_general

def test_dipole():
    kwargs = {
        "moment": np.array((1.0, 2.0, 3.0)),
    }
    run_test_general(Dipole, "dipole", kwargs, rtol=1e-15, atol=1e-15)
