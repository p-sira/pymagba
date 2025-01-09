/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */
use nalgebra::Point3;
use nalgebra::Vector3;
use numpy::{PyArray2, PyReadonlyArray2, PyUntypedArrayMethods};
use pyo3::exceptions::PyRuntimeError;
use pyo3::Bound;
use pyo3::PyResult;
use pyo3::Python;

pub fn pyarray_to_points_vec(array: PyReadonlyArray2<f64>) -> PyResult<Vec<Point3<f64>>> {
    // Check if the input has the correct dimensions
    let shape = array.shape();
    if shape.len() != 2 || shape[1] != 3 {
        return Err(PyRuntimeError::new_err(
            "fn array_to_points_vec: Input array must have shape (n, 3).",
        ));
    }

    let array_slice = array.as_array();
    let points = array_slice
        .rows()
        .into_iter()
        .map(|row| Point3::new(row[0], row[1], row[2]))
        .collect();

    Ok(points)
}

pub fn vec_to_pyarray<'py>(py: Python<'py>, vec: Vec<Vector3<f64>>) -> Bound<'py, PyArray2<f64>> {
    let rows: Vec<Vec<f64>> = vec.into_iter().map(|v| vec![v.x, v.y, v.z]).collect();
    PyArray2::from_vec2(py, &rows).unwrap()
}
