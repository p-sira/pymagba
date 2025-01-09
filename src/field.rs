/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use nalgebra::{Point3, Quaternion, UnitQuaternion, Vector3};
use numpy::{PyArray2, PyReadonlyArray2};
use pyo3::{exceptions::PyRuntimeError, prelude::*};

use crate::{
    convert::{pyarray_to_points_vec, vec_to_pyarray},
    fn_err,
};

pub fn register_functions(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(cyl_b, m)?)?;
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
    let points = pyarray_to_points_vec(point_array)?;
    let position = Point3::from(position);
    let orientation = UnitQuaternion::from_quaternion(Quaternion::new(
        orientation[0],
        orientation[1],
        orientation[2],
        orientation[3],
    ));

    match magba::field::cyl_b_vec(
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
