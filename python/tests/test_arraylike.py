import numpy as np
from pymagba.magnets import Dipole, CuboidMagnet, CylinderMagnet
from pymagba.sensors import HallSwitch, HallLatch, LinearHallSensor


def test_array_like():
    print("Testing ArrayLike support...")

    # Dipole
    pos = np.array([0.1, 0.2, 0.3])
    mom = np.array([0.0, 0.0, 1.0])
    d = Dipole(position=pos, moment=mom)
    print("Dipole created with numpy arrays.")
    d.position = np.array([0.5, 0.6, 0.7])
    d.moment = np.array([1.0, 0.0, 0.0])
    print("Dipole properties set with numpy arrays.")

    # Cuboid
    dim = np.array([0.01, 0.01, 0.01])
    pol = np.array([0.0, 0.0, 1.0])
    c = CuboidMagnet(dimensions=dim, polarization=pol)
    print("Cuboid created with numpy arrays.")
    c.dimensions = np.array([0.02, 0.02, 0.02])
    c.polarization = np.array([0.0, 1.0, 0.0])
    print("Cuboid properties set with numpy arrays.")

    # Cylinder
    cyl = CylinderMagnet(polarization=np.array([0.0, 1.0, 0.0]))
    print("Cylinder created with numpy array.")
    cyl.polarization = np.array([1.0, 0.0, 0.0])
    print("Cylinder properties set with numpy array.")

    # LinearHallSensor
    s = LinearHallSensor(sensitive_axis=np.array([1.0, 0.0, 0.0]))
    print("LinearHallSensor created with numpy array.")
    s.sensitive_axis = np.array([0.0, 0.0, 1.0])
    print("LinearHallSensor properties set with numpy array.")

    # HallSwitch
    sw = HallSwitch(position=(0, 0, 1), sensitive_axis=np.array([0, 1, 0]))
    print("HallSwitch created with tuple and numpy array.")
    sw.sensitive_axis = [1, 0, 0]
    print("HallSwitch properties set with list.")

    # HallLatch
    la = HallLatch(orientation=[0, 0, 0, 1])
    print("HallLatch created with list.")

    print("All tests passed!")


if __name__ == "__main__":
    test_array_like()
