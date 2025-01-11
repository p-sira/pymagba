/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use pyo3::prelude::*;
mod convert;
mod field;
mod helper;

#[pymodule(gil_used = false)]
#[pyo3(name = "pymagba_binding")]
fn pymagba_binding(py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    add_submodule!(field, "field", py, m);
    Ok(())
}
