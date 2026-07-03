# Magba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import numpy as np
from pymagba.magnets import CuboidMagnet
from tests.testing_util import run_test_general

def test_cuboid():
    kwargs = {
        "dimensions": np.array((0.1, 0.2, 0.3)),
        "polarization": np.array((1.0, 2.0, 3.0)),
    }
    run_test_general(CuboidMagnet, "cuboid", kwargs, rtol=5e-13, atol=1e-14)
