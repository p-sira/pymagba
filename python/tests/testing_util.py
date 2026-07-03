# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

from pathlib import Path
from typing import Any

import numpy as np
from numpy.testing import assert_allclose
from scipy.spatial.transform import Rotation

from pymagba.utils import FloatArray

TESTING_DATA_DIR = Path("testing/data")

def load_test_array(filename: str) -> FloatArray:
    return np.loadtxt(TESTING_DATA_DIR / filename, delimiter=",")

def get_points() -> FloatArray:
    return load_test_array("points.csv")

def get_points_small() -> FloatArray:
    return load_test_array("points-small.csv")

def _compute_field(obj, points: FloatArray) -> FloatArray:
    """Helper to call compute_B or getB depending on what is available."""
    if hasattr(obj, "compute_B"):
        return obj.compute_B(points)
    elif hasattr(obj, "getB"):
        return obj.getB(points)
    else:
        raise AttributeError(f"Object {obj} has neither compute_B nor getB method")

def _check_close(actual, desired, rtol, atol, max_mismatches=0):
    if actual.shape != desired.shape:
        assert_allclose(actual, desired, rtol=rtol, atol=atol)
        return
    mask = ~np.isclose(actual, desired, rtol=rtol, atol=atol)
    mismatches = np.sum(mask)
    if mismatches > max_mismatches:
        assert_allclose(actual, desired, rtol=rtol, atol=atol)

def run_test_general(
    magnet_class: type,
    name: str,
    kwargs: dict[str, Any],
    rtol: float = 1e-6,
    atol: float = 0.0,
    max_mismatches: int = 0
) -> None:
    """Validate a source object against pre-generated magba-testing CSV results.

    Args:
        magnet_class: The class of the magnetic source.
        name: Base name for the CSV files (e.g. 'cuboid').
        kwargs: Initial kwargs for the magnet.
        rtol: Relative tolerance.
        atol: Absolute tolerance.
        max_mismatches: Maximum allowed mismatched points (useful for singularities).
    """
    points = get_points()
    points_small = get_points_small()

    rotation = Rotation.from_rotvec([np.pi / 7, np.pi / 6, np.pi / 5])
    
    # 1. Base Magnet
    magnet = magnet_class(
        position=(0.1, 0.2, 0.3),
        orientation=rotation,
        **kwargs
    )
    expected = load_test_array(f"{name}.csv")
    _check_close(_compute_field(magnet, points), expected, rtol, atol, max_mismatches)

    # 2. Small Magnet
    small_kwargs = {}
    for k, v in kwargs.items():
        if isinstance(v, np.ndarray) and v.dtype.kind in "fc":
            small_kwargs[k] = v / 10.0
        elif isinstance(v, (float, int)):
            small_kwargs[k] = v / 10.0
        elif isinstance(v, (list, tuple)):
            if k == "faces":
                small_kwargs[k] = v
            else:
                small_kwargs[k] = (np.array(v) / 10.0).tolist()
        else:
            small_kwargs[k] = v

    small_magnet = magnet_class(
        position=(0.03, 0.02, 0.01),
        orientation=rotation,
        **small_kwargs
    )
    expected_small = load_test_array(f"{name}-small.csv")
    _check_close(_compute_field(small_magnet, points_small), expected_small, rtol, atol, max_mismatches)

    # 3. Translate
    magnet.translate((-0.1, -0.2, -0.3))
    expected_trans = load_test_array(f"{name}-translate.csv")
    _check_close(_compute_field(magnet, points), expected_trans, rtol, atol, max_mismatches)

    # 4. Rotate
    magnet.translate((0.1, 0.2, 0.3))
    magnet.rotate(rotation.inv())
    expected_rot = load_test_array(f"{name}-rotate.csv")
    _check_close(_compute_field(magnet, points), expected_rot, rtol, atol, max_mismatches)

    # 5. Rotate and Translate
    magnet.translate((-0.1, -0.2, -0.3))
    expected_rot_trans = load_test_array(f"{name}-rotate-translate.csv")
    _check_close(_compute_field(magnet, points), expected_rot_trans, rtol, atol, max_mismatches)
