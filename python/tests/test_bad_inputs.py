import numpy as np
import pytest
from pymagba.currents import CircularCurrent, PathCurrent, SheetCurrent, TriangleCurrent
from pymagba.magnets import (
    CuboidMagnet,
    CylinderMagnet,
    Dipole,
    MeshMagnet,
    SourceCollection,
    SphereMagnet,
    TetrahedronMagnet,
    TriangleMagnet,
)
from pymagba.sensors import HallLatch, HallSwitch, LinearHallSensor, ObserverCollection


def test_arraylike3_invalid():
    # Wrong number of elements
    with pytest.raises(ValueError, match="Expected exactly 3 elements"):
        SphereMagnet(position=[1, 2])

    with pytest.raises(ValueError, match="Expected exactly 3 elements"):
        SphereMagnet(position=np.array([1.0, 2.0, 3.0, 4.0]))

    # Wrong types
    with pytest.raises(TypeError):
        SphereMagnet(position="abc")


def test_pointslike_invalid():
    m = Dipole(moment=[0, 0, 1])
    # Wrong dimensionality for pointslike
    with pytest.raises(TypeError):
        m.compute_B([[1, 2]])  # Should be list of 3-element lists or a 3-element list


def test_sphere_magnet_validation():
    with pytest.raises(ValueError, match="Diameter cannot be negative"):
        SphereMagnet(diameter=-1.0)

    with pytest.raises(ValueError, match="Diameter cannot be negative"):
        SphereMagnet(diameter=0.0)

    s = SphereMagnet(diameter=1.0)
    with pytest.raises(ValueError, match="Diameter cannot be negative"):
        s.diameter = -0.5


def test_cylinder_magnet_validation():
    with pytest.raises(ValueError, match="Diameter cannot be negative"):
        CylinderMagnet(diameter=-1.0)

    with pytest.raises(ValueError, match="Height cannot be negative"):
        CylinderMagnet(height=0.0)

    c = CylinderMagnet(diameter=1.0, height=1.0)
    with pytest.raises(ValueError, match="Diameter cannot be negative"):
        c.diameter = 0
    with pytest.raises(ValueError, match="Height cannot be negative"):
        c.height = -1.0


def test_cuboid_magnet_validation():
    with pytest.raises(ValueError, match="Dimensions must be non-negative"):
        CuboidMagnet(dimensions=[1.0, -1.0, 1.0])

    c = CuboidMagnet(dimensions=[1, 1, 1])
    with pytest.raises(ValueError, match="Dimensions must be non-negative"):
        c.dimensions = [1, 0, -1]


def test_circular_current_validation():
    with pytest.raises(ValueError, match="Diameter must be positive"):
        CircularCurrent(diameter=-1.0)

    cur = CircularCurrent(diameter=1.0)
    with pytest.raises(ValueError, match="Diameter must be positive"):
        cur.diameter = 0


def test_path_current_validation():
    with pytest.raises(TypeError, match="Expected a NumPy array of shape"):
        PathCurrent(vertices=[[1.0, 2.0], [3.0, 4.0]])
    with pytest.raises(TypeError, match="Expected a NumPy array of shape"):
        PathCurrent(vertices=[[0, 0, 0]]).vertices = [[1.0, 2.0], [3.0, 4.0]]


def test_triangle_current_validation():
    with pytest.raises(ValueError):
        TriangleCurrent(vertices=[[1.0, 2.0], [3.0, 4.0]])
    with pytest.raises(ValueError):
        TriangleCurrent().vertices = [[1.0, 2.0], [3.0, 4.0]]
    with pytest.raises(ValueError, match="Expected exactly 3 elements"):
        TriangleCurrent(current_density=[1.0, 2.0])


def test_sheet_current_validation():
    with pytest.raises(TypeError):
        SheetCurrent(vertices=[[1.0, 2.0], [3.0, 4.0]])
    with pytest.raises(ValueError, match=r"(?i)(missing vertex|index out of bounds)"):
        SheetCurrent(
            current_densities=[[1.0, 2.0, 3.0]],
            vertices=[[-0.1, -0.1, -0.1], [0.1, -0.1, -0.1], [0.0, 0.1, -0.1]],
            faces=[[0, 2, 4]],  # Out of bounds
        )


