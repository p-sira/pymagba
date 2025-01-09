/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use pyo3::prelude::*;
mod field;
mod helper;
mod convert;

#[pymodule]
fn pymagba_binding(py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    add_submodule!(field, "field", py, m);
    Ok(())
}
