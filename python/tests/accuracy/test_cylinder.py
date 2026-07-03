# Magba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import numpy as np
from pymagba.magnets import CylinderMagnet
from tests.testing_util import run_test_general

def test_cylinder():
    kwargs = {
        "diameter": 0.1,
        "height": 0.2,
        "polarization": np.array((1.0, 2.0, 3.0)),
    }
    run_test_general(CylinderMagnet, "cylinder", kwargs, rtol=2e-8, atol=1e-14)
