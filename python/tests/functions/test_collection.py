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


def test_source_collection_spatial_manipulation():
    child_pos = [0.1, 0.2, 0.3]
    m1 = CylinderMagnet(position=child_pos, polarization=[0, 0, 1])
    col = SourceCollection([m1])
    
    # Translate collection
    col.translate([0, 0, 1])
    
    # Direct translation for comparison
    m2 = CylinderMagnet(position=child_pos, polarization=[0, 0, 1])
    m2.translate([0, 0, 1])
    
    B_col = col.compute_B([[0, 0, 2]])
    B_m2 = m2.compute_B([[0, 0, 2]])
    
    np.testing.assert_allclose(B_col, B_m2)
    
    # Verify child pose (position) remains at local offset
    np.testing.assert_allclose(col[0].position, child_pos)
    
    # Rotate collection (90 degrees around x-axis, quat=[sin(pi/4), 0, 0, cos(pi/4)])
    quat_x_90 = [0.70710678, 0.0, 0.0, 0.70710678]
    col.rotate(quat_x_90)
    m2.rotate_anchor(quat_x_90, anchor=col.position)
    
    B_col_rot = col.compute_B([[0, 0, 2]])
    B_m2_rot = m2.compute_B([[0, 0, 2]])
    
    np.testing.assert_allclose(B_col_rot, B_m2_rot)
    
    # Verify child pose (position) remains unchanged
    np.testing.assert_allclose(col[0].position, child_pos)


def test_observer_collection_spatial_manipulation():
    m1 = CylinderMagnet(position=[0, 0, 0], polarization=[0, 0, 1])
    child_pos = [0.1, 0.2, 0.3]
    
    s1 = LinearHallSensor(position=child_pos)
    col = ObserverCollection([s1])
    
    # Translate collection
    col.translate([0, 0, 1])
    
    # Direct translation for comparison
    s2 = LinearHallSensor(position=child_pos)
    s2.translate([0, 0, 1])
    
    col_read = col.read_all(m1)
    s2_read = s2.read_voltage(m1)
    
    assert len(col_read) == 1
    np.testing.assert_allclose(col_read[0], s2_read)
    
    # Verify child pose (position) remains at local offset
    np.testing.assert_allclose(col[0].position, child_pos)
    
    # Rotate collection
    quat_x_90 = [0.70710678, 0.0, 0.0, 0.70710678]
    col.rotate(quat_x_90)
    s2.rotate_anchor(quat_x_90, anchor=col.position)
    
    col_read_rot = col.read_all(m1)
    s2_read_rot = s2.read_voltage(m1)
    
    np.testing.assert_allclose(col_read_rot[0], s2_read_rot)
    
    # Verify child pose (position) remains unchanged
    np.testing.assert_allclose(col[0].position, child_pos)


if __name__ == "__main__":
    test_source_collection_methods()
    test_observer_collection_methods()
    test_source_collection_spatial_manipulation()
    test_observer_collection_spatial_manipulation()
    print("All tests passed!")
