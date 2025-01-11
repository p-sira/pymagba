/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */
use nalgebra::Point3;
use nalgebra::Quaternion;
use nalgebra::UnitQuaternion;
use nalgebra::Vector3;
use ndarray::Array2;
use numpy::PyArray2;
use pyo3::exceptions::PyRuntimeError;
use pyo3::Bound;
use pyo3::PyResult;
use pyo3::Python;

pub fn pyarray_to_point_vec(array: Array2<f64>) -> PyResult<Vec<Point3<f64>>> {
    // Check if the input has the correct dimensions
    let shape = array.shape();
    if shape.len() != 2 || shape[1] != 3 {
        return Err(PyRuntimeError::new_err(
            "fn array_to_point_vec: Input array must have shape (n, 3).",
        ));
    }

    let points = array
        .rows()
        .into_iter()
        .map(|row| Point3::new(row[0], row[1], row[2]))
        .collect();

    Ok(points)
}

pub fn pyarray_to_vector_vec(array: Array2<f64>) -> PyResult<Vec<Vector3<f64>>> {
    // Check if the input has the correct dimensions
    let shape = array.shape();
    if shape.len() != 2 || shape[1] != 3 {
        return Err(PyRuntimeError::new_err(
            "fn array_to_vector_vec: Input array must have shape (n, 4).",
        ));
    }

    let vectors = array
        .rows()
        .into_iter()
        .map(|row| Vector3::new(row[0], row[1], row[2]))
        .collect();

    Ok(vectors)
}

pub fn pyarray_to_quat_vec(array: Array2<f64>) -> PyResult<Vec<UnitQuaternion<f64>>> {
    // Check if the input has the correct dimensions
    let shape = array.shape();
    if shape.len() != 2 || shape[1] != 4 {
        return Err(PyRuntimeError::new_err(
            "fn array_to_quat_vec: Input array must have shape (n, 4).",
        ));
    }

    let quats = array
        .rows()
        .into_iter()
        .map(|row| UnitQuaternion::from_quaternion(Quaternion::new(row[0], row[1], row[2], row[3])))
        .collect();

    Ok(quats)
}

pub fn vec_to_pyarray(py: Python, vec: Vec<Vector3<f64>>) -> Bound<'_, PyArray2<f64>> {
    let rows: Vec<Vec<f64>> = vec.into_iter().map(|v| vec![v.x, v.y, v.z]).collect();
    PyArray2::from_vec2(py, &rows).unwrap()
}
