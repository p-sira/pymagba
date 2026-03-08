import pytest
import numpy as np
from pymagba.magnets import CylinderMagnet, CuboidMagnet, SourceCollection
from pymagba.sensors import LinearHallSensor, ObserverCollection


def test_source_collection_methods():
    m1 = CylinderMagnet(polarization=[0, 0, 1], diameter=0.01, height=0.01)
    m2 = CuboidMagnet(polarization=[0, 0, 1], dimensions=[0.01, 0.01, 0.01])

    col = SourceCollection([m1, m2])

    # Test len
    assert len(col) == 2

    # Test indexing
    assert col[0] is m1
    assert col[1] is m2
    assert col[-1] is m2
    assert col[-2] is m1

    with pytest.raises(IndexError):
        _ = col[2]
    with pytest.raises(IndexError):
        _ = col[-3]

    # Test append
    m3 = CylinderMagnet(polarization=[0, 0, 1], diameter=0.02, height=0.02)
    col.append(m3)
    assert len(col) == 3
    assert col[2] is m3

    # Verify B field calculation still works and includes the new magnet
    B = col.compute_B([0, 0, 0.05])
    assert B.shape == (1, 3)


def test_observer_collection_methods():
    s1 = LinearHallSensor(sensitivity=1.0)
    s2 = LinearHallSensor(sensitivity=2.0)

    col = ObserverCollection([s1, s2])

    # Test len
    assert len(col) == 2

    # Test indexing
    assert col[0] is s1
    assert col[1] is s2
    assert col[-1] is s2

    with pytest.raises(IndexError):
        _ = col[2]

    # Test append
    s3 = LinearHallSensor(sensitivity=3.0)
    col.append(s3)
    assert len(col) == 3
    assert col[2] is s3


if __name__ == "__main__":
    test_source_collection_methods()
    test_observer_collection_methods()
    print("All tests passed!")
