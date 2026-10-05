import numpy as np
import pytest
from pymagba.magnets import CuboidMagnet, CylinderMagnet, SourceCollection
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


def test_child_indexing_methods():
    # Source child
    m1 = CylinderMagnet(position=[0, 0, 0], polarization=[0, 0, 1])
    s_col = SourceCollection([m1])
    s_child = s_col[0]

    # Reference independent source
    m_ref = CylinderMagnet(position=[0, 0, 0], polarization=[0, 0, 1])

    # Test field function on child
    np.testing.assert_allclose(
        s_child.compute_B([[0, 0, 2]]), m_ref.compute_B([[0, 0, 2]])
    )

    # Test spatial transformation on child
    s_child.translate([0.1, 0, 0])
    m_ref.translate([0.1, 0, 0])
    np.testing.assert_allclose(s_child.position, [0.1, 0.0, 0.0])
    np.testing.assert_allclose(
        s_child.compute_B([[0, 0, 2]]), m_ref.compute_B([[0, 0, 2]])
    )

    # Observer child
    s1 = LinearHallSensor(position=[0, 0, 0])
    o_col = ObserverCollection([s1])
    o_child = o_col[0]

    # Reference independent observer
    s_ref = LinearHallSensor(position=[0, 0, 0])

    # Test read function on child
    np.testing.assert_allclose(o_child.read_voltage(m1), s_ref.read_voltage(m1))

    # Test spatial transformation on child
    o_child.translate([0.1, 0, 0])
    s_ref.translate([0.1, 0, 0])
    np.testing.assert_allclose(o_child.position, [0.1, 0.0, 0.0])
    np.testing.assert_allclose(o_child.read_voltage(m1), s_ref.read_voltage(m1))


def test_source_child_mutation():
    # Mutating indexed child must reflect in collection compute_B
    from pymagba.magnets import Dipole

    point = [0, 0, 2]
    magnet = Dipole(moment=[0, 0, 1])
    collection = SourceCollection([magnet])

    b_initial = collection.compute_B(point)
    magnet.moment = [0, 0, 2]

    b_mutated = collection.compute_B(point)
    np.testing.assert_allclose(b_mutated, 2 * b_initial, atol=0)
    np.testing.assert_allclose(
        collection.compute_B(point), collection[0].compute_B(point), atol=0
    )


def test_source_child_shared_between_collections():
    # Child used by multiple parents
    from pymagba.magnets import Dipole

    m = Dipole(moment=[0, 0, 1])
    col = SourceCollection([m], position=[0, 0, 0])
    _ = SourceCollection([m], position=[0, 0, 1])

    m.moment = [0, 0, 3]
    np.testing.assert_allclose(col.compute_B([0, 0, 2]), m.compute_B([0, 0, 2]), atol=0)


def test_nested_collection_child_mutation():
    # Nested collection child mutation
    from pymagba.magnets import Dipole

    m = Dipole(moment=[0, 0, 1])
    inner = SourceCollection([m])
    outer = SourceCollection([inner])

    m.moment = [0, 0, 4]
    np.testing.assert_allclose(
        outer.compute_B([0, 0, 2]), inner.compute_B([0, 0, 2]), atol=0
    )


def test_nested_collection_transformation_propagation():
    # Transformation propagation through nested collections
    from pymagba.magnets import CylinderMagnet, Dipole

    child_pos = [0.1, 0.2, 0.3]
    m = CylinderMagnet(position=child_pos, polarization=[0, 0, 1])
    inner = SourceCollection([m], position=[0, 0, 1])
    outer = SourceCollection([inner], position=[0, 0, 2])

    ref = CylinderMagnet(position=child_pos, polarization=[0, 0, 1])

    # 1. Translate outer collection
    delta_trans = [1.0, 2.0, 3.0]
    outer.translate(delta_trans)
    ref.translate(delta_trans)

    pt = [2.0, 3.0, 5.0]
    np.testing.assert_allclose(outer.compute_B(pt), ref.compute_B(pt), atol=0)

    # 2. Rotate outer collection around anchor
    quat_x_90 = [0.70710678, 0.0, 0.0, 0.70710678]
    outer.rotate_anchor(quat_x_90, anchor=outer.position)
    ref.rotate_anchor(quat_x_90, anchor=outer.position)

    np.testing.assert_allclose(outer.compute_B(pt), ref.compute_B(pt), atol=0)

    # 3. Multi-level nesting (depth 3)
    d = Dipole(moment=[0, 0, 1], position=[0, 0, 0])
    level1 = SourceCollection([d])
    level2 = SourceCollection([level1])
    level3 = SourceCollection([level2])

    d_ref = Dipole(moment=[0, 0, 1], position=[0, 0, 0])

    level3.translate([0, 1, 2])
    d_ref.translate([0, 1, 2])

    level3.rotate(quat_x_90)
    d_ref.rotate(quat_x_90)

    np.testing.assert_allclose(level3.compute_B(pt), d_ref.compute_B(pt), atol=0)


