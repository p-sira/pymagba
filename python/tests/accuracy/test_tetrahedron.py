# Magba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import numpy as np
from pymagba.magnets import TetrahedronMagnet
from tests.testing_util import run_test_general

def test_tetrahedron():
    kwargs = {
        "vertices": np.array([[-0.1, -0.1, -0.1], [0.1, -0.1, -0.1], [0.0, 0.1, -0.1], [0.0, 0.0, 0.1]]),
        "polarization": np.array((1.0, 2.0, 3.0)),
    }
    run_test_general(TetrahedronMagnet, "tetrahedron", kwargs, rtol=5e-9, atol=1e-14)
