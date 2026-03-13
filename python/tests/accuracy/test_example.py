# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import numpy as np

from pymagba.magnets import *
from pymagba.sensors import *

magnet = CylinderMagnet(
    position=[0.0, 0.0, 0.01],
    diameter=0.01,
    height=0.005,
    polarization=[0.0, 0.0, 1.0],
)
sensor = LinearHallSensor(
    position=[0.0, 0.0, 0.025],
    sensitive_axis=[0.0, 0.0, 1.0],
    sensitivity=0.05,
    supply_voltage=5.0,
)
b_field = magnet.compute_B([0.0, 0.0, 0.025])  # [[0, 0, 0.01652363]]
voltage = sensor.read_voltage(magnet)  # 2.5008261

assert np.allclose(b_field, [[0, 0, 0.01652363]])
assert np.allclose(voltage, 2.5008261814188892)