def test_mesh_magnet_validation():
    with pytest.raises(TypeError):
        MeshMagnet(vertices=[[1.0, 2.0], [3.0, 4.0]])
    with pytest.raises(ValueError, match=r"(?i)(missing vertex|index out of bounds)"):
        MeshMagnet(
            vertices=[[-0.1, -0.1, -0.1], [0.1, -0.1, -0.1], [0.0, 0.1, -0.1]],
            faces=[[0, 2, 4]],  # Out of bounds
        )


def test_linear_hall_sensor_validation():
    with pytest.raises(ValueError, match="Supply voltage must be positive"):
        LinearHallSensor(supply_voltage=-5.0)

    s = LinearHallSensor(supply_voltage=5.0)
    with pytest.raises(ValueError, match="Supply voltage must be positive"):
        s.supply_voltage = 0


def test_hall_switch_validation():
    with pytest.raises(ValueError, match="B_OP must be non-negative"):
        HallSwitch(b_op=-0.01)

    sw = HallSwitch(b_op=0.01)
    with pytest.raises(ValueError, match="B_OP must be non-negative"):
        sw.b_op = -0.001


def test_hall_latch_validation():
    with pytest.raises(ValueError, match="B_OP must be greater than B_RP"):
        HallLatch(b_op=0.01, b_rp=0.01)

    with pytest.raises(ValueError, match="B_OP must be greater than B_RP"):
        HallLatch(b_op=0.01, b_rp=0.02)


def test_collection_validation():
    # SourceCollection with non-source
    with pytest.raises(
        TypeError, match="source must be a valid Magnet, Current, or SourceCollection"
    ):
        SourceCollection(sources=[123])

    sc = SourceCollection()
    with pytest.raises(
        TypeError, match="source must be a valid Magnet, Current, or SourceCollection"
    ):
        sc.append("not a source")

    # ObserverCollection with non-sensor
    with pytest.raises(
        TypeError, match="sensors must be LinearHallSensor, HallSwitch, or HallLatch"
    ):
        ObserverCollection(sensors=[SphereMagnet()])

    oc = ObserverCollection()
    with pytest.raises(
        TypeError, match="sensors must be LinearHallSensor, HallSwitch, or HallLatch"
    ):
        oc.append(Dipole())


def test_quaternion_validation():
    # Invalid quaternions (zero norm, nan, inf) must raise ValueError
    for q in ([0, 0, 0, 0], [0, 0, 0, float("nan")], [0, 0, 0, float("inf")]):
        with pytest.raises(ValueError):
            Dipole(moment=[0, 0, 1], orientation=q)

    # Extreme magnitudes must be scaled to avoid overflow/underflow
    for q in ([0, 0, 0, 1e308], [0, 0, 0, 1e-300], [0, 0, 2, 0]):
        d = Dipole(moment=[0, 0, 1], orientation=q)
        quat = d.orientation.as_quat()
        assert np.isfinite(quat).all()
        assert np.isclose(np.linalg.norm(quat), 1.0)
        assert np.isfinite(d.compute_B([0, 0, 2])).all()

    # Setter failure must preserve old state
    m = Dipole(moment=[0, 0, 1])
    orig_quat = m.orientation.as_quat()
    with pytest.raises(ValueError):
        m.orientation = [0, 0, 0, 0]
    np.testing.assert_allclose(m.orientation.as_quat(), orig_quat)

    with pytest.raises(ValueError):
        m.rotate([0, 0, 0, 0])
    np.testing.assert_allclose(m.orientation.as_quat(), orig_quat)

    with pytest.raises(ValueError):
        m.rotate_anchor([0, 0, 0, 0], anchor=[0, 0, 0])
    np.testing.assert_allclose(m.orientation.as_quat(), orig_quat)


