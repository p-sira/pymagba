/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::base::Source;
use magba::magnets::{
    CuboidMagnet as MagbaCuboidMagnet, CylinderMagnet as MagbaCylinderMagnet, Dipole as MagbaDipole,
};
use pyo3::prelude::*;
use pyo3_stub_gen::derive::gen_stub_pyfunction;

use crate::util::{ArrayLike3, PointsLike, PyRotation};

#[pymodule]
pub fn fields(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(cylinder_B, m)?)?;
    m.add_function(wrap_pyfunction!(dipole_B, m)?)?;
    m.add_function(wrap_pyfunction!(cuboid_B, m)?)?;
    Ok(())
}

#[gen_stub_pyfunction]
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
    let pos = position.map(|p| p.0).unwrap_or([0.0, 0.0, 0.0]);
    let rot = orientation
        .map(|rot| rot.0)
        .unwrap_or_else(nalgebra::UnitQuaternion::identity);
    let pol = polarization.map(|p| p.0).unwrap_or([0.0, 0.0, 0.0]);

    let magnet = MagbaCylinderMagnet::new(pos, rot, pol, diameter, height);
    compute_B_batch_to_numpy(py, points, &magnet)
}

#[gen_stub_pyfunction]
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
    let pos = position.map(|p| p.0).unwrap_or([0.0, 0.0, 0.0]);
    let rot = orientation
        .map(|rot| rot.0)
        .unwrap_or_else(nalgebra::UnitQuaternion::identity);
    let m = moment.map(|m| m.0).unwrap_or([0.0, 0.0, 0.0]);

    let dipole = MagbaDipole::new(pos, rot, m);
    compute_B_batch_to_numpy(py, points, &dipole)
}

#[gen_stub_pyfunction]
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
    let pos = position.map(|p| p.0).unwrap_or([0.0, 0.0, 0.0]);
    let rot = orientation
        .map(|rot| rot.0)
        .unwrap_or_else(nalgebra::UnitQuaternion::identity);
    let pol = polarization.map(|p| p.0).unwrap_or([0.0, 0.0, 0.0]);
    let dim = dimensions.map(|d| d.0).unwrap_or([1.0, 1.0, 1.0]);

    let magnet = MagbaCuboidMagnet::new(pos, rot, pol, dim);
    compute_B_batch_to_numpy(py, points, &magnet)
}

#[inline]
fn compute_B_batch_to_numpy<'py>(
    py: Python<'py>,
    points: PointsLike,
    source: &impl Source<f64>,
) -> Bound<'py, numpy::PyArray2<f64>> {
    use ndarray::Array2;
    use numpy::IntoPyArray;

    let pts = points.0;
    let n_points = pts.len();

    let b_field = source.compute_B_batch(&pts);

    let mut out = Array2::<f64>::zeros((n_points, 3));
    for i in 0..n_points {
        out[[i, 0]] = b_field[i].x;
        out[[i, 1]] = b_field[i].y;
        out[[i, 2]] = b_field[i].z;
    }

    out.into_pyarray(py)
}
