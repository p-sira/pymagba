/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use nalgebra::Vector3;
use numpy::PyArray2;
use pyo3::prelude::*;

/// Efficiently converts a Vec<Vector3<f64>> into a (N, 3) PyArray2.
#[inline]
pub fn vec3_to_pyarray2<'py>(
    py: Python<'py>,
    vec3: Vec<Vector3<f64>>,
) -> Bound<'py, PyArray2<f64>> {
    let n = vec3.len();
    if n == 0 {
        let arr = ndarray::Array2::<f64>::zeros((0, 3));
        return numpy::PyArray2::from_owned_array(py, arr);
    }
    if n == 1 {
        let v = vec3[0];
        let arr = ndarray::arr2(&[[v.x, v.y, v.z]]);
        return numpy::PyArray2::from_owned_array(py, arr);
    }

    debug_assert_eq!(
        std::mem::size_of::<Vector3<f64>>(),
        3 * std::mem::size_of::<f64>()
    );
    debug_assert_eq!(
        std::mem::align_of::<Vector3<f64>>(),
        std::mem::align_of::<f64>()
    );

    let flat_results = unsafe {
        let mut v = std::mem::ManuallyDrop::new(vec3);
        Vec::from_raw_parts(v.as_mut_ptr() as *mut f64, n * 3, v.capacity() * 3)
    };

    let arr = ndarray::Array2::from_shape_vec((n, 3), flat_results).unwrap();
    numpy::PyArray2::from_owned_array(py, arr)
}

/// Runs a closure and catches any panics, converting them to a Python `ValueError`.
#[inline]
pub fn catch_unwind_to_pyerr<F, R>(f: F) -> PyResult<R>
where
    F: FnOnce() -> R + std::panic::UnwindSafe,
{
    std::panic::catch_unwind(f).map_err(|e| {
        let msg = if let Some(s) = e.downcast_ref::<&str>() {
            s.to_string()
        } else if let Some(s) = e.downcast_ref::<String>() {
            s.clone()
        } else {
            "An unknown panic occurred in the Rust core.".to_string()
        };
        pyo3::exceptions::PyValueError::new_err(msg)
    })
}
