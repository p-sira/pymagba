/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use std::panic;

pub fn register_functions(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(cel, m)?)?;
    Ok(())
}

#[pyfunction]
pub fn cel(kc: f64, p: f64, c: f64, s: f64) -> PyResult<f64> {
    panic::catch_unwind(|| magba::special::cel(kc, p, c, s))
        .map_err(|e| PyValueError::new_err(format!("{:?}", e)))
}