def test_collection_containment_cycle_rejection():
    # 1. Direct self-append
    a = SourceCollection()
    with pytest.raises(ValueError, match="circular|Cannot add collection to itself"):
        a.append(a)
    assert len(a) == 0

    # 2. Indirect cycle: a -> b, b -> a
    b = SourceCollection([a])
    with pytest.raises(ValueError, match="circular|Cannot add collection to itself"):
        a.append(b)
    assert len(a) == 0

    # 3. Two empty collections, append a to b, then b to a
    col1 = SourceCollection()
    col2 = SourceCollection()
    col1.append(col2)
    with pytest.raises(ValueError, match="circular|Cannot add collection to itself"):
        col2.append(col1)
    assert len(col2) == 0

    # 4. Multi-level indirect cycle (3 levels): c -> b -> a, then a -> c
    l1 = SourceCollection()
    l2 = SourceCollection([l1])
    l3 = SourceCollection([l2])
    with pytest.raises(ValueError, match="circular|Cannot add collection to itself"):
        l1.append(l3)
    assert len(l1) == 0

    # Verify original collection is still valid and functional
    m = CylinderMagnet(diameter=0.01, height=0.01)
    l1.append(m)
    assert len(l1) == 1
    B = l1.compute_B([0, 0, 0.05])
    assert B.shape == (1, 3)


def test_collection_setstate_cycle_rejection():
    a = SourceCollection()
    state = a.__getstate__()

    # Self-cycle via setstate
    state["sources"] = [a]
    with pytest.raises(ValueError, match="circular|Cannot restore collection"):
        a.__setstate__(state)
    assert len(a) == 0

    # Indirect cycle via setstate
    b = SourceCollection([a])
    state["sources"] = [b]
    with pytest.raises(ValueError, match="circular|Cannot restore collection"):
        a.__setstate__(state)
    assert len(a) == 0


def test_collection_valid_dag_sharing():
    # Diamond graph (DAG) - shared child magnet
    leaf = CylinderMagnet(diameter=0.01, height=0.01)
    a = SourceCollection([leaf])
    b = SourceCollection([leaf])
    c = SourceCollection([a, b])
    assert len(c) == 2

    pt = [0, 0, 0.05]
    B_c = c.compute_B(pt)
    B_leaf = leaf.compute_B(pt)
    np.testing.assert_allclose(B_c, 2 * B_leaf, atol=0)

    # Diamond graph - shared inner collection
    inner = SourceCollection([leaf])
    outer1 = SourceCollection([inner])
    outer2 = SourceCollection([inner])
    top = SourceCollection([outer1, outer2])
    assert len(top) == 2
    B_top = top.compute_B(pt)
    np.testing.assert_allclose(B_top, 2 * B_leaf, atol=0)

    # Appending the same inner collection twice (valid DAG)
    multi = SourceCollection()
    multi.append(inner)
    multi.append(inner)
    assert len(multi) == 2
    np.testing.assert_allclose(multi.compute_B(pt), 2 * B_leaf, atol=0)


def test_collection_gc_cyclic_collection():
    import gc
    import weakref

    # 1. Subclass attribute reference cycle
    class SubCollection(SourceCollection):
        self_ref: "SubCollection"

    sub = SubCollection()
    sub.self_ref = sub
    sub_ref = weakref.ref(sub)
    del sub
    gc.collect()
    assert sub_ref() is None, "Subclass self-reference cycle was not collected by GC"

    # 2. SourceCollection child backreference cycle
    class SubMagnet(CylinderMagnet):
        parent: SourceCollection

    child = SubMagnet(diameter=0.01, height=0.01)
    scol = SourceCollection([child])
    child.parent = scol
    scol_ref = weakref.ref(scol)
    child_ref = weakref.ref(child)
    del scol, child
    gc.collect()
    assert scol_ref() is None, "SourceCollection cycle was not collected by GC"
    assert child_ref() is None, "Child magnet cycle was not collected by GC"

    # 3. ObserverCollection sensor backreference cycle
    class SubSensor(LinearHallSensor):
        parent: ObserverCollection

    sensor = SubSensor()
    ocol = ObserverCollection([sensor])
    sensor.parent = ocol
    ocol_ref = weakref.ref(ocol)
    sensor_ref = weakref.ref(sensor)
    del ocol, sensor
    gc.collect()
    assert ocol_ref() is None, "ObserverCollection cycle was not collected by GC"
    assert sensor_ref() is None, "Sensor cycle was not collected by GC"
