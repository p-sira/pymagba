/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use nalgebra::{Point3, Vector3};
use numpy::{PyArray1, ToPyArray};
use pyo3::prelude::*;

pub fn register_functions(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(axial_cyl_b_cyl, m)?)?;
    m.add_function(wrap_pyfunction!(axial_cyl_b, m)?)?;
    m.add_function(wrap_pyfunction!(diametric_cyl_b, m)?)?;
    m.add_function(wrap_pyfunction!(diametric_cyl_b_cyl, m)?)?;
    m.add_function(wrap_pyfunction!(cyl_b_cyl, m)?)?;
    m.add_function(wrap_pyfunction!(cyl_b, m)?)?;
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
    magba::field::axial_cyl_b_cyl(r, z, radius, height, pol_z).to_pyarray(py)
}

#[pyfunction]
pub fn axial_cyl_b(
    py: Python,
    point: [f64; 3],
    radius: f64,
    height: f64,
    pol_z: f64,
) -> Bound<'_, PyArray1<f64>> {
    let b = magba::field::axial_cyl_b(Point3::from(point), radius, height, pol_z);
    vec![b.x, b.y, b.z].to_pyarray(py)
}

#[pyfunction]
pub fn diametric_cyl_b_cyl(
    py: Python,
    cyl_point: [f64; 3],
    radius: f64,
    height: f64,
    pol_r: f64,
) -> Bound<'_, PyArray1<f64>> {
    magba::field::diametric_cyl_b_cyl(cyl_point, radius, height, pol_r).to_pyarray(py)
}

#[pyfunction]
pub fn diametric_cyl_b(
    py: Python,
    point: [f64; 3],
    radius: f64,
    height: f64,
    pol_r: f64,
) -> Bound<'_, PyArray1<f64>> {
    let b = magba::field::diametric_cyl_b(Point3::from(point), radius, height, pol_r);
    vec![b.x, b.y, b.z].to_pyarray(py)
}

#[pyfunction]
pub fn cyl_b_cyl(
    py: Python,
    cyl_point: [f64; 3],
    radius: f64,
    height: f64,
    pol_r: f64,
    pol_z: f64,
) -> Bound<'_, PyArray1<f64>> {
    magba::field::cyl_b_cyl(cyl_point, radius, height, pol_r, pol_z).to_pyarray(py)
}

#[pyfunction]
pub fn cyl_b(
    py: Python,
    point: [f64; 3],
    radius: f64,
    height: f64,
    pol: [f64; 3],
) -> Bound<'_, PyArray1<f64>> {
    let b = magba::field::cyl_b(Point3::from(point), radius, height, Vector3::from(pol));
    vec![b.x, b.y, b.z].to_pyarray(py)
}
