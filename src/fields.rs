/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use nalgebra::Vector3;
use pyo3::prelude::*;

#[cfg(feature = "stub-gen")]
use pyo3_stub_gen::derive::gen_stub_pyfunction;

use crate::{
    base::{try_into_slice, try_into_slice_or, ArrayLike3, PointsLike, PyRotation},
    util::vec3_to_pyarray2,
};

#[pymodule]
pub fn fields(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(cylinder_B, m)?)?;
    m.add_function(wrap_pyfunction!(dipole_B, m)?)?;
    m.add_function(wrap_pyfunction!(cuboid_B, m)?)?;
    m.add_function(wrap_pyfunction!(sphere_B, m)?)?;
    m.add_function(wrap_pyfunction!(circular_B, m)?)?;
    Ok(())
}

#[cfg_attr(feature = "stub-gen", gen_stub_pyfunction)]
#[pyfunction]
/// Calculates the magnetic field of a cylindrical magnet.
///
/// Args:
///     points (PointsLike): Points [x, y, z] in meters at which to calculate the field.
///         Can be a single point or an (N, 3) array of points.
///     position (ArrayLike3, optional): Center of the cylinder [x, y, z] in meters.
///         Defaults to [0.0, 0.0, 0.0].
///     orientation (PyRotation, optional): Orientation of the cylinder.
///         Defaults to identity.
///     diameter (float, optional): Diameter of the cylinder in meters.
///         Defaults to 1.0.
///     height (float, optional): Height of the cylinder in meters.
///         Defaults to 1.0.
///     polarization (ArrayLike3, optional): Remanence polarization vector [Bx, By, Bz]
///         in Tesla. Defaults to [0.0, 0.0, 0.0].
///
/// Returns:
///     numpy.ndarray: Magnetic field (N, 3) in Tesla.
#[pyo3(signature = (points, position=None, orientation=None, diameter=1.0, height=1.0, polarization=None))]
pub fn cylinder_B<'py>(
    py: Python<'py>,
    points: PointsLike,
    position: Option<ArrayLike3>,
    orientation: Option<PyRotation>,
    diameter: f64,
    height: f64,
    polarization: Option<ArrayLike3>,
) -> Bound<'py, numpy::PyArray2<f64>> {
    let points = points.0;
    let n = points.len();

    // Map options to defaults
    let pos = try_into_slice!(position);
    let rot = orientation
        .map(|rot| rot.0)
        .unwrap_or_else(nalgebra::UnitQuaternion::identity);
    let pol = try_into_slice_or!(polarization, [0.0, 0.0, 0.0]);

    // Pre-allocate the result buffer
    let mut results: Vec<Vector3<f64>> = vec![Vector3::zeros(); n];

    // Multithreaded computation
    py.detach(|| {
        magba::fields::cylinder_B_batch(
            &points,
            pos.into(),
            rot,
            pol.into(),
            diameter,
            height,
            results.as_mut_slice(),
        );
    });

    vec3_to_pyarray2(py, results)
}

#[cfg_attr(feature = "stub-gen", gen_stub_pyfunction)]
#[pyfunction]
/// Calculates the magnetic field of a magnetic dipole source.
///
/// Args:
///     points (PointsLike): Points [x, y, z] in meters at which to calculate the field.
///         Can be a single point or an (N, 3) array of points.
///     position (ArrayLike3, optional): Position of the dipole [x, y, z] in meters.
///         Defaults to [0.0, 0.0, 0.0].
///     orientation (PyRotation, optional): Orientation of the dipole.
///         Defaults to identity.
///     moment (ArrayLike3, optional): Magnetic dipole moment vector [mx, my, mz] in A·m².
///         Defaults to [0.0, 0.0, 0.0].
///
/// Returns:
///     numpy.ndarray: Magnetic field (N, 3) in Tesla.
#[pyo3(signature = (points, position=None, orientation=None, moment=None))]
pub fn dipole_B<'py>(
    py: Python<'py>,
    points: PointsLike,
    position: Option<ArrayLike3>,
    orientation: Option<PyRotation>,
    moment: Option<ArrayLike3>,
) -> Bound<'py, numpy::PyArray2<f64>> {
    let points = points.0;
    let n = points.len();

    let pos = try_into_slice!(position);
    let rot = orientation
        .map(|rot| rot.0)
        .unwrap_or_else(nalgebra::UnitQuaternion::identity);
    let m = try_into_slice!(moment);

    let mut results: Vec<Vector3<f64>> = vec![Vector3::zeros(); n];

    py.detach(|| {
        magba::fields::dipole_B_batch(&points, pos.into(), rot, m.into(), results.as_mut_slice());
    });

    vec3_to_pyarray2(py, results)
}

