/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use numpy::{PyArray1, ToPyArray};
use pyo3::prelude::*;

pub fn register_functions(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(axial_cyl_b_cyl, m)?)?;
    m.add_function(wrap_pyfunction!(axial_cyl_b, m)?)?;
    Ok(())
}

#[pyfunction]
pub fn axial_cyl_b_cyl(
    py: Python,
    r: f64,
    z: f64,
    radius: f64,
    height: f64,
    pol_z: f64,
) -> Bound<'_, PyArray1<f64>> {
    let (a, b, c) = magba::fields::axial_cyl_b_cyl(r, z, radius, height, pol_z);
    vec![a, b, c].to_pyarray(py)
}

#[pyfunction]
pub fn axial_cyl_b(
    py: Python,
    x: f64,
    y: f64,
    z: f64,
    radius: f64,
    height: f64,
    pol_z: f64,
) -> Bound<'_, PyArray1<f64>> {
    let (a, b, c) = magba::fields::axial_cyl_b(x, y, z, radius, height, pol_z);
    vec![a, b, c].to_pyarray(py)
}