def test_sensor_sensitive_axis_validation():
    for cls in (HallSwitch, HallLatch, LinearHallSensor):
        # Zero norm, NaN, or Inf sensitive axis must raise ValueError
        for bad_axis in ([0, 0, 0], [0, 0, float("nan")], [0, 0, float("inf")]):
            with pytest.raises(ValueError):
                cls(sensitive_axis=bad_axis)

        # Setter rejection must preserve old state
        s = cls(sensitive_axis=[0, 0, 1])
        with pytest.raises(ValueError):
            s.sensitive_axis = [0, 0, 0]
        np.testing.assert_allclose(s.sensitive_axis, [0, 0, 1])

        # Non-unit and extreme axes must normalize properly without overflow/underflow
        s.sensitive_axis = [0, 0, 5]
        np.testing.assert_allclose(s.sensitive_axis, [0, 0, 1])

        s.sensitive_axis = [0, 0, 1e308]
        np.testing.assert_allclose(s.sensitive_axis, [0, 0, 1])

        s.sensitive_axis = [0, 0, 1e-300]
        np.testing.assert_allclose(s.sensitive_axis, [0, 0, 1])


def test_free_functions_geometry_validation():
    from pymagba.fields import circular_B, cuboid_B, cylinder_B, sphere_B

    # cylinder_B
    with pytest.raises(ValueError):
        cylinder_B([0, 0, 2], diameter=-1.0)
    with pytest.raises(ValueError):
        cylinder_B([0, 0, 2], diameter=0.0)
    with pytest.raises(ValueError):
        cylinder_B([0, 0, 2], height=-1.0)
    with pytest.raises(ValueError):
        cylinder_B([0, 0, 2], height=0.0)
    with pytest.raises(ValueError):
        cylinder_B([0, 0, 2], orientation=[0, 0, 0, 0])

    # sphere_B
    with pytest.raises(ValueError):
        sphere_B([0, 0, 2], diameter=-1.0)
    with pytest.raises(ValueError):
        sphere_B([0, 0, 2], diameter=0.0)

    # circular_B
    with pytest.raises(ValueError):
        circular_B([0, 0, 2], diameter=-1.0)
    with pytest.raises(ValueError):
        circular_B([0, 0, 2], diameter=0.0)

    # cuboid_B
    with pytest.raises(ValueError):
        cuboid_B([0, 0, 2], dimensions=[-1.0, 1.0, 1.0])


def test_setter_preserves_old_state_on_failure():
    c = CylinderMagnet(diameter=1.0, height=2.0)
    with pytest.raises(ValueError):
        c.diameter = -1.0
    assert c.diameter == 1.0

    with pytest.raises(ValueError):
        c.height = -1.0
    assert c.height == 2.0

    sw = HallSwitch(b_op=0.01)
    with pytest.raises(ValueError):
        sw.b_op = -0.01
    assert sw.b_op == 0.01

    hl = HallLatch(b_op=0.01, b_rp=-0.01)
    with pytest.raises(ValueError):
        hl.b_op = -0.02
    assert hl.b_op == 0.01

    with pytest.raises(ValueError):
        hl.b_rp = 0.02
    assert hl.b_rp == -0.01


def test_pickle_invalid_state_rejected():
    c = CylinderMagnet()
    with pytest.raises(ValueError):
        c.__setstate__(
            {
                "position": [0, 0, 0],
                "orientation": [0, 0, 0, 0],
                "diameter": 1.0,
                "height": 1.0,
                "polarization": [0, 0, 1],
            }
        )
    with pytest.raises(ValueError):
        c.__setstate__(
            {
                "position": [0, 0, 0],
                "orientation": [0, 0, 0, 1],
                "diameter": -1.0,
                "height": 1.0,
                "polarization": [0, 0, 1],
            }
        )


# https://github.com/p-sira/pymagba/pull/43
ALL_SERIALIZABLE_CLASSES = [
    CylinderMagnet,
    SphereMagnet,
    CuboidMagnet,
    Dipole,
    TriangleMagnet,
    TetrahedronMagnet,
    MeshMagnet,
    SourceCollection,
    CircularCurrent,
    PathCurrent,
    TriangleCurrent,
    SheetCurrent,
    HallSwitch,
    HallLatch,
    LinearHallSensor,
    ObserverCollection,
]


