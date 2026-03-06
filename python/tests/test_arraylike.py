import numpy as np
import pytest
from pymagba.magnets import Dipole, CuboidMagnet, CylinderMagnet
from pymagba.sensors import HallSwitch, HallLatch, LinearHallSensor
from scipy.spatial.transform import Rotation


def test_array_like():
    # Dipole
    pos = np.array([0.1, 0.2, 0.3])
    mom = np.array([0.0, 0.0, 1.0])
    d = Dipole(position=pos, moment=mom)
    d.position = np.array([0.5, 0.6, 0.7])
    d.moment = np.array([1.0, 0.0, 0.0])
    assert np.allclose(d.position, [0.5, 0.6, 0.7])
    assert np.allclose(d.moment, [1.0, 0.0, 0.0])

    # Cuboid
    dim = np.array([0.01, 0.01, 0.01])
    pol = np.array([0.0, 0.0, 1.0])
    c = CuboidMagnet(dimensions=dim, polarization=pol)
    c.dimensions = np.array([0.02, 0.02, 0.02])
    c.polarization = np.array([0.0, 1.0, 0.0])
    assert np.allclose(c.dimensions, [0.02, 0.02, 0.02])
    assert np.allclose(c.polarization, [0.0, 1.0, 0.0])

    # Cylinder
    cyl = CylinderMagnet(polarization=np.array([0.0, 1.0, 0.0]))
    cyl.polarization = np.array([1.0, 0.0, 0.0])
    assert np.allclose(cyl.polarization, [1.0, 0.0, 0.0])

    # LinearHallSensor
    s = LinearHallSensor(sensitive_axis=np.array([1.0, 0.0, 0.0]))
    s.sensitive_axis = np.array([0.0, 0.0, 1.0])
    assert np.allclose(s.sensitive_axis, [0.0, 0.0, 1.0])

    # HallSwitch
    sw = HallSwitch(position=(0, 0, 1), sensitive_axis=np.array([0, 1, 0]))
    sw.sensitive_axis = [1, 0, 0]
    assert np.allclose(sw.sensitive_axis, [1, 0, 0])

    # HallLatch
    la = HallLatch(orientation=[0, 0, 0, 1])
    assert np.allclose(la.orientation.as_quat(), [0, 0, 0, 1])

    # compute_B variants
    m = Dipole(moment=[0, 0, 1])

    # Single point list
    B1 = m.compute_B([0, 0, 0.01])
    assert B1.shape == (1, 3)

    # Multiple points list
    B2 = m.compute_B([[0, 0, 0.01], [0, 0, 0.02]])
    assert B2.shape == (2, 3)
    assert np.allclose(B1[0], B2[0])

    # Tuple
    B3 = m.compute_B(((0, 0, 0.01),))
    assert B3.shape == (1, 3)
    assert np.allclose(B1[0], B3[0])
