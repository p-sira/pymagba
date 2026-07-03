# Magba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import numpy as np
from pymagba.magnets import MeshMagnet
from tests.testing_util import run_test_general, _compute_field, get_points, load_test_array
from numpy.testing import assert_allclose
from scipy.spatial.transform import Rotation

def test_mesh():
    kwargs = {
        "vertices": np.array([[-0.1, -0.1, -0.1], [0.1, -0.1, -0.1], [0.0, 0.1, -0.1], [0.0, 0.0, 0.1]]),
        "faces": np.array([[0, 2, 1], [0, 1, 3], [1, 2, 3], [0, 3, 2]]),
        "polarization": np.array((1.0, 2.0, 3.0)),
    }
    run_test_general(MeshMagnet, "triangularmesh", kwargs, rtol=2e-10, atol=1e-12)

def test_mesh_suzanne():
    points = get_points()
    # In magba-testing, suzanne is tested at position (0,0,0) and identity orientation
    magnet = MeshMagnet.from_stl("testing/data/suzanne.stl")
    magnet.polarization = np.array([0.0, 0.0, 1.0])
    
    expected = load_test_array("suzanne-stl.csv")
    assert_allclose(_compute_field(magnet, points), expected, rtol=1e-5, atol=1e-12)