@pytest.mark.parametrize("cls", ALL_SERIALIZABLE_CLASSES)
def test_setstate_missing_keys_raises_keyerror(cls):
    # https://github.com/p-sira/pymagba/pull/43
    obj = cls()
    # Missing all keys must raise KeyError (caught by except Exception, not PanicException)
    with pytest.raises(KeyError, match="Missing required state key"):
        obj.__setstate__({})

    # Omitting any individual required key must raise KeyError
    valid_state = obj.__getstate__()
    for key in list(valid_state.keys()):
        # _schema_version is internal; local_offsets and latch state are optional for legacy compatibility
        if key.startswith("_") or key in ("local_offsets", "state"):
            continue
        corrupted_state = dict(valid_state)
        del corrupted_state[key]
        with pytest.raises(KeyError, match=f"Missing required state key: '{key}'"):
            obj.__setstate__(corrupted_state)


def test_setstate_failure_preserves_original_state():
    # https://github.com/p-sira/pymagba/pull/43
    c = CylinderMagnet(diameter=2.5, height=3.5, position=[1.0, 2.0, 3.0])
    orig_b = c.compute_B([0, 0, 5.0])

    # Failed __setstate__ with missing key
    with pytest.raises(KeyError):
        c.__setstate__({})
    assert c.diameter == 2.5
    assert c.height == 3.5
    np.testing.assert_allclose(c.position, [1.0, 2.0, 3.0])
    np.testing.assert_allclose(c.compute_B([0, 0, 5.0]), orig_b)

    # Failed __setstate__ with invalid numerical value
    state = c.__getstate__()
    state["diameter"] = -1.0
    with pytest.raises(ValueError):
        c.__setstate__(state)
    assert c.diameter == 2.5
    assert c.height == 3.5
    np.testing.assert_allclose(c.position, [1.0, 2.0, 3.0])
    np.testing.assert_allclose(c.compute_B([0, 0, 5.0]), orig_b)


def test_collection_setstate_invalid_children_and_offsets():
    # https://github.com/p-sira/pymagba/pull/43
    sc = SourceCollection([Dipole()])
    orig_len = len(sc)
    orig_b = sc.compute_B([0, 0, 2.0])

    # Restoring collection with invalid source type must raise TypeError
    with pytest.raises(
        TypeError, match="source must be a valid Magnet, Current, or SourceCollection"
    ):
        sc.__setstate__(
            {
                "sources": [123],
                "position": [0, 0, 0],
                "orientation": [0, 0, 0, 1],
                "local_offsets": [([0, 0, 0], [0, 0, 0, 1])],
            }
        )
    assert len(sc) == orig_len
    np.testing.assert_allclose(sc.compute_B([0, 0, 2.0]), orig_b)

    # Legacy state with invalid source type must also raise TypeError
    with pytest.raises(
        TypeError, match="source must be a valid Magnet, Current, or SourceCollection"
    ):
        sc.__setstate__(
            {
                "sources": ["not_a_source"],
                "position": [0, 0, 0],
                "orientation": [0, 0, 0, 1],
            }
        )
    assert len(sc) == orig_len
    np.testing.assert_allclose(sc.compute_B([0, 0, 2.0]), orig_b)

    # Mismatched local_offsets length
    with pytest.raises(ValueError, match="Number of local_offsets"):
        sc.__setstate__(
            {
                "sources": [Dipole()],
                "position": [0, 0, 0],
                "orientation": [0, 0, 0, 1],
                "local_offsets": [([0, 0, 0], [0, 0, 0, 1]), ([0, 0, 0], [0, 0, 0, 1])],
            }
        )
    assert len(sc) == orig_len

    # ObserverCollection with invalid sensor
    oc = ObserverCollection([HallSwitch()])
    orig_oc_len = len(oc)
    with pytest.raises(
        TypeError, match="sensors must be LinearHallSensor, HallSwitch, or HallLatch"
    ):
        oc.__setstate__(
            {
                "sensors": [Dipole()],
                "position": [0, 0, 0],
                "orientation": [0, 0, 0, 1],
                "local_offsets": [([0, 0, 0], [0, 0, 0, 1])],
            }
        )
    assert len(oc) == orig_oc_len

    with pytest.raises(ValueError, match="Number of local_offsets"):
        oc.__setstate__(
            {
                "sensors": [HallSwitch()],
                "position": [0, 0, 0],
                "orientation": [0, 0, 0, 1],
                "local_offsets": [],
            }
        )
    assert len(oc) == orig_oc_len


