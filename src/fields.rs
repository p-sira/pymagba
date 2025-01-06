/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use numpy::{PyArray1, ToPyArray};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

pub fn register_functions(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(axial_cyl_b_cyl, m)?)?;
    Ok(())
}

#[pyfunction]
pub fn axial_cyl_b_cyl(
    py: Python,
    r: f64,
    z: f64,
    radius: f64,
    height: f64,
) -> PyResult<Bound<'_, PyArray1<f64>>> {
    std::panic::catch_unwind(|| magba::fields::axial_cyl_b_cyl(r, z, radius, height).to_pyarray(py))
        .map_err(|e| PyValueError::new_err(format!("{:?}", e)))
}
