import numpy as np
from pymagba.magnets import CuboidMagnet, CylinderMagnet, Dipole
from pymagba.sensors import HallLatch, HallSwitch, LinearHallSensor


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


def test_float32_arrays_and_strided():
    from pymagba import fields

    # 1D float32 in ArrayLike3
    pos_f32 = np.array([0.1, 0.2, 0.3], dtype=np.float32)
    mom_f32 = np.array([0.0, 0.0, 1.0], dtype=np.float32)
    d = Dipole(position=pos_f32, moment=mom_f32)
    assert np.allclose(d.position, [0.1, 0.2, 0.3])
    assert np.allclose(d.moment, [0.0, 0.0, 1.0])

    # 1D float32 point in compute_B
    pt_f32 = np.array([0.25, 0.125, 2.0], dtype=np.float32)
    pt_f64 = pt_f32.astype(np.float64)
    b_pt32 = d.compute_B(pt_f32)
    b_pt64 = d.compute_B(pt_f64)
    assert b_pt32.shape == (1, 3)
    np.testing.assert_array_equal(b_pt32, b_pt64)

    # 2D float32 contiguous
    pts_f32 = np.tile(pt_f32, (100, 1))
    pts_f64 = pts_f32.astype(np.float64)
    b_f32 = d.compute_B(pts_f32)
    b_f64 = d.compute_B(pts_f64)
    assert b_f32.shape == (100, 3)
    np.testing.assert_array_equal(b_f32, b_f64)

    # Free function with float32
    bf_32 = fields.dipole_B(pts_f32, moment=[0, 0, 1])
    bf_64 = fields.dipole_B(pts_f64, moment=[0, 0, 1])
    np.testing.assert_array_equal(bf_32, bf_64)

    # Non-contiguous / strided float32
    pts_strided = np.tile(pt_f32, (200, 1))[::2]
    assert not pts_strided.flags["C_CONTIGUOUS"]
    b_strided = d.compute_B(pts_strided)
    np.testing.assert_array_equal(b_strided, b_f32)

    # Fortran-contiguous float32
    pts_fortran = np.asfortranarray(pts_f32)
    assert pts_fortran.flags["F_CONTIGUOUS"] and not pts_fortran.flags["C_CONTIGUOUS"]
    b_fortran = d.compute_B(pts_fortran)
    np.testing.assert_array_equal(b_fortran, b_f32)

    # Empty array (0, 3)
    pts_empty = np.zeros((0, 3), dtype=np.float64)
    b_empty = d.compute_B(pts_empty)
    assert b_empty.shape == (0, 3)

    pts_empty_f32 = np.zeros((0, 3), dtype=np.float32)
    b_empty_f32 = d.compute_B(pts_empty_f32)
    assert b_empty_f32.shape == (0, 3)


def test_gil_release_thread_progress():
    import threading
    import time

    from pymagba import fields

    points = np.tile([0.25, 0.125, 2.0], (300_000, 1))
    magnet = CylinderMagnet(polarization=[1, 2, 3])

    def measure_ticks(fn):
        timestamps = []
        ready, stop = threading.Event(), threading.Event()

        def ticker():
            ready.set()
            while not stop.is_set():
                timestamps.append(time.perf_counter())
                time.sleep(0.001)

        thread = threading.Thread(target=ticker)
        thread.start()
        ready.wait()
        time.sleep(0.005)
        try:
            start = time.perf_counter()
            fn()
            end = time.perf_counter()
        finally:
            stop.set()
            thread.join()

        # Count ticks during fn execution (excluding boundary margins)
        ticks = sum(start + 0.002 < t < end - 0.002 for t in timestamps)
        return ticks

    # Both class method and free function should release the GIL during parallel execution
    class_ticks = measure_ticks(lambda: magnet.compute_B(points))
    func_ticks = measure_ticks(
        lambda: fields.cylinder_B(points, polarization=[1, 2, 3])
    )

    assert class_ticks > 0, f"Expected interior ticker samples, got {class_ticks}"
    assert func_ticks > 0, f"Expected interior ticker samples, got {func_ticks}"
