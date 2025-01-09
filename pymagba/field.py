from warnings import warn
import pymagba_binding as pmb
import numpy as np
from numpy.typing import NDArray
from scipy.spatial.transform import Rotation

def cyl_b(
    points: NDArray,
    position: NDArray,
    orientation: Rotation,
    radius: float,
    height: float,
    polarization: NDArray,
) -> NDArray:
    position = tuple(position)
    orientation = tuple(orientation.as_quat(scalar_first=True))
    polarization = tuple(polarization)
    try:
        return pmb.field.cyl_b(
            points, position, orientation, radius, height, polarization
        )
    except RuntimeError as e:
        warn(e)
        return np.zeros(3)
