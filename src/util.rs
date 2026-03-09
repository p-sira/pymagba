/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use nalgebra::Vector3;
use numpy::prelude::*;
use numpy::{PyArray1, PyArray2};
use pyo3::prelude::*;

/// Efficiently converts a Vec<Vector3<f64>> into a (N, 3) PyArray2.
#[inline]
pub fn vec3_to_pyarray2<'py>(
    py: Python<'py>,
    vec3: Vec<Vector3<f64>>,
) -> Bound<'py, PyArray2<f64>> {
    let n = vec3.len();

    // Flatten to 1D
    let flat_results: Vec<f64> = vec3.into_iter().flat_map(|v| [v.x, v.y, v.z]).collect();

    // Move to NumPy and reshape to 2D
    PyArray1::from_vec(py, flat_results)
        .reshape([n, 3])
        .unwrap()
}