#[cfg_attr(feature = "stub-gen", gen_stub_pyfunction)]
#[pyfunction]
/// Calculates the magnetic field of a cuboid magnet.
///
/// Args:
///     points (PointsLike): Points [x, y, z] in meters at which to calculate the field.
///         Can be a single point or an (N, 3) array of points.
///     position (ArrayLike3, optional): Center of the cuboid [x, y, z] in meters.
///         Defaults to [0.0, 0.0, 0.0].
///     orientation (PyRotation, optional): Orientation of the cuboid.
///         Defaults to identity.
///     dimensions (ArrayLike3, optional): Side lengths [dx, dy, dz] in meters.
///         Defaults to [1.0, 1.0, 1.0].
///     polarization (ArrayLike3, optional): Remanence polarization vector [Bx, By, Bz]
///         in Tesla. Defaults to [0.0, 0.0, 0.0].
///
/// Returns:
///     numpy.ndarray: Magnetic field (N, 3) in Tesla.
#[pyo3(signature = (points, position=None, orientation=None, dimensions=None, polarization=None))]
pub fn cuboid_B<'py>(
    py: Python<'py>,
    points: PointsLike,
    position: Option<ArrayLike3>,
    orientation: Option<PyRotation>,
    dimensions: Option<ArrayLike3>,
    polarization: Option<ArrayLike3>,
) -> Bound<'py, numpy::PyArray2<f64>> {
    let points = points.0;
    let n = points.len();

    let pos = try_into_slice!(position);
    let rot = orientation
        .map(|rot| rot.0)
        .unwrap_or_else(nalgebra::UnitQuaternion::identity);
    let dim = dimensions.map(|d| d.0).unwrap_or([1.0, 1.0, 1.0]);
    let pol = try_into_slice_or!(polarization, [0.0, 0.0, 0.0]);

    let mut results: Vec<Vector3<f64>> = vec![Vector3::zeros(); n];

    py.detach(|| {
        magba::fields::cuboid_B_batch(
            &points,
            pos.into(),
            rot,
            pol.into(),
            dim.into(),
            results.as_mut_slice(),
        );
    });

    vec3_to_pyarray2(py, results)
}

#[cfg_attr(feature = "stub-gen", gen_stub_pyfunction)]
#[pyfunction]
/// Calculates the magnetic field of a spherical magnet.
///
/// Args:
///     points (PointsLike): Points [x, y, z] in meters at which to calculate the field.
///         Can be a single point or an (N, 3) array of points.
///     position (ArrayLike3, optional): Center of the sphere [x, y, z] in meters.
///         Defaults to [0.0, 0.0, 0.0].
///     orientation (PyRotation, optional): Orientation of the sphere.
///         Defaults to identity.
///     diameter (float, optional): Diameter of the sphere in meters.
///         Defaults to 1.0.
///     polarization (ArrayLike3, optional): Remanence polarization vector [Bx, By, Bz]
///         in Tesla. Defaults to [0.0, 0.0, 0.0].
///
/// Returns:
///     numpy.ndarray: Magnetic field (N, 3) in Tesla.
#[pyo3(signature = (points, position=None, orientation=None, diameter=1.0, polarization=None))]
pub fn sphere_B<'py>(
    py: Python<'py>,
    points: crate::base::PointsLike,
    position: Option<crate::base::ArrayLike3>,
    orientation: Option<crate::base::PyRotation>,
    diameter: f64,
    polarization: Option<crate::base::ArrayLike3>,
) -> Bound<'py, numpy::PyArray2<f64>> {
    let points = points.0;
    let n = points.len();

    let pos = try_into_slice!(position);
    let rot = orientation
        .map(|rot| rot.0)
        .unwrap_or_else(nalgebra::UnitQuaternion::identity);
    let pol = try_into_slice_or!(polarization, [0.0, 0.0, 0.0]);

    let mut results: Vec<Vector3<f64>> = vec![Vector3::zeros(); n];

    py.detach(|| {
        magba::fields::sphere_B_batch(
            &points,
            pos.into(),
            rot,
            pol.into(),
            diameter,
            results.as_mut_slice(),
        );
    });

    vec3_to_pyarray2(py, results)
}

#[cfg_attr(feature = "stub-gen", gen_stub_pyfunction)]
#[pyfunction]
/// Calculates the magnetic field of a circular current loop.
///
/// Args:
///     points (PointsLike): Points [x, y, z] in meters at which to calculate the field.
///         Can be a single point or an (N, 3) array of points.
///     position (ArrayLike3, optional): Center of the loop [x, y, z] in meters.
///         Defaults to [0.0, 0.0, 0.0].
///     orientation (PyRotation, optional): Orientation of the loop.
///         Defaults to identity.
///     diameter (float, optional): Diameter of the loop in meters.
///         Defaults to 1.0.
///     current (float, optional): Current in the loop in Amperes.
///         Defaults to 1.0.
///
/// Returns:
///     numpy.ndarray: Magnetic field (N, 3) in Tesla.
#[pyo3(signature = (points, position=None, orientation=None, diameter=1.0, current=1.0))]
pub fn circular_B<'py>(
    py: Python<'py>,
    points: crate::base::PointsLike,
    position: Option<crate::base::ArrayLike3>,
    orientation: Option<crate::base::PyRotation>,
    diameter: f64,
    current: f64,
) -> Bound<'py, numpy::PyArray2<f64>> {
    let points = points.0;
    let n = points.len();

    let pos = try_into_slice!(position);
    let rot = orientation
        .map(|rot| rot.0)
        .unwrap_or_else(nalgebra::UnitQuaternion::identity);

    let mut results: Vec<Vector3<f64>> = vec![Vector3::zeros(); n];

    py.detach(|| {
        magba::fields::circular_B_batch(
            &points,
            pos.into(),
            rot,
            diameter,
            current,
            results.as_mut_slice(),
        );
    });

    vec3_to_pyarray2(py, results)
}