def test_sheet_current_density_face_count_matching():
    # https://github.com/p-sira/pymagba/pull/43
    from pymagba.fields import sheet_current_B

    verts = [[-0.1, -0.1, -0.1], [0.1, -0.1, -0.1], [0.0, 0.1, -0.1], [0.0, 0.0, 0.1]]
    faces = [[0, 2, 1], [0, 1, 3], [1, 2, 3], [0, 3, 2]]  # 4 faces

    # 1. Exact count (4) succeeds
    s_exact = SheetCurrent(
        vertices=verts, faces=faces, current_densities=[[1.0, 0.0, 0.0]] * 4
    )
    b_exact = s_exact.compute_B([0, 0, 0.5])
    assert not np.allclose(b_exact, 0.0)

    # 2. Omitted current_densities defaults to zero densities per face
    s_omitted = SheetCurrent(vertices=verts, faces=faces, current_densities=None)
    b_omitted = s_omitted.compute_B([0, 0, 0.5])
    np.testing.assert_allclose(b_omitted, 0.0)
    assert len(s_omitted.current_densities) == 4
    np.testing.assert_allclose(s_omitted.current_densities, [[0.0, 0.0, 0.0]] * 4)

    # 3. Too few densities (1 instead of 4) raises ValueError
    with pytest.raises(
        ValueError,
        match=r"Number of current densities \(1\) must match number of faces \(4\)",
    ):
        SheetCurrent(vertices=verts, faces=faces, current_densities=[[1.0, 0.0, 0.0]])

    # 4. Too many densities (5 instead of 4) raises ValueError
    with pytest.raises(
        ValueError,
        match=r"Number of current densities \(5\) must match number of faces \(4\)",
    ):
        SheetCurrent(
            vertices=verts, faces=faces, current_densities=[[1.0, 0.0, 0.0]] * 5
        )

    # 5. Deserialization (__setstate__) density count mismatch raises ValueError
    state = s_exact.__getstate__()
    state["current_densities"] = [[1.0, 0.0, 0.0]]  # 1 instead of 4
    with pytest.raises(
        ValueError,
        match=r"Number of current densities \(1\) must match number of faces \(4\)",
    ):
        s_exact.__setstate__(state)
    # Verify s_exact remains intact
    assert len(s_exact.current_densities) == 4
    np.testing.assert_allclose(s_exact.compute_B([0, 0, 0.5]), b_exact)

    # 6. Free function sheet_current_B density count matching
    b_func_exact = sheet_current_B(
        [[0, 0, 0.5]],
        vertices=verts,
        faces=faces,
        current_densities=[[1.0, 0.0, 0.0]] * 4,
    )
    np.testing.assert_allclose(b_exact, b_func_exact)

    b_func_omitted = sheet_current_B(
        [[0, 0, 0.5]], vertices=verts, faces=faces, current_densities=None
    )
    np.testing.assert_allclose(b_func_omitted, 0.0)

    with pytest.raises(
        ValueError,
        match=r"Number of current densities \(1\) must match number of faces \(4\)",
    ):
        sheet_current_B(
            [[0, 0, 0.5]],
            vertices=verts,
            faces=faces,
            current_densities=[[1.0, 0.0, 0.0]],
        )

    with pytest.raises(
        ValueError,
        match=r"Number of current densities \(5\) must match number of faces \(4\)",
    ):
        sheet_current_B(
            [[0, 0, 0.5]],
            vertices=verts,
            faces=faces,
            current_densities=[[1.0, 0.0, 0.0]] * 5,
        )
