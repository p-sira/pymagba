/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use nalgebra::{Point3, Quaternion, UnitQuaternion, Vector3};
use numpy::{PyArray2, PyReadonlyArray1, PyReadonlyArray2};
use pyo3::{exceptions::PyRuntimeError, prelude::*};

use crate::{
    convert::{
        pyarray_to_float_vec, pyarray_to_point_vec, pyarray_to_quat_vec, pyarray_to_vector_vec,
        vec_to_pyarray,
    },
    fn_err,
};

pub fn register_functions(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(cyl_b, m)?)?;
    m.add_function(wrap_pyfunction!(sum_multiple_cyl_b, m)?)?;
    Ok(())
}

#[pyfunction]
pub fn cyl_b<'py>(
    py: Python<'py>,
    point_array: PyReadonlyArray2<f64>,
    position: [f64; 3],
    orientation: [f64; 4],
    radius: f64,
    height: f64,
    pol: [f64; 3],
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let points = pyarray_to_point_vec(point_array)?;
    let position = Point3::from(position);
    let orientation = UnitQuaternion::from_quaternion(Quaternion::new(
        orientation[0],
        orientation[1],
        orientation[2],
        orientation[3],
    ));

    match magba::field::cyl_b(
        &points,
        &position,
        &orientation,
        radius,
        height,
        &Vector3::from(pol),
    ) {
        Ok(result) => Ok(vec_to_pyarray(py, result)),
        Err(e) => fn_err!("cyl_b", e),
    }
}

#[pyfunction]
pub fn sum_multiple_cyl_b<'py>(
    py: Python<'py>,
    point_array: PyReadonlyArray2<f64>,
    position_array: PyReadonlyArray2<f64>,
    orientation_array: PyReadonlyArray2<f64>,
    radius_array: PyReadonlyArray1<f64>,
    height_array: PyReadonlyArray1<f64>,
    pol_array: PyReadonlyArray2<f64>,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let points = pyarray_to_point_vec(point_array)?;
    let positions = pyarray_to_point_vec(position_array)?;
    let orientations = pyarray_to_quat_vec(orientation_array)?;
    let radii = pyarray_to_float_vec(radius_array);
    let heights = pyarray_to_float_vec(height_array);
    let pols = pyarray_to_vector_vec(pol_array)?;

    match magba::field::sum_multiple_cyl_b(
        &points,
        &positions,
        &orientations,
        &radii,
        &heights,
        &pols,
    ) {
        Ok(result) => Ok(vec_to_pyarray(py, result)),
        Err(e) => fn_err!("sum_multiple_cyl_b", e),
    }
}
